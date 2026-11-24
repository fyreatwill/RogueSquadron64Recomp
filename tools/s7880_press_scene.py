#!/usr/bin/env python3
"""s7880: Start-press schedule vs scene boundaries, retail oracle vs port, in VI units.

Both sides are keyed to their own first 640->1024 VI width change (the level-select screen), so the press
offsets can be compared directly. Retail presses come from oracle.log `[press] vi=N down`, retail scenes from
`[vi] ... vi=N WIDTH a -> b`; port presses from run.log `[autopilot] fire ... vi=N`, port scenes from
`[phase] vi_width=b (was a) ... update_screen #N` (update_screen count = VI count, s7880 check: fire vi and
update_screen agree to <1 VI on the 1024 gate).
For every scene the table lists the presses inside it and the VIs from the last press to the scene end.
A constant port-minus-retail press offset is a recipe (schedule) difference, not an input defect: the tool prints
the AP shift in seconds that would put the port's presses on retail's VIs (H-sched, s7880).
usage: s7880_press_scene.py ORACLE.log RUN.log
"""
import re, sys
if len(sys.argv) != 3: print(__doc__); sys.exit(2)

def retail(p):
    pr, sc = [], []
    for l in open(p, errors='replace'):
        m = re.match(r'\[press\] vi=(\d+) down', l)
        if m: pr.append(int(m.group(1)))
        m = re.match(r'\[vi\] .*vi=(\d+)\s+WIDTH (\d+) -> (\d+)', l)
        if m: sc.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
    return pr, sc

def port(p):
    pr, sc = [], []
    for l in open(p, errors='replace'):
        m = re.match(r'\[autopilot\] fire .* vi=(\d+)', l)
        if m: pr.append(int(m.group(1)))
        m = re.match(r'\[phase\] vi_width=(\d+) \(was (\d+)\).*update_screen #(\d+)', l)
        if m: sc.append((int(m.group(3)), int(m.group(2)), int(m.group(1))))
    return pr, sc

def table(tag, pr, sc):
    a = next((v for v, w0, w1 in sc if w0 == 640 and w1 == 1024), None)
    if a is None: print(f'{tag}: no 640->1024 anchor'); return None, []
    print(f'{tag}: anchor 640->1024 at vi {a}; presses (rel) {[p - a for p in pr]}')
    for i, (v, w0, w1) in enumerate(sc):
        end = sc[i + 1][0] if i + 1 < len(sc) else None
        ins = [p - v for p in pr if v <= p < (end if end else 1 << 60)]
        last = max([p for p in pr if p < end], default=None) if end else None
        print(f'  scene w{w1} rel {v - a:6d} len {(end - v) if end else "open":>6}  presses in scene (rel to start) {ins}'
              f'  last press -> end {(end - last) if last is not None else "-"}')
    return a, [p - a for p in pr]

ra, rp = table('retail', *retail(sys.argv[1]))
pa, pp = table('port  ', *port(sys.argv[2]))
if ra is not None and pa is not None:
    rp = [x for x in rp if x > 0]; pp = [x for x in pp if x > 0]
    best = None   # the oracle carries fixed boot presses the port AP schedule may lack: try every lag k, keep the flattest
    for k in range(-len(pp) + 1, len(rp)):
        d = [q - r for r, q in zip(rp[max(k, 0):], pp[max(-k, 0):])]
        if len(d) >= 2 and (best is None or (max(d) - min(d), -len(d)) < (best[0], -len(best[2]))): best = (max(d) - min(d), k, d)
    if best:
        spread, k, d = best
        print(f'post-anchor press offsets port-retail (VI), lag {k} (retail presses unmatched: {rp[:k] if k > 0 else []}'
              f', port presses unmatched: {pp[:-k] if k < 0 else []}): {d}')
        if spread <= 30:
            print(f'H-sched: constant offset {sum(d) / len(d):+.0f} VI -> shift port AP times after the w1024 gate by '
                  f'{-sum(d) / len(d) / 60:+.2f} s' + (f'; retail has {k} extra press(es) the port lacks' if k > 0 else ''))
