#!/usr/bin/env python3
"""Add the s4601 target/control ranges to every generated store census."""
from pathlib import Path

RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4601 voice34 span census"
OLD = "static void rs64_m5_writer_parity(char width, uint32_t pc,\n                                   uint32_t addr, uint32_t value) {\n"
CALL = (
    "    { uint32_t s4601_p = addr & 0x1FFFFFFFu; "
    "if ((s4601_p >= 0x1724C0u && s4601_p < 0x17250Cu) || "
    "(s4601_p >= 0x17C000u && s4601_p < 0x17D000u)) "
    "rs64_s4597_target_store(width, pc, addr, value); } /* " + MARK + " */\n"
)

count = 0
for p in sorted(RF.glob("funcs_*.c")):
    s = p.read_text()
    if MARK in s:
        continue
    old_call = (
        "    { uint32_t s4598_p = addr & 0x1FFFFFFFu; "
        "if ((s4598_p >= 0x1724F4u && s4598_p < 0x1724F8u) || "
        "(s4598_p >= 0x17C000u && s4598_p < 0x17D000u)) "
        "rs64_s4597_target_store(width, pc, addr, value); } /* PATCH: s4598 complete voice34 census */\n"
    )
    if old_call in s:
        s = s.replace(old_call, CALL, 1)
        p.write_text(s)
        count += 1
        continue
    if OLD not in s:
        continue
    anchor = '#include "funcs.h"\n'
    if anchor not in s:
        raise SystemExit(f"missing include anchor: {p}")
    s = s.replace(anchor, anchor + "extern void rs64_s4597_target_store(char, uint32_t, uint32_t, uint32_t);\n", 1)
    s = s.replace(OLD, OLD + CALL, 1)
    p.write_text(s)
    count += 1
print(f"patched files: {count}")
if count == 0:
    print("generated writer-parity sites already patched")
