#!/usr/bin/env python3
"""s7099 G5b/G1e: same-run split of the near-wall flicker by game rate, plus the camera-eye motion term.
Inputs: one g5b_capture raw, its g5b_drops csv, and the game log carrying ROGUESQ_G3C_LOG=1 lines (s7099 format:
"[g3c] vi= t= tasks= lim= m= eye=x,y,z ..."), run with ROGUESQ_G1E_LIMIT=1 ROGUESQ_G1E_WIN=N (lim 1 = 60 fps window, 2 = retail 30).
Per state it reports: wall-hug seconds, flicker events / episodes (same rule as tools/s7098_wall_flicker.py), game ticks (eye
changes), episodes per 1000 ticks, and eye-motion statistics over new ticks:
  alt  = fraction of consecutive second differences of the eye path with a negative dot product (oscillation: ~1.0 means the
         eye zig-zags every tick, a smooth path gives ~0.5 or less)
  skip = fraction of VIs in which tasks advanced (a new game frame) but the eye did not move (a camera update skipped)
  jerk = mean |second difference| / mean |first difference|
Control: --shift S re-labels the states with the log clock shifted by S seconds (a half-window shift must smear the split).
usage: s7099_wall_split.py raw drops.csv game.log [--shift S] [--wall 0.85]"""
import sys, struct, os, re, bisect, math
a = sys.argv[1:]; shift = 0.0; WALL = 0.85
if '--shift' in a: i = a.index('--shift'); shift = float(a[i + 1]); del a[i:i + 2]
if '--wall' in a: i = a.index('--wall'); WALL = float(a[i + 1]); del a[i:i + 2]
raw, dcsv, glog = a[:3]
rx = re.compile(r'\[g3c\] vi=(\d+) t=([\d.]+) tasks=(\d+) lim=(\d+) m=(\d+) eye=([-\d.e+naif]+),([-\d.e+naif]+),([-\d.e+naif]+)')
M, LIM, TK, EYE = [], [], [], []
for line in open(glog, errors='replace'):
    if '[g3c]' not in line: continue
    g = rx.search(line)
    if not g: continue
    M.append(int(g.group(5)) + int(shift * 24e6)); LIM.append(int(g.group(4))); TK.append(int(g.group(3)))
    EYE.append(tuple(float(g.group(k)) for k in (6, 7, 8)))
if not M: sys.exit('no s7099 [g3c] lines in ' + glog)
def state_at(T):
    k = bisect.bisect_right(M, T) - 1
    return LIM[k] if k >= 0 else -1
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
    hug[i] = d >= WALL * c
st = {}
def S(k): return st.setdefault(k, dict(hug=0.0, span=0.0, ev=[], ticks=0, vis=0, alt=[0, 0], skip=[0, 0], d1=0.0, d2=0.0, nd=0))
for i in range(n - 1):
    dt = T[i + 1] - T[i]
    if dt >= 2.4e6: continue
    s = S(state_at(T[i])); s['span'] += dt / 24e6
    if hug[i]: s['hug'] += dt / 24e6
cap_t0 = T[0]
for k, line in enumerate(open(dcsv)):
    if k == 0: continue
    p = line.split(','); x, ts, Tt = int(p[0]), float(p[1]), float(p[4])
    if Tt >= 0.12 and ts >= 5 and x > 0 and hug[x - 1]:
        S(state_at(T[x]))['ev'].append(round((T[x] - cap_t0) / 24e6, 1))
# eye motion over the capture span only (flight), per state
lo, hi = T[0], T[-1]
pts = {}  # state -> list of (vi index, eye) at new ticks
for j in range(1, len(M)):
    if not (lo <= M[j] <= hi): continue
    s = S(LIM[j]); s['vis'] += 1
    moved = EYE[j] != EYE[j - 1]
    if TK[j] != TK[j - 1]:
        s['skip'][1] += 1
        if not moved: s['skip'][0] += 1
    if moved: s['ticks'] += 1; pts.setdefault(LIM[j], []).append((j, EYE[j]))
for k, P in pts.items():
    s = S(k)
    for q in range(2, len(P)):
        (j0, e0), (j1, e1), (j2, e2) = P[q - 2], P[q - 1], P[q]
        if j2 - j0 > 8 or LIM[j0] != LIM[j2]: continue
        a1 = [e1[i] - e0[i] for i in range(3)]; a2 = [e2[i] - e1[i] for i in range(3)]
        dd = [a2[i] - a1[i] for i in range(3)]
        s['d1'] += math.sqrt(sum(v * v for v in a2)); s['d2'] += math.sqrt(sum(v * v for v in dd)); s['nd'] += 1
        if q >= 3:
            (jm, em) = P[q - 3]; a0 = [e0[i] - em[i] for i in range(3)]; dp = [a1[i] - a0[i] for i in range(3)]
            s['alt'][1] += 1
            if sum(dp[i] * dd[i] for i in range(3)) < 0: s['alt'][0] += 1
print('g3c lines %d, capture frames %d, shift %.1fs' % (len(M), n, shift))
for k in sorted(st):
    s = st[k]; ev = s['ev']; ep = sum(1 for i, t in enumerate(ev) if i == 0 or t - ev[i - 1] > 1.0)
    print('lim=%d span %.1fs hug %.1fs (%.0f%%) events %d episodes %d ep/hug-min %.3f ticks %d ticks/s %.1f ep/1000ticks %.3f alt %.3f (%d) skip %.3f (%d) jerk %.3f  times %s' % (
        k, s['span'], s['hug'], 100 * s['hug'] / s['span'] if s['span'] else 0, len(ev), ep, 60 * ep / s['hug'] if s['hug'] else 0,
        s['ticks'], s['ticks'] / s['span'] if s['span'] else 0, 1000 * ep / s['ticks'] if s['ticks'] else 0,
        s['alt'][0] / s['alt'][1] if s['alt'][1] else 0, s['alt'][1], s['skip'][0] / s['skip'][1] if s['skip'][1] else 0, s['skip'][1],
        s['d2'] / s['d1'] if s['d1'] else 0, ev[:30]))
