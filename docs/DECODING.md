# Decoding the source: how font-locked swaralipi became data

The primary witness — the SNLTR Rabindra Rachanabali digital edition of Swarabitan —
serves akarmatrik notation as HTML tables rendered through a custom font
(`Swarabitan.ttf`). The underlying text is not Bengali: it is the font's input
code, Latin tokens like `sa ra ga ma pa qa na`, one table cell per matra column.
To digitize the notation, that token language had to be decoded. This document
records the decode and the evidence, because the whole dataset stands on it.

## The token language

| Token core | Decoded as | Evidence class |
|---|---|---|
| `sa ra ga ma pa na` | সা রা গা মা পা না — shuddha S R G M P N | direct (renders match, cross-source agreement everywhere) |
| `qa` | ধা — shuddha D | triangulated: aligns with D in an independent romanized sargam of the same songs at every occurrence |
| `ka` | হ্মা — kori (tivra) Ma | contextual: appears precisely where Behag/Kalyan-anga songs demand tivra Ma (e.g. hugging P in তুমি রবে নীরবে, আনন্দলোকে); mnemonic **k**ori |
| `ta` | জ্ঞা — komal Ga | triangulated: degree-exact alignment against the romanized witness of আমার পরান যাহা চায় (their S/N/D ↔ our g/R/S under a consistent tonic shift) |
| `da` | দা — komal Dha | contextual + mnemonic (দ IS the komal-Dha letter): chromatic d–D motion in kirtan-anga ভালোবেসে সখী |
| `ua` | ণা — komal Ni | contextual, strong: yields the textbook Desh avaroha S′–n–D–P in এসো শ্যামল সুন্দর and Jhinjhoti descents in মাঝে মাঝে |
| `va` | ঋা — **komal Re** *(added v0.2)* | positional: across the corpus `v` sits beside Sa 48 times and beside Ga/komal-Ga 14, and essentially never beside Ma or Pa — which is Re's position in the scale and nothing else's. Shuddha Re already has code `r`, so `v` is the komal form. It appears only in Bhairavi-flavoured songs, alongside komal Ga, Dha and Ni |
| suffix `h` | udara (lower saptak), e.g. `nha` = ণ়/na-udara… `pha` = পা় | triangulated (low passages align with by-ear witnesses) |
| suffix `f` | tara (upper saptak), e.g. `sfa` = সা′ | triangulated (S′ climaxes align) |
| trailing `a` | the আ-কার — one matra of vowel | structural (the system's namesake) |
| `-` / `-a` | sustain dash (previous swara continues) | direct |
| Capitalised prefix (`Rga`, `Qpa`, `SFgfa`, `-Gma`) | kan (grace) note(s) before the main swara; capital may take its own `f/h` octave letter | structural, consistent across corpus |
| multi-note bodies (`qpqa`, `sfrfsfa`) | matra-fraction groups: n notes in a cell divide the matra evenly | structural (matches akarmatrik column grouping) |
| `l` / `ll`, `L` | danda / double danda (bar, section bar) | direct |
| `A` | vibhag separator within the printed line | direct |
| `1f 2 0 3` header rows | taal beat numerals (sam / taali / khali-0) | direct |
| `{ } ( ) [ ]` | repeat, alternate, bracketed-passage spans | direct |
| `৹` (lyric rows) | melisma: previous syllable continues | direct |
| suffix `i` (`pai`, `-ki`) | rare vowel-form variant; pitch reading kept, semantics flagged `uncertain` in the data (22 units across 3 songs) | open question — v0.2 item |

## The triangulation, in one example

আমার পরান যাহা চায়, opening phrase. NLTR tokens: `ma pa ma ta | ra sa …`.
An independent by-ear romanized witness gives `R G R | S N D …` for the same
words. Under a single consistent tonic shift (their S = our komal-Ga slot), every
degree maps: their R→M, G→P, S→(g), N→R, D→S — which forces `ta` = komal Ga, and
the semitone relationships all land (their N sits a semitone below their S exactly
as our R sits a semitone below komal Ga). One unknown, two witnesses, zero degrees
of freedom left.

## Independent confirmation: the note-set test

After decoding, each song's total note inventory was computed *without any raga
assumption* — and the inventories reproduce the raga signatures the tradition
assigns these songs:

- তুমি রবে নীরবে → S G M **M#** P N core — **Behag**, as its metadata states
- এসো শ্যামল সুন্দর → S R G M P D **n N** (both Ni, no komal Ga) — textbook **Desh**
- মাঝে মাঝে তব দেখা পাই → mixed **g/G** and **n/N** — Jhinjhoti-anga
- পুরানো সেই দিনের কথা → S R G P D pentatonic core — exactly what a song built on
  "Auld Lang Syne" (a pentatonic Scots air) must show
- একলা চলো রে → shuddha frame with **d/n** inflections — Baul sur

A wrong decode of any komal/kori token would have scrambled these signatures.
It didn't.

## What v0.2 changed

**A missing swara.** The v0.1 table had no code for komal Re — the one variant with no
entry. Encoding twenty more songs surfaced an undecoded token, `v`, appearing 49 times in
two Bhairavi-flavoured songs. Its neighbours settle it: `v` sits next to Sa 48 times and
next to Ga 14, and never next to Ma or Pa. That is Re's position, and since shuddha Re is
already `r`, `v` is komal Re. None of the ten songs published in v0.1 use it, so that
release stands unaffected — but a corpus that grew without noticing would have silently
mis-encoded every Bhairavi song it touched.

**A policy change: we no longer guess.** Previously an unreadable character became a
placeholder Sa flagged `uncertain`. That is a bad failure mode — a wrong pitch sitting in
the data looking like a right one. Unreadable glyphs are now recorded as annotation marks
on the cell instead. They are visibly missing rather than invisibly wrong. Fifty-four
survive across thirty songs, mostly trailing capitals whose meaning we have not
established; if you know what they mark, that is a valuable issue to file.

**A theory corrected by the notation.** We entered ঝম্পক as ten matras, importing
Hindustani Jhaptaal. Every page printed its bar lines every five cells. Rabindrasangeet
uses its own taal system — ঝম্পক 5, ষষ্ঠী 6, রূপকড়া 8 — and the notation was right where
the imported theory was wrong. A test now enforces this: the taal we assign must agree
with the cycle the page prints.

## Residual uncertainty (all flagged in-data)

- The `i`-suffix vowel-form (22 units): pitch confident, duration/vowel semantics not.
- A handful of annotation glyphs (`w x \`, bracketed reference cells) are preserved
  as `marks` but not musically interpreted.
- Section labels (sthayi/antara/…) are heuristic from double-bar structure, not
  stated by the witness.
- Final authority remains the printed Swarabitan; v0.2 = scan verification.
