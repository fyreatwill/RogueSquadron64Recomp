#!/usr/bin/env python3
"""s6854: replay the s6852 ROGUESQ_G1D_REGION_ZGATE selection (rs64_region_scan) on a port RDP bin recorded with
ROGUESQ_SHIFT_REGION=0, and characterise every texture whose tris/texrects the gate WOULD shift.
Rule mirrored from src/rsp/dpc_bridge.cpp: state runs in bin order across records; 0x3E sets the z image, 0x3F onto the
z image (Z clear) resets 'world'; any z_cmp-on tri/texrect sets 'world'; a prim is shifted when z_cmp is off and world is
set and it falls in the box (tri: bbox centre in [x0-pad, x1] x [y0, y1], bbox <= 130 px; texrect: lr in box).
Per selected texture it also collects EVERY use of that texture on the colour image (in or out of the box, z on/off):
  H-hud: selected uses sit at a fixed screen place across VIs, and the texture is not drawn elsewhere;
  H-fx:  the texture is also drawn z_cmp-on / outside the box at scattered positions, and its in-box uses move with the
         world (centre spread over consecutive VIs), i.e. a world effect that crossed the box.
usage: g1d_zoffobj.py bin [--box x0,x1,y0,y1] [--cw 1024] [--pad 32] [--skip TIMG,TIMG] [--vis N] [--disc TIMG] [--only TIMG,..]
--only restricts the table and trace to those textures.
--rule cflip (s6854) also resets 'world' when SETCIMG names a different colour image than the last one (buffer flip =
new frame): lvl17 frames without a Z clear otherwise inherit the previous frame's latch and their sky gets shifted.
--disc keeps selections only in VIs where that texture is selected (stands in for the runtime's radar-on gate)."""
import struct, sys, collections
a = sys.argv; path = a[1]
box = tuple(map(float, a[a.index('--box') + 1].split(','))) if '--box' in a else (669.0, 810.0, 20.0, 135.0)
cw = int(a[a.index('--cw') + 1]) if '--cw' in a else 1024
pad = (float(a[a.index('--pad') + 1]) if '--pad' in a else 32.0) * (box[1] - box[0]) / 141.0
nvis = int(a[a.index('--vis') + 1]) if '--vis' in a else 12
sx14 = lambda v: ((v & 0x3FFF) - (0x4000 if v & 0x2000 else 0)) / 4.0
def s32(v): return v - (1 << 32) if v & 0x80000000 else v
uses = collections.defaultdict(list)   # timg -> [(vi, kind, zc, world, cx, cy, w, h, sel)]
sel_vis = collections.defaultdict(set); nsel = collections.Counter(); ctl = collections.Counter()
cflip = '--rule' in a and a[a.index('--rule') + 1] == 'cflip'; lastc = None
zcmp = False; world = False; zimg = None; timg = 0; ci = 0; ciw = 0; nrec = 0; vmin = 1 << 31; vmax = -1
with open(path, 'rb') as f:
    while True:
        h = f.read(16)
        if len(h) < 16: break
        mg, x, ln, vi = struct.unpack('<4I', h); b = f.read(ln)
        if len(b) < ln: break
        nrec += 1; vmin = min(vmin, vi); vmax = max(vmax, vi); p = 0
        while p + 8 <= len(b):
            w0, w1 = struct.unpack_from('<II', b, p); op = (w0 >> 24) & 0x3F; step = 8
            if 0x08 <= op <= 0x0F: step = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            elif op in (0x24, 0x25): step = 16
            if p + step > len(b): break
            if op == 0x2F: zcmp = bool((w1 >> 4) & 1)
            elif op == 0x3D: timg = w1 & 0xFFFFFF
            elif op == 0x3E: zimg = w1 & 0xFFFFFF
            elif op == 0x3F:
                ci = w1 & 0xFFFFFF; ciw = (w0 & 0x3FF) + 1
                if ci == zimg: world = False
                elif cflip and ci != lastc: world = False
                if ci != zimg: lastc = ci
            prim = 0x08 <= op <= 0x0F or op in (0x24, 0x25)
            if prim and zcmp: world = True
            if prim and ciw == cw:
                if op in (0x24, 0x25):
                    lrx, lry, ulx, uly = ((w0 >> 12) & 0xFFF) / 4, (w0 & 0xFFF) / 4, ((w1 >> 12) & 0xFFF) / 4, (w1 & 0xFFF) / 4
                    inb = box[0] <= lrx <= box[1] and box[2] <= lry <= box[3]
                    rec = (vi, 'R', zcmp, world, (ulx + lrx) / 2, (uly + lry) / 2, lrx - ulx, lry - uly, inb and world and not zcmp)
                    t = timg
                else:
                    yl, ym, yh = sx14(w0 & 0x3FFF), sx14((w1 >> 16) & 0x3FFF), sx14(w1 & 0x3FFF)
                    xl, dl, xh, dh, xm, dm = (s32(v) / 65536.0 for v in struct.unpack_from('<6I', b, p + 8))
                    xs = (xh, xm + dm * (ym - yh), xl, xl + dl * (yl - ym), xh + dh * (yl - yh)); mn, mx = min(xs), max(xs)
                    cx, cy = (mn + mx) / 2, (yh + yl) / 2
                    inb = box[0] - pad <= cx <= box[1] and box[2] <= cy <= box[3] and mx - mn <= 130 and yl - yh <= 130
                    rec = (vi, 'T', zcmp, world, cx, cy, mx - mn, yl - yh, inb and world and not zcmp)
                    t = timg if op & 2 else 0
                uses[t].append(rec)
                if rec[8]: nsel[(t, rec[1])] += 1; sel_vis[t].add(vi)
                if inb: ctl['inbox ' + ('world' if world else 'pre-world') + (' z-on' if zcmp else ' z-off')] += 1
            p += step
disc = int(a[a.index('--disc') + 1], 16) if '--disc' in a else None
if disc is not None:
    keep = sel_vis[disc]; nsel = collections.Counter()
    for t in list(uses):
        uses[t] = [u[:8] + (u[8] and u[0] in keep,) for u in uses[t]]
        for u in uses[t]:
            if u[8]: nsel[(t, u[1])] += 1
    for t in list(sel_vis):
        sel_vis[t] = sel_vis[t] & keep
        if not sel_vis[t]: del sel_vis[t]
    print('--disc %06X: %d radar VIs' % (disc, len(keep)))
only = {int(x, 16) for x in a[a.index('--only') + 1].split(',')} if '--only' in a else None
if only is not None:
    for t in list(sel_vis):
        if t not in only: del sel_vis[t]
print('records %d vi %d..%d box %s pad %.1f cw %d' % (nrec, vmin, vmax, box, pad, cw))
print('in-box prims by gate state: ' + ' '.join('%s=%d' % kv for kv in sorted(ctl.items())))
print('selected (would shift) by texture/kind: ' + ' '.join('%06X/%s=%d' % (k[0], k[1], c) for k, c in nsel.most_common(30)))
def q(v, f): v = sorted(v); return v[int(f * (len(v) - 1))] if v else float('nan')
print('timg   n_sel selVIs | all uses: n  z-on  z-off-pre z-off-post  outbox-VIs | sel cx p5/p50/p95  cy p5/p50/p95 | sel size med | out cx p5..p95 cy p5..p95')
for t in sorted(sel_vis, key=lambda t: -len(sel_vis[t])):
    U = uses[t]; S = [u for u in U if u[8]]; O = [u for u in U if not u[8]]
    zon = sum(1 for u in U if u[2]); zpre = sum(1 for u in U if not u[2] and not u[3]); zpost = sum(1 for u in U if not u[2] and u[3])
    ovis = len({u[0] for u in O})
    print('%06X %6d %5d | %6d %5d %6d %6d %6d | %4.0f/%4.0f/%4.0f %4.0f/%4.0f/%4.0f | %3.0fx%-3.0f | %4.0f..%-4.0f %4.0f..%-4.0f' % (
        t, len(S), len(sel_vis[t]), len(U), zon, zpre, zpost, ovis,
        q([u[4] for u in S], .05), q([u[4] for u in S], .5), q([u[4] for u in S], .95),
        q([u[5] for u in S], .05), q([u[5] for u in S], .5), q([u[5] for u in S], .95),
        q([u[6] for u in S], .5), q([u[7] for u in S], .5),
        q([u[4] for u in O], .05), q([u[4] for u in O], .95), q([u[5] for u in O], .05), q([u[5] for u in O], .95)))
skip = {int(s, 16) for s in a[a.index('--skip') + 1].split(',')} if '--skip' in a else set()
print('per-VI trace of selected non-skipped textures (vi: timg sel/total-in-VI, sel centre mean, all-uses centre mean):')
vis = sorted({v for t in sel_vis if t not in skip for v in sel_vis[t]})
for v in vis[:nvis] + (['...'] if len(vis) > 2 * nvis else []) + vis[max(nvis, len(vis) - nvis):]:
    if v == '...': print('  ...'); continue
    parts = []
    for t in sorted(sel_vis):
        if t in skip or v not in sel_vis[t]: continue
        A = [u for u in uses[t] if u[0] == v]; S = [u for u in A if u[8]]
        parts.append('%06X %d/%d sel(%.0f,%.0f) all(%.0f,%.0f) z-on %d' % (t, len(S), len(A), sum(u[4] for u in S) / len(S), sum(u[5] for u in S) / len(S),
                     sum(u[4] for u in A) / len(A), sum(u[5] for u in A) / len(A), sum(1 for u in A if u[2])))
    print('  vi %d: %s' % (v, ' | '.join(parts)))
print('selected-VI span of non-skipped textures: %d VIs %s' % (len(vis), ('%d..%d' % (vis[0], vis[-1])) if vis else ''))
