#!/usr/bin/env python3
"""s7816: compare two retail-oracle --fb-dump series (tools/s7816_oracle_rsp_ab.sh) from different RSP plugins.
For each dump of A (t*.bin title/menu 1024 phase, h*.bin 512 phase) the best-matching dump of B within +-W indices is found
on the VISIBLE framebuffer (VI origin from oracle.log, 16 bpp, width from the log, H rows); prints differing px and max 5-bit
channel delta. Exactly-equal frames prove the two plugins rendered that frame identically.
Positive control (--ctl): one pixel of B's matched frame is flipped and must report exactly 1 px.
usage: s7816_fb_ab.py A_dir B_dir [--win 3] [--rows 240] [--ctl]"""
import sys, os, re, argparse, glob
def meta(d):
    m = {}
    for l in open(os.path.join(d, 'oracle.log'), errors='replace'):
        g = re.match(r'\[fb-dump\] t=\s*([\d.]+)s vi=(\d+) width=(\d+) origin=0x([0-9a-f]+) .* -> (\S+)', l)
        if g: m[os.path.basename(g.group(5))] = (float(g.group(1)), int(g.group(3)), int(g.group(4), 16))
    return m
def frame(d, name, mt, rows):
    t, w, org = mt[name]; raw = open(os.path.join(d, name), 'rb').read()
    off = (org & 0xFFFFFF) - 0x600000; n = w * rows * 2
    if off < 0 or off + n > len(raw): return None
    return raw[off:off + n], w
def cmp(a, b):
    px = mx = 0
    for i in range(0, min(len(a), len(b)), 2):
        if a[i] != b[i] or a[i+1] != b[i+1]:
            px += 1; x = (a[i] << 8) | a[i+1]; y = (b[i] << 8) | b[i+1]
            mx = max(mx, max(abs(((x >> s) & 31) - ((y >> s) & 31)) for s in (11, 6, 1)))
    return px, mx
ap = argparse.ArgumentParser(); ap.add_argument('a'); ap.add_argument('b'); ap.add_argument('--win', type=int, default=3)
ap.add_argument('--rows', type=int, default=240); ap.add_argument('--ctl', action='store_true'); o = ap.parse_args()
MA, MB = meta(o.a), meta(o.b); tot = {}; ctl_done = False
for pre in ('t', 'h'):
    names = sorted(n for n in MA if n.startswith(pre))
    for n in names:
        fa = frame(o.a, n, MA, o.rows)
        if not fa: continue
        k = int(n[1:4]); best = None
        for j in range(k - o.win, k + o.win + 1):
            nb = '%s%03d.bin' % (pre, j)
            if nb not in MB: continue
            fb = frame(o.b, nb, MB, o.rows)
            if not fb or fb[1] != fa[1]: continue
            r = cmp(fa[0], fb[0])
            if best is None or r[0] < best[0][0]: best = (r, nb, fb[0])
        if best is None: print(n, 'no partner'); continue
        if o.ctl and not ctl_done and best[0][0] == 0:
            bb = bytearray(best[2]); bb[len(bb) // 2] ^= 0x40; c = cmp(fa[0], bytes(bb))
            print('CTL plant 1 px on %s vs %s -> %d px %s' % (n, best[1], c[0], 'PASS' if c[0] == 1 else 'FAIL')); ctl_done = True
        print('%s w=%d t=%.1f best=%s diff_px=%d maxd5=%d' % (n, fa[1], MA[n][0], best[1], best[0][0], best[0][1]))
        s = tot.setdefault(pre, [0, 0, 0]); s[0] += 1; s[1] += best[0][0] == 0; s[2] += best[0][0]
for pre, s in tot.items(): print('SUMMARY phase=%s frames=%d exact=%d diff_px_total=%d' % (pre, s[0], s[1], s[2]))
if o.ctl and not ctl_done: print('CTL not run: no exact frame to plant on')
