#!/usr/bin/env python3
"""s7151 line 2 (independent of PIL's transform and of SCK): a screencapture window PNG (tagged, display space) is converted
to sRGB with macOS sips (ColorSync), then compared with the nearest-in-time frames of the srgb and native raws over the
flattest blocks (8x8 blocks with std < 2 in the PNG, so resampling and timing barely matter). usage: png run_t0_mach? no:
s7151_png_check.py png srgb.raw nat.raw  -> per channel mean of block colours: sipsSRGB, srgbraw, natraw (median over
all raw frames inside the static pause window given by --frames a,b)."""
import sys, os, subprocess, struct, statistics
from PIL import Image, ImageStat
png, rs, rn = sys.argv[1:4]
fa, fb = map(int, sys.argv[sys.argv.index('--frames')+1].split(',')) if '--frames' in sys.argv else (None, None)
print('png profile:', subprocess.run(['sips', '-g', 'profile', png], capture_output=True, text=True).stdout.split('\n')[1].strip())
out = '/tmp/s7151_srgb.png'
subprocess.run(['sips', '-m', '/System/Library/ColorSync/Profiles/sRGB Profile.icc', png, '--out', out], capture_output=True)
def raw_img(p, i):
    f = open(p, 'rb'); _, w, h = struct.unpack('<QII', f.read(16)); rec = 16+w*h*3; n = os.path.getsize(p)//rec
    i = min(i if i >= 0 else n+i, n-1); f.seek(i*rec+16); return Image.frombytes('RGB', (w, h), f.read(w*h*3)), n
S0 = Image.open(png).convert('RGB'); S1 = Image.open(out).convert('RGB')
# --search: pick, per raw, the frame whose GREEN channel (least moved by P3<->sRGB here) best matches the PNG
def best(p):
    _, n = raw_img(p, 0); im0, _ = raw_img(p, 0); ref = S1.resize(im0.size, Image.BOX).getchannel('G')
    from PIL import ImageChops
    lo = fa if fa is not None else 0; hi = fb if fb is not None else n
    sc = [(ImageStat.Stat(ImageChops.difference(raw_img(p, i)[0].getchannel('G'), ref)).mean[0], i) for i in range(lo, hi, 3)]
    d, i = min(sc); print('  best %s frame %d G|d| %.2f' % (os.path.basename(p), i, d)); return raw_img(p, i)[0]
a = best(rs); b = best(rn)
W, H = a.size
S0, S1 = S0.resize((W, H), Image.BOX), S1.resize((W, H), Image.BOX)
res = []
for y in range(0, H-8, 8):
    for x in range(0, W-8, 8):
        bx = (x, y, x+8, y+8); st = ImageStat.Stat(S1.crop(bx))
        if max(st.stddev) < 2 and max(st.mean) > 30: res.append((st.mean, ImageStat.Stat(a.crop(bx)).mean, ImageStat.Stat(b.crop(bx)).mean, ImageStat.Stat(S0.crop(bx)).mean))
print('flat blocks', len(res))
for k, nm in enumerate(['sips-sRGB(png)', 'srgb raw', 'native raw', 'png as stored']):
    print('%-15s' % nm, ' '.join('%.1f' % statistics.mean(r[k][c] for r in res) for c in range(3)))
for k, nm in [(1, 'srgb raw'), (2, 'native raw'), (3, 'png stored')]:
    print('|%s - sipsSRGB| per ch' % nm, ' '.join('%.2f' % statistics.mean(abs(r[k][c]-r[0][c]) for r in res) for c in range(3)))
