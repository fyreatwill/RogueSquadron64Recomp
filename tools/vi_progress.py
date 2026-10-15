#!/usr/bin/env python3
"""Per-run VI-progress metric for mission-route soak logs.

Replaces the invalid `stalled=1` grep (that field appears at title/hangar/mission
VIs alike). Reports, per log: phase transitions (origin, time, update_screen #),
last update_screen / threadPresent ordinal, and whether the final N seconds of
the run still advanced the VI counter.
usage: vi_progress.py log [log...]
"""
import re
import sys

PH = re.compile(r'^\[phase\] vi_width=(\d+) .*origin=(0x[0-9A-Fa-f]+) at ([\d.]+)s update_screen #(\d+)')
TP = re.compile(r'^\[threadPresent #(\d+)\] viW=(\d+) origin=(0x[0-9A-Fa-f]+)')
FS = re.compile(r'^\[vi-fs-decision\] #(\d+) .*vi=(0x[0-9A-Fa-f]+)')

for path in sys.argv[1:]:
    phases, tp, fs = [], [], []
    with open(path, errors='replace') as f:
        for ln in f:
            if ln.startswith('[phase] vi_width'):
                m = PH.match(ln)
                if m:
                    phases.append(m.groups())
            elif ln.startswith('[threadPresent'):
                m = TP.match(ln)
                if m:
                    tp.append(m.groups())
            elif ln.startswith('[vi-fs-decision]'):
                m = FS.match(ln)
                if m:
                    fs.append(m.groups())
    print('==', path)
    for w, o, t, n in phases:
        print('  phase viW=%s origin=%s t=%ss us#%s' % (w, o, t, n))
    if tp:
        n0 = int(tp[0][0]); n1 = int(tp[-1][0])
        print('  threadPresent first #%d last #%d (viW=%s origin=%s); n_rows=%d' % (n0, n1, tp[-1][1], tp[-1][2], len(tp)))
        # distinct origins and the ordinal at which the last origin change happened
        last_change = 0
        for i in range(1, len(tp)):
            if tp[i][2] != tp[i-1][2]:
                last_change = i
        print('  last origin change at threadPresent #%s -> %s; rows since %d' % (tp[last_change][0], tp[last_change][2], len(tp) - last_change))
    if fs:
        print('  vi-fs-decision last #%s vi=%s' % (fs[-1][0], fs[-1][1]))
