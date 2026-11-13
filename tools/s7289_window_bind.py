#!/usr/bin/env python3
"""s7289: score site-17 window placements (ROGUESQ_G3E_TRACE rows: vi swap site ww w d cap). Per trace: n, w/d percentiles,
fraction of placements pinned at the 128 table edge (max(w,d) >= N), at 64, at the area cap (w*d >= cap-max(w,d)), and the
fraction bound by neither (footprint bounds). Verdict per trace: N / cap / bounds by majority. Usage: s7289_window_bind.py tr_*.txt"""
import sys, collections
def pct(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))] if v else 0
for fn in sys.argv[1:]:
    rows = []
    for ln in open(fn, errors="replace"):
        p = ln.split()
        if len(p) == 7 and p[2] == "17": rows.append(tuple(int(x) for x in p[3:]))
    if not rows: print(f"{fn}: no site-17 rows"); continue
    rows = rows[len(rows) // 4:]  # drop route/menu quarter
    n = len(rows); W = [r[1] for r in rows]; D = [r[2] for r in rows]; A = [r[1] * r[2] for r in rows]; C = [r[3] for r in rows]
    ww = sum(r[0] for r in rows) / n
    e128 = sum(max(r[1], r[2]) >= 128 for r in rows) / n
    e64 = sum(max(r[1], r[2]) == 64 for r in rows) / n
    capb = sum(r[3] > 0 and r[1] * r[2] >= r[3] - max(r[1], r[2]) for r in rows) / n
    nb = sum(not (max(r[1], r[2]) >= 128 or (r[3] > 0 and r[1] * r[2] >= r[3] - max(r[1], r[2]))) for r in rows) / n
    v = max([("N", e128), ("cap", capb), ("bounds", nb)], key=lambda t: t[1])[0]
    cc = collections.Counter(C).most_common(3)
    print(f"{fn}: n={n} ww={ww:.2f} w p10/50/90 {pct(W,.1)}/{pct(W,.5)}/{pct(W,.9)} d {pct(D,.1)}/{pct(D,.5)}/{pct(D,.9)} "
          f"area p50/90 {pct(A,.5)}/{pct(A,.9)} cap {cc} | pin128 {e128:.2f} pin64 {e64:.2f} capbound {capb:.2f} neither {nb:.2f} -> {v}")
