# NEXT: owner reports first; otherwise N64Recomp FPU-lowering census
HYPOTHESIS-ID: n64recomp-fpu-lowering-census
Context: s7082 closed N64Recomp's warning set, s7083 closed its silent control-flow lowerings (80 jalr, 1 jr $t9 already
fixed, 177 jump tables match the ROM, dropped table lw never read; tools/s7083_lowering_census.py). Next silent class:
floating point. The pristine front-end output is scratch/s7082/regen (regenerate with tools/regen_front.sh if cleaned);
54685 CHECK_FR lines, only 3 ctc1 sites (rounding-mode writes).
Unit (offline, one bounded change):
1. Enumerate every FPU op shape in the regen (op x fmt x odd/even register x FR mode lowering) and every ctc1/cfc1 site.
2. For each ctc1 site: what rounding mode it sets, which cvt.w/round/trunc/floor/ceil ops execute under it, and whether
   N64Recomp's lowering of cvt.w.s / cvt.w.d honours the FCSR mode (look at cgenerator.cpp / the runtime helpers).
3. Odd-register single/double access under the game's FR mode (uses_mips3_float_mode unset in rogue_squadron.toml), and
   likely-branch bc1tl/bc1fl delay-slot handling.
4. Any live mismatch: differential test of the generated C against tools/s7081_selfbranch_test/mips_ref.py (extend it
   with the needed FPU ops) and a generic fixup.
Discriminator: per shape {lowering matches MIPS semantics, differs but unreachable, differs and live}. Positive control:
a known rounding-sensitive site (e.g. convertMat3x4ToN64Mtx cvt.w.s after mul.s) must be enumerated and classified.
