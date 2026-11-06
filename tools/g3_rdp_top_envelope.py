#!/usr/bin/env python3
"""s6915 G3: top envelope of a frame's main textured surface, retail RDP dump vs port RDP dump, pixel-free.

Answers "does retail end this surface where the port does" when no retail pixels exist for the frame: retail.bin holds RDP
commands only. For each frame the surface is the texture with the most tris (--skip excludes a texture; addresses differ
between dumps and alternate per frame, so it is picked per frame). Envelope = lowest y of its tris per 32 px column bin.
Each sampled retail frame is paired with the port frame of the closest envelope, so run speed does not matter.
Frame numbers are g3_cine_sweep.py summ rows. Retail is entered by bisecting the record sequence stamp, port by parsing
the last --tail-gb of the file (raise it if "base" prints above PLO).

  g3_rdp_top_envelope.py RETAIL.bin RETAIL.tsv RLO:RHI PORT.bin PORT.tsv PLO:PHI [--tail-gb 3] [--samples 9] [--skip HEX] [--w 640]
  shot 78 of s6792: scratch/s6792/mov/retail.bin scratch/s6792/mr.tsv 19591:19844 scratch/s6792/mov/port.bin scratch/s6792/mp.tsv 33662:34162 --tail-gb 1.6 --skip 4e6c60

Control: the row "ctl" scores the same retail frame against the port frame half a shot away; it must be much larger than the
paired diff, or the envelope cannot discriminate. Tris span whole quads, so an envelope bin is an upper bound on the edge.
"""
import argparse, collections, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_cine_sweep import tribox

def parse(f, H, lo):
    """yield FULL_SYNC-delimited frames as lists of (texture, x0, x1, y0, y1); f sits on a record header"""
    carry = b''; cur = []; tex = 0
    while True:
        h = f.read(H)
        if len(h) < H: break
        buf = carry + f.read(struct.unpack_from('<I', h, lo)[0]); a = 0; end = len(buf)
        while a + 8 <= end:
            w0, w1 = struct.unpack_from('<II', buf, a); op = (w0 >> 24) & 0x3F; n = 8
            if 0x08 <= op <= 0x0F:
                n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
                if a + n > end: break
                cur.append((tex,) + tribox(buf, a))
            elif op in (0x24, 0x25):
                n = 16
                if a + n > end: break
            elif op == 0x3D: tex = w1 & 0xFFFFFF
            elif op == 0x29: yield cur; cur = []
            a += n
        carry = buf[a:]

def seek_retail(f, size, seq):
    lo, hi = 0, size
    while hi - lo > 1 << 16:
        m = (lo + hi) // 2; f.seek(m); b = f.read(1 << 16); i = b.find(b'CPDR')
        if struct.unpack_from('<I', b, i + 16)[0] < seq: lo = m
        else: hi = m
    f.seek(lo); b = f.read(1 << 16); f.seek(lo + b.find(b'CPDR'))

def envelope(fr, skip, w):
    c = collections.Counter(t[0] for t in fr if t[0] != skip)
    if not c or c.most_common(1)[0][1] < 250: return None
    tex = c.most_common(1)[0][0]; S = [t for t in fr if t[0] == tex]; out = []
    for x in range(0, w, 32):
        ys = [t[3] for t in S if t[1] < x + 32 and t[2] > x]
        out.append(round(min(ys), 2) if ys else None)
    return out

def dist(a, b):
    d = [abs(x - y) for x, y in zip(a, b) if x is not None and y is not None]
    return max(d) if d else float('inf')

def main():
    p = argparse.ArgumentParser(); p.add_argument('retail'); p.add_argument('rtsv'); p.add_argument('rr'); p.add_argument('port'); p.add_argument('ptsv'); p.add_argument('pr')
    p.add_argument('--tail-gb', type=float, default=3); p.add_argument('--samples', type=int, default=9); p.add_argument('--skip', default='0'); p.add_argument('--w', type=int, default=640)
    a = p.parse_args(); skip = int(a.skip, 16)
    rlo, rhi = map(int, a.rr.split(':')); plo, phi = map(int, a.pr.split(':'))
    rows = [l.split('\t') for l in open(a.rtsv)]; prows = sum(1 for _ in open(a.ptsv))
    f = open(a.retail, 'rb'); seek_retail(f, os.path.getsize(a.retail), int(rows[rlo - 6][6])); R = {}; i = rlo - 5
    for fr in parse(f, 20, 12):
        if i >= rlo: R[i] = envelope(fr, skip, a.w)
        i += 1
        if i >= rhi: break
    f = open(a.port, 'rb'); st = max(0, os.path.getsize(a.port) - int(a.tail_gb * 1e9)); f.seek(st); b = f.read(1 << 22); f.seek(st + b.find(b'PRDP'))
    F = [envelope(fr, skip, a.w) for fr in parse(f, 16, 8)]; base = prows - len(F)
    print('base', base, 'plo', plo)
    if base > plo: sys.exit('raise --tail-gb')
    P = {base + i: e for i, e in enumerate(F) if e and plo <= base + i < phi}; R = {k: v for k, v in R.items() if v}
    ks = sorted(R); pk = sorted(P); print('frames with a surface: retail', len(ks), 'port', len(pk))
    for k in ks[::max(1, len(ks) // a.samples)]:
        j = min(pk, key=lambda q: sum(abs((x or 0) - (y or 0)) for x, y in zip(R[k], P[q])))
        c = pk[(pk.index(j) + len(pk) // 2) % len(pk)]
        print(k, j, 'diff', round(dist(R[k], P[j]), 2), 'ctl', round(dist(R[k], P[c]), 2)); print('  ', R[k])

main()
