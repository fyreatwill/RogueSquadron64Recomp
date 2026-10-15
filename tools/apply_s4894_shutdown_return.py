#!/usr/bin/env python3
"""Add the post-body shutdownAudioEngine return witness to funcs_24.c."""
from pathlib import Path


ROOT = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
TARGET = ROOT / "funcs_24.c"
MARKER = "PATCH: s4894 callback teardown return"

text = TARGET.read_text()
if MARKER in text:
    print("s4894 return already present")
    raise SystemExit(0)

anchor = "    // 0x80091EAC: nop\n\n    return;\n"
if text.count(anchor) != 1:
    raise SystemExit(f"shutdownAudioEngine return anchor count={text.count(anchor)}")

insert = (
    "    { extern void rs64_m5_callback_teardown_event(unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned, unsigned); "
    "rs64_m5_callback_teardown_event(2u, U32(ctx->r31), U32(MEM_W(0, S32(0x8011A8A4u))), "
    "U32(MEM_W(4, S32(0x8011A8A4u))), U32(MEM_W(8, S32(0x8011A8A4u))), "
    "U32(MEM_W(12, S32(0x8011A8A4u))), 0u, 0u); } "
    f"/* {MARKER} */\n"
)
TARGET.write_text(text.replace(anchor, insert + anchor, 1))
print("s4894 callback teardown return patched x1")
