#!/usr/bin/env python3
"""s7103 fps60-wall-camera: does the flight camera leave applyPlayerVehicleStateUpdate with near-plane corners still inside
terrain, and does the ROGUESQ_S7103_CAMFIX re-push arm remove the near-wall episodes?
Per flight-camera tick (rx line): r = residual corner mask at exit before the fix, f = after, fx = arm on, yc = y clamp taken.
Control: rx bit 3 vs the s7102 pc probe (corner 3 from the loop-end pos) on ticks with no clamp and no fix (same ray, other call).
usage: s7103_residual.py push.txt drops.csv split.txt"""
import sys, re, ast
pf, dcsv, spl = sys.argv[1:4]
T = []; lim = 0; pc = None
for l in open(pf, errors='replace'):
    k = l[:2]
    if k not in ('ch', 'pc', 'rx'): continue
    d = dict(re.findall(r'(\w+)=(\S+)', l))
    if d.get('cam') != '80138458': continue
    try:
        if k == 'ch' and 'off' in d: lim = int(d['lim'])
        elif k == 'pc': pc = int(d['hit']) != 0
        elif k == 'rx':
            T.append(dict(m=int(d['m']), lim=lim, fx=int(d['fx']), r=int(d['r']), f=int(d['f']), np=int(d['np']), yc=int(d['yc']), pc=pc))
            pc = None
    except (ValueError, KeyError):
        pc = None
rows = [l.split(',') for l in open(dcsv)][1:]
cap0 = int(rows[0][6]) - float(rows[0][1]) * 24e6
ep = []
for l in open(spl, errors='replace'):
    g = re.match(r'lim=(\d+) span .* times (\[.*\])', l)
    if g:
        ts = ast.literal_eval(g.group(2)); ep += [cap0 + x * 24e6 for i, x in enumerate(ts) if i == 0 or x - ts[i - 1] > 1.0]
win = lambda m, e: e - 0.3 * 24e6 <= m <= e + 0.1 * 24e6
inep = lambda m: any(win(m, e) for e in ep)
c = [t for t in T if t['fx'] == 0 and t['yc'] != 1 and t['pc'] is not None]
agree = sum(((t['r'] >> 3) & 1) == t['pc'] for t in c)
print('rx ticks %d episodes %d | control bit3 vs pc: %d/%d agree, pc hits %d' % (len(T), len(ep), agree, len(c), sum(t['pc'] for t in c)))
print('set      lim fx ticks  resid%%  final%%  yc%%  fixpass>1%%  episodes ep/1000t')
for name, sel in (('episode', lambda t: inep(t['m'])), ('flight', lambda t: not inep(t['m']))):
    for L in (1, 2):
        for F in (0, 1):
            S = [t for t in T if t['lim'] == L and t['fx'] == F and sel(t)]
            if not S: continue
            n = len(S)
            ne = sum(1 for e in ep if any(win(t['m'], e) for t in S)) if name == 'episode' else 0
            NT = sum(1 for t in T if t['lim'] == L and t['fx'] == F)
            print('%-8s  %d  %d  %5d  %6.1f  %6.1f  %5.1f  %6.1f  %s' % (name, L, F, n, 100. * sum(t['r'] != 0 for t in S) / n,
                  100. * sum(t['f'] != 0 for t in S) / n, 100. * sum(t['yc'] == 1 for t in S) / n, 100. * sum(t['np'] > 1 for t in S) / n,
                  ('%d %.3f' % (ne, 1000. * ne / NT)) if name == 'episode' else ''))
print('episodes (per tick: residual mask digits, / fix on, * clamp taken; | marks the episode time)')
for e in ep:
    S = [t for t in T if win(t['m'], e)]
    if not S: continue
    s = ''
    for t in S:
        s += ('|' if t['m'] > e and '|' not in s else '') + '[' + ''.join(str(i) for i in range(4) if t['r'] >> i & 1) + ']' + ('/' if t['fx'] else '') + ('*' if t['yc'] == 1 else '')
    print('lim=%d fx=%d t=%.1f ticks %d resid %d  %s' % (S[0]['lim'], S[0]['fx'], (e - cap0) / 24e6, len(S), sum(t['r'] != 0 for t in S), s))
