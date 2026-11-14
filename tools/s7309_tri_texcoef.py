#!/usr/bin/env python3
"""s7309 G5f: decode the RDP triangle commands of one swap of a ROGUESQ_G5B_FRAME capture and print, per textured triangle, the edge
vertices (YH/YM/YL, XH/XM/XL) and the texture coefficients S,T,W at the start point with their x and edge(e)/y derivatives (s15.16 ->
float). Triangle index counts every 0x08-0x0F command in the swap, the same order as the G5B_TRIS stream (g5b_point_stack.py).
usage: s7309_tri_texcoef.py cap.bin swap idx[,idx...]   (idx 'all' = every textured tri)"""
import sys, struct
cap, want = sys.argv[1], int(sys.argv[2]); sel = sys.argv[3]
f = open(cap, 'rb'); cur = None; rngs = []
while True:
    h = f.read(4)
    if len(h) < 4: break
    if h == b'SWAP': _, cur = struct.unpack('<QI', f.read(12))
    elif h == b'RAM ': f.seek(16 << 20, 1)
    elif h == b'RNG ':
        lo, ln = struct.unpack('<II', f.read(8)); b = f.read(ln)
        if cur == want: rngs.append(b)
    else: break
def s16(v): return v - 65536 if v & 0x8000 else v
def fx(i, fr): return s16(i) + fr / 65536.0
LEN = {0x08: 32, 0x09: 48, 0x0A: 96, 0x0B: 112, 0x0C: 96, 0x0D: 112, 0x0E: 160, 0x0F: 176}
n = 0; out = []
for b in rngs:
    a = 0
    while a + 8 <= len(b):
        w0, = struct.unpack_from('<I', b, a); op = (w0 >> 24) & 0x3F  # RDRAM words, host order
        if op in LEN and a + LEN[op] <= len(b):
            W = struct.unpack_from('<%dI' % (LEN[op] // 4), b, a)
            yl = ((W[0] & 0x3FFF) << 18 >> 18) / 4; ym = (((W[1] >> 16) & 0x3FFF) << 18 >> 18) / 4; yh = ((W[1] & 0x3FFF) << 18 >> 18) / 4
            sx = lambda v: (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
            xl, dxl, xh, dxh, xm, dxm = sx(W[2]), sx(W[3]), sx(W[4]), sx(W[5]), sx(W[6]), sx(W[7])
            row = dict(i=n, op=op, y=(yh, ym, yl), x=(xh, dxh, xm, dxm, xl, dxl))
            if op & 2:
                t0 = 8 + (16 if op & 4 else 0)
                T = W[t0:t0 + 16]
                hi = lambda w: w >> 16; lo = lambda w: w & 0xFFFF
                row['S'] = fx(hi(T[0]), hi(T[4])); row['T'] = fx(lo(T[0]), lo(T[4])); row['W'] = fx(hi(T[1]), hi(T[5]))
                row['dSdx'] = fx(hi(T[2]), hi(T[6])); row['dTdx'] = fx(lo(T[2]), lo(T[6])); row['dWdx'] = fx(hi(T[3]), hi(T[7]))
                row['dSde'] = fx(hi(T[8]), hi(T[12])); row['dTde'] = fx(lo(T[8]), lo(T[12])); row['dWde'] = fx(hi(T[9]), hi(T[13]))
                row['dSdy'] = fx(hi(T[10]), hi(T[14])); row['dTdy'] = fx(lo(T[10]), lo(T[14])); row['dWdy'] = fx(hi(T[11]), hi(T[15]))
            out.append(row); n += 1; a += LEN[op]
        else: a += 8
print('swap', want, 'ranges', len(rngs), 'tris', n)
ids = range(n) if sel == 'all' else [int(x) for x in sel.split(',')]
for i in ids:
    r = out[i]
    if 'S' not in r and sel == 'all': continue
    print('i=%d op=%02X y(h,m,l)=%s x(h,dh,m,dm,l,dl)=%s' % (r['i'], r['op'], r['y'], tuple(round(v, 2) for v in r['x'])))
    if 'S' in r: print('   S=%.2f T=%.2f W=%.4f | dx %.3f %.3f %.5f | de %.3f %.3f %.5f | dy %.3f %.3f %.5f' % tuple(r[k] for k in ('S','T','W','dSdx','dTdx','dWdx','dSde','dTde','dWde','dSdy','dTdy','dWdy')))
