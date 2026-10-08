#!/usr/bin/env python3
"""Summarize s4250 A/B logs: crash frame, last [s4245] t / task_enter, audio tasks/s at t in [18,28]."""
import re, sys
for p in sys.argv[1:]:
    rows = {}
    crash = None
    last = None
    with open(p, errors="replace") as f:
        for ln in f:
            if ln.startswith("[s4245] t="):
                m = re.match(r"\[s4245\] t=([\d.]+) phase=(\d+) .*?task_enter=(\d+)", ln)
                if m: rows[float(m[1])] = int(m[3]); last = (float(m[1]), int(m[2]), int(m[3]))
            elif "[CRASH]" in ln: crash = ln.strip()[:60]
            elif crash and re.match(r"^3 ", ln): crash += " | " + ln.split()[3][:40]; 
    def at(t):
        k = min(rows, key=lambda x: abs(x - t)) if rows else None
        return k, rows.get(k)
    a, b = at(18), at(28)
    rate = (b[1] - a[1]) / (b[0] - a[0]) if a[0] and b[0] and b[0] > a[0] else None
    print(p.split("soak_results/")[1], "last(t,phase,tasks)=", last, "rate18-28=", None if rate is None else round(rate, 1), "crash=", crash)
