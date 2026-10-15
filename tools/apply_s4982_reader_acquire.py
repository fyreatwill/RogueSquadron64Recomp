#!/usr/bin/env python3
"""s4982: pair the song-channel count load with the writer's release fence.

ORIGIN: allocateSongChannelArray publishes the legitimate voice-array base
before its count; musyxMixActiveVoices reads that count at 0x80090E1C before
loading the base at 0x80090E78.  This is an ordering fix, not a value guard.
The acquire fence is placed after the count load so it can synchronize with a
release sequence observed by that load.  Idempotent; accepts a RecompiledFuncs
directory as its only argument.
"""
import pathlib
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_s4982_reader_acquire.py <RecompiledFuncs dir>")

path = pathlib.Path(sys.argv[1]) / "funcs_24.c"
text = path.read_text()
marker = "PATCH: s4982 reader acquire"
if marker in text:
    print("funcs_24.c: s4982 reader acquire already present")
    raise SystemExit(0)

anchor = (
    "    // 0x80090E1C: lhu         $a0, -0x6900($a0)\n"
    "    { uint32_t s4575_a = U32(ADD32(ctx->r4, -0X6900)); ctx->r4 = MEM_HU(ctx->r4, -0X6900); rs64_s4307_synth_read(rdram, 0x80090E1Cu, s4575_a, U32(ctx->r4)); } /* PATCH: s4307 synth read join */\n"
 )
if text.count(anchor) != 1:
    raise SystemExit(f"reader count-load anchor count={text.count(anchor)}")

replacement = anchor + (
    "    __atomic_thread_fence(__ATOMIC_ACQUIRE); /* PATCH: s4982 reader acquire */\n"
)
path.write_text(text.replace(anchor, replacement, 1))
print("funcs_24.c: s4982 reader acquire added")
