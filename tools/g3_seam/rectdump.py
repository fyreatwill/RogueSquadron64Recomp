# s6793: list texrects/fillrects with an edge near x=320 in a few 640-wide frames, with cycle type + tex coords
import struct, sys
kind, path, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
H, lofs = (20, 12) if kind == 'retail' else (16, 8)
f = open(path, 'rb'); carry = b''; ci = 0; idx = 0; anyc = False; cyc = 0; out = []; prim = 0; tile = {}
while idx < hi:
    h = f.read(H)
    if len(h) < H: break
    ln = struct.unpack_from('<I', h, lofs)[0]; buf = carry + f.read(ln); p = 0; n_ = len(buf)
    while p + 8 <= n_:
        w0, w1 = struct.unpack_from('<II', buf, p); op = (w0 >> 24) & 0x3F; n = 8
        if 0x08 <= op <= 0x0F:
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); anyc = True
        elif op in (0x24, 0x25):
            n = 16; anyc = True
            if p + n > n_: break
            xl, yl, xh, yh = ((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4, ((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4
            s_, t_, ds, dt = struct.unpack_from('>hhhh', struct.pack('<II', *struct.unpack_from('<II', buf, p + 8))[::-1][::-1], 0) if False else (0, 0, 0, 0)
            v2, v3 = struct.unpack_from('<II', buf, p + 8)
            s_, t_ = (v3 >> 16) - (65536 if v3 & 0x80000000 else 0), (v3 & 0xFFFF) - (65536 if v3 & 0x8000 else 0)
            ds, dt = (v2 >> 16) - (65536 if v2 & 0x80000000 else 0), (v2 & 0xFFFF) - (65536 if v2 & 0x8000 else 0)
            if lo <= idx < hi and ci == 640 and (abs(xl - 320) <= 2 or abs(xh - 320) <= 2):
                out.append((idx, 'TR' if op == 0x24 else 'TRF', cyc, xh, yh, xl, yl, s_ / 32, t_ / 32, ds / 1024, dt / 1024, tile.get((w1 >> 24) & 7)))
        elif op == 0x36:
            anyc = True
            xl, xh = ((w0 >> 12) & 0xFFF) / 4, ((w1 >> 12) & 0xFFF) / 4
            if lo <= idx < hi and ci == 640 and (abs(xl - 320) <= 2 or abs(xh - 320) <= 2):
                out.append((idx, 'FILL', cyc, xh, (w1 & 0xFFF) / 4, xl, (w0 & 0xFFF) / 4))
        elif op == 0x2F: cyc = (w0 >> 20) & 3
        elif op == 0x32 or op == 0x34: pass
        elif op == 0x35: tile[(w1 >> 24) & 7] = ('fmt%d/%d' % ((w0 >> 21) & 7, (w0 >> 19) & 3), 'cms%d' % ((w1 >> 8) & 3), 'masks%d' % ((w1 >> 4) & 15))
        elif op == 0x3F: ci = (w0 & 0x3FF) + 1
        elif op == 0x29:
            if anyc: idx += 1
            anyc = False
        if p + n > n_: break
        p += n
    carry = buf[p:]
fr = sorted(set(o[0] for o in out))
for o in out:
    if o[0] in fr[:2]: print(o)
print('frames', len(fr), 'rects', len(out))
