# s7138: for every RAM snapshot of a G5B capture, walk the 16 sky objects' DLs (obj+0x34), decode VTX (0x04, 8 B/vertex s16 xyz)
# and TRI2 (0xB4, 16 B, 4 indices /5) quads, and count quads with zero 3D area. usage: cap [S hex]
import struct, sys, array
cap = sys.argv[1]; S = int(sys.argv[2], 16) if len(sys.argv) > 2 else None  # None: locate per snapshot
f = open(cap, 'rb'); s = None
def area(a, b, c):
    u = [b[i]-a[i] for i in range(3)]; v = [c[i]-a[i] for i in range(3)]
    x = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]); return (x[0]**2+x[1]**2+x[2]**2) ** 0.5 / 2
while True:
    t = f.read(4)
    if len(t) < 4: break
    t = struct.unpack('<I', t)[0]
    if t == 0x50415753: m, s = struct.unpack('<QI', f.read(12)); continue
    if t == 0x20474E52: lo, n = struct.unpack('<II', f.read(8)); f.seek(n, 1); continue
    if t != 0x204D4152: break
    a = array.array('I', f.read(0x1000000)); a.byteswap(); r = a.tobytes()
    W = lambda x: struct.unpack('>I', r[x & 0xFFFFFF:(x & 0xFFFFFF) + 4])[0]
    H = lambda x: struct.unpack('>h', r[x & 0xFFFFFF:(x & 0xFFFFFF) + 2])[0]
    if S is None:  # 16 objects at stride 0x5C whose word 3 is 0x003D0018; S = first object - 0x1C
        i = r.find(struct.pack('>I', 0x003D0018))
        while i != -1 and not all(r[i + 0x5C*k:i + 0x5C*k + 4] == b'\x00\x3d\x00\x18' for k in range(16)): i = r.find(struct.pack('>I', 0x003D0018), i + 4)
        if i == -1: print('swap', s, 'no sky objects'); continue
        S = 0x80000000 + i - 0xC - 0x1C; print('# sky S = %08X, level byte %d, fadeH %d' % (S, r[0x130B40], struct.unpack('>h', r[0x0A05D0 + 0x30*r[0x130B40] + 0x2C:][:2])[0]))
    out = []
    for k in range(16):
        dl = W(S + 0x1C + 0x5C * k + 0x34); p = dl; vs = []; q = z = 0; ys = set()
        for _ in range(200):
            w0 = W(p); op = w0 >> 24
            if op == 0xB8: break
            if op == 0x04:
                va = W(p + 4); vs = [(H(va + 8*i), H(va + 8*i + 2), H(va + 8*i + 4)) for i in range(((w0 & 0xFF) + 1) // 8)]; ys |= {v[1] for v in vs}
            if op == 0xB4:
                w1 = W(p + 4); idx = [((w1 >> sh) & 0xFF) // 5 for sh in (24, 16, 8, 0)]
                if max(idx) < len(vs):
                    q += 1; A = area(vs[idx[0]], vs[idx[1]], vs[idx[2]]) + area(vs[idx[0]], vs[idx[2]], vs[idx[3]]); z += A == 0
                p += 8
            p += 8
        out.append('%d:%d/%d%s' % (k, z, q, '' if k < 8 else ' y%s' % sorted(ys)))
    print('swap', s, 'zero-area/quads', ' '.join(out[8:]), '| sectors', ' '.join(out[:8]))
