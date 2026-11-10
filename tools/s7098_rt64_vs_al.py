#!/usr/bin/env python3
"""s7098 G5b: RT64 presented frames vs angrylion replay of the SAME forwarded RDP stream (one capture run).

Inputs, all from ONE run (scratch/s7098/arm.zsh):
  cap  = ROGUESQ_G5B_FRAME capture (dpc_bridge.cpp rs64_g5b_frame: SWAP mach swap / RAM 16 MB / RNG lo len bytes)
  raw  = tools/g5b_capture.swift recording of the game window (u64 displayTime mach, u32 w, u32 h, w*h*3 RGB)
Steps:
  index  : list the swaps whose own first range carries a RAM snapshot (replayable with the frame's own textures)
  replay : run frame_replay on the chosen swaps (KILL_AREA=<px> variant = positive control: big terrain tris removed)
  score  : downscale both to blocks, calibrate display lag (mach ticks) on the median score, then per swap:
           hole = fraction of blocks where angrylion is far from the presented frame. Flags frames above
           floor = median + K * MAD.  Same metric on the KILL replay must flag (control).
usage:
  s7098_rt64_vs_al.py index  cap out.idx
  s7098_rt64_vs_al.py score  raw idx aldir out.csv [--kill killdir] [--t0 mach] [--t1 mach]
"""
import sys, struct, os, bisect, statistics

def index(cap, out):
    f = open(cap, 'rb'); rows = []; cur = None; first = False
    while True:
        b = f.read(4)
        if len(b) < 4: break
        t = struct.unpack('<I', b)[0]
        if t == 0x50415753:
            m, s = struct.unpack('<QI', f.read(12)); cur = [s, m, 0, 0, 0]; rows.append(cur); first = True
        elif t == 0x204D4152:
            f.seek(0x1000000, 1)
            if cur is not None and first: cur[4] = 1
        elif t == 0x20474E52:
            lo, n = struct.unpack('<II', f.read(8)); f.seek(n, 1)
            if cur is not None: cur[2] += 1; cur[3] += n; first = False
        else:
            print('bad tag', hex(t), f.tell()); break
    open(out, 'w').write(''.join('%d %d %d %d %d\n' % tuple(r) for r in rows))
    print('swaps', len(rows), 'ram-own', sum(r[4] for r in rows))

BW, BH = 48, 27  # block grid over the 16:9 presented frame

def load_raw(raw):
    f = open(raw, 'rb'); t, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3
    n = os.path.getsize(raw) // rec; T = []
    for i in range(n):
        f.seek(i * rec); T.append(struct.unpack('<Q', f.read(8))[0])
    return f, w, h, rec, T

def blocks_rgb(px, w, h, x0, y0, x1, y1):
    """mean RGB per BWxBH block of the rectangle [x0,x1)x[y0,y1) of an RGB8 buffer."""
    out = []
    for by in range(BH):
        ya, yb = y0 + (y1 - y0) * by // BH, y0 + (y1 - y0) * (by + 1) // BH
        for bx in range(BW):
            xa, xb = x0 + (x1 - x0) * bx // BW, x0 + (x1 - x0) * (bx + 1) // BW
            r = g = b = c = 0
            for y in range(ya, yb, max(1, (yb - ya) // 3)):
                row = y * w * 3
                for x in range(xa, xb, max(1, (xb - xa) // 3)):
                    i = row + x * 3; r += px[i]; g += px[i + 1]; b += px[i + 2]; c += 1
            out.append((r / c, g / c, b / c) if c else (0, 0, 0))
    return out

def load_al(path):
    d = open(path, 'rb').read(); w, h = struct.unpack('<II', d[:8]); px = d[8:]
    # active rows: rows whose pixels are not all the magenta prefill (F83E -> 248,0,248)
    rows = [y for y in range(h) if sum(1 for x in range(0, w, 8) if px[(y * w + x) * 3:(y * w + x) * 3 + 3] != b'\xf8\x00\xf8') > (w // 8) // 2]
    if not rows: return None
    y0, y1 = rows[0], rows[-1] + 1
    return blocks_rgb(px, w, h, 0, y0, w, y1), (w, y1 - y0)

def diffscore(a, b, T=48):
    bad = 0
    for p, q in zip(a, b):
        if abs(p[0] - q[0]) + abs(p[1] - q[1]) + abs(p[2] - q[2]) > T: bad += 1
    return bad / len(a)

def score(raw, idx, aldir, out, kill=None, t0=0, t1=1 << 63, py0=None):
    f, w, h, rec, T = load_raw(raw)
    # presented active rectangle: rows/cols not black across the run's middle frame (letterbox guard)
    f.seek((len(T) // 2) * rec + 16); mid = f.read(w * h * 3)
    lit_r = [y for y in range(h) if any(mid[(y * w + x) * 3] + mid[(y * w + x) * 3 + 1] + mid[(y * w + x) * 3 + 2] > 30 for x in range(0, w, 4))]
    lit_c = [x for x in range(w) if any(mid[(y * w + x) * 3] + mid[(y * w + x) * 3 + 1] + mid[(y * w + x) * 3 + 2] > 30 for y in range(0, h, 4))]
    px0, px1, py1 = lit_c[0], lit_c[-1] + 1, lit_r[-1] + 1
    py0 = lit_r[0] if py0 is None else py0  # --py0 skips the window title bar the recorder includes
    print('presented', w, h, 'active', px0, py0, px1, py1, 'frames', len(T))
    sw = {}
    for line in open(idx):
        s, m, nr, nb, ram = map(int, line.split()); sw[s] = m
    cache = {}
    def pres(i):
        if i not in cache:
            f.seek(i * rec + 16); cache[i] = blocks_rgb(f.read(w * h * 3), w, h, px0, py0, px1, py1)
        return cache[i]
    al = {}
    for fn in os.listdir(aldir):
        if fn.startswith('f') and fn.endswith('.rgb'):
            s = int(fn[1:-4])
            if s in sw and t0 <= sw[s] <= t1:
                r = load_al(os.path.join(aldir, fn))
                if r: al[s] = r
    ks = sorted(al); print('replayed', len(ks), 'al size', al[ks[0]][1] if ks else None)
    def at(m, lag):
        i = bisect.bisect_left(T, m + lag); return min(i, len(T) - 1)
    # lag calibration on every 4th swap: ticks are 24 MHz (41.67 ns); scan 0..150 ms
    best = None
    for lag in range(0, 3600000, 120000):
        sc = [diffscore(al[s][0], pres(at(sw[s], lag))) for s in ks[::4]]
        med = statistics.median(sc)
        if best is None or med < best[0]: best = (med, lag)
    lag = best[1]; print('lag ticks', lag, '(%.1f ms) median score %.3f' % (lag / 24000.0, best[0]))
    res = []
    for s in ks:
        i = at(sw[s], lag)
        sc0 = diffscore(al[s][0], pres(i))
        nb = min(diffscore(al[s][0], pres(j)) for j in range(max(0, i - 2), min(len(T), i + 3)))
        res.append((s, sw[s], i, sc0, nb))
    med = statistics.median(r[3] for r in res); mad = statistics.median(abs(r[3] - med) for r in res) or 1e-3
    flo = med + 6 * mad
    o = open(out, 'w'); o.write('swap,mach,pframe,score,best_nb,flag\n')
    nf = 0
    for r in res:
        fl = int(r[3] > flo and r[4] > flo); nf += fl
        o.write('%d,%d,%d,%.4f,%.4f,%d\n' % (r + (fl,)))
    print('floor median %.3f mad %.3f thr %.3f  flagged(exact AND +-2 neighbours) %d of %d' % (med, mad, flo, nf, len(res)))
    top = sorted(res, key=lambda r: -min(r[3], r[4]))[:12]
    print('top:', ' '.join('%d:%.2f/%.2f' % (r[0], r[3], r[4]) for r in top))
    if kill:
        kf = 0; kn = 0; ks2 = []
        for fn in os.listdir(kill):
            if not fn.endswith('.rgb'): continue
            s = int(fn[1:-4])
            if s not in al: continue
            r = load_al(os.path.join(kill, fn))
            if not r: continue
            i = at(sw[s], lag); a = diffscore(r[0], pres(i)); b = diffscore(al[s][0], pres(i)); d = diffscore(r[0], al[s][0])
            kn += 1; kf += int(a > flo); ks2.append((s, b, a, d))
        print('CONTROL kill replays %d flagged %d' % (kn, kf), ' '.join('%d:%.2f->%.2f(al-al %.2f)' % x for x in ks2[:10]))

if __name__ == '__main__':
    a = sys.argv
    if a[1] == 'index': index(a[2], a[3])
    elif a[1] == 'score':
        kw = {}; rest = a[6:]
        while rest:
            k, v = rest[0], rest[1]; rest = rest[2:]
            if k == '--kill': kw['kill'] = v
            elif k == '--t0': kw['t0'] = int(v)
            elif k == '--t1': kw['t1'] = int(v)
            elif k == '--py0': kw['py0'] = int(v)
        score(a[2], a[3], a[4], a[5], **kw)
