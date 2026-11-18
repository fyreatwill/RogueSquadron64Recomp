# NEXT (s7582; carried over unchanged from s7581, a maintenance iteration)
HYPOTHESIS-ID: gen-c-pointer-overflow-audit

gen-c-shift-align-audit CLOSED (s7580): build_ubsans (SAN=shift,alignment,signed-integer-overflow). Pre-fix the only executed
UB was class LU: N64Recomp's LUI emit `S32(0X8011 << 16)` (signed shift into the sign bit, C17 6.5.7p4), 22,669 generated sites
+ patch copies, 7,136 executed at boot; plus 2 fixup-patch residuals (s7009 spannarrow negative int64 <<, s4192 wait-spin
u16<<16 in int) and 1 static hand-LUI. tools/fixup_lui_unsigned.py (last pass of fixup_game_funcs_vendored.py) rewrites all
24,703; tools/s7580_lui_identity.py: 51 TUs 0 object diffs (plant control 34 diffs). Alignment: 0 reports (plant fired).
Last sanitizer-reachable UB class in the C: POINTER-OVERFLOW (rdram + (addr - 0xFFFFFFFF80000000) arithmetic in MEM_* macros and
fixup host pointers) and nonnull-attribute.
1. `env SAN=pointer-overflow,nonnull-attribute,signed-integer-overflow B=build_ubsanp zsh tools/build_ubsanc.sh > scratch/s7581/build.log 2>&1`
   Build control: `nm build_ubsanp/**/libRecompiledFuncs.a | grep -c ___ubsan_handle_pointer_overflow` (s7580 nm pattern; objdump -r per obj is too slow).
2. Plant PLANT=5 in tools/s7578_ubsanc_plant.h: `volatile uintptr_t z=0; char* p=(char*)z; p += 16;` style pointer wrap
   (e.g. a char* at (char*)UINTPTR_MAX - 4 plus 16). Add kind 'ptrovf' ("pointer index expression ... overflowed" / "applying
   non-zero offset") to tools/s7579_bounds_report.py.
3. Copy scratch/s7580/run.zsh + run_p.zsh (GAMEDIR=build_ubsanp; controls p5). Wait HIDIdle >= 130 s before launching (the
   harness voids at < 120).
Hypotheses: H-clean (0 reports), H-macro (MEM_* `- 0xFFFFFFFF80000000` wraps a host pointer for every access: a class-wide
report whose fix is in recomp.h via lib/ patch + export.sh, or a fixup-side macro override in include/rsp_dpc_macros.h),
H-patch (a fixup patch computes a wild host pointer). Discriminator: report grouped by file:line, macro-expansion sites vs patch.
Expect H-macro to be likely: rdram + (u64 wraps) is unsigned arithmetic, but the pointer add of a huge u64 may be flagged.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves (build_ubsanc.sh COPIES the save).
