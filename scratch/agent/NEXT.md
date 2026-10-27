# NEXT: trace the upstream operand (v4:v5 lane1 = E6E1.FBF6 and the 13C0/0004/0005 terms) feeding the -2.0001 multiplier at the FD57 SDV (s6377: multiplier is computed, not loaded)
HYPOTHESIS-ID: g3c-owner-visual-b
Hypotheses: H-input (bad upstream operand from guest matrix/vertex data), H-retail (value legit for near-plane vertices in retail), H-clip (legit clip scale term).
Work unit: raise the VU ring depth 24 -> 128 in main.cpp (g_vu_ring), dump at FD57 SDV; follow E6E1.FBF6 back to its LDV/LQV/LSV DMEM source and, if a guest matrix, find the DMA writer. Outcome: bad guest data -> trace guest writer; sane arithmetic on legit near-plane inputs -> ask owner about CULL_SPIKE default-on.
Recipe: env ROGUESQ_G1B=1 XENV_EXTRA="ROGUESQ_LOG_SPIKE=1 ROGUESQ_SPIKE_DMEM=1" HOLD_S=120 LEVEL=2 TAG_SUFFIX=s6378 zsh scratch/agent/g1_level_coverage_common.zsh
