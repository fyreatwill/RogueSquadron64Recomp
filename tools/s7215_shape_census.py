#!/usr/bin/env python3
"""s7215: offline present-shape census of one run.log (needs ROGUESQ_VI_SHAPE_LOG=1).
usage: s7215_shape_census.py <run.log> [max_lines=1000]
1. Distinct [g1d-vishape-vp] shapes (fb, viewport size, rs) with counts; the full window size is the most common viewport.
2. Every viewport >1% narrower/shorter than the window, with the scissor and the previous viewport line (to tell a new box from
   the game's own centred content: same scissor on the preceding frames = content, not a box).
3. Every [s7213-shape] correction with the distance (log lines) back to the last VI mode-switch line (osViSetMode / vi-mode-table).
   Exit 1 if a correction has no mode-switch line within max_lines (= a false fire on an ordinary frame, s7214 H-false).
s7658: a run.log filtered to the shape/mode lines keeps the original line numbers (distances are in log lines) in the form
"# s7215-numbered" then "<0-based line>\t<text>" per line; *.zst is read through zstd -dc. Standing input:
scratch/s7215/shape_lines.txt.zst (s7658 L17 21:9 long route; tools/s7215_shape_census.py --filter <run.log> <out> makes one)."""
import re, sys, collections, subprocess
KEEP = re.compile(r'\[g1d-vishape-vp\]|\[s7213-shape\]|osViSetMode|\[vi-mode-table\]')
def load(p):
    t = subprocess.run(['zstd', '-dc', p], capture_output=True, check=True).stdout.decode(errors='replace') if p.endswith('.zst') \
        else open(p, errors='replace').read()
    if not t.startswith('# s7215-numbered\n'): return t.split('\n')
    rows = [r.split('\t', 1) for r in t.split('\n')[1:] if r]
    L = [''] * (int(rows[-1][0]) + 2 if rows else 1)
    for n, x in rows: L[int(n)] = x
    return L
if len(sys.argv) > 1 and sys.argv[1] == '--filter':
    with open(sys.argv[3], 'w') as o:
        o.write('# s7215-numbered\n')
        for i, l in enumerate(load(sys.argv[2])):
            if KEEP.search(l): o.write('%d\t%s\n' % (i, l))
    sys.exit(0)
L = load(sys.argv[1]); MAXD = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
vp = re.compile(r'\[g1d-vishape-vp\] fb (\d+x\d+) vp ([\d.]+),([\d.]+) ([\d.]+)x([\d.]+) tex (\S+) rs (\S+).* sc (\S+),(\S+)')
mode = re.compile(r'osViSetMode|\[vi-mode-table\]')  # KEEP must cover this, vp and [s7213-shape]
V = [(i, vp.search(l)) for i, l in enumerate(L) if '[g1d-vishape-vp]' in l]; V = [(i, m) for i, m in V if m]
C = collections.Counter((m[1], '%.0fx%.0f' % (float(m[4]), float(m[5])), m[7]) for _, m in V)
sz = collections.Counter((round(float(m[4])), round(float(m[5]))) for _, m in V).most_common(1)[0][0]
print('window (most common viewport) %dx%d, %d viewport lines' % (sz[0], sz[1], len(V)))
for k, v in C.most_common(): print('  %6d fb %s vp %s rs %s' % (v, *k))
prev = None; nf = 0
for i, m in V:
    if float(m[4]) < 0.99 * sz[0] or float(m[5]) < 0.99 * sz[1]:
        nf += 1; print('NONFULL line %d fb %s vp %s,%s %sx%s tex %s rs %s sc %s,%s | prev sc %s' % (i, m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], prev[8] if prev else '-'))
    prev = m
print('nonfull', nf)
last = None; bad = 0; n = 0
for i, l in enumerate(L):
    if mode.search(l): last = i
    elif '[s7213-shape]' in l:
        n += 1; d = i - last if last is not None else None
        if d is None or d > MAXD: bad += 1
        print('SHAPE line %d %s | mode switch %s lines back' % (i, l.split('] ', 1)[1][:90], d))
print('shape corrections %d, without a mode switch within %d lines: %d' % (n, MAXD, bad)); sys.exit(1 if bad else 0)
