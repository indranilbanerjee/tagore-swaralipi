# Contributing

**You do not need to be a programmer to contribute to this project.** The rarest and most valuable
skill here is being able to *read swaralipi* — and if you have it, the most useful thing you can do
takes ten minutes and requires nothing but a GitHub account.

There are four ways to help, listed from "no technical skill needed" to "please write code."

---

## 1. Verify a song against the printed Swarabitan ⭐ most wanted

This corpus is **v0.1: archive-derived**. Every song was digitized from an online archive of
Swarabitan, not from the printed volumes themselves. That is honest but not final. The v0.2
milestone is having every song checked, line by line, against a Swarabitan page — by people who
read akarmatrik notation.

**If you can read swaralipi, you are exactly who this project needs.**

How to do it:

1. Pick a song from [`data/text/`](data/text) — these are human-readable versions of the data.
   You do **not** need to read the JSON.
2. Open the corresponding Swarabitan page (print, PDF, or [scans on Internet
   Archive](https://archive.org/search?query=swarabitan)).
3. Compare. Look especially for:
   - wrong swara, or right swara in the wrong saptak (octave)
   - komal/kori (flat/sharp) markings that should or shouldn't be there
   - matra counts that don't match the printed grid
   - lyric syllables aligned under the wrong note
   - meend, kan (grace notes), or repeat marks that we lost
4. Open a **Notation correction** issue
   ([new issue →](../../issues/new?template=notation-correction.yml)). Tell us the song, the line,
   what we have, what the book has, and which edition you're looking at. A photo of the page is
   ideal but optional.

**You will be credited by name in the song's provenance block** unless you ask us not to be.
Corrections are the single highest-value contribution to this repository.

### How to read `data/text/` files

```
S   S   -/N,  |  S   G   -  |  R   S   -   |  R  G   -
পু  রা  ৹     |  নো  সে  ই  |  দি  নে  র্  |  ক  থা  ৹
```

- Each column is **one matra**. `|` marks the vibhag (bar-group) boundary.
- `S R G M P D N` = Sa Re Ga Ma Pa Dha Ni. **Lowercase = komal** (`r g d n`), `M#` = kori Ma.
- `'` after a note = tara saptak (upper octave); `,` = udara saptak (lower).
- `-` = the previous note continues (the akarmatrik dash).
- `A/B` inside one column = both notes share that single matra, split evenly.
- `(X)Y` = X is a kan (grace note) before Y.
- Bottom row = lyrics; `৹` = the previous syllable is still sounding (melisma).

That's the whole notation. If something in the data can't be expressed in it, that's a schema
bug and we want to hear about it.


---

## Walkthrough: what verifying a song actually looks like

This is the real sequence, start to finish, for the task we most need. It took about forty
minutes per song the first time and under twenty after that. **No programming is involved** —
step 2 is two commands you can copy, and everything else is looking and comparing.

### Step 1 — pick a song and find its volume

[`docs/VERIFICATION.md`](docs/VERIFICATION.md) lists the seven unverified songs with their
Swarabitan volume and archive.org identifier. Say you pick **তুমি রবে নীরবে** — volume 10,
identifier `in.ernet.dli.2015.339517`.

### Step 2 — get the scan and find the page

The scans are free, no login. In a terminal:

```bash
# download the volume
curl -L -o vol10.pdf \
  https://archive.org/download/in.ernet.dli.2015.339517/2015.339517.Ed2.pdf

# the archive's Bengali OCR is good enough to LOCATE the song
# (not to read the notation — you'll do that with your eyes)
curl -L https://archive.org/download/in.ernet.dli.2015.339517/2015.339517.Ed2_djvu.txt \
  | grep -n "তুমি রবে"
```

Prefer not to use a terminal? Open
`https://archive.org/details/in.ernet.dli.2015.339517` and page through the reader. Songs are
numbered, and each begins with a page carrying the song number, a `রাগ । তাল` line, and the
lyrics — the notation follows underneath.

### Step 3 — read the page beside our text

Open [`data/text/তুমি-রবে-নীরবে`](data/text) — sorry, `data/text/tumi-robe-nirobe.txt` — next to
the scan. Our format maps one-to-one onto the printed grid:

| On the printed page | In our text |
|---|---|
| সা গা মা | `S G M` |
| ধা with a dot/hasanta below | `D,` (udara — lower octave) |
| সা with the mark above | `S'` (tara — upper octave) |
| `-া` (the akarmatrik dash) | `-` |
| গমপা — three swaras in one column | `G/M/P` |
| a small **raised** swara before a normal one | `(G)M` — that's a kan |
| `।` between groups | `\|` |
| `৹` under a syllable | `৹` — the syllable is still sounding |

Go matra by matra. Most lines will match. Where one doesn't, you've found the thing we're
looking for.

### Step 4 — write down what you found

Open a [notation correction issue](../../issues/new?template=notation-correction.yml). Say which
song, which line, what we have, what the book has, and which volume and page you read. **Say how
sure you are** — "certain, I'm looking at the page" and "worth checking, something seems off" are
both useful, and the second one is not a lesser contribution.

**If everything matched, tell us that too.** A song confirmed correct is exactly as valuable as a
song corrected — it moves that song from "archive-derived" to "verified" and that's the whole
point of v0.2. Most of this work will be confirmations, and each one is a real result.

### What happens next

The maintainer updates the song's `provenance.scan_verification` block and its `confidence`, and
credits you by name in the data unless you asked otherwise. The tests re-run, and if a melody
changed, the derived MIDI, MusicXML and audio are regenerated so everything stays in sync.

---

## Walkthrough: fixing a wrong note yourself

If you're comfortable with a text editor and a terminal, you can go further than reporting.

```bash
git clone https://github.com/indranilbanerjee/tagore-swaralipi.git
cd tagore-swaralipi
pip install -r requirements.txt
python -m pytest tests/ -q        # should be all green before you touch anything
```

The canonical data is `data/songs/<song>.json`. Find the line and cell — the JSON mirrors the
printed grid, so line 4, matra 5 is `lines[3].cells[4]`. A cell looks like:

```json
{ "units": [ { "type": "swara", "swara": { "degree": "D", "saptak": -1 } } ],
  "lyric": "ভো", "melisma": false }
```

Change what's wrong. Then regenerate everything downstream and check yourself:

```bash
python tools/render_text.py     # rebuild the human-readable text
python tools/to_midi.py         # rebuild MIDI
python tools/to_musicxml.py     # rebuild MusicXML
python tools/synth.py <song-id> # re-render the audio — then LISTEN to it
python -m pytest tests/ -q      # must still be green
```

**Listening is not optional.** The audio is synthesized from the data, so it is the fastest test
of whether an edit was right. A wrong note is usually obvious to anyone who knows the song.

Then open a pull request. Put your source in it — volume and page — because a correction without
a source can't be merged, however confident it sounds. The checklist in the PR template covers
the rest.

---

## 2. Add a song

We want the corpus to grow — carefully. A new song needs:

- **Notation source**: which Swarabitan volume, and any online witness you used. Songs where you
  have access to the printed page are far preferred.
- **Metadata**: taal, parjaay, and raga-anga if the tradition assigns one.
- The notation transcribed in the `data/text/` format above (see §1), or as a
  [New song](../../issues/new?template=new-song.yml) issue if you'd rather hand it off.

We would rather have 20 songs that are right than 200 that are approximately right. A song with
uncertain notation is still welcome — flag it and it ships with `confidence: "medium"` or `"low"`
and a note explaining what's unresolved. **Honest uncertainty is a feature of this dataset, not
an embarrassment.**

Priority list for v0.2: আলো আমার আলো ওগো · ক্লান্তি আমার ক্ষমা করো · আমার পরান যাহা চায় ·
আমার সোনার বাংলা (no machine-readable source found yet — needs a from-scratch transcription).

---

## 3. Improve the tooling

The pipeline lives in [`tools/`](tools) and is plain Python with three dependencies. Useful work:

- **Renderers** — draw proper akarmatrik notation (Bengali script, taal grids) from the JSON.
  Right now we only emit plain-text sargam.
- **Better synthesis** — `tools/synth.py` is a small additive synth. Meend (glides) and proper
  gamaka would make the reference audio far more musical.
- **Format bridges** — export to
  [SwaralipiXML](https://indic-music.github.io/swaralipixml.html), ABC, LilyPond, or Humdrum
  `**kern` so this data reaches existing musicology toolchains.
- **Analysis notebooks** — phrase mining, taal-cadence statistics, comparing Tagore's bhanga
  gaan against their Scottish/Hindustani sources. [`examples/explore.py`](examples/explore.py) is
  a starting point, and [`docs/USE_CASES.md`](docs/USE_CASES.md) lists open questions worth
  attacking. This is what the dataset exists for.

### Development setup

```bash
git clone https://github.com/indranilbanerjee/tagore-swaralipi.git
cd tagore-swaralipi
pip install -r requirements.txt
python -m pytest tests/ -v        # must pass before you open a PR
python tools/validate.py          # schema + taal arithmetic + note-set report

# The witness pages are not redistributed here (see sources/README.md).
# To rebuild the corpus from its cited sources:
python tools/fetch_sources.py     # downloads them into sources/raw/ (git-ignored)
python tools/build_dataset.py

# Optional: check every provenance URL still serves notation (hits the live archive)
RUN_NETWORK_TESTS=1 python -m pytest tests/ -k witness
```

Every PR runs the same checks in CI. A PR that changes `data/` must keep all tests green — that
includes the round-trip test (JSON → sargam-text → JSON must be lossless) and the taal-arithmetic
check.

---

## 4. Extend the schema

The schema ([`schema/SCHEMA.md`](schema/SCHEMA.md)) is at v0.1 and deliberately incomplete.
Known gaps, in rough priority order:

| Gap | What's needed |
|---|---|
| **Meend** | Glide arcs exist in the source pages; we preserve position but not span semantics |
| **The `i`-form tokens** | 22 units across 3 songs use a source-notation variant we haven't decoded. Pitch is confident; the vowel/duration semantics are not. If you know akarmatrik deeply, [this issue](../../issues) is for you |
| **Section labels** | `sthayi`/`antara`/`sanchari`/`abhog` are inferred from double-bars, not stated by the source |
| **Alternate versions** | Some songs have variant readings across Swarabitan editions; the schema has no way to hold two readings at once |

Schema changes need a version bump and a migration note. Open an issue to discuss before writing
code — the format is meant to outlive any one contributor's use case.

---

## Ground rules

- **Cite your source.** Every notation claim in this repo says where it came from and when it was
  read. A correction without a source can't be merged, however confident it sounds — not because
  we doubt you, but because the next person needs to be able to check it too.
- **Uncertainty is recorded, not hidden.** If you're 80% sure, say so and we'll write that down.
- **The compositions are public domain; be careful with the intermediaries.** Tagore's works
  entered the Indian public domain in 2002. Some archives and books that *print* the notation
  assert rights over their own digitization or typesetting. This project re-encodes musical facts
  into its own schema and cites its sources; please don't paste scans, page images, fonts, or
  large verbatim extracts of any archive's HTML into this repo.
- **Be kind.** See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Disagreement about a matra is normal
  and welcome; contempt is not.

---

## Credit

Contributors are listed in the repository's contributor graph, and anyone whose correction changes
the data is named in that song's `provenance.corrections` block — permanently, in the data itself.
If you'd rather stay anonymous, just say so in the issue.

See [`ROADMAP.md`](ROADMAP.md) for what's planned and which items are marked **help wanted** —
several are claimable without asking anyone first.

Questions? Open a [discussion](../../discussions) or an issue. Bengali, Hindi, and English are all
welcome — write in whichever you think in.
