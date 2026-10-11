#!/usr/bin/env python3
"""Add the phase-gated MusyX stream-block read join to the live generated file."""
from pathlib import Path
import re

ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
PC = re.compile(r"^\s*// 0x([0-9A-Fa-f]+):")
# s4576: address is captured BEFORE the load (dest==base made the old post-load
# U32(ADD32(base,off)) wrong), and every load form incl. LB/LH/LWL/LWR is hooked.
LOAD = re.compile(r"^(\s*)ctx->r(\d+) = MEM_(B|BU|H|HU|W)\((.*?),\s*(.*?)\);\s*$")
LOADLR = re.compile(r"^(\s*)ctx->r(\d+) = do_lw[lr]\(rdram, ctx->r\d+, (.*?),\s*(.*?)\);\s*$")
MARK = "/* PATCH: s4307 synth read join */"
ALL_FUNCS_FILES = ("funcs_24.c",)  # every function in these files, not just the synth four


def main():
    for path in sorted(ROOT.glob("funcs_*.c")):
        text = path.read_text()
        if path.name not in ALL_FUNCS_FILES:
            continue
        # strip any earlier (post-load, wrong-address) hook lines and rewrapped forms
        lines = [l for l in text.splitlines() if MARK not in l or l.lstrip().startswith("{")]
        lines = [re.sub(r"^(\s*)\{ uint32_t s4575_a = .*? (ctx->r\d+ = .*?;) rs64_s4307_synth_read\(.*\} " + re.escape(MARK) + r"$", r"\1\2", l) for l in lines]
        text = "\n".join(lines) + "\n"
        out = []
        active = False
        last_pc = None
        inserted = 0
        for line in lines:
            if line.startswith("RECOMP_FUNC "):
                active = True
                last_pc = None
            out.append(line)
            if not active:
                continue
            match = PC.match(line)
            if match:
                last_pc = match.group(1).upper()
            load = LOAD.match(line)
            if load:
                indent, reg, kind, base, offset = load.groups()
            else:
                lr = LOADLR.match(line)
                if not lr:
                    continue
                indent, reg, base, offset = lr.groups()
            if not last_pc:
                continue
            out.pop()
            out.append(f"{indent}{{ uint32_t s4575_a = U32(ADD32({base}, {offset})); {line.strip()} rs64_s4307_synth_read(rdram, 0x{last_pc}u, s4575_a, U32(ctx->r{reg})); }} {MARK}")
            inserted += 1
        if not inserted:
            continue
        result = "\n".join(out) + "\n"
        if "extern void rs64_s4307_synth_read" not in result:
            result = result.replace(
                '#include "funcs.h"\n',
                '#include "funcs.h"\nextern void rs64_s4307_synth_read(uint8_t*, uint32_t, uint32_t, uint32_t);\n',
                1,
            )
        path.write_text(result)
        print(f"{path}: {inserted} reads")


if __name__ == "__main__":
    main()
