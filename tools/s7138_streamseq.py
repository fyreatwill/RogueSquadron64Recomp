# s7138: run-length sequence of RDP state (cc, othermode) and tri ops in one swap of a G5B capture, to see which DL groups emit tris.
# usage: s7138_streamseq.py cap swap [max_lines]
import struct, sys
cap, want = sys.argv[1], int(sys.argv[2]); mx = int(sys.argv[3]) if len(sys.argv) > 3 else 400
f = open(cap, 'rb'); act = False; seq = []; st = {'cc': 0, 'om': 0, 'prim': 0, 'env': 0}
def push(k):
    if seq and seq[-1][0] == k: seq[-1][1] += 1
    else: seq.append([k, 1])
while True:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753:
        _, sw = struct.unpack('<QI', f.read(12))
        if sw > want: break
        act = sw == want; continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if not act: f.seek(n, 1); continue
    c = f.read(n); a = 0; rw = lambda o: struct.unpack('<I', c[o:o + 4])[0]
    while a + 8 <= n:
        w0 = rw(a); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): l = 16
        w1 = rw(a + 4)
        if op == 0x3C: push('CC %06X%08X' % (w0 & 0xFFFFFF, w1))
        elif op == 0x2F: push('OM %06X%08X' % (w0 & 0xFFFFFF, w1))
        elif op == 0x3A: push('PRIM %08X' % w1)
        elif op == 0x3B: push('ENV %08X' % w1)
        elif 8 <= op <= 15:
            k = 'TRI%X' % op
            if op & 4:  # shade: first coefficient words r,g,b,a integer parts
                s0, s1 = rw(a + 32), rw(a + 36); k += ' rgba %02X%02X%02X%02X' % ((s0 >> 16) & 0xFF, s0 & 0xFF, (s1 >> 16) & 0xFF, s1 & 0xFF)
            push(k)
        elif op in (0x24, 0x25): push('RECT%X' % op)
        a += l
for k, nn in seq[:mx]: print('%5d  %s' % (nn, k))
print('groups', len(seq))
