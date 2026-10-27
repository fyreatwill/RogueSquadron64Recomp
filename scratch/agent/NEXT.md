# NEXT: G3c(b) spike pinned-Y: find the RSP store that writes DMEM 0x43A/0x462
HYPOTHESIS-ID: g3c-owner-visual-b
s6371: H-loaded refuted (post-DMA v43A only 0000/3333, never FD57; pinned Y=-170.25px = s15.2 -681 = 0xFD57). H-ucode-write selected.
Work unit: one build with an RSP store watch (PC + value) on DMEM 0x43A/0x462 for the F5 ucode, gated by ROGUESQ_SPIKE_DMEM; log stores whose value==0xFD57 (and a positive control: watch a known-written address). Queue a lvl2 300 s soak with ROGUESQ_LOG_SPIKE=1 ROGUESQ_SPIKE_DMEM=1. Writer PC -> name the ucode stage; then decide if value legit (clip/VTX output) and whether to fix the emulation or ask owner about ROGUESQ_CULL_SPIKE default-on.
