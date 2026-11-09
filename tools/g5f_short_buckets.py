#!/usr/bin/env python3
"""s7002 G5f: bucket g5f_lines output (lines.txt) by run length and toggle block, with event dedupe and a
per-1000-frame-window split so one scene cannot carry the asymmetry.
usage: g5f_short_buckets.py <lines.txt> [skip_idx=2000]
block 0 = even 24 MHz seconds (the env's normal value), block 1 = odd seconds (=tog / W_SHEET_ALT arm)."""
import sys, collections
rows = [l.split() for l in open(sys.argv[1]) if l[0].isdigit()]
rows = [r for r in rows if r[-1] == '0']  # drop injected control lines
skip = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
B = [('20-39', 20, 40), ('40-59', 40, 60), ('60-99', 60, 100), ('100+', 100, 1 << 30)]
cnt, ev, last, win = collections.Counter(), collections.Counter(), {}, collections.Counter()
for r in rows:
    i, run, blk = int(r[0]), int(r[6]), int(r[11])
    if i < skip: continue
    k = next(n for n, lo, hi in B if lo <= run < hi)
    cnt[(blk, k)] += 1
    if last.get((blk, k), -9) < i - 2: ev[(blk, k)] += 1
    last[(blk, k)] = i
    if run < 60: win[(i // 1000, blk)] += 1
print('bucket   lines b0 b1   events b0 b1')
for n, _, _ in B: print(f'{n:7s}  {cnt[(0,n)]:5d} {cnt[(1,n)]:5d}   {ev[(0,n)]:5d} {ev[(1,n)]:5d}')
ws = sorted({w for w, _ in win})
print('short (<60) per 1000-frame window b0/b1:', ' '.join(f'{win[(w,0)]}/{win[(w,1)]}' for w in ws))
print('windows with b1 > b0:', sum(win[(w, 1)] > win[(w, 0)] for w in ws), 'of', len(ws))
