#!/usr/bin/env python3
"""s6922 G5h: read a port RDP dump (RS64_RDP_BIN_PORT, records PRDP lo len vi + words) and print what each frame draws, in order.
A frame starts at each SET_COLOR_IMAGE of the main buffer (width >= MINW). Per frame: mode groups (blender word, combiner, tris, rects, y span, x span).
  g5h_rdp_groups.py BIN census           one line per frame: vi, colour image, sky seen before first terrain fog mode, fog/melt tris, fill clears
  g5h_rdp_groups.py BIN frame N          group list of frame N
  g5h_rdp_groups.py BIN cover N X Y W H  per frame N, the groups that touch the box X Y W H (frame pixels), with pixels touched
  g5h_rdp_groups.py BIN pix N X Y        per frame N, every triangle covering pixel X Y in draw order: index, mode, texture, shade RGBA there
  g5h_rdp_groups.py BIN alpha N          per frame N, per mode: tris, and the share of tris by shade alpha at the top vertex
Words sit in the dump as native little-endian u32."""
import struct, sys
SKY, FOG, MELT = 0x00552224, 0xC811, 0x1200
LEN = lambda op: (32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)) if 8 <= op <= 15 else 16 if op in (0x24, 0x25) else 8
def records(p):
    f = open(p, 'rb')
    while True:
        h = f.read(16)
        if len(h) < 16: return
        m, lo, n, vi = struct.unpack('<IIII', h)
        assert m == 0x50445250, hex(f.tell())
        yield lo, vi, f.read(n)
def cmds(p):
    pend = b''; pvi = 0
    for lo, vi, b in records(p):
        b = pend + b; a = 0; n = len(b)
        while a + 8 <= n:
            w0, w1 = struct.unpack_from('<II', b, a); op = (w0 >> 24) & 0x3F; l = LEN(op)
            if a + l > n: break
            yield vi, op, w0, w1, b, a
            a += l
        pend = b[a:]
def s14(v): return ((v & 0x3FFF) ^ 0x2000) - 0x2000
def fx(v): return (v ^ 0x80000000) - 0x80000000 if v else 0
def tri_rows(b, a):
    """yield (y, x0, x1) in whole pixels for an RDP edge triangle"""
    w0, w1 = struct.unpack_from('<II', b, a)
    lft = (w0 >> 23) & 1; yl = s14(w0) / 4; ym = s14(w1 >> 16) / 4; yh = s14(w1) / 4
    xl, dl, xh, dh, xm, dm = [fx(v) / 65536 for v in struct.unpack_from('<6I', b, a + 8)]
    y0 = int(yh // 1) ; y1 = int(yl + .999)
    for y in range(max(y0, 0), min(y1, 1200)):
        yy = y + .5
        if yy < yh or yy >= yl: continue
        x_h = xh + dh * (yy - yh)
        x_o = xm + dm * (yy - yh) if yy < ym else xl + dl * (yy - ym)
        p, q = (x_h, x_o) if not lft else (x_o, x_h)
        p, q = min(p, q), max(p, q)
        yield y, p, q
def shade_at(b, a, x, y):
    """shade r,g,b,a at pixel x y for a shaded triangle"""
    w0, w1 = struct.unpack_from('<II', b, a); yh = s14(w1) / 4
    xh, dh = [fx(v) / 65536 for v in struct.unpack_from('<2I', b, a + 16)]
    o = a + 32; W = struct.unpack_from('<16I', b, o); out = []
    for i in range(4):
        def c(wi, wf):
            sh = 16 if i % 2 == 0 else 0; k = i // 2
            hi = (W[wi + k] >> sh) & 0xFFFF; lo = (W[wf + k] >> sh) & 0xFFFF
            return ((hi ^ 0x8000) - 0x8000) + lo / 65536
        v, dx, de = c(0, 4), c(2, 6), c(8, 12)
        out.append(v + (y - yh) * de + (x - (xh + dh * (y - yh))) * dx)
    return out
def frames(p, minw):
    cur = None; om = 0; cc = 0; fill = 0; ci = (0, 0); timg = 0
    for vi, op, w0, w1, b, a in cmds(p):
        if op == 0x3F:
            ci = (w1 & 0xFFFFFF, (w0 & 0xFFF) + 1)
            if ci[1] >= minw and (cur is None or cur['ci'] != ci or cur['n']):
                if cur: yield cur
                cur = dict(vi=vi, ci=ci, g=[], n=0)
            elif cur: cur['g'].append(['ci', ci[0], ci[1], 0, 0, 1e9, -1e9, 1e9, -1e9, None])
            continue
        if cur is None: continue
        if op == 0x2F: om = w1; hi = w0; cur.setdefault('hi', hi); continue
        if op == 0x3C: cc = (w0 & 0xFFFFFF, w1); continue
        if op == 0x37: fill = w1; continue
        if op == 0x3D: timg = w1; continue
        if 8 <= op <= 15 or op in (0x24, 0x25, 0x36):
            g = cur['g']
            if not g or g[-1][0] != 'd' or g[-1][1] != om or g[-1][2] != cc: g.append(['d', om, cc, 0, 0, 1e9, -1e9, 1e9, -1e9, []])
            q = g[-1]; cur['n'] += 1
            if 8 <= op <= 15:
                q[3] += 1; rows = list(tri_rows(b, a))
                q[9].append(rows); cur.setdefault('t', []).append((om, cc, timg, op, bytes(b[a:a + LEN(op)]), rows))
                for y, x0, x1 in rows: q[5] = min(q[5], y); q[6] = max(q[6], y); q[7] = min(q[7], x0); q[8] = max(q[8], x1)
            else:
                q[4] += 1
                x1 = ((w0 >> 12) & 0xFFF) / 4; y1 = (w0 & 0xFFF) / 4; x0 = ((w1 >> 12) & 0xFFF) / 4; y0 = (w1 & 0xFFF) / 4
                q[9].append([(y, x0, x1) for y in range(int(y0), int(y1) + 1)])
                q[5] = min(q[5], y0); q[6] = max(q[6], y1); q[7] = min(q[7], x0); q[8] = max(q[8], x1)
                if op == 0x36: q.append(fill)
    if cur: yield cur
def main():
    p, cmd = sys.argv[1], sys.argv[2]; minw = 300
    if cmd == 'census':
        for i, f in enumerate(frames(p, minw)):
            sky = fog = melt = nfirst = 0; first = None; fills = 0
            for g in f['g']:
                if g[0] != 'd': continue
                k = g[1] >> 16
                if g[1] == SKY: sky += g[3] + g[4]
                if k in (FOG, MELT):
                    fog += g[3] * (k == FOG); melt += g[3] * (k == MELT)
                    if first is None: first = sky
                if g[4] and len(g) > 10: fills += 1
            print(i, 'vi', f['vi'], 'ci %06X w%d' % f['ci'], 'n', f['n'], 'sky', sky, 'skyBeforeFog', first, 'fog', fog, 'melt', melt, 'fills', fills)
    else:
        N = int(sys.argv[3])
        for i, f in enumerate(frames(p, minw)):
            if i != N: continue
            if cmd == 'pix':
                X, Y = int(sys.argv[4]), int(sys.argv[5])
                for k, (o, c, ti, op, tb, rows) in enumerate(f.get('t', [])):
                    for y, a, b2 in rows:
                        if y == Y and a <= X < b2:
                            sh = ['%.0f' % v for v in shade_at(tb, 0, X + .5, Y + .5)] if op & 4 else '-'
                            print(k, 'op %02X om %08X cc %08X tex %08X shade' % (op, o, c[1] if c else 0, ti), sh)
                break
            if cmd == 'alpha':
                import collections
                d = collections.defaultdict(collections.Counter)
                for o, c, ti, op, tb, rows in f.get('t', []):
                    if op & 4 and rows: d[o, c[1] if c else 0][min(int(shade_at(tb, 0, rows[0][1], rows[0][0] + .5)[3]) // 64, 4)] += 1
                for k, v in d.items(): print('%08X %08X' % k, dict(sorted(v.items())))
                break
            box = [int(v) for v in sys.argv[4:8]] if cmd == 'cover' else None
            print('frame', i, 'vi', f['vi'], 'ci %06X w%d' % f['ci'])
            for g in f['g']:
                if g[0] == 'ci': print('  ci %06X w%d' % (g[1], g[2])); continue
                hit = ''
                if box:
                    x, y, w, h = box; px = 0
                    for rows in g[9]:
                        for yy, a, b2 in rows:
                            if y <= yy < y + h: px += max(0, min(b2, x + w) - max(a, x))
                    if not px: continue
                    hit = ' px %.0f' % px
                print('  om %08X cc %06X %08X tri %d rect %d y %.0f-%.0f x %.0f-%.0f%s%s' % (g[1], g[2][0] if g[2] else 0, g[2][1] if g[2] else 0, g[3], g[4], g[5], g[6], g[7], g[8], hit, ' fill %08X' % g[10] if len(g) > 10 else ''))
            break
main()
