#!/usr/bin/env python3
"""s4581: export the s4579 alloc-in-flight flag so ultramodern's resume_thread_tagged can log every thread
handoff that happens while allocateSongChannelArray is inside rs_malloc. Diagnostic only. Idempotent."""
from pathlib import Path
p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c"); s = p.read_text()
if "rs64_s4581_inflight" not in s:
    k = "void rs64_s4579_mix_ext(uint8_t* rdram, recomp_context* ctx) { rs64_s4579_mix(rdram, ctx); }\n"
    assert s.count(k) == 1
    s = s.replace(k, k + "int rs64_s4581_inflight(void) { return rs64_s4579_inflight; } /* PATCH: s4581 */\n")
    p.write_text(s)
print("applied")
