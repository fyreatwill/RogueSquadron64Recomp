# NEXT: owner reports first; otherwise N64Recomp integer mult/div/64-bit lowering census
HYPOTHESIS-ID: n64recomp-int-lowering-census
Context: s7082 closed the warning set, s7083 closed the control-flow lowerings and s7084 closed the FPU lowerings
(tools/s7084_fpu_census.py, tools/s7084_fpu_test/run_test.py, docs/N64RECOMP-WARNING-CENSUS.md). 0 live miscompiles
so far. The pristine front-end output is scratch/s7082/regen (regenerate with tools/regen_front.sh if cleaned).
Unit (offline, one bounded change):
1. Enumerate every integer op shape whose host semantics can differ from the R4300: mult/multu/div/divu (hi/lo,
   div by zero gives a defined MIPS result while C is UB, INT_MIN/-1), dmult/dmultu/ddiv/ddivu, dsll/dsrl/dsra(32)/dsllv,
   sra/srav on 64-bit sign extension, lwl/lwr/swl/swr/ldl/ldr/sdl/sdr, sltiu sign-extended immediates, addi overflow traps.
2. Shape-check each op's lowering, as tools/s7084_fpu_census.py does (first lowered statement vs the expected macro),
   with a mutation negative control.
3. Host semantic test of the recomp.h integer macros at the live -O2 flags against tools/s7081_selfbranch_test/mips_ref.py
   (extend it): div by 0, INT_MIN/-1, unaligned lwl/lwr pairs at all 4 offsets, 32-bit result sign extension.
4. Disassemble the built objects for division ops: any sdiv/udiv whose divisor is not checked becomes a C-UB question
   (arm64 gives 0; MIPS leaves hi/lo with a defined value).
Discriminator: per shape {matches, differs but unreachable, differs and live}. Positive control: a known divide site
(e.g. the menu JPEG decoder or the audio resampler) must be enumerated and classified.
