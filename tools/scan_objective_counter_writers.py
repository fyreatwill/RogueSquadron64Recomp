#!/usr/bin/env python3
"""List every site that touches objective counters at 0x80138060 (static, from a
disasm_mips_elf.py dump): direct `addiu rX,rX,-32672` users and constant-index
callers of increaseObjectiveCount (800C75EC) / setObjectiveCount (800C75C0).
usage: scan_objective_counter_writers.py DISASM.txt [DISASM2.txt ...]  (s5477)"""
import re, sys
for f in sys.argv[1:]:
    L = open(f).read().split("\n")
    for i, l in enumerate(L):
        if "addiu" in l and "-32672" in l:
            print(f, l[:8], "base-user")
        m = re.search(r"jal 800C(75EC|75C0)", l)
        if m:
            r4 = [x.group(1) for c in L[max(0, i - 2):i + 2]
                  for x in [re.search(r"addiu r4, r0, (\d+)", c)] if x]
            print(f, l[:8], "add" if m.group(1) == "75EC" else "set", "idx", r4[-1:] or "DYNAMIC")
