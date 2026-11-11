#!/usr/bin/env python3
"""s7108 fps60-wall-nearclip: split near-wall flicker by ROGUESQ_S7108_CAMWIDE=tog state (on in odd absolute mach seconds).
Two independent lines:
  (1) presented-window episodes: the s7099/s7098 rule (g5b_drops row T >= 0.12, t >= 5 s, previous frame wall-hugging, events
      <= 1 s apart merge into one episode), state = parity of the frame's mach second;
  (2) stream losses: tools/s7107_losscan.py rows (lost >= MIN cells), split into eye-cell near-z losses (ref painter c+0+0 and
      drop near minz < 0x0100) vs others, state from cap0 + t (losscan's own clock).
Also per state: wall-hug seconds and the [s7108] k / on lines from the game log (positive control that the arm toggled).
Control: --shift S adds S seconds before the parity test (S=0.5 must smear a real split toward equal).
usage: s7108_split.py raw drops.csv losscan.txt game.log [--shift S]"""
import sys, struct, os, re
a = sys.argv[1:]; shift = 0.0
if '--shift' in a: i = a.index('--shift'); shift = float(a[i + 1]); del a[i:i + 2]
raw, dcsv, lsc, glog = a[:4]
def st(m): return int((m + shift * 24e6) // 24e6) & 1
f = open(raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = os.path.getsize(raw) // rec
hug = bytearray(n); T = [0] * n
ys = range(40, h, 6); xs = range(0, min(370, w), 6)
for i in range(n):
    f.seek(i * rec); T[i] = struct.unpack('<Q', f.read(8))[0]; f.seek(i * rec + 16); px = f.read(w * h * 3)
    d = c = 0
    for y in ys:
        r = y * w * 3
        for x in xs:
            j = r + 3 * x; c += 1
            if px[j] * 3 + px[j + 1] * 6 + px[j + 2] < 700: d += 1
    hug[i] = d >= 0.85 * c
span = [0.0, 0.0]; hugs = [0.0, 0.0]
for i in range(n - 1):
    dt = T[i + 1] - T[i]
    if dt >= 2.4e6: continue
    s = st(T[i]); span[s] += dt / 24e6
    if hug[i]: hugs[s] += dt / 24e6
rows = [l.strip().split(',') for l in open(dcsv)][1:]
cap0 = T[0]
ev = [[], []]
for p in rows:
    x, ts, Tt = int(p[0]), float(p[1]), float(p[4])
    if Tt >= 0.12 and ts >= 5 and 0 < x < n and hug[x - 1]: ev[st(T[x])].append((T[x] - cap0) / 24e6)
evs = sorted((t, s) for s in (0, 1) for t in ev[s]); epi = [0, 0]; ept = [[], []]
for k, (t, s) in enumerate(evs):
    if k == 0 or t - evs[k - 1][0] > 1.0: epi[s] += 1; ept[s].append(round(t, 1))
# losscan: cap0 there = first drops-csv row mach - its t_s
ec = sorted((int(p[6]), float(p[1])) for p in rows); lcap0 = ec[0][0] - ec[0][1] * 24e6
rl = re.compile(r'sw\s+(\d+) t=\s*([-\d.]+) lost\s+(\d+) ref (\[.*?\]) -> .*near tris/minz ref (\d+)/([0-9A-F]+) drop (\d+)/([0-9A-F]+)')
L = [[0, 0], [0, 0]]; LT = [[], []]
for line in open(lsc):
    g = rl.search(line)
    if not g: continue
    t = float(g.group(2))
    if t < 0: continue  # flight only (capture window)
    s = st(lcap0 + t * 24e6); eye = "'c+0+0'" in g.group(4).split(',')[0] and int(g.group(8), 16) < 0x100
    L[s][0 if eye else 1] += 1
    if eye: LT[s].append(round(t, 2))
K = [[], []]
for line in open(glog, errors='replace'):
    g = re.search(r'\[s7108\] s2=\S+ cam=\S+ w=(\d+) h=(\d+) fov=(\S+) pfov=(\S+) asp=(\S+) near=(\S+) pnear=(\S+) hx=(\S+) px=(\S+) vy=(\S+) pv=(\S+) k=(\S+) on=(\d)', line)
    if g: K[int(g.group(13))].append(g.groups())
print('shift %.2fs, capture frames %d' % (shift, n))
for s in (0, 1):
    hm = hugs[s] / 60 if hugs[s] else 0
    print('camwide=%d span %.1fs hug %.1fs episodes %d (%.2f/hug-min) events %d  eye-nearz stream losses %d other %d  times %s  loss-t %s' % (
        s, span[s], hugs[s], epi[s], epi[s] / hm if hm else 0, len(ev[s]), L[s][0], L[s][1], ept[s][:20], LT[s][:20]))
    if K[s]:
        g = K[s][len(K[s]) // 2]
        print('   [s7108] lines %d, mid: w=%s h=%s fov=%s pfov=%s asp=%s near=%s pnear=%s hx=%s px=%s vy=%s pv=%s k=%s' % ((len(K[s]),) + g[:12]))
