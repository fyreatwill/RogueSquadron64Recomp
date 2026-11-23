#!/usr/bin/env python3
"""s7861: synthetic-score test for tools/s7856_det_verdict.py fork= classification (audio-clock vs unclassified)."""
import os, subprocess, sys, tempfile
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7856_det_verdict.py')
CTRL = "=== p2\ncrashlines 0\nfirst seed-differing tick: 0 | first call-sequence-differing tick: 0\n" \
       "ticks with a full 460-w record on both sides 9\nfirst nonpose diff tick (3, [59])\n" \
       "=== control (p1 word 50 flipped at tick 100)\nfirst nonpose diff tick (100, [50])\n"
def p1(fork, rch, pch):
    return ("=== p1\ncrashlines 0\nretail ticks 2000 (x)\nfirst seed-differing tick: %s | first call-sequence-differing tick: %s\n"
            "ticks retail 2000 port 2000 compared 2000; differing ticks 5 in 1 window(s)\n"
            "== retail: ticks 2000  handle changes %s\n== port: ticks 2000  handle changes %s\n"
            "ticks with a full 460-w record on both sides 1999\nfirst nonpose diff tick (%s, [7])\n" % (fork, fork, rch, pch, fork))
CASES = [  # (fork tick, retail changes, port changes, expected fork= prefix, exit)
    (1124, 't1:00000000 t956:00000003 t1124:00000002', 't1:00000000 t956:00000003 t1123:00000002', 'fork=audio-clock(song 00000002 retail t1124 port t1123)', 1),
    (1413, 't1:00000000 t1396:00000000', 't1:00000000 t1395:00000000', 'fork=audio-clock', 1),   # 17-tick lag (0x31=14)
    (1500, 't1:00000000 t1396:00000000', 't1:00000000 t1395:00000000', 'fork=unclassified', 1),  # beyond LAG
    (395, 't1:00000000', 't1:00000000', 'fork=unclassified', 1),                                # no differing switch (v16b)
    (900, 't1:00000000 t956:00000003', 't1:00000000 t956:00000003', 'fork=unclassified', 1),     # fork before any split
]
bad = 0
with tempfile.TemporaryDirectory() as d:
    for i, (f, r, p, want, rc) in enumerate(CASES):
        fn = os.path.join(d, 's%d.txt' % i); open(fn, 'w').write(p1(f, r, p) + CTRL)
        cp = subprocess.run([sys.executable, T, fn, '--tag', 'c%d' % i], capture_output=True, text=True)
        ok = cp.returncode == rc and want in cp.stdout
        bad += not ok; print('PASS' if ok else 'FAIL', i, want, '|', cp.stdout.strip()[-90:])
    fn = os.path.join(d, 'x.txt'); open(fn, 'w').write(p1('None', 't1:0', 't1:0').replace('in 1 window', 'in 0 window')
                                                        .replace('first nonpose diff tick (None, [7])', 'first nonpose diff tick None') + CTRL)
    cp = subprocess.run([sys.executable, T, fn], capture_output=True, text=True)
    ok = cp.returncode == 0 and 'H-exact' in cp.stdout and 'fork=' not in cp.stdout
    bad += not ok; print('PASS' if ok else 'FAIL', 'exact line has no fork=', '|', cp.stdout.strip()[-60:])
print('FAILURES', bad); sys.exit(1 if bad else 0)
