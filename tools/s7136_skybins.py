# s7136: per swap, the 16 sky-sector objects' (S+0x1C+0x5C*k) +0x30 / +0x34 words and camera yaw/pitch; S found by signature
import struct, sys, math, array
cap, a, b, step = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
f = open(cap, 'rb'); s = None; done = set(); S = None
def find(r):
    A = array.array('I'); A.frombytes(r[:0x800000])
    for i in range(len(A) - 400):
        v = A[i]
        if v >> 24 == 0x80 and A[i+23] == v+0x10 and A[i+46] == v+0x20 and A[i+23*15] == v+0xF0 and v == (0x80000000 | (i*4 + 0x5A0)): return 0x80000000 | (i*4 - 0x3C)
while True:
    t = f.read(4)
    if len(t) < 4: break
    t = struct.unpack('<I', t)[0]
    if t == 0x50415753:
        m, s = struct.unpack('<QI', f.read(12))
        if s > b: break
    elif t == 0x204D4152:
        if s is not None and a <= s <= b and (s - a) % step == 0 and s not in done:
            r = f.read(0x1000000); done.add(s)
            if S is None: S = find(r); print('S', hex(S or 0))
            W = lambda x: struct.unpack('<I', r[x & 0xFFFFFF:(x & 0xFFFFFF)+4])[0]
            Fl = lambda x: struct.unpack('<f', r[x & 0xFFFFFF:(x & 0xFFFFFF)+4])[0]
            P = W(0x138D1C); R = [Fl(P+0x28+4*i) for i in range(9)]; fx, fy, fz = R[2], R[5], R[8]
            st = [W(S + 0x4C + 0x5C*k) for k in range(16)]
            on = ''.join('#' if v > 4 else '.' for v in st[:8]) + ' ' + ''.join('#' if v > 4 else '.' for v in st[8:])
            print(s, 'yaw %.1f pitch %.1f' % (math.degrees(math.atan2(fx, fz)), math.degrees(math.atan2(fy, math.hypot(fx, fz)))), on, ' '.join('%X' % v for v in st[:8]))
        else: f.seek(0x1000000, 1)
    elif t == 0x20474E52: lo, n = struct.unpack('<II', f.read(8)); f.seek(n, 1)
