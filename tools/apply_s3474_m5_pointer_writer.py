#!/usr/bin/env python3
"""Install the regeneration-safe M5 pointer-span store witness."""
from pathlib import Path


BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3474 M5 pointer-span store witness"
PARITY_MARKER = "PATCH: s3474 M5 pointer-span parity witness"
WRITER_MARKER = "PATCH: s3487 M5 selector writer inputs"
DECL = "    extern void rs64_m5_pointer_span_store(char width, uint32_t pc, uint32_t addr, uint32_t value);\n"
CALL = "    rs64_m5_pointer_span_store(width, pc, addr, value); /* PATCH: s3474 M5 pointer-span store witness */\n"
WRITER_DECL = "    extern void rs64_m5_selector_writer(uint32_t v0, uint32_t s0, uint32_t s1, uint32_t s2, uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t ra, uint32_t value);\n"
WRITER_CALL = "    rs64_m5_selector_writer(U32(ctx->r2), U32(ctx->r16), U32(ctx->r17), U32(ctx->r18), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r31), U32(ctx->r2)); /* PATCH: s3487 M5 selector writer inputs */\n"


def main() -> None:
    changed = 0
    for path in sorted(BASE.glob("funcs_*.c")):
        text = path.read_text(encoding="utf-8")
        if "0x80091074u" in text and WRITER_MARKER not in text:
            anchor = "    rs64_probe_submit_gate_store('W', 0x80091074u, U32(ADD32(ctx->r1, -0X68B0)), U32(ctx->r2));\n"
            if anchor in text:
                text = text.replace(anchor, anchor + WRITER_DECL + WRITER_CALL, 1)
                path.write_text(text, encoding="utf-8")
                changed += 1
                continue
        start = text.find("static void rs64_probe_submit_gate_store(")
        if start < 0:
            continue
        old = ("    if (!enabled) return;\n"
               "        extern void rs64_m5_pointer_span_store(char width, uint32_t pc, uint32_t addr, uint32_t value);\n"
               "        rs64_m5_pointer_span_store(width, pc, addr, value); /* PATCH: s3474 M5 pointer-span store witness */\n")
        if old in text[start:]:
            text = text.replace(old, "    extern void rs64_m5_pointer_span_store(char width, uint32_t pc, uint32_t addr, uint32_t value);\n"
                                     "    rs64_m5_pointer_span_store(width, pc, addr, value); /* PATCH: s3474 M5 pointer-span store witness */\n"
                                     "    if (!enabled) return;\n", 1)
            path.write_text(text, encoding="utf-8")
            changed += 1
            continue
        if MARKER in text:
            pass
        parity_start = text.find("static void rs64_m5_writer_parity(")
        if parity_start >= 0 and PARITY_MARKER not in text:
            anchor = text.find("    if (!enabled) return;\n", parity_start)
            if anchor < 0:
                raise SystemExit(f"{path}: writer-parity enabled anchor is missing")
            end = anchor + len("    if (!enabled) return;\n")
            decl = "    extern void rs64_m5_pointer_span_store(char width, uint32_t pc, uint32_t addr, uint32_t value);\n"
            call = "    rs64_m5_pointer_span_store(width, pc, addr, value); /* PATCH: s3474 M5 pointer-span parity witness */\n"
            text = text[:end] + decl + call + text[end:]
            path.write_text(text, encoding="utf-8")
            changed += 1
            continue
        anchor = text.find("    if (!enabled) return;\n", start)
        if anchor < 0:
            raise SystemExit(f"{path}: submit-gate enabled anchor is missing")
        end = anchor + len("    if (!enabled) return;\n")
        text = text[:end] + DECL + CALL + text[end:]
        path.write_text(text, encoding="utf-8")
        changed += 1
    print(f"s3474 pointer-span store witness patched {changed} generated files")


if __name__ == "__main__":
    main()
