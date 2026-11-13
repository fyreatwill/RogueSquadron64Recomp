# s7251: host-clock ratio between two runs of the same recipe, from their [g1b] per-second lines.
# usage: python3 tools/s7251_clock_ratio.py SLOW_g1b.txt:REF_g1b.txt [...]   (grep '^\[g1b\] t=' out of a game log first)
# A constant sd_cpu ratio across light and heavy windows (s7249: 1.37-1.44) is a clock cap (battery Low Power Mode, s7250),
# not contention (which adds wall-cpu wait, not CPU per task). Ratio ~1.00 = same host state.
import re,sys
def load(p):
    d={}
    for l in open(p):
        m=re.search(r't=(\d+) vi=(\d+) tasks=(\d+) sd_wall=([\d.]+)/(\d+) sd_cpu=([\d.]+)/(\d+).*load1=([\d.]+) qos=(\S+)',l)
        if m: d[int(m[1])]=(int(m[3]),float(m[4]),float(m[6]),float(m[8]),m[9])
    return d
for pair in sys.argv[1:]:
    a,b=pair.split(':'); s,f=load(a),load(b)
    print(f'== {a} vs {b}')
    rs=[]
    for lo,hi in ((2,20),(20,40),(40,60),(60,77),(77,97),(97,140),(140,200),(200,240)):
        ks=[k for k in range(lo,hi) if k in s and k in f]
        if not ks: continue
        av=lambda d,i:sum(d[k][i] for k in ks)/len(ks)
        r=av(s,2)/max(av(f,2),1e-9); rs.append(r) if lo>=20 else None
        print(f' t{lo:3}-{hi:3} tasks {av(s,0):5.1f}/{av(f,0):5.1f} cpu {av(s,2):5.2f}/{av(f,2):5.2f} ratio {r:4.2f} wall {av(s,1):5.2f}/{av(f,1):5.2f} load {av(s,3):4.2f}/{av(f,3):4.2f}')
    print(f' ratio t>=20 range {min(rs):.2f}-{max(rs):.2f}; qos',set(v[4] for v in s.values()),set(v[4] for v in f.values()))
