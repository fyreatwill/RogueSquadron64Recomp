#!/usr/bin/env python3
"""s6894 G5b: ASCII map of the last painter per screen cell for swaps of a ROGUESQ_G5B_TRIS stream, in draw order.
'.' nothing, 's' op 0E (no Z), 'c' op 0D, 't' op 0F small, '#' op 0F over 40000 px, 'o' other. Cells 20x32 px.
KNOWN LIMIT: the convex hull test misses many sky tris ('.' cells), so '.' does not mean nothing was drawn there.
usage: g5b_cover_map.py <tris.bin> <swap> [swap...]"""
import sys, struct, mmap
F = open(sys.argv[1], 'rb'); d = mmap.mmap(F.fileno(), 0, access=mmap.ACCESS_READ); want = {int(x) for x in sys.argv[2:]}
M = b'\xf5\xf5\xf5\xf5'; p = d.find(M); sw = {}
while p >= 0 and len(sw) < len(want):
    q = struct.unpack_from('<I', d, p + 12)[0]; n = d.find(M, p + 16)
    if q in want: sw[q] = (p + 16, n if n > 0 else len(d))
    p = n
GX, GY = 20, 32; W, H = 796 // GX, 448 // GY
for q in sorted(sw):
    a, b = sw[q]; g = [['.'] * W for _ in range(H)]; N = (b - a) // 32; cnt = {}
    for i in range(N):
        op = d[a + i*32]; c = struct.unpack_from('<10h', d, a + i*32 + 12); P = [(c[2*k]/4, c[2*k+1]/4) for k in range(5)]
        ar = abs(sum(P[k][0]*P[(k+1)%5][1] - P[(k+1)%5][0]*P[k][1] for k in range(5))) / 2
        ch = {0x0E: 's', 0x0D: 'c', 0x0F: '#' if ar > 40000 else 't'}.get(op, 'o'); cnt[ch] = cnt.get(ch, 0) + 1
        xs = [v[0] for v in P]; ys = [v[1] for v in P]
        for gy in range(max(0, int(min(ys) // GY)), min(H, int(max(ys) // GY) + 1)):
            for gx in range(max(0, int(min(xs) // GX)), min(W, int(max(xs) // GX) + 1)):
                x, y = gx * GX + GX / 2, gy * GY + GY / 2; s = 0; ok = True
                for k in range(5):
                    x0, y0 = P[k]; x1, y1 = P[(k+1) % 5]; cr = (x1-x0)*(y-y0)-(y1-y0)*(x-x0)
                    if abs(cr) < 1e-9: continue
                    if s == 0: s = 1 if cr > 0 else -1
                    elif (cr > 0) != (s > 0): ok = False; break
                if ok: g[gy][gx] = ch
    print('swap', q, 'tris', N, cnt)
    for r in g: print(''.join(r))
