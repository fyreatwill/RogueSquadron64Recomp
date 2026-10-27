# NEXT: find the writer of the -2.0001 (FFFD.FFF7) multiplier vector that feeds the spike's VMADN/VMADH (s6376: FD57 is legit arithmetic on it)
HYPOTHESIS-ID: g3c-owner-visual-b
Hypotheses: H-input (multiplier vector written by a DMA/guest matrix with a bad value), H-retail (retail produces same vector; wedge is retail behaviour), H-clip (multiplier is a legit clip/scale term).
Work unit: extend [spike-vu] ring with the vte full vector (all lanes) and the DMEM address it was loaded from (LDV/LQV tracking of last load into the vte register); at FD57 SDV print source DMEM offset, then identify the DMEM writer (DMA from which RDRAM address / guest matrix). Outcome: bad guest matrix -> trace guest writer; sane for ucode (e.g. clip scale) -> ask owner about CULL_SPIKE default-on.
Recipe: env ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_LOG_SPIKE=1 ROGUESQ_SPIKE_DMEM=1" HOLD_S=120 LEVEL=2 TAG_SUFFIX=s6377 zsh scratch/agent/g1_level_coverage_common.zsh
