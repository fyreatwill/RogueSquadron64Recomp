#!/usr/bin/env python3
"""s7854: tick-keyed 460-word player-record compare, retail oracle vs port, for levels where the s7834 [ramdump] PC
(0x80043918, inside buildVisibleTerrainGridAroundCamera) does not run per tick (0x31=10 Bespin: no terrain grid, 1 row each
side). Both sides dump 0x80137DB0..0x801384E0 at the runInMissionFrame tick marker 0x800FA730 through the XTRACE_MEM spec
that tools/s7849_det_pair.sh adds with REC=1 (7x64 + 1x12 words; oracle RS64_XTRACE_MEM / port ROGUESQ_XTRACE_MEM, max 16
specs x 64 words on both sides). Tick k = k-th 0x800FA730 row, the same key s7845_rng_tick_cmp.py uses.
Word classes are the s7849_rec_align.py ones (POSE / ALLOC / TIMING).
usage: s7854_tick_rec_cmp.py RETAIL_ORACLE_LOG PORT_RAND_TXT [--control TICK]
  --control TICK flips word 50 of the port record at TICK: the scorer must report that tick as the first nonpose diff."""
import re, struct, sys
TICK, BASE, NW = 0x800FA730, 0x80137DB0, 460
POSE = set(range(430, 448)) | {4, 5, 6, 160, 161, 162}; ALLOC = {133, 146}; TIMING = {115, 116, 135, 149}
seg = re.compile(r'm=([0-9a-f]{8}):([0-9a-f,]+)')
F = lambda v: struct.unpack('>f', struct.pack('>I', v))[0]

def load(path, retail):
    out = []
    for l in open(path, errors='replace'):
        if retail:
            if not l.startswith('[xtrace] ') or ' pc=800fa730' not in l: continue
        else:
            f = l.split(None, 3)
            if len(f) < 3 or f[2] != '800fa730': continue
        w = {}
        for a, vs in seg.findall(l):
            a = int(a, 16)
            for k, v in enumerate(vs.split(',')):
                w[a + 4 * k] = int(v, 16)
        rec = [w.get(BASE + 4 * q) for q in range(NW)]
        out.append(rec if None not in rec else None)
    return out

R = load(sys.argv[1], True); P = load(sys.argv[2], False)
ctl = int(sys.argv[sys.argv.index('--control') + 1]) if '--control' in sys.argv else None
if ctl is not None and ctl < len(P) and P[ctl]:
    P[ctl] = list(P[ctl]); P[ctl][50] ^= 1
n = min(len(R), len(P)); full = [k for k in range(n) if R[k] and P[k]]
print(f'ticks retail {len(R)} port {len(P)}; ticks with a full 460-w record on both sides {len(full)}')
if not full:
    print('NO RECORD ROWS (spec not armed?) -> no verdict'); sys.exit(2)
first_np = first_t = None; np_ticks = 0; wc = {}; maxd = 0.0; maxd_k = None; first_pose = None
for k in full:
    d = [q for q in range(NW) if R[k][q] != P[k][q]]
    np = [q for q in d if q not in POSE | ALLOC | TIMING]
    tm = [q for q in d if q in TIMING]
    if d and first_pose is None and any(q in POSE for q in d): first_pose = k
    if np:
        np_ticks += 1
        for q in np: wc[q] = wc.get(q, 0) + 1
        if first_np is None: first_np = (k, np[:12])
    if tm and first_t is None: first_t = (k, tm)
    dp = sum(abs(F(R[k][q]) - F(P[k][q])) for q in (4, 5, 6))
    if dp > maxd: maxd, maxd_k = dp, k
print('first nonpose diff tick', first_np if first_np else None)
print('nonpose diff ticks', np_ticks, 'of', len(full), '| words (word:ticks)', sorted(wc.items(), key=lambda x: -x[1])[:12])
print('first pose-word diff tick', first_pose, '| max pos |d| %.6f at tick %s' % (maxd, maxd_k))
print('(timing-class) first TIMING-word diff tick', first_t)
