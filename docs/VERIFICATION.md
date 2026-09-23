# Verification record

This corpus was encoded from an online archive. That is a reasonable place to start and a bad
place to stop, because an archive can be wrong and you would never know. So: three songs have been
checked, matra by matra, against scans of the **printed Swarabitan** — Visva-Bharati's own edition,
the source every other witness is downstream of.

This document records what was checked, what matched, what didn't, and what changed as a result.
It is written so that you can repeat it rather than trust it.

**Status: 3 of 30 songs scan-verified.** The rest are archive-derived and say so in their
`confidence` block.

That ratio got worse in v0.2, and it is worth being blunt about why. Once the pipeline existed,
adding twenty songs cost a day; verifying one song against print costs an evening of careful human
reading and cannot be automated. So the corpus grew and the verified fraction fell from 30% to 10%.

Growth was still worth it — the twenty new songs took the corpus from 6 taal families to 20, and
two of them exposed a real gap in the decoder (see [DECODING.md](DECODING.md)). But the honest
statement of where this project stands is: **the data is broad and thinly verified, and the
bottleneck is human eyes on printed pages.** Closing that is what v0.3 is for, and it is the one
job where a reader of swaralipi is worth more than any amount of tooling.

---

## How to repeat any of this

```bash
# 1. Get the volume (free, no login; these are Digital Library of India scans)
curl -L -o vol32.pdf https://archive.org/download/in.ernet.dli.2015.339540/2015.339540.Ed2.pdf

# 2. Find the song. IA's own Bengali OCR is good enough to locate it, not to read notation:
curl -L https://archive.org/download/in.ernet.dli.2015.339540/2015.339540.Ed2_djvu.txt | less

# 3. Render the page and read it yourself
pdftoppm -f 37 -l 37 -r 200 -png vol32.pdf page

# 4. Compare against the human-readable corpus
cat data/text/purano-sei-diner-katha.txt
```

Every song's `provenance.scan_verification` block carries its volume, song number, scan URL,
what was checked and the outcome.

---

## 1. পুরানো সেই দিনের কথা — Swarabitan vol. 32, song ১৬

**Scan:** [archive.org/details/in.ernet.dli.2015.339540](https://archive.org/details/in.ernet.dli.2015.339540) (PDF page 37)
**Checked:** lines 1–6 — sthayi through the first antara — every matra and every lyric syllable.
**Result: exact match.**

The printed page sets the notation as `॥ সা সা -ন়া । সা গা -া । রা সা -া । রা গা -া ।`
under `পু রা ৹ । নো সে ই । দি নে র্ । ক থা ৹`. The corpus has
`S S -/N, | S G - | R S - | R G -` under the same syllables. Every subsequent line agreed the
same way, including the compound matras (`-ন়সরা` = sustain + Ni-udara + Sa + Re inside one matra)
and the tara-saptak marks in line 2.

**What this changed:**

- **We gained a raga, and it checks out numerically.** The printed header reads
  **মিশ্র ভূপালী । একতাল**; the online witness states only the taal. Bhupali is the pentatonic
  S R G P D, and *mishra* means *mixed*. Counting the corpus: of this song's 135 pitched notes,
  **127 (94.1%) are that pentatonic core**, and the other eight are seven Ni — mostly a lower
  neighbour to Sa — plus exactly one Ma. A pentatonic frame with a small admixture is what the
  raga name literally claims, and it is what the data independently shows. Two things follow:
  the *Auld Lang Syne* origin (a pentatonic Scots air) is visible in the numbers, and the
  decoding is corroborated, because this distribution was produced before the raga name was
  known to us and could not have been assumed into it.
- **One honest doubt recorded.** Line 4, matra 5: the udara mark under the second ধা is ambiguous
  at this scan's resolution. We keep the witness reading (udara) because the surrounding phrase
  sits low, and we say so in the data rather than pretending the page was clear.

---

## 2. ভালোবেসে সখী, নিভৃতে যতনে — Swarabitan vol. 56, song ১৯

**Scan:** [archive.org/details/in.ernet.dli.2015.336651](https://archive.org/details/in.ernet.dli.2015.336651) (PDF page 58)
**Checked:** lines 1–2 (sthayi), every matra and lyric syllable.
**Result: exact match.**

Printed: `॥ { সা গা রা   গা গা গা   রা গমপা মা   গা মা গমগা` under
`ভা লো বে  সে স খী  নি ভৃ৹৹ তে  য ত নে৹৹`.
Corpus: `S G R  G G G  R G/M/P  M  G M G/M/G` under the same syllables. The three-note matras
(গমপা, গমগা) matched our matra-fraction encoding exactly — which is the part of the schema most
likely to be wrong, so this was the useful thing to check.

**What this settled — a real conflict between sources:**

geetabitan.com lists this song as **Dadra**. Our data says **talamukta** (free rhythm), following
the online witness. One of them had to be wrong, and the printed page decides it:

- there is **no raga/taal header** at all — unusual, since every other song page in these volumes
  carries one (song ১৫ two pages earlier reads "মিশ্র-আশাবরী । কাওয়ালি");
- there are **no vibhag dandas anywhere** in the notation, where a taal-bound song shows them
  every few matras.

Both are how Swarabitan sets a talamukta song. **The talamukta reading stands**, and the corpus
now records why, so nobody has to re-litigate it. A secondary source disagreeing is not an error
in that source — "Dadra" is a reasonable description of how the song is *performed*. It is simply
not what the page notates.

---

## 3. গ্রামছাড়া ওই রাঙা মাটির পথ — Swarabitan vol. 9, song ২২

**Scan:** [archive.org/details/in.ernet.dli.2015.339565](https://archive.org/details/in.ernet.dli.2015.339565) (PDF page 54)
**Checked:** line 1 (sthayi), all 16 matras and lyric syllables.
**Result: exact match.**

Printed: `॥ { ধ়া -সা -া সা । সা -া সা -রা । গা -পা পা -ধা । পা -া মা -পমা ।`
Corpus: `D, -/S - S | S - S -/R | G -/P P -/D | P - M -/P/M` — identical, with vibhag bars every
four matras, i.e. two kaharba cycles to the printed line, exactly as the corpus encodes it.

**What this changed:**

- **A metadata correction.** The printed header reads **বাংলা । কাহারবা**. We had recorded the
  raga-anga as "Baul-anga (traditional attribution)" — that came from tradition, not from a
  source. It now reads **বাংলা (Bangla), as printed in Swarabitan vol. 9**. The taal was right.
- **The kan encoding is validated.** This was the check worth doing. Our parser infers a *kan*
  (grace note) from a capitalisation convention in the online witness's font encoding — a
  reasonable-looking guess that could easily have been wrong across the whole corpus. On the
  printed page, the same position sets the ornamenting swara as a **smaller, raised glyph**
  (মগা) — the akarmatrik convention for kan. The guess was right, and now it is evidence.
- **Confidence raised** from `medium` to `high`, with the scope stated: line 1 verified, lines
  2–21 still archive-derived.

---

## What is still unverified

Twenty-seven songs remain checked only against the online witness, cross-source metadata, the
raga-signature test in [`DECODING.md`](DECODING.md), and — new in v0.2 — a test that the taal we
assign agrees with the cycle the page prints.

For the seven remaining from v0.1 the Swarabitan volumes are already identified, so that work is
entirely well-defined:

| Song | Swarabitan vol. | Scan |
|---|---|---|
| ফুলে ফুলে ঢ'লে ঢ'লে | 29 (Kalmrigaya) | `in.ernet.dli.2015.339537` |
| আনন্দলোকে মঙ্গলালোকে | 4 | `in.ernet.dli.2015.339558` |
| যদি তোর ডাক শুনে (একলা চলো রে) | 46 | `in.ernet.dli.2015.336646` |
| আগুনের পরশমণি | 43 | `in.ernet.dli.2015.336643` |
| তুমি রবে নীরবে | 10 | `in.ernet.dli.2015.339517` |
| মাঝে মাঝে তব দেখা পাই | 23 | `in.ernet.dli.2015.339531` |
| এসো শ্যামল সুন্দর | 54 | `in.ernet.dli.2015.339549` |

For the twenty songs added in v0.2 the volumes are not yet identified; finding them is itself a
useful contribution, and `sources/catalogue.json` plus the Swarabitan index
(`in.ernet.dli.2015.340247`) is where to start.

If you read swaralipi, taking any one song is the most useful contribution available to this
project — see [CONTRIBUTING.md](../CONTRIBUTING.md).

### Two things v0.2 found without a printed page

Neither needed a scan, and both are recorded in the data:

- **A missing swara.** Two new songs used a token the decoder did not know. Positional analysis
  identified it as komal Re — the one swara variant the v0.1 table lacked. None of the published
  ten used it, so that release is unaffected.
- **A taal we had wrong.** ঝম্পক was entered as ten matras from Hindustani Jhaptaal; every page
  printed its bars every five cells. Rabindrasangeet has its own taal system, and the notation was
  right. There is now a test asserting that the assigned taal matches the printed cycle, so this
  class of error cannot recur silently.

### One known open question

**মাঝে মাঝে তব দেখা পাই has two settings in Swarabitan vol. 23**, not one: a Kafi/Ektaal setting
and a Kirtan-sur/Dadra setting. Vol. 27's front matter says so explicitly — both forms were
collected. The corpus currently holds the **ektaal** setting only. The other is a missing song,
not a wrong one, and it is on the v0.2 list. This is exactly the kind of thing a single online
witness will never tell you.

---

## Independent witnesses used elsewhere

Beyond the scans, the corpus is cross-checked against two other lineages, recorded per song in
`provenance.secondary_witnesses`:

- **geetabitan.com** — an independent re-typesetting of the canonical swaralipi (images/PDF, not
  machine-readable), plus per-song metadata. Used for taal, parjaay and raga cross-checks.
- **notesandsargam.com** — romanized sargam for four of the songs. Worth knowing what this is: the
  author states plainly that these are **his own by-ear transcriptions played on flute**, not
  derived from Swarabitan. That makes them a genuinely independent witness to the *melody as
  performed*, and a poor authority on the notated text. We use them for melodic contour only, and
  say so.

Treating a source as more authoritative than it claims to be is its own kind of error. Where these
disagree with the print, the print wins.
