# s7188: SETSCISSOR / SETCOLORIMAGE / FILLRECT / TEXRECT right-edge histograms over ROGUESQ_G5B_FRAME swaps [lo,hi] (RNG blocks = RDP cmds, host-LE words)
import struct, sys, collections
cap, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
sc = collections.Counter(); ci = collections.Counter(); fr = collections.Counter(); tr = collections.Counter(); f = open(cap, 'rb'); s = -1
while True:
    b = f.read(4)
    if len(b) < 4: break
    t = struct.unpack('<I', b)[0]
    if t == 0x50415753: m, s = struct.unpack('<QI', f.read(12))
    elif t == 0x204D4152: f.seek(0x1000000, 1)
    elif t == 0x20474E52:
        l, n = struct.unpack('<II', f.read(8))
        if not (lo <= s <= hi): f.seek(n, 1); continue
        d = f.read(n); a = 0
        while a + 8 <= len(d):
            w0, w1 = struct.unpack_from('<II', d, a); op = (w0 >> 24) & 0x3F; k = 8
            if 8 <= op <= 15: k = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
            elif op in (0x24, 0x25): k = 16; tr[((w0 >> 12) & 0xFFF) / 4] += 1
            elif op == 0x2D: sc[((w0>>12)&0xFFF)/4, (w0&0xFFF)/4, ((w1>>12)&0xFFF)/4, (w1&0xFFF)/4] += 1
            elif op == 0x3F: ci[(w0 & 0x3FF) + 1] += 1
            elif op == 0x36: fr[((w0>>12)&0xFFF)/4, (w0&0xFFF)/4, ((w1>>12)&0xFFF)/4, (w1&0xFFF)/4] += 1
            a += k
    else: print('bad tag', hex(t)); break
print('scissor', sc.most_common(5)); print('cimg width', ci.most_common(4)); print('fillrect lr/ul', fr.most_common(5)); print('texrect max xl', max(tr) if tr else None, 'top', sorted(tr.items())[-3:])
