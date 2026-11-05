#!/usr/bin/env python3
"""s6896 G5b: join ROGUESQ_G5B_TG per-swap TriGen rows to ROGUESQ_G5B_SHEET sheets (op 0F, terrain blender, hull >= 100000 px).
H-wrap predicts sheets only on swaps with commands past s16. usage: g5b_tg_join.py tg_x.txt sh_x.txt [...pairs]"""
import re, sys
def sheets(p):
    d = {}
    for l in open(p, errors='replace'):
        m = re.match(r'(\d+) (\d+) op=(\w+) area=(\d+) ', l)
        if m and m[3] == '0F' and 'C8112220' in l and int(m[4]) >= 100000: d[int(m[1])] = d.get(int(m[1]), 0) + 1
    return d
def rows(p):
    for l in open(p, errors='replace'):
        m = re.match(r'S (\d+) (\d+) n=(\d+) m2=(\d+) wa=(\d+) wb=(\d+) ha=(\d+) hb=(\d+) a=(-?\d+),(-?\d+) b=(-?\d+),(-?\d+) v0=(-?\d+),(-?\d+) win=(-?\d+),(-?\d+),(-?\d+),(-?\d+) deb4=(\S+) tt=(\S*) cam=(\S*)', l)
        if m: yield m
a = sys.argv[1:]
for tg, sh in zip(a[0::2], a[1::2]):
    S = sheets(sh); n = w = h = 0; both = wonly = sonly = 0; amax = bmax = -99999; amin = bmin = 99999; ntot = 0; seen = set(); v0 = set()
    for m in rows(tg):
        sw = int(m[1]); seen.add(sw); n += 1; ntot += int(m[3]); wr = int(m[5]) + int(m[6]) > 0; w += wr; h += int(m[7]) + int(m[8]) > 0; s = sw in S
        both += wr and s; wonly += wr and not s; sonly += s and not wr
        amin = min(amin, int(m[9])); amax = max(amax, int(m[10])); bmin = min(bmin, int(m[11])); bmax = max(bmax, int(m[12])); v0 |= {int(m[13]), int(m[14])}
    print(f'{tg}: swaps {n}, trigen/swap {ntot / max(n, 1):.0f}, a [{amin},{amax}] b [{bmin},{bmax}] v0 {sorted(v0)[:6]}')
    print(f'  swaps past s16 {w}, past half range {h} (control); sheet swaps {len(S)} ({sum(S.values())} sheets), joined {len(set(S) & seen)}')
    print(f'  sheet&wrap {both}, wrap only {wonly}, sheet only {sonly}')
