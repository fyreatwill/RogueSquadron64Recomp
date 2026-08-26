#!/usr/bin/env python3
"""Inject caller-side probes at every generated rs_memset jal site."""

from pathlib import Path
import re


GEN = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
JAL = re.compile(r"^\s*//\s*0x([0-9A-Fa-f]+): jal\s+0x800078E0\s*$")
MARKER = "/* PATCH: s2448 m5 static rs_memset caller */"


def main() -> None:
    total = 0
    changed = 0
    for path in sorted(GEN.glob("funcs_*.c")):
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        out = []
        i = 0
        file_total = 0
        while i < len(lines):
            match = JAL.match(lines[i].rstrip("\n"))
            if not match:
                out.append(lines[i])
                i += 1
                continue
            callsite = int(match.group(1), 16)
            file_total += 1
            j = i + 1
            while j < len(lines) and j <= i + 10 and "rs_memset(rdram, ctx);" not in lines[j]:
                j += 1
            if j >= len(lines) or "rs_memset(rdram, ctx);" not in lines[j]:
                raise SystemExit(f"{path}: no rs_memset call after 0x{callsite:08X}")
            if j >= 2 and MARKER in lines[j - 2]:
                out.extend(lines[i:j - 2])
                out.append(
                    f"    {MARKER}\n"
                    "    { extern void rs64_m5_static_rs_memset_callsite(unsigned, unsigned, unsigned, unsigned, unsigned); "
                    f"rs64_m5_static_rs_memset_callsite(0x{callsite:08X}u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)); }}\n"
                )
            else:
                out.extend(lines[i:j])
                out.append(
                    f"    {MARKER}\n"
                    "    { extern void rs64_m5_static_rs_memset_callsite(unsigned, unsigned, unsigned, unsigned, unsigned); "
                    f"rs64_m5_static_rs_memset_callsite(0x{callsite:08X}u, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6)); }}\n"
                )
                changed += 1
            i = j
        total += file_total
        if file_total:
            path.write_text("".join(out), encoding="utf-8")
    if total != 88:
        raise SystemExit(f"expected 88 jal sites, found {total}")
    print(f"apply_s2448: found {total} sites, inserted {changed} caller probes")


if __name__ == "__main__":
    main()
