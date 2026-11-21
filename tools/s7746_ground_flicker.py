"""s7746: ground-only stand-in flicker scorer (G6c).

s7624_flicker_score counts parity flicker over the whole frame. Under a rolling/banking camera the cloud layer flickers too,
and stand-ins are ground objects, so sky pixels only add noise. This counts flicker (b differs from mean(a,c) while a~c) only on
pixels that are non-sky in all three frames (sky = blue-dominant: B > R+30 and B > G+10 and B > 110), per window, plus the
same-run positive control: a 6x6 +90 luma square painted on a ground pixel of alternate window-2 frames must be found.
usage: s7746_ground_flicker.py LOG FBDIR
"""
import re, sys, os
from PIL import Image
T = 40

def load(p):
    im = Image.open(p).convert('RGB'); w, h = im.size; px = im.tobytes()
    L = [(299 * px[k] + 587 * px[k + 1] + 114 * px[k + 2]) // 1000 for k in range(0, len(px), 3)]
    S = [px[k + 2] > px[k] + 30 and px[k + 2] > px[k + 1] + 10 and px[k + 2] > 110 for k in range(0, len(px), 3)]
    return w, h, L, S

def score(fr):
    tot, per = 0, []
    for k in range(1, len(fr) - 1):
        (wa, ha, a, sa), (wb, hb, b, sb), (wc, hc, c, sc) = fr[k - 1], fr[k], fr[k + 1]
        if not (wa == wb == wc and ha == hb == hc): per.append(0); continue
        n = sum(1 for q in range(wb * hb) if not (sa[q] or sb[q] or sc[q]) and abs(a[q] - c[q]) < T // 2 and abs(2 * b[q] - a[q] - c[q]) > 2 * T)
        per.append(n); tot += n
    return tot, per

def main():
    log, fb = sys.argv[1], sys.argv[2]
    rows = [tuple(map(int, m.groups())) for l in open(log, errors='replace') for m in [re.search(r'\[standins-fb\] n=(\d+) win=(\d+) on=(\d)', l)] if m]
    files = {int(re.search(r'fb_(\d+)_', f).group(1)): os.path.join(fb, f) for f in os.listdir(fb) if f.startswith('fb_')}
    for win in (1, 2):
        sel = [r for r in rows if r[1] == win and r[0] in files]
        fr = [load(files[n]) for n, _, _ in sel]
        tot, per = score(fr)
        gnd = sum(sum(1 for s in f[3] if not s) for f in fr) / max(1, len(fr))
        top = sorted(zip(per, [r[0] for r in sel[1:-1]], [r[2] for r in sel[1:-1]]), reverse=True)[:3]
        print('win=%d triplets=%d ground_flicker=%d per_triplet=%.1f mean_ground_px=%d top=%s' % (win, len(per), tot, tot / max(1, len(per)), gnd, top))
        if win == 2 and len(fr) > 4:
            w, h = fr[0][0], fr[0][1]
            q0 = next((q for q in range(w * h // 2, w * h) if all(not f[3][q] for f in fr) and q % w < w - 8 and q // w < h - 8), None)
            if q0 is None: print('control: no all-ground pixel -> UNEVALUABLE'); continue
            for i in range(1, len(fr), 2):
                for dy in range(6):
                    for dx in range(6):
                        q = q0 + dy * w + dx; fr[i][2][q] = min(255, fr[i][2][q] + 90) if fr[i][2][q] < 160 else fr[i][2][q] - 90
            t2, _ = score(fr)
            need = 36 * (len(fr) - 2) // 2
            print('control: painted 36 px ground square, found +%d (need >= %d) -> %s' % (t2 - tot, need, 'PASS' if t2 - tot >= need else 'FAIL'))

main()
