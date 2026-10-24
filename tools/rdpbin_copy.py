#!/usr/bin/env python3
"""s6118: per current-SETCOLORIMAGE target, tabulate SETTEXTUREIMAGE/SETTILE/LOADBLOCK/LOADTILE/TEXRECT/FILLRECT/scissor
seen in an RS64_RDP_BIN_PORT dump. usage: rdpbin_copy.py dump.bin [max_bytes]"""
import struct, sys, collections
d = open(sys.argv[1], 'rb').read(int(sys.argv[2]) if len(sys.argv) > 2 else -1)
T = collections.defaultdict(collections.Counter)
cur = None; p = 0
while p + 16 <= len(d):
    magic, lo, ln, o = struct.unpack_from('<IIII', d, p)
    if magic != 0x50445250: break
    b = d[p+16:p+16+ln]; p += 16 + ln; a = 0
    while a + 8 <= len(b):
        w0, w1 = struct.unpack_from('<II', b, a); op = (w0 >> 24) & 0x3F; n = 8
        if 8 <= op <= 15: n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): n = 16
        if op == 0x3F: cur = (hex(w1), (w0 & 0x3FF) + 1)
        elif cur:
            t = T[cur]
            if op == 0x3D: t[('TEXIMG fmt,sz,w,addr', (w0>>21)&7, (w0>>19)&3, (w0&0x3FF)+1, hex(w1))] += 1
            elif op == 0x35: t[('SETTILE fmt,sz,line,tmem,tile', (w0>>21)&7, (w0>>19)&3, (w0>>9)&0x1FF, w0&0x1FF, (w1>>24)&7)] += 1
            elif op == 0x33: t[('LOADBLOCK sl,tl,sh,dxt', (w0>>12)&0xFFF, w0&0xFFF, (w1>>12)&0xFFF, w1&0xFFF)] += 1
            elif op == 0x34: t[('LOADTILE', (w0>>12)&0xFFF, w0&0xFFF, (w1>>12)&0xFFF, w1&0xFFF)] += 1
            elif op == 0x24 and a + 16 <= len(b):
                t[('TEXRECT xl,yl,xh,yh', (w1>>12)&0xFFF, w1&0xFFF, (w0>>12)&0xFFF, w0&0xFFF)] += 1
            elif op == 0x36: t[('FILLRECT', (w0>>12)&0xFFF, w0&0xFFF, (w1>>12)&0xFFF, w1&0xFFF)] += 1
            elif op == 0x2D: t[('SCISSOR', (w0>>12)&0xFFF, w0&0xFFF, (w1>>12)&0xFFF, w1&0xFFF)] += 1
            elif 8 <= op <= 15: t[('TRI',)] += 1
        a += n
for k, c in sorted(T.items(), key=lambda kv: -sum(kv[1].values())):
    print('COLORIMAGE addr,w', k, 'ops', sum(c.values()))
    for kk, v in c.most_common(60): print('   ', kk, v)
