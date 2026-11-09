#!/usr/bin/env python3
"""s7023: join [s7022-st] (loop inclusive) with [s7023-cs] (callee/region/path) per cap bucket, last K lines each, and print the
self/callee split per cell and per path. Each timed span is corrected by ovh_ns (one mach pair). usage: s7023_calleetime_sum.py <run.log> [K=6]"""
import re, sys, collections
K = int(sys.argv[2]) if len(sys.argv) > 2 else 6
st, cs = collections.defaultdict(list), collections.defaultdict(list)
for l in open(sys.argv[1], errors="replace"):
    for tag, d in (("s7022-st", st), ("s7023-cs", cs)):
        m = re.search(r"\[%s\] cap=(-?\d+) (.*)" % tag, l)
        if m: d[int(m.group(1))].append({k: float(v) for k, v in re.findall(r"(\w+)=([-\d.]+)", m.group(2))})
for cap in sorted(set(st) | set(cs)):
    a, b = st[cap][-K:], cs[cap][-K:]
    if not a or not b: print(f"cap={cap} st={len(a)} cs={len(b)} (missing)"); continue
    A = lambda r, k: sum(x[k] for x in r) / len(r)
    loop, cells = A(a, "loop_us"), A(a, "cells"); ov = A(b, "ovh_ns") * 1e-3
    gv = A(b, "gv_us") - A(b, "gv_n") * ov; pg = A(b, "pg_us") - A(b, "pg_n") * ov
    cp = A(b, "cp_us") - A(b, "cp_n") * ov - (A(b, "gv_n") + A(b, "pg_n")) * ov  # region inclusive, minus its own + inner pairs
    self_ = loop - gv - pg; cp_self = cp - gv - pg; rest = loop - cp - (A(b, "gv_n") + A(b, "pg_n") + A(b, "cp_n")) * ov
    n_cp, n_sk, n_rj = A(b, "callp"), A(b, "spaneq"), A(b, "rej")
    print(f"cap={cap:6d} n={len(a)}/{len(b)} loop_us={loop:.0f} cells={cells:.0f} ovh_ns={ov*1e3:.1f}")
    print(f"   callee gv={gv:.0f}us ({gv/loop*100:.0f}%, n={A(b,'gv_n'):.0f}, {gv*1e3/max(A(b,'gv_n'),1):.0f} ns/call)  pg={pg:.0f}us ({pg/loop*100:.0f}%, n={A(b,'pg_n'):.0f}, {pg*1e3/max(A(b,'pg_n'),1):.0f} ns/call)")
    print(f"   self={self_:.0f}us ({self_/loop*100:.0f}%): call-path inline {cp_self:.0f}us over {n_cp:.0f} cells ({cp_self*1e3/max(n_cp,1):.0f} ns/cell); "
          f"rest (skip+reject+rows) {rest:.0f}us over {cells-n_cp:.0f} cells ({rest*1e3/max(cells-n_cp,1):.0f} ns/cell)")
    print(f"   paths/call: spaneq={n_sk:.0f} ({n_sk/cells*100:.0f}%) rej={n_rj:.0f} ({n_rj/cells*100:.0f}%) callp={n_cp:.0f} ({n_cp/cells*100:.0f}%) "
          f"cp_entries={A(b,'cp_n'):.0f} poolcap={A(b,'poolcap'):.1f}  check sum={n_sk+n_rj+n_cp:.0f} vs cells={cells:.0f}")
