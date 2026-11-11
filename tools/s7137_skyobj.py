# s7137: dump the 16 sky bin objects (S+0x1C+0x5C*k, 23 words each, as stored in the capture RAM: little-endian words) at the first RAM snapshot >= swap. usage: cap swap [S hex]
import struct, sys
cap, want = sys.argv[1], int(sys.argv[2]); S = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x8056E010
f = open(cap, 'rb'); s = None
while True:
    t = f.read(4)
    if len(t) < 4: break
    t = struct.unpack('<I', t)[0]
    if t == 0x50415753: m, s = struct.unpack('<QI', f.read(12))
    elif t == 0x204D4152:
        if s is not None and s >= want:
            r = f.read(0x1000000)
            for k in range(16):
                o = (S + 0x1C + 0x5C*k) & 0xFFFFFF
                print('%2d' % k, ' '.join('%08X' % struct.unpack('>I', r[o+4*i:o+4*i+4])[0] for i in range(23)))
            break
        f.seek(0x1000000, 1)
    elif t == 0x20474E52: lo, n = struct.unpack('<II', f.read(8)); f.seek(n, 1)
