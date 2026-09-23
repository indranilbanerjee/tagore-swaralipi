#!/usr/bin/env python3
"""
parse_nltr.py — parse SNLTR Rabindra-Rachanabali swaralipi HTML grids into Swaralipi-JSON.

The SNLTR digital edition of Swarabitan serves akarmatrik notation as an HTML
table: one <td> per matra-column cell, tokens in the custom Swarabitan.ttf
font encoding. This parser decodes that token language.

Token language (decoded by cross-source triangulation, see docs/DECODING.md):
  note codes : s r g m p q n  -> S R G M P D N (shuddha)
               k -> kori (tivra) Ma       (হ্ম)
               t -> komal Ga              (জ্ঞ)
               d -> komal Dha             (দ)
               u -> komal Ni              (ণ)
               v -> komal Re              (ঋ)
  octave     : code + 'h' = udara (-1), code + 'f' = tara (+1), bare = mudara (0)
  terminator : trailing 'a' = the আ-কার that gives the system its name
  '-' prefix / bare '-a' = sustain (dash) of the previous swara
  Capitalised leading code(s) = kan (grace) note attached to the following swara
  structural : l = bar, ll/L = section bar, A = vibhag separator,
               { } ( ) = repeat / alternate spans, \\ w x [..] = page annotations
  lyric rows : Bengali syllables; ৹ = melisma continuation
"""
import json, re, sys, html
from pathlib import Path

NOTE_CODES = {'s': ('S', False, False), 'r': ('R', False, False), 'g': ('G', False, False),
              'm': ('M', False, False), 'p': ('P', False, False), 'q': ('D', False, False),
              'n': ('N', False, False), 'k': ('M', False, True),  't': ('G', True, False),
              'd': ('D', True, False),  'u': ('N', True, False),
              'v': ('R', True, False)}   # komal Re — see docs/DECODING.md

STRUCTURAL = {'l', 'll', 'L', 'A', '{', '}', '(', ')', '\\', 'w', 'x', '|'}

def parse_token_body(body):
    """Parse the body of a note token (lowercase, no trailing 'a') into swaras/sustains."""
    out = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == '-':
            out.append({'type': 'sustain'})
            i += 1
            continue
        if ch in NOTE_CODES:
            deg, komal, kori = NOTE_CODES[ch]
            saptak = 0
            if i + 1 < len(body) and body[i+1] in 'hf':
                saptak = -1 if body[i+1] == 'h' else 1
                i += 1
            sw = {'degree': deg, 'saptak': saptak}
            if komal: sw['komal'] = True
            if kori: sw['kori'] = True
            out.append({'type': 'swara', 'swara': sw})
            i += 1
            continue
        if ch == 'a':  # stray akar inside body = sustain vowel
            out.append({'type': 'sustain'})
            i += 1
            continue
        # A character we cannot read is recorded as an annotation, never guessed
        # into a pitch. Inventing a note would be silently wrong in the data; an
        # annotation is visibly incomplete, which is the honest failure mode.
        out.append({'_annotation': ch})
        i += 1
    return out

def parse_note_token(tok):
    """Full token -> dict(units=[...], kan=[...]) or structural marker."""
    raw = tok
    if tok in STRUCTURAL:
        return {'structural': tok}
    if tok == '৹':  # melisma dot in a note row = sustain
        return {'units': [{'type': 'sustain'}], 'marks': [], 'raw': raw}
    # strip braces/brackets glued to tokens
    pre_marks, post_marks = [], []
    while tok and tok[0] in '{([':
        pre_marks.append(tok[0]); tok = tok[1:]
    while tok and tok[-1] in '})]':
        post_marks.append(tok[-1]); tok = tok[:-1]
    if not tok:
        return {'structural': ''.join(pre_marks + post_marks) or None, 'marks': pre_marks + post_marks}
    # kan (grace): leading capitals (possibly with F/H octave capitals)
    kan = []
    m = re.match(r'^(-*)((?:[A-Z][fhFH]?)+)(?=[a-z-])', tok)
    if m and tok not in ('A', 'L'):
        lead_dashes, caps = m.group(1), m.group(2)
        # don't let a trailing lowercase octave letter swallow the body's first note
        # (octave letters f/h can only follow a capital)
        tok = lead_dashes + tok[len(lead_dashes) + len(caps):]
        j = 0
        while j < len(caps):
            c = caps[j].lower()
            if c in NOTE_CODES:
                deg, komal, kori = NOTE_CODES[c]
                saptak = 0
                if j + 1 < len(caps) and caps[j+1] in 'FHfh':
                    saptak = 1 if caps[j+1] in 'Ff' else -1
                    j += 1
                sw = {'degree': deg, 'saptak': saptak}
                if komal: sw['komal'] = True
                if kori: sw['kori'] = True
                kan.append(sw)
            j += 1
    uncertain = False
    # 'i'-suffix variant (rare; vowel-form uncertain) e.g. pai, -ki, -pi
    if tok.endswith('i'):
        uncertain = True
        tok = tok[:-1] + 'a' if not tok.endswith('a') else tok
    # A capital after the akar is not a kan (kans precede their swara). We do not
    # know what it marks, so it is preserved as an annotation rather than guessed.
    trailing = ''
    while tok and tok[-1].isupper():
        trailing = tok[-1] + trailing
        tok = tok[:-1]
    # trailing akar
    if tok.endswith('a'):
        tok = tok[:-1]
    parsed_units = parse_token_body(tok)
    annotations = [u['_annotation'] for u in parsed_units if '_annotation' in u]
    units = [u for u in parsed_units if '_annotation' not in u]
    if kan and units:
        # attach kan to first swara unit
        for u in units:
            if u['type'] == 'swara':
                u['kan'] = kan
                break
        else:
            units[0]['kan'] = kan
    if uncertain:
        for u in units:
            u['uncertain'] = True
    return {'units': units, 'marks': pre_marks + post_marks,
            'annotations': annotations + ([trailing] if trailing else []), 'raw': raw}

BEN_DIGITS = '০১২৩৪৫৬৭৮৯'

def is_lyric(text):
    return bool(re.search(r'[ঀ-৿৹৺]', text)) and not re.match(r'^[\s৹]*$', text)

def extract_grid(path):
    h = Path(path).read_text(encoding='utf-8', errors='replace')
    cells = re.findall(r"<td[^>]*id=\"?([\d.]+)\"?[^>]*>(.*?)</td>", h, re.S)
    grid = {}
    for cid, content in cells:
        txt = re.sub(r'<[^>]+>', '', content)
        txt = html.unescape(txt).strip()
        r, c = cid.split('.')
        grid.setdefault(int(r), {})[int(c)] = txt
    # song header: label / ':' / value in successive style3 spans
    hdr = re.findall(r"<span class='style3'>([^<]*)</span>", h)
    meta = {'name': None, 'taal': None, 'abarton': None}
    labels = {'নাম': 'name', 'তাল': 'taal', 'আবর্তন': 'abarton'}
    for i, v in enumerate(hdr):
        v = v.strip()
        if v in labels and i + 2 < len(hdr) and hdr[i+1].strip() == ':':
            meta[labels[v]] = hdr[i+2].strip()
    return grid, meta

NOTE_TOKEN_RE = re.compile(r'^-?[a-z-]*a\)?\}?$|^\{?\(?-?[A-Z]*[a-z-]*a$')

def classify_row(cols):
    vals = [v.strip() for v in cols.values() if v and v.strip() and v != '\xa0']
    if not vals:
        return 'empty'
    if any(is_lyric(v) for v in vals):
        return 'lyric'
    beatish = sum(1 for v in vals if re.match(r'^\d+f?\|?$', v) or re.match(r'^\[\w+\]$', v))
    noteish = sum(1 for v in vals for t in v.split() if NOTE_TOKEN_RE.match(t))
    if beatish >= 2 and noteish == 0:
        return 'beathead'
    return 'note'

def parse_song(path):
    grid, meta = extract_grid(path)
    rows = sorted(grid.keys())
    # pair note rows with the following lyric row
    paired = []
    i = 0
    while i < len(rows):
        r = rows[i]
        kind = classify_row(grid[r])
        if kind == 'note':
            lyr = None
            for j in rows[rows.index(r)+1: rows.index(r)+3]:
                if classify_row(grid[j]) == 'lyric':
                    lyr = grid[j]
                    break
            paired.append((grid[r], lyr))
        i += 1
    # build lines
    lines = []
    for note_cols, lyr_cols in paired:
        maxc = max(list(note_cols.keys()) + list((lyr_cols or {}).keys()))
        cells = []
        marks = []
        for c in range(0, maxc + 1):
            cellraw = (note_cols.get(c) or '').strip()
            lyr = (lyr_cols or {}).get(c, '')
            lyr = (lyr or '').strip()
            if not cellraw or cellraw == '\xa0':
                continue
            subtoks = cellraw.split()
            # a physical cell may hold several tokens (e.g. 'll  ll', 'l -a');
            # structural subtokens become marks, note subtokens share the cell
            note_subtoks = [t for t in subtoks if t not in STRUCTURAL
                            and not re.match(r'^\[.*\]$', t) and t not in ('w', 'x', '\\')]
            for t in subtoks:
                if t in ('l', 'll', 'L', '|'):
                    marks.append({'type': 'bar' if t in ('l', '|') else 'section_bar', 'cell': len(cells)})
                elif t == 'A':
                    marks.append({'type': 'vibhag', 'cell': len(cells)})
                elif t in ('{', '}', '(', ')', '[', ']'):
                    marks.append({'type': {'{': 'repeat_open', '}': 'repeat_close',
                                           '(': 'alt_open', ')': 'alt_close',
                                           '[': 'bracket_open', ']': 'bracket_close'}[t], 'cell': len(cells)})
                elif re.match(r'^\[.*\]$', t) or t in ('w', 'x', '\\'):
                    marks.append({'type': 'annotation', 'raw': t, 'cell': len(cells)})
            if not note_subtoks:
                continue
            all_units = []
            cell_marks_pre = []
            for t in note_subtoks:
                parsed = parse_note_token(t)
                if 'structural' in parsed:
                    continue
                for mk in parsed.get('marks', []):
                    marks.append({'type': {'{': 'repeat_open', '}': 'repeat_close',
                                           '(': 'alt_open', ')': 'alt_close',
                                           '[': 'bracket_open', ']': 'bracket_close'}[mk], 'cell': len(cells)})
                for ann in parsed.get('annotations', []):
                    marks.append({'type': 'annotation', 'raw': ann, 'cell': len(cells)})
                all_units.extend(parsed['units'])
            if not all_units:
                continue
            melisma = lyr in ('৹', '৹৹', '') or all(ch in '৹ ' for ch in lyr)
            cells.append({'units': all_units,
                          'lyric': None if melisma else lyr,
                          'melisma': bool(melisma and lyr)})
        if cells:
            lines.append({'cells': cells, 'marks': marks})
    return {'meta': meta, 'lines': lines}

if __name__ == '__main__':
    out = parse_song(sys.argv[1])
    print(json.dumps(out, ensure_ascii=False, indent=1))
