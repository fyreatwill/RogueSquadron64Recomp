#!/usr/bin/env python3
"""Convert P6 PPM framebuffer dumps to PNG (no deps): ppm2png.py in.ppm [out.png]"""
import struct, sys, zlib

def conv(src, dst):
    parts = open(src, 'rb').read().split(None, 4)
    w, h = int(parts[1]), int(parts[2])
    px = parts[4][-w * h * 3:]
    raw = b''.join(b'\0' + px[y * w * 3:(y + 1) * w * 3] for y in range(h))
    def ch(t, b):
        return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t + b))
    open(dst, 'wb').write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                          + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b''))

if __name__ == '__main__':
    conv(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else sys.argv[1].rsplit('.', 1)[0] + '.png')
