# NEXT: who zeroes the hud service queue 0x80955130 (svc 0x80954F60+0x1D0) at px3+spill (s6571)
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6571, 3/3): at the fault the queue struct (validCount, first, msgCount, msg ptr) is entirely 0; earlier 32 NOBLOCK sends to it landed; signalServiceWorkerStop never fired.
Hypotheses: H-freed-zeroed (record freed by guest heap then memset/reused; check rs64 free census s5041 for 0x80954F60 and the spill/pool allocators), H-overlap (a px3/DLPOOLX/spill carve overlaps 0x80954F60..0x80955150 and is cleared at pool init), H-host-clear (host code memset of a range, e.g. pool init in upstream_compat.cpp).
Discriminator, ONE build: a store watch on guest 0x80955130..0x80955148 (hook in the generated MEM_W stores via RS64_S5798_ST or host memset sites) logging PC/ra of the first store after msgCount becomes 0, plus log of any free()/malloc of the block 0x80954F60 and the DLPOOLX/spill ranges at init. Positive control: the watch must fire on the legit osCreateMesgQueue init of this queue.
Repro: zsh scratch/agent/s6553_run.sh 6 3 "ROGUESQ_RAMTOP_MB=16 ROGUESQ_DLPOOLX=1 ROGUESQ_DLPOOLX_MB=4 ROGUESQ_DLPOOLX_AT=3000 ROGUESQ_MALLOC_SPILL=1 ROGUESQ_SVCNULL=1" N
