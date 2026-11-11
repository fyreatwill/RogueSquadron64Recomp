#!/usr/bin/env python3
"""s7136 owner sheet: angrylion replays of the 21:9 banked dive, sky fill off (s7134 Z1) vs ROGUESQ_HORIZON_SKYFILL on (s7136 Y1),
pose-matched by camera forward horizontal length (tools/s7135_campitch.py). Magenta = pixels nothing drew this frame.
usage: s7136_sheet.py out.png zdir xdir zswap:xswap[:label] ..."""
import struct, sys
from PIL import Image, ImageDraw
def load(p):
    d = open(p, 'rb').read(); w, h = struct.unpack('<II', d[:8]); return Image.frombytes('RGB', (w, h), d[8:8 + w * h * 3])
out, zd, xd = sys.argv[1:4]; pairs = [a.split(':') for a in sys.argv[4:]]
ims = [(load('%s/f%s.rgb' % (zd, p[0])), load('%s/f%s.rgb' % (xd, p[1])), p) for p in pairs]
W, H = ims[0][0].size; s = 0.5; w, h = int(W * s), int(H * s)
S = Image.new('RGB', (2 * w + 30, len(ims) * (h + 22) + 26), (24, 24, 24)); D = ImageDraw.Draw(S)
D.text((10, 6), 'sky fill OFF (s7134 Z1)', fill=(255, 255, 255)); D.text((w + 20, 6), 'ROGUESQ_HORIZON_SKYFILL on (default, s7136)', fill=(255, 255, 255))
for i, (a, b, p) in enumerate(ims):
    y = 26 + i * (h + 22)
    S.paste(a.resize((w, h)), (10, y)); S.paste(b.resize((w, h)), (w + 20, y))
    D.text((10, y + h + 4), 'swap %s  %s' % (p[0], p[2] if len(p) > 2 else ''), fill=(200, 200, 200)); D.text((w + 20, y + h + 4), 'swap %s (same pose)' % p[1], fill=(200, 200, 200))
S.save(out); print(out, S.size)
