#!/usr/bin/env python3
"""s4680: retain every generated write to the MusyX voice status table."""
from pathlib import Path

ROOT = Path("/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp")
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s4680 status table store"
SITES = {
    0x8009B2C4: "ctx->r1, 0X4620, 0u",
    0x8009B30C: "ctx->r1, 0X4620, ctx->r2",
    0x8009B6F8: "ctx->r1, 0X4620, ctx->r23",
    0x8009B7A8: "ctx->r1, 0X4620, 0u",
    0x8009B7CC: "ctx->r1, 0X4620, ctx->r8",
    0x8009B7EC: "ctx->r1, 0X4620, 0u",
    0x8009BBF0: "ctx->r1, 0X4620, 0u",
}

path = RF / "funcs_26.c"
text = path.read_text()
if MARK in text:
    print("s4680 already present")
    raise SystemExit(0)

decl = 'extern void rs64_m5_status_table_store(uint8_t*, uint32_t, uint32_t, uint32_t, uint32_t);\n'
anchor = '#include "funcs.h"\n'
if text.count(anchor) != 1:
    raise SystemExit(f"funcs_26.c funcs.h anchor count={text.count(anchor)}")
text = text.replace(anchor, anchor + decl, 1)

inserted = 0
for pc, expr in SITES.items():
    needle = f"    // 0x{pc:08X}:"
    start = text.find(needle)
    if start < 0:
        raise SystemExit(f"missing site 0x{pc:08X}")
    store = text.find("    MEM_B(0X4620, ctx->r1) =", start)
    if store < 0 or store > text.find("RECOMP_FUNC", start + 1):
        raise SystemExit(f"missing status store after 0x{pc:08X}")
    before = text[:store]
    base, offset, value = expr.split(", ")
    line = ("    rs64_m5_status_table_store(rdram, 0x%08Xu, "
            "U32(ADD32(%s, %s)), U32(MEM_BU(%s, %s)), U32(%s)); "
            "/* %s */\n") % (pc, base, offset, base, offset, value, MARK)
    text = before + line + text[store:]
    inserted += 1

path.write_text(text)
print(f"funcs_26.c: status-table sites patched x{inserted}")
