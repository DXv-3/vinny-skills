#!/usr/bin/env python3
"""
yt_kb.ui — local web UI over the knowledge base. Stdlib server, zero extra deps.

  python3 ui.py [--db data] [--port 8765]

Endpoints: / (UI)  /api/stats  /api/search?q=&n=&channel=  /api/map?channel=
           /api/extract?type=tools|numbers|frameworks&q=  /api/compare?q=
"""
import argparse
import json
import os
import re
import sqlite3
import struct
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

DB_DIR = os.path.abspath(os.path.join(os.getcwd(), "data"))
PORT = 8765
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
_lock = threading.Lock()
_embedder = None


def open_db():
    path = os.path.join(DB_DIR, "kb.sqlite")
    if not os.path.exists(path):
        raise SystemExit(f"no DB at {path}")
    db = sqlite3.connect(path, timeout=60, check_same_thread=False)
    db.execute("PRAGMA busy_timeout=60000")
    db.enable_load_extension(True)
    import sqlite_vec
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    return db


DB = open_db()


def embed(text):
    global _embedder
    with _lock:
        if _embedder is None:
            from fastembed import TextEmbedding
            _embedder = TextEmbedding("BAAI/bge-small-en-v1.5",
                                      cache_dir=os.path.join(DB_DIR, "fastembed_cache"))
        v = list(_embedder.embed([QUERY_PREFIX + text]))[0]
    return struct.pack("<%df" % len(v), *v)


def fmt_ts(s):
    s = int(s or 0)
    return f"{s//60}:{s%60:02d}"


def rrf(a, b, k=60):
    sc = {}
    for rank, (cid, *_ ) in enumerate(a):
        sc[cid] = sc.get(cid, 0) + 1.0 / (k + rank + 1)
    for rank, row in enumerate(b):
        cid = row[0]
        sc[cid] = sc.get(cid, 0) + 1.0 / (k + rank + 1)
    return sorted(sc.items(), key=lambda x: -x[1])


def search(q, n=10, channel=None):
    qvec = embed(q)
    vec_sql = """SELECT cv.chunk_id FROM chunks_vec cv JOIN chunks c ON c.chunk_id=cv.chunk_id
                 JOIN videos v ON v.video_id=c.video_id
                 WHERE cv.embedding MATCH ? AND cv.k=60""" + (" AND v.channel_id=?" if channel else "")
    vec_args = [qvec, 60] + ([channel] if channel else [])
    vec = DB.execute(vec_sql, vec_args).fetchall()
    toks = re.findall(r"\w+", q)
    fts = []
    if toks:
        try:
            fts_sql = """SELECT f.chunk_id FROM chunks_fts f JOIN chunks c ON c.chunk_id=f.chunk_id
                         JOIN videos v ON v.video_id=c.video_id
                         WHERE chunks_fts MATCH ?""" + (" AND v.channel_id=?" if channel else "") + " LIMIT 60"
            fts_args = [" OR ".join(toks)] + ([channel] if channel else [])
            fts = DB.execute(fts_sql, fts_args).fetchall()
        except sqlite3.OperationalError:
            pass
    out = []
    for cid, score in rrf(vec, fts)[:n]:
        r = DB.execute("""SELECT c.body, c.start_s, c.end_s, v.video_id, v.title,
                          v.upload_date, v.view_count, ch.name
                          FROM chunks c JOIN videos v ON v.video_id=c.video_id
                          JOIN channels ch ON ch.channel_id=v.channel_id
                          WHERE c.chunk_id=?""", (cid,)).fetchone()
        if r:
            out.append({"body": r[0], "start": r[1], "end": r[2], "video": r[3],
                        "title": r[4], "date": r[5], "views": r[6], "channel": r[7],
                        "url": f"https://youtu.be/{r[3]}?t={int(r[1])}",
                        "ts": fmt_ts(r[1]) + "–" + fmt_ts(r[2])})
    return out


def stats():
    rows = DB.execute("""SELECT ch.name, ch.channel_id, vstat.nv,
                         (SELECT COUNT(*) FROM chunks c WHERE c.video_id IN
                            (SELECT video_id FROM videos WHERE channel_id=ch.channel_id)),
                         vstat.d1, vstat.d2
                         FROM channels ch
                         LEFT JOIN (SELECT channel_id,
                              SUM(CASE WHEN status='ok' THEN 1 ELSE 0 END) nv,
                              MIN(upload_date) d1, MAX(upload_date) d2
                              FROM videos GROUP BY channel_id) vstat
                           ON vstat.channel_id=ch.channel_id
                         ORDER BY vstat.nv DESC""").fetchall()
    return [{"name": r[0], "id": r[1], "videos": r[2] or 0, "chunks": r[3] or 0,
             "from": r[4], "to": r[5]} for r in rows]


def month_volume(channel):
    where, args = "v.status='ok'", []
    if channel:
        where += " AND v.channel_id=?"; args.append(channel)
    return DB.execute(f"""SELECT substr(upload_date,1,6) ym, COUNT(*) FROM videos v
                          WHERE {where} GROUP BY ym ORDER BY ym""", args).fetchall()


def map_data(channel):
    where, args = "v.status='ok'", []
    if channel:
        where += " AND v.channel_id=?"; args.append(channel)
    base = DB.execute(f"""SELECT COUNT(*), SUM(v.n_chunks), MIN(v.upload_date), MAX(v.upload_date)
                          FROM videos v WHERE {where}""", args).fetchone()
    tools = DB.execute(f"""SELECT t.tool, COUNT(DISTINCT t.video_id) n, MIN(v.upload_date)
                           FROM tools_mentions t JOIN videos v ON v.video_id=t.video_id
                           WHERE {where} GROUP BY t.tool ORDER BY n DESC LIMIT 12""", args).fetchall()
    fws = DB.execute(f"""SELECT f.name, MIN(v.upload_date) FROM frameworks f
                         JOIN videos v ON v.video_id=f.video_id
                         WHERE {where} GROUP BY f.name ORDER BY f.name LIMIT 40""", args).fetchall()
    top = DB.execute(f"""SELECT title, view_count, upload_date, video_id FROM videos v
                         WHERE {where} ORDER BY view_count DESC LIMIT 8""", args).fetchall()
    months = [(m, n) for m, n in month_volume(channel)]
    return {"videos": base[0], "chunks": base[1], "from": base[2], "to": base[3],
            "tools": [{"tool": t, "n": n, "since": d} for t, n, d in tools],
            "frameworks": [{"name": n, "since": d} for n, d in fws],
            "top": [{"title": t, "views": v, "date": d, "url": f"https://youtu.be/{i}"}
                    for t, v, d, i in top],
            "months": months}


def extract_data(etype, q=None, limit=100):
    q = (q or "").strip()
    if etype == "tools":
        sql = """SELECT t.tool, v.title, v.upload_date, t.start_s, t.video_id, t.mentions,
                 t.first_snippet FROM tools_mentions t JOIN videos v ON v.video_id=t.video_id """
        order = "GROUP BY t.tool, t.video_id ORDER BY v.upload_date DESC, t.mentions DESC"
        args = []
        if q:
            sql += "WHERE t.tool LIKE ? "; args.append(f"%{q}%")
        sql += order + " LIMIT ?"
        rows = DB.execute(sql, args + [limit]).fetchall()
        return [{"tool": r[0], "title": r[1], "date": r[2], "start_s": r[3],
                 "url": f"https://youtu.be/{r[4]}?t={int(r[3])}", "mentions": r[5],
                 "snippet": r[6]} for r in rows]
    if etype == "numbers":
        sql = """SELECT n.value, v.title, v.upload_date, n.start_s, n.video_id, n.snippet
                 FROM numbers_mentions n JOIN videos v ON v.video_id=n.video_id """
        args = []
        if q:
            sql += "WHERE n.value LIKE ? "; args.append(f"%{q}%")
        sql += "ORDER BY v.upload_date DESC LIMIT ?"
        rows = DB.execute(sql, args + [limit]).fetchall()
        return [{"value": r[0], "title": r[1], "date": r[2], "start_s": r[3],
                 "url": f"https://youtu.be/{r[4]}?t={int(r[3])}", "snippet": r[5]} for r in rows]
    if etype == "frameworks":
        sql = """SELECT f.name, v.title, v.upload_date, f.start_s, f.video_id, f.snippet
                 FROM frameworks f JOIN videos v ON v.video_id=f.video_id """
        args = []
        if q:
            sql += "WHERE f.name LIKE ? "; args.append(f"%{q}%")
        sql += "ORDER BY f.name LIMIT ?"
        rows = DB.execute(sql, args + [limit]).fetchall()
        return [{"name": r[0], "title": r[1], "date": r[2], "start_s": r[3],
                 "url": f"https://youtu.be/{r[4]}?t={int(r[3])}", "snippet": r[5]} for r in rows]
    if etype == "claims":
        sql = """SELECT c.sentence, v.title, v.upload_date, c.start_s, c.video_id
                 FROM claims_candidates c JOIN videos v ON v.video_id=c.video_id """
        args = []
        if q:
            sql += "WHERE c.sentence LIKE ? "; args.append(f"%{q}%")
        sql += "ORDER BY v.upload_date DESC LIMIT ?"
        rows = DB.execute(sql, args + [limit]).fetchall()
        return [{"sentence": r[0], "title": r[1], "date": r[2], "start_s": r[3],
                 "url": f"https://youtu.be/{r[4]}?t={int(r[3])}"} for r in rows]
    return []


HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>yt-kb — YouTube Knowledge Base</title>
<style>
:root{--bg:#0d1117;--panel:#161b22;--edge:#21262d;--txt:#e6edf3;--dim:#8b949e;
--acc:#58a6ff;--ok:#3fb950;--warn:#d29922;--pink:#f778ba}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font:15px/1.55 -apple-system,"SF Pro Text",Inter,sans-serif}
a{color:var(--acc);text-decoration:none} a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:9;background:rgba(13,17,23,.92);backdrop-filter:blur(8px);
border-bottom:1px solid var(--edge);padding:14px 22px;display:flex;gap:18px;align-items:center;flex-wrap:wrap}
h1{font-size:17px;font-weight:700;letter-spacing:-.01em}
h1 span{color:var(--acc)}
nav{display:flex;gap:4px;margin-left:auto}
nav button{background:none;border:1px solid transparent;color:var(--dim);padding:6px 12px;
border-radius:7px;cursor:pointer;font-size:13.5px;font-weight:500}
nav button:hover{color:var(--txt);background:var(--panel)}
nav button.on{color:var(--txt);background:var(--panel);border-color:var(--edge)}
main{max-width:980px;margin:0 auto;padding:26px 22px 80px}
.searchbox{display:flex;gap:10px;margin:6px 0 18px}
.searchbox input{flex:1;background:var(--panel);border:1px solid var(--edge);border-radius:10px;
padding:13px 16px;color:var(--txt);font-size:16px;outline:none}
.searchbox input:focus{border-color:var(--acc)}
.searchbox button{background:var(--acc);color:#04121f;border:0;border-radius:10px;padding:0 22px;
font-weight:700;font-size:15px;cursor:pointer}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px}
.chip{background:var(--panel);border:1px solid var(--edge);border-radius:999px;padding:5px 13px;
font-size:12.5px;color:var(--dim);cursor:pointer}
.chip.on{color:var(--txt);border-color:var(--acc)}
.chip b{color:var(--txt)}
.card{background:var(--panel);border:1px solid var(--edge);border-radius:12px;padding:16px 18px;margin-bottom:12px}
.card h3{font-size:14.5px;margin-bottom:4px}
.meta{font-size:12.5px;color:var(--dim);margin-bottom:8px}
.meta .t{color:var(--warn);font-weight:600}
.snip{font-size:14px;color:#c9d1d9}
.score{float:right;font-size:11px;color:var(--dim)}
.sect{margin:26px 0 12px;font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--dim)}
.bar{display:inline-block;background:var(--acc);height:9px;border-radius:3px;vertical-align:middle;margin-right:8px;opacity:.85}
table{width:100%;border-collapse:collapse;font-size:13.5px}
td,th{padding:8px 10px;border-bottom:1px solid var(--edge);text-align:left;vertical-align:top}
th{color:var(--dim);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.06em}
.mono{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;color:var(--pink)}
.tabs2{display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap}
.tabs2 button{background:var(--panel);border:1px solid var(--edge);color:var(--dim);
padding:6px 14px;border-radius:999px;cursor:pointer;font-size:13px}
.tabs2 button.on{color:var(--txt);border-color:var(--acc)}
input.mini{background:var(--bg);border:1px solid var(--edge);border-radius:8px;color:var(--txt);
padding:8px 12px;font-size:14px;outline:none;width:280px}
.empty{color:var(--dim);text-align:center;padding:40px 0;font-size:14px}
.spin{color:var(--dim);font-size:13px;padding:14px 2px}
.kbd{background:var(--panel);border:1px solid var(--edge);border-radius:5px;padding:1px 6px;font-size:12px;color:var(--dim)}
</style></head><body>
<header>
  <h1>yt<span>·</span>kb <span style="font-weight:400;color:var(--dim);font-size:13px">local knowledge base</span></h1>
  <nav>
    <button data-v="search" class="on">Search</button>
    <button data-v="map">Channel Map</button>
    <button data-v="know">Knowledge Tables</button>
  </nav>
</header>
<main>
<section id="v-search">
  <div class="searchbox"><input id="q" placeholder="Ask anything… e.g. pricing AI services, Claude Code workflow" autofocus>
  <button onclick="doSearch()">Search</button></div>
  <div class="chips" id="chips"></div>
  <div id="results"><div class="empty">Hybrid search — semantic + keyword, fused. Every hit links to the exact second.</div></div>
</section>
<section id="v-map" style="display:none">
  <div class="chips" id="mchips"></div><div id="mapout"></div>
</section>
<section id="v-know" style="display:none">
  <div class="tabs2">
    <button data-k="tools" class="on">Tools</button><button data-k="numbers">Money</button>
    <button data-k="frameworks">Frameworks</button><button data-k="claims">Advice claims</button>
  </div>
  <div style="margin-bottom:14px"><input class="mini" id="kq" placeholder="filter… (tool name, $amount, keyword)"></div>
  <div id="kout"></div>
</section>
</main>
<script>
const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s);
let CH=null, CUR=null;
async function j(url){const r=await fetch(url);return r.json();}
function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function snip(s){s=esc(s||'');return s.length>320?s.slice(0,320)+'…':s}
function views(v){if(!v)return'';return v>=1e6?(v/1e6).toFixed(1)+'M views':v>=1e3?Math.round(v/1e3)+'K views':v+' views'}
// nav
$$('nav button').forEach(b=>b.onclick=()=>{
  $$('nav button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
  ['search','map','know'].forEach(v=>$('#v-'+v).style.display=v===b.dataset.v?'':'none');
  if(b.dataset.v==='map')loadMap();
});
// chips
async function chips(){
  CH=await j('/api/stats');
  const mk=(c,cur,on)=>`<span class="chip ${on?'on':''}" data-c="${c}">${esc(cur)} <b>${c==='all'?'':c}</b></span>`;
  $('#chips').innerHTML=mk('all','All',true)+CH.map(c=>mk(c.id,c.name+` (${c.videos})`,false)).join('');
  $('#mchips').innerHTML=CH.map((c,i)=>mk(c.id,c.name+` (${c.videos})`,i===0)).join('');
  $$('#chips .chip').forEach(el=>el.onclick=()=>{$$('#chips .chip').forEach(x=>x.classList.remove('on'));el.classList.add('on');CUR=el.dataset.c==='all'?null:el.dataset.c;doSearch();});
  $$('#mchips .chip').forEach((el,i)=>el.onclick=()=>{$$('#mchips .chip').forEach(x=>x.classList.remove('on'));el.classList.add('on');loadMap(CH[i].id);});
}
async function doSearch(){
  const q=$('#q').value.trim();if(!q)return;
  $('#results').innerHTML='<div class="spin">Searching… (first search loads the embedding model, ~30s once)</div>';
  const r=await j('/api/search?q='+encodeURIComponent(q)+'&n=12'+(CUR?'&channel='+CUR:''));
  if(!r.length){$('#results').innerHTML='<div class="empty">no matches</div>';return;}
  $('#results').innerHTML=r.map(x=>`<div class="card"><span class="score">${x.score}</span>
   <h3><a href="${x.url}" target="_blank">${esc(x.title)}</a></h3>
   <div class="meta">${x.channel} · ${x.date} · ${views(x.views)} · <span class="t">at ${x.ts}</span></div>
   <div class="snip">${snip(x.body)}</div></div>`).join('');
}
$('#q').addEventListener('keydown',e=>{if(e.key==='Enter')doSearch()});
// map
async function loadMap(cid){
  cid=cid||CH[0].id;
  $('#mapout').innerHTML='<div class="spin">loading…</div>';
  const m=await j('/api/map?channel='+cid);
  const max=Math.max(...m.months.map(x=>x[1]),1);
  const mm=m.months.map(([ym,n])=>`<div style="margin:3px 0"><span class="bar" style="width:${Math.round(n/max*260)}px"></span>${ym.slice(0,4)}-${ym.slice(4)} <span style="color:var(--dim)">${n}</span></div>`).join('');
  $('#mapout').innerHTML=`
   <div class="card"><h3>${esc(CH.find(c=>c.id===cid).name)}</h3>
   <div class="meta">${m.videos} videos · ${m.chunks} chunks · ${m.from} → ${m.to}</div></div>
   <div class="sect">upload volume</div><div class="card">${mm}</div>
   <div class="sect">tool footprint (first mention = adoption)</div>
   <div class="card"><table><tr><th>tool</th><th>videos</th><th>since</th></tr>
   ${m.tools.map(t=>`<tr><td><b>${esc(t.tool)}</b></td><td>${t.n}</td><td class="mono">${t.since}</td></tr>`).join('')}</table></div>
   <div class="sect">named frameworks</div>
   <div class="card">${m.frameworks.map(f=>`<span class="chip" style="cursor:default">${esc(f.name)} <b style="color:var(--dim)">${f.since}</b></span>`).join(' ')||'<span class=empty>none</span>'}</div>
   <div class="sect">biggest videos</div>
   <div class="card"><table>${m.top.map(t=>`<tr><td style="width:90px" class="mono">${views(t.views)}</td><td><a href="${t.url}" target="_blank">${esc(t.title)}</a><div class="meta">${t.date}</div></td></tr>`).join('')}</table></div>`;
}
// knowledge tables
let KTAB='tools';
$$('.tabs2 button').forEach(b=>b.onclick=()=>{
  $$('.tabs2 button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
  KTAB=b.dataset.k;loadK();
});
$('#kq').addEventListener('keydown',e=>{if(e.key==='Enter')loadK()});
async function loadK(){
  const q=$('#kq').value.trim();
  $('#kout').innerHTML='<div class="spin">loading…</div>';
  const rows=await j('/api/extract?type='+KTAB+'&q='+encodeURIComponent(q));
  if(!rows.length){$('#kout').innerHTML='<div class="empty">no rows</div>';return;}
  if(KTAB==='tools'){
    $('#kout').innerHTML='<div class="card"><table><tr><th>tool</th><th>video</th><th>at</th><th>x</th></tr>'+
    rows.map(r=>`<tr><td><b>${esc(r.tool)}</b></td><td><a href="${r.url}" target="_blank">${esc(r.title)}</a><div class="meta">${r.date}</div></td><td class="mono">${fmt(r.start_s)}</td><td>${r.mentions}</td></tr>`).join('')+'</table></div>';
  }else if(KTAB==='numbers'){
    $('#kout').innerHTML='<div class="card"><table><tr><th>figure</th><th>video</th><th>context</th></tr>'+
    rows.map(r=>`<tr><td class="mono">${esc(r.value)}</td><td><a href="${r.url}" target="_blank">${esc(r.title)}</a><div class="meta">${r.date} · at ${fmt(r.start_s)}</div></td><td class="snip">${snip(r.snippet,120)}</td></tr>`).join('')+'</table></div>';
  }else if(KTAB==='frameworks'){
    $('#kout').innerHTML='<div class="card"><table><tr><th>framework</th><th>video</th></tr>'+
    rows.map(r=>`<tr><td><b>${esc(r.name)}</b></td><td><a href="${r.url}" target="_blank">${esc(r.title)}</a><div class="meta">${r.date} · at ${fmt(r.start_s)}</div></td></tr>`).join('')+'</table></div>';
  }else{
    $('#kout').innerHTML=rows.map(r=>`<div class="card"><div class="snip">“${esc(r.sentence)}”</div>
     <div class="meta" style="margin-top:8px"><a href="${r.url}" target="_blank">${esc(r.title)}</a> · ${r.date} · at ${fmt(r.start_s)}</div></div>`).join('');
  }
}
function fmt(s){s=Math.floor(s||0);return Math.floor(s/60)+':'+String(s%60).padStart(2,'0')}
snip=(s,w)=>{s=esc(s||'');const W=w||320;return s.length>W?s.slice(0,W)+'…':s};
chips();
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = urlparse(self.path)
        q = parse_qs(p.query)
        try:
            if p.path == "/":
                html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.html")
                with open(html_path, "rb") as f:
                    b = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)
            elif p.path == "/api/stats":
                self._json(stats())
            elif p.path == "/api/search":
                res = search(unquote(q["q"][0]), n=int(q.get("n", ["10"])[0]),
                             channel=q.get("channel", [None])[0])
                for r in res:
                    r["score"] = round(1.0 / (1.0 + (10 - len(res))) , 4)
                # attach fused ranks as scores by position
                for i, r in enumerate(res):
                    r["score"] = round(0.05 - i * 0.001, 4)
                self._json(res)
            elif p.path == "/api/map":
                self._json(map_data(q.get("channel", [None])[0]))
            elif p.path == "/api/extract":
                self._json(extract_data(q["type"][0], unquote(q.get("q", [""])[0])))
            elif p.path == "/api/compare":
                from synthesize import do_compare  # not used by UI yet
                self._json({"ok": False})
            else:
                self._json({"err": "not found"}, 404)
        except Exception as e:
            self._json({"err": str(e)}, 500)


def main():
    global DB_DIR, PORT
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=None)
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    if args.db:
        DB_DIR = os.path.abspath(args.db)
    PORT = args.port
    # re-open DB against the right dir
    global DB
    DB.close()
    DB = open_db()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"yt-kb UI → http://127.0.0.1:{PORT}   (DB: {DB_DIR}/kb.sqlite)", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
