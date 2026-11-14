#!/usr/bin/env python3
# s7267: owner sheet from a same-run =tog capture raw (g5b_capture format: 16-byte header <QII mach,w,h + w*h RGB per frame).
# Picks N adjacent OFF/ON pairs (state = int(mach/PER) % 2, mid-period phase 0.4-0.6, in-flight frames only: side columns not black,
# same filter as g5e_edge_score.py) spread across the run, and tiles them as rows "OFF | ON" so the owner sees the side edge with and
# without the lever a fraction of a second apart (same flight, same camera path).
# usage: s7267_tog_sheet.py raw out.png [label] [pairs=6] [period_ticks=24e6] [cell_w=640] [split=parity|xor8]
# s7301: split=xor8 = rs64_tog_odd default clock (state = (k ^ k>>3) & 1); pairs are adjacent periods whose states differ.
import sys, struct
from PIL import Image, ImageDraw

def main(a):
    if len(a) < 3:
        print(__doc__ if __doc__ else open(__file__).read().split('\n')[3]); return 2
    raw, out = a[1], a[2]; label = a[3] if len(a) > 3 else raw
    NP = int(a[4]) if len(a) > 4 else 6; PER = float(a[5]) if len(a) > 5 else 24e6; CW = int(a[6]) if len(a) > 6 else 640
    f = open(raw, 'rb'); t, w, h = struct.unpack('<QII', f.read(16)); rec = 16 + w * h * 3; n = f.seek(0, 2) // rec
    if n == 0: print("empty raw"); return 1
    best = {}  # period index -> (|phase-0.5|, frame index)
    for i in range(n):
        f.seek(i * rec); t, _, _ = struct.unpack('<QII', f.read(16))
        ph = (t / PER) % 1
        if not 0.4 <= ph <= 0.6: continue
        f.seek(i * rec + 16 + (200 * w + 5) * 3); px = f.read(33)
        if px[0] + px[15] + px[30] < 30: continue  # debrief / letterboxed / black
        k = int(t // PER); d = abs(ph - 0.5)
        if k not in best or d < best[k][0]: best[k] = (d, i)
    # adjacent (off, on) periods: off = even state, on = the next period
    X8 = len(a) > 7 and a[7] == 'xor8'
    def stt(k): return ((k ^ (k >> 3)) & 1) if X8 else (k & 1)
    pairs = [((best[k][1], best[k + 1][1]) if stt(k) == 0 else (best[k + 1][1], best[k][1]))
             for k in sorted(best) if k + 1 in best and stt(k) != stt(k + 1) and (X8 or k % 2 == 0)]
    if not pairs: print("no OFF/ON pairs"); return 1
    pick = [pairs[round(j * (len(pairs) - 1) / max(1, NP - 1))] for j in range(min(NP, len(pairs)))]
    ch = round(h * CW / w); hdr = 22
    sheet = Image.new('RGB', (2 * CW, hdr + len(pick) * (ch + hdr)), (24, 24, 24)); dr = ImageDraw.Draw(sheet)
    dr.text((6, 4), f"{label}   left: lever OFF   right: lever ON   ({len(pairs)} pairs, {n} frames)", fill=(255, 255, 255))
    def frame(i):
        f.seek(i * rec); t, _, _ = struct.unpack('<QII', f.read(16))
        return t, Image.frombytes('RGB', (w, h), f.read(w * h * 3)).resize((CW, ch))
    for r, (io, ii) in enumerate(pick):
        y = hdr + r * (ch + hdr)
        for c, i in enumerate((io, ii)):
            t, im = frame(i); sheet.paste(im, (c * CW, y + hdr))
            dr.text((c * CW + 6, y + 4), f"{'OFF' if c == 0 else 'ON'}  t={t / 24e6:.1f}s  frame {i}", fill=(255, 220, 120))
    sheet.save(out); print(f"sheet {out}: {len(pick)} pairs of {len(pairs)}, {w}x{h}")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
