#!/usr/bin/env python3
"""s7845: per-mission-tick rng seed + player hp, retail (rs64_oracle --exec-trace 0x80003430 --exec-trace-also 0x800FA730,
RS64_XTRACE_MEM=800FA730:0:80137E7C:1,800FA730:0:80003470:1) vs port (ROGUESQ_RAND_TRACE[_BOOT] + same ROGUESQ_XTRACE_MEM).
Per arm: tick list (seed at tick start, hp, rand calls since previous tick, rand caller multiset). Aligns tick k = k-th
0x800FA730 marker and prints: seed at first tick, first tick whose seed differs, first tick whose rand-call count or
caller sequence differs, and hp-change ticks on each side.
usage: s7845_rng_tick_cmp.py RETAIL_ORACLE_LOG PORT_RAND_TXT [shift]   (shift: port tick index = retail + shift)"""
import re, sys
RAND, TICK = 0x80003430, 0x800FA730
PORT_MARKS = {0x8006BEC8, 0x8006C018, 0x8006C010, 0x800AF374, 0x800C6674, 0x8008EE08, 0x8008EE84}  # fixup_rand_trace probes
mre = re.compile(r'm=([0-9a-f]{8}):([0-9a-f]{8})')
def load(path, retail):
    ticks, cur = [], []  # cur = rand callers since the last tick
    pre = 0
    for l in open(path, errors='replace'):
        if retail:
            if not l.startswith('[xtrace] '): continue
            f = l.split()[1:]
            pc = int(f[4][3:], 16) if len(f) > 4 and f[4].startswith('pc=') else RAND
            site = int(f[2], 16) - (8 if pc == RAND else 0)
        else:
            f = l.split()
            if len(f) < 4: continue
            site = int(f[2], 16)
            if site == TICK: pc = TICK
            elif len(f) != 4 or site in PORT_MARKS or site >> 24 != 0x80: continue  # probe/marker/other-diag rows
            else: pc = RAND
        if pc == TICK:
            m = dict((int(a, 16), int(b, 16)) for a, b in mre.findall(l))
            ticks.append({'vi': int(f[1]), 'hp': m.get(0x80137E7C), 'seed': m.get(0x80003470), 'calls': cur})
            cur = []
        elif pc == RAND:
            if ticks: cur.append(site)
            else: pre += 1
    return ticks, pre
R, rpre = load(sys.argv[1], True); P, ppre = load(sys.argv[2], False)
sh = int(sys.argv[3]) if len(sys.argv) > 3 else 0
print(f'retail ticks {len(R)} (rand calls before 1st tick {rpre}); port ticks {len(P)} (before {ppre})')
for nm, T in (('retail', R), ('port', P)):
    print(nm, 'tick0 seed %08x hp %s' % (T[0]['seed'] or 0, T[0]['hp'] and '%08x' % T[0]['hp']) if T else 'none')
F = lambda h: __import__('struct').unpack('>f', h.to_bytes(4, 'big'))[0] if h is not None else None
for nm, T in (('retail', R), ('port', P)):
    ev = [(i, F(T[i-1]['hp']), F(T[i]['hp'])) for i in range(1, len(T)) if T[i]['hp'] != T[i-1]['hp']]
    print(nm, 'hp changes (tick, old, new):', [(i, round(a, 4), round(b, 4)) for i, a, b in ev[:12]])
n = min(len(R), len(P) - sh)
fs = next((k for k in range(n) if R[k]['seed'] != P[k+sh]['seed']), None)
fc = next((k for k in range(n) if R[k]['calls'] != P[k+sh]['calls']), None)
print('first seed-differing tick:', fs, '| first call-sequence-differing tick:', fc)
if fc is not None:
    for k in range(max(0, fc-2), min(n, fc+3)):
        r, p = R[k], P[k+sh]
        print(f' tick {k}: seed r={r["seed"]:08x} p={p["seed"]:08x} ncalls r={len(r["calls"])} p={len(p["calls"])}')
        if k == fc:
            i = next((j for j in range(min(len(r['calls']), len(p['calls']))) if r['calls'][j] != p['calls'][j]), min(len(r['calls']), len(p['calls'])))
            print('   first differing call #%d  retail %s  port %s' % (i, ' '.join('%08x' % x for x in r['calls'][max(0,i-3):i+4]),
                  ' '.join('%08x' % x for x in p['calls'][max(0,i-3):i+4])))
