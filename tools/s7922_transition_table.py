#!/usr/bin/env python3
"""s7922 G5c: per pre-flight transition, port picture-hold length (VIs) vs the retail oracle's hold at the same transition.

usage: s7922_transition_table.py <port ring[.zst]> <oracle.log> [--thr-ms 120] [--slack 3] [--merge 3]

Port side: VI-origin holds >= thr in a ROGUESQ_PRESENT_RING (s7920_hold_class.load/classify); holds whose rows keep advancing
  gen= on >= 90% of rows are an ANIMATING single-buffer scene (the 1592-wide title, s7921 side check), not a freeze; its END is
  still a scene transition (title -> menu) and enters the table as a 0-VI port hold.
  Length in VIs = ms / 16.683.
Retail side (oracle run with --vi-holds N --hit-vi and --watch-pc 0x80091EC4 [MusyX wait taken] and 0x800A9364
  [mallocCraftSelectionData]): one transition per 0x80091EC4 hit; its hold = the [vi-hold] run containing (or starting
  <= merge VIs after) the hit VI, plus every following run that starts <= merge VIs after the previous one ends (the wait hold
  and the load hold the port may merge into one).
Matching: by transition identity, anchored at hangar entry: the port IN-SCENE hold (same fb pair before/after) <-> the retail
  transition whose group contains the mallocCraftSelectionData hit with s3=0x80130b40 (s7921). Other holds match by ordinal
  outward from the anchor. Verdict per pair: PORT-LONGER if port > retail + slack, else EQUAL (|d| <= slack) or PORT-SHORTER.
Planted controls (same run): a synthetic pair port = retail + 10 must read PORT-LONGER, an equal pair EQUAL; exit 3 otherwise.
Exit 1 if any real pair reads PORT-LONGER.
"""
import sys, os, re, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7920_hold_class import load, classify
VI_MS = 1000.0 / 59.94

def verdict(p, r, slack):
    d = p - r
    return 'PORT-LONGER' if d > slack else ('EQUAL' if abs(d) <= slack else 'PORT-SHORTER')

def port_holds(ring, thr):
    Q = load(ring)
    H = classify(Q, thr, 10)
    out = []
    t0 = Q[0][0]
    for h in H:
        rows = [r for r in Q if h['t'] <= r[0] - t0 <= h['t'] + h['ms'] / 1e3]
        adv = sum(1 for a, b in zip(rows, rows[1:]) if b[2] != a[2])
        frac = adv / max(1, len(rows) - 1)
        if h['ms'] > 2000 and frac >= 0.9:
            h['skip'] = 'ANIMATING gen %.0f%%' % (100 * frac)
        h['vis'] = h['ms'] / VI_MS
        out.append(h)
    return out

def retail_groups(log, merge):
    holds, waits, hangar = [], [], None
    for l in open(log, errors='replace'):
        m = re.match(r'\[vi-hold\] vi=(\d+)\.\.(\d+) len=(\d+) t=([\d.]+)s width=(\d+)', l)
        if m: holds.append(tuple(int(m.group(i)) for i in (1, 2, 3)) + (int(m.group(5)),)); continue
        if l.startswith('[hit]') and 'pc=0x80091ec4' in l:
            waits.append(int(re.search(r' vi=(\d+)', l).group(1)))
        if l.startswith('[hit]') and 'pc=0x800a9364' in l and 's3=0x80130b40' in l:
            hangar = int(re.search(r' vi=(\d+)', l).group(1))
    G = []
    for w in waits:
        first = [h for h in holds if h[0] <= w <= h[1] or 0 <= h[0] - w <= merge]
        if not first:
            G.append(dict(vi=w, a=w, b=w, len=0, widths=[], hangar=False)); continue
        grp = [first[0]]
        for h in holds:
            if h[0] > grp[-1][1] and h[0] - grp[-1][1] - 1 <= merge: grp.append(h)
        a, b = grp[0][0], grp[-1][1]
        G.append(dict(vi=w, a=a, b=b, len=b - a + 1, widths=sorted({g[3] for g in grp}),
                      parts=[g[2] for g in grp], hangar=hangar is not None and a <= hangar <= b))
    return G, hangar, len(holds)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ring'); ap.add_argument('oracle')
    ap.add_argument('--thr-ms', type=float, default=120); ap.add_argument('--slack', type=float, default=3)
    ap.add_argument('--merge', type=int, default=3)
    A = ap.parse_args()
    ok1 = verdict(27, 17, A.slack) == 'PORT-LONGER'; ok2 = verdict(17, 17, A.slack) == 'EQUAL'
    P = port_holds(A.ring, A.thr_ms); G, hv, nh = retail_groups(A.oracle, A.merge)
    # an animating single-buffer scene still has a transition at its END (e.g. title -> menu): keep it as a 0-VI port hold
    live = []
    for h in P:
        if 'skip' in h:
            live.append(dict(t=h['t'] + h['ms'] / 1e3, ms=0.0, vis=0.0, cls='END-OF-ANIMATING'))
        else:
            live.append(h)
    print('port holds >= %g ms: %d (%d animating dropped); retail vi-holds %d, MusyX waits %d, hangar hit vi=%s'
          % (A.thr_ms, len(P), sum('skip' in h for h in P), nh, len(G), hv))
    for h in P:
        if 'skip' in h: print('  dropped port t=%7.1f s %6.0f ms  %s' % (h['t'], h['ms'], h['skip']))
    pa = [i for i, h in enumerate(live) if h['cls'] == 'IN-SCENE']
    ra = [i for i, g in enumerate(G) if g['hangar']]
    ctl_anchor = len(pa) == 1 and len(ra) == 1
    print('control: planted +10 -> %s, equal -> %s, anchor port=%s retail=%s'
          % ('PORT-LONGER' if ok1 else 'FAIL', 'EQUAL' if ok2 else 'FAIL', pa, ra))
    if not (ok1 and ok2 and ctl_anchor):
        print('VOID'); sys.exit(3)
    off = ra[0] - pa[0]; longer = 0
    print('%-4s %9s %7s %9s | %-6s %-11s %7s %-14s %s' % ('#', 'port_t_s', 'port_ms', 'port_VIs', 'r_wait', 'r_hold', 'r_VIs', 'r_parts', 'verdict'))
    for i, h in enumerate(live):
        j = i + off
        if 0 <= j < len(G):
            g = G[j]; v = verdict(h['vis'], g['len'], A.slack); longer += v == 'PORT-LONGER'
            print('%-4d %9.1f %7.0f %9.1f | %-6d %5d..%-5d %7d %-14s %s%s' % (i, h['t'], h['ms'], h['vis'], g['vi'], g['a'], g['b'],
                  g['len'], '+'.join(map(str, g.get('parts', []))), v, '  [anchor: hangar entry]' if j == ra[0] else ''))
        else:
            print('%-4d %9.1f %7.0f %9.1f | (no retail twin in the oracle window)' % (i, h['t'], h['ms'], h['vis']))
    for j, g in enumerate(G):
        if not 0 <= j - off < len(live):
            print('retail-only wait vi=%d hold %d..%d (%d VIs): port shows no hold >= %g ms here'
                  % (g['vi'], g['a'], g['b'], g['len'], A.thr_ms))
    print('pairs_port_longer=%d' % longer)
    sys.exit(1 if longer else 0)

if __name__ == '__main__':
    main()
