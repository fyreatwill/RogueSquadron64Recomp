# s6842: per-VI non-triangle RDP command dump of a VI-stamped port RDP bin (RS64_RDP_BIN_PORT_VI=1). usage: rdp_bin_cmds.py bin 0 vi_lo vi_hi [tri]
import struct, sys
p, F, lo, hi = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); wanttri = len(sys.argv) > 5
f = open(p, 'rb'); pos = 0
while True:
    h = f.read(16)
    if len(h) < 16: break
    mg, x, ln, vi = struct.unpack('<4I', h)
    if vi >= lo - 2: break
    f.seek(ln, 1); pos += 16 + ln
f.seek(pos); data = f.read(400 << 20); o = 0
# resync: find magic of record header
mg0 = None
recs = []
# find a plausible header: assume records '<4I' mg,lo,ln,vi with constant mg
import re
fr = []; cur = []; curvi = None
def fx(v): return v / 4.0
while o + 16 <= len(data):
    mg, x, ln, vi = struct.unpack_from('<4I', data, o); o += 16; b = data[o:o + ln]; o += ln
    if curvi is None: curvi = vi
    a = 0
    while a + 8 <= len(b):
        w0, w1 = struct.unpack_from('<II', b, a); op = (w0 >> 24) & 0x3F; n = 8; s = None
        if 0x08 <= op <= 0x0F:
            n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            if wanttri:
                yl = ((w0 & 0x3FFF) << 18 >> 18) / 4; ym = (((w1 >> 16) & 0x3FFF) << 18 >> 18) / 4; yh = ((w1 & 0x3FFF) << 18 >> 18) / 4
                xs = [struct.unpack_from('<i', b, a + k)[0] / 65536 for k in (8, 16, 24)]
                s = 'tri%02X y %.0f..%.0f x %s' % (op, yh, yl, ' '.join('%.0f' % v for v in xs))
        elif op in (0x24, 0x25):
            n = 16; s = 'texrect %s ul(%.1f,%.1f) lr(%.1f,%.1f) t%d' % ('F' if op == 0x25 else '', fx((w1 >> 12) & 0xFFF), fx(w1 & 0xFFF), fx((w0 >> 12) & 0xFFF), fx(w0 & 0xFFF), (w1 >> 24) & 7)
        elif op == 0x36: s = 'fill ul(%.1f,%.1f) lr(%.1f,%.1f)' % (fx((w1 >> 12) & 0xFFF), fx(w1 & 0xFFF), fx((w0 >> 12) & 0xFFF), fx(w0 & 0xFFF))
        elif op == 0x2D: s = 'scis (%.1f,%.1f)-(%.1f,%.1f)' % (fx((w0 >> 12) & 0xFFF), fx(w0 & 0xFFF), fx((w1 >> 12) & 0xFFF), fx(w1 & 0xFFF))
        elif op == 0x37: s = 'fillc %08X' % w1
        elif op == 0x3A: s = 'prim %08X' % w1
        elif op == 0x3B: s = 'env %08X' % w1
        elif op == 0x38: s = 'fog %08X' % w1
        elif op == 0x39: s = 'blend %08X' % w1
        elif op == 0x3C: s = 'comb %06X %08X' % (w0 & 0xFFFFFF, w1)
        elif op == 0x2F: s = 'om %06X %08X' % (w0 & 0xFFFFFF, w1)
        elif op == 0x3F: s = 'ci %06X w%d' % (w1 & 0xFFFFFF, (w0 & 0x3FF) + 1)
        elif op == 0x3E: s = 'zi %06X' % (w1 & 0xFFFFFF)
        elif op == 0x3D: s = 'ti %06X w%d' % (w1 & 0xFFFFFF, (w0 & 0x3FF) + 1)
        elif op == 0x29:
            if lo <= curvi <= hi: fr.append((curvi, cur))
            cur = []; curvi = vi
            if curvi > hi: break
        if s and lo <= curvi <= hi: cur.append(s)
        a += n
    if curvi is not None and curvi > hi: break
for vi, c in fr:
    print('=== vi', vi, len(c))
    for s in c: print('  ', s)
