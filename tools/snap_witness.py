#!/usr/bin/env python3
"""Offline analysis of ROGUESQ_RDRAM_SNAP_DIR snapshots (s5069_mission_snap.sh).
Usage: snap_witness.py DIR [keyname ...]   (default keyW)
Witness = word equal across ctl1..ctl3 but different in a key snapshot.
Positive control = words that differ between ctl1 and ctl2 (free-running state)."""
import struct
import sys

d = sys.argv[1]
keys = sys.argv[2:] or ["keyW"]


def ld(n):
    b = open(f"{d}/{n}.bin", "rb").read()
    return struct.unpack(f">{len(b)//4}I", b[: len(b) // 4 * 4])


c = [ld(f"ctl{i}") for i in (1, 2, 3)]
for k in keys:
    kk = ld(k)
    n = min(len(kk), *map(len, c))
    c1, c2, c3 = c[0], c[1], c[2]
    d12 = d23 = stable = 0
    wit = []
    for i in range(n):
        if c1[i] != c2[i]:
            d12 += 1
        if c2[i] != c3[i]:
            d23 += 1
        if c1[i] == c2[i] == c3[i]:
            stable += 1
            if kk[i] != c1[i]:
                wit.append(i)
    print(f"{k}: words={n} ctl12_differ={d12} ctl23_differ={d23} stable={stable} witnesses={len(wit)}")
    for i in wit[:60]:
        print(f"  0x{i*4:06X} ctl=0x{c1[i]:08X} {k}=0x{kk[i]:08X}")
