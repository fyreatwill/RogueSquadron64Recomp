#!/usr/bin/env python3
"""Census of lwl/lwr/swl/swr/ldl/ldr/sdl/sdr/ll/lld/sc/scd/cache sites (s4820).
Per mnemonic: total, how many sit in data-as-code functions (>=50% of instruction
comments are .word/do_break), a sample of the emitted C line, and the set of
distinct emitted C shapes (digits/registers normalised)."""
from pathlib import Path
from collections import Counter, defaultdict
import re, sys
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MN = "lwl lwr swl swr ldl ldr sdl sdr ll lld sc scd cache".split()
fn_re = re.compile(r'^(?:RECOMP_FUNC\s+)?void\s+(\w+)\(')
ins_re = re.compile(r'// 0x([0-9A-Fa-f]{8}): (\S+)')
per = defaultdict(Counter)
sites = defaultdict(list)  # mn -> (fn, file:line, emitted-line)
for p in sorted(ROOT.glob("funcs_*.c")):
    fn = None
    lines = p.read_text(errors="replace").splitlines()
    for i, l in enumerate(lines):
        m = fn_re.match(l)
        if m:
            fn = m.group(1)
        m = ins_re.search(l)
        if not m:
            continue
        per[fn]["ins"] += 1
        if m.group(2) in (".word",) or "do_break(" in l:
            per[fn]["word"] += 1
        if m.group(2) in MN:
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            sites[m.group(2)].append((fn, "%s:%d" % (p.name, i + 1), nxt))
        if "do_break(" in l:
            per[fn]["word"] += 1
dac = {f for f, c in per.items() if c["word"] >= 0.5 * max(c["ins"], 1)}
norm = lambda s: re.sub(r'0x[0-9A-Fa-f]+|-?\d+|\bc\d+\b|\bctx->r\d+', 'N', s)
for mn in MN:
    s = sites[mn]
    live = [x for x in s if x[0] not in dac]
    print("== %s total %d, in data-as-code fns %d, live %d (%d fns)" % (mn, len(s), len(s) - len(live), len(live), len({x[0] for x in live})))
    shapes = Counter(norm(x[2]) for x in live)
    for sh, n in shapes.most_common(4):
        print("   %4d  %s" % (n, sh[:150]))
    if mn in ("sc", "scd", "lld", "cache", "sdl", "sdr") :
        for x in live[:12]:
            print("   LIVE", x[0], x[1], x[2][:100])
