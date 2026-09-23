#!/usr/bin/env python3
"""
fetch_sources.py — download the witness pages this corpus was encoded from.

The witness HTML is deliberately **not redistributed** in this repository. The
compositions are public domain, but the archive that serves the notation asserts
rights over its own digitization, and re-hosting its pages is both legally
unnecessary for us and inconsistent with what we ask contributors to do.

So: this script fetches the pages into `sources/raw/` (git-ignored), after which
`tools/build_dataset.py` reproduces `data/songs/*.json` byte-for-byte.

    python tools/fetch_sources.py
    python tools/build_dataset.py

Be polite to the archive — this sleeps between requests and is meant to be run
once, not in a loop.
"""
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

OUT = ROOT / "sources" / "raw"
DELAY_SECONDS = 2
USER_AGENT = (
    "tagore-swaralipi/0.1 (open research corpus; "
    "https://github.com/indranilbanerjee/tagore-swaralipi)"
)


# The archive writes য় ড় ঢ় as single precomposed characters, while these same
# letters are often typed (and stored elsewhere) as base + nukta. Unicode NFC will
# NOT fix this: Bengali nukta pairs are composition exclusions. So compose them
# explicitly, or four of the ten witness URLs silently return an empty viewer page
# instead of the notation — a failure mode that looks like success.
NUKTA_PAIRS = {
    "\u09af\u09bc": "\u09df",  # ya + nukta  -> ya-nukta   (য় )
    "\u09a1\u09bc": "\u09dc",  # dda + nukta -> rra        (ড় )
    "\u09a2\u09bc": "\u09dd",  # ddha + nukta-> rha        (ঢ় )
}


def compose_nukta(text):
    """Normalise Bengali nukta sequences to the archive's precomposed form."""
    for pair, composed in NUKTA_PAIRS.items():
        text = text.replace(pair, composed)
    return text


def targets():
    """(local filename, url) for every witness page, read from the dataset builder."""
    from build_dataset import SONGS
    return [(f"{cfg['file']}.html", cfg["url"]) for cfg in SONGS]


def fetch(url):
    # The archive's URLs carry Bengali titles; percent-encode the path safely.
    parts = urllib.parse.urlsplit(compose_nukta(url))
    safe = urllib.parse.urlunsplit((
        parts.scheme,
        parts.netloc,
        urllib.parse.quote(parts.path, safe="/%"),
        urllib.parse.quote(parts.query, safe="=&%"),
        parts.fragment,
    ))
    request = urllib.request.Request(safe, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pending = [(name, url) for name, url in targets() if not (OUT / name).exists()]
    if not pending:
        print(f"All witness pages already present in {OUT.relative_to(ROOT)}/")
        return 0

    print(f"Fetching {len(pending)} witness page(s) into {OUT.relative_to(ROOT)}/\n")
    failures = []
    for index, (name, url) in enumerate(pending, start=1):
        try:
            body = fetch(url)
            (OUT / name).write_bytes(body)
            print(f"  [{index}/{len(pending)}] {name}  ({len(body):,} bytes)")
        except Exception as exc:  # noqa: BLE001 - report and continue
            failures.append((name, exc))
            print(f"  [{index}/{len(pending)}] {name}  FAILED: {exc}")
        if index < len(pending):
            time.sleep(DELAY_SECONDS)

    if failures:
        print(
            f"\n{len(failures)} page(s) could not be fetched. The archive's URLs encode "
            "Bengali titles and occasionally change; the canonical URL for each song is "
            "recorded in that song's provenance block in data/songs/."
        )
        return 1

    print("\nDone. Now run:  python tools/build_dataset.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
