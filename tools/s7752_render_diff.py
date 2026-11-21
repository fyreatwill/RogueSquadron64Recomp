#!/usr/bin/env python3
"""s7752: pixel-diff two angrylion renders (tools/s7752_port_task/rdp_render .ram outputs) of the same gfx task.
Attributes every differing 16-bit word to the stream's colour images (SET_COLOR_IMAGE 0x3F, 16 bpp) or Z image (0x3E), using
the stream's widths and the max scissor y as height. Positive control: --ctl flips one pixel in A's colour image and must report 1.
usage: s7752_render_diff.py <stream.rdp|snap.bin> <a.ram> <b.ram> [--ctl]   exit 0 = identical images, 1 = differ"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7751_rdp_compare import load, split

def images(stream):
    cimg, z, h = {}, set(), 0
    for op, c in split(load(stream)):
        w1 = int.from_bytes(c[4:8], 'big'); w0 = int.from_bytes(c[0:4], 'big')
        if op == 0x3F and ((w0 >> 19) & 3) == 2: cimg[w1 & 0xFFFFFF] = (w0 & 0x3FF) + 1
        elif op == 0x3E: z.add(w1 & 0xFFFFFF)
        elif op == 0x2D: h = max(h, ((w1 & 0xFFF) >> 2))
    return cimg, z, h

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('stream'); ap.add_argument('a'); ap.add_argument('b')
    ap.add_argument('--ctl', action='store_true'); o = ap.parse_args()
    A = bytearray(open(o.a, 'rb').read()); B = open(o.b, 'rb').read()
    cimg, z, h = images(o.stream)
    if o.ctl:  # flip one pixel of A's widest colour image (host byte = guest byte ^ 3)
        base, w = max(cimg.items(), key=lambda kv: kv[1]); A[(base + 2 * (w * (h // 2) + w // 2)) ^ 3] ^= 1
    anyd = 0
    wz = max(cimg.values() or [0])
    for kind, regs in (('cimg', sorted(cimg.items())), ('zimg', [(a, wz) for a in sorted(z)])):
        for base, w in regs:
            n = w * h * 2
            if base + n > len(A): continue
            rows = []; cnt = 0; cols = []; mag = [0, 0, 0, 0]
            for off in range(0, n, 4):
                if A[base + off:base + off + 4] != B[base + off:base + off + 4]:
                    for half in (0, 2):  # host half 0 holds guest pixel off+2, half 2 holds guest pixel off
                        if A[base + off + half:base + off + half + 2] != B[base + off + half:base + off + half + 2]:
                            g = (off + (2 - half)) // 2; cnt += 1; rows.append(g // w); cols.append(g % w)
                            if kind == 'cimg':
                                va = A[base + off + half] | A[base + off + half + 1] << 8; vb = B[base + off + half] | B[base + off + half + 1] << 8
                                dm = max(abs((va >> sh & 31) - (vb >> sh & 31)) for sh in (11, 6, 1))
                                mag[0 if dm <= 1 else 1 if dm <= 3 else 2 if dm <= 7 else 3] += 1
            print(f'{kind} {base:06X} w={w} h={h}: differing px={cnt} of {w*h}' + (f' rows {min(rows)}-{max(rows)} cols {min(cols)}-{max(cols)}' if cnt else '') + (f' max-channel-delta(5bit) <=1:{mag[0]} 2-3:{mag[1]} 4-7:{mag[2]} >=8:{mag[3]}' if kind == 'cimg' and cnt else ''))
            anyd += cnt
    print(f'total differing px={anyd}')
    return 1 if anyd else 0

if __name__ == '__main__':
    sys.exit(main())
