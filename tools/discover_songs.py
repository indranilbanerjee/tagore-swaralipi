#!/usr/bin/env python3
"""
discover_songs.py — map which Rabindrasangeet actually have machine-readable
notation in the witness archive, and where.

Why this exists: finding a song's swaralipi URL by guessing its Bengali title is
unreliable (see the nukta problem in fetch_sources.py — four of our first ten URLs
silently returned an empty viewer page). The archive's own lyric pages carry the
link, so crawling them yields URLs that are correct by construction, plus the
parjaay the archive itself assigns — better provenance than attributing it to
tradition.

Writes sources/catalogue.json:
    [{node, parjaay, gaan, url, taal, abarton, name}, ...]

    python tools/discover_songs.py            # crawl + header lookup
    python tools/discover_songs.py --range 3500 6700
"""
import argparse, json, re, sys, threading, time
import concurrent.futures as cf
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from fetch_sources import fetch  # noqa: E402

BASE = "https://rabindra-rachanabali.nltr.org"
OUT = ROOT / "sources" / "catalogue.json"
_lock = threading.Lock()
_done = [0]


def lyric_node(nid):
    """Return {node, parjaay, gaan} if this lyric page links to a swaralipi."""
    try:
        html = fetch(f"{BASE}/node/{nid}").decode("utf-8", "replace")
    except Exception:
        return None
    finally:
        with _lock:
            _done[0] += 1
            if _done[0] % 200 == 0:
                print(f"  ...{_done[0]} nodes", flush=True)
    m = re.search(r"href='16053\?gaan=([^']+)'", html)
    if not m:
        return None
    title = re.search(r"<title>([^<]*)</title>", html)
    parjaay = (title.group(1).split("|")[0].strip() if title else "")
    return {"node": nid, "parjaay": re.sub(r"[,\s]*[০-৯]+$", "", parjaay).strip(),
            "gaan": m.group(1)}


def header(entry):
    """Fetch the swaralipi page and read its নাম / তাল / আবর্তন header."""
    url = f"{BASE}/node/16053?gaan={entry['gaan']}"
    try:
        html = fetch(url).decode("utf-8", "replace")
    except Exception as exc:
        entry["error"] = str(exc)[:60]
        return entry
    spans = [s.strip() for s in re.findall(r"<span class='style3'>([^<]*)</span>", html)]
    labels = {"নাম": "name", "তাল": "taal", "আবর্তন": "abarton"}
    for i, v in enumerate(spans):
        if v in labels and i + 2 < len(spans) and spans[i + 1].strip() == ":":
            entry[labels[v]] = spans[i + 2].strip()
    # a page with no notation grid returns the bare viewer shell
    entry["cells"] = len(re.findall(r"<td[^>]*id=\"?[\d.]+\"?", html))
    entry["url"] = url
    return entry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", nargs=2, type=int, default=[3500, 6700])
    ap.add_argument("--workers", type=int, default=5)
    args = ap.parse_args()

    lo, hi = args.range
    print(f"Crawling lyric nodes {lo}-{hi} for swaralipi links...")
    hits = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(lyric_node, range(lo, hi)):
            if r:
                hits.append(r)
    print(f"{len(hits)} songs carry a swaralipi link.")

    print("Reading each song's header (name / taal / avartan)...")
    out = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        for r in ex.map(header, hits):
            out.append(r)
    out.sort(key=lambda e: e["node"])
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    usable = [e for e in out if e.get("cells", 0) > 40]
    taals = {}
    for e in usable:
        taals[e.get("taal", "?")] = taals.get(e.get("taal", "?"), 0) + 1
    print(f"\nwrote {OUT.relative_to(ROOT)} — {len(out)} songs, {len(usable)} with a notation grid")
    print("taals found:", dict(sorted(taals.items(), key=lambda kv: -kv[1])))


if __name__ == "__main__":
    main()
