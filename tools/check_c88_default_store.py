#!/usr/bin/env python3
"""Fail if reapplyDisplayMode 0x8008EC88 still force-zeros by default.

s2608 inverted the hatch: unset stores ctx->r2; ROGUESQ_M5_C88_VALUE=0 is
the rollback. ORIGIN: writer is reapplyDisplayMode; guest requested 0x01;
retail post-store is 0x01000000.
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
n64 = root.parent / "N64Recomp"
live = n64 / "RecompiledFuncs" / "funcs_23.c"
fixup = n64 / "fixup_game_funcs.py"

guest_default = re.compile(
    r'getenv\("ROGUESQ_M5_C88_VALUE"\)\[0\] == \'0\'\) \? 0 : ctx->r2'
)
old_force_zero = re.compile(
    r'getenv\("ROGUESQ_M5_C88_VALUE"\)\[0\] != \'0\'\) \? ctx->r2 : 0'
)

for path in (live, fixup):
    if not path.is_file():
        sys.exit(f"missing {path}")
    text = path.read_text()
    if old_force_zero.search(text):
        sys.exit(f"{path.name}: C88 hatch still force-zeros unless env is nonzero")
    if "0x8008EC88" not in text:
        sys.exit(f"{path.name}: missing 0x8008EC88 site")
    if not guest_default.search(text):
        sys.exit(f"{path.name}: missing guest-default C88 ternary")

print("ok: 0x8008EC88 default stores ctx->r2; env 0 is the rollback")
