#!/usr/bin/env python3
"""s7143: hangar text-box residual discriminator (H-filter / H-misalign / H-scale / H-tex), offline on s7142 raws + angrylion replays.
For sampled paired frames: crop a box (compare coords) from RT64 presented frame and box-downscaled angrylion, and score frac>40 / mean|d|
under: integer dx,dy shifts; 0.5 px subpixel shifts; horizontal scale about box centre; blur of angrylion only; blur of both sides;
plus per-channel signed mean and bright-pixel coverage (glyph colour / weight).  A same-run control box (non-text centre) gives the floor.
usage: s7143_textbox.py raw aldir frames.csv rect box ctrlbox [nsample]"""
import sys, os, csv, statistics as S, importlib.util
sp = importlib.util.spec_from_file_location('f', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7122_fidelity.py')); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
from PIL import Image, ImageFilter
raw = F.Raw(sys.argv[1]); ald = sys.argv[2]
rows = [r for r in csv.DictReader(open(sys.argv[3])) if int(r['pframe']) > 0]
R = tuple(map(int, sys.argv[4].split(','))); B = tuple(map(int, sys.argv[5].split(':'))); C = tuple(map(int, sys.argv[6].split(':')))
n = int(sys.argv[7]) if len(sys.argv) > 7 else 40; rows = rows[::max(1, len(rows) // n)][:n]; W, H = R[2] - R[0], R[3] - R[1]
def sc(a, p):
    d = F.dmap(a, p); return sum(v > F.T for v in d) / len(d), sum(d) / len(d)
res = {}
def add(k, v): res.setdefault(k, []).append(v)
for r in rows:
    al = F.load_al(os.path.join(ald, 'f%s.rgb' % r['swap']))
    if al is None: continue
    a = al.resize((W, H), Image.BOX); p = raw.img(int(r['pframe'])).crop(R)
    pb = lambda b, dx=0, dy=0: p.crop((b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy))
    add('base', sc(a.crop(B), pb(B))); add('ctrl', sc(a.crop(C), pb(C)))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx or dy: add('d%+d%+d' % (dx, dy), sc(a.crop(B), pb(B, dx, dy)))
    a2 = al.resize((W * 2, H * 2), Image.BOX)  # half-pixel shifts on the angrylion side
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        sh = a2.transform(a2.size, Image.AFFINE, (1, 0, sx, 0, 1, sy), Image.NEAREST).resize((W, H), Image.BOX)
        add('half%+d%+d' % (sx, sy), sc(sh.crop(B), pb(B)))
    cx = (B[0] + B[2]) / 2 * al.size[0] / W  # horizontal scale about box centre, in angrylion pixels
    for s in (0.94, 0.97, 1.03, 1.06):
        t = al.transform(al.size, Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1, 0), Image.BILINEAR).resize((W, H), Image.BOX)
        add('xs%.2f' % s, sc(t.crop(B), pb(B)))
    for rad in (0.5, 0.8, 1.2):
        g = ImageFilter.GaussianBlur(rad)
        add('blurAL%.1f' % rad, sc(a.filter(g).crop(B), pb(B)))
        add('blurBOTH%.1f' % rad, sc(a.filter(g).crop(B), p.filter(g).crop(B)))
        add('blurBOTHctrl%.1f' % rad, sc(a.filter(g).crop(C), p.filter(g).crop(C)))
    ab, pp = a.crop(B), pb(B)
    for ch in range(3):
        add('signed_ch%d' % ch, (S.mean(pp.getdata(ch)) - S.mean(ab.getdata(ch)), 0))
    lum = lambda im: [sum(px) / 3 for px in im.getdata()]
    la, lp = lum(ab), lum(pp)
    add('bright>128 frac al,rt', (sum(v > 128 for v in la) / len(la), sum(v > 128 for v in lp) / len(lp)))
    # column-profile correlation peak: bright column histograms
    def cols(L): return [sum(L[y * (B[2] - B[0]) + x] for y in range(B[3] - B[1])) for x in range(B[2] - B[0])]
    ca, cp = cols(la), cols(lp)
    def corr(k):
        xs = [(ca[i], cp[i + k]) for i in range(len(ca)) if 0 <= i + k < len(cp)]
        ma = S.mean(x for x, _ in xs); mb = S.mean(y for _, y in xs)
        num = sum((x - ma) * (y - mb) for x, y in xs); den = (sum((x - ma) ** 2 for x, _ in xs) * sum((y - mb) ** 2 for _, y in xs)) ** .5
        return num / den if den else 0
    best = max(range(-4, 5), key=corr); add('colprof best dx,corr0', (best, corr(0)))
print('frames', len(res['base']), 'box', B, 'ctrl', C)
for k, v in res.items():
    print('%-22s med %.4f  mean2 %.3f' % (k, S.median(x for x, _ in v), S.mean(y for _, y in v)))
