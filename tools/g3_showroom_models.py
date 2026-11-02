# s6786: SHOWROOM model-index sequence per arm from the rand seeds (rand: s*=0xA8351D63, ret (s>>6)&0x7FFF).
# usage: g3_showroom_models.py RETAIL_ORACLE_LOG PORT_XT_TXT  (retail run with RANDX="--exec-trace 0x80003430:400000:3470")
# init 0x800C5764: idx = (int16)ret % 18; each flyby 0x800C4458: idx = (idx + 1 + (ret & 1)) % 18.
import sys
def rnd(s): s = (s * 0xA8351D63) & 0xFFFFFFFF; return (s >> 6) & 0x7FFF
def seq(rows):
    out, idx = [], None
    for vi, site, seed in rows:
        r = rnd(seed)
        if site == 0x800C5764: idx = r % 18; out.append((vi, 'init', idx))
        elif site == 0x800C4458 and idx is not None: idx = (idx + 1 + (r & 1)) % 18; out.append((vi, 'next', idx))
    return out
R = []
for l in open(sys.argv[1], errors='replace'):
    if l.startswith('[xtrace] '):
        f = l.split()
        if len(f) > 5 and f[5] == 'pc=80003430':
            R.append((int(f[2]), int(f[3], 16) - 8, int(f[4], 16)))  # $ra = jal + 8, peek = seed
P = [(int(f[1]), int(f[2], 16), int(f[3], 16)) for f in (l.split() for l in open(sys.argv[2])) if len(f) == 4]
print('retail', seq(R)); print('port  ', seq(P))
