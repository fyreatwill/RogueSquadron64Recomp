# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4736: runaway tasks have 1 RSP entry; their L_11B0 refill sources cycle 740AD8 -> ... -> 744078 (link word 0) -> 740AD8. Question: who puts 740AD8 into the refill source (DMEM state+0x30 = 0x30(r18)) after the 744078 chunk?

Hypotheses:
- H-state30-reset: some store to 0x30(r18) (or the saved frame slot) writes the task's initial data pointer (e.g. the end/b8 or zero-link path re-seeds it from OSTask data_ptr at DMEM).
- H-link-from-other-field: the refill source comes from another DMEM field (e.g. slot-0 frame 0x650/0x654) that still holds 740AD8.
- H-cyclic-data: chunk words themselves chain back (weighed against: 744078 link word is 0).

Discriminator (one build, one run): in fixup 18 add a probe at every `RSP_MEM_W_STORE(0X30, r18, ...)` in factor5_ucode_recompiled.c (grep enumerates) logging (site label, value, task, fetch count) via rs64_dlw_root kind 6, plus log r2 provenance at L_11B0 (value of 0x30(r18) vs w0 of previous chunk). Outcome: store of 740AD8 at site X on the wrap => H-state30-reset (inspect X's guard); no store but value present => H-link-from-other-field; positive control: normal task 41 must show its own stores with monotone sources.
Run: zsh scratch/agent/s4735_run.sh (rebuild with DEVELOPER_DIR=... cmake --build build -j8; apply fixup to build/factor5_ucode/factor5_ucode_recompiled.c first).
