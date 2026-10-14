# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4875 result: the extra synth copy in callback table 0x8011A8A4 is cycle 1's unmatched register. The teardown at 0x8008ECxx (musyxNoopStub) skips its wait/dereg when gate byte 0x800A0F50==0; in the port that is true at the first (boot) call, in retail it is 1. Later cycles are balanced, so 2 copies persist -> synth walks 2x/VI.
Unit: ONE bounded change in a fixup script (not RecompiledFuncs): at reapplyAudioConfig's synth register (registerSiCallback a0==0x8009123C), if the table already holds 0x8009123C, do not register a second copy (or run the one-shot dereg first) - this equals retail's dereg->register net state. Arms in one build via env (ROGUESQ_S4875_DEDUP=0/1) run concurrently with run_s4877_order.sh. Discriminator: synth-entry per VI (s4875_trace recipe): ~1.0 with DEDUP=1 vs ~2.0 with 0; AI-ring delta per synth entry (s4870) moves toward retail +2 / chunk ratio. Guard: no new crash/hang over 3 runs to VI1024.
Do NOT flip gate-write force-zero stubs (hung boot 4x). Reuse: scratch/agent/run_s4877_order.sh, tools/apply_s4877_dereg_order.py, oracle recipe scratch/agent/s4877_oracle_order.sh.
