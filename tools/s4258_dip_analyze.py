#!/usr/bin/env python3
"""s4258: per-second audio/gfx breakdown in the t=18-34 window from [s4245]/[s4248] log lines.
usage: s4258_dip_analyze.py LOG [LOG...]"""
import sys

for path in sys.argv[1:]:
    print(path)
    prev = None
    n = big = lk = 0
    mx = 0
    for l in open(path, errors="ignore"):
        if l.startswith("[s4245] t="):
            d = dict(x.split("=", 1) for x in l.split()[1:] if "=" in x)
            t = float(d["t"])
            if 18 <= t <= 34:
                te = int(d["task_enter"])
                dt = te - prev if prev is not None else -1
                print(f"  t={t:5.1f} aud/s={dt:3d} gfx_enter={d['gfx_enter']:>4} gfx_us={d['gfx_us']:>8} gfx_max={d['gfx_max_us']:>7} aud_us={d['aud_us']:>7} aud_max={d['aud_max_us']:>6}")
            prev = int(d["task_enter"])
        elif l.startswith("[s4248]"):
            d = dict(x.split("=", 1) for x in l.split()[1:])
            if 22 <= float(d["t"]) <= 30:
                n += 1
                w = int(d["wall_us"])
                big += w > 20000
                lk += int(d["lockwait_us"]) > 0
                mx = max(mx, w)
    print(f"  s4248 t22-30: tasks={n} wall>20ms={big} lockwait>0={lk} maxwall_us={mx}")
