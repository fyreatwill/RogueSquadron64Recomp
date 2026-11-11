# s7136: per band tri (op E, om 002C..) the shade RGBA at its 3 vertices, plus every SetFillColor (0x37) / FillRect (0x36) in order
import struct, sys
cap, want = sys.argv[1], int(sys.argv[2]); f = open(cap, 'rb'); act = False; om = 0; i = 0; fill = None; cimg = 0
def s32(v): return v - (1 << 32) if v & 0x80000000 else v
while True:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753:
        _, sw = struct.unpack('<QI', f.read(12))
        if sw > want: break
        act = sw == want; continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if not act: f.seek(n, 1); continue
    c = f.read(n); a = 0; rw = lambda o: struct.unpack('<I', c[o:o + 4])[0]
    while a + 8 <= n:
        w0 = rw(a); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): l = 16
        if op == 0x3F: cimg = rw(a+4) & 0xFFFFFF
        if op == 0x2F: om = ((w0 & 0xFFFFFF) << 32) | rw(a + 4)
        if op == 0x37: fill = rw(a+4)
        if op == 0x36: w1 = rw(a+4); print('FILLRECT cimg %06X fill %08X' % (cimg, fill), (w1 >> 14) & 0x3FF, (w1 >> 2) & 0x3FF, (w0 >> 14) & 0x3FF, (w0 >> 2) & 0x3FF, 'before band tri', i)
        if 8 <= op <= 15:
            if op & 4:
                w1 = rw(a+4); sx = lambda v, b: (v & ((1 << b) - 1)) - ((1 << b) if v & (1 << (b - 1)) else 0)
                yl = sx(w0, 14)/4; ym = sx(w1 >> 16, 14)/4; yh = sx(w1, 14)/4; y0 = int(yh)
                XL = s32(rw(a+8))/65536; XH, DXH = s32(rw(a+16))/65536, s32(rw(a+20))/65536
                sb = a + 32
                def coef(io):  # 4 channels r g b a, int words io, io+4; frac at io+16, io+20
                    vals = []
                    for wi in (0, 4):
                        hi = rw(sb+io+wi); fr = rw(sb+io+16+wi)
                        vals += [s32(((hi >> 16) << 16 | (fr >> 16)) & 0xFFFFFFFF)/65536, s32(((hi & 0xFFFF) << 16 | (fr & 0xFFFF)) & 0xFFFFFFFF)/65536]
                    return vals
                C = coef(0); DX = coef(8); DE = coef(32)
                def at(x, y): xe = XH + DXH*(y - y0); return [C[j] + DE[j]*(y - y0) + DX[j]*(x - xe) for j in range(4)]
                V = [(XH, yh), (XL, ym), (XH + DXH*(yl - y0), yl)]
                vv = [at(x, y) for x, y in V]
                if min(v[3] for v in vv) < 250: print('fade#%d op%X om %014X' % (i, op, om), ' '.join('(%.0f,%.0f rgba %s)' % (x, y, ','.join('%.0f' % v for v in at(x, y))) for x, y in V))
            i += 1
        a += l
