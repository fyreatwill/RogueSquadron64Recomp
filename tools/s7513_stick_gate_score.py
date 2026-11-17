#!/usr/bin/env python3
"""s7513 class FJ: score [stick-gate] / [padlog] lines (ROGUESQ_PAD_LOG=1) per game log.
usage: s7513_stick_gate_score.py [--ctl-off LOG] LOG...
Each LOG must show '[stick-gate] on=1' and every guest-bound stick count inside the OEM gate (|axis| <= card, and the octagon
|x|+|y|*(card-diag)/diag <= card + 1). --ctl-off LOG = an arm run with ROGUESQ_STICK_GATE=0: must print on=0 (the switch is live).
rc 0 = pass, 1 = a stick count outside the gate, 3 = control failed, 4 = a log without a [stick-gate] line."""
import re, sys
def scan(p):
    on = card = diag = None; n = 0; worst = (0, 0); bad = []
    for l in open(p, errors='ignore'):
        m = re.search(r'\[stick-gate\] on=(\d) card=(\d+) diag=(\d+)', l)
        if m: on, card, diag = int(m[1]), int(m[2]), int(m[3]); continue
        m = re.search(r'\[padlog\] .* sx=(-?\d+) sy=(-?\d+) err=0', l)
        if m:
            x, y = abs(int(m[1])), abs(int(m[2])); n += 1
            if max(x, y) > max(worst): worst = (x, y)
            if card and on and (max(x, y) > card or (max(x, y) + min(x, y) * (card - diag) / diag) > card + 1): bad.append((x, y))
    return on, card, diag, n, worst, bad
args = sys.argv[1:]; ctl = None
if args[:1] == ['--ctl-off']: ctl, args = args[1], args[2:]
rc = 0
for p in args:
    on, card, diag, n, worst, bad = scan(p)
    print(f'{p}: on={on} card={card} diag={diag} padlog={n} max={worst} out_of_gate={len(bad)} {bad[:4]}')
    if on is None: rc = max(rc, 4)
    elif on != 1: rc = max(rc, 1)
    elif bad: rc = max(rc, 1)
if ctl:
    on, card, diag, n, worst, bad = scan(ctl)
    ok = on == 0
    print(f'ctl-off {ctl}: on={on} padlog={n} max={worst} -> {"ctl PASS" if ok else "ctl FAIL"}')
    if not ok: rc = 3 if rc in (0, 1) else rc
sys.exit(rc)
