#!/usr/bin/env python3
"""Re-apply s652 submitSceneNodeRender freelist-header zero-store probe.

s651 freeroll Outcome B (refined): fault_ring LIVE, near_hdr=9/16, in_hdr=0.
Last near leaf submitSceneNodeRender+0x380 / guest 0x80010054 is
  sw $v0, 0x30($s4)  with fa=hdr+0x40 ⇒ s4=hdr+0x10 (user ptr of LIVE
  flags=0x2 size=0x60 allocation). That store is payload traffic, NOT the
  header zero — H-ssnr380-writer REFUTED by code+ring.

Residual SSNR hypothesis: list-unlink sw $zero,0/4($reg) sites may zero
heap flags/size if reg lands on 0x801F3CC0. Instrument every
MEM_W(0X0/0X4, ...)=0 in submitSceneNodeRender. Tag: [ssnr-hdr-zero].
Gate: ROGUESQ_LOG_FL_ZERO_WATCH.
"""
from pathlib import Path
import os
import re
import sys

FUNCS = Path(os.environ.get(
    "RECOMP_FUNCS",
    str(Path.home() / "Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c"),
))

MARKER = "ssnr-hdr-zero (s652"


def probe_block(indent: str, reg: str, off: str, site: str) -> str:
    i = indent
    i1 = indent + "    "
    i2 = indent + "        "
    i3 = indent + "            "
    return (
        f"{i}{{ // PATCH: {MARKER}, item -406) -- see fixup_game_funcs.py comment\n"
        f"{i1}static int s_ssnr_hz_en = -1;\n"
        f'{i1}if (s_ssnr_hz_en < 0) {{ const char* e = getenv("ROGUESQ_LOG_FL_ZERO_WATCH"); '
        f"s_ssnr_hz_en = (e && e[0] && e[0] != '0') ? 1 : 0; }}\n"
        f"{i1}if (s_ssnr_hz_en) {{\n"
        f"{i2}uint32_t ssnr_base = U32({reg});\n"
        f"{i2}uint32_t ssnr_dest = ssnr_base + {off}u;\n"
        f"{i2}static int s_ssnr_hz_n = 0;\n"
        f"{i2}s_ssnr_hz_n++;\n"
        f"{i2}int ssnr_tgt = (ssnr_dest >= 0x801F3CC0u && ssnr_dest < 0x801F3CC8u);\n"
        f"{i2}int ssnr_near = (ssnr_base >= 0x801F3C00u && ssnr_base < 0x801F3D00u);\n"
        f"{i2}if (ssnr_tgt || ssnr_near || s_ssnr_hz_n <= 16 || (s_ssnr_hz_n % 500) == 0) {{\n"
        f"{i3}uint16_t ssnr_f = 0; uint32_t ssnr_sz = 0;\n"
        f"{i3}if (ssnr_base >= 0x80000000u && ssnr_base < 0x80800000u) {{\n"
        f"{i3}    gpr ssnr_b = S32(ssnr_base);\n"
        f"{i3}    ssnr_f = (uint16_t)MEM_HU(0x0, ssnr_b);\n"
        f"{i3}    ssnr_sz = U32(MEM_W(0x4, ssnr_b));\n"
        f"{i3}}}\n"
        f"{i3}fprintf(stderr,\n"
        + i3
        + r'"[ssnr-hdr-zero] n=%d site='
        + site
        + r' dest=0x%08X base=0x%08X off=0x%X pre_f=0x%X pre_sz=0x%X ra=0x%08X%s\n",'
        + "\n"
        f"{i3}s_ssnr_hz_n, ssnr_dest, ssnr_base, (unsigned){off}u,\n"
        f"{i3}(unsigned)ssnr_f, ssnr_sz, U32(ctx->r31),\n"
        f'{i3}ssnr_tgt ? " TARGET" : (ssnr_near ? " NEAR" : " sample"));\n'
        f"{i3}fflush(stderr);\n"
        f"{i2}}}\n"
        f"{i1}}}\n"
        f"{i}}}\n"
    )


def main() -> int:
    text = FUNCS.read_text()
    start = text.find(
        "RECOMP_FUNC void submitSceneNodeRender(uint8_t* rdram, recomp_context* ctx) {"
    )
    if start < 0:
        print("ERROR: submitSceneNodeRender not found", file=sys.stderr)
        return 1
    end = text.find("RECOMP_FUNC void ", start + 10)
    if end < 0:
        print("ERROR: next RECOMP_FUNC after SSNR not found", file=sys.stderr)
        return 1
    body = text[start:end]

    if MARKER in body and "[ssnr-hdr-zero]" in body:
        print("apply_s652: already present; no change")
        return 0

    # Match bare zero-stores to off 0 or 4 (not already inside a probe block).
    # Capture indent, off, reg.
    pat = re.compile(
        r"^([ \t]*)MEM_W\((0X0|0X4), (ctx->r\d+)\) = 0;\n",
        re.M,
    )

    # Walk matches and skip those already preceded by our marker in previous ~15 lines.
    lines = body.splitlines(keepends=True)
    # Rebuild with probes; track guest pc from comments.
    out = []
    pc = "unknown"
    total = 0
    site_counts: dict[str, int] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        m_pc = re.search(r"// 0x([0-9A-Fa-f]+):", line)
        if m_pc:
            pc = "0x" + m_pc.group(1).upper().replace("0X", "")
            if not pc.startswith("0x"):
                pc = "0x" + m_pc.group(1)
            # normalize
            pc = "0x" + m_pc.group(1).upper()

        m = re.match(r"^([ \t]*)MEM_W\((0X0|0X4), (ctx->r\d+)\) = 0;\n$", line)
        if m:
            # Skip if already probed (look back for marker)
            lookback = "".join(lines[max(0, i - 20) : i])
            if MARKER in lookback or "[ssnr-hdr-zero]" in lookback:
                out.append(line)
                i += 1
                continue
            indent, off, reg = m.group(1), m.group(2), m.group(3)
            # Unique site key: guest pc + off + reg suffix
            reg_n = reg.replace("ctx->r", "r")
            base_site = f"{pc}_{off.lower()}_{reg_n}"
            n_dup = site_counts.get(base_site, 0)
            site_counts[base_site] = n_dup + 1
            site = base_site if n_dup == 0 else f"{base_site}_{n_dup}"
            out.append(probe_block(indent, reg, off, site))
            out.append(line)
            total += 1
            i += 1
            continue
        out.append(line)
        i += 1

    if total < 1:
        print("ERROR: no zero-stores patched", file=sys.stderr)
        return 1

    new_body = "".join(out)
    # Sanity: format lines must embed backslash-n
    for line in new_body.splitlines():
        if "[ssnr-hdr-zero]" in line and "dest=" in line:
            if "\\n" not in line:
                print("ERROR: format missing \\\\n:", repr(line), file=sys.stderr)
                return 1

    text = text[:start] + new_body + text[end:]
    FUNCS.write_text(text)
    print(f"apply_s652: patched {total} zero-stores in submitSceneNodeRender; wrote")
    return 0


if __name__ == "__main__":
    sys.exit(main())
