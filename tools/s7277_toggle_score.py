#!/usr/bin/env python3
"""s7277 G5c within-run load toggle scorer. From scratch/s7277/ring_<TAG>.txt (ROGUESQ_PRESENT_RING Q rows: wall t, fb gen)
and <TAG>.toggle (on/off times, same CLOCK_UPTIME_RAW clock), per load window: game frames/s (new fb gens/s), Q/s (presents),
max gap between new gens, gen gaps >= 250 ms (frozen image, the owner's freeze), gpu_ms / acq_ms p95. The +-3 s around each SIGSTOP
control (<TAG>.ctl, 24 MHz ticks) is cut out of its window and scored separately: the control gap must be >= 900 ms.
usage: s7277_toggle_score.py TAG [DIR=scratch/s7277]"""
import sys
T = sys.argv[1]; D = sys.argv[2] if len(sys.argv) > 2 else 'scratch/s7277'
pc = lambda v, p: sorted(v)[int(p*(len(v)-1))] if v else 0
Q = []
for l in open(f'{D}/ring_{T}.txt'):
    if not l.startswith('Q '): continue
    f = l.split(); kv = dict(x.split('=', 1) for x in f[2:] if '=' in x)
    Q.append((float(f[1]), kv.get('gen'), float(kv.get('gpu_ms', 0)), float(kv.get('acq_ms', 0))))
ev = [(l.split()[0], float(l.split()[1])) for l in open(f'{D}/{T}.toggle') if l.strip()]
try: ctl = [(int(a)/24e6, int(b)/24e6) for a, b in (l.split() for l in open(f'{D}/{T}.ctl') if l.strip())]
except OSError: ctl = []
newg = [Q[0][0]] if Q else []
for i in range(1, len(Q)):
    if Q[i][1] != Q[i-1][1]: newg.append(Q[i][0])
cut = lambda t: any(a - 3 <= t <= b + 3 for a, b in ctl)
print(f'ring rows {len(Q)} new gens {len(newg)} span {Q[-1][0]-Q[0][0]:.0f} s' if Q else 'empty ring')
print('win state  t0_s   dur | gen/s  Q/s  maxgap_ms gaps>=250 gaps>=100 | gpu95 acq95')
S = {'on': [], 'off': []}
for k in range(len(ev) - 1):
    st, a = ev[k]; b = ev[k+1][1]
    if st not in S or b - a < 5: continue
    g = [t for t in newg if a <= t < b and not cut(t)]; q = [r for r in Q if a <= r[0] < b and not cut(r[0])]
    dur = (b - a) - sum(max(0, min(b, y + 3) - max(a, x - 3)) for x, y in ctl)
    gaps = [(g[i+1] - g[i]) * 1000 for i in range(len(g) - 1) if not any(g[i] < x - 3 < g[i+1] or g[i] < y + 3 < g[i+1] for x, y in ctl)]
    row = (len(g)/dur, len(q)/dur, max(gaps or [0]), sum(x >= 250 for x in gaps), sum(x >= 100 for x in gaps), pc([r[2] for r in q], .95), pc([r[3] for r in q], .95))
    S[st].append(row)
    print(f'{k:3} {st:4} {a-Q[0][0]:6.0f} {dur:5.0f} | {row[0]:5.1f} {row[1]:5.1f} {row[2]:9.0f} {row[3]:9} {row[4]:9} | {row[5]:5.2f} {row[6]:5.2f}')
for st, v in S.items():
    if v: print(f'mean {st:4}: gen/s {sum(r[0] for r in v)/len(v):5.1f}  Q/s {sum(r[1] for r in v)/len(v):5.1f}  gaps>=250 {sum(r[3] for r in v)}  gaps>=100 {sum(r[4] for r in v)}  max {max(r[2] for r in v):.0f} ms  gpu95 {max(r[5] for r in v):.2f}')
for x, y in ctl:
    g = [t for t in newg if x - 3 <= t <= y + 3]
    m = max([(g[i+1]-g[i])*1000 for i in range(len(g)-1)] or [0]); print(f'control {x-Q[0][0]:.0f} s: max gen gap {m:.0f} ms {"CAUGHT" if m >= 900 else "MISSED"}')
