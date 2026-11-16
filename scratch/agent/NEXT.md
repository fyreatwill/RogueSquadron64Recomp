# NEXT (s7472)
HYPOTHESIS-ID: guest-heap-integrity

Class EA (host ASan per-level) CLOSED s7471: L0-L18 flown, 0 NEW. Its blind spot is guest code: RecompiledFuncs access guest
memory through rdram, so a guest overrun into a neighbouring rs_malloc block is invisible to ASan. Class EB closes that gap.

Unit (class EB): guest-heap chain integrity per level, ONE instrument, ONE build.
1. Read the existing heap tooling first (no new discovery cost): tools/apply_s6063_heaplog.py, tools/apply_s7325_heaprebuild.py,
   ROGUESQ_S7317_ALLOCMAP=1 (PORTING-STATE s7317), tools/audit_heap_addr_tests.py, PROJECT-OVERVIEW heapWalker section. Get the
   rs_malloc arena base/end, block-header layout (size/flags/next) and the dd>1 spill arena (s6858, 0x8082xxxx).
2. Host-side walker (src/, env ROGUESQ_S7472_HEAPCHK=1, default off): every N VIs (and at each initMission) walk the guest block
   chain from host C++ reading rdram; check size alignment, next within arena, next == this+size, flags sane, free-list links
   inside the arena; log the first bad header per phase `[s7472] heap-bad arena= blk= field= val= prev_ok=` + the last guest PC.
   Planted control ROGUESQ_S7472_HEAPCHK_PLANT=1: after mission load, corrupt one free block's size word; the walker MUST report it.
3. Recipe via tools/s7470_gen_asan_lv.zsh pattern on the normal build (plant on arm 1): L4, L7, L12 dd4 16:9 + L15 dd8 21:9,
   HOLD=220. Queue as soak if the host is busy.
Hypotheses: H-heap-clean (0 bad headers outside the plant, all arms in flight) / H-heap-hit (a bad header: name the writer with a
write watch on that header word, fix root cause, ORIGIN line) / H-walker-wrong (bad headers on every arm at load = layout misread;
fix the walker against the s7317 alloc map before any verdict). Plant not firing = instrument blind, no verdict.
