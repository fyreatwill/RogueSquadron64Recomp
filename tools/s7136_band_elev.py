# s7136: world elevation/azimuth (deg) of view rays through sky-band vertices (s7134_band.py txt) and hole (magenta) pixels of a frame_replay16 frame; camera from the capture RAM. usage: s7136_band_elev.py cap swap band.txt frame.rgb k
import struct, sys, math, re
cap, sw, txt, rgb, k = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4], float(sys.argv[5])
def F(r, va): o = va & 0xFFFFFF; return struct.unpack('<f', r[o:o+4])[0]
f = open(cap, 'rb'); s = None; R = None
while True:
    t = f.read(4)
    if len(t) < 4: break
    t = struct.unpack('<I', t)[0]
    if t == 0x50415753:
        m, s = struct.unpack('<QI', f.read(12))
        if s > sw: break
    elif t == 0x204D4152:
        if s == sw: r = f.read(0x1000000); P = struct.unpack('<I', r[0x138D1C:0x138D20])[0]; R = [F(r, P+0x28+4*i) for i in range(9)]; fov = F(r, 0x80138D20+0x20)
        else: f.seek(0x1000000, 1)
    elif t == 0x20474E52:
        lo, n = struct.unpack('<II', f.read(8)); f.seek(n, 1)
rt = (R[0], R[3], R[6]); up = (R[1], R[4], R[7]); fw = (R[2], R[5], R[8]); ty = math.tan(math.radians(fov)/2); tx = ty*4/3*k
d = open(rgb, 'rb').read(); W, H = struct.unpack('<II', d[:8]); p = d[8:]
def el(x, y, sgn=1):
    nx = (x - W/2)/(W/2); ny = (H/2 - y)/(H/2)
    v = [fw[i] + sgn*nx*tx*rt[i] + ny*ty*up[i] for i in range(3)]
    return math.degrees(math.asin(v[1]/math.sqrt(sum(c*c for c in v))))
for sgn in (1, -1):
    vs = []
    for l in open(txt):
        if ' opE ' not in l or 'om 002C' not in l: continue
        for x, y in re.findall(r'\(([-\d.]+),([-\d.]+)\)', l): vs.append((float(x), float(y)))
    e = sorted(el(x, y, sgn) for x, y in vs)
    print('sgn', sgn, 'fov %.1f' % fov, 'band vertex elev min %.1f max %.1f' % (e[0], e[-1]), 'deciles', ' '.join('%.1f' % e[i*len(e)//10] for i in range(10)))
    hole = [(x, y) for y in range(H) for x in range(W) if p[(y*W+x)*3] > 240 and p[(y*W+x)*3+1] < 16 and p[(y*W+x)*3+2] > 240]
    if hole:
        he = sorted(el(x, y, sgn) for x, y in hole); print('   hole px', len(hole), 'elev min %.1f med %.1f max %.1f' % (he[0], he[len(he)//2], he[-1]))
    print('   corners', ' '.join('%.1f' % el(x, y, sgn) for x, y in ((0, 0), (W-1, 0), (0, H-1), (W-1, H-1))), ' 4:3 corners', ' '.join('%.1f' % el(x, y, sgn) for x, y in ((W/2-W/2/k, 0), (W/2+W/2/k, 0), (W/2-W/2/k, H-1), (W/2+W/2/k, H-1))))
def ae(x, y):
    nx = (x - W/2)/(W/2); ny = (H/2 - y)/(H/2)
    v = [fw[i] - nx*tx*rt[i] + ny*ty*up[i] for i in range(3)]; n = math.sqrt(sum(c*c for c in v))
    return math.degrees(math.atan2(v[0], v[2])), math.degrees(math.asin(v[1]/n))
print('split check (664,300) (664,447) (300,93) (100,93):', ['(%.1f,%.1f)' % ae(*q) for q in ((664,300),(664,447),(300,93),(100,93))])
for l in open(txt):
    if ' opE ' not in l or 'om 002C' not in l: continue
    vs = [(float(x), float(y)) for x, y in re.findall(r'\(([-\d.]+),([-\d.]+)\)', l)]
    if min(x for x, y in vs) < 400 and max(y for x, y in vs) > 250:
        print(l.split()[0], l.split()[6], ' '.join('[%.0f,%.0f az%.1f el%.1f]' % ((x, y) + ae(x, y)) for x, y in vs))
hole = [(x, y) for y in range(H) for x in range(W) if p[(y*W+x)*3] > 240 and p[(y*W+x)*3+1] < 16 and p[(y*W+x)*3+2] > 240]
A = [ae(x, y) for x, y in hole[::50]]; print('hole az', min(a for a, e in A), max(a for a, e in A))
for x, y in ((5, 440), (120, 440), (240, 440), (5, 360), (100, 350)): print('hole sample', x, y, '%.1f %.1f' % ae(x, y))
