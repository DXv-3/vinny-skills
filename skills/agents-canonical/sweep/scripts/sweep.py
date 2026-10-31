#!/usr/bin/env python3
"""
SWEEP — file triage for a folder: extract, compile, score KEEP/MAYBE/TRASH.

Read-only on the target. All output goes to one folder (default: <target>/SWEEP-DATA
or --out). Nothing is ever deleted. Stage-trash moves verdicts into a staging folder
plus an undo script — run it only after a human says go.

Usage:
  sweep.py TARGET [--out DIR] [--no-extract] [--quiet]
  sweep.py TARGET --stage-trash        # move TRASH verdicts -> OUT/_TRASH-staging + undo.sh
"""

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import zipfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

CHUNK = 1 << 20
TEXT_SAMPLE = 400_000          # bytes of raw text to keep per file
MAX_ARCHIVE_BYTES = 500 << 20  # skip archives bigger than this
MAX_EXTRACT_TOTAL = 2 << 30    # stop extracting after this much total
MAX_EXTRACT_DEPTH = 2
READABLE_TEXT_EXTS = {
    ".txt", ".md", ".markdown", ".csv", ".tsv", ".json", ".jsonl", ".xml", ".yaml",
    ".yml", ".log", ".ini", ".cfg", ".conf", ".env", ".sql", ".html", ".htm", ".css",
    ".js", ".mjs", ".cjs", ".ts", ".py", ".rb", ".go", ".rs", ".java", ".kt", ".swift",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".php", ".sh", ".zsh", ".bash", ".r", ".tex",
    ".srt", ".vtt", ".plist", ".strings", ".gp", ".gpx", ".vcf", ".ics", ".m3u",
}
ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".tbz2", ".xz", ".txz", ".7z", ".rar"}
DOC_EXTS = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".ods",
            ".odp", ".rtf", ".pages", ".numbers", ".key", ".eml", ".msg"}
MEDIA_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".heic", ".heif", ".tiff", ".webp", ".bmp",
              ".svg", ".mp4", ".mov", ".avi", ".mkv", ".webm", ".mp3", ".m4a", ".wav",
              ".aiff", ".flac", ".ogg", ".aac"}
INSTALLER_EXTS = {".dmg", ".pkg", ".exe", ".msi", ".deb", ".rpm", ".appimage"}
TRASH_EXTS = {".tmp", ".temp", ".swp", ".crdownload", ".part", ".partial", ".download"}
TRASH_NAMES = {".ds_store", "thumbs.db", "desktop.ini", ".localized", ".trash"}
TRASH_PATH_PARTS = {"__macosx", "node_modules", "__pycache__", ".cache", "site-packages",
                    ".gradle", ".npm", ".venv", "venv/.venv"}

J_KEEP, J_MAYBE, J_TRASH = "KEEP", "MAYBE", "TRASH"

NOW = time.time()


def log(msg, quiet=False):
    if not quiet:
        print(msg, flush=True)


def sha256_of(path, limit=None):
    h = hashlib.sha256()
    remaining = limit
    try:
        with open(path, "rb") as f:
            while True:
                b = f.read(CHUNK)
                if not b:
                    break
                if remaining is not None:
                    if remaining <= 0:
                        break
                    b = b[:remaining]
                    remaining -= len(b)
                h.update(b)
        return h.hexdigest()
    except OSError:
        return None


def sanitize_rel(name):
    """Make an archive member name safe to place under a destination root."""
    name = name.replace("\\", "/")
    name = re.sub(r"^[A-Za-z]:/", "", name)          # windows drive
    parts = []
    for p in name.split("/"):
        if p in ("", ".", ".."):
            continue
        p = p.replace("\x00", "_")
        parts.append(p)
    return "/".join(parts)


def safe_extract_member(root: Path, rel: str) -> Path | None:
    dest = (root / rel).resolve()
    try:
        dest.relative_to(root.resolve())
    except ValueError:
        return None
    return dest


def extract_zip(zpath: Path, dest_root: Path, extracted_bytes: list, depth_notes: list):
    try:
        with zipfile.ZipFile(zpath) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                if extracted_bytes[0] + info.file_size > MAX_EXTRACT_TOTAL:
                    depth_notes.append(f"stopped: extract budget hit at {zpath.name}")
                    return
                rel = sanitize_rel(info.filename)
                if not rel:
                    continue
                out = safe_extract_member(dest_root, rel)
                if out is None:
                    depth_notes.append(f"skipped unsafe member {info.filename} in {zpath.name}")
                    continue
                out.parent.mkdir(parents=True, exist_ok=True)
                try:
                    with z.open(info) as src, open(out, "wb") as dst:
                        shutil.copyfileobj(src, dst, CHUNK)
                    extracted_bytes[0] += info.file_size
                except (OSError, RuntimeError, zlib.error, zipfile.BadZipFile) as e:
                    depth_notes.append(f"member failed {info.filename} in {zpath.name}: {e}")
    except zipfile.BadZipFile:
        raise
    except OSError as e:
        raise RuntimeError(str(e))


def extract_tar(tpath: Path, dest_root: Path, extracted_bytes: list, depth_notes: list):
    try:
        with tarfile.open(tpath) as t:
            for m in t:
                if not m.isfile():
                    continue
                if extracted_bytes[0] + m.size > MAX_EXTRACT_TOTAL:
                    depth_notes.append(f"stopped: extract budget hit at {tpath.name}")
                    return
                rel = sanitize_rel(m.name)
                if not rel:
                    continue
                out = safe_extract_member(dest_root, rel)
                if out is None:
                    depth_notes.append(f"skipped unsafe member {m.name} in {tpath.name}")
                    continue
                out.parent.mkdir(parents=True, exist_ok=True)
                src = t.extractfile(m)
                if src is None:
                    continue
                with open(out, "wb") as dst:
                    shutil.copyfileobj(src, dst, CHUNK)
                extracted_bytes[0] += m.size
    except (tarfile.TarError, OSError) as e:
        raise RuntimeError(str(e))


def is_archive(path: Path):
    ext = path.suffix.lower()
    if ext in (".7z", ".rar"):
        return "unsupported"
    if ext in (".zip", ".tar", ".tgz", ".tbz2", ".txz"):
        return "supported"
    if ext in (".gz", ".bz2", ".xz"):
        return "supported"
    return None


def read_first_bytes(path, n=16):
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except OSError:
        return b""


# ---------------------------------------------------------------- text mining

TAG_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'’\-]{1,}|[0-9]{2,}")
CJK_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")


def count_words(text):
    if not text:
        return 0
    return len(WORD_RE.findall(text)) + len(CJK_RE.findall(text))


def xml_text(xml_bytes):
    """Pull readable text out of OOXML/ODF: keep w:t/a:t/text:p/office:text bodies."""
    try:
        s = xml_bytes.decode("utf-8", "replace")
    except Exception:
        return ""
    # paragraph-ish boundaries
    s = re.sub(r"</(?:w:p|a:p|text:p|text:h)>", "\n", s)
    s = re.sub(r"<w:tab[^>]*/>", "\t", s)
    s = re.sub(r"<w:br[^>]*/>", "\n", s)
    # keep only text inside known text elements, else strip tags wholesale
    chunks = re.findall(r"<(?:w:t|a:t|text:span|text:s)[^>]*>(.*?)</(?:w:t|a:t|text:span|text:s)>",
                        s, re.S)
    if chunks:
        s = " ".join(chunks)
    s = TAG_RE.sub(" ", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    s = s.replace("&quot;", '"').replace("&apos;", "'").replace("&#39;", "'")
    return re.sub(r"[ \t]{2,}", " ", s).strip()


def text_from_pdf(path: Path):
    """Stdlib PDF text: decompress Flate streams, grab Tj/TJ strings."""
    raw = read_first_bytes(path, 8)
    if not raw.startswith(b"%PDF"):
        return None  # not a pdf
    try:
        data = path.read_bytes()
    except OSError:
        return None
    out = []
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        blob = m.group(1)
        try:
            blob = zlib.decompress(blob)
        except zlib.error:
            pass  # maybe uncompressed stream
        try:
            s = blob.decode("latin-1", "ignore")
        except Exception:
            continue
        if "BT" not in s:
            continue
        for sm in re.finditer(r"\(((?:\\.|[^()\\])*)\)\s*(?:Tj|TJ|'|\")", s):
            frag = sm.group(1)
            frag = re.sub(r"\\([()\\])", r"\1", frag)
            frag = re.sub(r"\\n|\\r", "\n", frag)
            out.append(frag)
    text = " ".join(out)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip() or None


def mdls_text(path: Path):
    """Spotlight's extracted text, when it has indexed the file."""
    if not sys.platform == "darwin":
        return None
    try:
        r = subprocess.run(
            ["mdls", "-raw", "-name", "kMDItemTextContent", str(path)],
            capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            t = r.stdout.strip()
            if t and t != "(null)":
                return t[:TEXT_SAMPLE]
    except Exception:
        pass
    return None


def mdls_meta(path: Path):
    keys = ["kMDItemTitle", "kMDItemAuthors", "kMDItemNumberOfPages",
            "kMDItemPixelWidth", "kMDItemPixelHeight", "kMDItemDurationSeconds",
            "kMDItemFSSize", "kMDItemContentCreationDate"]
    out = {}
    if sys.platform != "darwin":
        return out
    try:
        r = subprocess.run(["mdls"] + [f"-name{k}" for k in keys] + [str(path)],
                           capture_output=True, text=True, timeout=20)
        for line in r.stdout.splitlines():
            m = re.match(r"kMDItem(\w+)\s*=\s*(.*)$", line.strip())
            if m and m.group(2) != "(null)":
                out["kMDItem" + m.group(1)] = m.group(2).strip()
    except Exception:
        pass
    return out


def textutil_text(path: Path):
    if sys.platform != "darwin" or not shutil.which("textutil"):
        return None
    try:
        r = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)],
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout[:TEXT_SAMPLE]
    except Exception:
        pass
    return None


def extract_text(path, ext):
    """Return (text_or_None, note)."""
    path = Path(path)
    try:
        if ext in READABLE_TEXT_EXTS:
            if path.stat().st_size > 5_000_000:
                with open(path, "rb") as f:
                    return f.read(TEXT_SAMPLE).decode("utf-8", "replace"), "big file, head only"
            return path.read_text("utf-8", errors="replace")[:TEXT_SAMPLE], None

        if ext == ".docx":
            with zipfile.ZipFile(path) as z:
                return xml_text(z.read("word/document.xml")), None
        if ext == ".xlsx":
            with zipfile.ZipFile(path) as z:
                return xml_text(z.read("xl/sharedStrings.xml")), None
        if ext == ".pptx":
            with zipfile.ZipFile(path) as z:
                slides = sorted(n for n in z.namelist()
                                if re.match(r"ppt/slides/slide\d+\.xml$", n))
                return "\n\n".join(xml_text(z.read(s)) for s in slides), None
        if ext == ".odt":
            with zipfile.ZipFile(path) as z:
                return xml_text(z.read("content.xml")), None
        if ext == ".ods":
            with zipfile.ZipFile(path) as z:
                return xml_text(z.read("content.xml")), None
        if ext == ".odp":
            with zipfile.ZipFile(path) as z:
                return xml_text(z.read("content.xml")), None
        if ext in (".rtf", ".doc", ".pages", ".numbers", ".key", ".webarchive"):
            t = textutil_text(path)
            if t:
                return t, None
            return None, "no textutil result"
        if ext == ".pdf":
            t = text_from_pdf(path)
            if t and count_words(t) >= 10:
                return t, None
            t2 = mdls_text(path)
            if t2:
                return t2, "text via Spotlight"
            return None, "no extractable text (likely scan/image pdf)"
        if ext == ".eml":
            return path.read_text("utf-8", errors="replace")[:TEXT_SAMPLE], None
        if ext in MEDIA_EXTS or ext in INSTALLER_EXTS:
            return None, None
        # unknown binary-ish: skip
        return None, None
    except zipfile.BadZipFile:
        return None, "corrupt zip-based document"
    except (OSError, ValueError) as e:
        return None, f"read failed: {e}"
    except Exception as e:
        return None, f"parse failed: {e}"


# ---------------------------------------------------------------- main pass

def scan_files(root: Path, exclude: Path | None = None):
    files = []
    repo_roots = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dp = Path(dirpath)
        rel_parts = dp.relative_to(root).parts
        if exclude is not None:
            dirnames[:] = [d for d in dirnames if (dp / d).resolve() != exclude]
            if dp.resolve() == exclude:
                continue
        # do not descend into .git internals
        if ".git" in dirnames:
            repo_roots.add(str(dp))
            dirnames.remove(".git")
        for name in filenames:
            p = dp / name
            try:
                st = p.lstat()
            except OSError:
                continue
            if not stat.S_ISREG(st.st_mode):
                continue
            files.append({
                "path": str(p),
                "rel": str(p.relative_to(root)),
                "root": str(root),
                "size": st.st_size,
                "mtime": st.st_mtime,
                "ext": p.suffix.lower(),
                "depth": len(rel_parts),
                "origin": "target",
            })
    return files, repo_roots


def classify_base(f):
    """(verdict, reason) from name/size rules only. Later rules can override to KEEP-best."""
    name = Path(f["rel"]).name.lower()
    ext = f["ext"]
    rel_l = f["rel"].lower()
    parts = [p.lower() for p in Path(f["rel"]).parts[:-1]]

    if name in TRASH_NAMES or f['ext'] == "" and name.startswith("icon"):
        return J_TRASH, "OS junk file"
    if name.startswith("._") or name.startswith("~$"):
        return J_TRASH, "app lock/AppleDouble junk"
    if ext in TRASH_EXTS:
        return J_TRASH, f"temp/partial file ({ext})"
    if any(p in TRASH_PATH_PARTS for p in parts):
        return J_TRASH, "inside regenerable/cache folder"
    if f["size"] == 0:
        return J_TRASH, "empty file"
    if ext == ".git" or ".git/" in rel_l:
        return J_TRASH, "git internals"
    if ext in INSTALLER_EXTS:
        age_days = (NOW - f["mtime"]) / 86400
        if age_days > 90:
            return J_TRASH, f"installer >90d old ({int(age_days)}d)"
        return J_MAYBE, "recent installer — installed already?"
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-extract", action="store_true")
    ap.add_argument("--stage-trash", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"SWEEP: target is not a directory: {target}", file=sys.stderr)
        sys.exit(2)

    out = Path(args.out).expanduser().resolve() if args.out else target / "SWEEP-DATA"
    out.mkdir(parents=True, exist_ok=True)
    ex_dir = out / "extracted"
    tx_dir = out / "text"
    tx_dir.mkdir(parents=True, exist_ok=True)
    log(f"SWEEP — target: {target}", args.quiet)
    log(f"SWEEP — output: {out}", args.quiet)

    # ---- stage-trash mode: move trash verdicts, write undo script
    if args.stage_trash:
        vfile = out / "sweep-verdicts.json"
        if not vfile.exists():
            print("SWEEP: no sweep-verdicts.json found — run a sweep first.", file=sys.stderr)
            sys.exit(2)
        verdicts = json.loads(vfile.read_text())
        staging = out / "_TRASH-staging"
        staging.mkdir(exist_ok=True)
        undo, moved, freed = [], 0, 0
        for item in verdicts["items"]:
            if item["verdict"] != J_TRASH or item.get("origin") == "extracted":
                continue
            src = Path(item["path"])
            if not src.exists():
                continue
            dest = staging / item["rel"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                dest = staging / (dest.stem + f"__{item.get('sha8','x')}" + dest.suffix)
            shutil.move(str(src), str(dest))
            undo.append(f'mkdir -p "$(dirname "{src}")" && mv "{dest}" "{src}"')
            moved += 1
            freed += item["size"]
            for parent in sorted(src.parents):
                pf = Path(parent)
                if pf == target or pf == out:
                    break
                try:
                    next(pf.iterdir())
                except StopIteration:
                    pf.rmdir()
                except OSError:
                    pass
        (out / "undo-trash.sh").write_text(
            "#!/bin/bash\n# restores every moved file\nset -e\n" + "\n".join(undo) + "\n")
        os.chmod(out / "undo-trash.sh", 0o755)
        print(f"SWEEP: staged {moved} files ({freed/1e6:.1f} MB) into {staging}")
        print(f"SWEEP: undo anytime with: bash {out/'undo-trash.sh'}")
        return

    t0 = time.time()
    files, repo_roots = scan_files(target, exclude=out)
    log(f"SWEEP — found {len(files)} files", args.quiet)

    # ---- extract archives (target pass, then one nested pass inside extracted/)
    notes = []
    extracted_bytes = [0]
    archive_reasons = {}  # resolved path -> reason
    if not args.no_extract:
        extracted_paths = set()

        def extract_pass(file_dicts):
            for f in file_dicts:
                if extracted_bytes[0] > MAX_EXTRACT_TOTAL:
                    notes.append("extract budget reached; remaining archives left sealed")
                    return
                p = Path(f["path"])
                rp = str(p.resolve())
                kind = is_archive(p)
                if not kind or rp in extracted_paths:
                    continue
                extracted_paths.add(rp)
                if f["size"] > MAX_ARCHIVE_BYTES:
                    notes.append(f"archive too big, left sealed: {f['rel']} ({f['size']/1e6:.0f} MB)")
                    continue
                if kind == "unsupported":
                    notes.append(f"archive type needs manual handling (.7z/.rar): {f['rel']}")
                    continue
                tag = hashlib.sha256(f["rel"].encode()).hexdigest()[:8]
                dest_root = ex_dir / f"{p.stem}__{tag}"
                try:
                    suffix = p.suffix.lower()
                    if suffix == ".zip":
                        extract_zip(p, dest_root, extracted_bytes, notes)
                    elif suffix in (".gz", ".bz2", ".xz"):
                        try:
                            extract_tar(p, dest_root, extracted_bytes, notes)
                        except RuntimeError:
                            # single compressed file, not a tarball
                            import bz2, gzip, lzma
                            opener = {".gz": gzip.open, ".bz2": bz2.open, ".xz": lzma.open}[suffix]
                            dest = safe_extract_member(dest_root, p.stem) or dest_root / p.stem
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            with opener(p, "rb") as src, open(dest, "wb") as dst:
                                shutil.copyfileobj(src, dst, CHUNK)
                            extracted_bytes[0] += dest.stat().st_size
                    else:
                        extract_tar(p, dest_root, extracted_bytes, notes)
                    if dest_root.exists() and not any(dest_root.rglob("*")):
                        dest_root.rmdir()  # nothing survived extraction
                    else:
                        archive_reasons[rp] = f"archive — extracted to SWEEP-DATA/extracted/{dest_root.name}/"
                        notes.append(f"extracted: {f['rel']} -> {dest_root.name}/")
                except (zipfile.BadZipFile, RuntimeError) as e:
                    notes.append(f"archive corrupt/failed: {f['rel']} — {e}")
                    shutil.rmtree(dest_root, ignore_errors=True)

        extract_pass(files)
        if ex_dir.exists():
            for depth in (2, 3):  # archives found inside extracted output
                nested = scan_files(ex_dir, exclude=None)[0]
                before = len(extracted_paths)
                extract_pass(nested)
                if len(extracted_paths) == before:
                    break

        if ex_dir.exists():
            ex_files, _ = scan_files(ex_dir)
            for f in ex_files:
                f["origin"] = "extracted"
                f["rel"] = "(extracted) " + f["rel"]
            files.extend(ex_files)
            log(f"SWEEP — {len(ex_files)} files now visible after extraction", args.quiet)

    # ---- hash, dedupe
    for f in files:
        f["sha8"] = (sha256_of(f["path"]) or "???")[:8]
    groups = {}
    for f in files:
        groups.setdefault(f["sha8"], []).append(f)

    dupe_count = 0
    for sha, members in groups.items():
        if len(members) > 1 and sha != "???" and members[0]["size"] > 0:
            # best copy: newest mtime, then shallowest, then longest name
            best = sorted(members, key=lambda x: (-x["mtime"], x["depth"], -len(x["rel"]), x["rel"]))[0]
            for m in members:
                m["dupe_group"] = sha
            for m in members:
                if m is not best:
                    m["dupe_of"] = best["rel"]
                    dupe_count += 1

    # ---- text extraction + scoring
    for f in files:
        base_v, base_r = classify_base(f)
        words, note = 0, None
        f["verdict"], f["reasons"] = base_v or J_MAYBE, ([base_r] if base_r else [])

        if base_v == J_TRASH:
            f["words"] = 0
            continue  # no point text-mining a verdict already in the bin

        rp = str(Path(f["path"]).resolve())
        if rp in archive_reasons:
            f["reasons"].append(archive_reasons[rp])

        if f["ext"] in DOC_EXTS | READABLE_TEXT_EXTS or f["ext"] in MEDIA_EXTS:
            if f["ext"] in MEDIA_EXTS:
                meta = mdls_meta(f["path"])
                if "kMDItemPixelWidth" in meta:
                    f["reasons"].append(f"image {meta.get('kMDItemPixelWidth')}x{meta.get('kMDItemPixelHeight')}")
                if "kMDItemDurationSeconds" in meta:
                    f["reasons"].append(f"{meta['kMDItemDurationSeconds']}s media")
            elif f["ext"] not in ARCHIVE_EXTS:
                text, note = extract_text(f["path"], f["ext"])
                if text:
                    words = count_words(text)
                    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", f["rel"])[:120]
                    (tx_dir / f"{f['sha8']}_{slug}.txt").write_text(text, "utf-8")
                if note:
                    f["reasons"].append(note)

        f["words"] = words
        age_days = (NOW - f["mtime"]) / 86400
        f["age_days"] = int(age_days)

        if base_v is None:  # not already junk
            if "dupe_of" in f:
                f["verdict"] = J_TRASH
                f["reasons"] = [f"duplicate of: {f['dupe_of']}"]
            elif words >= 200:
                f["verdict"] = J_KEEP
                f["reasons"] = [f"{words} words of real content"]
            elif words >= 30:
                if age_days <= 180:
                    f["verdict"] = J_KEEP
                    f["reasons"] = [f"{words} words, recent ({f['age_days']}d old)"]
                else:
                    f["reasons"].append(f"{words} words, {f['age_days']}d old")
            else:
                f["reasons"].append("little/no extractable text — judge by eye")

    # ---- fix up extracted files lacking root-relative info & write outputs
    for f in files:
        f["mtime_s"] = datetime.fromtimestamp(f["mtime"], tz=timezone.utc).strftime("%Y-%m-%d")
        f["size_mb"] = round(f["size"] / 1e6, 3)
        f["age_days"] = f.get("age_days", int((NOW - f["mtime"]) / 86400))

    trash = [f for f in files if f["verdict"] == J_TRASH and "dupe_of" not in f]
    dupes = [f for f in files if "dupe_of" in f]
    keep = [f for f in files if f["verdict"] == J_KEEP]
    maybe = [f for f in files if f["verdict"] == J_MAYBE]
    trash_bytes = sum(f["size"] for f in trash + dupes)
    keep_bytes = sum(f["size"] for f in keep)

    def fmt_size(n):
        return f"{n/1e9:.2f} GB" if n >= 1e9 else (f"{n/1e6:.1f} MB" if n >= 1e6 else f"{n/1e3:.1f} KB")

    keep_sorted = sorted(keep, key=lambda x: (-x["words"], -x["size"]))
    trash_sorted = sorted(trash + dupes, key=lambda x: -x["size"])

    rep = []
    rep.append(f"# SWEEP REPORT — {target}")
    rep.append(f"_generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · read-only pass · nothing was deleted_\n")
    rep.append("## Overview")
    rep.append(f"| | files | bytes |\n|---|---|---|")
    rep.append(f"| **KEEP** | {len(keep)} | {fmt_size(keep_bytes)} |")
    rep.append(f"| **MAYBE** | {len(maybe)} | {fmt_size(sum(f['size'] for f in maybe))} |")
    rep.append(f"| **TRASH** | {len(trash + dupes)} | {fmt_size(trash_bytes)} |")
    rep.append(f"| total scanned | {len(files)} | {fmt_size(sum(f['size'] for f in files))} |\n")
    if notes:
        rep.append("## Extraction log")
        rep += [f"- {n}" for n in notes]
        rep.append("")
    if repo_roots:
        rep.append("## Project folders (kept whole, internals skipped)")
        rep += [f"- `{r}`" for r in sorted(repo_roots)]
        rep.append("")
    if trash_sorted:
        rep.append(f"## TRASH — {len(trash_sorted)} files, {fmt_size(trash_bytes)} reclaimable")
        rep.append("| size | file | why |")
        rep.append("|---|---|---|")
        for f in trash_sorted[:400]:
            rep.append(f"| {fmt_size(f['size'])} | `{f['rel']}` | {'; '.join(f['reasons'])} |")
        if len(trash_sorted) > 400:
            rep.append(f"| … | {len(trash_sorted)-400} more, see sweep-manifest.csv | |")
        rep.append("")
    if maybe:
        rep.append(f"## MAYBE — {len(maybe)} files needing eyes")
        media = [f for f in maybe if f["ext"] in MEDIA_EXTS]
        other = [f for f in maybe if f["ext"] not in MEDIA_EXTS]
        if other:
            rep.append("| size | file | note |")
            rep.append("|---|---|---|")
            for f in sorted(other, key=lambda x: -x["size"])[:200]:
                rep.append(f"| {fmt_size(f['size'])} | `{f['rel']}` | {'; '.join(f['reasons']) or '—'} |")
            rep.append("")
        if media:
            rep.append(f"**{len(media)} media files** (images/audio/video) — can't judge content without looking:")
            for f in sorted(media, key=lambda x: -x["size"])[:60]:
                rep.append(f"- {fmt_size(f['size'])} `{f['rel']}` ({'; '.join(f['reasons']) or f['ext']})")
            if len(media) > 60:
                rep.append(f"- … {len(media)-60} more")
            rep.append("")
    if keep_sorted:
        rep.append(f"## KEEP — {len(keep)} files with substance")
        rep.append("| words | size | file |")
        rep.append("|---|---|---|")
        for f in keep_sorted[:300]:
            rep.append(f"| {f['words']} | {fmt_size(f['size'])} | `{f['rel']}` |")
        if len(keep_sorted) > 300:
            rep.append(f"| … | | {len(keep_sorted)-300} more, see manifest |")
        rep.append("")
    if dupe_count or any("dupe_group" in f for f in files):
        rep.append("## Duplicate groups")
        seen = {}
        for f in files:
            if "dupe_of" in f:
                seen.setdefault(f["dupe_group"], {"keep": None, "drops": []})
        for f in files:
            g = seen.get(f.get("dupe_group"))
            if g:
                if "dupe_of" in f:
                    g["drops"].append(f["rel"])
                else:
                    g["keep"] = f["rel"]
        for sha, g in list(seen.items())[:100]:
            rep.append(f"- keep `{g['keep']}`  ·  drop: " + ", ".join(f"`{d}`" for d in g["drops"]))
        rep.append("")

    (out / "SWEEP-REPORT.md").write_text("\n".join(rep), "utf-8")

    with open(out / "sweep-manifest.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["verdict", "rel_path", "size_bytes", "words", "age_days", "mtime",
                    "sha8", "dupe_of", "reasons", "origin"])
        for f in sorted(files, key=lambda x: ({"TRASH": 0, "MAYBE": 1, "KEEP": 2}[x["verdict"]], -x["size"])):
            w.writerow([f["verdict"], f["rel"], f["size"], f["words"], f["age_days"],
                        f["mtime_s"], f["sha8"], f.get("dupe_of", ""), "; ".join(f["reasons"]),
                        f["origin"]])

    json.dump({
        "target": str(target), "generated": datetime.now().isoformat(timespec="seconds"),
        "notes": notes,
        "counts": {"keep": len(keep), "maybe": len(maybe),
                   "trash": len(trash + dupes), "total": len(files),
                   "reclaimable_bytes": trash_bytes},
        "items": [{k: f.get(k) for k in ("path", "rel", "verdict", "reasons", "size",
                                         "words", "sha8", "dupe_of", "origin", "mtime")}
                  for f in files],
    }, open(out / "sweep-verdicts.json", "w"), indent=1)

    # compiled corpus of all extracted text, one searchable file
    corpus = out / "CORPUS-ALL-DOCUMENTS.md"
    parts = [f"# Compiled corpus — {target}\n"]
    for f in sorted(keep, key=lambda x: x["rel"]) + sorted(maybe, key=lambda x: x["rel"]):
        tx = None
        if tx_dir.exists():
            for cand in tx_dir.glob(f"{f['sha8']}_*"):
                tx = cand.read_text("utf-8", errors="replace")
                break
        if tx and tx.strip():
            parts.append(f"\n\n---\n## {f['rel']}\n_{f['verdict']} · {fmt_size(f['size'])} · {f['words']} words · modified {f['mtime_s']}_\n\n{tx[:20000]}")
    corpus.write_text("\n".join(parts), "utf-8")

    dt = time.time() - t0
    log(f"SWEEP done in {dt:.1f}s — {len(keep)} KEEP · {len(maybe)} MAYBE · "
        f"{len(trash+dupes)} TRASH ({fmt_size(trash_bytes)} reclaimable)", args.quiet)
    log(f"  report:  {out/'SWEEP-REPORT.md'}", args.quiet)
    log(f"  corpus:  {corpus}", args.quiet)
    log(f"  data:    {out/'sweep-manifest.csv'} + sweep-verdicts.json", args.quiet)


if __name__ == "__main__":
    main()
