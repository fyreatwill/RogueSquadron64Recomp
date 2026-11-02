# s6779: contact sheet of retail 1024 (title) dumps + port window captures. usage: sheet.py SDIR OUT [port_step]
import struct, re, glob, sys
from PIL import Image, ImageDraw
S, out = sys.argv[1], sys.argv[2]; step = int(sys.argv[3]) if len(sys.argv) > 3 else 4
th = []
for m in re.finditer(r'\[fb-dump\] t=\s*([\d.]+)s vi=(\d+) width=1024 .*?-> (\S+)', open(S + '/retail/oracle.log').read()):
    raw = open(m[3], 'rb').read(); px = struct.unpack_from('>%dH' % (512 * 448), raw, 0x190000)
    b = bytearray()
    for v in px: b += bytes(((v >> 11 & 31) << 3, (v >> 6 & 31) << 3, (v >> 1 & 31) << 3))
    im = Image.frombytes('RGB', (512, 448), bytes(b)).resize((184, 160)); ImageDraw.Draw(im).text((2, 2), 'R' + m[1], fill=(0, 255, 255)); th.append(im)
for f in sorted(glob.glob(S + '/port/w_*.png'))[::step]:
    im = Image.open(f).convert('RGB').crop((85, 64, 1191, 1024)).resize((184, 160)); ImageDraw.Draw(im).text((2, 2), 'P' + f[-12:-4], fill=(255, 255, 0)); th.append(im)
cols = 8; s = Image.new('RGB', (184 * cols, 160 * ((len(th) + cols - 1) // cols)))
for i, t in enumerate(th): s.paste(t, ((i % cols) * 184, (i // cols) * 160))
s.save(out)
