# NEXT: G1d step 19 - why does rs_malloc(0x1000) fail at 21:9 with only ~4.2 MB live?
HYPOTHESIS-ID: g1d-widescreen
Known (s6126): crash writer = rs_malloc(0x1000)->NULL (heaplog-null1000, live=0x3FF568 nblk=630), stored unchecked into load struct 0x48(s0) by processAssetLoadStep, becomes DMA dest 0.
Hypotheses: H-frag (free space exists but no 0x1000 contiguous block / freelist damaged), H-limit (allocator heap end lower than 8 MB, or wide FBs/pools eat region), H-divert (s6086 bigarena divert interacting).
Build: in rs64_s6063_malloc NULL path (src/main/upstream_compat.cpp ~2392) walk the guest freelist (find rs_malloc_s5041_inner's list head/heap bounds in funcs_0.c:3340) and log heap start/end, total free, top-5 free blocks. Run 21:9 once (m6 recipe: env ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_ASPECT=21:9 ROGUESQ_LOG_DMA=1 ROGUESQ_HEAPLOG=1 " HOLD_S=30 LEVEL=1 TAG_SUFFIX=x zsh scratch/agent/g1_level_coverage_common.zsh), and a 4:3 ctl logging the same freelist stats at the same alloc ordinal.
Outcomes: tiny total free => limit (enlarge heap/move pools >=0x80800000); big free but no block => fragmentation (find the fragmenting alloc).
