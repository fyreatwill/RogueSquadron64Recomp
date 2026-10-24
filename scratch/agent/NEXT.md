# NEXT: why does tickTextureMaterialExpiry never age the 2048-bucket table? (G1c phase 2)
HYPOTHESIS-ID: g1c-phase2-drawdist
Facts (s6094): tick runs, table valid (nb=2048 base 0x8018B490, ent=1715), all ages 0 across 40 consecutive ticks, resetMaterialExpiryById never called, only 2 nodes >=8MB.
Hypotheses: H-body the loop body's age store never executes (guard branch / control-flow bug in recompiled code, e.g. goto L_80022128 for every node); H-inlinezero an inline writer zeroes +8 between ticks (find via store-watch on a sampled node's age halfword, PC attribution); H-reader tick sees entries the reader misreads (unlikely: same macros).
Discriminator, one build: inside tick (funcs_6.c, via apply_s6088_bucketlog.py) count nodes visited, age-store executions (path at 0x800220A4/AC), expiry path (0x800220B0) hits, and guard skips; plus RS64 store hook logging PC of any write to age of node #1 of bucket 0. Run s6094_tick_dd3.sh (150s hold, in scratch/agent/soak_queue/).
Outcomes: visited>0 & stores>0 -> H-inlinezero (name writer PC); visited==0 -> H-body; stores==0 with visited>0 -> age>=0x708 or branch bug.
