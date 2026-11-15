"""s7387: flag raw-RDRAM stripe frames (r2r=0 abort-cut artefact, s7386) in window captures.
usage: python3 tools/s7387_stripe_detect.py <dir> [t0 t1]   -> per frame: t, mean luma, black rows, noisy rows (mean |dx|>30) in the 4:3 box; STRIPE =
>=60 black rows and >=8 noisy rows. Calibrated on scratch/s7386/aboff/w_0156.12.png (stripe, positive control) vs abon/w_0155.90.png (black)."""
import glob, os, sys
from PIL import Image, ImageStat, ImageFilter
def score(p):
    im = Image.open(p).convert('RGB'); W, H = im.size
    bw = int(H * 4 / 3); x0 = (W - bw) // 2
    box = im.crop((x0, 0, x0 + bw, H)).resize((320, 240))
    L = box.convert('L'); m = ImageStat.Stat(L).mean[0]
    px = list(L.get_flattened_data() if hasattr(L, 'get_flattened_data') else L.getdata()); blk = noisy = 0
    for y in range(240):
        r = px[y * 320:(y + 1) * 320]
        if max(r) < 10: blk += 1
        if sum(abs(r[i + 1] - r[i]) for i in range(319)) / 319 > 30: noisy += 1
    return m, blk, noisy
def main():
    d = sys.argv[1]; t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
    fs = glob.glob(f'{d}/w_*.png') + glob.glob(f'{d}/b_*.png') + glob.glob(f'{d}/burst*/*.png')
    rows = []
    for p in fs:
        try: t = float(os.path.basename(p).split('_', 1)[1][:-4])
        except ValueError: continue
        if t0 <= t <= t1: rows.append((t, p))
    n = 0
    for t, p in sorted(rows):
        m, b, g = score(p); st = b >= 60 and g >= 8
        n += st
        if st or os.environ.get('ALL') == '1': print(f'{t:8.2f} luma={m:5.1f} blackrows={b:3d} noisyrows={g:3d} {"STRIPE" if st else ""} {os.path.basename(p)}')
    print(f'{d}: frames={len(rows)} stripe={n}')
if __name__ == '__main__': main()
