#!/usr/bin/env python3
"""s6749 G3: retail-vs-port timeline of one VI-width phase from g3_oracle_match.py output.
usage: g3_phase_timeline.py MATCH_TXT RETAIL_VI0 PORT_T0 [--maxd 10] [--minL 8]
  RETAIL_VI0 = oracle [vi] WIDTH switch vi of the phase, PORT_T0 = port [phase] vi_width switch seconds.
Prints per matched retail frame: retail rel s, port rel s, offset; then the linear fit port_rel = a*retail_rel + b.
Constant offset from the first lit frame = load lead-in (H-load); a != 1 = rate drift; an offset jump = a skipped segment."""
import re, sys
a = sys.argv[4:]
opt = lambda k, d: float(a[a.index(k) + 1]) if k in a else d
vi0, t0, maxd, minL = int(sys.argv[2]), float(sys.argv[3]), opt('--maxd', 10.0), opt('--minL', 8.0)
xs, ys = [], []
for m in re.finditer(r'retail vi=\s*(\d+) org=\w+ meanL=\s*([\d.]+) -> port n=\s*(\d+) d=\s*([\d.]+)', open(sys.argv[1]).read()):
    vi, L, n, d = int(m[1]), float(m[2]), int(m[3]), float(m[4])
    r = (vi - vi0) / 60.0
    if L < minL:
        print(f'{r:6.2f}  black'); continue
    if d > maxd:
        print(f'{r:6.2f}  unmatched d={d:.1f} meanL={L:.0f}'); continue
    p = n / 100.0 - t0
    xs.append(r); ys.append(p)
    print(f'{r:6.2f} -> port {p:6.2f}  offset {r - p:5.2f}  d={d:.1f}')
if len(xs) > 1:
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sl = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    print(f'fit port_rel = {sl:.4f}*retail_rel {my - sl * mx:+.2f}  ({len(xs)} frames, offset {min(x - y for x, y in zip(xs, ys)):.2f}..{max(x - y for x, y in zip(xs, ys)):.2f})')
