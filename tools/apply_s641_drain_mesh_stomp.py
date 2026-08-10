#!/usr/bin/env python3
"""Re-apply s641 drainMeshReleaseQueue freelist-header stomp probe (idempotent).

Instruments every sw $zero,0x4($a0) and every sw $v0,0x0($v1) (when v0==0)
inside drainMeshReleaseQueue. Logs [drain-mesh-stomp] when dest==0x801F3CC0 or
pre-write looks like an allocated/free heap header (flags in {1,2}, size sane).
First N zero-stores always sample so silence is not "probe dead".

Gate: ROGUESQ_LOG_FL_ZERO_WATCH (same as fl-zero-poll / fl-hdr-write).
"""
from pathlib import Path
import os
import re
import sys

FUNCS = Path(os.environ.get(
    "RECOMP_FUNCS",
    str(Path.home() / "Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c"),
))


def a0_block() -> str:
    # Use raw segments so C format \n stays as two chars (backslash, n).
    return (
        "            { // PATCH: drain-mesh-stomp a0+4 (s641, item -395) -- see fixup_game_funcs.py comment\n"
        "                static int s_dms_en = -1;\n"
        '                if (s_dms_en < 0) { const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH"); s_dms_en = (e && e[0] && e[0] != \'0\') ? 1 : 0; }\n'
        "                if (s_dms_en) {\n"
        "                    uint32_t dms_dest = U32(ctx->r4);\n"
        "                    static int s_dms_a0_n = 0;\n"
        "                    s_dms_a0_n++;\n"
        "                    if (dms_dest >= 0x80000000u && dms_dest < 0x80800000u) {\n"
        "                        gpr dms_b = S32(dms_dest);\n"
        "                        uint16_t dms_f = (uint16_t)MEM_HU(0x0, dms_b);\n"
        "                        uint32_t dms_sz = U32(MEM_W(0x4, dms_b));\n"
        "                        int dms_tgt = (dms_dest == 0x801F3CC0u);\n"
        "                        int dms_heap = ((dms_f == 1u || dms_f == 2u) && dms_sz != 0u && dms_sz < 0x800000u);\n"
        "                        if (dms_tgt || dms_heap || s_dms_a0_n <= 12 || (s_dms_a0_n % 400) == 0) {\n"
        "                            fprintf(stderr,\n"
        r'                                "[drain-mesh-stomp] n=%d site_pc=0x%08X dest=0x%08X pre_f=0x%X pre_sz=0x%X reg=a0 off=4 val=0 ra=0x%08X%s\n",' + "\n"
        "                                s_dms_a0_n, (unsigned)g_rs64_last_guest_pc, dms_dest,\n"
        "                                (unsigned)dms_f, dms_sz, U32(ctx->r31),\n"
        '                                dms_tgt ? " TARGET" : (dms_heap ? " HEAPLIKE" : " sample"));\n'
        "                            fflush(stderr);\n"
        "                        }\n"
        "                    } else if (s_dms_a0_n <= 12) {\n"
        "                        fprintf(stderr,\n"
        r'                            "[drain-mesh-stomp] n=%d site_pc=0x%08X dest=0x%08X reg=a0 off=4 sample_oob ra=0x%08X\n",' + "\n"
        "                            s_dms_a0_n, (unsigned)g_rs64_last_guest_pc, dms_dest, U32(ctx->r31));\n"
        "                        fflush(stderr);\n"
        "                    }\n"
        "                }\n"
        "            }\n"
        "            MEM_W(0X4, ctx->r4) = 0;\n"
    )


def v1_block(indent: str) -> str:
    i = indent
    i1 = indent + "    "
    i2 = indent + "        "
    i3 = indent + "            "
    i4 = indent + "                "
    return (
        f"{i}{{ // PATCH: drain-mesh-stomp v1+0 (s641, item -395) -- see fixup_game_funcs.py comment\n"
        f"{i1}static int s_dms_v1_en = -1;\n"
        f'{i1}if (s_dms_v1_en < 0) {{ const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH"); s_dms_v1_en = (e && e[0] && e[0] != \'0\') ? 1 : 0; }}\n'
        f"{i1}if (s_dms_v1_en && U32(ctx->r2) == 0u) {{\n"
        f"{i2}uint32_t dms_dest = U32(ctx->r3);\n"
        f"{i2}static int s_dms_v1_n = 0;\n"
        f"{i2}s_dms_v1_n++;\n"
        f"{i2}if (dms_dest >= 0x80000000u && dms_dest < 0x80800000u) {{\n"
        f"{i3}gpr dms_b = S32(dms_dest);\n"
        f"{i3}uint16_t dms_f = (uint16_t)MEM_HU(0x0, dms_b);\n"
        f"{i3}uint32_t dms_sz = U32(MEM_W(0x4, dms_b));\n"
        f"{i3}int dms_tgt = (dms_dest == 0x801F3CC0u);\n"
        f"{i3}int dms_heap = ((dms_f == 1u || dms_f == 2u) && dms_sz != 0u && dms_sz < 0x800000u);\n"
        f"{i3}if (dms_tgt || dms_heap || s_dms_v1_n <= 12 || (s_dms_v1_n % 400) == 0) {{\n"
        f"{i4}fprintf(stderr,\n"
        + i4 + r'"[drain-mesh-stomp] n=%d site_pc=0x%08X dest=0x%08X pre_f=0x%X pre_sz=0x%X reg=v1 off=0 val=0 ra=0x%08X%s\n",' + "\n"
        f"{i4}s_dms_v1_n, (unsigned)g_rs64_last_guest_pc, dms_dest,\n"
        f"{i4}(unsigned)dms_f, dms_sz, U32(ctx->r31),\n"
        f'{i4}dms_tgt ? " TARGET" : (dms_heap ? " HEAPLIKE" : " sample"));\n'
        f"{i4}fflush(stderr);\n"
        f"{i3}}}\n"
        f"{i2}}} else if (s_dms_v1_n <= 12) {{\n"
        f"{i3}fprintf(stderr,\n"
        + i3 + r'"[drain-mesh-stomp] n=%d site_pc=0x%08X dest=0x%08X reg=v1 off=0 sample_oob ra=0x%08X\n",' + "\n"
        f"{i3}s_dms_v1_n, (unsigned)g_rs64_last_guest_pc, dms_dest, U32(ctx->r31));\n"
        f"{i3}fflush(stderr);\n"
        f"{i2}}}\n"
        f"{i1}}}\n"
        f"{i}}}\n"
        f"{i}MEM_W(0X0, ctx->r3) = ctx->r2;\n"
    )


def main() -> int:
    # Sanity: format lines must embed backslash-n, not real newlines.
    sample = a0_block()
    for line in sample.splitlines():
        if "[drain-mesh-stomp]" in line and "site_pc" in line:
            if line.count('"') < 2 or "\\n" not in line:
                print("ERROR: format line missing \\\\n escape:", repr(line), file=sys.stderr)
                return 1

    text = FUNCS.read_text()
    report = []
    changed = False

    start = text.find("RECOMP_FUNC void drainMeshReleaseQueue(uint8_t* rdram, recomp_context* ctx) {")
    if start < 0:
        print("ERROR: drainMeshReleaseQueue not found", file=sys.stderr)
        return 1
    end = text.find("RECOMP_FUNC void ", start + 10)
    if end < 0:
        print("ERROR: next RECOMP_FUNC after drainMesh not found", file=sys.stderr)
        return 1
    body = text[start:end]

    if "drain-mesh-stomp a0+4 (s641" in body:
        report.append("a0+4 already present")
    else:
        pat_a0 = re.compile(r"^            MEM_W\(0X4, ctx->r4\) = 0;\n", re.M)
        n = len(pat_a0.findall(body))
        if n != 5:
            print(f"ERROR a0+4 zero count={n} (want 5)", file=sys.stderr)
            return 1
        # Function repl: re.sub string repl interprets \n escapes and would
        # corrupt C format strings that contain backslash-n.
        blk = a0_block()
        body, n_sub = pat_a0.subn(lambda _m: blk, body)
        if n_sub != 5:
            print(f"ERROR a0+4 sub count={n_sub}", file=sys.stderr)
            return 1
        changed = True
        report.append(f"a0+4 stomp x{n_sub}")

    if "drain-mesh-stomp v1+0 (s641" in body:
        report.append("v1+0 already present")
    else:
        n_total = 0
        for indent in ("                ", "            "):
            pat = re.compile(
                r"^" + re.escape(indent) + r"MEM_W\(0X0, ctx->r3\) = ctx->r2;\n",
                re.M,
            )
            n = len(pat.findall(body))
            if n == 0:
                continue
            blk = v1_block(indent)
            body, n_sub = pat.subn(lambda _m, b=blk: b, body)
            n_total += n_sub
            changed = True
        if n_total != 10:
            print(f"ERROR v1+0 write count={n_total} (want 10)", file=sys.stderr)
            return 1
        report.append(f"v1+0 stomp x{n_total}")

    if changed:
        if "#include <stdio.h>" not in text:
            text = text.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <stdio.h>\n', 1)
        if "#include <stdlib.h>" not in text:
            text = text.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <stdlib.h>\n', 1)
        text = text[:start] + body + text[end:]
        FUNCS.write_text(text)

    print("apply_s641:", "; ".join(report), "; wrote" if changed else "; no change")
    return 0


if __name__ == "__main__":
    sys.exit(main())
