#!/usr/bin/env python3
"""s7909 G3: per-game-frame VI spacing, retail vs port, over one press-delimited VI window (island B's +28 frames).

Retail: an rs64_oracle log with `--exec-trace-also 0x8000BBE8` + RS64_XTRACE_MEM ...8011A904 (s7872 rdt recipe): one
`[xtrace] n VI ... pc=8000bbe8 ... m=8011a904:<dt>` row per game frame (computeFrameDeltaTime), and `[press] vi=N down` rows.
Port: run.log with ROGUESQ_S7835_DT=1 (`[dt7835] vi n=` per VI wake, `[dt7835] fr n= dt=` per frame) and `[autopilot] fire`
rows (the dt7835 VI at each fire is taken as that press's port VI).
The VI clocks are aligned by the presses (retail press k VI - port fire k VI must be constant for list items A-1..A+1, rc 3 if not).
--a is the 1-based index into the DOWN-press list (the autopilot's gate event 3 has no row, so m11 key press 7 = item 6).
Window = [press A, press B) on each side (default A=7, B = last press both sides have before the window end VI given
by --end-ret VI, e.g. retail's 512->640 WIDTH change). Prints per side: frames, wake-VI gap histogram, stalls (gap > 3 VI)
with their window offset, dt class histogram, and per-bucket (--bucket VI, default 120) frame counts with the port-retail
difference, so extra frames show as spread (H-cost) or as one bucket (H-scene / stall-length).
Control (iron rule 1): both sides must show the steady 2-VI class in the window and >=1 frame per bucket; rc 3 otherwise.
usage: s7909_window_vi.py RETAIL_ORACLE.log[.zst] PORT_RUN.log[.zst] [--a 6] [--end-ret VI] [--bucket 120] [--off N]
"""
import re, sys, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import zopen

RVI, PVI = 811092, 781250


def lines(p):
    with zopen(p) as f:
        for l in f:
            yield l.decode('latin1') if isinstance(l, bytes) else l


def retail(p):
    fr, pr = [], []
    for l in lines(p):
        if l.startswith('[xtrace]') and 'pc=8000bbe8' in l:
            m = re.search(r'm=8011a904:([0-9a-f]+)', l)
            fr.append((int(l.split()[2]), int(m[1], 16) / RVI if m else None))
        elif l.startswith('[press]') and ' down ' in l:
            pr.append(int(re.search(r'vi=(\d+)', l)[1]))
    return fr, pr


def port(p):
    fr, pr, vi = [], [], 0
    for l in lines(p):
        if l.startswith('[dt7835] vi n='): vi = int(l.split()[2][2:])
        elif l.startswith('[dt7835] fr n='): fr.append((vi, int(l.split()[3][3:]) / PVI))
        elif l.startswith('[autopilot] fire'): pr.append(vi)
    return fr, pr


def side(tag, fr, lo, hi, bk):
    w = [(v, d) for v, d in fr if lo <= v < hi]
    gaps = [b[0] - a[0] for a, b in zip(w, w[1:])]
    st = [(w[i][0] - lo, gaps[i]) for i in range(len(gaps)) if gaps[i] > 3]
    dc = collections.Counter(round(d, 2) if d is not None else None for _, d in w)
    bc = collections.Counter((v - lo) // bk for v, _ in w)
    print(f'{tag}: window VI [{lo},{hi}) = {hi - lo} VI, frames {len(w)}')
    print(f'  wake-gap hist {sorted(collections.Counter(gaps).items())}')
    print(f'  stalls (offsetVI, gapVI) {st}  stall VI total {sum(g for _, g in st)}')
    print(f'  dt classes (VI) {sorted(dc.items(), key=lambda x: (x[0] is None, x[0] or 0))}')
    return w, gaps, bc, dc


def main():
    a = sys.argv[1:]
    def opt(k, d):
        if k in a: i = a.index(k); v = int(a[i + 1]); del a[i:i + 2]; return v
        return d
    A, END, BK, OFF = opt('--a', 6), opt('--end-ret', None), opt('--bucket', 120), opt('--off', None)
    if len(a) != 2: print(__doc__); return 2
    rf, rp = retail(a[0]); pf, pp = port(a[1])
    n = min(len(rp), len(pp)); offs = [rp[i] - pp[i] for i in range(n)]
    print(f'presses retail {rp[:n]}\n        port   {pp[:n]}\n  offsets {offs}')
    # the port autopilot's width gate (fire 3) rebases its clock, so only the window's own presses must agree
    win = offs[max(0, A - 2):A + 1]
    if OFF is not None: win = [OFF]   # s7909: --off N forces the retail-port VI offset (windows straddling a port stall)
    if len(set(win)) != 1: print(f'control: FAIL (press VI offset not constant over press-list items {A - 1}..{A + 1}: {win})'); return 3
    off = win[0]
    rlo = rp[A - 1]; rhi = END if END is not None else rp[A]
    rw, rg, rb, rd = side('retail', rf, rlo, rhi, BK)
    pw, pg, pb, pd = side('port  ', pf, rlo - off, rhi - off, BK)
    print(f'frames port - retail = {len(pw) - len(rw)}')
    print('per-bucket (bucket start VI offset: retail port diff), nonzero diffs only:')
    nb = (rhi - rlo + BK - 1) // BK
    rows = [(k * BK, rb[k], pb[k], pb[k] - rb[k]) for k in range(nb)]
    print('  ' + ' '.join(f'{o}:{r}/{p}/{d:+d}' for o, r, p, d in rows if d))
    print(f'  buckets with diff: {sum(1 for r in rows if r[3])}/{nb}; sum diff {sum(r[3] for r in rows)}')
    ok = rd.get(2.0, 0) > 0 and pd.get(2.0, 0) > 0 and all(r[1] and r[2] for r in rows[:-1])
    print('control:', 'PASS' if ok else 'FAIL')
    return 0 if ok else 3


if __name__ == '__main__':
    sys.exit(main())
