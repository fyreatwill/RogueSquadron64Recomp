#!/usr/bin/env python3
"""s6815 G3 FPS60 hit attribution over ROGUESQ_RAND_TRACE logs (lvl14 recipe scratch/s6814/run.sh + seeds.sh: 800FA730
tick rows carry the player object m=80137db0, hp float = word 51). Game time = tick-row ordinal / hz (30 or 60, from the
run name a30*/b60*). Prints (1) per-caller rand rate per game second across all runs with an overlap flag, (2) per run:
impact effects (randomlyScaledEffectNpcHandler 0x800606F4 onsets) per game second, hp hits (>5 hp) per game second, and
how many impacts land a hit within 0.1 s. Usage: g3_fps60_hit_attrib.py <dir> a30 a30_s1 ... b60 b60_s1 ..."""
import sys, struct, collections, re, bisect
fl = lambda w: struct.unpack('>f', struct.pack('>I', w))[0]
D = sys.argv[1]; RUNS = sys.argv[2:]
s = open('syms/rogue_squadron.syms.toml').read()
E = sorted((int(v, 16), n) for n, v in re.findall(r'name\s*=\s*"([^"]+)"\s*,\s*vram\s*=\s*(0x[0-9A-Fa-f]+)', s)); K = [e[0] for e in E]
nm = lambda a: E[bisect.bisect_right(K, a) - 1][1]
def load(f):
    ticks = []
    for ln in open('%s/%s.rand.txt' % (D, f)):
        x = ln.split()
        if len(x) < 4: continue
        if x[2] == '800fa730':
            m = [y for y in x[4:] if y.startswith('m=80137db0')]
            ticks.append([fl(int(m[0].split(':')[1].split(',')[51], 16)) if m else None, collections.Counter()]); continue
        if ticks: ticks[-1][1][x[2]] += 1
    return ticks
data = {f: load(f) for f in RUNS}
hzof = lambda f: int(f[1:3])
# (1) caller rates, 16..50 game s
rate = {}
for f, t in data.items():
    hz = hzof(f); c = collections.Counter()
    for hp, cc in t[16 * hz:50 * hz]: c.update(cc)
    rate[f] = {a: n / 34 for a, n in c.items()}
A = [f for f in RUNS if hzof(f) == 30]; B = [f for f in RUNS if hzof(f) == 60]
rows = []
for a in set().union(*rate.values()):
    ra = [rate[f].get(a, 0) for f in A]; rb = [rate[f].get(a, 0) for f in B]
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    if ma + mb < 0.3: continue
    sep = '<' if max(rb) < min(ra) else ('>' if min(rb) > max(ra) else '~')
    rows.append((mb / ma if ma else 99, a, ma, mb, sep))
for r, a, ma, mb, sep in sorted(rows):
    print('%5.2f %s %-40s 30Hz %8.2f/s FPS60 %8.2f/s %s' % (r, a, nm(int(a, 16))[:40], ma, mb, sep))
# (2) impacts vs hits while alive, from 16 s
for f, t in data.items():
    hz = hzof(f); W = hz // 10; i0 = 16 * hz
    end = next((i for i in range(1, len(t)) if t[i][0] is not None and t[i][0] <= 0 < (t[i - 1][0] or 0)), len(t))
    imp = [i for i in range(i0, end) if t[i][1]['800606f4'] and not t[i - 1][1]['800606f4']]
    hit = [i for i in range(i0, end) if t[i - 1][0] is not None and t[i][0] is not None and t[i - 1][0] - t[i][0] > 5]
    ih = sum(any(abs(i - h) <= W for h in hit) for i in imp); hi = sum(any(abs(i - h) <= W for i in imp) for h in hit)
    T = (end - i0) / hz
    print('%-7s alive 16-%.0f s  impacts %.3f/s  hits %.3f/s  impacts->hit %d/%d  hits preceded by impact %d/%d'
          % (f, end / hz, len(imp) / T, len(hit) / T, ih, len(imp), hi, len(hit)))
