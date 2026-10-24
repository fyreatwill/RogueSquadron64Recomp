# NEXT: G1d step 22 - give the widened fb carve room: where does RT64 cap rdram at 8 MB, and can it be 16 MB?
HYPOTHESIS-ID: g1d-widescreen
Known (s6129): 21:9 NULL = fb carve by partitionFramebufferMemory eats 1.9 MB of the 2.6 MB free (see CURRENT-TRUTH s6129). 16:9 (796) has no heap NULL but stalls in lv1_initializeObjectTracking under initMission.
Hypotheses: H-cap (RT64/librecomp rdram sized 8 MB, s6114 crash for osMemSize>8; lifting to 16 MB lets 21:9 carve fit), H-shrink (patch partition to size depth/aux fbs at 512 wide), H-stall16 (16:9 stall is the same heap squeeze on another allocator or an independent loop bound).
Discriminator: grep RT64/librecomp for the 8 MB cap (rdram size passed to RT64 / mmap 0x800000); raise to 16 MB under ROGUESQ_OSMEM_MB=12 and rerun 21:9 (recipe: ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_ASPECT=21:9 ROGUESQ_OSMEM_MB=12 ROGUESQ_HEAPLOG=1 " HOLD_S=30 LEVEL=1 zsh scratch/agent/g1_level_coverage_common.zsh). Positive control: [s6129] prints 63E4 near 0x80B1xxxx and no NULL. Separately dump the heap walk at the 16:9 stall.
Remember: lib/ edits need ./submodule-patches/export.sh + commit.
