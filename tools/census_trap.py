#!/usr/bin/env python3
"""Census of do_break / syscall / cop0 status sites in generated code (s4818).
Classifies each do_break by the originating instruction comment and by whether
its enclosing function is data-as-code (>=50% of its instruction comments are
.word / do_break)."""
from pathlib import Path
from collections import Counter, defaultdict
import re, sys
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
fn_re = re.compile(r'^(?:RECOMP_FUNC\s+)?void\s+(\w+)\(')
ins_re = re.compile(r'// 0x([0-9A-Fa-f]{8}): (\S+)')
mn = Counter()
per = defaultdict(Counter)
sysc = []
cop0 = []
for p in sorted(ROOT.glob("funcs_*.c")):
    fn = None
    last = None
    for i, l in enumerate(p.read_text(errors="replace").splitlines(), 1):
        m = fn_re.match(l)
        if m:
            fn = m.group(1)
        m = ins_re.search(l)
        if m:
            last = (m.group(1), m.group(2))
            per[fn]["ins"] += 1
            if m.group(2) == ".word":
                per[fn]["word"] += 1
        if "do_break(" in l:
            mn[last[1] if last else "?"] += 1
            per[fn]["brk"] += 1
        if "recomp_syscall_handler(" in l:
            sysc.append((fn, "%s:%d" % (p.name, i)))
        if "cop0_status_" in l and "(ctx" in l:
            cop0.append((fn, last[1] if last else "?", "%s:%d" % (p.name, i)))
print("do_break by originating mnemonic:", mn.most_common(12))
dac = {f for f, c in per.items() if c["brk"] and (c["brk"] + c["word"]) >= 0.5 * max(c["ins"], 1)}
mixed = {f: c["brk"] for f, c in per.items() if c["brk"] and f not in dac}
print("do_break total", sum(c["brk"] for c in per.values()),
      "in data-as-code fns", sum(per[f]["brk"] for f in dac), "(", len(dac), "fns )")
print("do_break in NON-data-as-code fns:", len(mixed), "fns", sum(mixed.values()), "sites")
for f, n in sorted(mixed.items(), key=lambda x: -x[1])[:40]:
    print("  ", f, n, dict(per[f]))
print("syscall sites", len(sysc), Counter(f for f, _ in sysc).most_common(8))
print("cop0 status sites", len(cop0))
for c in cop0:
    print("  ", c)

# --- part 2: real-code (non-data-as-code) do_break breakdown -----------------
DAC_BIG = {"audioCompandS16", "__OSGlobalIntMask", "data_gap_800CC3D4"}
brk_codes = Counter()
non_break = defaultdict(list)
for p in sorted(ROOT.glob("funcs_*.c")):
    fn = None
    last = ""
    for i, l in enumerate(p.read_text(errors="replace").splitlines(), 1):
        m = fn_re.match(l)
        if m:
            fn = m.group(1)
        m = re.search(r'// 0x[0-9A-Fa-f]{8}: (.*)', l)
        if m:
            last = m.group(1)
        if "do_break(" in l and fn not in dac and fn not in DAC_BIG:
            if last.startswith("break"):
                brk_codes[" ".join(last.split()[:2])] += 1
            else:
                non_break[fn].append((last.split()[0] if last else "?", "%s:%d" % (p.name, i)))
print("\nreal-code do_break from break N:", brk_codes.most_common())
print("real-code do_break from other mnemonics:", sum(len(v) for v in non_break.values()), "in", len(non_break), "fns")
for f, v in sorted(non_break.items(), key=lambda x: -len(x[1]))[:40]:
    print("  ", f, len(v), Counter(a for a, _ in v).most_common(4), v[0][1])
