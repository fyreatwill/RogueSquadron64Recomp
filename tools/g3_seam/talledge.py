# s6793: per 640-wide frame, the x (0.25 px) of every near-vertical triangle edge taller than MINH px, in the
# x window 280..360; writes idx<TAB>stamp<TAB>x:h,... Args: retail|port DUMP LO HI OUT
import struct, sys
kind, path, lo, hi, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
H, lofs = (20, 12) if kind == 'retail' else (16, 8); MINH = 120
sx = lambda v: (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
sy = lambda v: (v - (1 << 14) if v & 0x2000 else v) / 4.0
f = open(path, 'rb'); o = open(out, 'w'); carry = b''; ci = 0; idx = 0; anyc = False; cur = []; stamp = 0
while idx < hi:
    h = f.read(H)
    if len(h) < H: break
    ln = struct.unpack_from('<I', h, lofs)[0]; stamp = struct.unpack_from('<I', h, H - 4)[0]
    buf = carry + f.read(ln); p = 0; n_ = len(buf)
    while p + 8 <= n_:
        w0, w1 = struct.unpack_from('<II', buf, p); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); anyc = True
            if p + n > n_: break
            if lo <= idx < hi and ci == 640:
                w = struct.unpack_from('<8I', buf, p)
                yl, ym, yh = sy(w[0] & 0x3FFF), sy((w[1] >> 16) & 0x3FFF), sy(w[1] & 0x3FFF)
                for x0, d, ya, yb in ((sx(w[4]), sx(w[5]), yh, yl), (sx(w[6]), sx(w[7]), yh, ym), (sx(w[2]), sx(w[3]), ym, yl)):
                    hgt = yb - ya
                    if hgt >= MINH and abs(d) * hgt < 3 and 280 <= x0 <= 360:
                        cur.append('%.2f:%d:%d' % (x0, ya, hgt))
        elif op in (0x24, 0x25): n = 16; anyc = True
        elif op == 0x36: anyc = True
        elif op == 0x3F: ci = (w0 & 0x3FF) + 1
        elif op == 0x29:
            if anyc:
                if lo <= idx < hi and cur: o.write('%d\t%d\t%s\n' % (idx, stamp, ','.join(cur)))
                idx += 1
            anyc = False; cur = []
        if p + n > n_: break
        p += n
    carry = buf[p:]
o.close()
