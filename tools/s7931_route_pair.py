#!/usr/bin/env python3
"""s7931: port vs retail runVideoFrameTick CALLER SEQUENCE on the same save (settles s7928's single-source route reading).

usage: s7931_route_pair.py <port ring (ROGUESQ_S7928_GATEW=1)> <retail oracle.log (tools/s7931_oracle_route.sh)> [--control <ring>]
Compares caller sites only (the gate value differs by design at the B40 boot tick). The retail run is a fixed 110 s window, so
the verdict is on the common prefix: SEQ-MATCH when every one of min(len) callers agrees. Same-run controls:
  mutation  - the port sequence with its 3rd caller dropped must NOT match (instrument can tell sequences apart);
  --control - a second port ring from a different route (e.g. FORCE_SAVE_MISSION arm) must NOT match retail.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7928_gate_writers as g

NM = {0x8003E29C: 'mainGameLoop@E29C', 0x8003E360: 'mainGameLoop@E360', 0x800A9C70: 'initScene@9C70', 0x800C5A18: 'menu@5A18'}

def port_seq(ring):
    g.load(ring)
    return [pc for t, pc, n, gv in sorted(c for c in g.C if c[2] <= 16)]

def prefix(a, b):
    k = 0
    for x, y in zip(a, b):
        if x != y: break
        k += 1
    return k, min(len(a), len(b))

def verdict(a, b):
    k, m = prefix(a, b); return k, m, (m >= 4 and k == m)

def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    p = port_seq(argv[0]); r = [pc for vi, pc, w in g.oracle_callers(argv[1])]
    print('retail: ' + ' '.join(NM.get(x, hex(x)) for x in r))
    print('port:   ' + ' '.join(NM.get(x, hex(x)) for x in p))
    k, m, ok = verdict(p, r)
    mut = p[:2] + p[3:]; km, mm, okm = verdict(mut, r)
    rc = 0 if ok and not okm else 3
    ctl = ''
    if '--control' in argv:
        c = port_seq(argv[argv.index('--control') + 1]); kc, mc, okc = verdict(c, r)
        ctl = '; control ring prefix %d/%d %s' % (kc, mc, 'MATCH(bad)' if okc else 'differs(ok)')
        if okc: rc = 3
    print('s7931 route: common prefix %d/%d (retail %d, port %d) -> %s; mutation prefix %d/%d %s%s' % (
        k, m, len(r), len(p), 'SEQ-MATCH' if ok else 'SEQ-DIFFER', km, mm, 'MATCH(bad)' if okm else 'differs(ok)', ctl))
    return rc

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
