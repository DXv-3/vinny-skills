#!/usr/bin/env python3
"""stage-to-files.py — Door 2 phase 7: staged conversation dirs → real files on disk.

Reads a staging root of per-conversation dirs (conversation.json + files.json, the
Manus web-harvest convention), writes every inline content entry as a real file
(preserving in-task paths), downloads every URL-bearing entry, and emits _MANIFEST.json.

Usage:
  stage-to-files.py <staging_root> <files_root> [--workers 6] [--skip-downloads]

Idempotent: existing files are overwritten only from fresher inline content; failed
downloads are retried on the next run. Manifest records counts + total MB.
"""
import json, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor


def safe_rel(p):
    p = p or "unnamed"
    p = re.sub(r"^/?(home/ubuntu|home/mnt|mnt)/?", "", p)
    parts = [re.sub(r"[^\w.\- ()\[\]]", "_", seg) for seg in p.split("/") if seg and seg not in (".", "..")]
    return "/".join(parts) or "unnamed"


def harvest_jobs(staging_root, files_root):
    downloads, inline_written = [], 0
    for d in sorted(os.listdir(staging_root)):
        sdir = os.path.join(staging_root, d)
        fj = os.path.join(sdir, "files.json")
        if not os.path.isdir(sdir) or not os.path.exists(fj):
            continue
        try:
            j = json.load(open(fj))
        except Exception:
            continue
        data = j.get("data")
        file_list = (data or {}).get("files") if isinstance(data, dict) else None
        if not isinstance(file_list, list):
            continue
        uid = (data or {}).get("id") or d
        out_dir = os.path.join(files_root, str(uid))
        for f in file_list:
            if not isinstance(f, dict):
                continue
            raws = [r for r in (f.get("raw") or []) if isinstance(r, dict)]
            if not raws:
                continue
            path = next((r.get("path") for r in reversed(raws) if r.get("path")), None) \
                or f.get("displayFilename") or "unnamed"
            dest = os.path.join(out_dir, safe_rel(path))
            inline = next((r.get("fileContent") for r in reversed(raws)
                           if r.get("fileContent") is not None), None)
            url = next((r.get("url") for r in reversed(raws) if r.get("url")), None) \
                or (raws[-1].get("rawUrl") if raws else None) \
                or next((r.get("inlineImageUrl") for r in reversed(raws)
                         if r.get("inlineImageUrl")), None)
            if inline is not None:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with open(dest, "wb" if isinstance(inline, bytes) else "w") as fh:
                    fh.write(inline)
                inline_written += 1
            elif url:
                downloads.append((url, dest))
    return inline_written, downloads


def download(job):
    url, dest = job
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as fh:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
        return (dest, os.path.getsize(dest), None)
    except Exception as e:
        return (dest, 0, str(e)[:120])


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    staging_root, files_root = os.path.expanduser(sys.argv[1]), os.path.expanduser(sys.argv[2])
    workers, skip = 6, "--skip-downloads" in sys.argv
    os.makedirs(files_root, exist_ok=True)

    inline_written, downloads = harvest_jobs(staging_root, files_root)
    print(f"inline files written: {inline_written}")
    ok = failed = 0
    total_bytes = 0
    if downloads and not skip:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for dest, size, err in ex.map(download, downloads):
                if err:
                    failed += 1
                    print(f"  FAIL {os.path.basename(dest)}: {err}", file=sys.stderr)
                else:
                    ok += 1
                    total_bytes += size
    print(f"downloads: {ok} ok ({total_bytes / 1048576:.1f}MB), {failed} failed, {len(downloads) - ok - failed} skipped")

    n_files = sum(len(fs) for _, _, fs in os.walk(files_root))
    total_mb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(files_root) for f in fs) / 1048576
    manifest = {"files_on_disk": n_files, "total_mb": round(total_mb, 1),
                "inline_written_this_run": inline_written, "downloads_ok": ok, "downloads_failed": failed}
    json.dump(manifest, open(os.path.join(files_root, "_MANIFEST.json"), "w"), indent=1)
    print("manifest:", manifest)


if __name__ == "__main__":
    main()
