#!/usr/bin/env python3
"""Install the regeneration-safe call sites for the M5 table-selection witness."""

from pathlib import Path


GEN = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_14.c"
MARKER_DC = "PATCH: s3469 M5 table selection at 644DC"
MARKER_24 = "PATCH: s3469 M5 table selection at 64524"


def main() -> None:
    text = GEN.read_text(encoding="utf-8")
    decl = "extern void rs64_m5_table_selection(uint8_t* rdram, recomp_context* ctx, uint32_t pc);\n"
    if decl not in text:
        anchor = "extern void rs64_m5_producer_input(uint8_t* rdram, recomp_context* ctx, uint32_t producer_pc, uint32_t call_pc, uint32_t target_pc);\n"
        if text.count(anchor) != 1:
            raise SystemExit("s3469 declaration anchor is not unique")
        text = text.replace(anchor, anchor + decl, 1)
    dc = "    rs64_m5_table_selection(rdram, ctx, 0x800644DCu); /* PATCH: s3469 M5 table selection at 644DC */\n"
    if MARKER_DC not in text:
        anchor = "    // 0x800644E0: lw          $v0, 0x14($s0)\n"
        if text.count(anchor) != 1:
            raise SystemExit("s3469 644DC anchor is not unique")
        text = text.replace(anchor, dc + anchor, 1)
    selected = "    rs64_m5_table_selection(rdram, ctx, 0x80064524u); /* PATCH: s3469 M5 table selection at 64524 */\n"
    if MARKER_24 not in text:
        anchor = "    // 0x80064524: sw          $s0, 0x0($v0)\n"
        if text.count(anchor) != 1:
            raise SystemExit("s3469 64524 anchor is not unique")
        text = text.replace(anchor, selected + anchor, 1)
    GEN.write_text(text, encoding="utf-8")
    print("s3469 M5 table-selection witness patched funcs_14.c")


if __name__ == "__main__":
    main()
