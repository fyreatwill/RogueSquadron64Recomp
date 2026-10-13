#!/usr/bin/env python3
"""Census of FPR memory ops (lwc1/swc1/ldc1/sdc1) and the LL/SC family in
generated code. For each MIPS mnemonic (from the `// 0xADDR: op` comment) report
which C macro the statement lowers to, or do_break (dead data-in-code)."""
from pathlib import Path
import collections
import re
import sys

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OPS = ("lwc1", "swc1", "ldc1", "sdc1", "ll", "lld", "sc", "scd")
HDR = re.compile(r"^\s*// 0x[0-9A-Fa-f]+: (\w+)\s")
MACRO = re.compile(r"\b(MEM_[A-Z]+|LD|SD|SW|SH|SB|do_break|rs64_m5_writer_parity)\b")


def main():
    tab = collections.defaultdict(collections.Counter)
    for p in sorted(ROOT.glob("funcs_*.c")):
        lines = p.read_text(errors="replace").splitlines()
        for i, l in enumerate(lines):
            m = HDR.match(l)
            if not m or m.group(1) not in OPS:
                continue
            body = " ".join(x for x in lines[i + 1:i + 4]
                            if not x.strip().startswith("//") and "CHECK_FR" not in x)
            key = tuple(sorted(set(MACRO.findall(body)))) or ("OTHER",)
            tab[m.group(1)][key] += 1
    for op in OPS:
        print(op, sum(tab[op].values()), dict(tab[op]))


if __name__ == "__main__":
    main()
