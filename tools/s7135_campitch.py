#!/usr/bin/env python3
"""s7135: per-swap camera forward vector + pitch from a ROGUESQ_G5B_FRAME capture (RAM snapshots).
The horizon clear builder 0x8005B51C skips every clear rect when sqrt(f.x^2 + f.z^2) < 0.5 (rodata 0x8003AE34, branch at
0x8005B5F0), where f = 3rd rotation column of the matrix at *(0x80138D1C) + 0x28 (0x80059D18 copies M+0x8/+0x14/+0x20).
Also prints the right/up columns, so roll is recoverable.
usage: s7135_campitch.py cap first last"""
import struct, sys, math
cap, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
f = open(cap, 'rb'); s = None; done = set()
def F(r, va): return struct.unpack('<f', r[(va & 0xFFFFFF):(va & 0xFFFFFF) + 4])[0]
def W(r, va): return struct.unpack('<I', r[(va & 0xFFFFFF):(va & 0xFFFFFF) + 4])[0]
while True:
    t = f.read(4)
    if len(t) < 4: break
    t = struct.unpack('<I', t)[0]
    if t == 0x50415753:
        m, s = struct.unpack('<QI', f.read(12))
        if s > b: break
    elif t == 0x204D4152:
        if s is not None and a <= s <= b and s not in done:
            r = f.read(0x1000000); done.add(s); P = W(r, 0x80138D1C); M = P + 0x28
            R = [F(r, M + 4 * i) for i in range(12)]
            fx, fy, fz = R[2], R[5], R[8]; h = math.hypot(fx, fz)
            ux, uy, uz = R[1], R[4], R[7]
            pitch = math.degrees(math.atan2(fy, h))
            print('%d P=%08X fwd=(%.3f,%.3f,%.3f) horiz=%.3f pitch=%.1f up=(%.3f,%.3f,%.3f) %s' % (s, P, fx, fy, fz, h, pitch, ux, uy, uz, 'SKIP' if h < 0.5 else ''))
        else: f.seek(0x1000000, 1)
    elif t == 0x20474E52:
        lo, n = struct.unpack('<II', f.read(8)); f.seek(n, 1)
    else: print('bad tag', hex(t)); break
