#!/usr/bin/env python3
"""s6876 G3: steady writers of the camera object 0x138458 from [watch-wr] census lines (ROGUESQ_WATCH_LOG=1). Compares the last census
line with the one DELTA lines earlier, so setup stores drop out, and prints per pc the object offsets stored and how often.
A word whose [camlog] value changes but which has no writer here is a census blind spot (host write or uninstrumented store).
Usage: g3_cam_writers.py run.log [DELTA]"""
import re, sys

lines = [l for l in open(sys.argv[1], 'rb') if l.startswith(b'[watch-wr')]
delta = int(sys.argv[2]) if len(sys.argv) > 2 else 300
def parse(l):
    d = {}
    for t in l.decode('latin1').split()[2:]:
        m = re.match(r'([0-9A-F]+)@([0-9A-F]+):(\d+)', t)
        if m and 0x138458 <= int(m.group(2), 16) < 0x1384C0:
            d[(m.group(1), int(m.group(2), 16) - 0x138458)] = int(m.group(3))
    return d
a, b = parse(lines[-1 - min(delta, len(lines) - 1)]), parse(lines[-1])
pcs = {}
for k, v in b.items():
    if v - a.get(k, 0):
        pcs.setdefault(k[0], []).append((k[1], v - a.get(k, 0)))
print('census lines', len(lines), 'delta', delta)
for pc, v in sorted(pcs.items()):
    print(pc, ' '.join('+%02X:%d' % x for x in sorted(v)))
hit = {o for v in pcs.values() for o, _ in v}
print('offsets with no steady writer:', ' '.join('+%02X' % o for o in range(0, 0x68, 4) if o not in hit))
