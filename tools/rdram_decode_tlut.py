#!/usr/bin/env python3
"""s5992: decode TLUT (RGBA5551) and CI8 texels from a word-swapped RDRAM dump (pure python).
Usage: rdram_decode_tlut.py rdram.bin tlut_hex[:count] ... -- timg_hex[:bytes] ... [--rgba16 hex:bytes]
Positive control: --rgba16 decodes a known RGBA16 region and prints its mean colour."""
import sys
raw = bytearray(open(sys.argv[1], 'rb').read())
for i in range(0, len(raw) - 3, 4):
    raw[i:i+4] = raw[i:i+4][::-1]  # undo ^3 word swap
def pal(addr, n):
    out = []
    for k in range(n):
        v = (raw[addr+2*k] << 8) | raw[addr+2*k+1]
        out.append((((v >> 11) & 31) * 255 // 31, ((v >> 6) & 31) * 255 // 31, ((v >> 1) & 31) * 255 // 31))
    return out
def mean(c):
    n = len(c) or 1
    return '(%.0f,%.0f,%.0f)' % tuple(sum(x[i] for x in c) / n for i in range(3))
args = sys.argv[2:]
sep = args.index('--') if '--' in args else len(args)
rg = args.index('--rgba16') if '--rgba16' in args else len(args)
tluts = [(int(x.split(':')[0], 16), int(x.split(':')[1]) if ':' in x else 256) for x in args[:sep]]
timgs = [(int(x.split(':')[0], 16), int(x.split(':')[1]) if ':' in x else 4096) for x in args[sep+1:rg]]
for x in args[rg+1:]:
    a, n = x.split(':'); print('RGBA16 control', x, 'mean', mean(pal(int(a, 16), int(n)//2)))
for ta, n in tluts:
    p = pal(ta, n)
    print('TLUT %07x n=%d mean=%s nonblack=%d' % (ta, n, mean(p), sum(1 for e in p if sum(e) > 0)))
    print('  first16:', p[:16])
    for ia, nb in timgs:
        t = raw[ia:ia+nb]
        print('  timg %07x idx_min=%d max=%d distinct=%d via-palette mean=%s' % (ia, min(t), max(t), len(set(t)), mean([p[i] for i in t])))
