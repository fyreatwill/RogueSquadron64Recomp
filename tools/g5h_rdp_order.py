#!/usr/bin/env python3
"""s6917 G5h: draw order of one RDP dump frame, as runs of tris sharing a blender word (SET_OTHER_MODES low word).
Answers "what was drawn after what, and with which z" for a frame, so a sky-coloured band or a missing object can be named from the
command stream rather than from pixels. Reads the tail of a RS64_RDP_BIN_PORT dump, FULL_SYNC-delimited frames.

  g5h_rdp_order.py DUMP.bin [--tail-gb 2] [--frames A:B:STEP] [--min-tris 200] [--w 0]
Each run row: first tri index, blender, Z flags (c = compare, u = update), n tris, op, y range, x range, z range (integer part of the tri's z; for a tri with no z block, the last SET_PRIM_DEPTH).
Control: terrain tris should read blender ..2220 (update, no compare) and ships ..2230: if neither shows, the parse is off.
"""
import argparse, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from g3_cine_sweep import tribox

def frames(f, end=None):
    carry = b''; cur = []; mode = 0; cmb = 0; tex = 0; pd = None
    while True:
        h = f.read(16)
        if len(h) < 16: break
        buf = carry + f.read(struct.unpack_from('<I', h, 8)[0]); a = 0; n_ = len(buf)
        while a + 8 <= n_:
            w0, w1 = struct.unpack_from('<II', buf, a); op = (w0 >> 24) & 0x3F; n = 8
            if 0x08 <= op <= 0x0F:
                n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
                if a + n > n_: break
                x0, x1, y0, y1 = tribox(buf, a)
                z = struct.unpack_from('<i', buf, a + n - 16)[0] >> 16 if op & 1 else pd
                cur.append((op, mode, cmb, tex, x0, x1, y0, y1, z))
            elif op in (0x24, 0x25):
                n = 16
                if a + n > n_: break
                cur.append((op, mode, cmb, tex, ((w1 >> 12) & 0xFFF) / 4, ((w0 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4, (w0 & 0xFFF) / 4, None))
            elif op == 0x36:
                cur.append((op, mode, cmb, tex, ((w1 >> 12) & 0xFFF) / 4, ((w0 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4, (w0 & 0xFFF) / 4, None))
            elif op == 0x2F: mode = w1
            elif op == 0x2E: pd = (w1 >> 16) & 0xFFFF
            elif op == 0x3C: cmb = w1
            elif op == 0x3D: tex = w1 & 0xFFFFFF
            elif op == 0x29:
                yield cur; cur = []
            a += n
        carry = buf[a:]

def runs(fr):
    o = []
    for i, t in enumerate(fr):
        if o and o[-1][1] == t[1] and (o[-1][2] == t[0]):
            r = o[-1]; r[3] += 1; r[4] = min(r[4], t[6]); r[5] = max(r[5], t[7]); r[6] = min(r[6], t[4]); r[7] = max(r[7], t[5])
            if t[8] is not None: r[8] = t[8] if r[8] is None else min(r[8], t[8]); r[9] = t[8] if r[9] is None else max(r[9], t[8])
        else: o.append([i, t[1], t[0], 1, t[6], t[7], t[4], t[5], t[8], t[8]])
    return o

def show(k, fr, cap=60):
    print(f'frame {k} prims {len(fr)}')
    for r in runs(fr)[:cap]:
        m = r[1]; zf = ('c' if m & 0x10 else '-') + ('u' if m & 0x20 else '-')
        print(f'  {r[0]:6d} {m:08X} {zf} op{r[2]:02X} n{r[3]:5d} y {r[4]:7.1f}..{r[5]:7.1f} x {r[6]:8.1f}..{r[7]:8.1f} z {r[8]}..{r[9]}')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('dump'); ap.add_argument('--tail-gb', type=float, default=2.0)
    ap.add_argument('--frames', default=''); ap.add_argument('--min-tris', type=int, default=200); ap.add_argument('--cap', type=int, default=60)
    a = ap.parse_args()
    f = open(a.dump, 'rb'); sz = os.path.getsize(a.dump); st = max(0, sz - int(a.tail_gb * 1e9)); f.seek(st); b = f.read(1 << 22); f.seek(st + b.find(b'PRDP'))
    F = [x for x in frames(f)]
    print('frames', len(F))
    lo, hi, step = (int(x) for x in a.frames.split(':')) if a.frames else (0, len(F), max(1, len(F) // 8))
    for k in range(lo, min(hi, len(F)), step):
        if len(F[k]) >= a.min_tris: show(k, F[k], a.cap)
