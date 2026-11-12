#!/usr/bin/env python3
"""s7182: per-triangle RDP state for tris whose screen bbox overlaps a box, in one swap of a G5B capture.
Prints the state groups (combine, othermode, prim/env/blend/fog colour, tile fmt) and per-group tri count + shade colour range.
usage: s7182_tristate.py cap swap x0,y0,x1,y1 [--all]"""
import struct, sys, collections
cap, swap = sys.argv[1], int(sys.argv[2]); bx = list(map(float, sys.argv[3].split(','))); ALL = '--all' in sys.argv
def s(v, b): return v - (1 << b) if v & (1 << (b - 1)) else v
def comb(w0, w1):
    return dict(c0=('a%d b%d c%d d%d' % ((w0 >> 20) & 15, (w1 >> 28) & 15, (w0 >> 15) & 31, (w1 >> 15) & 7)),
                a0=('a%d b%d c%d d%d' % ((w0 >> 12) & 7, (w1 >> 12) & 7, (w0 >> 9) & 7, (w1 >> 9) & 7)),
                c1=('a%d b%d c%d d%d' % ((w0 >> 5) & 15, (w1 >> 24) & 15, w0 & 31, (w1 >> 6) & 7)),
                a1=('a%d b%d c%d d%d' % ((w1 >> 21) & 7, (w1 >> 3) & 7, (w1 >> 18) & 7, w1 & 7)))
def om(w0, w1):
    cyc = ['1cyc', '2cyc', 'copy', 'fill'][(w0 >> 20) & 3]
    bl = '%d%d%d%d/%d%d%d%d' % ((w1 >> 30) & 3, (w1 >> 26) & 3, (w1 >> 22) & 3, (w1 >> 18) & 3, (w1 >> 28) & 3, (w1 >> 24) & 3, (w1 >> 20) & 3, (w1 >> 16) & 3)
    fl = [n for b, n in ((14, 'force_blend'), (13, 'alpha_cvg_sel'), (12, 'cvg_x_alpha'), (7, 'color_on_cvg'), (6, 'img_read'), (5, 'z_upd'), (4, 'z_cmp'), (3, 'aa'), (1, 'alpha_cmp'), (0, 'zsrc_prim'), (2, 'dither_alpha')) if w1 >> b & 1]
    return '%s bl=%s cvgdst=%d zmode=%d %s tf=%d tlut=%d rgbdith=%d adith=%d persp=%d' % (cyc, bl, (w1 >> 8) & 3, (w1 >> 10) & 3, ','.join(fl), (w0 >> 12) & 3, (w0 >> 14) & 3, (w0 >> 6) & 3, (w0 >> 4) & 3, (w0 >> 19) & 1)
f = open(cap, 'rb'); cur = None; st = {}; groups = collections.OrderedDict(); ntri = 0
done = False
while not done:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753:
        _, cur = struct.unpack('<QI', f.read(12))
        if cur > swap: break
        continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if cur != swap: f.seek(n, 1); continue
    c = f.read(n); a = 0
    while a + 8 <= n:
        w0, w1 = struct.unpack('>II', c[a:a + 8]) if False else struct.unpack('<II', c[a:a + 8]); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15:
            l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0); ntri += 1
            W = struct.unpack('<%dI' % (l // 4), c[a:a + l])
            yl, ym, yh = s(W[0] & 0x3FFF, 14) / 4, s((W[1] >> 16) & 0x3FFF, 14) / 4, s(W[1] & 0x3FFF, 14) / 4
            xl, xh, xm = s(W[2], 32) / 65536, s(W[4], 32) / 65536, s(W[6], 32) / 65536
            dh, dm, dl = s(W[5], 32) / 65536, s(W[7], 32) / 65536, s(W[3], 32) / 65536
            xs = [xh, xm, xh + dh * (yl - yh), xm + dm * (ym - yh), xl, xl + dl * (yl - ym)]
            x0, x1 = min(xs), max(xs)
            if not (x1 < bx[0] or x0 > bx[2] or yl < bx[1] or yh > bx[3]) or ALL:
                sh = None
                if op & 4:
                    S = W[8:24]
                    sh = tuple(((S[i // 2] >> (16 if i % 2 == 0 else 0)) & 0xFFFF) for i in range(4))
                    sh = tuple(v - 65536 if v > 32767 else v for v in sh)
                key = (op, st.get('comb'), st.get('om'), st.get('prim'), st.get('env'), st.get('blend'), st.get('fog'), st.get('tile'))
                g = groups.setdefault(key, [0, [], 1e9, -1e9, 1e9, -1e9, a])
                g[0] += 1; g[2] = min(g[2], x0); g[3] = max(g[3], x1); g[4] = min(g[4], yh); g[5] = max(g[5], yl)
                if sh: g[1].append(sh)
        elif op in (0x24, 0x25): l = 16
        elif op == 0x3C: st['comb'] = str(comb(w0, w1))
        elif op == 0x2F: st['om'] = om(w0, w1)
        elif op == 0x3A: st['prim'] = 'prim %08X lod %02X minlod %02X' % (w1, w0 & 0xFF, (w0 >> 8) & 0x1F)
        elif op == 0x3B: st['env'] = 'env %08X' % w1
        elif op == 0x39: st['blend'] = 'blend %08X' % w1
        elif op == 0x38: st['fog'] = 'fog %08X' % w1
        elif op == 0x35 and ((w1 >> 24) & 7) == 0: st['tile'] = 'tile0 fmt%d siz%d line%d pal%d' % ((w0 >> 21) & 7, (w0 >> 19) & 3, (w0 >> 9) & 0x1FF, (w1 >> 20) & 15)
        a += l
print('swap', swap, 'tris', ntri, 'groups', len(groups))
for k, g in groups.items():
    print('--- op%02X n=%d bbox x %.0f-%.0f y %.0f-%.0f @%d' % (k[0], g[0], g[2], g[3], g[4], g[5], g[6]))
    for v in k[1:]: print('   ', v)
    if g[1]:
        print('    shade RGBA min', tuple(min(x[i] for x in g[1]) for i in range(4)), 'max', tuple(max(x[i] for x in g[1]) for i in range(4)))
