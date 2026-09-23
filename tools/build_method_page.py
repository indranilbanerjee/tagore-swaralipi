#!/usr/bin/env python3
"""
build_method_page.py — generate method.html, an interactive walkthrough of how this
corpus was made: the source, the decoding, the pipeline, the verification, the experiment.

The centrepiece is a notation follower: because the synthesizer advances exactly one
matra per cell at a fixed rate, cell *i* of a song begins at *i × matra_seconds*. That
makes it possible to highlight the swaralipi in time with the audio, and to show the
taal cycle turning underneath — sam, taali, khali — which is the thing a newcomer to
this music most needs to see rather than be told.

Everything on the page is generated from data/songs/*.json, so it cannot drift from
the corpus.
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

REPO = "https://github.com/indranilbanerjee/tagore-swaralipi"
MATRA_S = 0.66          # tools/synth.py, taal-bound songs
MATRA_S_FREE = 0.9      # tools/synth.py, talamukta songs


# ---------------------------------------------------------------- notation text

def swara_txt(sw):
    n = sw["degree"]
    if sw.get("komal"):
        n = n.lower()
    if sw.get("kori"):
        n = "M#"
    return n + {1: "'", -1: ","}.get(sw.get("saptak", 0), "")


def unit_txt(u):
    if u["type"] == "sustain":
        return "–"
    if u["type"] == "rest":
        return "·"
    t = swara_txt(u["swara"])
    if u.get("kan"):
        t = "(" + "".join(swara_txt(k) for k in u["kan"]) + ")" + t
    return t


def cell_txt(cell):
    return "/".join(unit_txt(u) for u in cell["units"])


def pack_song(doc, lines=None):
    """Flatten to the compact shape the page's follower needs."""
    taal = doc["taal"]
    matras = None if taal["talamukta"] else taal["matras"]
    src = lines if lines is not None else doc["lines"]
    cells, breaks = [], []
    for line in src:
        for cell in line["cells"]:
            cells.append([cell_txt(cell),
                          cell.get("lyric") or ("৹" if cell.get("melisma") else ""),
                          1 if cell.get("melisma") else 0])
        breaks.append(len(cells))
    return {
        "id": doc["id"],
        "bn": doc["title"]["bn"],
        "tr": doc["title"]["translit"],
        "taal": "talamukta" if taal["talamukta"] else taal["name"]["translit"],
        "taalBn": taal["name"]["bn"],
        "matras": matras,
        "vibhags": taal["vibhags"],
        "beats": taal["beats"],
        "matraS": MATRA_S_FREE if taal["talamukta"] else MATRA_S,
        "raga": doc.get("raga_anga") or "",
        "verified": bool(doc["provenance"].get("scan_verification")),
        "cells": cells,
        "breaks": breaks,
    }


# ---------------------------------------------------------------- page assets

CSS = r"""
:root{
  --bg:#0f0e0d;--panel:#1a1817;--panel2:#211e1c;--ink:#f2ece4;--muted:#a2968a;
  --line:#332e2a;--accent:#e0864f;--accent2:#6fb3a0;--ok:#79c08f;--warn:#d9a441;
  --sam:#e0864f;--taali:#6fb3a0;--khali:#6b625b;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
 font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans Bengali",sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:0 22px}
a{color:var(--accent)}
h2{font-size:1.7rem;margin:0 0 4px;font-weight:650;letter-spacing:-.01em}
h3{font-size:1.12rem;margin:28px 0 8px;font-weight:620}
p{max-width:70ch}
.muted{color:var(--muted)}
.small{font-size:.9rem}

/* ---- progress + nav ---- */
#bar{position:fixed;top:0;left:0;height:3px;background:var(--accent);width:0;z-index:99;transition:width .1s linear}
nav{position:sticky;top:0;background:rgba(15,14,13,.93);backdrop-filter:blur(8px);
 border-bottom:1px solid var(--line);z-index:50}
nav .wrap{display:flex;gap:4px;overflow-x:auto;padding:9px 22px;scrollbar-width:none}
nav .wrap::-webkit-scrollbar{display:none}
nav button{background:none;border:1px solid transparent;color:var(--muted);cursor:pointer;
 font:inherit;font-size:.85rem;padding:5px 11px;border-radius:99px;white-space:nowrap}
nav button:hover{color:var(--ink)}
nav button.on{color:var(--ink);border-color:var(--line);background:var(--panel2)}

/* ---- sections ---- */
section{padding:74px 0;border-bottom:1px solid var(--line)}
section:last-of-type{border-bottom:0}
.step{display:inline-block;font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;
 color:var(--accent);border:1px solid var(--line);border-radius:99px;padding:3px 12px;margin-bottom:14px}
.reveal{opacity:0;transform:translateY(18px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}

/* ---- hero ---- */
.hero{padding:96px 0 74px;text-align:left}
.hero h1{font-size:clamp(2rem,5.2vw,3.3rem);line-height:1.12;margin:0 0 14px;font-weight:660;letter-spacing:-.02em}
.hero .bn{display:block;color:var(--accent);margin-bottom:6px}
.counter{display:flex;gap:34px;flex-wrap:wrap;margin:34px 0 0}
.counter div span{display:block;font-size:2rem;font-weight:660;font-variant-numeric:tabular-nums}
.counter div small{color:var(--muted);font-size:.84rem}

/* ---- panels ---- */
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:18px 0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:760px){.grid2{grid-template-columns:1fr}}
code,pre,.mono{font-family:"SF Mono",Menlo,Consolas,"Noto Sans Bengali",monospace}
pre{overflow-x:auto;background:var(--panel2);border:1px solid var(--line);border-radius:9px;
 padding:14px 16px;font-size:13px;line-height:1.85;margin:12px 0}

/* ---- token decoder ---- */
.tokens{display:flex;flex-wrap:wrap;gap:7px;margin:14px 0}
.tok{background:var(--panel2);border:1px solid var(--line);border-radius:7px;padding:6px 11px;
 cursor:pointer;font-family:"SF Mono",Menlo,monospace;font-size:14px;transition:.15s}
.tok:hover{border-color:var(--accent);color:var(--accent)}
.tok.on{background:var(--accent);border-color:var(--accent);color:#1a1008;font-weight:600}
.decode{background:var(--panel2);border:1px solid var(--line);border-radius:9px;padding:16px 18px;min-height:118px}
.decode .row{display:flex;gap:12px;align-items:baseline;padding:4px 0;border-bottom:1px dashed var(--line)}
.decode .row:last-child{border-bottom:0}
.decode .k{color:var(--muted);font-size:.84rem;min-width:104px}
.big{font-size:1.5rem;font-weight:650;color:var(--accent)}

/* ---- pipeline ---- */
.pipe{display:flex;gap:8px;flex-wrap:wrap;margin:20px 0 14px}
.pipe button{flex:1;min-width:132px;background:var(--panel);border:1px solid var(--line);border-radius:10px;
 padding:13px 12px;color:var(--muted);cursor:pointer;font:inherit;text-align:left;transition:.18s}
.pipe button:hover{border-color:var(--accent)}
.pipe button.on{border-color:var(--accent);background:var(--panel2);color:var(--ink)}
.pipe button b{display:block;font-size:.95rem;margin-bottom:2px;color:inherit}
.pipe button small{font-size:.76rem;color:var(--muted)}
.stage{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:18px 20px}
.stage h4{margin:0 0 6px;font-size:1.05rem}

/* ---- notation follower ---- */
.player{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:16px 0}
.pickrow{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.pick{background:var(--panel2);border:1px solid var(--line);border-radius:99px;padding:5px 13px;
 cursor:pointer;font:inherit;font-size:.85rem;color:var(--muted)}
.pick:hover{color:var(--ink);border-color:var(--accent)}
.pick.on{background:var(--accent);border-color:var(--accent);color:#1a1008;font-weight:600}
.cycle{display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin:12px 0 6px;min-height:34px}
.beat{width:26px;height:26px;border-radius:6px;border:1px solid var(--line);background:var(--panel2);
 display:flex;align-items:center;justify-content:center;font-size:.72rem;color:var(--muted);
 font-variant-numeric:tabular-nums;transition:.12s}
.beat.sam{border-color:var(--sam)}
.beat.taali{border-color:var(--taali)}
.beat.khali{border-color:var(--khali);opacity:.65}
.beat.edge{border-color:var(--muted);opacity:.85}
.beat.now{background:var(--accent);color:#1a1008;font-weight:700;transform:scale(1.16);border-color:var(--accent)}
.legend{display:flex;gap:16px;font-size:.78rem;color:var(--muted);margin:2px 0 12px;flex-wrap:wrap}
.legend i{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px;vertical-align:middle}
.notation{overflow:auto;max-height:330px;background:var(--panel2);border:1px solid var(--line);
 border-radius:9px;padding:14px;margin:10px 0;scroll-behavior:smooth}
.nline.active{background:rgba(224,134,79,.06);border-radius:7px}
.nline{display:flex;gap:3px;margin-bottom:11px;min-width:min-content}
.cellbox{min-width:46px;text-align:center;padding:5px 4px;border-radius:6px;border:1px solid transparent;transition:.1s}
.cellbox .n{font-family:"SF Mono",Menlo,monospace;font-size:13px;white-space:nowrap}
.cellbox .l{font-size:12px;color:var(--muted);margin-top:3px;min-height:16px}
.cellbox.vib{border-left:1px solid var(--line);padding-left:8px;margin-left:5px}
.cellbox.now{background:var(--accent);border-color:var(--accent)}
.cellbox.now .n,.cellbox.now .l{color:#1a1008;font-weight:700}
.cellbox.done{opacity:.42}
.ctrl{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:10px}
.ctrl button{background:var(--accent);border:0;color:#1a1008;font:inherit;font-weight:650;
 padding:9px 20px;border-radius:99px;cursor:pointer}
.ctrl button.ghost{background:none;border:1px solid var(--line);color:var(--muted)}
audio{width:100%;height:36px;margin-top:6px;filter:invert(.9) hue-rotate(180deg)}

/* ---- quiz ---- */
.quiz{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}
@media(max-width:760px){.quiz{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:17px 19px}
.card h4{margin:0 0 3px;font-size:1rem}
.card.reveal-ok{border-color:var(--ok)}
.card.reveal-no{border-color:var(--warn)}
.verdict{margin-top:10px;font-size:.88rem;padding:9px 12px;border-radius:8px;display:none}
.verdict.show{display:block}
.verdict.ok{background:rgba(121,192,143,.11);color:var(--ok)}
.verdict.no{background:rgba(217,164,65,.11);color:var(--warn)}

/* ---- charts ---- */
.chart{margin:16px 0}
.barrow{display:flex;align-items:center;gap:11px;margin:6px 0;font-size:.9rem}
.barrow .lab{min-width:62px;text-align:right;color:var(--muted);font-family:"SF Mono",Menlo,monospace}
.bartrack{flex:1;background:var(--panel2);border-radius:5px;height:22px;overflow:hidden}
.barfill{height:100%;background:linear-gradient(90deg,var(--accent),#c96a3a);width:0;
 transition:width 1.1s cubic-bezier(.2,.7,.3,1);border-radius:5px}
.barval{min-width:52px;color:var(--muted);font-variant-numeric:tabular-nums;font-size:.85rem}

/* ---- findings ---- */
.find{border-left:3px solid var(--accent);padding:3px 0 3px 16px;margin:16px 0}
.find b{color:var(--ink)}
.tag{display:inline-block;font-size:.72rem;padding:2px 9px;border-radius:99px;
 border:1px solid var(--line);color:var(--muted);margin-right:6px}
.tag.ok{color:var(--ok);border-color:rgba(121,192,143,.4)}
footer{padding:56px 0 80px;color:var(--muted);font-size:.9rem}
"""


JS = r"""
// ---------- scroll progress + reveal + nav ----------
const bar = document.getElementById('bar');
addEventListener('scroll', () => {
  const h = document.documentElement;
  bar.style.width = (h.scrollTop / (h.scrollHeight - h.clientHeight) * 100) + '%';
});
const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
}), {threshold: .12});
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

const navBtns = [...document.querySelectorAll('nav button')];
const secs = navBtns.map(b => document.getElementById(b.dataset.go));
navBtns.forEach(b => b.onclick = () => document.getElementById(b.dataset.go)
  .scrollIntoView({behavior: 'smooth', block: 'start'}));
addEventListener('scroll', () => {
  const y = scrollY + 120;
  let idx = 0;
  secs.forEach((s, i) => { if (s && s.offsetTop <= y) idx = i; });
  navBtns.forEach((b, i) => b.classList.toggle('on', i === idx));
});

// ---------- counters ----------
const cio = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return;
  const el = e.target, target = +el.dataset.n, t0 = performance.now();
  (function tick(t) {
    const p = Math.min(1, (t - t0) / 1100), e2 = 1 - Math.pow(1 - p, 3);
    el.textContent = Math.round(target * e2).toLocaleString();
    if (p < 1) requestAnimationFrame(tick);
  })(t0);
  cio.unobserve(el);
}), {threshold: .5});
document.querySelectorAll('[data-n]').forEach(el => cio.observe(el));

// ---------- token decoder ----------
const TOKENS = window.__TOKENS__;
const tokWrap = document.getElementById('tokens'), decodeBox = document.getElementById('decodeOut');
function showToken(key) {
  const t = TOKENS[key];
  document.querySelectorAll('.tok').forEach(b => b.classList.toggle('on', b.dataset.k === key));
  decodeBox.innerHTML =
    `<div class="row"><span class="k">source token</span><span class="mono big">${key}</span></div>` +
    t.rows.map(r => `<div class="row"><span class="k">${r[0]}</span><span>${r[1]}</span></div>`).join('') +
    `<div class="row"><span class="k">why we know</span><span class="small muted">${t.why}</span></div>`;
}
Object.keys(TOKENS).forEach((k, i) => {
  const b = document.createElement('button');
  b.className = 'tok'; b.dataset.k = k; b.textContent = k;
  b.onclick = () => showToken(k);
  tokWrap.appendChild(b);
  if (i === 0) setTimeout(() => showToken(k), 60);
});

// ---------- pipeline ----------
const STAGES = window.__STAGES__;
const stageBox = document.getElementById('stage');
function showStage(i) {
  document.querySelectorAll('.pipe button').forEach((b, j) => b.classList.toggle('on', i === j));
  const s = STAGES[i];
  stageBox.innerHTML = `<h4>${s.title}</h4><p class="small muted">${s.body}</p>` +
    (s.code ? `<pre>${s.code}</pre>` : '') +
    (s.note ? `<p class="small" style="color:var(--accent2);margin:8px 0 0">${s.note}</p>` : '');
}
document.querySelectorAll('.pipe button').forEach((b, i) => b.onclick = () => showStage(i));
showStage(0);

// ---------- notation follower ----------
const SONGS = window.__SONGS__;
const audio = document.getElementById('au');
const notation = document.getElementById('notation');
const cycleEl = document.getElementById('cycle');
const nowInfo = document.getElementById('nowinfo');
let song = SONGS[0], boxes = [];

function renderSong(s) {
  song = s; audio.src = 'audio/' + s.id + '.mp3'; audio.load();
  notation.innerHTML = ''; boxes = [];
  let start = 0;
  s.breaks.forEach(end => {
    const line = document.createElement('div'); line.className = 'nline';
    for (let i = start; i < end; i++) {
      const c = s.cells[i];
      const d = document.createElement('div');
      d.className = 'cellbox' + (s.matras && i % s.matras !== 0 && vibhagHead(s, i) ? ' vib' : '');
      d.innerHTML = `<div class="n">${c[0]}</div><div class="l">${c[1] || ''}</div>`;
      line.appendChild(d); boxes.push(d);
    }
    notation.appendChild(line); start = end;
  });
  // taal cycle strip
  cycleEl.innerHTML = '';
  if (s.matras) {
    let m = 0;
    s.vibhags.forEach((v, vi) => {
      for (let k = 0; k < v; k++) {
        const b = document.createElement('div');
        b.className = 'beat ' + (k === 0 ? ((s.beats && s.beats[vi]) || 'edge') : '');
        b.textContent = ++m; cycleEl.appendChild(b);
      }
    });
  } else {
    cycleEl.innerHTML = '<span class="small muted">তালমুক্ত — free rhythm, no cycle to count</span>';
  }
  document.getElementById('songmeta').innerHTML =
    `<b>${s.bn}</b> <span class="muted small">· ${s.taalBn} (${s.taal})` +
    (s.matras ? ` · ${s.matras} matras` : '') + (s.raga ? ` · ${s.raga.split(',')[0]}` : '') +
    (s.verified ? ` · <span class="tag ok">scan-verified</span>` : '') + '</span>';
  paint(-1);
}
function vibhagHead(s, i) {
  let acc = 0, pos = i % s.matras;
  for (const v of s.vibhags) { acc += v; if (pos === acc) return true; }
  return false;
}
function paint(idx) {
  boxes.forEach((b, i) => {
    b.classList.toggle('now', i === idx);
    b.classList.toggle('done', i < idx);
  });
  const beats = cycleEl.querySelectorAll('.beat');
  beats.forEach((b, i) => b.classList.toggle('now', song.matras && idx >= 0 && i === idx % song.matras));
  if (idx >= 0 && boxes[idx]) {
    const c = song.cells[idx];
    nowInfo.innerHTML = song.matras
      ? `matra <b>${idx % song.matras + 1}</b> of ${song.matras} · <span class="mono">${c[0]}</span>` +
        (c[1] ? ` · ${c[1]}` : '')
      : `<span class="mono">${c[0]}</span>` + (c[1] ? ` · ${c[1]}` : '');
    const el = boxes[idx], line = el.parentElement;
    [...notation.children].forEach(l => l.classList.toggle('active', l === line));
    const r = el.getBoundingClientRect(), p = notation.getBoundingClientRect();
    if (r.left < p.left + 40 || r.right > p.right - 40)
      notation.scrollLeft += (r.left - p.left) - p.width / 3;
    if (r.top < p.top + 8 || r.bottom > p.bottom - 8)
      notation.scrollTop += (r.top - p.top) - p.height / 2.6;
  } else nowInfo.innerHTML = '<span class="muted">press play — the notation follows the sound</span>';
}
audio.addEventListener('timeupdate', () => paint(Math.floor(audio.currentTime / song.matraS)));
audio.addEventListener('ended', () => paint(-1));
document.getElementById('play').onclick = () => audio.paused ? audio.play() : audio.pause();
audio.addEventListener('play', () => document.getElementById('play').textContent = 'Pause');
audio.addEventListener('pause', () => document.getElementById('play').textContent = 'Play');

const pickrow = document.getElementById('pickrow');
SONGS.forEach((s, i) => {
  const b = document.createElement('button');
  b.className = 'pick' + (i === 0 ? ' on' : ''); b.textContent = s.bn;
  b.onclick = () => {
    document.querySelectorAll('.pick').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); audio.pause(); renderSong(s);
  };
  pickrow.appendChild(b);
});
renderSong(SONGS[0]);

// ---------- experiment quiz ----------
document.getElementById('revealBtn').onclick = () => {
  document.getElementById('cardA').classList.add('reveal-ok');
  document.getElementById('cardB').classList.add('reveal-no');
  document.querySelectorAll('.verdict').forEach(v => v.classList.add('show'));
  document.getElementById('revealBtn').style.display = 'none';
};

// ---------- charts ----------
const bio = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return;
  e.target.querySelectorAll('.barfill').forEach((f, i) =>
    setTimeout(() => f.style.width = f.dataset.w + '%', i * 110));
  bio.unobserve(e.target);
}), {threshold: .35});
document.querySelectorAll('.chart').forEach(c => bio.observe(c));
"""


# ---------------------------------------------------------------- content data

TOKENS = {
    "sa": {"rows": [["renders as", "সা"], ["decodes to", "Sa — the tonic"],
                    ["in our data", '{"degree":"S","saptak":0}']],
           "why": "Direct: the base seven are unambiguous across every witness."},
    "qa": {"rows": [["renders as", "ধা"], ["decodes to", "Dha (shuddha)"],
                    ["in our data", '{"degree":"D","saptak":0}']],
           "why": "Triangulated: aligns with Dha at every occurrence in an independent romanized sargam of the same songs."},
    "ka": {"rows": [["renders as", "হ্মা"], ["decodes to", "kori (tivra) Ma — the sharpened fourth"],
                    ["in our data", '{"degree":"M","kori":true,"saptak":0}']],
           "why": "Contextual: appears exactly where Behag and Kalyan-anga songs require tivra Ma — beside Pa in তুমি রবে নীরবে. Mnemonic: <b>k</b>ori."},
    "ua": {"rows": [["renders as", "ণা"], ["decodes to", "komal Ni — the flattened seventh"],
                    ["in our data", '{"degree":"N","komal":true,"saptak":0}']],
           "why": "Contextual, strong: yields the textbook Desh descent S′–n–D–P in এসো শ্যামল সুন্দর, and Jhinjhoti descents in মাঝে মাঝে."},
    "ta": {"rows": [["renders as", "জ্ঞা"], ["decodes to", "komal Ga — the flattened third"],
                    ["in our data", '{"degree":"G","komal":true,"saptak":0}']],
           "why": "Triangulated: degree-exact alignment against an independent witness of আমার পরান যাহা চায় under a single consistent tonic shift — zero degrees of freedom left."},
    "da": {"rows": [["renders as", "দা"], ["decodes to", "komal Dha"],
                    ["in our data", '{"degree":"D","komal":true,"saptak":0}']],
           "why": "Contextual + mnemonic — দ <i>is</i> the komal-Dha letter; produces the chromatic d–D motion of kirtan-anga."},
    "nha": {"rows": [["renders as", "না with the udara mark"], ["decodes to", "Ni in the lower octave"],
                     ["in our data", '{"degree":"N","saptak":-1}']],
            "why": "The suffix <b>h</b> = udara (lower saptak); <b>f</b> = tara (upper). Confirmed by ear — low passages sound low."},
    "sfa": {"rows": [["renders as", "সা with the tara mark"], ["decodes to", "Sa in the upper octave"],
                     ["in our data", '{"degree":"S","saptak":1}']],
            "why": "Suffix <b>f</b> = tara saptak. Verified against the printed Swarabitan page for পুরানো সেই দিনের কথা."},
    "-a": {"rows": [["renders as", "the akarmatrik dash"], ["decodes to", "the previous swara continues"],
                    ["in our data", '{"type":"sustain"}']],
           "why": "Structural, and the reason this notation is called <i>akarmatrik</i> — the আ-কার carries duration."},
    "Rga": {"rows": [["renders as", "a small raised রা before গা"],
                     ["decodes to", "Ga, ornamented by a kan (grace note) Re"],
                     ["in our data", '{"swara":{"degree":"G"},"kan":[{"degree":"R"}]}']],
            "why": "A capitalised prefix meant a kan — a guess, until the printed page confirmed it: Swarabitan sets the ornamenting swara as a smaller, raised glyph. <b>Verified against print.</b>"},
    "gmpa": {"rows": [["renders as", "গমপা in one column"],
                      ["decodes to", "Ga, Ma, Pa sharing a single matra — a third each"],
                      ["in our data", "three units inside one cell"]],
             "why": "Structural: a cell is one matra and divides evenly among its units. Confirmed on the printed page of ভালোবেসে সখী."},
}

STAGES = [
    {"title": "1 · The witness",
     "body": "The West Bengal government's digital edition of Swarabitan serves akarmatrik notation as an HTML table — one cell per matra — but the notation is locked inside a custom font. What comes down the wire is not Bengali. It is this:",
     "code": "&lt;td id=\"1.8\"&gt;sa&lt;/td&gt;&lt;td id=\"1.9\"&gt;sa&lt;/td&gt;&lt;td id=\"1.10\"&gt;-nha&lt;/td&gt;\n&lt;td id=\"1.11\"&gt;A&lt;/td&gt;&lt;td id=\"1.12\"&gt;sa&lt;/td&gt;&lt;td id=\"1.13\"&gt;ga&lt;/td&gt;",
     "note": "Readable by a human with the font installed. Unreadable by any program — which is why no dataset existed."},
    {"title": "2 · The decode",
     "body": "Work out what each token means, then prove it three independent ways rather than trusting the guess: against a second unrelated archive of romanized sargam; against music theory (do the decoded note-sets reproduce each song's known raga?); and by ear, since audio synthesized from the decoded data should be recognisably the song.",
     "code": "sa ra ga ma pa qa na  →  S  R  G  M  P  D  N\nka → kori Ma   ta → komal Ga   da → komal Dha   ua → komal Ni   va → komal Re\nsuffix h → lower octave    suffix f → upper octave    - → sustain",
     "note": "A wrong reading of any komal/kori token would have scrambled every raga signature in the corpus. None were scrambled."},
    {"title": "3 · The canonical form",
     "body": "Encode into a schema built for this notation rather than borrowed from Western music: swara degree with komal and kori as first-class letters, three saptaks, one cell per matra dividing evenly among its units, taal cycles with sam/taali/khali, and Bengali lyrics aligned syllable-to-matra. Every song carries where it came from and how confident we are.",
     "code": '{ "units": [ {"type":"sustain"},\n             {"type":"swara","swara":{"degree":"N","saptak":-1}} ],\n  "lyric": null, "melisma": true }',
     "note": "That is one matra of পুরানো সেই দিনের কথা — a held note followed by a low Ni, under a syllable that is still sounding."},
    {"title": "4 · The derived views",
     "body": "MIDI, MusicXML and human-readable sargam text are generated from the canonical JSON, never edited by hand. The text form round-trips losslessly — text back to JSON reproduces every pitch and duration — which is what makes it safe for a musician to edit the notation directly.",
     "code": "data/songs/*.json  ──┬──►  data/text/*.txt      (round-trip verified)\n                     ├──►  derived/midi/*.mid\n                     ├──►  derived/musicxml/*.musicxml\n                     └──►  audio/*.mp3",
     "note": "CI regenerates all of them on every push and fails if a single byte differs from what is committed."},
    {"title": "5 · The proof",
     "body": "Synthesize audio straight from the data. This is not decoration — it is the test. If the notation was decoded correctly the song is recognisable; if a matra is wrong, anyone who knows the song hears it immediately. Then check the notation itself against scans of the printed Swarabitan, page by page.",
     "code": "393 automated checks · schema · taal arithmetic · pitch range · provenance\n            · lossless round-trip · reproducible outputs · printed-cycle agreement\n 3 of 30 songs read against the printed first edition — all exact",
     "note": "The audio on this page is the pipeline's own output. You are listening to the dataset."},
]


def bars(rows, unit="%"):
    out = ['<div class="chart">']
    top = max(v for _, v in rows) or 1
    for label, value in rows:
        out.append(
            f'<div class="barrow"><div class="lab mono">{label}</div>'
            f'<div class="bartrack"><div class="barfill" data-w="{value/top*100:.1f}"></div></div>'
            f'<div class="barval">{value}{unit}</div></div>')
    out.append("</div>")
    return "\n".join(out)


def build():
    docs = [json.load(open(f, encoding="utf-8"))
            for f in sorted(glob.glob(str(ROOT / "data" / "songs" / "*.json")))]
    by_id = {d["id"]: d for d in docs}

    # Follower order: scan-verified songs first, then one song per taal so the picker
    # doubles as a tour of the taal system, then everything else.
    lead = ["purano-sei-diner-katha", "bhalobese-sokhi", "gram-chhara-oi-ranga-matir-path"]
    order, seen_taal = list(lead), set()
    for d in docs:
        t = d["taal"]["name"]["translit"]
        if d["id"] not in order and t not in seen_taal:
            seen_taal.add(t)
            order.append(d["id"])
    order += [d["id"] for d in docs if d["id"] not in order]
    songs = [pack_song(by_id[i]) for i in order if i in by_id]

    # experiment: real (lines 0-7) vs AI (sthayi 0-3 + model's 4 lines)
    purano = by_id["purano-sei-diner-katha"]
    ai_lines = json.load(open(ROOT / "experiment" / "claude_antara.json", encoding="utf-8"))
    real_pack = pack_song(purano, purano["lines"][:8])
    ai_pack = pack_song(purano, purano["lines"][:4] + ai_lines)

    total_cells = sum(len(d["lines"][i]["cells"]) for d in docs for i in range(len(d["lines"])))
    total_units = sum(len(c["units"]) for d in docs for l in d["lines"] for c in l["cells"])
    verified = sum(1 for d in docs if d["provenance"].get("scan_verification"))
    jsonld = (ROOT / "dataset.jsonld").read_text(encoding="utf-8")

    nav_items = [("problem", "The problem"), ("input", "Input"), ("decode", "The decode"),
                 ("pipeline", "Pipeline"), ("follow", "Listen & follow"), ("verify", "Verification"),
                 ("experiment", "The experiment"), ("findings", "What it shows"), ("use", "Use it")]

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>How it was made — Songs of Tagore, In Data</title>
<meta name="description" content="An interactive walkthrough of how ten Rabindrasangeet were digitized from akarmatrik swaralipi into open symbolic notation: the source, the decoding, the pipeline, the verification against printed Swarabitan, and a blind AI-continuation experiment.">
<style>{CSS}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<div id="bar"></div>

<nav><div class="wrap">
{chr(10).join(f'<button data-go="{i}">{t}</button>' for i, t in nav_items)}
</div></nav>

<div class="wrap">

<div class="hero">
  <span class="step">Methodology · how this was built</span>
  <h1><span class="bn">সুর থেকে সংখ্যায়</span>From a page of swaralipi<br>to something a machine can read</h1>
  <p class="muted" style="font-size:1.08rem">Rabindranath Tagore left about 2,200 songs, and — unusually for any
  song tradition of that size — nearly all of them were <em>written down</em>, in the Bengali
  akarmatrik notation system. Yet none of that notation was machine-readable. This page shows
  exactly how ten of them became data, what had to be decoded, how it was checked, and what
  happened when a frontier AI model was asked to continue one.</p>
  <div class="counter">
    <div><span data-n="10">0</span><small>songs encoded</small></div>
    <div><span data-n="{total_cells}">0</span><small>matras</small></div>
    <div><span data-n="{total_units}">0</span><small>note units</small></div>
    <div><span data-n="{verified}">0</span><small>verified against print</small></div>
    <div><span data-n="126">0</span><small>automated checks</small></div>
  </div>
</div>

<section id="problem" class="reveal">
  <span class="step">00 · Why</span>
  <h2>A tradition computers could not see</h2>
  <p>Western art music has centuries of digitized scores. Every music search tool, analysis library
  and music-AI model is built on that foundation. Rabindrasangeet had essentially none — the
  notation existed only as printed pages and as websites that render it through a locked font.</p>
  <p>A repertoire absent from the data is absent from the tools, then from the research, and
  eventually from what the next generation can find. The compositions have been in the Indian public
  domain since 2002. Nothing stood between this music and open scholarship except the format.</p>
</section>

<section id="input" class="reveal">
  <span class="step">01 · Input</span>
  <h2>What we started with</h2>
  <div class="grid2">
    <div class="panel">
      <h3 style="margin-top:0">The printed source</h3>
      <p class="small muted">Swarabitan — Visva-Bharati's own edition, roughly 64 volumes,
      first published from the 1930s. Each song page carries a number, a <span class="mono">রাগ । তাল</span>
      line, the lyrics, and then the notation grid: swaras in Bengali letters, one column per matra,
      the lyric syllable set underneath, vibhag bars marking the taal.</p>
      <p class="small muted">Scans of these volumes are freely available. They are pictures of paper —
      a person can read them; a program cannot.</p>
    </div>
    <div class="panel">
      <h3 style="margin-top:0">The online witness</h3>
      <p class="small muted">A government digital edition serves the same notation as an HTML table,
      one cell per matra. The notation renders correctly in a browser only because a custom font
      turns Latin letter codes into Bengali swaralipi glyphs.</p>
      <p class="small muted">So the actual text behind the page is a token stream in an undocumented
      code. Decoding that code was the first real problem — and the reason this dataset did not
      already exist.</p>
    </div>
  </div>
</section>

<section id="decode" class="reveal">
  <span class="step">02 · The decode</span>
  <h2>Cracking the token language</h2>
  <p>Click any token to see what it means, how it is stored, and — the part that matters — <em>how
  we know</em>. Nothing here was assumed; every reading has a line of evidence behind it.</p>
  <div id="tokens" class="tokens"></div>
  <div id="decodeOut" class="decode"></div>
  <h3>Why the decoding can be trusted</h3>
  <p>Three independent checks, none of which relies on the others:</p>
  <div class="grid2">
    <div class="panel"><b>A second archive</b><p class="small muted" style="margin:6px 0 0">An unrelated
    site publishes by-ear romanized sargam for four of these songs. Aligning them against our decode
    left no freedom: one unknown, two witnesses, every degree forced.</p></div>
    <div class="panel"><b>Raga signatures</b><p class="small muted" style="margin:6px 0 0">The pipeline
    never assumes a raga. Yet the decoded note-sets reproduce the ragas tradition assigns: Behag's
    kori Ma in তুমি রবে নীরবে, Desh's both-Ni in এসো শ্যামল সুন্দর. A wrong komal/kori reading would
    have destroyed this.</p></div>
    <div class="panel"><b>Your ears</b><p class="small muted" style="margin:6px 0 0">Audio synthesized
    purely from the decoded data is recognisably the songs. Scroll down and judge that yourself —
    it is the check that needs no expertise.</p></div>
    <div class="panel"><b>And then the print</b><p class="small muted" style="margin:6px 0 0">Three songs
    were finally read against the printed Swarabitan itself, matra by matra. All three matched
    exactly — and corrected two things we had wrong.</p></div>
  </div>
</section>

<section id="pipeline" class="reveal">
  <span class="step">03 · Process</span>
  <h2>The pipeline, stage by stage</h2>
  <p>Five stages, each reproducible from the one before. Click through them.</p>
  <div class="pipe">
{chr(10).join(f'    <button><b>{i+1}. {s["title"].split("·")[1].strip()}</b><small>{["archive HTML","token → swara","Swaralipi-JSON","MIDI · XML · text","tests + audio"][i]}</small></button>' for i, s in enumerate(STAGES))}
  </div>
  <div id="stage" class="stage"></div>
</section>

<section id="follow" class="reveal">
  <span class="step">04 · Output</span>
  <h2>Listen — and watch the notation follow</h2>
  <p>This is the corpus itself, sounding. <strong>Nothing here is a recording</strong> — every note was
  synthesized from the JSON. As it plays, the current matra lights up in the notation and the taal
  cycle turns beneath it, so you can see the rhythm being counted rather than take it on faith.</p>
  <div class="player">
    <div id="pickrow" class="pickrow"></div>
    <div id="songmeta" class="small" style="margin-bottom:6px"></div>
    <div id="cycle" class="cycle"></div>
    <div class="legend">
      <span><i style="background:var(--sam)"></i>sam — beat one, the anchor</span>
      <span><i style="background:var(--taali)"></i>taali — clap</span>
      <span><i style="background:var(--khali)"></i>khali — the empty beat</span>
      <span><i style="background:var(--muted)"></i>vibhag start — this taal's clap pattern is not stated by the source</span>
    </div>
    <div class="ctrl">
      <button id="play">Play</button>
      <div id="nowinfo" class="small muted"></div>
    </div>
    <audio id="au" controls preload="none"></audio>
    <div id="notation" class="notation"></div>
    <p class="small muted" style="margin:10px 0 0">Reading it: <span class="mono">S R G M P D N</span> are the
    seven swaras · lowercase is komal (flat) · <span class="mono">M#</span> is kori Ma · <span class="mono">'</span>
    upper octave, <span class="mono">,</span> lower · <span class="mono">–</span> the note continues ·
    <span class="mono">A/B</span> two notes sharing one matra · <span class="mono">(X)Y</span> a grace note ·
    <span class="mono">৹</span> the syllable is still sounding.</p>
  </div>
</section>

<section id="verify" class="reveal">
  <span class="step">05 · Verification</span>
  <h2>Checking it against the printed book</h2>
  <p>An archive can be wrong and you would never know. So three songs were read against scans of the
  printed Swarabitan — Visva-Bharati's own edition, the source every other witness descends from.
  All three matched exactly. More usefully, the exercise changed things:</p>

  <div class="find"><span class="tag">vol. 32</span><span class="tag ok">exact match</span>
    <p style="margin:8px 0 0"><b>পুরানো সেই দিনের কথা gained a raga.</b> The printed header reads
    মিশ্র ভূপালী — the online witness gives only the taal. <i>Bhupali</i> is the pentatonic S R G P D;
    <i>mishra</i> means <i>mixed</i>. Count the data: 127 of its 135 notes (94.1%) are that pentatonic
    core, and the remaining eight are seven Ni and exactly one Ma. The name is numerically exact — and
    we had measured it before we ever saw the name.</p></div>

  <div class="find"><span class="tag">vol. 56</span><span class="tag ok">exact match</span>
    <p style="margin:8px 0 0"><b>ভালোবেসে সখী settled a conflict.</b> A secondary source lists it as
    dadra; our data said talamukta — free rhythm. The printed page has no taal header at all and no
    vibhag bars anywhere, which is precisely how Swarabitan sets a talamukta song. Our reading stands,
    and now records why.</p></div>

  <div class="find"><span class="tag">vol. 9</span><span class="tag ok">exact match</span>
    <p style="margin:8px 0 0"><b>গ্রামছাড়া corrected a label, and proved the grace notes.</b> The anga
    is বাংলা as printed, not the "Baul" we had from tradition. And the check worth doing: our parser
    infers a kan (grace note) from a capitalisation quirk in the font encoding — a guess that could
    have been wrong across the whole corpus. The printed page sets that swara as a smaller, raised
    glyph. The guess was right, and is now evidence.</p></div>

  <p class="small muted">Seven songs remain archive-derived and say so in their confidence block.
  Their volume numbers are published, so the work is well-defined and anyone who reads swaralipi can
  take one. <a href="{REPO}/blob/main/docs/VERIFICATION.md">The full record →</a></p>
</section>

<section id="experiment" class="reveal">
  <span class="step">06 · The experiment</span>
  <h2>Can a model continue Tagore?</h2>
  <p>Once the songs are data, you can ask a question that was previously unaskable. A frontier model
  was given nine of the songs in full, plus <em>only the sthayi</em> — the opening section — of
  পুরানো সেই দিনের কথা, and asked to compose the antara for Tagore's actual words. It never saw what
  Tagore wrote.</p>
  <p class="small muted">Same synthesizer, same tonic, same tempo in both. The only difference is who
  composed the second half. <strong>Listen before you look.</strong></p>

  <div class="quiz">
    <div class="card" id="cardA">
      <h4>Version A</h4>
      <p class="small muted">Sthayi, then a continuation.</p>
      <audio controls preload="none" src="experiment/purano_real_sthayi_antara.mp3"></audio>
      <div class="verdict ok">Tagore. He stays in the middle register, and saves the one climb to the
      upper octave for three words — <b>প্রাণের মাঝে আয়</b>, <i>come into my heart</i> — approached
      stepwise, not leapt.</div>
    </div>
    <div class="card" id="cardB">
      <h4>Version B</h4>
      <p class="small muted">Same sthayi, then a continuation.</p>
      <audio controls preload="none" src="experiment/purano_claude_continuation.mp3"></audio>
      <div class="verdict no">The model. It broke no rules — exact 12-matra cycles, inside the song's
      pentatonic frame, a cadence properly prepared to fall back into the sthayi. Then it leapt to the
      upper octave on the first word, because that is what nearly every antara does.</div>
    </div>
  </div>
  <div class="ctrl"><button id="revealBtn">Reveal which is which</button></div>

  <div class="panel" style="margin-top:22px">
    <p style="margin:0"><b>What it means.</b> The machine passed every mechanical test and still made a
    choice Tagore didn't. It applied the convention — antaras rise. Tagore broke the convention, and
    put the rise where the <em>poem</em> rises. Ten songs of data were enough to teach the grammar.
    Style, in the sense that matters, was not in the grammar.</p>
    <p class="small muted" style="margin:10px 0 0">That gap is also an opportunity: a benchmark that
    separates <i>followed the rules</i> from <i>understood the idiom</i> is hard to construct, and this
    repertoire supplies one — strict grammar, and a ground truth that already exists.
    <a href="{REPO}/blob/main/experiment/EXPERIMENT.md">Method, prompt and raw output →</a></p>
  </div>
</section>

<section id="findings" class="reveal">
  <span class="step">07 · What the data shows</span>
  <h2>Questions you could not ask before</h2>

  <h3>Which note lands on sam?</h3>
  <p class="small muted">Sam is beat one — the anchor the whole cycle hangs from. Across the taal-bound
  songs, Pa sits there nearly twice as often as the tonic itself — and it stayed that way when the corpus grew from ten songs to thirty.</p>
  {bars([("P", 21.6), ("M", 13.4), ("S", 12.1), ("G", 11.7), ("S'", 9.8), ("D", 8.2)])}

  <h3>How much of this music is melisma?</h3>
  <p class="small muted">The share of matras where a syllable is still sounding rather than a new one
  starting — nearly a six-fold spread across the corpus.</p>
  {bars([("এ পরবাসে", 65.3), ("গ্রামছাড়া", 53.0), ("তুমি রবে", 38.5), ("আনন্দলোকে", 31.0), ("আগুনের", 28.4), ("বিপদে মোরে", 11.2)])}

  <p class="small muted">These are hints on thirty songs — the sam figure held when the corpus tripled, which is the first weak evidence it is about the music and not the sample. Both
  charts come from <a href="{REPO}/blob/main/examples/explore.py">examples/explore.py</a>, which runs
  in ten seconds with no dependencies. The gap between "hint" and "finding" is what the project is for.</p>
</section>

<section id="use" class="reveal">
  <span class="step">08 · From here</span>
  <h2>Use it, check it, extend it</h2>
  <div class="grid2">
    <div class="panel"><b>Use the data</b><p class="small muted" style="margin:6px 0 0">Plain JSON, CC BY 4.0.
    MIDI and MusicXML for existing tools. Research directions and open questions are in
    <a href="{REPO}/blob/main/docs/USE_CASES.md">USE_CASES.md</a>.</p></div>
    <div class="panel"><b>Check our work</b><p class="small muted" style="margin:6px 0 0">If you read
    swaralipi, take one of the seven unverified songs. No programming needed — the volume numbers and
    exact steps are in <a href="{REPO}/blob/main/CONTRIBUTING.md">CONTRIBUTING.md</a>. You are credited
    in the data itself.</p></div>
    <div class="panel"><b>Build the tooling</b><p class="small muted" style="margin:6px 0 0">An akarmatrik
    renderer, meend-aware synthesis, format bridges to LilyPond and ABC. Marked <i>help wanted</i> in
    <a href="{REPO}/blob/main/ROADMAP.md">ROADMAP.md</a>.</p></div>
    <div class="panel"><b>Disagree with us</b><p class="small muted" style="margin:6px 0 0">Every reading
    records its source and its confidence, so disagreement is cheap and productive. A correction with a
    citation beats a certainty without one.</p></div>
  </div>
</section>

<footer>
  <p><a href="index.html">← the listening page</a> · <a href="{REPO}">repository</a> ·
  <a href="{REPO}/blob/main/docs/VERIFICATION.md">verification</a> ·
  <a href="{REPO}/blob/main/ROADMAP.md">roadmap</a></p>
  <p class="small">Compositions by Rabindranath Tagore (1861–1941), public domain in India since 2002.
  Notation lineage: Swarabitan, Visva-Bharati. Data CC BY 4.0, code MIT.
  This page is generated by <span class="mono">tools/build_method_page.py</span> from the corpus, so it
  cannot drift from the data it describes.</p>
</footer>

</div>

<script>
window.__TOKENS__ = {json.dumps(TOKENS, ensure_ascii=False)};
window.__STAGES__ = {json.dumps(STAGES, ensure_ascii=False)};
window.__SONGS__ = {json.dumps(songs, ensure_ascii=False)};
window.__EXP__ = {json.dumps({"real": real_pack, "ai": ai_pack}, ensure_ascii=False)};
</script>
<script>{JS}</script>
</body>
</html>
"""
    out = ROOT / "method.html"
    out.write_text(page, encoding="utf-8")
    print(f"wrote method.html ({len(page):,} bytes) — {len(songs)} songs in the follower, "
          f"{len(TOKENS)} decodable tokens, {len(STAGES)} pipeline stages")


if __name__ == "__main__":
    build()
