#!/usr/bin/env python3
"""s6826 G3 FPS60: per-site rates from two ROGUESQ_TICK_TRACE files (a30 arm, FPS60 arm) for the float sites hooked by
tools/fixup_fps60_float_trace.py (and, as controls, the s6821 integer sites).
Per pc and arm: executions per game second (ex/gs), and the per-tick change of the field: for every field address,
consecutive executions ONE mission tick apart give d = v(next) - v(prev). Reported: median |d| per tick, and for
mul-type sites the median log ratio. Discriminator (f60/a30 ratio of median |d| per tick):
  ~0.5  the update is dt-scaled (half the game time per tick)  -> fine
  ~1.0  a per-tick QUANTUM (constant step / damping per tick)   -> runs 2x per game second at FPS60
Controls: updateNpcEventTimer 0x800EFE3C (+0x10 -= dt) must read ~0.5; an integer +-1 counter that steps every tick
must read 1.0. Rows need >= MIN pairs in both arms.
Usage: g3_float_quanta_rates.py a30.tick.bin f60.tick.bin [--min N] [--sites float_sites.tsv]"""
import sys, struct, math, collections
from statistics import median

def load(path):
    t0 = None; tick_t = {}; tick_dt = {}
    by = collections.defaultdict(list)   # pc -> [(tick, addr, raw)]
    with open(path, 'rb') as f:
        data = f.read()
    for pc, a, v, tk in struct.iter_unpack('<4I', data[:len(data) // 16 * 16]):
        if pc == 0:
            tick_t[tk] = struct.unpack('<f', struct.pack('<I', a))[0]; tick_dt[tk] = struct.unpack('<f', struct.pack('<I', v))[0]
        elif pc > 2:
            by[pc].append((tk, a, v))
    gs = sum(d for d in tick_dt.values() if 0 < d < 0.2)
    return by, gs, tick_dt

def f32(u): return struct.unpack('<f', struct.pack('<I', u & 0xFFFFFFFF))[0]

def stats(recs, isf, tick_dt):
    last = {}; ds = []; lr = []
    for tk, a, v in recs:
        if tk == 0 or not (0 < tick_dt.get(tk, 0) < 0.2): continue
        x = f32(v) if isf else struct.unpack('<i', struct.pack('<I', v))[0]
        if a in last and last[a][0] == tk - 1:
            p = last[a][1]
            if isf and (math.isnan(x) or math.isnan(p) or abs(x) > 1e7 or abs(p) > 1e7): pass
            else:
                d = x - p
                if d != 0: ds.append(abs(d))
                if p != 0 and x != 0 and (x / p) > 0 and x != p: lr.append(abs(math.log(x / p)))
        last[a] = (tk, x)
    return ds, lr

if __name__ == '__main__':
    args = [a for a in sys.argv[1:]]
    MIN = int(args[args.index('--min') + 1]) if '--min' in args else 20
    sites = {}
    if '--sites' in args:
        for ln in open(args[args.index('--sites') + 1]):
            c = ln.rstrip('\n').split('\t'); sites[int(c[1], 16)] = (c[0], c[2], c[3], c[4], c[5])
    A, gA, dtA = load(args[0]); B, gB, dtB = load(args[1])
    print('# game s: a30 %.1f  f60 %.1f' % (gA, gB))
    print('%-10s %-36s %-12s %-6s %-6s %8s %8s %6s %10s %10s %6s %6s %s' % ('pc', 'func', 'field', 'op', 'kind', 'exgsA', 'exgsB',
          'exR', 'med|d|A', 'med|d|B', 'dR', 'lrR', 'nA/nB'))
    out = []
    for pc in sorted(set(A) | set(B)):
        isf = pc in sites
        fn, fld, op, oth, kind = sites.get(pc, ('int-site', '', 'addiu', '', 'INT'))
        dA, lA = stats(A.get(pc, []), isf, dtA); dB, lB = stats(B.get(pc, []), isf, dtB)
        eA = len(A.get(pc, [])) / gA if gA else 0; eB = len(B.get(pc, [])) / gB if gB else 0
        if len(dA) < MIN or len(dB) < MIN: continue
        mA, mB = median(dA), median(dB)
        dR = mB / mA if mA else float('nan')
        lrR = (median(lB) / median(lA)) if (len(lA) >= MIN and len(lB) >= MIN and median(lA)) else float('nan')
        out.append((pc, fn, fld, op, kind, eA, eB, eB / eA if eA else 0, mA, mB, dR, lrR, len(dA), len(dB)))
    for r in out:
        print('0x%08X %-36s %-12s %-6s %-6s %8.1f %8.1f %6.2f %10.4g %10.4g %6.2f %6.2f %d/%d' % (r[0], r[1][:36], r[2], r[3], r[4],
              r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13]))
