# NEXT (s7574)
HYPOTHESIS-ID: guard6-fire-census

s7573 decided 5/6 GUARD levers (COPY/PI_DMA/SPAI/s1978 H-dead with FORCE ctl, PIO unreached). Left: musyxKeyOnVoice div-trap.
The ROGUESQ_LOG_M5_KEYON_CENSUS instrument printed NOTHING in s7573 (no kind-1 entry rows, no kind-5 phase-ctl rows at 0x8008FFAC),
though the patches are in N64Recomp/RecompiledFuncs/funcs_24.c.
Hypotheses: H-unreached (the live audio path never calls musyxKeyOnVoice: host key-on replacement or caller gated off -> guard
unreachable, close as dead), H-env (census gate reads a different env / is compiled out of the linked object), H-late (key-on only
after a scripted event not reached in 150 s).
Discriminator, offline first: grep callers of musyxKeyOnVoice in funcs_*.c and check whether their parents are on the live path
(host overrides in src/), and check the 0x8008FFAC phase-control function. If a build is needed: one unconditional first-entry print
in musyxKeyOnVoice via the fixup script, positive control = phase-ctl row that must fire on the title.
Then: item 21 (next 3c rung). OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
Run template: scratch/s7573/run.zsh; scorer tools/s7573_guard_census.py.
