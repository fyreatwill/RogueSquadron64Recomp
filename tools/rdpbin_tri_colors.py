#!/usr/bin/env python3
"""Offline per-triangle colour-state census of an RS64_RDP_BIN_PORT dump (s5989).
Usage: rdpbin_tri_colors.py rdp.bin [ord_filter]
Tracks combine/prim/env/fill/timg/tlut state and reports, per (ord, state), tri counts and mean shade RGB."""
import struct, sys, collections
import os as _os; sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from rs64_zopen import zopen, zbytes  # s7805: zst-only retained inputs
def main():
    d = zbytes(sys.argv[1])
    want = int(sys.argv[2]) if len(sys.argv) > 2 else None
    p = 0
    st = dict(comb=(0, 0), prim=0, env=0, timg=0, tfmt=0, tlut=0, tlutaddr=0, othermode=(0, 0))
    agg = collections.OrderedDict()
    nsub = 0
    while p + 16 <= len(d):
        mg, lo, ln, od = struct.unpack_from('<IIII', d, p)
        if mg != 0x50445250: print('bad magic at', p); break
        p += 16
        buf = bytearray(d[p:p+ln]); p += ln
        for i in range(0, len(buf) - 3, 4):  # RDRAM host layout is word-swapped (r[a^3])
            buf[i:i+4] = buf[i:i+4][::-1]
        nsub += 1
        a = 0
        while a + 8 <= len(buf):
            w0, w1 = struct.unpack_from('>II', buf, a)
            op = (w0 >> 24) & 0x3F
            n = 8
            if 0x08 <= op <= 0x0F:
                n = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
                if op & 4 and a + 32 + 64 <= len(buf):
                    sh = struct.unpack_from('>16I', buf, a + 32)
                    r = ((sh[0] >> 16) & 0xFFFF); g = (sh[0] & 0xFFFF); b = (sh[1] >> 16) & 0xFFFF; al = sh[1] & 0xFFFF
                    # sh words: [R|G],[B|A] integer parts; take int16 high bytes
                    def s(x): return x - 0x10000 if x & 0x8000 else x
                    rgb = (s(r), s(g), s(b))
                else:
                    rgb = None
                key = (od, st['comb'], st['prim'], st['env'], st['timg'], st['tfmt'], st['tlutaddr'], 'sh' if rgb else 'noshade', 'tex' if op & 2 else 'notex')
                e = agg.setdefault(key, [0, [0, 0, 0]])
                e[0] += 1
                if rgb:
                    for k in range(3): e[1][k] += max(0, min(255, rgb[k]))
            elif op == 0x3C: st['comb'] = (w0 & 0xFFFFFF, w1)
            elif op == 0x3A: st['prim'] = w1
            elif op == 0x3B: st['env'] = w1
            elif op == 0x3D: st['timg'] = w1 & 0x3FFFFFF; st['tfmt'] = (w0 >> 19) & 0x1F
            elif op == 0x30: st['tlut'] = w1; st['tlutaddr'] = st['timg']
            elif op == 0x2F: st['othermode'] = (w0 & 0xFFFFFF, w1)
            elif op in (0x24, 0x25): n = 16
            a += n
    print('submissions', nsub)
    for k, (c, sm) in agg.items():
        if want is not None and k[0] != want: continue
        m = tuple(x // c for x in sm)
        print('ord=%d comb=%06x_%08x prim=%08x env=%08x timg=%07x fmt=%d tlutsrc=%07x %s %s n=%d meanRGB=%s' % (k[0], k[1][0], k[1][1], k[2], k[3], k[4], k[5], k[6], k[7], k[8], c, m))
main()
