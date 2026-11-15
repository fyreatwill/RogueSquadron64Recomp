# NEXT (s7407)
HYPOTHESIS-ID: libm-replacement-contract

s7406 closed class BP (H-none; build_fpat per-PC FPSR attribution). First fold soak s7406_fpat_levels if SOAK-RESULTS has it
(pass: per level CONTROL PASS and VERDICT H-none; a rc 3 names a guest stmt that consumed a denormal or made an invalid op ->
reopen BP for that PC).
Class BQ: host replacements of guest libm.
1. Census (offline, one script tools/s7407_libm_census.py): every callee of the form X_recomp / host function called from
   RecompiledFuncs that replaces a libultra/libm routine (sinf, cosf, sqrtf, guSqrtf, atan2f, ...), where it is defined (grep
   src/, lib/N64ModernRuntime/librecomp, patches), call-site count, and whether the retail body exists in the ROM (ELF symbols
   in syms/ / N64Recomp toml ignored list).
2. For each with a retail body: run the recompiled retail body (or a C transcription of its MIPS) against the host version over
   all 2^32 float inputs (or a dense sweep for 2-arg) offline; report max ulp, mismatches on inf/NaN/denormal/-0.
3. Hypotheses: H-equal (bit-identical), H-ulp-benign (<=2 ulp, no edge mismatch), H-diverge (edge-case or large mismatch that a
   game branch sees -> switch the replacement to the retail body behind a default-on flag, =0 host).
4. Positive control: a deliberately perturbed host copy (result+1 ulp) must show mismatches in the same harness.
