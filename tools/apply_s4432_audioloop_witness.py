#!/usr/bin/env python3
"""s4432: observe the title audio loop 0x8008EE10..0x8008EE9C (read-only).

Stages: 0 loop head, 1 after osRecvMesg (msg byte vs s3/s2), 2 before the
0x8008EE84 osAiSetNextBuffer call, 3 after it returns, 4 before the 0x8008EE08 call.
"""
from pathlib import Path

P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
MARK = "PATCH: s4432 audioloop"
t = P.read_text()
if MARK in t:
    print("already applied")
    raise SystemExit(0)


def w(stage):
    return f"    rs64_audioloop_witness(rdram, ctx, {stage}u); /* {MARK} */\n"


def rep(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit(f"anchor count {t.count(old)}: {old!r}")
    t = t.replace(old, new, 1)


rep("L_8008EE10:\n", "L_8008EE10:\n" + w(0))
rep("    // 0x8008EE24: lw          $v0, 0x10($sp)\n",
    w(1) + "    // 0x8008EE24: lw          $v0, 0x10($sp)\n")
rep("    // 0x8008EE84: jal         0x80029E80\n",
    w(2) + "    // 0x8008EE84: jal         0x80029E80\n")
rep("    osAiSetNextBuffer_recomp(rdram, ctx);\n        goto after_5;\n",
    "    osAiSetNextBuffer_recomp(rdram, ctx);\n" + w(3) + "        goto after_5;\n")
rep("    // 0x8008EE08: jal         0x80029E80\n",
    w(4) + "    // 0x8008EE08: jal         0x80029E80\n")
anchor = '#include "funcs.h"\n'
if t.count(anchor) != 1:
    raise SystemExit("funcs.h anchor")
t = t.replace(anchor, anchor +
    "extern void rs64_audioloop_witness(uint8_t* rdram, recomp_context* ctx, uint32_t stage);\n", 1)
P.write_text(t)
print("applied")
