#!/usr/bin/env python3
"""Add the phase-gated MusyX stream-block read join to the live generated file."""
from pathlib import Path
import re

ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
PC = re.compile(r"^\s*// 0x([0-9A-Fa-f]+):")
LOAD = re.compile(r"^(\s*)ctx->r(\d+) = MEM_(BU|HU|W)\((.*?),\s*(.*?)\);\s*$")
FUNCTIONS = (
    "musyxSynthFrame",
    "musyxMixActiveVoices",
    "musyxRenderVoiceSamples",
    "fillSampleStreamRange",
)


def main():
    for path in sorted(ROOT.glob("funcs_*.c")):
        text = path.read_text()
        lines = text.splitlines()
        out = []
        active = False
        last_pc = None
        inserted = 0
        for line in lines:
            if line.startswith("RECOMP_FUNC "):
                active = any(f"void {name}(" in line for name in FUNCTIONS)
                last_pc = None
            out.append(line)
            if not active:
                continue
            match = PC.match(line)
            if match:
                last_pc = match.group(1).upper()
            load = LOAD.match(line)
            if not load or not last_pc:
                continue
            indent, reg, kind, base, offset = load.groups()
            marker = f"{indent}rs64_s4307_synth_read(rdram, 0x{last_pc}u, U32(ADD32({base}, {offset})), U32(ctx->r{reg})); /* PATCH: s4307 synth read join */"
            if marker in text:
                continue
            out.append(marker)
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
