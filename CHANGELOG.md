# Changelog

All notable changes to this corpus are recorded here. The dataset follows semantic-ish versioning:
the **major.minor** version describes the corpus state, and any change to the *schema* bumps the
schema version independently (see `schema/SCHEMA.md`).

## [0.2.0] — 2026-09-02

Twenty more songs, and two corrections the new songs forced.

### Added
- **20 songs (10 → 30)**, chosen for structural coverage rather than fame: the corpus goes from
  6 taal families to **20**, adding teora 7, jhanp 10, jhampak 5, sasthi 6, kawwali 8, dhamar 14,
  surfank 10, chautal 12, ardha-jhanp 5, madhyaman 16, rupak 7, rupakra 8, arathheka 16, and a
  second talamukta song. Also the Indian national anthem, কৃষ্ণকলি, আলো আমার আলো and ক্লান্তি
  আমার ক্ষমা করো — the last two delivering on reserve songs promised in the v0.1 roadmap.
- `sources/catalogue.json` — a map of **all 1,568 songs** in the witness archive that carry
  notation, with taal, parjaay and URL for each. Built by the new `tools/discover_songs.py`,
  which crawls the archive's own lyric pages so the URLs are correct by construction rather than
  guessed from Bengali titles.
- `parjaay` is now taken from the witness's own classification instead of from tradition.
- The song table moved out of `tools/build_dataset.py` into `sources/songs.json`, so adding a song
  is a data edit rather than a code edit.
- A test asserting that the taal assigned to a song matches the avartan its page actually prints.

### Fixed
- Derived MusicXML is now reproducible across music21 releases, not just across runs: music21 9.9
  stopped writing `<supports>` capability hints, which would have failed the CI reproducibility
  check on a fresh install. `stabilise()` now strips them, so every version produces identical bytes.

### Moved
- The repository moved from the `NeelVerse-Lab` organization to the maintainer's personal account:
  **https://github.com/indranilbanerjee/tagore-swaralipi**. GitHub redirects old clone and web
  URLs, but the Pages site does not redirect — the listening page and method walkthrough now live at
  **https://indranilbanerjee.github.io/tagore-swaralipi/**. Every link in the repo, the citation
  file, the JSON-LD and the schema `$id` points at the new home.

### Fixed / corrected
- **komal Re was missing from the decoder.** Two new Bhairavi-flavoured songs used an unknown
  token; positional analysis identified it as komal Re — the one swara variant the v0.1 table had
  no code for. 49 notes now decode correctly. None of the ten songs in v0.1 use it, so that
  release was unaffected.
- **ঝম্পক was wrong.** It was entered as ten matras from Hindustani Jhaptaal; every page printed
  bars every five cells. Rabindrasangeet uses its own taal system and the notation was right.
- **Unreadable glyphs are no longer guessed into pitches.** Previously an undecodable character
  became a placeholder Sa flagged `uncertain` — a wrong note that looks like a right one. They are
  now recorded as annotation marks on the cell: visibly missing instead of invisibly wrong.
  54 remain across the corpus.

### Known regression
- **Scan verification did not scale with the corpus**: 3 of 10 songs in v0.1, 3 of 30 now.
  Adding songs is cheap once the pipeline exists; checking one against a printed page is an
  evening of human reading. This is stated plainly in `docs/VERIFICATION.md` and is the v0.3
  milestone.

## [0.1.0] — 2026-08-11

First public release.

### Added
- 10 Rabindrasangeet encoded in **Swaralipi-JSON v0.1** — akarmatrik-faithful symbolic notation
  with swara/saptak/matra-fraction timing, taal cycles, komal & kori swaras as first-class notes,
  kan (grace) notes, and syllable-aligned Bengali lyrics.
- Coverage: ektaal, dadra, kaharba, tintal, khemta and one **talamukta** (free-rhythm) song;
  three raga-angas; two bhanga gaan built on Scottish airs.
- `schema/` — JSON Schema validator and the design rationale behind the format.
- `tools/` — full reproducible pipeline: source parser, dataset builder, validator, text renderer
  and re-parser, MIDI and MusicXML converters, and a dependency-free additive synthesizer.
- `derived/` — MIDI and MusicXML for every song.
- `audio/` — reference audio synthesized purely from the notation, no recordings involved.
- `docs/DECODING.md` — how the source archive's font-encoded notation was decoded, with the
  three-way triangulation evidence.
- `docs/DATASET_CARD.md` — coverage, intended uses, limitations, rights, prior art.
- `experiment/` — blind AI-continuation experiment with A/B audio and writeup.
- `tests/` — 116 integrity checks (schema, taal arithmetic, musical sanity, provenance, lossless
  round-trip) run in CI on every push and pull request.

### Verification
- 3 of 10 songs checked matra-by-matra against scans of the printed Swarabitan (vols. 32, 56, 9) —
  all three exact matches. Recorded per song in `provenance.scan_verification` and written up in
  `docs/VERIFICATION.md`.
- Corrections this produced: গ্রামছাড়া's anga is **বাংলা** as printed (not the "Baul" recorded from
  tradition); পুরানো সেই দিনের কথা gains the raga **মিশ্র ভূপালী** from the printed header, which the
  online witness omits.
- Conflicts this settled: ভালোবেসে সখী is **talamukta**, not dadra — the printed page carries no
  taal header and no vibhag dandas.
- Validated by print: the corpus's *kan* (grace-note) encoding matches the akarmatrik convention of
  setting the ornamenting swara as a smaller raised glyph.

### Notes on determinism
- `tools/to_musicxml.py` normalises music21's encoding date, version stamp and randomly
  generated part ids, so every derived file is byte-reproducible from the canonical JSON on any
  machine. CI asserts this on every push — a diff in `derived/` therefore always means a real
  change to the data, never a rerun artefact.

### Notes on sources
- Witness pages are **not redistributed**; `tools/fetch_sources.py` retrieves them from the cited
  URLs on demand and `sources/raw/` is git-ignored. Rationale in `sources/README.md`.
- Witness URLs use the archive's precomposed Bengali nukta characters (য় ড় ঢ়). Unicode NFC does
  not produce these — they are composition exclusions — so four of the ten URLs would otherwise
  return an empty viewer page that *looks* like a successful fetch. An opt-in network test
  (`RUN_NETWORK_TESTS=1`) checks every citation against the live archive.

### Known limitations
- Archive-derived, not verified against printed Swarabitan pages — this is the v0.2 milestone.
- 22 note-units across 3 songs use an undecoded source-notation variant; pitch confident, vowel
  semantics flagged `uncertain`.
- Section labels (sthayi/antara/…) are inferred from double-bar structure, not stated by the source.
- Meend spans are preserved positionally but not semantically.

[0.2.0]: https://github.com/indranilbanerjee/tagore-swaralipi/releases/tag/v0.2.0
[0.1.0]: https://github.com/indranilbanerjee/tagore-swaralipi/releases/tag/v0.1.0
