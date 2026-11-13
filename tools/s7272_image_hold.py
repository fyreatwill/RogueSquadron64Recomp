#!/usr/bin/env python3
"""s7272 G5c: image holds per same-run tog3 phase in a tools/g5b_capture .raw. A hold = time from one image change to the next
(covers byte-identical repeated frames AND idle gaps, since g5b_capture drops SCK idle frames). Phase = (mach/24e6)%3 of the
frame that starts the hold. Holds overlapping a control window (file of mach-tick 'start end' lines, the SIGSTOP positive
control) are reported apart. usage: s7272_image_hold.py RAW [min_ms=250] [ctl_file] [labels=off,stack,R88only]"""
import struct, sys, hashlib
raw = sys.argv[1]; mn = float(sys.argv[2]) if len(sys.argv) > 2 else 250
ctl = []
if len(sys.argv) > 3 and sys.argv[3] != '-':
    for l in open(sys.argv[3]):
        p = l.split()
        if len(p) >= 2: ctl.append((int(p[0]), int(p[1])))
lab = (sys.argv[4] if len(sys.argv) > 4 else 'off,stack,R88only').split(',')
f = open(raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); fs = w * h * 3; f.seek(0)
chg = []; prev = None; n = 0
while True:
    hd = f.read(16); b = f.read(fs)
    if len(hd) < 16 or len(b) < fs: break
    t = struct.unpack('<Q', hd[:8])[0]; d = hashlib.blake2b(b, digest_size=16).digest(); n += 1
    if d != prev: chg.append(t); prev = d
span = {0: 0.0, 1: 0.0, 2: 0.0}; holds = {0: [], 1: [], 2: []}; cl = []
for a, b in zip(chg, chg[1:]):
    ms = (b - a) / 24e3; ph = (a // 24000000) % 3; span[ph] += ms / 1e3
    if ms < mn: continue
    if any(a <= ce + 24000000 and b >= cs for cs, ce in ctl): cl.append((ms, (a - t0) / 24e6, ph)); continue
    holds[ph].append((ms, (a - t0) / 24e6))
print(f"frames {n} changes {len(chg)} span {(chg[-1]-chg[0])/24e6:.1f}s {w}x{h} changes/s {len(chg)/max(1e-9,(chg[-1]-chg[0])/24e6):.1f}")
print(f"control windows {len(ctl)} caught {len(cl)}: " + ' '.join(f"+{t:.2f}s {ms:.0f}ms ph{p}" for ms, t, p in cl))
for p in range(3):
    hs = holds[p]
    print(f"ph{p} {lab[p]:8s} {span[p]:6.1f}s holds>={mn:.0f}ms {len(hs)} max {max([x[0] for x in hs] or [0]):.0f} :: " + ' '.join(f"+{t:.1f}s/{ms:.0f}" for ms, t in hs[:12]))
