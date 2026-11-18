# NEXT (s7578)
HYPOTHESIS-ID: gen-c-ub-audit

s7575 (div), s7576 (float->int trunc) and s7577 (RSP ucode, all classes) are closed. One -O2 UB lever was never measured on the
52 RecompiledFuncs TUs: null-check deletion (-fdelete-null-pointer-checks is ON there; -fno-strict-aliasing already is set).
Also the W arm (-fwrapv) has not been run on the game C as a whole (s7576 only reasoned that gpr is uint64_t).
1. `env TU_RE=RecompiledFuncs/ python3 tools/s7577_ucode_ub_census.py scratch/s7578` (52 TUs x 4 arms; ~a few minutes at -j12).
   Controls must read wrapv/u16mul/null FIRED, alias PRE-OFF, in every TU.
2. Any N-arm function diff = clang deleted a host null check after a dereference: read it (hand) and name the source line.
   Any W-arm diff: run `python3 tools/s7577_ubsan_sites.py <tu>` on that TU and classify the sites; generated game C should have
   ~0 signed ops (gpr uint64_t), so expect glue/fixup counters only. Extend CLASSES only with a written value-range proof.
3. If a real UB-grounded fold exists: fix it in a fixup script (tools/apply_*.py chained in fixup_game_funcs_vendored.py), one
   runtime arm (scratch/s7576/run.zsh template, L1/L4 dd2/L12, 150 s) with a control.
Hypotheses: H-safe (N arm 0 diffs, W sites all bounded), H-null (a null check deleted after deref), H-wrap (a W-site unbounded).
If H-safe: close gen-c-ub-audit and take ITERATION.md item 22 (next 3c rung / new idiom-class audit).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
