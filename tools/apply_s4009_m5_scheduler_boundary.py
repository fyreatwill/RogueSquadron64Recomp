#!/usr/bin/env python3
"""Add the regeneration-safe M5 scheduler boundary table."""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_4.c")
MARK = "PATCH: s4009 M5 scheduler boundary"

HELPER = r'''
extern void rs64_m5_scheduler_boundary(uint8_t* rdram, const char* edge,
                                       uint32_t pc, uint32_t a0, uint32_t a1,
                                       uint32_t a2, uint32_t successor);
'''

LOAD = (
    "    // 0x80019CD8: lw          $a0, 0x10($sp)\n"
    "    ctx->r4 = MEM_W(ctx->r29, 0X10);\n"
)
LOAD_NEW = LOAD + (
    "    rs64_m5_scheduler_boundary(rdram, \"task-load\", 0x80019CD8u,\n"
    "                               U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                               U32(MEM_W(S32(0X8013 << 16), -0X72C0)));\n"
)

SEND = (
    "    // 0x80019F64: jal         0x80033410\n"
    "    // 0x80019F68: nop\n"
    "\n"
    "    { /* PATCH: s3294 scheduler stall */\n"
)
SEND_NEW = (
    "    // 0x80019F64: jal         0x80033410\n"
    "    // 0x80019F68: nop\n"
    "\n"
    "    rs64_m5_scheduler_boundary(rdram, \"send-before\", 0x80019F64u,\n"
    "                               U32(ctx->r4), U32(ctx->r5), U32(ctx->r6),\n"
    "                               U32(MEM_W(S32(0X8013 << 16), -0X72C0)));\n"
    "    { /* PATCH: s3294 scheduler stall */\n"
)

def apply(text: str):
    if MARK in text:
        return text, False
    if text.count('#include "funcs.h"\n') != 1:
        raise RuntimeError("funcs.h anchor count mismatch")
    if text.count(LOAD) != 1 or text.count(SEND) != 1:
        raise RuntimeError("scheduler boundary anchor count mismatch")
    text = text.replace('#include "funcs.h"\n', '#include "funcs.h"\n' + HELPER + '\n/* ' + MARK + ' */\n', 1)
    text = text.replace(LOAD, LOAD_NEW, 1)
    text = text.replace(SEND, SEND_NEW, 1)
    return text, True

if __name__ == "__main__":
    text, changed = apply(GEN.read_text())
    if changed:
        GEN.write_text(text)
        print(f"patched {GEN}")
    else:
        print("already patched")
