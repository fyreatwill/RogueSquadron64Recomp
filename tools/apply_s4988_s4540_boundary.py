#!/usr/bin/env python3
"""s4988: add caller-boundary provenance to the existing s4540 diagnostic.

This records the phase/origin, caller r31/r4, and the guest count/base observed
at the bad-row boundary. It does not rewrite, reject, or guard any value.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
p = root / "funcs_24.c"
s = p.read_text()
marker = "PATCH: s4988 caller boundary provenance"
if marker in s:
    print("s4988 already applied")
    raise SystemExit(0)

old = '''        fprintf(stderr,
            "[s4540-call] kind=bad a0=0x%08X n_all=%u n_in=%u s0=%u base=0x%08X count=%u sum=0x%08X\\n",
            a0, rs64_s4540_n_all, rs64_s4540_n_in, s0, mix_base, mix_count, sum);
'''
new = '''        fprintf(stderr,
            "[s4540-call] kind=bad phase=%u origin=0x%08X pc=0x80090F00 r31=0x%08X r4=0x%08X a0=0x%08X n_all=%u n_in=%u s0=%u base=0x%08X count=%u guest_base=0x%08X guest_count=%u sum=0x%08X /* PATCH: s4988 caller boundary provenance */\\n",
            rs64_vi_committed_width(), rs64_vi_committed_origin(),
            (uint32_t)ctx->r31, (uint32_t)ctx->r4, a0,
            rs64_s4540_n_all, rs64_s4540_n_in, s0, mix_base, mix_count,
            (uint32_t)MEM_W(-0x6908, S32(0x8015 << 16)),
            (uint32_t)MEM_HU(-0x6900, S32(0x8015 << 16)), sum);
'''
if s.count(old) != 1:
    raise SystemExit(f"bad-row anchor count={s.count(old)}")
if "extern uint32_t rs64_vi_committed_width(void);" not in s:
    s = s.replace("static void rs64_s4540_call(uint8_t* rdram, recomp_context* ctx) {\n",
                  "extern uint32_t rs64_vi_committed_width(void);\nextern uint32_t rs64_vi_committed_origin(void);\n\n"
                  "static void rs64_s4540_call(uint8_t* rdram, recomp_context* ctx) {\n", 1)
s = s.replace(old, new, 1)
p.write_text(s)
print("s4988 caller boundary provenance applied")
