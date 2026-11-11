# s7137: per streamed swap of a G5B capture, the sky band (othermode 002C..., cc low 24 bits FFFFFF, no Z) tri count and its
# min top-y on screen; also tris drawn ABOVE the band top inside the band's x span (candidate top-fade geometry). usage: cap [every]
import struct, sys
cap = sys.argv[1]; every = int(sys.argv[2]) if len(sys.argv) > 2 else 1
f = open(cap, 'rb'); s = None; cur = None; out = {}
def s32(v): return v - (1 << 32) if v & 0x80000000 else v
def sx(v, b): return (v & ((1 << b) - 1)) - ((1 << b) if v & (1 << (b - 1)) else 0)
st = {'om': 0, 'cc': 0, 'timg': 0}
while True:
    t = f.read(4)
    if len(t) < 4: break
    tag = struct.unpack('<I', t)[0]
    if tag == 0x50415753: _, s = struct.unpack('<QI', f.read(12)); continue
    if tag == 0x204D4152: f.seek(0x1000000, 1); continue
    lo, n = struct.unpack('<II', f.read(8))
    if s % every: f.seek(n, 1); continue
    c = f.read(n); p = 0; rw = lambda o: struct.unpack('<I', c[o:o + 4])[0]
    rec = out.setdefault(s, {'band': 0, 'miny': 1e9, 'tris': [], 'tex': set()})
    while p + 8 <= n:
        w0 = rw(p); op = (w0 >> 24) & 0x3F; l = 8
        if 8 <= op <= 15: l = 32 + (64 if op & 4 else 0) + (64 if op & 2 else 0) + (16 if op & 1 else 0)
        elif op in (0x24, 0x25): l = 16
        if op == 0x2F: st['om'] = ((w0 & 0xFFFFFF) << 32) | rw(p + 4)
        if op == 0x3C: st['cc'] = ((w0 & 0xFFFFFF) << 32) | rw(p + 4)
        if op == 0x3D: st['timg'] = rw(p + 4) & 0xFFFFFF
        if 8 <= op <= 15 and p + l <= n:
            w1 = rw(p + 4); yh = sx(w1, 14) / 4; yl = sx(w0, 14) / 4
            isband = (st['om'] >> 40) == 0x002C and (st['cc'] & 0xFFFFFF) == 0xFFFFFF
            if isband: rec['band'] += 1; rec['miny'] = min(rec['miny'], yh); rec['tex'].add(st['timg'])
            rec['tris'].append((yh, yl, isband, st['timg']))
        p += l
for s in sorted(out):
    r = out[s]
    if not r['band']: print(s, 'band 0'); continue
    above = sum(1 for yh, yl, b, tx in r['tris'] if not b and yl <= r['miny'] + 1 and yh >= 0)
    print(s, 'band', r['band'], 'miny %.1f' % r['miny'], 'tris-above-band', above, 'tex', ' '.join('%X' % x for x in sorted(r['tex'])))
