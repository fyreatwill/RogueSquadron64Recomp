"""s7133: summarise [swatch] store-watch rows on the flight camera 0x80138D18 (ROGUESQ_STORE_WATCH=138D18:138DE4).
Splits writers by camera offset band: ctl = +0x00..+0x74 (per-frame camera fields, positive control), clr = +0x74..+0xCC
(clear-rect count/ptr/rects read by emitFrameRdpInitDl). Usage: s7133_swatch.py run.log"""
import re, sys, collections
R = re.compile(r'\[swatch\] swap=(-?\d+) (pc|api)=([0-9A-F]+)\S* n=(\d+) bytes=\d+ lo=([0-9A-F]+) hi=([0-9A-F]+)')
CAM = 0x138D18
band = collections.defaultdict(lambda: collections.Counter()); swaps = collections.defaultdict(set)
for line in open(sys.argv[1], errors='replace'):
    m = R.search(line)
    if not m: continue
    sw, k, pc, n, lo, hi = int(m[1]), m[2], m[3], int(m[4]), int(m[5], 16) - CAM, int(m[6], 16) - CAM
    b = 'clr' if hi > 0x74 else 'ctl'
    key = (b, k, pc, '%02X-%02X' % (lo, hi))
    band[key][sw] += n; swaps[b].add(sw)
for b in ('ctl', 'clr'):
    s = swaps[b]; print('%s: %d swaps with stores (%s..%s)' % (b, len(s), min(s) if s else '-', max(s) if s else '-'))
    for key, c in sorted(band.items(), key=lambda kv: -len(kv[1])):
        if key[0] == b: print('  %s=%s off=%s swaps=%d stores=%d first=%d last=%d' % (key[1], key[2], key[3], len(c), sum(c.values()), min(c), max(c)))
