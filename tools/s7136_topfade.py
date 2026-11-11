# s7136: per swap, count tris whose shade at some vertex is ~(168,152,128) (the sky top-bin vertex colour A89880xx)
import struct, sys
cap, a, b, step = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); f = open(cap, 'rb'); act = False; cnt = {}; om = 0
def s32(v): return v - (1 << 32) if v & 0x80000000 else v
while True:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753:
        _, sw = struct.unpack('<QI', f.read(12))
        if sw > b: break
        act = a <= sw <= b and (sw - a) % step == 0; cnt.setdefault(sw, [0, 0]) if act else None; continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if not act: f.seek(n, 1); continue
    c = f.read(n); p = 0; rw = lambda o: struct.unpack('<I', c[o:o + 4])[0]
    while p + 8 <= n:
        w0 = rw(p); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): l = 16
        if 8 <= op <= 15 and op & 4 and p + l <= n:
            hi0 = rw(p + 32); hi1 = rw(p + 36); r_ = s32(hi0) >> 16; g_ = (hi0 & 0xFFFF); b_ = s32(hi1) >> 16; al = hi1 & 0xFFFF
            if abs(r_ - 168) <= 6 and abs(g_ - 152) <= 6 and abs(b_ - 128) <= 6: cnt[sw][0] += 1
            cnt[sw][1] += 1
        p += l
for s in sorted(cnt): print(s, 'topfade-colour tris', cnt[s][0], 'of shaded', cnt[s][1])
