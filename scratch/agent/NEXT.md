# NEXT (s7583)
HYPOTHESIS-ID: gen-c-residual-ub-audit

gen-c-pointer-overflow-audit CLOSED s7582 (H-clean, plant 5 fired, 0 reports L1/L4/L12). Classes done over the game C:
signed overflow/null (s7578), array-bounds (s7579), shift/alignment (s7580, LUI fix), pointer-overflow (s7582). Remaining
UBSan-checkable UB, all in ONE build (iron rule 13/14):
  SAN=integer-divide-by-zero,float-cast-overflow,bool,builtin,unreachable,return,vla-bound,nonnull-attribute
1. Plants in tools/s7578_ubsanc_plant.h (allow '6'-'9', or switch to a two-char PLANT value): 6 = volatile int d=0; 7/d;
   7 = volatile float f=1e20f; (int)f; 8 = nonnull: a static __attribute__((nonnull)) fn called with a volatile NULL;
   9 = builtin: __builtin_clz(volatile 0). Add scorer kinds ('division by zero', 'is outside the range of representable',
   'null pointer passed as argument', 'passing zero to clz'/'builtin') to tools/s7579_bounds_report.py.
   Check first (boring thing): does N64Recomp's DIV/DIVU emit guard divisor 0? grep RecompiledFuncs for '/ ' on ctx->r
   and the do_div helpers; a guarded emit means a report can only come from a fixup patch.
2. `env SAN=<list above> B=build_ubsanr zsh tools/build_ubsanc.sh > scratch/s7583/build.log 2>&1`;
   nm build_ubsanr/libRecompiledFuncs.a | grep -c ___ubsan_handle_divrem_overflow (and float_cast_overflow).
3. Copy scratch/s7582/run.zsh + run_p.zsh (GAMEDIR=build_ubsanr, one 60 s control arm per plant, or one arm if the plant
   constructor fires all kinds at once). Wait HIDIdle >= 130 s.
Hypotheses: H-clean; H-div (a guest DIV by 0 reaches host '/': hardware defines the result, C does not -> fix the emit in a
fixup pass like fixup_lui_unsigned.py); H-fcast (a cvt/trunc of out-of-range float in a patch, despite s7576 static census);
H-patch (nonnull/builtin in a hand patch). Discriminator: reports by file:line and kind.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves (build_ubsanc.sh COPIES the save).
