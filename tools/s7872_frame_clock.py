#!/usr/bin/env python3
"""s7872 G3: per-game-frame clock table, retail vs port, for the pre-flight half-frame island (s7870/s7871 island A).

Retail side: an rs64_oracle log run with
  RS64_XTRACE_MEM=8000BBE8:0:8011A904:1,8000BBE8:0:80128ED8:1  --exec-trace-also 0x8000BBE8  --exec-trace-also 0x8000BE28
(0x8000BBE8 = computeFrameDeltaTime after the dt store: m=8011a904 is dt, m=80128ed8 the VI-thread stamp; 0x8000BE28 =
timeSnapshotFiller holding v0 = el = stamp - prev, the value ROGUESQ_RETAIL_SNAP pins to 811160).
Port side: a run.log with ROGUESQ_S7835_DT=1 (`[dt7835] vi n=` per VI wake, `[dt7835] fr n= dt=` per game frame).

Prints, per side: dt run-lengths in VI units, every load stall (stamp/VI gap > 3.5 VI) with the dt of the frame after it,
and (retail) the run-lengths of el classes (0 / 1VI / other). Rows with --align: retail frame = port frame - OFF.
Control (iron rule 1): retail must show the steady 2-VI dt and both el classes (0 and 1VI) somewhere, port must show a
2-VI steady state; rc 3 otherwise (an instrument that saw nothing cannot report "equal").
usage: s7872_frame_clock.py RETAIL_ORACLE.log PORT_RUN.log [--off N]
"""
import re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import zopen

RVI = 811092      # retail count units per VI (CPO1 oracle; 0x18c0a8 per 2-VI frame)
PVI = 781250      # port VI_STAMP units per VI (s7837)


def runs(seq):
    out, p, s = [], None, 0
    for i, c in enumerate(seq):
        if c != p:
            if p is not None: out.append((s, i - s, p))
            p, s = c, i
    if p is not None: out.append((s, len(seq) - s, p))
    return out


def retail(path):
    dt, st, el = [], [], {}
    with zopen(path) as f:
        for l in f:
            if isinstance(l, bytes): l = l.decode('latin1')
            if not l.startswith('[xtrace]'): continue
            if 'pc=8000bbe8' in l:
                m = dict(re.findall(r'm=([0-9a-f]+):([0-9a-f]+)', l))
                dt.append(int(m['8011a904'], 16)); st.append(int(m['80128ed8'], 16))
            elif 'pc=8000be28' in l:
                v = int(re.search(r'v0=([0-9a-f]+)', l)[1], 16); v = v - 2**32 if v >= 2**31 else v
                el.setdefault(len(dt) - 1, []).append(v)
    return dt, st, el


def port(path):
    vi, rows = 0, []
    with zopen(path) as f:
        for l in f:
            if isinstance(l, bytes): l = l.decode('latin1')
            if not l.startswith('[dt7835]'): continue
            m = re.match(r'\[dt7835\] vi n=(\d+)', l)
            if m: vi = int(m[1]); continue
            m = re.match(r'\[dt7835\] fr n=(\d+) dt=(\d+)', l)
            if m: rows.append((int(m[2]), vi))
    return rows


def main():
    a = sys.argv[1:]
    off = None
    if '--off' in a:
        i = a.index('--off'); off = int(a[i + 1]); del a[i:i + 2]
    if len(a) != 2: print(__doc__); return 2
    dt, st, el = retail(a[0]); pr = port(a[1])
    rq = [round(d / RVI, 2) for d in dt]; pq = [round(d / PVI, 2) for d, _ in pr]
    print(f'retail frames {len(dt)}  dt runs (start,len,VI): {runs(rq)}')
    print(f'port   frames {len(pr)}  dt runs (start,len,VI): {runs(pq)}')
    rs = [(i, ((st[i] - st[i - 1]) & 0xffffffff) / RVI, rq[i]) for i in range(1, len(st))
          if ((st[i] - st[i - 1]) & 0xffffffff) / RVI > 3.5]
    ps = [(i, pr[i][1] - pr[i - 1][1], pq[i]) for i in range(1, len(pr)) if pr[i][1] - pr[i - 1][1] > 3]
    print('retail stalls (frame, gapVI, dt-after VI):', [(i, round(g, 1), d) for i, g, d in rs])
    print('port   stalls (frame, gapVI, dt-after VI):', ps)

    def cls(v):
        return '0' if v == 0 else ('1VI' if abs(v - RVI) < 3000 else f'x{v}')
    ec = [cls(el[f][0]) if f in el else 'none' for f in range(len(dt))]
    print('retail el runs (start,len,class) len>2 or non-none:', [r for r in runs(ec) if r[1] > 2 or r[2] != 'none'])
    if off is not None:
        print(f'aligned stalls (retail = port - {off}):')
        rset = {i: (g, d) for i, g, d in rs}
        for i, g, d in ps:
            r = rset.get(i - off)
            print(f'  port fr {i} gap {g} dt {d} | retail fr {i - off}: '
                  + (f'gap {r[0]:.1f} dt {r[1]} el {el.get(i - off)}' if r else f'no stall (dt {rq[i - off] if 0 <= i - off < len(rq) else "-"})'))
    ok = 2.0 in rq and 2.0 in pq and '0' in ec and '1VI' in ec
    print('control:', 'PASS (retail 2-VI dt + el 0 and 1VI seen; port 2-VI dt seen)' if ok else 'FAIL')
    return 0 if ok else 3


if __name__ == '__main__':
    sys.exit(main())
