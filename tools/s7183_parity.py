#!/usr/bin/env python3
"""s7183 H-interlace test for interlaced (RDP scissor field-mode) screens, e.g. the 512x448 level-description screen.

Each swap paints ONE field (every other row) of the 512x448 colour image; the other field is the previous frame's rows still in
RAM, which is what the VI scans out (weave). Inputs per swap:
  r replay (magenta pre-fill)  -> which row parity this swap painted (the current field)
  n replay (NOPREFILL)         -> hardware weave W (current field drawn over the RAM snapshot's previous field)
  presented RT64 frame (raw + pframe from a s7122_fidelity frames.csv) -> cropped by rect, box-scaled to native 512x448 = P
Models compared against P at native rows:
  WEAVE  = W
  BOB    = current-field rows line-doubled (other-field rows replaced by the current-field row above/below)
  PREV   = previous-field rows line-doubled (RT64 one field late)
Per model: mean |d| on current-field rows, on other-field rows, and whole frame. H-interlace (RT64 bobs or lags a field) predicts
BOB or PREV beating WEAVE and a current/other row asymmetry in d(P, W).
POSITIVE CONTROL (same data, same pipeline): synthesise a bobbed presented frame (BOB upscaled to the rect size, then box-scaled
back like P) and check the classifier picks BOB for it, and WEAVE for a synthesised weave. Must pass or the null means nothing.
usage: s7183_parity.py raw frames.csv rdir ndir x0,y0,x1,y1 [s0 s1]
"""
import sys, os, struct, csv, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7122_fidelity import Raw, dmap
from PIL import Image

MAG = b'\xf8\x00\xf8'
REPAIR = int(os.environ.get('REPAIR', '0'))


def rgb(path):
    d = open(path, 'rb').read(); w, h = struct.unpack('<II', d[:8]); return w, h, d[8:]


def parity(path):
    w, h, px = rgb(path); c = [0, 0]
    for y in range(min(h, 448)):
        row = px[y * w * 3:(y + 1) * w * 3]
        c[y & 1] += sum(1 for x in range(0, w, 16) if row[x * 3:x * 3 + 3] != MAG)
    return (0 if c[0] > c[1] else 1), c


def double(im, keep):
    """rows of parity `keep` kept, the other rows copied from the nearest kept row (bob)"""
    w, h = im.size; b = im.tobytes(); out = bytearray(b); rl = w * 3
    for y in range(h):
        if (y & 1) != keep:
            src = y - 1 if y - 1 >= 0 and ((y - 1) & 1) == keep else y + 1
            src = min(max(src, 0), h - 1); out[y * rl:(y + 1) * rl] = b[src * rl:(src + 1) * rl]
    return Image.frombytes('RGB', (w, h), bytes(out))


def comb(im):
    """adjacent-row vs two-apart-row mean |luma| difference; > 1 means the two fields hold different pictures (comb)"""
    g = im.convert('L'); w, h = g.size; px = g.tobytes(); a = b = 0
    for y in range(2, h - 2, 2):
        r0, r1, r2 = px[y * w:(y + 1) * w], px[(y + 1) * w:(y + 2) * w], px[(y + 2) * w:(y + 3) * w]
        a += sum(abs(p - q) for p, q in zip(r0, r1)); b += sum(abs(p - q) for p, q in zip(r0, r2))
    return a / max(b, 1)


def rowd(a, b, cur):
    w, h = a.size; d = dmap(a, b); s = [0.0, 0.0]; n = [0, 0]
    for y in range(h):
        k = 0 if (y & 1) == cur else 1; s[k] += sum(d[y * w:(y + 1) * w]); n[k] += w
    return s[0] / n[0], s[1] / n[1], (s[0] + s[1]) / (n[0] + n[1])


def main():
    rawp, fcsv, rdir, ndir, rect = sys.argv[1:6]; rect = tuple(map(int, rect.split(',')))
    s0, s1 = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else (0, 1 << 30)
    raw = Raw(rawp); RW, RH = rect[2] - rect[0], rect[3] - rect[1]
    rows = [r for r in csv.DictReader(open(fcsv)) if s0 <= int(r['swap']) <= s1]
    res = {k: [] for k in ('W', 'B', 'P', 'ctlB_pickB', 'ctlW_pickW', 'eff_real', 'eff_bob')}; asym = []; picks = {'W': 0, 'B': 0, 'P': 0}; npar = [0, 0]; combrows = []; rep = []
    for r in rows:
        s = int(r['swap']); fr = os.path.join(rdir, 'f%d.rgb' % s); fn = os.path.join(ndir, 'f%d.rgb' % s)
        if not (os.path.exists(fr) and os.path.exists(fn)): continue
        cur, c = parity(fr)
        if min(c) * 4 > max(c): continue  # not a field frame (both parities painted)
        npar[cur] += 1
        w, h, px = rgb(fn); h = min(h, 448); W = Image.frombytes('RGB', (w, h), px[:w * h * 3])
        P = raw.img(int(r['pframe'])).crop(rect).resize((w, h), Image.BOX)
        B = double(W, cur); PV = double(W, 1 - cur)
        dW, dB, dP = rowd(P, W, cur), rowd(P, B, cur), rowd(P, PV, cur)
        res['W'].append(dW); res['B'].append(dB); res['P'].append(dP); asym.append(dW[1] - dW[0])
        pk = min((dW[2], 'W'), (dB[2], 'B'), (dP[2], 'P'))[1]; picks[pk] += 1
        cw_, cp_ = comb(W), comb(P); combrows.append((s, cw_, cp_, pk, dW[2], dB[2]))
        if REPAIR and cw_ > 1.0:  # s7183: re-pair each model separately over pframe +-REPAIR (a 1-frame lag fakes PREV)
            j0 = int(r['pframe']); best = {}
            for j in range(max(0, j0 - REPAIR), min(len(raw.T), j0 + REPAIR + 1)):
                Q = raw.img(j).crop(rect).resize((w, h), Image.BOX)
                for nm, M in (('W', W), ('B', B), ('P', PV)):
                    v = rowd(Q, M, cur)[2]
                    if nm not in best or v < best[nm][0]: best[nm] = (v, j - j0)
            rep.append((s, best))
        # positive control: run synthetic presented frames through the same up/down scaling
        for model, key, want in ((B, 'ctlB_pickB', 'B'), (W, 'ctlW_pickW', 'W')):
            S = model.resize((RW, RH), Image.BICUBIC).resize((w, h), Image.BOX)
            got = min((rowd(S, W, cur)[2], 'W'), (rowd(S, B, cur)[2], 'B'), (rowd(S, PV, cur)[2], 'P'))[1]
            res[key].append(got == want)
            if want == 'B': res['eff_bob'].append(rowd(S, W, cur)[2] - rowd(S, B, cur)[2])
        res['eff_real'].append(dW[2] - dB[2])
    n = len(res['W'])
    print('field swaps scored', n, 'parity counts (even,odd current field)', npar)
    if not n: return 1
    for k, nm in (('W', 'WEAVE'), ('B', 'BOB'), ('P', 'PREV')):
        v = res[k]
        print('%-5s cur %.2f other %.2f all %.2f (median of frames)' % (nm, statistics.median(x[0] for x in v),
              statistics.median(x[1] for x in v), statistics.median(x[2] for x in v)))
    print('picks (lowest whole-frame d):', picks)
    print('d(P,WEAVE) other-minus-current rows: median %.3f, p10 %.3f, p90 %.3f' % (statistics.median(asym),
          sorted(asym)[n // 10], sorted(asym)[(9 * n) // 10]))
    print('effect d(.,WEAVE)-d(.,BOB): real median %.3f (p10 %.3f p90 %.3f); synthetic-bob median %.3f  (a real bob would sit near the synthetic value)' % (
        statistics.median(res['eff_real']), sorted(res['eff_real'])[n // 10], sorted(res['eff_real'])[(9 * n) // 10], statistics.median(res['eff_bob'])))
    cm = [c for c in combrows if c[1] > 1.0]
    print('COMB split: hardware weave combed (adj/two > 1) on %d/%d swaps; RT64 presented combed on %d of those (%d overall)' % (
        len(cm), n, sum(1 for c in cm if c[2] > 1.0), sum(1 for c in combrows if c[2] > 1.0)))
    if cm:
        pk = {'W': 0, 'B': 0, 'P': 0}
        for c in cm: pk[c[3]] += 1
        print('  combed swaps: picks', pk, 'median d WEAVE %.2f BOB %.2f; swaps %s' % (statistics.median(c[4] for c in cm),
              statistics.median(c[5] for c in cm), ','.join(str(c[0]) for c in cm[:40])))
    if rep:
        for nm in 'WBP':
            print('  REPAIRED (+-%d frames) combed swaps, model %s: median best d %.2f, offsets %s' % (REPAIR, nm,
                  statistics.median(b[nm][0] for _, b in rep), dict(sorted(__import__('collections').Counter(b[nm][1] for _, b in rep).items()))))
    cb = sum(res['ctlB_pickB']); cw = sum(res['ctlW_pickW'])
    ok = cb >= 0.9 * n and cw >= 0.9 * n
    print('CONTROL synthetic bob picked BOB %d/%d, synthetic weave picked WEAVE %d/%d -> %s' % (cb, n, cw, n, 'PASS' if ok else 'FAIL'))
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
