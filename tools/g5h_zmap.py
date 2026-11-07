#!/usr/bin/env python3
"""s6923 G5h: per-pixel depth map of one game frame from a port RDP dump (RS64_RDP_BIN_PORT).
  g5h_zmap.py BIN FRAME_A FRAME_B OUT.png
Replays every z triangle of census frames A..B in draw order against a software z buffer (hardware rule: compare if Z_CMP, write if Z_UPD),
then, for the translucent no-update mode group 00504A50 (or MODE=hex), reports pixels that pass with terrain z written and pixels that
pass only if terrain z is ignored. PNG: red pass both, green pass only without terrain z, blue fail both, grey terrain only."""
import struct, sys, os
from PIL import Image
src = open(os.path.join(os.path.dirname(__file__), 'g5h_rdp_groups.py')).read().replace('\nmain()\n', '\n')
_a = sys.argv; sys.argv = ['x']; exec(src); sys.argv = _a
W, H = 640, 360
def zco(tb, op):
    o = 8 + 24 + (64 if op & 4 else 0) + (64 if op & 2 else 0)
    z, dzdx, dzde, dzdy = [(v ^ 0x80000000) - 0x80000000 for v in struct.unpack_from('<4I', tb, o)]
    return z / 65536, dzdx / 65536, dzde / 65536
def raster(tb, op, rows):
    w0, w1 = struct.unpack_from('<II', tb, 0); yh = s14(w1) / 4
    xh, dh = [fx(v) / 65536 for v in struct.unpack_from('<2I', tb, 16)]
    z, dzdx, dzde = zco(tb, op)
    for y, a, b in rows:
        if not 0 <= y < H: continue
        yy = y + .5; zr = z + (yy - yh) * dzde - (xh + dh * (yy - yh)) * dzdx
        for x in range(max(int(a + .5), 0), min(int(b + .5), W)):
            yield y * W + x, zr + (x + .5) * dzdx
def main2():
    p, A, B, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    mode = int(os.environ.get('MODE', '00504A50'), 16)
    N = W * H; zt = [1e9] * N; zn = [1e9] * N; terr = bytearray(N); pa = bytearray(N); pb = bytearray(N); seen = {}
    for i, f in enumerate(frames(p, 300)):
        if i < A: continue
        if i > B: break
        for o, c, ti, op, tb, rows in f.get('t', []):
            if not op & 1: continue
            zc, zu = bool(o & 0x10), bool(o & 0x20); t = (o >> 16) in (0xC811, 0x1200) and not zc
            s = seen.setdefault('%08X' % o, [0, 1e9, -1e9]); s[0] += 1
            for k, z in raster(tb, op, rows):
                if z < s[1]: s[1] = z
                if z > s[2]: s[2] = z
                if o == mode:
                    if z < zt[k]: pa[k] = 1
                    if z < zn[k]: pb[k] = 1
                if zu:
                    if not zc or z < zt[k]: zt[k] = z
                    if not t and (not zc or z < zn[k]): zn[k] = z
                if t: terr[k] = 1
    for k, v in seen.items(): print(k, 'tris', v[0], 'z %.0f..%.0f' % (v[1], v[2]))
    print('mode pixels pass with terrain z', sum(pa), 'pass only ignoring terrain z', sum(1 for k in range(N) if pb[k] and not pa[k]), 'terrain px', sum(terr))
    im = Image.new('RGB', (W, H)); px = bytearray()
    for k in range(N): px += bytes((220, 40, 40) if pa[k] else (40, 220, 40) if pb[k] else (70, 70, 70) if terr[k] else (0, 0, 0))
    Image.frombytes('RGB', (W, H), bytes(px)).save(out)
main2()
