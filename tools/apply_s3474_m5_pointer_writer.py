#!/usr/bin/env python3
"""Install the regeneration-safe M5 pointer-span store witness."""
from pathlib import Path


BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3474 M5 pointer-span store witness"
PARITY_MARKER = "PATCH: s3474 M5 pointer-span parity witness"
DECL = "    extern void rs64_m5_pointer_span_store(char width, uint32_t pc, uint32_t addr, uint32_t value);\n"
CALL = "    rs64_m5_pointer_span_store(width, pc, addr, value); /* PATCH: s3474 M5 pointer-span store witness */\n"


def main() -> None:
    changed = 0
    for path in sorted(BASE.glob("funcs_*.c")):
        text = path.read_text(encoding="utf-8")
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
