#!/usr/bin/env python3
"""s6110: histogram SETSCISSOR / SETCOLORIMAGE / SETOTHERMODE seen in an RS64_RDP_BIN_PORT dump (PRDP hdr: magic,lo,len,ord)."""
import struct, sys, collections
d = open(sys.argv[1], 'rb').read()
sc = collections.Counter(); ci = collections.Counter(); fr = collections.Counter(); tri_x = [1e9, -1e9]
p = 0
while p + 16 <= len(d):
    magic, lo, ln, o = struct.unpack_from('<IIII', d, p)
    if magic != 0x50445250: break
    b = d[p+16:p+16+ln]; p += 16 + ln
    a = 0
    while a + 8 <= len(b):
        w0, w1 = struct.unpack_from('<II', b, a)  # RDRAM words are host-LE (code reads r[a^3])
        op = (w0 >> 24) & 0x3F; n = 8
        if 8 <= op <= 15: n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): n = 16
        elif op == 0x2D: sc[((w0>>12)&0xFFF, (w0&0xFFF), (w1>>12)&0xFFF, w1&0xFFF)] += 1
        elif op == 0x3F: ci[(((w0>>19)&7), ((w0>>17)&3), (w0&0x3FF)+1, w1)] += 1
        elif op == 0x36: fr[((w0>>12)&0xFFF, w0&0xFFF, (w1>>12)&0xFFF, w1&0xFFF)] += 1
        a += n
print("SETSCISSOR (ulx,uly,lrx,lry in 10.2):"); [print(' ', k, v) for k, v in sc.most_common(12)]
print("SETCOLORIMAGE (fmt,size,width,addr):"); [print(' ', k, v) for k, v in ci.most_common(12)]
print("FILLRECT xl,yl,xh,yh (10.2) top:"); [print(' ', k, v) for k, v in fr.most_common(8)]
