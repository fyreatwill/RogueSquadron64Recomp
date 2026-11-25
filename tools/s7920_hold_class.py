#!/usr/bin/env python3
"""s7920 G5c: classify every VI-origin hold >= thr in ROGUESQ_PRESENT_RING files as a scene TRANSITION or an IN-SCENE freeze.

usage: s7920_hold_class.py <ring[.zst]>... [--thr-ms 250] [--win 10] [--jobs 2] [--quiet]

A hold = Q rows keep coming but vi= (the VI origin shown) does not change for >= thr (the picture is frozen; s7919_gap_check).
  TRANSITION: the set of framebuffer origins shown in the `win` rows after the hold differs from the `win` rows before it.
              The game re-allocated its colour buffers: a mode/scene change (boot, menu, mission load, cutscene cut). The game
              itself stopped swapping across its own reconfiguration -> load-class, outside the G5c bar.
  IN-SCENE:   exactly the same framebuffer set resumes after the hold. The picture froze inside one scene -> the G5c defect class.
Also reports gen/frame (ring gen= delta per row, a proxy of per-frame RDP work) before vs after.
Control (same run, per file with >= 200 rows): a copy of the rows with one planted 300 ms in-scene hold (mid-file, same
pair resumes) must classify IN-SCENE, and one planted hold followed by a relabelled pair (new addresses) must classify
TRANSITION; else the file is void (exit 3 if any file is void).
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import zopen
from multiprocessing import Pool

def load(path):
    with zopen(path) as f:
        data = f.read()
    Q = []
    for l in data.split('\n')[:-1]:
        if not l.startswith('Q ') or ' vi=' not in l: continue
        p = l.split()
        try:
            t = float(p[1]); d = dict(x.split('=', 1) for x in p[2:] if '=' in x)
            Q.append((t, d['vi'], int(d.get('gen', '0') or 0)))
        except (ValueError, KeyError):
            continue
    return Q

def classify(Q, thr, win):
    out = []; i = 0; n = len(Q)
    while i < n - 1:
        j = i
        while j + 1 < n and Q[j + 1][1] == Q[i][1]: j += 1
        if j + 1 < n and (Q[j + 1][0] - Q[i][0]) * 1e3 >= thr:
            k = i - 1
            while k >= 0 and Q[k][1] == Q[i][1]: k -= 1   # Q[i] starts the run of identical origins
            before = Q[max(0, i - win):i + 1]; after = Q[j + 1:j + 1 + win]
            bset = {r[1] for r in before}; aset = {r[1] for r in after}
            cls = 'IN-SCENE' if bset == aset else 'TRANSITION'   # s7920: a dropped/added buffer (pair -> single) is a reconfiguration too
            def rate(rs): return (rs[-1][2] - rs[0][2]) / max(1, len(rs) - 1) if len(rs) > 1 else 0
            out.append(dict(t=Q[i][0] - Q[0][0], ms=(Q[j + 1][0] - Q[i][0]) * 1e3, cls=cls,
                            b=sorted(bset), a=sorted(aset), gb=rate(before), ga=rate(after)))
        i = j + 1
    return out

def planted(Q, thr, win, newpair):
    """Insert a 300 ms hold at the middle of the longest stretch whose last 2*win rows alternate >=2 origins."""
    m = len(Q) // 2
    # find a row m with >=2 distinct origins in the win rows around it and not inside an existing hold
    for off in range(0, len(Q) // 2 - win - 2):
        for mm in (m + off, m - off):
            if win < mm < len(Q) - win - 2 and len({r[1] for r in Q[mm - win:mm + win]}) >= 2:
                m = mm; break
        else: continue
        break
    t0, v0, g0 = Q[m]; d = 0.3
    P = Q[:m + 1] + [(t0 + d * k / 10, v0, g0) for k in range(1, 10)]
    tail = [(t + d, v, g) for t, v, g in Q[m + 1:]]
    if newpair:
        tail = [(t, 'NEW' + v, g) for t, v, g in tail]
    else:
        tail = [r for r in tail]
        # make sure the first row after the hold differs from v0 but the pair is the old one
        while tail and tail[0][1] == v0: tail.pop(0)
    P += tail
    hits = [h for h in classify(P, thr, win) if abs(h['t'] - (t0 - Q[0][0])) < 1e-3]
    return t0 - Q[0][0], (hits[0]['cls'] if hits else None)

def one(args):
    path, thr, win = args
    Q = load(path)
    if len(Q) < 200: return path, len(Q), None, None, []
    H = classify(Q, thr, win)
    c1 = planted(Q, thr, win, False)[1] == 'IN-SCENE'
    c2 = planted(Q, thr, win, True)[1] == 'TRANSITION'
    return path, len(Q), c1, c2, H

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('rings', nargs='+'); ap.add_argument('--thr-ms', type=float, default=250)
    ap.add_argument('--win', type=int, default=10); ap.add_argument('--jobs', type=int, default=2); ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    void = 0; tot = dict(T=0, I=0); files = 0
    with Pool(min(a.jobs, 2)) as pool:   # iron rule 0
        for path, n, c1, c2, H in pool.imap(one, [(p, a.thr_ms, a.win) for p in a.rings]):
            if c1 is None:
                if not a.quiet: print('%s rows=%d too few -> skipped' % (path, n))
                continue
            files += 1
            if not (c1 and c2): void += 1
            nt = sum(h['cls'] == 'TRANSITION' for h in H); ni = len(H) - nt; tot['T'] += nt; tot['I'] += ni
            if a.quiet and ni == 0 and c1 and c2: continue
            print('%s rows=%d holds=%d transition=%d in_scene=%d control_in=%s control_tr=%s' % (path, n, len(H), nt, ni, c1, c2))
            for h in H:
                if a.quiet and h['cls'] != 'IN-SCENE': continue
                print('  %-10s t=%7.1f s %6.0f ms  before=%s after=%s gen/frame %.0f -> %.0f' % (
                    h['cls'], h['t'], h['ms'], ','.join(h['b']), ','.join(h['a']), h['gb'], h['ga']))
    print('files=%d void=%d holds_transition=%d holds_in_scene=%d' % (files, void, tot['T'], tot['I']))
    sys.exit(3 if void else 0)

if __name__ == '__main__':
    main()
