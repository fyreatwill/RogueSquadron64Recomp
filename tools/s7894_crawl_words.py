#!/usr/bin/env python3
"""s7894 G3 m6 island A: the crawl scene loop's own state words, retail vs port, call-aligned at the crawl dt site.

runModelViewerLoop (0x800C9BF0, frame 0x108; really the post-crawl craft scene loop: it calls selectPostCrawlCraft) calls the
menu dt site 0x800C6660 (frame 0x48) from ra 0x800C9D94 once per frame. Its locals sp+0xC0..0xDC are read at mark 0x800C6674
as callee sp+0x108..0x124 (tools/s7891_crawl_clock.sh MX=800C6674:29:108:8):
  C0 C4 C8 CC  position/camera floats advanced by dt*const (0x800C9EF0.. 0x800C9FD8)
  D0           derived rate (0x800C9D88)          D4  accumulated time (+= f24 each frame, 0x800C9DC0)   D8 start value
Per word: first call index where port != retail (abs tol --tol, default 1e-4), and the port-retail delta at that call and
at the end. Every word equal -> H-retail-rdp; a time word (D4) differs -> H-carry; only position words differ -> H-text.
Control (iron rule 1): --plant K adds 1.0 to port word D4 from call K on; the scorer must report D4 differing on every call from K on (rc 3 if not).
usage: s7894_crawl_words.py RETAIL.log PORT_RAND.txt [--plant K] [--tol T]
"""
import re, struct, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rs64_zopen import zopen

NAMES = ['C0', 'C4', 'C8', 'CC', 'D0', 'D4', 'D8', 'DC']


def f32(h):
    return struct.unpack('>f', bytes.fromhex(h.zfill(8)))[0]


def parse(path, retail):
    rows = []
    with zopen(path) as fh:
        for ln in fh:
            if isinstance(ln, bytes): ln = ln.decode(errors='replace')
            if retail:
                m = re.match(r'\[xtrace\] \d+ (\d+) \S+ \S+ pc=([0-9a-f]{8})', ln)
                if not m: continue
                vi, pc = int(m.group(1)), int(m.group(2), 16)
            else:
                t = ln.split(' ', 4)
                if len(t) < 4: continue
                try: vi, pc = int(t[1]), int(t[2], 16)
                except ValueError: continue
            if pc != 0x800C6674: continue
            fs = re.findall(r' m=([0-9a-f]{8}):([0-9a-f,]+)', ln)
            w8 = next((w.split(',') for a, w in fs if len(w.split(',')) == 8), None)
            ra = next((w for a, w in fs if len(w.split(',')) == 1 and int(a, 16) != 0x8013889C), '-')
            if w8 is None: continue
            rows.append(dict(vi=vi, w=[f32(x) for x in w8], raw=w8, ra=ra))
    return rows


def crawl_seg(rows, retail):
    """last contiguous run (<= 8 VI gaps) of >= 20 calls; retail: the run whose ra is 800c9d94"""
    segs, s = [], 0
    for i in range(1, len(rows) + 1):
        if i == len(rows) or rows[i]['vi'] - rows[i - 1]['vi'] > 8:
            if i - s >= 20: segs.append((s, i))
            s = i
    if retail:
        segs = [x for x in segs if rows[x[0]]['ra'] == '800c9d94'] or segs
    return segs[-1] if segs else None


def main():
    a = sys.argv[1:]
    if len(a) < 2: print(__doc__); return 2
    plant = int(a[a.index('--plant') + 1]) if '--plant' in a else None
    tol = float(a[a.index('--tol') + 1]) if '--tol' in a else 1e-4
    R, P = parse(a[0], True), parse(a[1], False)
    print(f'rows with 8 locals: retail {len(R)} port {len(P)}')
    rs, ps = crawl_seg(R, True), crawl_seg(P, False)
    if not rs or not ps: print('no crawl segment'); return 3
    (r0, r1), (p0, p1) = rs, ps
    n = min(r1 - r0, p1 - p0)
    print(f'crawl seg retail [{r0}:{r1}] vi {R[r0]["vi"]}..{R[r1-1]["vi"]} | port [{p0}:{p1}] vi {P[p0]["vi"]}..{P[p1-1]["vi"]} | aligned {n}')
    for i in (0, 1, 2, 3, 4):
        print(f'  call {i}: retail {" ".join(f"{x:.4f}" for x in R[r0+i]["w"])}\n          port   {" ".join(f"{x:.4f}" for x in P[p0+i]["w"])}')
    rc, res = 0, {}
    for j, nm in enumerate(NAMES):
        first, ndiff, dmax = None, 0, 0.0
        for i in range(n):
            pv = P[p0 + i]['w'][j] + (1.0 if plant is not None and nm == 'D4' and i >= plant else 0.0)
            d = pv - R[r0 + i]['w'][j]
            if abs(d) > tol:
                ndiff += 1; dmax = max(dmax, abs(d))
                if first is None: first = (i, d)
        res[nm] = (first, ndiff)
        last = P[p0 + n - 1]['w'][j] - R[r0 + n - 1]['w'][j]
        print(f'  {nm}: differ {ndiff}/{n} first {first[0] if first else None} d_first {first[1] if first else 0:+.5f} '
              f'max|d| {dmax:.5f} d_last {last:+.5f}')
    if plant is not None:
        ok = res['D4'][1] >= n - plant
        print(f'control plant +1.0 on D4 from call {plant}: {"PASS" if ok else "FAIL"}'); rc = 0 if ok else 3
    return rc


if __name__ == '__main__':
    sys.exit(main())
