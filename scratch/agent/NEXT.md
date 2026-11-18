# NEXT (s7576)
HYPOTHESIS-ID: gen-c-ub-audit

s7575 closed the do_break class and found that RecompiledFuncs is built at -O2, so C UB in the generated code is
something clang can exploit. The 32-bit div emission ran before its zero check and -O2 deleted 36 do_break checks;
tools/apply_s7575_div_total.py fixed it (BLIND=0). Next, the same audit for the other UB-capable emissions.
1. Enumerate: grep lib/N64ModernRuntime/N64Recomp/include/recomp.h for macros that are plain C casts or ops with UB:
   TRUNC_W_S/TRUNC_W_D/TRUNC_L_*/CVT_W_*/ROUND/FLOOR/CEIL (`(int32_t)(float)` is UB for NaN or out-of-range values),
   shifts (sllv/srlv/dsllv by amount >= width), and anything else emitted bare in cgenerator.cpp. Count the emission
   sites per macro in ../N64Recomp/RecompiledFuncs.
2. Static exploit test, as s7575 did: compile to -O2 IR (tools/s7575_ir_flags.txt) and look for `fptosi`/`fptoui`
   whose result feeds a compare or branch that the optimiser folded. Control: a planted C snippet where clang provably
   folds `if ((int)f > INT_MAX)` style code.
3. If a class is exploitable or MIPS-inexact, write a total MIPS-exact macro behind a fixup apply script (R4300: an
   out-of-range cvt raises an Unimplemented exception, so retail would fault). Then do one runtime arm with an ungated
   out-of-range counter (L1 / L4 dd2 / L12, 150 s, scratch/s7575/run.zsh template) and a forced control.
Hypotheses: H-safe (arm64 fcvtzs saturation, no folding exploited), H-folded (IR shows folded range checks),
H-hit (the runtime counter shows out-of-range conversions at defaults: name the writer of the bad float).
After any regen: tools/apply_s7575_div_total.py is chained, so verify with
`mkdir -p D; ls ../N64Recomp/RecompiledFuncs/funcs_*.c | env D=D xargs -P6 -n1 sh tools/s7575_ir_calls.sh;
python3 tools/s7575_break_census.py --controls --ir D` (wants BLIND=0, rc 0).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
