#!/usr/bin/env python3
# s7211: per VI mode, the rows the HARDWARE VI scans vs the rows RT64 presents, from a run log with ROGUESQ_VI_EXTENT_PROBE=2
# (+ ROGUESQ_VI_SHAPE_LOG=1 for the window viewport). Hardware: (vEnd-vStart)/2 lines per field, each advancing yScale/1024 stride rows;
# a double-stride interlace (width = 2x fb cols) reads alternate fb rows per field, so the frame shows lines*yScale/1024 fb rows either way.
# RT64 VI::fbSize() adds 2 "ExtraRows" and rounds to x4 (s7147). usage: s7211_vi_rows.py <run.log>
import re, sys
V = re.compile(r'\[viext #\d+\] origin=0x([0-9A-F]+) width=(\d+) .*?vStart=(\d+) vEnd=(\d+) yScale=0x([0-9A-F]+) .*?serrate=(\d) visRows1024=(\d+) fbSize=(\d+)x(\d+)')
P = re.compile(r'\[g1d-vishape-vp\] fb (\d+)x(\d+) vp ([\d.]+),([\d.]+) ([\d.]+)x([\d.]+)')
modes, vps = {}, {}
for ln in open(sys.argv[1], 'rb'):
    s = ln.decode('latin1')
    m = V.search(s)
    if m:
        o, w, vs, ve, ys, ser, vr, fx, fy = m.groups(); w, vs, ve, ys, fx, fy = int(w), int(vs), int(ve), int(ys, 16), int(fx), int(fy)
        if ve <= vs: continue
        # stride rows per field = lines/2 * ys/1024; in fb rows x2 when the stride is two fb rows (double-stride interlace)
        k = (w, vs, ve, ys, ser); hw = (ve - vs) / 2.0 * ys / 1024.0 * (2.0 if fx * 2 == w else 1.0)
        modes.setdefault(k, [0, hw, fx, fy]); modes[k][0] += 1
        continue
    m = P.search(s)
    if m: vps.setdefault((int(m.group(1)), int(m.group(2))), set()).add('%s,%s %sx%s' % m.groups()[2:])
print('%6s %4s %4s %6s %3s | %7s %9s %8s | %s' % ('width', 'vS', 'vE', 'yScale', 'ser', 'hw rows', 'RT64 box', 'extra', 'window vp (x,y wxh)'))
for (w, vs, ve, ys, ser), (n, hw, fx, fy) in sorted(modes.items(), key=lambda t: -t[1][0]):
    print('%6d %4d %4d %#6x %3s | %7.1f %4dx%-4d %+8.1f | %s' % (w, vs, ve, ys, ser, hw, fx, fy, fy - hw, '; '.join(sorted(vps.get((fx, fy), [])))[:90]))
