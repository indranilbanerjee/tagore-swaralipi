"""
Corpus integrity tests.

These exist so that a contributor correcting a matra in a song they know by heart cannot
accidentally break the dataset — and so that anyone can verify our claims about the data
rather than taking them on trust. Every test states what it is protecting.

Run:  python -m pytest tests/ -v
"""
import glob
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

SONG_FILES = sorted(glob.glob(str(ROOT / "data" / "songs" / "*.json")))
SONG_IDS = [Path(f).stem for f in SONG_FILES]

OFFSET = {"S": 0, "R": 2, "G": 4, "M": 5, "P": 7, "D": 9, "N": 11}
KOMAL_ALLOWED = {"R", "G", "D", "N"}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="session")
def songs():
    assert SONG_FILES, "no song files found in data/songs/"
    return {Path(f).stem: load(f) for f in SONG_FILES}


# --------------------------------------------------------------------------
# Structure
# --------------------------------------------------------------------------

def test_corpus_is_not_empty():
    """The repo should never ship with an empty corpus."""
    assert len(SONG_FILES) >= 10


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_validates_against_json_schema(song_file):
    """Every song must satisfy schema/swaralipi.schema.json."""
    jsonschema = pytest.importorskip("jsonschema")
    schema = load(ROOT / "schema" / "swaralipi.schema.json")
    errors = list(jsonschema.Draft202012Validator(schema).iter_errors(load(song_file)))
    assert not errors, "\n".join(
        f"{list(e.path)[:6]}: {e.message}" for e in errors[:5]
    )


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_id_matches_filename(song_file):
    assert load(song_file)["id"] == Path(song_file).stem


def test_ids_are_unique(songs):
    ids = [s["id"] for s in songs.values()]
    assert len(ids) == len(set(ids))


# --------------------------------------------------------------------------
# Musical correctness — the checks a schema can't express
# --------------------------------------------------------------------------

@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_komal_and_kori_are_musically_possible(song_file):
    """
    Sa and Pa have no komal form; only Ma takes kori (tivra). A decoding bug that
    invented, say, a komal Pa would show up here and nowhere else.
    """
    doc = load(song_file)
    for line in doc["lines"]:
        for cell in line["cells"]:
            for unit in cell["units"]:
                for sw in [unit.get("swara")] + list(unit.get("kan") or []):
                    if not sw:
                        continue
                    if sw.get("komal"):
                        assert sw["degree"] in KOMAL_ALLOWED, (
                            f"{doc['id']} line {line['line_no']}: komal {sw['degree']} is not a note"
                        )
                    if sw.get("kori"):
                        assert sw["degree"] == "M", (
                            f"{doc['id']} line {line['line_no']}: kori {sw['degree']} is not a note"
                        )


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_taal_cycles_close(song_file):
    """
    In a taal-bound song every line should hold a whole number of avartan cycles,
    allowing for a printed pickup (anacrusis) line. This is the arithmetic that
    catches a dropped or doubled matra during transcription.
    """
    doc = load(song_file)
    taal = doc["taal"]
    if taal["talamukta"]:
        pytest.skip("talamukta (free rhythm): no cycle to close")
    matras = taal["matras"]
    assert sum(taal["vibhags"]) == matras, "vibhags must sum to the matra count"
    if taal.get("beats"):
        assert len(taal["beats"]) == len(taal["vibhags"])
    offenders = [
        line["line_no"]
        for line in doc["lines"]
        if not line.get("anacrusis") and len(line["cells"]) % matras != 0
    ]
    # Printed pages carry pickup cells at line ends; we assert the corpus does not
    # drift worse than the state we verified by ear at v0.1.
    assert len(offenders) <= 4, f"{doc['id']}: lines off-cycle: {offenders}"


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_assigned_taal_matches_the_printed_bar_structure(song_file):
    """
    In akarmatrik notation the bar line marks the avartan (the taal cycle) and the
    vibhag marks divide it. So the page itself states the cycle length, and the taal
    we assign must agree with it.

    This exists because it caught a real error: jhampak was entered as ten matras
    from Hindustani Jhaptaal, while every page printed bars every five cells —
    Rabindrasangeet uses its own taal system. Theory lost to the notation, as it
    should.
    """
    from collections import Counter

    doc = load(song_file)
    if doc["taal"]["talamukta"]:
        pytest.skip("talamukta: no cycle printed")
    cycles = Counter()
    for line in doc["lines"]:
        n = len(line["cells"])
        bars = sorted({m["cell"] for m in line["marks"]
                       if m["type"] in ("bar", "section_bar")} | {n})
        prev = 0
        for b in bars:
            if 0 < b <= n and b - prev > 1:
                cycles[b - prev] += 1
            prev = b
    if not cycles:
        pytest.skip("no bar lines recorded for this song")
    printed = cycles.most_common(1)[0][0]
    assigned = doc["taal"]["matras"]
    assert printed % assigned == 0 or assigned % printed == 0, (
        f"{doc['id']}: taal is recorded as {assigned} matras but the page prints "
        f"its bars every {printed} cells"
    )


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_no_empty_cells_and_no_orphan_sustain(song_file):
    """
    Every matra must contain something, and a song cannot open by sustaining a
    note that was never struck.
    """
    doc = load(song_file)
    for line in doc["lines"]:
        assert line["cells"], f"{doc['id']} line {line['line_no']} has no cells"
        for cell in line["cells"]:
            assert cell["units"], f"{doc['id']} line {line['line_no']} has an empty matra"
    first_line = next((l for l in doc["lines"] if not l.get("anacrusis")), doc["lines"][0])
    assert first_line["cells"][0]["units"][0]["type"] != "sustain"


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_pitch_range_is_singable(song_file):
    """
    Rabindrasangeet sits within roughly two octaves around the tonic. A range wider
    than three octaves means an octave marker was misparsed.
    """
    doc = load(song_file)
    semitones = []
    for line in doc["lines"]:
        for cell in line["cells"]:
            for unit in cell["units"]:
                sw = unit.get("swara")
                if not sw:
                    continue
                v = OFFSET[sw["degree"]] + 12 * sw.get("saptak", 0)
                v += -1 if sw.get("komal") else 0
                v += 1 if sw.get("kori") else 0
                semitones.append(v)
    assert semitones, f"{doc['id']} contains no pitched notes"
    span = max(semitones) - min(semitones)
    assert span <= 36, f"{doc['id']} spans {span} semitones — an octave mark is probably wrong"


# --------------------------------------------------------------------------
# Provenance — the promises the README makes about this data
# --------------------------------------------------------------------------

@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_every_song_states_where_it_came_from(song_file):
    """No song may enter the corpus without a citable witness and a retrieval date."""
    prov = load(song_file)["provenance"]
    witness = prov["primary_witness"]
    assert witness["archive"].strip()
    assert witness["url"].startswith("http")
    assert len(witness["retrieved"]) == 10 and witness["retrieved"][4] == "-"
    assert prov["encoding_method"].strip()


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_confidence_is_declared(song_file):
    doc = load(song_file)
    assert doc["confidence"]["level"] in {"high", "medium", "low"}
    if doc["confidence"]["level"] != "high":
        assert doc["confidence"].get("notes"), (
            f"{doc['id']}: non-high confidence must explain itself"
        )


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_scan_verification_is_evidenced(song_file):
    """
    A song may only claim to have been checked against the printed Swarabitan if it
    says which volume, which scan, when, how much was checked, and what came out.
    An unevidenced verification claim is worse than none.
    """
    record = load(song_file)["provenance"].get("scan_verification")
    if record is None:
        return
    assert isinstance(record["swarabitan_volume"], int)
    assert record["scan"].startswith("http")
    assert len(record["checked"]) == 10
    assert record["scope"].strip()
    assert record["result"] in {"exact match", "match with noted differences", "differences found"}
    if record["result"] != "exact match":
        assert record.get("notes"), "a non-exact result must say what differed"


def test_corpus_reports_its_verification_state(songs):
    """The README claims a specific number of scan-verified songs; keep that honest."""
    verified = [s["id"] for s in songs.values() if s["provenance"].get("scan_verification")]
    assert len(verified) >= 3, verified


# --------------------------------------------------------------------------
# Round-trip — the guarantee that makes human editing safe
# --------------------------------------------------------------------------

def _pitch_stream(lines):
    """(kind, semitone, matra-fraction) for every unit, in order."""
    stream = []
    for line in lines:
        for cell in line["cells"]:
            frac = round(1.0 / len(cell["units"]), 6)
            for unit in cell["units"]:
                if unit["type"] == "swara":
                    sw = unit["swara"]
                    v = OFFSET[sw["degree"]] + 12 * sw.get("saptak", 0)
                    v += -1 if sw.get("komal") else 0
                    v += 1 if sw.get("kori") else 0
                    stream.append(("note", v, frac))
                else:
                    stream.append((unit["type"], None, frac))
    return stream


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_text_roundtrip_is_lossless(song_file):
    """
    JSON → human-readable sargam-text → JSON must preserve every pitch and duration.

    This is what lets a musician edit `data/text/` by hand, or a model emit notation in
    that format, without the canonical data drifting.
    """
    from render_text import render
    from parse_text import parse_lines

    doc = load(song_file)
    reparsed = parse_lines(render(doc))
    assert _pitch_stream(reparsed) == _pitch_stream(doc["lines"])


@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_published_text_matches_the_json(song_file):
    """`data/text/` must not fall out of sync with `data/songs/`."""
    from render_text import render

    doc = load(song_file)
    published = ROOT / "data" / "text" / f"{doc['id']}.txt"
    assert published.exists(), f"missing {published.name} — run tools/render_text.py"
    assert published.read_text(encoding="utf-8") == render(doc), (
        f"{doc['id']}: data/text is stale — run tools/render_text.py"
    )


# --------------------------------------------------------------------------
# Derived artefacts
# --------------------------------------------------------------------------

@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_midi_derives_and_is_playable(song_file, tmp_path):
    mido = pytest.importorskip("mido")
    from to_midi import to_midi

    doc = load(song_file)
    out = tmp_path / f"{doc['id']}.mid"
    to_midi(doc, out)
    midi = mido.MidiFile(out)
    assert midi.length > 5, "suspiciously short rendering"
    notes = [m for track in midi.tracks for m in track if m.type == "note_on"]
    assert len(notes) > 40


def test_validator_script_runs_clean():
    """tools/validate.py is what contributors are told to run; it must exit 0."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate.py")],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr


# --------------------------------------------------------------------------
# Documented claims about the corpus
# --------------------------------------------------------------------------

def test_corpus_covers_multiple_taal_families(songs):
    """The README claims structural diversity, not a list of favourites."""
    names = {s["taal"]["name"]["translit"] for s in songs.values()}
    assert len(names) >= 4, names


def test_corpus_includes_a_talamukta_song(songs):
    """Free-rhythm songs are the hardest case for the schema; one must stay in the corpus."""
    assert any(s["taal"]["talamukta"] for s in songs.values())


def test_corpus_exercises_komal_and_kori(songs):
    """
    If no song used komal or kori swaras, our decoding of those markings would be
    untested by the corpus itself.
    """
    komal = kori = False
    for doc in songs.values():
        for line in doc["lines"]:
            for cell in line["cells"]:
                for unit in cell["units"]:
                    sw = unit.get("swara") or {}
                    komal |= bool(sw.get("komal"))
                    kori |= bool(sw.get("kori"))
    assert komal and kori


# --------------------------------------------------------------------------
# Provenance URLs (network) — opt in with:  RUN_NETWORK_TESTS=1 pytest tests/
# --------------------------------------------------------------------------

@pytest.mark.skipif(
    not __import__("os").environ.get("RUN_NETWORK_TESTS"),
    reason="set RUN_NETWORK_TESTS=1 to check witness URLs against the live archive",
)
@pytest.mark.parametrize("song_file", SONG_FILES, ids=SONG_IDS)
def test_witness_url_still_serves_notation(song_file):
    """
    A citation that 404s, or quietly returns an empty viewer page, is worse than no
    citation — it looks checkable and isn't. (Four of these URLs failed exactly that
    way before v0.1 shipped: Bengali nukta characters must be precomposed.)
    """
    from fetch_sources import fetch
    from parse_nltr import parse_song

    doc = load(song_file)
    body = fetch(doc["provenance"]["primary_witness"]["url"])
    tmp = ROOT / "sources" / "raw" / f"_urlcheck_{doc['id']}.html"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    try:
        tmp.write_bytes(body)
        lines = parse_song(tmp)["lines"]
    finally:
        tmp.unlink(missing_ok=True)
    assert lines, f"{doc['id']}: witness URL returned no notation grid"
