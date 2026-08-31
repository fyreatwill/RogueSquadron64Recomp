#!/usr/bin/env python3
"""Replay the s3334 callback-writer attribution probes after regeneration."""

from pathlib import Path


GEN = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
CALL = "{ extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);"


def insert_once(path: Path, anchor: str, text: str) -> None:
    source = path.read_text(encoding="utf-8")
    if text in source:
        return
    if source.count(anchor) != 1:
        raise SystemExit(f"{path}: expected one anchor, found {source.count(anchor)}")
    path.write_text(source.replace(anchor, text + anchor, 1), encoding="utf-8")


def main() -> None:
    insert_once(
        GEN / "funcs_15.c",
        "    initMusyXVoiceTable(rdram, ctx);",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x80066AA4u, 1u, 0u); }\n",
    )
    insert_once(
        GEN / "funcs_26.c",
        "    // 0x8009BBA0: addiu         $sp, $sp, -0x28\n",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x8009BBA0u, 2u, 0u); }\n",
    )
    insert_once(
        GEN / "funcs_26.c",
        "    registerSiCallback(rdram, ctx);",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x8009BC50u, 3u, U32(ctx->r4)); }\n",
    )
    insert_once(
        GEN / "funcs_2.c",
        "    rs64_m5_writer_parity('W', 0x80007928u",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x80007928u, 4u, U32(ctx->r4)); }\n",
    )
    print("apply_s3334: callback-writer probes installed")


if __name__ == "__main__":
    main()
