#!/usr/bin/env python3
"""s4784: per NOOP-ENTER..GATE-CLEAR window of a port run, locate the rs-free burst, rs-malloc rows and synth ticks
(with thread ids) by log line. Usage: s4784_gap_order.py run.log"""
import re
import sys

lines = open(sys.argv[1], errors="replace").read().splitlines()
wins = []
cur = None
for i, l in enumerate(lines, 1):
    if "NOOP-ENTER" in l:
        cur = {"start": i, "gate": re.search(r"gate=(\w+)", l).group(1), "free": [], "malloc": [], "synth": [], "end": None}
        wins.append(cur)
    elif cur is not None:
        if "GATE-CLEAR" in l:
            cur["end"] = i
            cur = None
        elif l.startswith("[rs-free]"):
            cur["free"].append(i)
        elif l.startswith("[rs-malloc]"):
            cur["malloc"].append(i)
        elif "SYNTH-IN-NOOP" in l:
            cur["synth"].append((i, re.search(r"tid=(\w+)", l).group(1)))
for n, w in enumerate(wins):
    ff = w["free"][0] if w["free"] else None
    lf = w["free"][-1] if w["free"] else None
    after_first = [s for s in w["synth"] if ff and s[0] > ff]
    after_last = [s for s in w["synth"] if lf and s[0] > lf]
    print(f"win{n} gate={w['gate']} lines {w['start']}-{w['end']} free={len(w['free'])}[{ff}..{lf}] malloc={len(w['malloc'])} "
          f"synth={len(w['synth'])} synth_after_first_free={len(after_first)} synth_after_last_free={len(after_last)} "
          f"tids={sorted(set(t for _, t in w['synth']))}")
    if after_first:
        print("   synth lines after first free:", [s[0] for s in after_first][:12])

# post-clear positions: what comes first after each gate clear -- re-init mallocs or a freed-arena hit?
ends = [w["end"] for w in wins if w["end"]]
for e in ends:
    fm = next((i for i in range(e, len(lines)) if lines[i].startswith("[rs-malloc]")), None)
    fu = next((i for i in range(e, len(lines)) if lines[i].startswith("[s4779")), None)
    fc = next((i for i in range(e, len(lines)) if "SYNTH-CONTROL" in lines[i]), None)
    cr = next((i for i in range(e, len(lines)) if "Crashed" in lines[i] or "SIGSEGV" in lines[i] or "EXC_BAD" in lines[i]), None)
    nxt = [x for x in ends if x > e]
    print(f"after clear@{e}: first_malloc={fm and fm+1} first_s4779={fu and fu+1} first_synth_control={fc and fc+1} crash={cr and cr+1} next_clear={nxt[0] if nxt else None}")

# s4784 part 2: per clear, rs-malloc rows before the first SYNTH-POST tick (retail: 32-44 mallocs, zero ticks)
for e in ends:
    nxt = min([x for x in ends if x > e] + [len(lines) + 1])
    seg = lines[e:nxt - 1]
    first_tick = next((k for k, l in enumerate(seg) if "SYNTH-POST" in l), None)
    pre = seg[:first_tick] if first_tick is not None else seg
    mal = sum(1 for l in pre if l.startswith("[rs-malloc]"))
    tot_mal = sum(1 for l in seg if l.startswith("[rs-malloc]"))
    ticks = sum(1 for l in seg if "SYNTH-POST" in l)
    tid = sorted(set(re.search(r"tid=(\w+)", l).group(1) for l in seg if "SYNTH-POST" in l))
    print(f"clear@{e}: mallocs_before_first_tick={mal} first_tick_at={first_tick and e + first_tick + 1} total_post_ticks_logged={ticks} total_mallocs_in_seg={tot_mal} tids={tid}")
