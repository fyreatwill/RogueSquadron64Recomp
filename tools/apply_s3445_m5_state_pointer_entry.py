#!/usr/bin/env python3
"""Add the s3445 state-pointer entry witness to generated output."""
from pathlib import Path

BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3445 state-pointer entry"
target = BASE / "funcs_0.c"
text = target.read_text()
if MARKER not in text:
    anchor = '#include "funcs.h"\n'
    if text.count(anchor) != 1:
        raise SystemExit("funcs_0.c: funcs.h anchor count mismatch")
    text = text.replace(anchor, anchor +
        'extern void rs64_m5_state_pointer_entry(uint8_t* rdram, recomp_context* ctx);\n', 1)
    needle = 'RECOMP_FUNC void rs_free(uint8_t* rdram, recomp_context* ctx) {\n'
    if text.count(needle) != 1:
        raise SystemExit("rs_free entry count mismatch")
    text = text.replace(needle, needle +
        '    rs64_m5_state_pointer_entry(rdram, ctx); /* ' + MARKER + ' */\n', 1)
    target.write_text(text)
    print("funcs_0.c: 1")
else:
    print("already applied")
