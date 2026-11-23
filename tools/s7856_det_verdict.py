#!/usr/bin/env python3
"""s7856: one-line verdict from a tools/s7849_det_pair.sh score.txt.

usage: python3 tools/s7856_det_verdict.py OUTDIR/score.txt [--tag 0x31=12]

Rules (the s7847-s7855 hand scoring, made mechanical):
  NO-VERDICT  p1/p2/control section missing, crashlines > 0, tick-rec has 0 full-record ticks,
              control did not report its flip tick, or p2 (unpinned) did NOT fork (positive control failed).
  H-exact     p1: seed tick None, call tick None, 0 fork windows, tick-rec first nonpose diff tick None.
  FORK        anything else; prints the first seed/call/nonpose/timing tick so the next step can pick
              H-audio-clock / H-pin-gap / H-new-fork by hand.
  residual=   (s7857) on every judged line: 'none', or 'timing-class' when p1 still shows a TIMING-word
              (s7849_rec_align TIMING = 3D-sound node flags w115/116/135/149) or rumble pulse-order difference.
              Those are sub-VI audio/dump phase (s7851/s7852), so they do NOT demote H-exact; listed so the
              ledger records them instead of reading the line as bit-identical.
  fork=       (s7861) on FORK lines: 'audio-clock(song H retail tR port tP)' when p1's first seed/call fork tick lies
              within [-1, +LAG=32] ticks of the first song-handle change (g3_song_windows 'handle changes') that retail and port
              make on different ticks with the same handle (0x31=14 rand forks 17 ticks after its t1395/t1396 switch): the s6806 audio-clocked split (0x31=8, 14, bonus 17).
              Otherwise 'unclassified' (pick H-pin-gap / H-new-fork by hand).
Exit 0 = H-exact, 1 = FORK, 2 = NO-VERDICT.
"""
import re, sys


def sections(text):
    out, cur = {}, None
    for ln in text.splitlines():
        m = re.match(r'^=== (p\d+|control)', ln)
        if m:
            cur = m.group(1); out[cur] = []; continue
        if cur:
            out[cur].append(ln)
    return {k: '\n'.join(v) for k, v in out.items()}


def grab(pat, s, default=None):
    m = re.search(pat, s, re.M)
    return m.group(1) if m else default


def facts(s):
    return {
        'crash': int(grab(r'^crashlines (\d+)', s, '-1')),
        'seed': grab(r'first seed-differing tick: (\S+)', s),
        'call': grab(r'first call-sequence-differing tick: (\S+)', s),
        'windows': grab(r'differing ticks \d+ in (\d+) window', s),
        'ticks': grab(r'^retail ticks (\d+)', s),
        'full': grab(r'ticks with a full 460-w record on both sides (\d+)', s),
        'nonpose': grab(r'^first nonpose diff tick (.+)$', s),
        'timing': grab(r'first TIMING-word diff tick (.+)$', s),
        'rumble': grab(r'first differing event (\S+)', s),
    }


def song_changes(s, side):
    m = re.search(r'^== ' + side + r': ticks \d+\s+handle changes (.*)$', s, re.M)
    return [(int(t), h) for t, h in re.findall(r't(\d+):([0-9a-fA-F]+)', m.group(1))] if m else None


LAG = 32


def fork_class(s, fork):
    r, p = song_changes(s, 'retail'), song_changes(s, 'port')
    if fork is None or not r or not p:
        return 'unclassified'
    for (tr, hr), (tp, hp) in zip(r, p):
        if hr != hp:
            return 'unclassified'
        if tr != tp:
            return (f'audio-clock(song {hr} retail t{tr} port t{tp})'
                    if min(tr, tp) - 1 <= fork <= max(tr, tp) + LAG else 'unclassified')
    return 'unclassified'


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return 2
    tag = a[a.index('--tag') + 1] if '--tag' in a else a[0]
    sec = sections(open(a[0], errors='replace').read())
    why = []
    for k in ('p1', 'p2', 'control'):
        if k not in sec:
            why.append(f'missing {k}')
    if why:
        print(f'{tag} NO-VERDICT ' + '; '.join(why)); return 2
    p1, p2, c = facts(sec['p1']), facts(sec['p2']), facts(sec['control'])
    if p1['crash'] != 0 or p2['crash'] != 0:
        why.append(f"crashlines p1={p1['crash']} p2={p2['crash']}")
    if not p1['full'] or p1['full'] == '0':
        why.append('p1 tick-rec has 0 full-record ticks')
    if not c['nonpose'] or c['nonpose'] == 'None':
        why.append('control flip not reported')
    p2_forked = (p2['seed'] not in (None, 'None')) or (p2['windows'] not in (None, '0')) or \
                (p2['nonpose'] not in (None, 'None'))
    if not p2_forked:
        why.append('p2 control did not fork')
    if why:
        print(f'{tag} NO-VERDICT ' + '; '.join(why)); return 2
    detail = (f"ticks={p1['ticks']} full_rec={p1['full']} p1 seed={p1['seed']} call={p1['call']} "
              f"windows={p1['windows']} nonpose={p1['nonpose']} timing={p1['timing']} rumble={p1['rumble']} "
              f"| p2 forked (seed={p2['seed']} nonpose={p2['nonpose']}) | control {c['nonpose']}")
    res = [k for k in ('timing', 'rumble') if p1[k] not in (None, 'None')]
    detail += f" | residual={'timing-class(' + ','.join(res) + ')' if res else 'none'}"
    exact = p1['seed'] == 'None' and p1['call'] == 'None' and p1['windows'] == '0' and p1['nonpose'] == 'None'
    if not exact:
        ft = [int(x) for x in (p1['seed'], p1['call']) if x not in (None, 'None')]
        detail += f" | fork={fork_class(sec['p1'], min(ft) if ft else None)}"
    print(f"{tag} {'H-exact' if exact else 'FORK'} {detail}")
    return 0 if exact else 1


if __name__ == '__main__':
    sys.exit(main())
