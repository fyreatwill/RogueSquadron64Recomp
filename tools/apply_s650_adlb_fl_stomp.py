#!/usr/bin/env python3
"""Re-apply s650 allocateDisplayListBuffer freelist-header stomp probe (idempotent).

s649 freeroll Outcome B: recovery-active freelist to_zero 0x2/0x60→0 at
phys 0x1F3CC0 with arm_fl LIVE, flz_fault_hdr=0; to_zero_correlate last_sym=
allocateDisplayListBuffer (last_in_hdr=0, fa=+0x50). busy_rearm did not
catch an in_hdr fault — escalate leaf probe on ADLB stores that touch
[0x801F3CC0, 0x801F3CC8).

Instruments every MEM_W store in allocateDisplayListBuffer whose effective
destination lands in the freelist header window (or first N samples for
posctrl). Tag: [adlb-fl-stomp]. Gate: ROGUESQ_LOG_FL_ZERO_WATCH.
"""
from pathlib import Path
import os
import re
import sys

FUNCS = Path(os.environ.get(
    "RECOMP_FUNCS",
    str(Path.home() / "Documents/Tools/N64Recomp/RecompiledFuncs/funcs_3.c"),
))

MARKER = "adlb-fl-stomp (s650"


def probe_block(indent: str, reg: str, off: str, site: str) -> str:
    """reg is ctx->rN; off is hex like 0X4 or 0X0; site is guest pc string."""
    i = indent
    i1 = indent + "    "
    i2 = indent + "        "
    i3 = indent + "            "
    # C format string must keep \\n as two chars for fprintf.
    return (
        f"{i}{{ // PATCH: {MARKER}, item -404) -- see fixup_game_funcs.py comment\n"
        f"{i1}static int s_adlb_fl_en = -1;\n"
        f'{i1}if (s_adlb_fl_en < 0) {{ const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH"); '
        f"s_adlb_fl_en = (e && e[0] && e[0] != '0') ? 1 : 0; }}\n"
        f"{i1}if (s_adlb_fl_en) {{\n"
        f"{i2}uint32_t adlb_base = U32({reg});\n"
        f"{i2}uint32_t adlb_dest = adlb_base + {off}u;\n"
        f"{i2}static int s_adlb_fl_n = 0;\n"
        f"{i2}s_adlb_fl_n++;\n"
        f"{i2}int adlb_tgt = (adlb_dest >= 0x801F3CC0u && adlb_dest < 0x801F3CC8u);\n"
        f"{i2}int adlb_near = (adlb_base >= 0x801F3C00u && adlb_base < 0x801F3D00u);\n"
        f"{i2}if (adlb_tgt || adlb_near || s_adlb_fl_n <= 16 || (s_adlb_fl_n % 500) == 0) {{\n"
        f"{i3}uint16_t adlb_f = 0; uint32_t adlb_sz = 0;\n"
        f"{i3}if (adlb_base >= 0x80000000u && adlb_base < 0x80800000u) {{\n"
        f"{i3}    gpr adlb_b = S32(adlb_base);\n"
        f"{i3}    adlb_f = (uint16_t)MEM_HU(0x0, adlb_b);\n"
        f"{i3}    adlb_sz = U32(MEM_W(0x4, adlb_b));\n"
        f"{i3}}}\n"
        f"{i3}fprintf(stderr,\n"
        + i3
        + r'"[adlb-fl-stomp] n=%d site='
        + site
        + r' dest=0x%08X base=0x%08X off=0x%X pre_f=0x%X pre_sz=0x%X ra=0x%08X%s\n",'
        + "\n"
        f"{i3}s_adlb_fl_n, adlb_dest, adlb_base, (unsigned){off}u,\n"
        f"{i3}(unsigned)adlb_f, adlb_sz, U32(ctx->r31),\n"
        f'{i3}adlb_tgt ? " TARGET" : (adlb_near ? " NEAR" : " sample"));\n'
        f"{i3}fflush(stderr);\n"
        f"{i2}}}\n"
        f"{i1}}}\n"
        f"{i}}}\n"
    )


def main() -> int:
    text = FUNCS.read_text()
    start = text.find(
        "RECOMP_FUNC void allocateDisplayListBuffer(uint8_t* rdram, recomp_context* ctx) {"
    )
    if start < 0:
        print("ERROR: allocateDisplayListBuffer not found", file=sys.stderr)
        return 1
    end = text.find("RECOMP_FUNC void ", start + 10)
    if end < 0:
        print("ERROR: next RECOMP_FUNC after ADLB not found", file=sys.stderr)
        return 1
    body = text[start:end]
    report = []
    changed_body = body

    # Indent lengths measured from live funcs_3.c body (spaces only).
    # Idempotent per site via site=0x... uniqueness in already-patched body.
    sites = [
        # 0x80007DC4 sw $v0,0($a0) — delay-slot + fallthrough (4- and 8-space)
        (
            re.compile(r"^(        )MEM_W\(0X0, ctx->r4\) = ctx->r2;\n", re.M),
            "        ",
            "ctx->r4",
            "0X0",
            "0x80007DC4a",
            1,
        ),
        (
            re.compile(r"^(    )MEM_W\(0X0, ctx->r4\) = ctx->r2;\n", re.M),
            "    ",
            "ctx->r4",
            "0X0",
            "0x80007DC4b",
            1,
        ),
        # 0x80007DD4 sw $zero,0x4($v1)
        (
            re.compile(r"^(    )MEM_W\(0X4, ctx->r3\) = 0;\n", re.M),
            "    ",
            "ctx->r3",
            "0X4",
            "0x80007DD4",
            1,
        ),
        # 0x80007DC8 sw $a0,0x4($v0) — R1 guard write
        (
            re.compile(r"^(            )MEM_W\(0X4, ctx->r2\) = ctx->r4;\n", re.M),
            "            ",
            "ctx->r2",
            "0X4",
            "0x80007DC8",
            1,
        ),
        # 0x80007DF8 sw $zero,0x4($v0) — two FREELIST_NEXT_GUARD arms
        (
            re.compile(r"^(                )MEM_W\(0X4, ctx->r2\) = 0;\n", re.M),
            "                ",
            "ctx->r2",
            "0X4",
            "0x80007DF8a",
            1,
        ),
        (
            re.compile(r"^(            )MEM_W\(0X4, ctx->r2\) = 0;\n", re.M),
            "            ",
            "ctx->r2",
            "0X4",
            "0x80007DF8b",
            1,
        ),
        # 0x80007E24 / 0x80007E2C (20-space, inside DEREF/RWRITE guards)
        (
            re.compile(r"^(                    )MEM_W\(0X0, ctx->r3\) = ctx->r4;\n", re.M),
            "                    ",
            "ctx->r3",
            "0X0",
            "0x80007E24",
            1,
        ),
        (
            re.compile(r"^(                    )MEM_W\(0X4, ctx->r4\) = ctx->r2;\n", re.M),
            "                    ",
            "ctx->r4",
            "0X4",
            "0x80007E2C",
            1,
        ),
        # 0x80007E38 / 0x80007E3C (12-space, inside RESET guards)
        (
            re.compile(r"^(            )MEM_W\(0X0, ctx->r4\) = 0;\n", re.M),
            "            ",
            "ctx->r4",
            "0X0",
            "0x80007E38",
            1,
        ),
        (
            re.compile(r"^(            )MEM_W\(0X0, ctx->r3\) = ctx->r4;\n", re.M),
            "            ",
            "ctx->r3",
            "0X0",
            "0x80007E3C",
            1,
        ),
    ]

    total = 0
    for pat, indent, reg, off, site, want in sites:
        # Match only our probe format lines (avoid collision with older GUARD
        # comments that also embed site=0x80007DC8 etc.).
        if f"[adlb-fl-stomp]" in changed_body and f"site={site} dest=" in changed_body:
            report.append(f"{site} already")
            continue
        n = len(pat.findall(changed_body))
        if n != want:
            print(
                f"ERROR site {site}: count={n} want={want}",
                file=sys.stderr,
            )
            return 1
        blk = probe_block(indent, reg, off, site)

        def make_repl(b=blk):
            def _r(m):
                return b + m.group(0)

            return _r

        changed_body, n_sub = pat.subn(make_repl(), changed_body)
        if n_sub != want:
            print(f"ERROR site {site}: sub={n_sub} want={want}", file=sys.stderr)
            return 1
        total += n_sub
        report.append(f"{site} x{n_sub}")

    if total < 1 and all("already" in r for r in report):
        print("apply_s650:", "; ".join(report), "; no change")
        return 0
    if total < 1:
        print("ERROR: no sites patched", file=sys.stderr)
        return 1

    # Sanity: format lines must embed backslash-n
    for line in changed_body.splitlines():
        if "[adlb-fl-stomp]" in line and "dest=" in line:
            if "\\n" not in line:
                print("ERROR: format missing \\\\n:", repr(line), file=sys.stderr)
                return 1

    text = text[:start] + changed_body + text[end:]
    if '#include <stdio.h>' not in text[:start + 200]:
        # stdio already required by other patches in funcs_3.c
        pass
    FUNCS.write_text(text)
    print("apply_s650:", "; ".join(report), f"; total={total} wrote")
    return 0


if __name__ == "__main__":
    sys.exit(main())
