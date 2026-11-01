#!/usr/bin/env python3
"""s6713 G1e: same-run A/B of ROGUESQ_G1E_FAST_TOGGLE from [g1e-split] rows.

Per arm (fast=0/1): fit rest_ms = a + b*calls (rest = ucode wall minus bridge submit, i.e. the interpreter side), plus
mean ucode/task, tasks/s and dense-row (calls > --dense) means. Rows whose 1 s window straddles a [g1e-fast] flip are
dropped (the row printed right after a flip line). Usage: g1e_fast_ab.py <log> [--dense 25000] [--phase N]
"""
import re, sys, argparse

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--dense", type=float, default=25000)
ap.add_argument("--phase", type=int, default=None)
a = ap.parse_args()

row_re = re.compile(r"\[g1e-split\] phase=(\d+) spin=\d+ fast=(\d) tasks=(\d+) ucode_ms=([\d.]+) submit_ms=([\d.]+) "
                    r"rest_ms=([\d.]+) commit_ms=[\d.]+ calls=([\d.]+)")
rows = {0: [], 1: []}
flips = 0
skip = False
for line in open(a.log, errors="replace"):
    if line.startswith("[g1e-fast] on=") and " t=" in line:
        flips += 1
        skip = True
        continue
    m = row_re.search(line)
    if not m:
        continue
    if skip:
        skip = False
        continue
    ph, fast, n, uc, sub, rest, calls = int(m[1]), int(m[2]), int(m[3]), float(m[4]), float(m[5]), float(m[6]), float(m[7])
    if a.phase is not None and ph != a.phase:
        continue
    if n == 0 or calls < 100:
        continue
    rows[fast].append((n, uc, sub, rest, calls))


def fit(rs):
    xs = [r[4] for r in rs]; ys = [r[3] for r in rs]
    n = len(xs)
    mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx else 0.0
    return my - b * mx, b


print(f"flips={flips}")
for k in (0, 1):
    rs = rows[k]
    if len(rs) < 3:
        print(f"fast={k}: {len(rs)} rows (too few)")
        continue
    ic, sl = fit(rs)
    dense = [r for r in rs if r[4] > a.dense]
    m = lambda i, s: sum(r[i] for r in s) / len(s)
    line = (f"fast={k}: rows={len(rs)} rest = {ic:.3f} ms + {sl * 1e6:.1f} ns/cmd | mean tasks/s={m(0, rs):.1f} "
            f"ucode={m(1, rs):.2f} sub={m(2, rs):.2f} rest={m(3, rs):.2f} calls={m(4, rs):.0f}")
    if dense:
        line += f" | dense n={len(dense)} ucode={m(1, dense):.2f} rest={m(3, dense):.2f} calls={m(4, dense):.0f} tasks/s={m(0, dense):.1f}"
    print(line)
