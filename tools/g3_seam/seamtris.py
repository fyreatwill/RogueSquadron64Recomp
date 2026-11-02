# s6793: in one frame, every tri with a tall edge within X+-1.5, plus RDP-exact per-scanline coverage of the column
# band around X: for each scanline y (centre y+0.5... RDP samples at 4 subscanlines), which tris cover pixel columns
# X-2..X+2 (pixel covered if span start <= col and col < span end, using the edge x at the scanline's y). Args:
# retail|port DUMP FRAME X
import struct, sys
kind, path, fr, X = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
H, lofs = (20, 12) if kind == 'retail' else (16, 8)
sx = lambda v: (v - (1 << 32) if v & 0x80000000 else v) / 65536.0
sy = lambda v: (v - (1 << 14) if v & 0x2000 else v) / 4.0
f = open(path, 'rb'); carry = b''; ci = 0; idx = 0; anyc = False; tris = []; prim = 0; om = 0
while idx <= fr:
    h = f.read(H)
    if len(h) < H: break
    ln = struct.unpack_from('<I', h, lofs)[0]; buf = carry + f.read(ln); p = 0; n_ = len(buf)
    while p + 8 <= n_:
        w0, w1 = struct.unpack_from('<II', buf, p); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); anyc = True
            if p + n > n_: break
            if idx == fr: tris.append((struct.unpack_from('<8I', buf, p), op, prim, om, len(tris)))
        elif op in (0x24, 0x25): n = 16; anyc = True
        elif op == 0x36: anyc = True
        elif op == 0x3A: prim = w1
        elif op == 0x2F: om = (w0 & 0xFFFFFF, w1)
        elif op == 0x3F: ci = (w0 & 0x3FF) + 1
        elif op == 0x29:
            if anyc: idx += 1
            anyc = False
        if p + n > n_: break
        p += n
    carry = buf[p:]
def span(w, y):
    lft = (w[0] >> 23) & 1
    yl, ym, yh = sy(w[0] & 0x3FFF), sy((w[1] >> 16) & 0x3FFF), sy(w[1] & 0x3FFF)
    if not (yh <= y < yl): return None
    yhi = int(yh)  # RDP: edges start at the integer scanline of yh
    xh = sx(w[4]) + sx(w[5]) * (y - yhi); xm = sx(w[6]) + sx(w[7]) * (y - yhi) if y < ym else sx(w[2]) + sx(w[3]) * (y - ym)
    return (xm, xh) if lft else (xh, xm)
print(kind, 'frame', fr, 'ci', ci, 'tris', len(tris))
sel = []
for w, op, pr, om, k in tris:
    yl, yh = sy(w[0] & 0x3FFF), sy(w[1] & 0x3FFF)
    for y in (yh + 20, (yh + yl) / 2, yl - 20):
        s = span(w, y)
        if s and (abs(s[0] - X) < 1.5 or abs(s[1] - X) < 1.5) and yl - yh >= 100: sel.append((w, op, pr, om, k)); break
for w, op, pr, om, k in sel:
    print(' tri#%d op%02X prim=%08X om=%s lft=%d y=%.2f..%.2f..%.2f xh=%.4f dxh=%.6f xm=%.4f dxm=%.6f xl=%.4f dxl=%.6f' % (k, op, pr, om, (w[0] >> 23) & 1,
          sy(w[1] & 0x3FFF), sy((w[1] >> 16) & 0x3FFF), sy(w[0] & 0x3FFF), sx(w[4]), sx(w[5]), sx(w[6]), sx(w[7]), sx(w[2]), sx(w[3])))
# per-scanline: covered columns around X (RDP: pixel col c covered when start <= c+? we report raw span ends)
ys = sorted(set(int(y) for w, *_ in sel for y in (sy(w[1] & 0x3FFF) + 30, sy(w[0] & 0x3FFF) - 30)))
for y in ys[:4]:
    print('  y=%d' % y, ['#%d %.3f-%.3f' % (k, *span(w, y + 0.0)) for w, op, pr, om, k in sel if span(w, y + 0.0)])
