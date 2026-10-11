#!/usr/bin/env python3
"""s4580: causal test of the count-before-base publication window in allocateSongChannelArray
(0x8008F0CC sh count ... jal rs_malloc ... 0x8008F0EC sw base).
With ROGUESQ_S4580_HOLDMIX=1 a mixer entry (musyxMixActiveVoices, via the s4579 hook) on a thread other than the
allocator waits (<=2 s, 100 us polls) while an allocateSongChannelArray is in flight, i.e. mimics 'no preemption
inside the window'. Needs ROGUESQ_LOG_S4579=1 (it sets the in-flight flag). Diagnostic only; default off. Idempotent."""
from pathlib import Path
p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
s = p.read_text()
if "rs64_s4580_hold" not in s:
    old = "static void rs64_s4579_mix(uint8_t* rdram, recomp_context* ctx) {\n    if (!rs64_s4579_on()) return;\n"
    assert s.count(old) == 1
    new = r'''#include <unistd.h>
static int rs64_s4580_hold = -1; static unsigned rs64_s4580_nh = 0;
static void rs64_s4579_mix(uint8_t* rdram, recomp_context* ctx) {
    if (!rs64_s4579_on()) return;
    if (rs64_s4580_hold < 0) { const char* e = getenv("ROGUESQ_S4580_HOLDMIX"); rs64_s4580_hold = (e && e[0] && e[0] != '0') ? 1 : 0; }
    if (rs64_s4580_hold && rs64_s4579_inflight && rs64_s4579_atid != (unsigned long)(uintptr_t)pthread_self()) { /* PATCH: s4580 holdmix */
        unsigned spins = 0; while (rs64_s4579_inflight && spins < 20000u) { usleep(100); spins++; }
        if (rs64_s4580_nh++ < 20) { fprintf(stderr, "[s4580-hold] n=%u spins=%u still_inflight=%d\n", rs64_s4580_nh, spins, (int)rs64_s4579_inflight); fflush(stderr); }
    }
'''
    s = s.replace(old, new)
    p.write_text(s)
print("applied")
