# What this data is for

A dataset is only as good as the questions it lets you ask. This page is about what becomes
possible once Rabindrasangeet notation is data — some of it demonstrated here on thirty songs,
most of it waiting on a bigger corpus.

Everything in the first section is real output from
[`examples/explore.py`](../examples/explore.py), which you can run in ten seconds with no
dependencies. Nothing below is hypothetical unless it says so.

---

## 1. Questions you can answer today, in a few lines of Python

### Where does the music land on sam?

Sam — the first beat of the taal cycle — is the anchor the whole rhythm hangs from. Across the
taal-bound songs in this corpus:

```
P    214  21.6%  ██████
M    133  13.4%  ████
S    120  12.1%  ████
G    116  11.7%  ████
S'    97   9.8%  ███
D     81   8.2%  ██
```

Pa, not Sa, is the most common note at sam — nearly twice as often as the tonic. **This finding
survived the corpus tripling**, which is what makes it worth reporting: measured on ten songs Pa
led with 27.7%, and on thirty it still leads with 21.6% while Sa sits at 12.1%. A number that holds
when the sample changes is starting to be about the music rather than about the sample. (On five
hundred songs it would be a paper.)

### Which phrases recur across different songs?

Reducing every four-note run to its interval shape, so the comparison is key-independent:

```
in 27/30 songs   e.g. G G G G      intervals (0, 0, 0, 0)
in 25/30 songs   e.g. D P D P      intervals (0, -2, 0, -2)
in 23/30 songs   e.g. S' N D N     intervals (0, -1, -3, -1)
in 23/30 songs   e.g. D P M G      intervals (0, -2, -4, -5)
```

This is the beginning of a **phrase vocabulary** for the tradition — the shared building blocks a
composer draws on. Scale it up and you get something no textbook currently contains: an empirical
account of Rabindrasangeet's melodic grammar, derived rather than asserted.

### How much of this music is melisma?

The proportion of matras where a syllable is still sounding rather than a new one beginning:

```
e-parabase-rabe-ke-hay             65.3%
gram-chhara-oi-ranga-matir-path    53.0%
tumi-robe-nirobe                   38.5%
bipade-more-rokkha-koro            11.2%
```

Nearly a six-fold spread. Word-setting density turns out to be a measurable stylistic
dimension, and it separates the songs in ways that don't line up neatly with taal or parjaay —
which is itself interesting, and worth a real study.

### Did the raga names survive the digitization?

The corpus never assumes a raga anywhere in the pipeline. So you can ask the data what notes each
song *actually* uses, and check it against what tradition says:

| Song | What the data contains | Tradition says |
|---|---|---|
| তুমি রবে নীরবে | both Ma forms, M# beside P | **Behag** |
| এসো শ্যামল সুন্দর | both Ni forms, no komal Ga | **Desh** |
| মাঝে মাঝে তব দেখা পাই | mixed g/G and n/N | **Jhinjhoti**-anga |
| পুরানো সেই দিনের কথা | 94.1% pentatonic S R G P D; the rest 7 Ni + 1 Ma | **Mishra Bhupali** |
| গভীর রজনী নামিল হৃদয়ে | komal Re, Ga, Dha and Ni together | **Bhairavi**-anga — and the song that exposed a missing swara in our decoder |

That last row is the sharpest. *Bhupali* is the pentatonic; *mishra* means *mixed*. The data shows
a pentatonic frame with a 6% admixture — exactly what the name claims — and we measured it before
we had ever seen the printed raga header. Independent corroboration in both directions: the
tradition's label is empirically accurate, and our decoding is sound.

---

## 2. What a larger corpus makes possible

### Computational musicology on a repertoire that has never had it

**How did Tagore rework what he borrowed?** He built *bhanga gaan* — songs whose melodies come
from Scottish airs, Hindustani bandish, Baul tunes, kirtan. Two are already in this corpus
(*Auld Lang Syne*, *Ye Banks and Braes*). The source tunes are themselves available as symbolic
data. So the diff is computable: which intervals he kept, which he bent to fit a taal cycle, where
he inserted melisma to carry Bengali syllables that the English original never had to. That is a
substantial piece of comparative musicology, and it is currently blocked on nothing but corpus
size.

**Do the notators have fingerprints?** Swarabitan's volumes were transcribed by different people
over decades — Jyotirindranath Tagore, Dinendranath Tagore, Indira Devi Chaudhurani, Sailajaranjan
Majumdar, Shantidev Ghosh. Each faced the same problem — write down a song you have heard sung —
and no two people solve that identically. With enough encoded songs you could test whether
transcriber identity is detectable from notation style: how finely they subdivide matras, how
freely they mark kan and meend, how they handle a held syllable. A question about the *history of
notation*, answerable only with data.

**Does parjaay have a musical signature, or only a thematic one?** Tagore grouped his songs by
theme — Puja, Prem, Prakriti, Swadesh. Whether those groupings carry any consistent *musical*
character is an open question that a classifier could put numbers on.

### Music AI that includes this tradition

Models learn the grammar of what they can read, and this repertoire has been unreadable to them.
Concretely, symbolic data unlocks:

- **Melody continuation and completion** in a non-Western grammar — the experiment in this repo is
  a first probe.
- **Style transfer that respects taal**, rather than treating Indian music as Western music with
  unusual scales.
- **Low-resource symbolic music research.** A corpus this small is a *feature* for this line of work: it is
  a natural testbed for how much musical grammar can be learned from very little, which matters
  for every under-documented tradition, not just this one.
- **Training data with clean provenance.** Every note here traces to a cited public-domain source.
  For anyone building music models under real licensing scrutiny, that is rare and valuable.

### A benchmark, not just a dataset

This is the idea I would most like someone to take up.

The continuation experiment can be formalised into an evaluation: *given N songs of a tradition,
continue the N+1th in-grammar.* It is scoreable without human raters on the mechanical
dimensions — matra arithmetic, note-set membership, cadence legality, lyric alignment — and those
scores can be checked against a held-out truth that actually exists, because Tagore wrote the real
continuation.

What makes it worth building is precisely the result we already got: the model passed every
mechanical check and still made a choice Tagore didn't. **A benchmark that separates "followed the
rules" from "understood the idiom" is a genuinely hard thing to construct**, and this repertoire
hands you one, because the grammar is strict and the corpus has a ground truth.

### Tools that musicians would actually use

- **Practice tracks at any tonic and tempo.** The data is tonic-free by design, so a learner who
  sings in a different scale isn't stuck with someone else's key. `tools/synth.py` already does
  this; it needs a front end.
- **Notation rendering.** Proper akarmatrik typesetting from the JSON — Bengali script, taal
  grids, meend arcs. Then any correction to the data reprints a correct page.
- **Search that doesn't exist anywhere.** "Songs in dadra that use kori Ma." "Songs whose antara
  climbs past tara Ga." "Every song with a three-note matra in the sthayi." Trivial over this JSON,
  impossible over a shelf of books.
- **Accessibility.** Symbolic notation can be rendered to Braille music or read aloud by a screen
  reader. Page scans cannot. For blind musicians this repertoire is currently far less accessible
  than the Western canon, and that is a data problem with a data solution.

### Preservation that is honest about itself

Print decays, editions drift, and the differences between them go unrecorded. This format carries
provenance and confidence *per song* — where each reading came from, when, how sure we are, and
what remains unresolved. Scaled up, that produces something the printed edition cannot: a record
that shows its own uncertainty, and where two editions disagree, keeps both.

---

## 3. Why it's worth doing

**Because the alternative is a tradition that computers cannot see.** Western art music has
centuries of digitized scores; every music model, search tool and analysis library is built on
that foundation. Rabindrasangeet has roughly 2,200 songs, nearly all of them notated — an
unusually complete written record for any song tradition on earth — and until now, essentially
none of it was machine-readable. A repertoire absent from the data is absent from the tools, and
then absent from the research, and eventually absent from what the next generation can find.

**Because the notation is a claim about the music, and claims can be checked.** Verifying three
songs against the printed Swarabitan already produced a metadata correction, a settled conflict
between sources, and a raga name that the online archive had dropped. Those are small findings.
They are also the kind that simply do not surface while notation lives only as pictures of paper.

**Because it is legally clean and permanently free.** Tagore's works entered the Indian public
domain in 2002. This is one of the great song repertoires of the world, and there is no rights
holder standing between it and open scholarship. That is not true of most twentieth-century music,
and it makes this a rare opportunity rather than an ordinary one.

**Because thirty songs proves the hard part.** The schema handles the awkward cases — free rhythm,
three-note matras, grace notes, komal and kori as distinct letters, Bengali syllable alignment.
The pipeline is reproducible end to end. Twenty more songs were added in a day once it existed, spanning taals no Western format can hold.
The remaining work is real but it is no longer *research*; it is careful, checkable effort that
many hands can share — and the binding constraint is now verification, not encoding. That is the point at which a project
stops being one person's and becomes a community's.

---

## Where to start

- Run [`examples/explore.py`](../examples/explore.py) and change the questions.
- Read [`schema/SCHEMA.md`](../schema/SCHEMA.md) to understand what the encoding preserves and why.
- See [`ROADMAP.md`](../ROADMAP.md) for what's planned, and
  [`CONTRIBUTING.md`](../CONTRIBUTING.md) for how to take a piece of it.

If you build something with this, open a discussion and tell us — a list of work built on the
corpus is the best argument for extending it.
