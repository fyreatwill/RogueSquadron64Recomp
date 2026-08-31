#!/usr/bin/env python3
"""Install the regeneration-safe M5 pointer store-to-consumer join witness."""
from pathlib import Path


BASE = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARKER = "PATCH: s3475 state-pointer consumer join"


def main() -> None:
    path = BASE / "funcs_0.c"
    text = path.read_text(encoding="utf-8")
    decl = "extern void rs64_m5_state_pointer_consumer(uint32_t s1);\n"
    if MARKER in text:
        print("s3475 pointer consumer join already installed")
        return
    anchor = "extern void rs64_m5_state_pointer_entry(uint8_t* rdram, recomp_context* ctx);\n"
    if anchor not in text:
        raise SystemExit("state-pointer entry declaration not found")
    text = text.replace(anchor, anchor + decl, 1)
    call = "    rs64_m5_state_pointer_consumer(U32(ctx->r17)); /* " + MARKER + " */\n"
    entry = "    rs64_m5_state_pointer_entry(rdram, ctx); /* PATCH: s3445 state-pointer entry */\n"
    if entry not in text:
        raise SystemExit("state-pointer entry call not found")
    text = text.replace(entry, entry + call, 1)
    path.write_text(text, encoding="utf-8")
    print("s3475 pointer consumer join patched funcs_0.c")


if __name__ == "__main__":
    main()
