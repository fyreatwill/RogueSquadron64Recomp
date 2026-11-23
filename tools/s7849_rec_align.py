#!/usr/bin/env python3
"""s7849: 460-word player-record aligner (scratch/s7847/al2.py generalised). usage: s7849_rec_align.py RETAIL_ORACLE_LOG PORT_RUN_LOG
Greedy-aligns each port [ramdump] 460-w row to the best retail row within a 25-row window; reports ndiff transitions,
a 150-row sample, and the first row with a non-pose, non-alloc differing word (None = record identical)."""
import importlib.util, struct, sys, os
sp = importlib.util.spec_from_file_location('c', os.path.join(os.path.dirname(os.path.abspath(__file__)), 's7834_ramdump_cmp.py'))
c = importlib.util.module_from_spec(sp); sp.loader.exec_module(c)
R = [r[1] for r in c.rows(sys.argv[1]) if len(r[1]) == 460]; P = [r[1] for r in c.rows(sys.argv[2]) if len(r[1]) == 460]
F = lambda v: struct.unpack('>f', struct.pack('>I', v))[0]
POSE = set(range(430, 448)) | {4, 5, 6, 160, 161, 162}; ALLOC = {133, 146}
# s7850: w115/w116 (craft rumble handle/prio) are TIMING-class: the oracle's SI pass can preempt updatePlayerCraftPhysics mid-frame
# (r4: 3/23 rumble calls after a mid-frame pass), shifting effect expiry by one pass; the port finishes a frame before the next
# VI. They are excluded from the nonpose verdict and reported by the event check below instead.
TIMING = {115, 116}
nd = lambda a, b: [q for q in range(460) if a[q] != b[q]]
dist = lambda a, b: sum(abs(F(a[q]) - F(b[q])) for q in (4, 5, 6))
j = 0; prev = None; out = []
for i in range(len(P)):
    js = range(j, min(len(R), j + 25))
    if not js: break
    j = min(js, key=lambda t: (len(set(nd(P[i], R[t])) - POSE - ALLOC - TIMING), dist(P[i], R[t])))
    d = frozenset(nd(P[i], R[j])) - ALLOC; nonpose = d - POSE - TIMING
    out.append((i, j, len(d), len(nonpose), dist(P[i], R[j])))
    if prev is None or len(d ^ prev) > 2:
        print('port', i, 'retail', j, 'ndiff', len(d), 'nonpose', len(nonpose), 'dpos %.4f' % dist(P[i], R[j]))
    prev = d
print('rows port', len(P), 'retail', len(R), 'aligned', len(out))
print('--- every 150 rows (port,retail,ndiff,nonpose,dpos)')
for o in out[::150]: print(o[:4], '%.4f' % o[4])
print('total differing words', sum(o[2] for o in out))
print('first nonpose diff row', next((o for o in out if o[3] > 0), None))
# s7849: record words 115/116 (= player obj 0x80137DBC +0x1C0/+0x1C4) are the craft's rumble handle and priority, written by
# updatePlayerCraftPhysics 0x800B2CE0 from startRumbleEffect 0x80002ADC (gated by isRumbleSlotActive 0x80003150). Compare the
# event sequence (handle increments with their priority), which row sampling cannot add to or drop from.
def ev(rows):
    out, prev = [], None
    for r in rows:
        if r[115] != prev and r[115] != 0xFFFFFFFF: out.append((r[115], r[116]))
        prev = r[115]
    return out
er, ep = ev(R), ev(P)
k = next((i for i in range(min(len(er), len(ep))) if er[i] != ep[i]), None)
print('(timing-class, s7850) rumble events retail', len(er), 'port', len(ep), 'first differing event', k,
      '' if k is None else 'retail %s port %s' % ([(hex(a), b) for a, b in er[k:k+3]], [(hex(a), b) for a, b in ep[k:k+3]]))
