#!/usr/bin/env python3
"""s6902 G5b: split [g1b] seconds of a run.log by a toggled arm, in stream order. A flip line ([fwdtog] on=N, or [g1e-fast] on=N) sets the arm; any
[g1b] second that had a flip inside it is dropped. Reports tasks/s (game frames) and sd_wall per arm for seconds with t >= tmin, plus a paired
difference over adjacent on/off blocks, which cancels slow drift in scene load.  Usage: g5b_fwdtog_rate.py run.log [tmin=60] [flip-regex]"""
import re, sys, statistics as st
log = sys.argv[1]; tmin = int(sys.argv[2]) if len(sys.argv) > 2 else 60
FL = re.compile(sys.argv[3] if len(sys.argv) > 3 else r"^\[(?:fwdtog|g1e-fast)\] on=(\d)")
G = re.compile(r"^\[g1b\] t=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/")
arm = None; dirty = True; blocks = []; cur = None; flips = 0
for ln in open(log, errors="replace"):
    m = FL.match(ln)
    if m: arm = int(m.group(1)); dirty = True; cur = None; flips += 1; continue
    m = G.match(ln)
    if not m: continue
    t, vi, tk, sd = int(m[1]), int(m[2]), int(m[3]), float(m[4])
    if dirty: dirty = False; continue
    if arm is None or t < tmin or vi < 50: continue
    if cur is None: cur = [arm, []]; blocks.append(cur)
    cur[1].append((tk, sd))
print(f"flips {flips} blocks {len(blocks)}")
def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
for a in (0, 1):
    s = [x for b in blocks if b[0] == a for x in b[1]]
    if not s: print(f"arm {a}: none"); continue
    tk = [x[0] for x in s]; sd = [x[1] for x in s]
    print(f"arm {a}: secs {len(s)} tasks/s mean {st.mean(tk):.2f} p10 {q(tk,.1)} p50 {q(tk,.5)} under50 {sum(x<50 for x in tk)} sd_wall p50 {q(sd,.5):.2f} p90 {q(sd,.9):.2f}")
d = [st.mean(x[0] for x in b[1]) - st.mean(x[0] for x in c[1]) if b[0] == 1 else st.mean(x[0] for x in c[1]) - st.mean(x[0] for x in b[1])
     for b, c in zip(blocks, blocks[1:]) if b[0] != c[0] and b[1] and c[1]]
if len(d) > 1: print(f"paired on-off tasks/s: n {len(d)} mean {st.mean(d):+.2f} SE {st.stdev(d)/len(d)**.5:.2f} median {st.median(d):+.2f}")
