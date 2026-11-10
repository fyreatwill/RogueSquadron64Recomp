#!/usr/bin/env python3
"""s7098 G5b: are the presented-frame transients (g5b_drops) already in the RDP stream, or RT64-only?
For each transient presented frame x (and its steady neighbours a = x-1, b = x+k) take every swap whose SWAP time lies within
[T - win, T] of that frame's display time, replay them through angrylion (frame_replay16, nearest earlier RAM snapshot) and score
min over candidate swaps of block-diff(angrylion, presented).
  Sx at floor           -> some swap's hardware render IS the transient picture: H-stream (the stream carries it)
  Sx high, Sa/Sb floor  -> RT64 shows a picture no nearby swap produces on the RDP: H-rt64
  all high              -> unmatchable (scene cut / stale texture); not counted
usage: s7098_transients.py plan  drops.csv idx raw out.swaps [t1_mach]       (lists swaps to replay)
       s7098_transients.py judge drops.csv idx raw aldir out.csv [t1_mach]
"""
import sys, os, bisect, statistics, struct
sys.path.insert(0, os.path.dirname(__file__))
import importlib.util
spec = importlib.util.spec_from_file_location('rv', os.path.join(os.path.dirname(__file__), 's7098_rt64_vs_al.py'))
rv = importlib.util.module_from_spec(spec); spec.loader.exec_module(rv)
WIN = 2400000  # 100 ms of 24 MHz ticks
PY0 = 9        # window title bar rows in the 384x216 recording

def drops(path, t1):
    out = []
    for i, line in enumerate(open(path)):
        if i == 0: continue
        p = line.strip().split(',')
        idx, k, T, m = int(p[0]), int(p[3]), float(p[4]), int(p[6])
        if m <= t1: out.append((idx, k, T))
    return out

def swaps(idx):
    S, M = [], []
    for line in open(idx):
        s, m = map(int, line.split()[:2]); S.append(s); M.append(m)
    return S, M

def cands(S, M, t):
    j = bisect.bisect_right(M, t); i = bisect.bisect_left(M, t - WIN)
    return S[i:j]

def main():
    mode, dcsv, idx, raw = sys.argv[1:5]
    S, M = swaps(idx); f, w, h, rec, T = rv.load_raw(raw)
    t1 = int(sys.argv[6 if mode == 'plan' else 7]) if len(sys.argv) > (6 if mode == 'plan' else 7) else 1 << 63
    D = drops(dcsv, t1)
    if mode == 'plan':
        want = set()
        for x, k, _ in D:
            for n in (x - 1, x, x + k):
                if 0 <= n < len(T): want.update(cands(S, M, T[n]))
        open(sys.argv[5], 'w').write(' '.join(str(s) for s in sorted(want)) + '\n'); print('transients', len(D), 'swaps', len(want)); return
    aldir, out = sys.argv[5], sys.argv[6]
    al = {}
    for fn in os.listdir(aldir):
        if fn.endswith('.rgb'):
            r = rv.load_al(os.path.join(aldir, fn))
            if r: al[int(fn[1:-4])] = r[0]
    cache = {}
    def pres(n):
        if n not in cache:
            f.seek(n * rec + 16); cache[n] = rv.blocks_rgb(f.read(w * h * 3), w, h, 0, PY0, 370, h)
        return cache[n]
    def best(n):
        c = [s for s in cands(S, M, T[n]) if s in al]
        if not c: return None, None
        sc = [(rv.diffscore(al[s], pres(n)), s) for s in c]; return min(sc)
    o = open(out, 'w'); o.write('pidx,k,T,Sx,sx,Sa,Sb,verdict\n'); tally = {}
    for x, k, Tt in D:
        Sx, sx = best(x); Sa, _ = best(x - 1); Sb, _ = best(x + k)
        if Sx is None or Sa is None or Sb is None: v = 'nocand'
        elif Sa > 0.10 or Sb > 0.10: v = 'unmatched'
        elif Sx <= max(Sa, Sb) + 0.03: v = 'H-stream'
        else: v = 'H-rt64'
        tally[v] = tally.get(v, 0) + 1
        o.write('%d,%d,%.3f,%s,%s,%s,%s,%s\n' % (x, k, Tt, '%.3f' % Sx if Sx is not None else '', sx, '%.3f' % Sa if Sa is not None else '', '%.3f' % Sb if Sb is not None else '', v))
    print('verdicts', tally)

if __name__ == '__main__':
    main()
