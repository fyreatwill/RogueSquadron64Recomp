# NEXT (s5656): fold soak s5655_vstore_b (SOAK-RESULTS.md; log scratch/agent/m6/s5655_vstore_b/run.log)
grep `\[vstore-rail\]`, `\[vstore-val\]`. Positive control: [vstore-val] nonzero>0.
Outcomes: rail PCs named -> identify function (grep RecompiledFuncs for the PC), trace its source operand (H-W2: game fills voice buffer with clamp values, e.g. uninit/overflowed mix); rails==0 & nonzero>0 -> writer is uninstrumented (SWL/SWR/sdc1/non-hooked store macros, or a zmemcpy/memset variant) -> enumerate store forms not covered by rs64_m5_writer_parity and add; nonzero==0 -> readback broken (check g_recomp_rdram_for_wp_raw set).
If no soak result yet, wait on it (do offline work) — do not rebuild.
Hypotheses: H-W1 refuted (s5653); H-W3 refuted; H-W2 game stores vs H-W4 uninstrumented/never-written.
HYPOTHESIS-ID: g2-voice-never-requested
