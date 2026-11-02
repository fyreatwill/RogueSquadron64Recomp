# s6793: decode the retail fb dumps (tNNN.bin = phys 0x600000+2MB, origin from oracle.log) as 640x340 RGBA5551 and
# report, per dump, the column luminance dip around x=300..340 (fraction of rows y 80..330 where column x is >=12
# darker than both x-3 and x+3; best column), plus save PNGs. Args: DIR
import sys, os, re, struct
from PIL import Image
D = sys.argv[1]; W = 640; H = 340
org = {}
for l in open(os.path.join(D, 'oracle.log')):
    m = re.search(r'\[fb-dump\S*\] t=\s*([\d.]+)s .*origin=0x([0-9a-f]+).* -> (\S+)$', l.strip())
    if m: org[os.path.basename(m.group(3))] = (float(m.group(1)), int(m.group(2), 16))
for f in sorted(org):
    t, o = org[f]; raw = open(os.path.join(D, f), 'rb').read(); off = (o & ~0x3FF) - 0x600000 if False else o - 0x600000
    off -= (off % (W * 2)) % (W * 2) if False else 0
    if off < 0 or off + W * H * 2 > len(raw): print(f, 'origin out of range', hex(o)); continue
    px = struct.unpack_from('>%dH' % (W * H), raw, off)
    L = [[((v >> 11 & 31) * 3 + (v >> 6 & 31) * 6 + (v >> 1 & 31)) * 255 // 310 for v in px[y * W:(y + 1) * W]] for y in range(H)]
    out = bytearray()
    for v in px: out += bytes(((v >> 11 & 31) << 3, (v >> 6 & 31) << 3, (v >> 1 & 31) << 3))
    Image.frombytes('RGB', (W, H), bytes(out)).save(os.path.join(D, f[:-4] + '.png'))
    ys = range(80, 330); best = (0, 0)
    for x in range(296, 345):
        c = sum(1 for y in ys if L[y][x] + 12 <= L[y][x - 3] and L[y][x] + 12 <= L[y][x + 3]) / len(ys)
        best = max(best, (c, x))
    lit = sum(L[y][320] for y in ys) / len(ys)
    print('%s t=%.1f origin=%x lit=%.0f best_col=%d frac=%.2f prof318=%s' % (f, t, o, lit, best[1], best[0],
          [round(sum(L[y][x] for y in ys) / len(ys)) for x in range(314, 327)]))
