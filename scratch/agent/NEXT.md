# NEXT: fold s6372 [spike-st] soak: which RSP store leaves 0xFD57 in DMEM 0x43A/0x462
HYPOTHESIS-ID: g3c-owner-visual-b
Read scratch/agent/SOAK-RESULTS.md tail + soak_results/s6372_spike_store_*.log. Check positive control first (ctl>0 in [spike-st] rows; if no rows at all with n43A=0, the slots are never stored -> revisit: written by DMA after all or different DMEM copy).
Resolve the FD57-row `ra=` with `atos -o build/RogueSquadron64Recomp -arch arm64 <ra - slide>` or lldb `image lookup -a`; map to the ucode source line/op (sh/sw/SQV/...), name the stage, and decide whether the value is legit (VTX output) -> emulation vs ucode-state bug. Then fix or ask owner about ROGUESQ_CULL_SPIKE default-on.
