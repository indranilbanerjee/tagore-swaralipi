#!/usr/bin/env python3
"""
build_site.py — generate index.html: a listening page for the corpus.

Every player on this page is sounding notation, not a recording. The point of the
page is that you can read a line of swaralipi and hear exactly that line, so the
data can be judged by ear as well as by eye.
"""
import glob
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from render_text import render  # noqa: E402

REPO = "https://github.com/indranilbanerjee/tagore-swaralipi"


def excerpt(doc, lines=4):
    body = render(doc).splitlines()
    keep = [l for l in body if l.strip() and not l.startswith("#")]
    out, count = [], 0
    for line in keep:
        if line.startswith("["):
            continue
        out.append(line)
        count += 1
        if count >= lines * 2:
            break
    return "\n".join(out)


def song_card(doc):
    taal = doc["taal"]
    taal_txt = ("talamukta — free rhythm" if taal["talamukta"]
                else f"{taal['name']['translit']} · {taal['matras']} matras · vibhags {'+'.join(map(str, taal['vibhags']))}")
    raga = doc.get("raga_anga") or "—"
    verified = doc["provenance"].get("scan_verification")
    badge = ""
    if verified:
        badge = (f'<span class="badge verified" title="{html.escape(verified["scope"])}">'
                 f'✓ verified against Swarabitan vol. {verified["swarabitan_volume"]}</span>')
    conf = doc["confidence"]["level"]
    return f"""
    <article class="song">
      <header>
        <h3>{html.escape(doc['title']['bn'])}</h3>
        <p class="translit">{html.escape(doc['title']['translit'])}</p>
      </header>
      <dl class="meta">
        <div><dt>Taal</dt><dd>{html.escape(taal_txt)}</dd></div>
        <div><dt>Raga / anga</dt><dd>{html.escape(raga)}</dd></div>
        <div><dt>Confidence</dt><dd>{conf}{badge}</dd></div>
      </dl>
      <audio controls preload="none" src="audio/{doc['id']}.mp3"></audio>
      <details>
        <summary>See the notation this audio is made from</summary>
        <pre>{html.escape(excerpt(doc))}</pre>
      </details>
      <p class="links">
        <a href="{REPO}/blob/main/data/songs/{doc['id']}.json">JSON</a> ·
        <a href="{REPO}/blob/main/data/text/{doc['id']}.txt">sargam-text</a> ·
        <a href="{REPO}/blob/main/derived/midi/{doc['id']}.mid">MIDI</a> ·
        <a href="{REPO}/blob/main/derived/musicxml/{doc['id']}.musicxml">MusicXML</a>
      </p>
    </article>"""


CSS = """
:root{--bg:#faf8f5;--ink:#1c1a17;--muted:#6b635a;--line:#e2dcd3;--accent:#8c3b1b;--ok:#2f6b45}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans Bengali",sans-serif}
.wrap{max-width:860px;margin:0 auto;padding:0 20px 80px}
header.top{padding:64px 0 32px;border-bottom:1px solid var(--line);margin-bottom:40px}
h1{font-size:2.1rem;line-height:1.25;margin:0 0 6px;font-weight:650}
h1 .bn{display:block;font-size:2.4rem;margin-bottom:4px}
.lede{color:var(--muted);font-size:1.05rem;max-width:62ch}
a{color:var(--accent)}
h2{font-size:1.35rem;margin:48px 0 6px;font-weight:650}
h2+p.sub{color:var(--muted);margin:0 0 24px;max-width:62ch}
.song{border:1px solid var(--line);border-radius:10px;padding:20px 22px;margin:0 0 18px;background:#fff}
.song h3{margin:0;font-size:1.3rem;font-weight:650}
.translit{margin:2px 0 14px;color:var(--muted);font-size:.95rem}
dl.meta{display:flex;flex-wrap:wrap;gap:8px 28px;margin:0 0 14px;font-size:.88rem}
dl.meta div{display:flex;gap:6px}
dt{color:var(--muted)}dd{margin:0}
.badge{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:99px;
  font-size:.78rem;background:#e8f2ec;color:var(--ok);border:1px solid #cfe4d8}
audio{width:100%;height:38px;margin:2px 0 12px}
details summary{cursor:pointer;color:var(--muted);font-size:.9rem}
pre{overflow-x:auto;background:#faf8f5;border:1px solid var(--line);border-radius:7px;
  padding:12px 14px;font:13px/1.9 "SF Mono",Menlo,Consolas,"Noto Sans Bengali",monospace;margin:10px 0 0}
.links{font-size:.85rem;color:var(--muted);margin:12px 0 0}
.ab{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.ab>div{border:1px solid var(--line);border-radius:10px;padding:16px 18px;background:#fff}
.ab h4{margin:0 0 4px;font-size:1rem}
.ab p{margin:0 0 10px;color:var(--muted);font-size:.88rem}
blockquote{border-left:3px solid var(--accent);margin:20px 0;padding:2px 0 2px 16px;color:var(--ink)}
footer{margin-top:64px;padding-top:24px;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}
@media(max-width:620px){.ab{grid-template-columns:1fr}h1 .bn{font-size:1.9rem}h1{font-size:1.6rem}}
"""


def build():
    docs = [json.load(open(f, encoding="utf-8"))
            for f in sorted(glob.glob(str(ROOT / "data" / "songs" / "*.json")))]
    jsonld = (ROOT / "dataset.jsonld").read_text(encoding="utf-8")
    verified = sum(1 for d in docs if d["provenance"].get("scan_verification"))
    cards = "\n".join(song_card(d) for d in docs)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Songs of Tagore, In Data — listen</title>
<meta name="description" content="Thirty Rabindrasangeet digitized from akarmatrik swaralipi into open symbolic notation. Every recording here is synthesized from the notation itself.">
<style>{CSS}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<div class="wrap">

<header class="top">
  <h1><span class="bn">গান, ডেটায়</span>Songs of Tagore, In Data</h1>
  <p class="lede">Thirty Rabindrasangeet encoded from akarmatrik swaralipi into open symbolic
  notation, across twenty taal families. <strong>Nothing on this page is a recording.</strong> Every note you hear was
  synthesized directly from the data — so if a song sounds right, the digitization is right,
  and if a phrase sounds wrong, you have found a bug worth reporting.</p>
  <p class="lede"><a href="method.html"><strong>How it was made →</strong></a> an interactive
  walkthrough: the source, the decoding, the pipeline, the verification, and the experiment —
  with the notation following the audio as it plays.</p>
  <p class="lede"><a href="{REPO}">Repository</a> ·
  <a href="{REPO}/blob/main/docs/VERIFICATION.md">Verification record</a> ·
  <a href="{REPO}/blob/main/CONTRIBUTING.md">How to contribute</a></p>
</header>

<h2>The corpus</h2>
<p class="sub">{len(docs)} songs · {verified} checked line-by-line against scans of the printed
Swarabitan. Open “see the notation” on any song to read the swaralipi the audio is made from.</p>

{cards}

<h2>The experiment: can a model continue Tagore?</h2>
<p class="sub">We gave a frontier model (Claude) the nine other songs plus only the
<em>sthayi</em> of “Purano sei diner katha”, and asked it to compose the antara for Tagore's
actual words. It never saw what Tagore wrote. Same synthesizer, same tonic, same tempo in both
clips below — the only difference is the composition.</p>

<div class="ab">
  <div>
    <h4>Tagore's antara</h4>
    <p>Sthayi, then the real continuation.</p>
    <audio controls preload="none" src="experiment/purano_real_sthayi_antara.mp3"></audio>
  </div>
  <div>
    <h4>Claude's antara</h4>
    <p>Same sthayi, then the model's blind continuation.</p>
    <audio controls preload="none" src="experiment/purano_claude_continuation.mp3"></audio>
  </div>
</div>

<blockquote>The model broke no rules: exact 12-matra ektaal cycles, a note-set that stayed
inside the song's pentatonic frame, a cadence properly prepared to fall back into the sthayi. Then it did what nearly
every Hindustani antara does — it leapt to the upper octave. Tagore didn't. He stays in the
middle register and saves the one climb for three words: <em>প্রাণের মাঝে আয়</em> — come into
my heart. The music rises where the poem rises, not where the rulebook says.</blockquote>

<p><a href="{REPO}/blob/main/experiment/EXPERIMENT.md">Full method, prompt and output →</a></p>

<footer>
  Compositions by Rabindranath Tagore (1861–1941), public domain in India since 2002.
  Data <a href="{REPO}/blob/main/LICENSE">CC BY 4.0</a>, code MIT.
  Built by <a href="https://github.com/indranilbanerjee">Indranil Banerjee</a>.
  Corrections are the point — <a href="{REPO}/issues/new?template=notation-correction.yml">file one</a>.
</footer>

</div>
</body>
</html>
"""
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"wrote index.html ({len(page):,} bytes) — {len(docs)} songs, {verified} scan-verified")


if __name__ == "__main__":
    build()
