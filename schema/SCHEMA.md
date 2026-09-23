# Swaralipi-JSON: an akarmatrik-faithful symbolic encoding

**Version 0.1** · Canonical format of the *Songs of Tagore, In Data* corpus

## Design principle

Western symbolic formats (MIDI, MusicXML, ABC) cannot losslessly hold what a page
of Swarabitan holds: the taal cycle with its sam/taali/khali structure, the
three-saptak swara system with komal/kori variants written as distinct Bengali
letters, matra-fractional note groups, kan (grace) notes, meend, and syllable-level
lyric alignment in Bengali script. Swaralipi-JSON encodes the **akarmatrik page as
its own grammar**, and treats MIDI/MusicXML as derived, lossy views.

The unit of time is the **matra**, not the second. The unit of pitch is the
**swara degree relative to Sa**, not a frequency: Rabindrasangeet has no absolute
pitch — the singer chooses the tonic.

## Top-level document

```json
{
  "schema_version": "0.1",
  "id": "purano-sei-diner-katha",
  "title": { "bn": "পুরানো সেই দিনের কথা", "translit": "Purano sei diner katha" },
  "composer": "Rabindranath Tagore",
  "parjaay": { "bn": "স্মরণ", "en": "Remembrance" },
  "taal": { ... },
  "sections": [ ... ],
  "lines": [ ... ],
  "provenance": { ... },
  "confidence": { "level": "high", "notes": ["..."] }
}
```

## Pitch: the `swara` object

```json
{ "degree": "S", "komal": false, "kori": false, "saptak": 0 }
```

- `degree`: one of `S R G M P D N` (Sa Re Ga Ma Pa Dha Ni).
- `komal` (flat): valid for `R G D N`. In akarmatrik these are separate letters
  (ঋ জ্ঞ দ ণ), and the encoding preserves that they are first-class notes.
- `kori` (sharp, তীব্র/কড়ি): valid for `M` only (হ্ম).
- `saptak`: `-1` udara (mandra), `0` mudara (madhya), `+1` tara.

Semitone offset from Sa (for derivation only):
`S=0, R=2 (komal 1), G=4 (komal 3), M=5 (kori 6), P=7, D=9 (komal 8), N=11 (komal 10)`
plus `12 × saptak`.

## Time: matras and cells

A `line` is a sequence of `cells`. **One cell = one matra** (the akarmatrik grid
column). A cell contains 1..n `units`; the matra divides **evenly** among its
units (2 units = ½ matra each, 3 = ⅓, …), exactly as akarmatrik groups symbols
within a column.

Each unit is one of:

```json
{ "type": "swara", "swara": {...}, "kan": [ {...} ] }   // optional kan = grace note(s), printed as raised prefix
{ "type": "sustain" }                                    // the akarmatrik dash: previous swara continues
{ "type": "rest" }                                       // silence (rare in this corpus)
```

`kan` notes take negligible notated time (they steal from the main note on
performance); they are preserved structurally, not given matra fractions.

## Lyrics

Each cell carries `"lyric"`: the Bengali syllable(s) aligned under that matra
column, or `"৹"` — the akarmatrik continuation mark meaning the previous syllable
is still sounding (encoded as `null` + `"melisma": true` on the cell).

```json
{ "units": [...], "lyric": "পু", "melisma": false }
```

## Taal

```json
{
  "name": { "bn": "একতাল", "translit": "ektaal" },
  "matras": 12,
  "vibhags": [3, 3, 3, 3],
  "beats": ["sam", "taali", "khali", "taali"],
  "talamukta": false
}
```

`beats[i]` labels vibhag *i*: `sam` (১), `taali` (clap), `khali` (০).
For **talamukta** (free-rhythm) songs — e.g. *Bhalobese sokhi* — `talamukta` is
`true`, `matras`/`vibhags` are `null`, and cells still carry relative duration
via their unit counts, but no cycle is implied.

## Lines and sections

```json
{ "line_no": 4, "section": "sthayi", "cells": [ ... ], "anacrusis": false,
  "marks": [ {"type": "repeat_open", "cell": 0} ] }
```

`marks` preserve page-level signs: `{ }` repeat/ornament spans, `( )` optional or
alternate passages, `meend` arcs where the source shows them, and section double
bars. Section names follow Rabindrasangeet convention: `sthayi`, `antara`,
`sanchari`, `abhog` where identifiable, else `"body"`.

## Provenance (required)

```json
{
  "primary_witness": {
    "archive": "SNLTR Rabindra Rachanabali digital edition (of Swarabitan)",
    "url": "https://rabindra-rachanabali.nltr.org/...",
    "retrieved": "2026-08-11",
    "taal_as_stated": "একতালা"
  },
  "secondary_witnesses": [ { "site": "...", "url": "...", "agreement": "melodic contour matches" } ],
  "encoding_method": "automated grid parse + manual review",
  "known_deviations": ["..."]
}
```

Every song states where its notation was read from, when, and how much the
witnesses agree. This corpus is **archive-derived**; verification against first-edition
Swarabitan page scans is the v0.3 milestone (3 of 30 songs done).

## What is intentionally NOT encoded

- Absolute pitch / tonic frequency (performance choice)
- Tempo in BPM (akarmatrik pages do not specify it; laya is tradition)
- Harmony (Rabindrasangeet is melodic; accompaniment is not notated)

## Machine validation

`schema/swaralipi.schema.json` is a JSON Schema (draft 2020-12) that validates
every file in `data/songs/`. Beyond structural validation, `tools/validate.py`
checks **taal arithmetic**: every non-anacrusis line of a taal-bound song must
contain a whole number of vibhags, and cycles must close at section boundaries.
