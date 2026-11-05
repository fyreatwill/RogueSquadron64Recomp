#!/usr/bin/env python3
"""s6894 G5b: for one swap of a ROGUESQ_G5B_TRIS stream, list in draw order every triangle whose hull covers a screen point.
KNOWN LIMIT: same hull test as g5b_cover_map, it can miss triangles, so a short stack proves nothing.
usage: g5b_point_stack.py <tris.bin> <swap> <x> <y> [x y ...]"""
import sys, struct, mmap
F = open(sys.argv[1], 'rb'); d = mmap.mmap(F.fileno(), 0, access=mmap.ACCESS_READ); want = int(sys.argv[2])
pts = [(float(sys.argv[i]), float(sys.argv[i+1])) for i in range(3, len(sys.argv), 2)]
M = b'\xf5\xf5\xf5\xf5'; p = d.find(M); a = b = None
while p >= 0:
    q = struct.unpack_from('<I', d, p + 12)[0]; n = d.find(M, p + 16)
    if q == want: a, b = p + 16, (n if n > 0 else len(d)); break
    p = n
def inside(c, x, y):
    s = 0; 
    for k in range(5):
        x0, y0, x1, y1 = c[2*k]/4, c[2*k+1]/4, c[(2*k+2)%10]/4, c[(2*k+3)%10]/4
        cr = (x1-x0)*(y-y0)-(y1-y0)*(x-x0)
        if abs(cr) < 1e-9: continue
        if s == 0: s = 1 if cr > 0 else -1
        elif (cr > 0) != (s > 0): return False
    return True
N = (b - a) // 32
print('swap', want, 'tris', N)
for x, y in pts:
    print('point', x, y); hits = []
    for i in range(N):
        op, _, cw, tm, z = struct.unpack_from('<BBHII', d, a + i*32); c = struct.unpack_from('<10h', d, a + i*32 + 12)
        if inside(c, x, y): hits.append((i, op, cw, tm, z))
    print('  hits', len(hits)); 
    for h in hits[:6] + hits[-6:]: print('   i=%d op=%02X cw=%d timg=%08X z=%08X' % h)
