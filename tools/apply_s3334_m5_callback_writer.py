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


def insert_after_once(path: Path, anchor: str, text: str) -> None:
    source = path.read_text(encoding="utf-8")
    if text in source:
        return
    if source.count(anchor) != 1:
        raise SystemExit(f"{path}: expected one anchor, found {source.count(anchor)}")
    path.write_text(source.replace(anchor, anchor + text, 1), encoding="utf-8")


def main() -> None:
    insert_once(
        GEN / "funcs_26.c",
        "    registerSiCallback(rdram, ctx);",
        "    { extern void rs64_m5_callback_transfer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_transfer_event(0x8009BC50u, 0x80007910u, U32(ctx->r4)); }\n",
    )
    insert_once(
        GEN / "funcs_0.c",
        "    registerSiCallback(rdram, ctx);",
        "    { extern void rs64_m5_callback_transfer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_transfer_event(0x80002FDCu, 0x80007910u, U32(ctx->r4)); }\n",
    )
    insert_once(
        GEN / "funcs_24.c",
        "    // 0x800919EC: jalr        $v0\n"
        "    // 0x800919F0: nop\n\n"
        "    LOOKUP_FUNC(ctx->r2)(rdram, ctx);",
        "    { extern void rs64_m5_callback_transfer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_transfer_event(0x800919ECu, U32(ctx->r2), U32(ctx->r4)); }\n",
    )
    insert_once(
        GEN / "funcs_15.c",
        "    initMusyXVoiceTable(rdram, ctx);",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x80066AA4u, 1u, 0u); }\n",
    )
    insert_after_once(
        GEN / "funcs_26.c",
        "RECOMP_FUNC void initMusyXVoiceTable(uint8_t* rdram, recomp_context* ctx) {\n"
        "    uint64_t hi = 0, lo = 0, result = 0;\n",
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
        GEN / "funcs_0.c",
        "    registerSiCallback(rdram, ctx);",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x80002FDCu, 5u, U32(ctx->r4)); }\n",
    )
    insert_once(
        GEN / "funcs_2.c",
        "    rs64_m5_writer_parity('W', 0x80007928u",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x80007928u, 4u, U32(ctx->r4)); }\n",
    )
    insert_once(
        GEN / "funcs_2.c",
        "    rs64_m5_writer_parity('W', 0x80007968u, U32(ADD32(ctx->r3, 0X0)), 0u); /* PATCH: s2190 m5 scalar */\n"
        "    rs64_probe_submit_gate_store('W', 0x80007968u, U32(ADD32(ctx->r3, 0X0)), U32(0));\n"
        "    MEM_W(0X0, ctx->r3) = 0;\nL_8000796C:",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x80007968u, 6u, U32(0)); }\n",
    )
    insert_once(
        GEN / "funcs_4.c",
        "    rs64_m5_writer_parity('H', 0x80017D08u",
        "    { extern void rs64_m5_callback_writer_event(unsigned, unsigned, unsigned);\n"
        "      rs64_m5_callback_writer_event(0x80017D08u, 7u, U32(ctx->r8)); }\n",
    )
    print("apply_s3334: callback-writer probes installed")


if __name__ == "__main__":
    main()
