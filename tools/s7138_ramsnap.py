# s7138: extract the first RAM snapshot >= swap from a G5B capture as a big-endian (guest order) 16 MB image. usage: cap swap out.bin
import struct, sys, array
cap, want, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
f = open(cap, 'rb'); s = None
while True:
    t = f.read(4)
    if len(t) < 4: sys.exit('no snapshot')
    t = struct.unpack('<I', t)[0]
    if t == 0x50415753: m, s = struct.unpack('<QI', f.read(12))
    elif t == 0x204D4152:
        if s is not None and s >= want:
            a = array.array('I', f.read(0x1000000)); a.byteswap(); open(out, 'wb').write(a.tobytes()); print('swap', s); break
        f.seek(0x1000000, 1)
    elif t == 0x20474E52: lo, n = struct.unpack('<II', f.read(8)); f.seek(n, 1)
