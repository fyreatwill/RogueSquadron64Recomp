#!/usr/bin/env python3
"""s7134: unpainted (hole) px per swap from a frame_replay16 log, split by whether the swap emits a clear FillRect (s7133_rects.py file).
usage: s7134_score.py name replay.log rects [name replay.log rects ...]"""
import sys
a = sys.argv[1:]
for i in range(0, len(a), 3):
    nm, lg, rf = a[i:i + 3]; F = {}; R = {}
    for l in open(lg):
        w = l.split()
        if w and w[0] == 'swap': F[int(w[1])] = int(w[11]) - int(w[9])
    for l in open(rf):
        w = l.split(); R[int(w[0])] = len(w) > 1 and w[1] != 'absent'
    c = [h for s, h in F.items() if R.get(s)]; nc = [h for s, h in F.items() if not R.get(s)]
    print('%s swaps %d | clear n %d >3000 %d max %d | noclear n %d >3000 %d max %d' % (nm, len(F), len(c), sum(h > 3000 for h in c), max(c or [0]),
          len(nc), sum(h > 3000 for h in nc), max(nc or [0])))
    big = sorted((s, h, int(bool(R.get(s)))) for s, h in F.items() if h > 3000)
    print('   >3000 swaps (swap,px,clear):', ' '.join('%d:%d:%d' % b for b in big))
