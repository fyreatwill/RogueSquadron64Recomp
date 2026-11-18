# NEXT (s7580)
HYPOTHESIS-ID: gen-c-shift-align-audit

gen-c-bounds-audit is CLOSED (s7579): build_ubsanb (SAN=array-bounds,signed-integer-overflow) carries 879 bounds checks in
RecompiledFuncs; L1 dd1/dd4, L4 dd2, L12 dd4 150 s -> 0 reports, plant ROGUESQ_S7578_PLANT=2 fired; scorer
tools/s7579_bounds_report.py rc 0. Next sanitizer-reachable UB classes left in the C: SHIFT (exponent >= width or negative in the
fixup C; generated shifts are masked) and ALIGNMENT (misaligned host loads/stores through casted rdram/host pointers in fixup C).
1. `env SAN=shift,alignment,signed-integer-overflow B=build_ubsans zsh tools/build_ubsanc.sh > scratch/s7580/build.log 2>&1`
   Build control: `objdump -r` on RecompiledFuncs objects shows ___ubsan_handle_shift_out_of_bounds and
   ___ubsan_handle_type_mismatch_v1 relocations (count them, s7579 pattern).
2. Add plants to tools/s7578_ubsanc_plant.h: PLANT=3 shift (volatile int s=40; 1u<<s), PLANT=4 misaligned u32 read from a
   char buffer at +1. Extend tools/s7579_bounds_report.py kinds (shift / misaligned) and its plant check (--plant-kind).
3. Arms (copy scratch/s7579/run.zsh + run_p2.zsh, GAMEDIR=build_ubsans): p3, p4 (HOLD 60), l1 dd4, l4 dd2 (FORCE_SAVE_MISSION=4),
   l12 dd4 (=12), HOLD 150.
Hypotheses: H-clean (0 reports outside plants), H-diag (a diagnostic shift/cast in an apply_*.py: fix bound there),
H-behav (a behaviour-changing patch shifts out of range / misaligned: root-cause + fix in its fixup script).
Discriminator: tools/s7579_bounds_report.py grouped by file:line; both plants must report.
Caveat: alignment UBSan may report RT64/librecomp C++? No - C flags only (C++ is built as in build/).
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves (build_ubsanc.sh COPIES the save).
