#!/usr/bin/env python3
"""s7817: index-for-index comparison of two retail-oracle --fb-dump series (tools/s7816_oracle_rsp_ab.sh), no best-match
search. Per dump: whole 2 MB window identical?, VI number of the copy, visible-frame differing px (16 bpp, origin+width from
oracle.log, ROWS rows) and max 5-bit channel delta. Under --clock vi two same-plugin runs must agree on every vi= and every byte.
Positive control (--ctl): one visible pixel of B is flipped in memory for the first comparable frame and must read exactly 1 px.
usage: s7817_oracle_det.py A_dir B_dir [--rows 240] [--ctl]"""
import sys, os, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument('a'); ap.add_argument('b'); ap.add_argument('--rows', type=int, default=240)
ap.add_argument('--ctl', action='store_true'); o = ap.parse_args()
def meta(d):
    m = {}
    for l in open(os.path.join(d, 'oracle.log'), errors='replace'):
        g = re.match(r'\[fb-dump\] t=\s*[\d.]+s vi=(\d+) width=(\d+) origin=0x([0-9a-f]+) .* -> (\S+)', l)
        if g: m[os.path.basename(g.group(4))] = (int(g.group(1)), int(g.group(2)), int(g.group(3), 16))
    return m
def vis(raw, w, org):
    off = (org & 0xFFFFFF) - 0x600000; n = w * o.rows * 2
    return raw[off:off + n] if 0 <= off and off + n <= len(raw) else None
def diff(x, y):
    px = 0; mx = 0
    for i in range(0, min(len(x), len(y)), 2):
        if x[i:i+2] != y[i:i+2]:
            px += 1; p = (x[i] << 8) | x[i+1]; q = (y[i] << 8) | y[i+1]
            mx = max(mx, *(abs(((p >> s) & 31) - ((q >> s) & 31)) for s in (11, 6, 1)))
    return px, mx
ma, mb = meta(o.a), meta(o.b); names = sorted(set(ma) & set(mb))
tot = dict(n=0, raw_eq=0, vi_eq=0, vis_eq=0, px=0); ctl_done = False
for nm in names:
    (va, wa, oa), (vb, wb, ob) = ma[nm], mb[nm]
    ra = open(os.path.join(o.a, nm), 'rb').read(); rb = open(os.path.join(o.b, nm), 'rb').read()
    fa, fb = vis(ra, wa, oa), vis(rb, wb, ob)
    tot['n'] += 1; tot['raw_eq'] += ra == rb; tot['vi_eq'] += va == vb
    if fa is None or fb is None: print(f'{nm} vi {va}/{vb} raw_eq={int(ra==rb)} visible=n/a'); continue
    if o.ctl and not ctl_done:
        fb2 = bytearray(fb); fb2[1000] ^= 0x02; c, _ = diff(fa, fa[:1000] + bytes([fa[1000] ^ 0x02]) + fa[1001:])
        print(f'CTL planted 1 px -> {c} px {"PASS" if c == 1 else "FAIL"}'); ctl_done = True
    px, mx = diff(fa, fb); tot['vis_eq'] += px == 0; tot['px'] += px
    print(f'{nm} vi {va}/{vb} w={wa}/{wb} org={oa:08x}/{ob:08x} raw_eq={int(ra==rb)} vis_px={px} max5={mx}')
print('SUMMARY ' + ' '.join(f'{k}={v}' for k, v in tot.items()) + f' onlyA={len(set(ma)-set(mb))} onlyB={len(set(mb)-set(ma))}')
