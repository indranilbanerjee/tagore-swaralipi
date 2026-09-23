#!/usr/bin/env python3
"""
explore.py — five questions you can only ask once the notation is data.

Run:  python examples/explore.py

Nothing here needs a library beyond the standard one. The point is that each of these
took a few lines to answer, and none of them could be answered at all a week ago
without a person reading sixty volumes by hand.
"""
import glob
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFSET = {"S": 0, "R": 2, "G": 4, "M": 5, "P": 7, "D": 9, "N": 11}


def load_songs():
    return [json.load(open(f, encoding="utf-8"))
            for f in sorted(glob.glob(str(ROOT / "data" / "songs" / "*.json")))]


def name(sw):
    n = sw["degree"]
    if sw.get("komal"):
        n = n.lower()
    if sw.get("kori"):
        n = "M#"
    return n + {1: "'", -1: ","}.get(sw.get("saptak", 0), "")


def swaras(doc):
    """Every pitched swara in a song, in order."""
    return [u["swara"] for line in doc["lines"] for cell in line["cells"]
            for u in cell["units"] if u["type"] == "swara"]


def q1_note_vocabulary(songs):
    print("\n1. What notes does each song actually use?")
    print("   (no raga was assumed anywhere in the pipeline — this is what the data contains)\n")
    for doc in songs:
        used = sorted({name(s) for s in swaras(doc)},
                      key=lambda n: (0 if "," in n else (2 if "'" in n else 1),
                                     "SrRgGmMPdDnN".find(n[0])))
        flag = ""
        if not ({n.rstrip("',") for n in used} - {"S", "R", "G", "P", "D"}):
            flag = "  <- pentatonic"
        print(f"   {doc['id'][:34]:34s} {' '.join(used)}{flag}")


def q2_cadences(songs):
    print("\n2. Where do lines come to rest?")
    print("   The last pitched note of every line, pooled by taal.\n")
    by_taal = {}
    for doc in songs:
        taal = "talamukta" if doc["taal"]["talamukta"] else doc["taal"]["name"]["translit"]
        for line in doc["lines"]:
            pitched = [u["swara"] for cell in line["cells"]
                       for u in cell["units"] if u["type"] == "swara"]
            if pitched:
                by_taal.setdefault(taal, Counter())[name(pitched[-1])] += 1
    for taal, counter in sorted(by_taal.items()):
        top = ", ".join(f"{n}×{c}" for n, c in counter.most_common(4))
        print(f"   {taal:12s} {top}")


def q3_sam(songs):
    print("\n3. What note does the corpus land on at sam (beat 1 of the cycle)?")
    print("   Sam is the anchor of the taal; what sits there is a real stylistic fact.\n")
    counter = Counter()
    for doc in songs:
        taal = doc["taal"]
        if taal["talamukta"]:
            continue
        for line in doc["lines"]:
            for i, cell in enumerate(line["cells"]):
                if i % taal["matras"] != 0:
                    continue
                for u in cell["units"]:
                    if u["type"] == "swara":
                        counter[name(u["swara"])] += 1
                        break
    total = sum(counter.values())
    for note, count in counter.most_common(6):
        print(f"   {note:4s} {count:3d}  {100*count/total:4.1f}%  {'█' * round(30*count/total)}")


def q4_phrases(songs):
    print("\n4. Which melodic phrases recur across different songs?")
    print("   4-note sequences (as intervals from the first note, so key-independent)\n")
    seen = {}
    for doc in songs:
        seq = swaras(doc)
        vals = [OFFSET[s["degree"]] + 12 * s.get("saptak", 0)
                - (1 if s.get("komal") else 0) + (1 if s.get("kori") else 0) for s in seq]
        names = [name(s) for s in seq]
        for i in range(len(vals) - 3):
            shape = tuple(v - vals[i] for v in vals[i:i + 4])
            seen.setdefault(shape, {"songs": set(), "example": " ".join(names[i:i + 4])})
            seen[shape]["songs"].add(doc["id"])
    threshold = max(3, int(len(songs) * 0.6))
    shared = sorted(((len(v["songs"]), v["example"], shape) for shape, v in seen.items()
                     if len(v["songs"]) >= threshold), reverse=True)[:6]
    for count, example, shape in shared:
        print(f"   in {count:2d}/{len(songs)} songs   e.g. {example:22s} intervals {shape}")


def q5_melisma(songs):
    print("\n5. How much of this music is melisma?")
    print("   i.e. matras where a syllable is still sounding rather than a new one starting\n")
    for doc in songs:
        cells = [c for line in doc["lines"] for c in line["cells"]]
        held = sum(1 for c in cells if c["lyric"] is None)
        print(f"   {doc['id'][:34]:34s} {100*held/len(cells):4.1f}% of matras carry no new syllable")


if __name__ == "__main__":
    songs = load_songs()
    print(f"Loaded {len(songs)} songs from data/songs/")
    q1_note_vocabulary(songs)
    q2_cadences(songs)
    q3_sam(songs)
    q4_phrases(songs)
    q5_melisma(songs)
    print("\nEach answer above is a few lines of Python over data/songs/*.json.")
