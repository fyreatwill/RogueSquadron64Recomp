# NEXT: px3 + MALLOC_SPILL faults NULL+0x14 in hudDisplayUpdateWorker+3332 (s6569)
HYPOTHESIS-ID: g1c-dd-phase2
Fact: px3 pool alloc now succeeds via ROGUESQ_MALLOC_SPILL=1. Next crash: hudDisplayUpdateWorker+3332, si_addr=0x380000014.
Hypotheses: H-hud-malloc (a hud-side rs_malloc still NULL: arena full? no, 'arena full' count 0; or alloc failure path returning 0 before spill because inner not called); H-dd-table (hud reads per-object table indexed by a dd-scaled count -> NULL slot); H-spill-side (spill at boot altered a retail-NULL flag; px1 clean argues against).
Discriminator: map +3332 to the generated hudDisplayUpdateWorker source line (funcs_*.c), name the NULL pointer's source global, log it once under env; then px3 run with ROGUESQ_HEAPLOG=1 too.
Repro: zsh scratch/agent/s6553_run.sh 6 3 "ROGUESQ_RAMTOP_MB=16 ROGUESQ_DLPOOLX=1 ROGUESQ_DLPOOLX_MB=4 ROGUESQ_DLPOOLX_AT=3000 ROGUESQ_MALLOC_SPILL=1" X
