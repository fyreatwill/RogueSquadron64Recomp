#!/usr/bin/env python3
"""G3c turn-shake analysis. Input: log with [g3c] lines (ROGUESQ_G3C_LOG=1).
Series = camera yaw atan2(m[0],m[2]) of cam matrix floats, taken only on VIs where the camera matrix changed
(a new game frame). Reports: game-frame spacing in VIs, second difference of yaw per real second^2, and the
fraction of sign-alternating consecutive second differences (shake signature; ~0.5 = noise, >0.7 = jitter).
Also the same for craft pos x/z speed and for camera-vs-craft relative yaw if craft fwd guess (pl[4],pl[6]) is sane.
Usage: g3c_jerk.py LOG [--synthetic]"""
import re, sys, math, statistics as st

def parse(path):
    rows = []
    for ln in open(path, errors='replace'):
        m = re.match(r'\[g3c\] vi=(\d+) t=([\d.]+) tasks=(\d+) cam=(\S+) pl=(\S+)', ln)
        if m:
            rows.append((int(m[1]), float(m[2]), int(m[3]),
                         [float(x) for x in m[4].split(',')], [float(x) for x in m[5].split(',')]))
    return rows

def analyse(rows, name):
    frames, prev = [], None
    for vi, t, tk, cam, pl in rows:
        if any(not math.isfinite(x) for x in cam): continue
        if prev is None or cam != prev:
            frames.append((vi, t, cam, pl)); prev = cam
    print(f"== {name}: {len(rows)} VI rows, {len(frames)} distinct-camera frames")
    if len(frames) < 10: print("too few frames"); return
    gaps = [b[0] - a[0] for a, b in zip(frames, frames[1:])]
    print("frame spacing in VIs: mean %.2f, histogram %s" % (st.mean(gaps), {g: gaps.count(g) for g in sorted(set(gaps)) if gaps.count(g) > 2}))
    yaw = []
    for vi, t, cam, pl in frames:
        y = math.atan2(cam[0], cam[2]); yaw.append(y)
    # unwrap
    for i in range(1, len(yaw)):
        while yaw[i] - yaw[i-1] > math.pi: yaw[i] -= 2*math.pi
        while yaw[i] - yaw[i-1] < -math.pi: yaw[i] += 2*math.pi
    ts = [f[1] for f in frames]
    vel = [(yaw[i+1]-yaw[i])/(ts[i+1]-ts[i]) for i in range(len(yaw)-1) if ts[i+1] > ts[i]]
    acc = [vel[i+1]-vel[i] for i in range(len(vel)-1)]
    turning = [i for i in range(len(vel)-1) if abs(vel[i]) > 0.05]  # rad/s
    print("turning frames (|yawrate|>0.05 rad/s): %d" % len(turning))
    if len(turning) < 10: print("no steady turn present - arm void"); return
    a = [acc[i] for i in turning if i < len(acc)]
    alt = sum(1 for x, y in zip(a, a[1:]) if x*y < 0) / max(1, len(a)-1)
    print("yaw accel rms %.3f rad/s^2, sign-alternation fraction %.3f (random ~0.5; shake > 0.7)" % (math.sqrt(sum(x*x for x in a)/len(a)), alt))
    # relative camera vs craft heading
    rel = []
    for vi, t, cam, pl in frames:
        cy = math.atan2(cam[0], cam[2]); py = math.atan2(pl[4], pl[6]); d = cy - py
        rel.append(math.atan2(math.sin(d), math.cos(d)))
    print("camera-minus-craft heading: mean %.3f, sd %.4f rad (craft fwd guess = pl[4],pl[6])" % (st.mean(rel), st.pstdev(rel)))

if __name__ == '__main__':
    if '--synthetic' in sys.argv:  # positive control: alternating jitter must score ~1.0, smooth turn ~0
        for jit in (0.0, 0.02):
            rows = []
            for i in range(300):
                y = 0.5*i/30 + (jit if i % 2 else 0)
                rows.append((i, i/60, i, [math.sin(y), 0, math.cos(y)] + [0]*13, [0]*12))
            analyse(rows, "synthetic jitter=%g" % jit)
    else:
        analyse(parse(sys.argv[1]), sys.argv[1])
