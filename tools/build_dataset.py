#!/usr/bin/env python3
"""Assemble canonical Swaralipi-JSON song files from parsed NLTR grids + curated metadata."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from parse_nltr import parse_song

ROOT = Path(__file__).parent.parent
RETRIEVED = "2026-08-11"

# Witness URLs must use the archive's precomposed Bengali nukta characters
# (য় ড় ঢ়). See tools/fetch_sources.py — Unicode NFC does not do this for you.

# Songs checked line-by-line against scans of the printed Swarabitan (Visva-Bharati),
# not only against the online witness. docs/VERIFICATION.md holds the full record:
# which page images were consulted, what matched, and every discrepancy found.
SCAN_VERIFIED = {
    "purano-sei-diner-katha": {
        "swarabitan_volume": 32,
        "song_number_in_volume": 16,
        "scan": "https://archive.org/details/in.ernet.dli.2015.339540",
        "checked": "2026-08-11",
        "scope": "lines 1-6 (sthayi through first antara): every matra and lyric syllable",
        "result": "exact match",
        "printed_header": "মিশ্র ভূপালী । একতাল",
        "notes": [
            "The printed header confirms ektaal and supplies a raga the online witness omits: Mishra Bhupali, a pentatonic raga — consistent both with the song's Auld Lang Syne origin and with the pentatonic note-set the data itself shows.",
            "Line 4, matra 5: the udara mark under the second ধা is ambiguous in this scan. We keep the witness reading (udara), which fits the surrounding low-register phrase.",
        ],
    },
    "bhalobese-sokhi": {
        "swarabitan_volume": 56,
        "song_number_in_volume": 19,
        "scan": "https://archive.org/details/in.ernet.dli.2015.336651",
        "checked": "2026-08-11",
        "scope": "lines 1-2 (sthayi): every matra and lyric syllable",
        "result": "exact match",
        "printed_header": "none — no raga/taal line is printed for this song",
        "notes": [
            "Resolves a conflict with a secondary source. geetabitan.com lists this song as Dadra; the printed page carries no taal line and no vibhag dandas anywhere in the notation, which is how Swarabitan sets a talamukta (free-rhythm) song. The talamukta reading stands.",
            "Three-note matras in the print (গমপা, গমগা) match the corpus's matra-fraction encoding exactly.",
        ],
    },
    "gram-chhara-oi-ranga-matir-path": {
        "swarabitan_volume": 9,
        "song_number_in_volume": 22,
        "scan": "https://archive.org/details/in.ernet.dli.2015.339565",
        "checked": "2026-08-11",
        "scope": "line 1 (sthayi): all 16 matras and lyric syllables",
        "result": "exact match",
        "printed_header": "বাংলা । কাহারবা",
        "notes": [
            "The printed header confirms kaharba and gives the anga as বাংলা (Bangla), correcting the 'Baul-anga' attribution previously recorded here from tradition rather than from a source.",
            "Validates the corpus's kan (grace-note) encoding: where we write a kan, the print sets the ornamenting swara as a smaller raised glyph (মগা) — the akarmatrik convention for kan.",
        ],
    },
}

TAALS = {
    "ektaal":  {"name": {"bn": "একতাল", "translit": "ektaal"}, "matras": 12, "vibhags": [3, 3, 3, 3],
                "beats": ["sam", "taali", "khali", "taali"], "talamukta": False},
    "dadra":   {"name": {"bn": "দাদরা", "translit": "dadra"}, "matras": 6, "vibhags": [3, 3],
                "beats": ["sam", "khali"], "talamukta": False},
    "kaharba": {"name": {"bn": "কাহারবা", "translit": "kaharba"}, "matras": 8, "vibhags": [4, 4],
                "beats": ["sam", "khali"], "talamukta": False},
    "khemta":  {"name": {"bn": "খেমটা", "translit": "khemta"}, "matras": 6, "vibhags": [3, 3],
                "beats": ["sam", "khali"], "talamukta": False},
    "tintal":  {"name": {"bn": "তিনতাল", "translit": "tintal"}, "matras": 16, "vibhags": [4, 4, 4, 4],
                "beats": ["sam", "taali", "khali", "taali"], "talamukta": False},
    "talamukta": {"name": {"bn": "তালমুক্ত", "translit": "talamukta"}, "matras": None, "vibhags": None,
                  "beats": None, "talamukta": True},
    # --- taals added in v0.2 -------------------------------------------------
    # Where the witness states the vibhag division in its taal label — e.g.
    # "ধামার(৩/২/২/৩/৪)" — that division is used verbatim and marked `stated`.
    # Where it does not, the division below is the standard one for that taal and
    # was cross-checked against the bar structure the notation itself prints; the
    # affected songs say so in their confidence notes.
    # `beats` (sam/taali/khali) is left null for these: the witness does not mark
    # them and we will not invent them.
    "teora":      {"name": {"bn": "তেওড়া", "translit": "teora"}, "matras": 7, "vibhags": [3, 2, 2],
                   "beats": None, "talamukta": False},
    "jhanp":      {"name": {"bn": "ঝাঁপ", "translit": "jhanp"}, "matras": 10, "vibhags": [2, 3, 2, 3],
                   "beats": None, "talamukta": False},
    "jhampak":    {"name": {"bn": "ঝম্পক", "translit": "jhampak"}, "matras": 5, "vibhags": [3, 2],
                   "beats": None, "talamukta": False},
    # The archive labels this song's taal দাদরা, but the page prints a five-matra
    # avartan divided 2+3 (bars every 5 cells, আবর্তন ৩ over a 15-cell line) —
    # not the six-matra dadra. We record what the page notates and flag the
    # conflict; see this song's confidence notes.
    "dadra_5":    {"name": {"bn": "দাদরা", "translit": "dadra (5-matra setting as printed)"},
                   "matras": 5, "vibhags": [2, 3], "beats": None, "talamukta": False},
    "sasthi":     {"name": {"bn": "ষষ্ঠী", "translit": "sasthi"}, "matras": 6, "vibhags": [2, 4],
                   "beats": None, "talamukta": False},
    "kawwali":    {"name": {"bn": "কাওয়ালি", "translit": "kawwali"}, "matras": 8, "vibhags": [4, 4],
                   "beats": None, "talamukta": False},
    "dhamar":     {"name": {"bn": "ধামার", "translit": "dhamar"}, "matras": 14, "vibhags": [3, 2, 2, 3, 4],
                   "beats": None, "talamukta": False},
    "surfank":    {"name": {"bn": "সুরফাঁক", "translit": "surfank"}, "matras": 10, "vibhags": [4, 2, 4],
                   "beats": None, "talamukta": False},
    "chautal":    {"name": {"bn": "চৌতাল", "translit": "chautal"}, "matras": 12,
                   "vibhags": [2, 2, 2, 2, 2, 2], "beats": None, "talamukta": False},
    "ardha_jhanp":{"name": {"bn": "অর্দ্ধঝাঁপ", "translit": "ardha-jhanp"}, "matras": 5, "vibhags": [2, 3],
                   "beats": None, "talamukta": False},
    "rupak":      {"name": {"bn": "রুপক", "translit": "rupak"}, "matras": 7, "vibhags": [3, 2, 2],
                   "beats": None, "talamukta": False},
    "rupakra":    {"name": {"bn": "রুপকড়া", "translit": "rupakra"}, "matras": 8, "vibhags": [3, 2, 3],
                   "beats": None, "talamukta": False},
    "madhyaman":  {"name": {"bn": "মধ্যমান", "translit": "madhyaman"}, "matras": 16,
                   "vibhags": [4, 4, 4, 4], "beats": None, "talamukta": False},
    "arathheka":  {"name": {"bn": "আড়াঠেকা", "translit": "arathheka"}, "matras": 16,
                   "vibhags": [4, 4, 4, 4], "beats": None, "talamukta": False},

}

NLTR_BASE = "https://rabindra-rachanabali.nltr.org"

# The song table lives in sources/songs.json, not in this file, so that adding a song
# is a data edit rather than a code edit — see CONTRIBUTING.md. Each entry gives the
# witness path, the curated metadata, and the confidence statement for that song.
SONGS_FILE = ROOT / "sources" / "songs.json"


def load_songs():
    songs = json.loads(SONGS_FILE.read_text(encoding="utf-8"))
    for cfg in songs:
        cfg.setdefault("file", cfg["id"])
        cfg.setdefault("secondary", [])
        cfg.setdefault("raga_anga", None)
        cfg.setdefault("retrieved", RETRIEVED)
        if not cfg["url"].startswith("http"):
            cfg["url"] = NLTR_BASE + cfg["url"]
        unknown = set(cfg["taal"].split()) - set(TAALS)
        if cfg["taal"] not in TAALS:
            raise SystemExit(f"{cfg['id']}: unknown taal {cfg['taal']!r}. "
                             f"Add it to TAALS in {__file__}.")
    return songs


def guess_sections(lines, n):
    """Label lines by section using section_bar marks as boundaries (best-effort)."""
    sections = []
    current = 0
    names = ["sthayi", "antara", "sanchari", "abhog", "body5", "body6", "body7", "body8"]
    for ln in lines:
        sections.append(names[min(current, len(names) - 1)])
        if any(m["type"] == "section_bar" and m["cell"] >= len(ln["cells"]) - 1 for m in ln["marks"]):
            current += 1
    return sections

def build():
    outdir = ROOT / "data" / "songs"
    outdir.mkdir(parents=True, exist_ok=True)
    for cfg in load_songs():
        parsed = parse_song(ROOT / "sources" / "raw" / f"{cfg['file']}.html")
        lines = []
        secs = guess_sections(parsed["lines"], len(parsed["lines"]))
        taal = TAALS[cfg["taal"]]
        for i, (ln, sec) in enumerate(zip(parsed["lines"], secs), start=1):
            for c in ln["cells"]:
                for u in c["units"]:
                    u.pop("_raw", None)
            entry = {"line_no": i, "section": sec, "cells": ln["cells"], "marks": ln["marks"]}
            if taal["matras"] and len(ln["cells"]) < taal["matras"]:
                entry["anacrusis"] = True
            lines.append(entry)
        doc = {
            "schema_version": "0.1",
            "id": cfg["id"],
            "title": cfg["title"],
            "composer": "Rabindranath Tagore",
            "parjaay": cfg["parjaay"],
            "raga_anga": cfg["raga_anga"],
            "taal": taal,
            "sections": sorted(set(secs), key=secs.index),
            "lines": lines,
            "provenance": {
                "primary_witness": {
                    "archive": "SNLTR Rabindra Rachanabali digital edition (digitization of Swarabitan, Visva-Bharati)",
                    "url": cfg["url"],
                    "retrieved": cfg["retrieved"],
                    "taal_as_stated": parsed["meta"]["taal"] or "",
                },
                "scan_verification": SCAN_VERIFIED.get(cfg["id"]),
                "secondary_witnesses": cfg["secondary"],
                "encoding_method": "automated parse of the witness's notation grid (tools/parse_nltr.py) + manual review of every line",
                "known_deviations": [],
            },
            "confidence": cfg["confidence"],
        }
        out = outdir / f"{cfg['id']}.json"
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {out.name}: {len(lines)} lines, "
              f"{sum(len(l['cells']) for l in lines)} cells")

if __name__ == "__main__":
    build()
