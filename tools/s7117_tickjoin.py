#!/usr/bin/env python3
"""s7117 fps60-wall-frame: which sim tick does a swap draw, and do the s7116 non-pierce losses pierce at another tick? (offline)

usage: s7117_tickjoin.py push.txt tris.bin losscan.txt      (an s7115-recipe capture; reuses tools/s7115_neargap.py verbatim
       up to its analysis section: parsing, basis, surface, geo(), the loss rule and controls 1-2 print first)
FPS60 is a real 60 Hz sim (docs/FPS60-FIXES.md), so there is no interpolated render eye: the only join freedom is WHICH tick's camera
built the display list a swap presents. s7115 joins a swap to the last bv tick <= swap (tick_m). Here, per offset k (tick index j+k):
  - pierce rate on eye-cell losses vs a flight-swap sample (the correct offset maximises the loss/flight ratio: positive control,
    because the pierce class is known real from the s7116 NEARLIFT toggle);
  - per loss that does NOT pierce at k=0: pierce at any k in -3..+2, dmin per k, tick-to-swap gap, on/off second.
Verdicts: H-join if the non-pierce losses pierce at the offset the pierce class itself prefers; H-proj/H-other if none pierce anywhere."""
import sys, random
src = open(__file__.replace('s7117_tickjoin.py', 's7115_neargap.py')).read()
exec(compile(src[:src.index('cache = {}')], 's7115_neargap.py', 'exec'))
KS = range(-3, 3)
def tj(m):
    j = bisect.bisect_left(bm, m) - 1
    return j if j >= 0 and m - bm[j] <= 40 * 24e3 else None
memo = {}
def P(j):
    if j < 0 or j >= len(TU): return None
    if j not in memo:
        t = TU[j]; bs = basis(t); H = surf(t); e = t['bv'][1]
        cut, tot, out, npts, _, ray = geo(e, bs, H); *_, dmin, _ = geo(e, bs, H, 3.0)
        memo[j] = (cut > 0, dmin if dmin is not None else 9.0)
    return memo[j]
gaps = sorted((m - bm[tj(m)]) / 24e3 for m in fl if tj(m) is not None)
print(f'swap - joined tick (ms): p10/p50/p90 {gaps[len(gaps)//10]:.1f}/{gaps[len(gaps)//2]:.1f}/{gaps[9*len(gaps)//10]:.1f}; '
      f'tick spacing near losses (ms) shown per loss')
lm = [SWM[s] for s in loss]
random.seed(7117); fsm = random.sample(fl, min(600, len(fl)))
for lab, sel in (('off', lambda m: par(m) == 0), ('on', lambda m: par(m) == 1)):
    L = [tj(m) for m in lm if sel(m) and tj(m) is not None]; Fs = [tj(m) for m in fsm if sel(m) and tj(m) is not None]
    row = []
    for k in KS:
        a = [P(j + k) for j in L]; a = [x for x in a if x]; b = [P(j + k) for j in Fs]; b = [x for x in b if x]
        pl = sum(x[0] for x in a) / max(len(a), 1); pf = sum(x[0] for x in b) / max(len(b), 1)
        row.append(f'k{k:+d} loss {pl:.2f} flight {pf:.3f} ratio {pl / max(pf, 1e-3):5.1f}')
    print(f'OFFSET SCAN {lab:3s} (losses {len(L)}, flight {len(Fs)}): ' + ' | '.join(row))
print('NON-PIERCE LOSSES (pierce at k=0 false): t  on  gap_ms  dt_prev_ms | pierce k-3..k+2 | dmin k-3..k+2')
NP = 0; NPany = collections.Counter()
for m in lm:
    j = tj(m)
    if j is None or not P(j) or P(j)[0]: continue
    NP += 1
    ps = [P(j + k) for k in KS]
    for k, x in zip(KS, ps):
        if x and x[0]: NPany[k] += 1
    if any(x and x[0] for x in ps): NPany['any'] += 1
    dtp = (bm[j] - bm[j - 1]) / 24e3 if j else -1
    print(f'  {m / 24e6:9.2f} {par(m)} {(m - bm[j]) / 24e3:5.1f} {dtp:5.1f} | '
          + ' '.join('-' if x is None else str(int(x[0])) for x in ps) + ' | ' + ' '.join('-' if x is None else f'{x[1]:.2f}' for x in ps))
print(f'NON-PIERCE SUMMARY n {NP}: pierce at k ' + ' '.join(f'{k:+d}:{NPany[k]}' for k in KS) + f' any {NPany["any"]}')
# ---- re-class with the k=-1 join (the offset the pierce class prefers in every run), vs a flight base rate
print('RECLASS k=-1 join (off+on): class counts, dmin hist (near units; 9 = none <3), share of ticks after a 33 ms gap')
def dtp(j): return (bm[j] - bm[j - 1]) / 24e3 if j > 0 else 0
def row(lab, js):
    a = [(P(j - 1), dtp(j - 1)) for j in js if P(j - 1)]
    n = len(a); h = collections.Counter(min(x[0][1], 3.0) if not x[0][0] else 0 for x in a)
    print(f'  {lab:22s} n {n:4d} pierce {sum(x[0][0] for x in a) / max(n, 1):.3f} | dmin(non-pierce) ' +
          ' '.join(f'{k:.2f}:{v / max(n, 1):.3f}' for k, v in sorted(h.items()) if k) +
          f' | dt>25ms {sum(1 for x in a if x[1] > 25) / max(n, 1):.3f}')
for lab, sel in (('off', lambda m: par(m) == 0), ('on', lambda m: par(m) == 1)):
    row(f'loss {lab}', [tj(m) for m in lm if sel(m) and tj(m) is not None])
    row(f'flight {lab}', [tj(m) for m in fsm if sel(m) and tj(m) is not None])
# ---- confound control: is a 33 ms step just a marker of near-wall (heavy) scenes? dt>25 on flight split by wall proximity,
#      plus the game's own ch dt field (not log spacing) on loss ticks vs flight
DT = {}
for line in open(pushf, errors='replace'):
    if line.startswith('ch ') and 'cam=' + FC in line:
        d = dict(kv.findall(line)); DT[int(d['m'])] = float(d['dt'])
gdt = lambda j: DT.get(TU[j]['m'])
allj = [tj(m) for m in fl if tj(m) is not None and tj(m) > 1]
near = [j for j in allj if P(j - 1)[0] or P(j - 1)[1] <= 1.5]
random.seed(1); farj = [j for j in random.sample(allj, min(800, len(allj))) if not (P(j - 1)[0] or P(j - 1)[1] <= 1.5)]
for lab, js in (('flight near-wall (pierce|dmin<=1.5)', near), ('flight far', farj), ('loss', [tj(m) for m in lm if tj(m) is not None])):
    n = len(js); g = [gdt(j - 1) for j in js]
    print(f'CONFOUND {lab:36s} n {n:5d} logspacing>25ms {sum(1 for j in js if dtp(j - 1) > 25) / max(n, 1):.3f} '
          f'game dt>0.025 {sum(1 for x in g if x and x > 0.025) / max(n, 1):.3f} (dt known {sum(1 for x in g if x) / max(n, 1):.2f})')
