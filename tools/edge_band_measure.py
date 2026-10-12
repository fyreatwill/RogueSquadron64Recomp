#!/usr/bin/env python3
"""Measure right-edge garbage band width in hangar frame PNGs.

Usage: edge_band_measure.py DIR
Per frame: per-column vertical roughness (mean |row-to-row diff|, RGB) for the
last 12 columns and first 4 columns, as a multiple of the median column
roughness (interior control). Stdlib only: minimal 8-bit non-interlaced PNG
decoder (no numpy/PIL on this machine).
"""
import glob
import statistics
import struct
import sys
import zlib


def decode_png(path):
    data = open(path, "rb").read()
    pos, idat = 8, b""
    while pos < len(data):
        n, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, inter = struct.unpack(">IIBBBBB", body)
        elif typ == b"IDAT":
            idat += body
        pos += 12 + n
    assert depth == 8 and inter == 0 and ctype in (2, 6), (depth, ctype, inter)
    bpp = 3 if ctype == 2 else 4
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev = [], bytearray(stride)
    for y in range(h):
        off = y * (stride + 1)
        ft = raw[off]
        cur = bytearray(raw[off + 1:off + 1 + stride])
        for i in range(stride):
            a = cur[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if ft == 1:
                cur[i] = (cur[i] + a) & 255
            elif ft == 2:
                cur[i] = (cur[i] + b) & 255
            elif ft == 3:
                cur[i] = (cur[i] + ((a + b) >> 1)) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                cur[i] = (cur[i] + pr) & 255
        rows.append(cur)
        prev = cur
    return w, h, bpp, rows


for f in sorted(glob.glob(sys.argv[1] + "/f_*.png")):
    w, h, bpp, rows = decode_png(f)
    rough = []
    for x in range(w):
        s = 0
        for y in range(h - 1):
            r0, r1 = rows[y], rows[y + 1]
            o = x * bpp
            s += abs(r0[o] - r1[o]) + abs(r0[o + 1] - r1[o + 1]) + abs(r0[o + 2] - r1[o + 2])
        rough.append(s / (3.0 * (h - 1)))
    med = statistics.median(rough) or 1e-6
    r = ["%.1f" % (v / med) for v in rough[-12:]]
    l = ["%.1f" % (v / med) for v in rough[:4]]
    print(f.split("/")[-1], w, h, "med=%.1f" % med, "L4x", l, "R12x", r)
