#!/usr/bin/env python3
"""s7844 G3 det sweep: player hull/shield damage timeline from a 460-word player-record ramdump (0x80137DB0..0x801384E0,
port run.log or retail oracle.log; parser = tools/s7834_ramdump_cmp.py rows()). Word 51 (+0xCC) = hp float (regenerates
~0.0278/tick), word 55 (+0xDC) = damage-state counter (+5 per hit). Prints each hp drop >0.5 or w55 change as
(row, hp before, hp after, w55). Use it when a det pair forks suddenly in the player rotation/hp words: a hit that one side
takes and the other does not is an enemy/projectile-side fork (outside this dump), not a player-state defect.
usage: s7844_hp_events.py LOG [LOG ...]"""
import importlib.util, pathlib, struct, sys
sp = importlib.util.spec_from_file_location('c', pathlib.Path(__file__).with_name('s7834_ramdump_cmp.py'))
c = importlib.util.module_from_spec(sp); sp.loader.exec_module(c)
F = lambda v: struct.unpack('>f', struct.pack('>I', v))[0]
for path in sys.argv[1:]:
    X = [r[1] for r in c.rows(path) if len(r[1]) == 460]; ev = []
    for i in range(1, len(X)):
        a, b = F(X[i-1][51]), F(X[i][51])
        if b < a - 0.5 or X[i][55] != X[i-1][55]: ev.append((i, round(a, 2), round(b, 2), round(F(X[i][55]), 2)))
    hits = [e for e in ev if e[1] - e[2] > 0.5]
    gaps = [hits[k+1][0] - hits[k][0] for k in range(len(hits) - 1)]
    print(path, 'rows', len(X), 'hits', hits[:6], 'gaps', gaps[:5])
