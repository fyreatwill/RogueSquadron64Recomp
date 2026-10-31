#!/usr/bin/env python3
"""s6691: score the 21:9 level-select floor tear in a framebuffer dump.

The s6611/s6631 scorer reads step columns at x=16 / x=w-17 and dy at row
180. It passed the s6631 21:9 level-select frame, which still shows the
floor as horizontal stripes of unrelated texels. A torn floor varies from
row to row; a real floor is smooth down a column. So: mean |dLuma| between
vertically adjacent pixels over the side floor band (rows Y0..Y1, outer
SIDE fraction of the width each side, which keeps the centre table out).
Measured s6691: clean 16:9 / 21:9 hangar frames 5.1-6.8, torn 21:9
level-select frames 19.1-26.1. Torn when > VHF_MAX.

Self-test: shuffle the band's rows in 2-row strips of a clean frame (the
tear's shape: whole rows taken from elsewhere) and require the score to
cross VHF_MAX while the clean frame stays below it.

usage: g1d_row_noise.py [--selftest clean.ppm] frame.ppm[.zst] ...
"""
import json
import random
import subprocess
import sys

Y0, Y1 = 180, 330
SIDE = 0.22
VHF_MAX = 10.0


def load(path):
    data = open(path, 'rb').read()
    if path.endswith('.zst'):
        data = subprocess.run(['zstd', '-dcq', path], capture_output=True, check=True).stdout
    toks, pos = [], 0
    while len(toks) < 4:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b'#':
            pos = data.index(b'\n', pos) + 1
            continue
        end = pos
        while not data[end:end + 1].isspace():
            end += 1
        toks.append(data[pos:end])
        pos = end
    pos += 1
    w, h = int(toks[1]), int(toks[2])
    px = data[pos:pos + w * h * 3]
    rows = []
    for y in range(h):
        r = px[y * w * 3:(y + 1) * w * 3]
        rows.append([(30 * r[3 * x] + 59 * r[3 * x + 1] + 11 * r[3 * x + 2]) / 100.0
                     for x in range(w)])
    return w, h, rows


def score(w, h, rows):
    xs = [x for x in range(w) if x < w * SIDE or x > w * (1 - SIDE)]
    s = n = 0
    for y in range(Y0, min(h - 1, Y1)):
        a, b = rows[y], rows[y + 1]
        for x in xs:
            s += abs(b[x] - a[x])
            n += 1
    vhf = s / n if n else 0.0
    return dict(w=w, h=h, vhf=round(vhf, 2), torn=vhf > VHF_MAX)


def selftest(path):
    w, h, rows = load(path)
    clean = score(w, h, rows)
    strips = [rows[y:y + 2] for y in range(Y0, Y1, 2)]
    random.Random(6691).shuffle(strips)
    torn = rows[:Y0] + [r for s in strips for r in s] + rows[Y0 + 2 * len(strips):]
    t = score(w, h, torn)
    return dict(clean=clean['vhf'], shuffled=t['vhf'], ok=(not clean['torn']) and t['torn'])


def main(argv):
    if argv and argv[0] == '--selftest':
        res = selftest(argv[1])
        print(json.dumps(res))
        return 0 if res['ok'] else 2
    for p in argv:
        print(p, json.dumps(score(*load(p))))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
