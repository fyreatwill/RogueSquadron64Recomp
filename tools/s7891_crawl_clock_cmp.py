#!/usr/bin/env python3
"""s7891 G3 island A: per-call dt at the pre-flight dt sites (menu advanceWrappingPhaseAccumulator mark 0x800C6674, cinematic
cinematicComputeDt mark 0x800AF374), retail oracle log vs port ROGUESQ_RAND_TRACE file (tools/s7891_crawl_clock.sh).

Both sites quantize timeSnapshotFiller's stored value v (struct +0x20) by the VI period p (+0x1C): r = frac(v/p)*p;
r/p < 0.5 -> v - r, else v + p - r; v <= 0 -> 1/60; menu also clamps to <= 1/6. dt is printed in VI units (dt*60).
Per side: run-length table of (site, dt VI) with first VI and caller ra (retail; the port leaves $ra unset). Then the
640 crawl segment (longest run of menu-site calls that follows the hangar, chosen as the retail segment whose caller ra
covers island A, see --seg) is aligned call-by-call on its first call, and the cumulative dt (sum from segment start)
is compared: delta 0 everywhere -> guest time state equal; a constant +-1 VI -> half a 2-VI frame (H-index).
Control (iron rule 1): --plant K adds +1 VI to port call K of the segment and the comparator must report a 1-VI cumulative
delta from K on (rc 3 if not).
usage: s7891_crawl_clock_cmp.py RETAIL.log PORT_RAND.txt [--plant K[:SEG]]  (s7898: SEG = menu segment pair index, default 0)
"""
import re, struct, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import zopen

SITES = {0x800C6674: 'menu', 0x800AF374: 'cine'}


def f32(h):
    return struct.unpack('>f', bytes.fromhex(h))[0]


def quant(site, v, p):
    if p > 0:
        q = v / p
        r = (q - int(q)) * p
        if r > 0:
            v = v - r if r / p < 0.5 else v + p - r
    if v <= 0:
        v = 1 / 60
    if site == 'menu' and v > 1 / 6:
        v = 1 / 6
    return v


def parse(path, retail):
    rows = []
    with zopen(path) as fh:
        for ln in fh:
            if isinstance(ln, bytes): ln = ln.decode(errors='replace')
            if retail:
                if not ln.startswith('[xtrace]'): continue
                m = re.match(r'\[xtrace\] \d+ (\d+) \S+ \S+ pc=([0-9a-f]{8})', ln)
                if not m: continue
                vi, pc = int(m.group(1)), int(m.group(2), 16)
            else:
                t = ln.split(' ', 4)
                if len(t) < 4: continue
                try: vi, pc = int(t[1]), int(t[2], 16)
                except ValueError: continue
            if pc not in SITES: continue
            mm = dict((int(a, 16), w.split(',')) for a, w in re.findall(r' m=([0-9a-f]{8}):([0-9a-f,]+)', ln))
            st = next((w for a, w in mm.items() if len(w) == 12), None)
            if st is None: continue
            site = SITES[pc]
            v, p = f32(st[8]), f32(st[7])
            ra = next((w[0] for a, w in mm.items() if len(w) == 1 and a not in (0x8013889C, 0x800B0B2C, 0x80130BA4)), '-')
            rows.append(dict(vi=vi, site=site, raw=v, dt=quant(site, v, p), cnt=int(mm.get(0x8013889C, ['0'])[0], 16),
                             ra=ra if retail else '-', acc=[f32(mm[a][0]) for a in (0x800B0B2C, 0x80130BA4) if a in mm]))
    return rows


def table(name, rows):
    print(f'== {name}: {len(rows)} calls')
    out, prev = [], None
    for i, r in enumerate(rows):
        k = (r['site'], round(r['dt'] * 60), r['ra'])
        if k != prev: out.append([i, 0, k, r['vi']]); prev = k
        out[-1][1] += 1
    for i, n, k, vi in out[:80]:
        print(f'  call {i:6d} n {n:5d} vi {vi:6d}  {k[0]} dt {k[1]} VI  ra {k[2]}')
    if len(out) > 80: print(f'  ... {len(out) - 80} more runs')
    return out


def segments(rows):
    """contiguous same-site runs where consecutive calls are <= 8 VI apart"""
    segs, s = [], 0
    for i in range(1, len(rows) + 1):
        if i == len(rows) or rows[i]['site'] != rows[s]['site'] or rows[i]['vi'] - rows[i - 1]['vi'] > 8:
            segs.append((s, i)); s = i
    return segs


def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 2
    pa = a[a.index('--plant') + 1].split(':') if '--plant' in a else None
    plant = int(pa[0]) if pa else None; pseg = int(pa[1]) if pa and len(pa) > 1 else 0
    R, P = parse(a[0], True), parse(a[1], False)
    if not R or not P: print(f'no rows (retail {len(R)} port {len(P)})'); return 3
    table('retail', R); table('port', P)
    rs, ps = segments(R), segments(P)
    print('retail segments (site, calls, vi0..vi1, ra set, dt VI histogram):')
    for s, e in rs:
        if e - s < 20: continue
        h = {}
        for r in R[s:e]: h[round(r['dt'] * 60)] = h.get(round(r['dt'] * 60), 0) + 1
        print(f'  [{s}:{e}] {R[s]["site"]} n {e - s} vi {R[s]["vi"]}..{R[e - 1]["vi"]} ra {sorted({r["ra"] for r in R[s:e]})} dt {h}')
    print('port segments:')
    for s, e in ps:
        if e - s < 20: continue
        h = {}
        for r in P[s:e]: h[round(r['dt'] * 60)] = h.get(round(r['dt'] * 60), 0) + 1
        print(f'  [{s}:{e}] {P[s]["site"]} n {e - s} vi {P[s]["vi"]}..{P[e - 1]["vi"]} dt {h}')
    # pair segments in order of appearance per site (both sides walk the same menu/cinematic sequence)
    rc = 0
    for site in ('menu', 'cine'):
        RS = [x for x in rs if R[x[0]]['site'] == site and x[1] - x[0] >= 20]
        PS = [x for x in ps if P[x[0]]['site'] == site and x[1] - x[0] >= 20]
        for k, ((r0, r1), (p0, p1)) in enumerate(zip(RS, PS)):
            n = min(r1 - r0, p1 - p0)
            rd = [round(R[r0 + i]['dt'] * 60) for i in range(n)]
            pd = [round(P[p0 + i]['dt'] * 60) for i in range(n)]
            if plant is not None and k == pseg and site == 'menu' and plant < n: pd[plant] += 1
            cr = cp = 0; first = None; deltas = {}
            for i in range(n):
                cr += rd[i]; cp += pd[i]
                d = cp - cr; deltas[d] = deltas.get(d, 0) + 1
                if d and first is None: first = i
            same = sum(x == y for x, y in zip(rd, pd))
            acc = ''
            if site == 'cine' and R[r0]['acc'] and P[p0]['acc']:
                ad = [P[p0 + i]['acc'][0] - R[r0 + i]['acc'][0] for i in range(n)]
                acc = f' acc0x800B0B2C delta(port-retail) first {ad[0]:+.5f} last {ad[-1]:+.5f} min {min(ad):+.5f} max {max(ad):+.5f}'
            print(f'{site} seg {k}: retail [{r0}:{r1}] vi {R[r0]["vi"]} n {r1 - r0} | port [{p0}:{p1}] vi {P[p0]["vi"]} n {p1 - p0} | '
                  f'per-call dt equal {same}/{n}, first cum delta at call {first}, cum delta VI histogram {dict(sorted(deltas.items()))}{acc}')
            if plant is not None and k == pseg and site == 'menu':
                ok = first is not None and first <= plant and deltas.get(1, 0) >= n - plant - 1
                print(f'control plant +1 VI at call {plant}: {"PASS" if ok else "FAIL"}')
                rc = 0 if ok else 3
    return rc


if __name__ == '__main__':
    sys.exit(main())
