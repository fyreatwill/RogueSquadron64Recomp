#!/usr/bin/env python3
"""s7213: lit-extent of each window-capture frame around given mach times, to see a one-off letterbox/pillarbox present.
usage: s7213_box_scan.py <raw> <mach> [mach ...]   (g5b_capture raw: header <QII t0,w,h>, records <Q t><pad8> + w*h*3 RGB)
Per frame: lit row span (rows whose sampled luma mean > THR) and lit column span, plus mean luma. A boxed present shows a lit span
narrower than its neighbours. Positive control per event: the brightest frame within +-1 s gets its outer quarter rows/cols zeroed
and must report the narrowed span (CONTROL PASS); a frame that is dark everywhere cannot show a box (verdict DARK)."""
import sys, struct, os
raw = sys.argv[1]; f = open(raw, 'rb'); t0, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = os.path.getsize(raw) // rec
THR, Y0 = 6.0, 40  # luma threshold; skip title-bar rows
T = []
for i in range(n): f.seek(i * rec); T.append(struct.unpack('<Q', f.read(8))[0])
def frame(i): f.seek(i * rec + 16); return bytearray(f.read(w * h * 3))
def lum(seg): return (sum(seg[0::3]) + 2 * sum(seg[1::3]) + sum(seg[2::3])) / (4 * max(1, len(seg) // 3))
def extent(a):
    rows = [y for y in range(Y0, h, 4) if lum(a[y * w * 3:(y + 1) * w * 3]) > THR]
    body = a[Y0 * w * 3:]; hh = h - Y0
    cols = [x for x in range(0, w, 4) if (sum(body[x * 3::w * 3]) + 2 * sum(body[x * 3 + 1::w * 3]) + sum(body[x * 3 + 2::w * 3])) / (4 * hh) > THR]
    tot = sum(body[::31]) / max(1, len(body[::31]))
    return (rows[0], rows[-1]) if rows else None, (cols[0], cols[-1]) if cols else None, tot
def span(e): return (e[1] - e[0]) if e else 0
if sys.argv[2] == 'scan':  # whole-raw census: flag frames whose lit row or col span is <90% of the median of +-4 lit neighbours
    E = [extent(frame(i)) for i in range(n)]; hits = 0
    for i in range(n):
        nb = [E[j] for j in range(max(0, i - 4), min(n, i + 5)) if j != i and E[j][0] and E[j][1]]
        if len(nb) < 4 or not E[i][0] or not E[i][1]: continue
        mr = sorted(span(e[0]) for e in nb)[len(nb) // 2]; mc = sorted(span(e[1]) for e in nb)[len(nb) // 2]
        if span(E[i][0]) < 0.9 * mr or span(E[i][1]) < 0.9 * mc:
            hits += 1; print('NARROW f%d mach %d rows %s cols %s mean %.1f (nb median rows %d cols %d)' % (i, T[i], E[i][0], E[i][1], E[i][2], mr, mc))
    print('frames', n, 'lit', sum(1 for e in E if e[0]), 'narrow', hits); sys.exit()
for m in map(int, sys.argv[2:]):
    k = min(range(n), key=lambda i: abs(T[i] - m))
    if abs(T[k] - m) > 24e6 * 0.1: print('mach %d outside raw (%d..%d)' % (m, T[0], T[-1])); continue
    print('== event mach %d nearest frame %d (%+.1f ms)' % (m, k, (T[k] - m) / 24e3))
    for i in range(max(0, k - 8), min(n, k + 12)):
        r, c, t = extent(frame(i)); print('  f%d %+7.1f ms rows %s cols %s mean %.1f' % (i, (T[i] - m) / 24e3, r, c, t))
    lo, hi = max(0, k - 60), min(n, k + 60); b = max(range(lo, hi, 4), key=lambda i: extent(frame(i))[2])
    a = frame(b); r0, c0, _ = extent(a); z = bytearray(a)
    for y in range(h):
        o = y * w * 3
        if y < h // 4 or y > 3 * h // 4: z[o:o + w * 3] = bytes(w * 3)
        else: z[o:o + (w // 4) * 3] = bytes((w // 4) * 3); z[o + (3 * w // 4) * 3:o + w * 3] = bytes((w - 3 * w // 4) * 3)
    r1, c1, _ = extent(z); ok = r1 and c1 and r1[0] >= h // 4 - 4 and r1[1] <= 3 * h // 4 + 4 and c1[0] >= w // 4 - 4 and c1[1] <= 3 * w // 4 + 4 and r0 != r1
    print('  control f%d orig rows %s cols %s -> boxed rows %s cols %s: CONTROL %s' % (b, r0, c0, r1, c1, 'PASS' if ok else 'FAIL'))
