#!/usr/bin/env python3
"""Move swapBufferWithViMode jal delay-slot $a0 before osViSetMode.

ORIGIN: jal at 0x8001BB54. Hardware executes `addiu $a0, $a0, -0x44` in the
delay slot and passes copied-mode dest 0x80128C90. N64Recomp emits the call
first and skips the delay slot via goto-after, so osViSetMode_recomp sees
0x80128CD4 (width 2). That $a0 is not a legitimate OSViMode pointer.

This script patches an already-sentinel'd RecompiledFuncs/funcs_5.c without
re-running the full fixup. The same transform is a unique PATCH in
../N64Recomp/fixup_game_funcs.py for the next clear+regen+fixup.
"""
from pathlib import Path

GEN = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_5.c")
MARK = "PATCH: s3277 jal delay-slot $a0 before osViSetMode"
OLD_SKIP = (
    "    osViSetMode_recomp(rdram, ctx);\n"
    "        goto after_0;\n"
    "    // 0x8001BB58: addiu       $a0, $a0, -0x44\n"
    "    ctx->r4 = ADD32(ctx->r4, -0X44);\n"
    "    after_0:\n"
)
NEW_SKIP = (
    "    ctx->r4 = ADD32(ctx->r4, -0X44); /* PATCH: s3277 jal delay-slot $a0 before osViSetMode */\n"
    "    osViSetMode_recomp(rdram, ctx);\n"
    "        goto after_0;\n"
    "    // 0x8001BB58: addiu       $a0, $a0, -0x44\n"
    "    // PATCH: s3277 — hardware executes this delay slot before the jal; post-call copy is a no-op\n"
    "    // ctx->r4 = ADD32(ctx->r4, -0X44);\n"
    "    after_0:\n"
)
PROBE_CALL = (
    "        ++vi_call_n;\n"
    "    }\n"
    "    osViSetMode_recomp(rdram, ctx);\n"
)
PROBE_PRE = (
    "        ++vi_call_n;\n"
    "    }\n"
    "    ctx->r4 = ADD32(ctx->r4, -0X44); /* PATCH: s3277 jal delay-slot $a0 before osViSetMode */\n"
    "    osViSetMode_recomp(rdram, ctx);\n"
)


def apply_text(text):
    if MARK in text:
        return text, "already present"
    skip_n = text.count(OLD_SKIP)
    if skip_n == 1:
        return text.replace(OLD_SKIP, NEW_SKIP, 1), "moved delay-slot $a0 before osViSetMode"
    if skip_n != 0:
        raise SystemExit(f"s3277 skip-goto delay-slot anchor count={skip_n}")
    if "PATCH: s803 direct VI caller probe site=0x8001BB54" not in text:
        raise SystemExit("s3277: delay-slot and s803 probe both missing")
    start = text.find("PATCH: s803 direct VI caller probe site=0x8001BB54")
    window = text[start:start + 2500]
    if window.count(PROBE_CALL) != 1:
        raise SystemExit("s3277: s803 swapBuffer probe call-site unmatched")
    return text[:start] + window.replace(PROBE_CALL, PROBE_PRE, 1) + text[start + 2500:], (
        "reinserted delay-slot $a0 before osViSetMode"
    )


def main():
    text = GEN.read_text()
    text, msg = apply_text(text)
    if msg == "already present":
        print(f"{GEN}: s3277 delay-slot $a0 already present")
        return
    GEN.write_text(text)
    print(f"{GEN}: s3277 {msg}")


if __name__ == "__main__":
    main()
