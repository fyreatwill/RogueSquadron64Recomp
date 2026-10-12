#!/usr/bin/env python3
"""s4638: widen the s4299 nodewatch store filter in generated funcs_*.c to cover
the hangar colour buffer 0x656400..0x696400, so rs64_s4299_store_watch (gated by
ROGUESQ_LOG_S4299) sees CPU stores into it. Idempotent."""
from pathlib import Path
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = "(nw_p >= 0x170000u && nw_p < 0x1A0000u))"
NEW = "(nw_p >= 0x170000u && nw_p < 0x1A0000u) || (nw_p >= 0x656400u && nw_p < 0x696400u))"
n = 0
for p in sorted(RF.glob("funcs_*.c")):
    s = p.read_text()
    if OLD in s and "0x696400u" not in s:
        p.write_text(s.replace(OLD, NEW)); n += 1
print("patched files:", n)
