#!/usr/bin/env python3
"""s6852: classify the texrects the s6159 radar-region shift (rs64_region_scan) selects, from a port RDP bin
(RS64_RDP_BIN_PORT, RS64_RDP_BIN_PORT_VI=1) recorded with ROGUESQ_SHIFT_REGION=0 so positions are the game's own.
Selection mirrors rs64_region_scan exactly: texrect lr (w0 x/y) inside the box; tri bbox centre inside the box and
bbox <= 130 px (the radar disc / sweep wedge = known radar content, the positive control).
Per selected texrect it records the texture image (last G_SETTIMG before it), the rect size, and where it sits in its
submit record relative to the record's region tris (before / inside / after the tri span, commands to nearest tri).
Then, per texture image, it counts uses of the SAME image outside the box on the same colour image:
  H-radar: a HUD texture never drawn elsewhere, emitted next to the disc tris;
  H-world: a texture also drawn at scattered screen positions (a world billboard that crossed the box).
usage: g1d_regiontex.py bin [--box x0,x1,y0,y1] [--cw 1024] [--ring TIMG]
--ring keeps only VIs that also draw that texture (the anchored radar ring, 792DA0 on lvl17 = flight HUD on)."""
import struct, sys, collections
path = sys.argv[1]
box = (669.0, 810.0, 20.0, 135.0); cwant = 1024
if '--box' in sys.argv: box = tuple(map(float, sys.argv[sys.argv.index('--box') + 1].split(',')))
ring = int(sys.argv[sys.argv.index('--ring') + 1], 16) if '--ring' in sys.argv else None
if '--cw' in sys.argv: cwant = int(sys.argv[sys.argv.index('--cw') + 1])
inb = lambda x, y: box[0] <= x <= box[1] and box[2] <= y <= box[3]
sx14 = lambda v: ((v & 0x3FFF) - (0x4000 if v & 0x2000 else 0)) / 4.0
def s32(v): return v - (1 << 32) if v & 0x80000000 else v
tex = collections.defaultdict(lambda: {'in': 0, 'out': 0, 'inx': [1e9, -1e9], 'iny': [1e9, -1e9], 'outx': [1e9, -1e9],
                                       'outy': [1e9, -1e9], 'sz': collections.Counter(), 'vi': [1 << 31, -1], 'outvi': set(),
                                       'rel': collections.Counter(), 'dist': [], 'fmt': None, 'tri_in': 0})
nrec = 0; ntri_box = 0; ntexr_box = 0; recs_with_tri = 0; ci_w = 0; vmin = 1 << 31; vmax = -1
hud_ulx = [1e9, -1e9]; hud_lrx = [1e9, -1e9]; tri_x = [1e9, -1e9]
def upd(r, v): r[0] = min(r[0], v); r[1] = max(r[1], v)
cur_vi = -1; idx = 0; boxr = []; tris = []; pend = []; nflight = 0; nskip = 0; samples = []
firstz = [-1]; zsel = collections.Counter(); gtri = collections.Counter(); gtex = collections.Counter(); gd = collections.defaultdict(list); gdt = collections.defaultdict(list)
timg = (0, 0, 0, 0); om = (0, 0); gop = collections.Counter(); gzr = collections.Counter()
def flush():
    global ntexr_box, recs_with_tri, nflight, nskip
    if not tris or (ring is not None and not any(p[1][0] == ring for p in pend)):
        nskip += 1; return
    nflight += 1; recs_with_tri += 1
    ri = [p[0] for p in pend if ring is not None and p[1][0] == ring]
    for i, op, ti, mn, mx, cy in ptri:
        gop[(ti if op & 2 else 0, op & 0xFF, op >> 8)] += 1
        zsel[('tri', ti if op & 2 else 0, 'SHIFT' if not (op >> 8) and 0 <= firstz[0] < i else 'keep')] += 1
        k = ('tex' if op & 2 else 'shade', 'beforeRing' if ri and i < ri[0] else 'afterRing')
        gtri[k] += 1; gtex[(k[0], ti if op & 2 else 0)] += 1
        if ri: gd[k].append(ri[0] - i); gdt[ti if op & 2 else 0].append(ri[0] - i)
    for i, ti, ulx, uly, lrx, lry, vi, zc in pend:
        t = tex[ti[0]]; t['fmt'] = ti[1:]
        if inb(lrx, lry):
            gzr[(ti[0], zc)] += 1; zsel[('rect', ti[0], 'SHIFT' if not zc and 0 <= firstz[0] < i else 'keep')] += 1; ntexr_box += 1; t['in'] += 1; upd(t['inx'], ulx); upd(t['iny'], uly); upd(t['vi'], vi)
            t['sz'][(round(lrx - ulx), round(lry - uly))] += 1
            t['rel']['before' if i < tris[0] else 'after' if i > tris[-1] else 'inside'] += 1
            t['dist'].append(min(abs(i - j) for j in tris))
            if 750 <= ulx <= 800 and len(samples) < 12: samples.append((vi, ti[0], ulx, uly, lrx, lry, i, tris[0], tris[-1]))
        else:
            t['out'] += 1; upd(t['outx'], ulx); upd(t['outy'], uly); t['outvi'].add(vi)
            if ulx >= 880 and uly <= 160: upd(hud_ulx, ulx); upd(hud_lrx, lrx)
with open(path, 'rb') as f:
    while True:
        h = f.read(16)
        if len(h) < 16: break
        mg, x, ln, vi = struct.unpack('<4I', h); b = f.read(ln)
        if len(b) < ln: break
        nrec += 1; vmin = min(vmin, vi); vmax = max(vmax, vi); a = 0
        if vi != cur_vi:
            flush(); cur_vi = vi; firstz[0] = -1; idx = 0; boxr = []; tris = []; pend = []; ptri = []; ptri = []
        while a + 8 <= len(b):
            w0, w1 = struct.unpack_from('<II', b, a); op = (w0 >> 24) & 0x3F; step = 8
            if 0x08 <= op <= 0x0F: step = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            elif op in (0x24, 0x25): step = 16
            if a + step > len(b): break
            if op == 0x3F: ci_w = (w0 & 0x3FF) + 1
            elif op == 0x2F: om = (w0, w1)
            elif op == 0x3D: timg = (w1 & 0xFFFFFF, (w0 >> 21) & 7, (w0 >> 19) & 3, (w0 & 0xFFF) + 1)
            if ci_w == cwant and (op in (0x24, 0x25) or 0x08 <= op <= 0x0F) and (om[1] >> 4) & 1 and firstz[0] < 0: firstz[0] = idx
            if op == 0x3F or op == 0x3D or op == 0x2F: pass
            elif ci_w == cwant and op in (0x24, 0x25):
                lrx, lry, ulx, uly = ((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4, ((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4
                pend.append((idx, timg, ulx, uly, lrx, lry, vi, (om[1] >> 4) & 1))
            elif ci_w == cwant and 0x08 <= op <= 0x0F:
                yl, ym, yh = sx14(w0 & 0x3FFF), sx14((w1 >> 16) & 0x3FFF), sx14(w1 & 0x3FFF)
                xl, dl, xh, dh, xm, dm = (s32(v) / 65536.0 for v in struct.unpack_from('<6I', b, a + 8))
                xs = (xh, xm + dm * (ym - yh), xl, xl + dl * (yl - ym), xh + dh * (yl - yh))
                mn, mx = min(xs), max(xs)
                if inb((mn + mx) / 2, (yh + yl) / 2) and mx - mn <= 130 and yl - yh <= 130:
                    ntri_box += 1; tris.append(idx); ptri.append((idx, op | (((om[1] >> 4) & 1) << 8), timg[0], mn, mx, (yh + yl) / 2)); upd(tri_x, mn); upd(tri_x, mx)
                    if op & 2: tex[timg[0]]['tri_in'] += 1
                    if op & 2: tex[timg[0]]['fmt'] = timg[1:]
            a += step; idx += 1
    flush()
print('records %d vi %d..%d box %s cw %d; flight VIs (disc tris present) %d, other VIs skipped %d' % (nrec, vmin, vmax, box, cwant, nflight, nskip))
print('CONTROL region tris %d in %d VIs, x %.1f..%.1f; box texrects %d' % (ntri_box, recs_with_tri, tri_x[0], tri_x[1], ntexr_box))
print('right-HUD texrects (ul.x>=880, ul.y<=160, outside box): ul.x %.1f..%.1f lr.x %.1f..%.1f' % tuple(hud_ulx + hud_lrx))
print('timg     fmt/siz/w     in  out  tri_in  in ul.x       in ul.y      sizes(top3)            rel(before/inside/after disc tris, same VI)  med_dist  out ul.x        out ul.y   outVIs')
for ti, t in sorted(tex.items(), key=lambda kv: -kv[1]['in']):
    if not t['in'] and not t['tri_in']: continue
    d = sorted(t['dist']); md = d[len(d) // 2] if d else -1
    sz = ' '.join('%dx%d:%d' % (k[0], k[1], c) for k, c in t['sz'].most_common(3))
    rel = '/'.join(str(t['rel'][k]) for k in ('before', 'inside', 'after', 'no-tri-in-record'))
    ox = '%.0f..%.0f' % tuple(t['outx']) if t['out'] else '-'; oy = '%.0f..%.0f' % tuple(t['outy']) if t['out'] else '-'
    ix = '%.0f..%.0f' % tuple(t['inx']) if t['in'] else '-'; iy = '%.0f..%.0f' % tuple(t['iny']) if t['in'] else '-'
    print('%06X %-12s %5d %5d %6d  %-12s %-12s %-22s %-30s %4d  %-14s %-10s %d' % (ti, t['fmt'], t['in'], t['out'], t['tri_in'], ix, iy, sz, rel, md, ox, oy, len(t['outvi'])))
print('samples ul.x 750..800 (vi timg ul lr cmd-idx first/last disc tri idx):')
for s in samples: print('  vi=%d timg=%06X ul=(%.1f,%.1f) lr=(%.1f,%.1f) idx=%d tris=%d..%d' % s)
print('gated region tris by (texture, side of first ring texrect): ' + ' '.join('%s/%s=%d med_cmds_to_ring=%d' % (k[0], k[1], c, sorted(gd[k])[len(gd[k]) // 2] if gd[k] else -1) for k, c in sorted(gtri.items())))
print('gated region tris top textures: ' + ' '.join('%s:%06X=%d' % (k[0], k[1], c) for k, c in gtex.most_common(10)))
def q(v, f): v = sorted(v); return v[int(f * (len(v) - 1))] if v else -1
print('per tri texture (0 = shade-only): n, commands before first ring texrect min/med/max')
for ti, v in sorted(gdt.items(), key=lambda kv: -len(kv[1]))[:14]: print('  %06X n=%d %d/%d/%d' % (ti, len(v), q(v, 0), q(v, .5), q(v, 1)))
print('gated region tris by (texture, opcode, othermode z_cmp): ' + ' '.join('%06X/%02X/z%d=%d' % (k[0], k[1], k[2], c) for k, c in gop.most_common(16)))
print('gated box texrects by (texture, othermode z_cmp): ' + ' '.join('%06X/z%d=%d' % (k[0], k[1], c) for k, c in gzr.most_common(12)))
print('simulated s6852 rule (shift only z_cmp-off prims after the VI\'s first z_cmp-on prim): ' + ' '.join('%s:%06X:%s=%d' % (k[0], k[1], k[2], c) for k, c in sorted(zsel.items(), key=lambda kv: -kv[1]) if k[0] == 'rect' or k[2] == 'SHIFT' or c >= 1000))
