#!/usr/bin/env python3
"""M3 idiom census: ldl/ldr (64-bit unaligned loads) and swl/swr/sdl/sdr
(unaligned stores) in generated code. Groups sites per function, flags
functions that contain data-decoded-as-code markers (do_break, INVALID,
.word, mfc0/cache), and for ldl/ldr checks whether the assembled dst is later
used as a memory-address base. Asserts counts against an independent grep."""

from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
FUNCTION = re.compile(r"\b(\w+)\(uint8_t\*\s*rdram,\s*recomp_context\*\s*ctx\)\s*\{")
LOAD = re.compile(r"^\s*ctx->r(\d+) = do_(ld[lr])\(rdram, (?:ctx->r(\d+)|0), (?:ctx->r(\d+)|0), (-?0[xX][0-9A-Fa-f]+|-?\d+)\)")
STORE = re.compile(r"^\s*do_(s[wd][lr])\(rdram, (-?0[xX][0-9A-Fa-f]+|-?\d+), (ctx->r\d+|0), ")
DEADMARK = re.compile(r"do_break\(|INVALID|\.word|\bmfc0\b|\bmtc0\b|\bcache\b|\beret\b|\btlb")
DEF = re.compile(r"^\s*#\s*define")


def main():
    funcs = defaultdict(lambda: defaultdict(int))  # (file,func) -> kind -> n
    dead = set()
    ldsites = []
    totals = defaultdict(int)
    for p in sorted(ROOT.glob("funcs_*.c")):
        lines = p.read_text(errors="replace").splitlines()
        cur = ""
        for i, line in enumerate(lines):
            m = FUNCTION.search(line)
            if m:
                cur = m.group(1)
            if DEF.match(line):
                continue
            if DEADMARK.search(line):
                dead.add((p.name, cur))
            m = LOAD.match(line)
            if m:
                funcs[(p.name, cur)][m.group(2)] += 1
                totals[m.group(2)] += 1
                ldsites.append((p.name, i, cur, int(m.group(1)), lines))
                continue
            m = STORE.match(line)
            if m:
                funcs[(p.name, cur)][m.group(1)] += 1
                totals[m.group(1)] += 1
    grep = defaultdict(int)
    for p in ROOT.glob("funcs_*.c"):
        for line in p.read_text(errors="replace").splitlines():
            if DEF.match(line):
                continue
            for k in ("ldl", "ldr", "swl", "swr", "sdl", "sdr"):
                grep[k] += len(re.findall(rf"\bdo_{k}\(", line))
    print("regex totals:", dict(totals))
    print("grep totals: ", dict(grep))
    unmatched = {k: grep[k] - totals[k] for k in grep if grep[k] != totals[k]}
    print("unmatched (grep - regex; PATCH-commented $zero dsts land here):", unmatched)
    live = {k: v for k, v in funcs.items() if k not in dead}
    print(f"functions with sites: {len(funcs)}; with dead-decode markers: {len(set(funcs) & dead)}; live: {len(live)}")
    for k, v in sorted(live.items()):
        print("LIVE\t", k, dict(v))
    # ldl/ldr dst reused as an address base within 10 statements?
    n = 0
    for fn, i, cur, d, lines in ldsites:
        if (fn, cur) in dead:
            continue
        nxt = [x for x in lines[i + 1:i + 11] if x.strip() and not x.strip().startswith("//")][:6]
        r = re.escape(f"ctx->r{d}")
        pat = re.compile(rf"\b(?:MEM_\w+|LD|S[WDBH]|SDC1|SWC1|LWC1|do_\w+)\([^;]*?{r}\b[^;]*?\)")
        if any(pat.search(x) for x in nxt):
            n += 1
            print("ADDR?\t", fn, i + 1, cur, f"r{d}", nxt[:2])
    print("live ldl/ldr dst used in following memory op:", n)


if __name__ == "__main__":
    main()
