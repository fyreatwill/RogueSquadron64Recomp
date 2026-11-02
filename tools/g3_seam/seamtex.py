# s6793: for frame FR, tris with an edge at X (+-0.6) over y in [Y0,Y1]: tile, tile size, clamp/mirror/mask, and the
# texel S,T (perspective-divided when persp is on) the RDP would sample at pixel centres X-1.5, X-0.5, X+0.5, X+1.5 on y=YM.
import struct, sys
kind, path, fr, X, YM = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
H, lofs = (20, 12) if kind == 'retail' else (16, 8)
sx = lambda v: (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
sy = lambda v: (v - (1 << 14) if v & 0x2000 else v) / 4.0
f = open(path, 'rb'); carry = b''; idx = 0; anyc = False; tiles = {}; tsz = {}; om = (0, 0); res = []; ti = {}
while idx <= fr:
    h = f.read(H)
    if len(h) < H: break
    ln = struct.unpack_from('<I', h, lofs)[0]; buf = carry + f.read(ln); p = 0; n_ = len(buf)
    while p + 8 <= n_:
        w0, w1 = struct.unpack_from('<II', buf, p); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); anyc = True
            if p + n > n_: break
            if idx == fr and op & 2:
                w = struct.unpack_from('<%dI' % (n // 4), buf, p)
                yl, ym, yh = sy(w[0] & 0x3FFF), sy((w[1] >> 16) & 0x3FFF), sy(w[1] & 0x3FFF)
                if yh <= YM < yl:
                    yf = int(yh) if yh >= 0 else -int(-yh)  # floor
                    import math; yf = math.floor(yh)
                    xh = sx(w[4]) + sx(w[5]) * (YM - yf)
                    xo = sx(w[6]) + sx(w[7]) * (YM - yf) if YM < ym else sx(w[2]) + sx(w[3]) * (YM - ym)
                    if abs(xh - X) < 0.6 or abs(xo - X) < 0.6:
                        t0 = 8 + (16 if op & 4 else 0)
                        T = w[t0:t0 + 16]
                        fx = lambda i: ((T[i] & 0xFFFF0000) | (T[i + 4] >> 16)) , 
                        def coef(base, k):  # k: 0=s,1=t,2=w ; base word offset in tex block (0 = value, 2 = dx, 8 = de, 10 = dy)
                            hi = T[base + (k // 2)]; lo = T[base + 4 + (k // 2)]
                            v = ((hi >> 16) << 16 | (lo >> 16)) if k % 2 == 0 else ((hi & 0xFFFF) << 16 | (lo & 0xFFFF))
                            return (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
                        S0, T0_, W0 = coef(0, 0), coef(0, 1), coef(0, 2)
                        Sx, Tx, Wx = coef(2, 0), coef(2, 1), coef(2, 2)
                        Se, Te, We = coef(8, 0), coef(8, 1), coef(8, 2)
                        dy = YM - yf
                        out = []
                        for px in (X - 1.5, X - 0.5, X + 0.5, X + 1.5):
                            xs = xh  # attributes are stepped along the major (H) edge then by dx
                            s = S0 + Se * dy + Sx * (px - xh); t = T0_ + Te * dy + Tx * (px - xh); ww = W0 + We * dy + Wx * (px - xh)
                            persp = (om[0] >> 19) & 1
                            if persp and ww: s, t = s / ww * 32768 / 32 , t / ww * 32768 / 32
                            else: s, t = s / 32, t / 32
                            inside = min(xh, xo) <= px < max(xh, xo)
                            out.append('%s%.1f:(%.2f,%.2f)' % ('*' if inside else ' ', px, s, t))
                        tl = (w[0] >> 16) & 7
                        res.append('op%02X tile%d %s size=%s persp=%d edges %.2f..%.2f  %s' % (op, tl, ti.get(tl), tsz.get(tl), (om[0] >> 19) & 1, min(xh, xo), max(xh, xo), ' '.join(out)))
        elif op in (0x24, 0x25): n = 16; anyc = True
        elif op == 0x36: anyc = True
        elif op == 0x2F: om = (w0 & 0xFFFFFF, w1)
        elif op == 0x32: tsz[(w1 >> 24) & 7] = (((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4, ((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4)
        elif op == 0x35: ti[(w1 >> 24) & 7] = 'fmt%d/%d line%d tmem%d cmt%d mt%d cms%d ms%d' % ((w0 >> 21) & 7, (w0 >> 19) & 3, (w0 >> 9) & 0x1FF, w0 & 0x1FF, (w1 >> 18) & 3, (w1 >> 14) & 15, (w1 >> 8) & 3, (w1 >> 4) & 15)
        elif op == 0x29:
            if anyc: idx += 1
            anyc = False
        if p + n > n_: break
        p += n
    carry = buf[p:]
print(kind, fr, 'X', X, 'y', YM)
for r in res: print(' ', r)
