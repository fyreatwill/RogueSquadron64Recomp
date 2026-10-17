#!/usr/bin/env python3
"""Per-VI-width M4 table from a cxd4 retail run (s5354).

usage: analyze_m4_pc_phase.py DIR   (DIR holds oracle.log, rsp.dump, mid.dump)

Phase join: the Nth RSD1 graphics task (type 1) is the Nth `[rdp] sync=` line
of oracle.log (counts must be equal), which carries vi_width. Reports, per
width, tasks with mid samples / with a -32768 lane, per-PC sample counts, and
task-end -32768 counts. Mid dump should be filtered by RS64_RSP_MID_PCS.
"""
import collections
import re
import struct
import sys

d = sys.argv[1]
syn = []
for l in open(f"{d}/oracle.log", errors="replace"):
    m = re.match(r"\[rdp\] sync=(\d+) vi_origin=0x([0-9a-f]+) vi_width=(\d+)", l)
    if m:
        syn.append((int(m[2], 16), int(m[3])))
raw = open(f"{d}/rsp.dump", "rb").read()
S = 4160
gfx, endv = [], {}
for o in range(0, len(raw), S):
    _, _, ser, ty = struct.unpack_from("<4s3I", raw, o)
    if ty == 1:
        gfx.append(ser)
        endv[ser] = struct.unpack_from("<24h", raw, o + 16)
if len(gfx) != len(syn):
    raise SystemExit(f"join control failed: {len(gfx)} gfx tasks vs {len(syn)} syncs")
phase = {ser: syn[i] for i, ser in enumerate(gfx)}
seen = collections.defaultdict(set)
seen8 = collections.defaultdict(set)
pcc = collections.defaultdict(collections.Counter)
pc8 = collections.defaultdict(collections.Counter)
with open(f"{d}/mid.dump", "rb") as f:
    while True:
        r = f.read(72)
        if len(r) < 72:
            break
        _, _, ser, ty, pc, _ = struct.unpack("<4s5I", r[:24])
        if ty != 1 or ser not in phase:
            continue
        w = phase[ser][1]
        pcc[w][pc] += 1
        seen[w].add(ser)
        if -32768 in struct.unpack("<24h", r[24:]):
            pc8[w][pc] += 1
            seen8[w].add(ser)
tasks = collections.Counter(p[1] for p in phase.values())
for w in sorted(pcc):
    print(f"width {w}: tasks={tasks[w]} with_samples={len(seen[w])} "
          f"with_-32768={len(seen8[w])} samples={dict(pcc[w])} -32768_samples={dict(pc8[w])}")
e8 = collections.Counter((phase[s][1], -32768 in v) for s, v in endv.items())
print("task-end -32768 by (width, present):", dict(e8))
