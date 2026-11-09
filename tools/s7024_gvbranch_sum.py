#!/usr/bin/env python3
"""s7024: summarise [s7024-gv] (per-branch getGridCellValueAt time) and [s7023-cs] (stream loop split) per bucket.
Bucket key printed as cap= is cap*10 + ROGUESQ_G1E_CELLIDX active mode (s7024); the last N lines per bucket are averaged.
Also prints [g1e-cell] CHECK totals when present. Usage: s7024_gvbranch_sum.py run.log [N=6]"""
import sys, re, collections
f = sys.argv[1]; N = int(sys.argv[2]) if len(sys.argv) > 2 else 6
gv = collections.defaultdict(list); cs = collections.defaultdict(list); chk = None
for l in open(f, errors="replace"):
    if l.startswith("[s7024-gv]"): gv[int(re.search(r"cap=(\d+)", l).group(1))].append(l)
    elif l.startswith("[s7023-cs]"): cs[int(re.search(r"cap=(\d+)", l).group(1))].append(l)
    elif l.startswith("[g1e-cell] s=") and "tot_chk" in l: chk = l.strip()
for key in sorted(gv):
    ls = gv[key][-N:]; agg = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
    for l in ls:
        for b, n, ns, w in re.findall(r" b(\d)=([\d.]+)/([\d.]+)ns/w([\d.]+)", l):
            a = agg[b]; a[0] += float(n); a[1] += float(n) * float(ns); a[2] += float(n) * float(w)
    tot = sum(a[1] for a in agg.values()) or 1
    c = {}
    for l in cs[key][-N:]:
        for k, v in re.findall(r"(\w+)=([\d.]+)", l): c[k] = c.get(k, 0) + float(v) / len(cs[key][-N:])
    print(f"bucket cap={key // 10} mode={key % 10} lines={len(gv[key])} | stream gv_us={c.get('gv_us', 0):.0f} gv_n={c.get('gv_n', 0):.0f} "
          f"pg_us={c.get('pg_us', 0):.0f} cp_us={c.get('cp_us', 0):.0f} (per call, ovh {c.get('ovh_ns', 0):.1f} ns/pair)")
    for b, a in sorted(agg.items()):
        print(f"   b{b}: {a[0] / len(ls):7.1f}/call-of-stream {a[1] / a[0]:6.1f} ns  share {100 * a[1] / tot:5.1f}%  us {a[1] / len(ls) / 1000:6.1f}  walk {a[2] / a[0]:.2f}")
if chk: print("last check line:", chk[:400])
