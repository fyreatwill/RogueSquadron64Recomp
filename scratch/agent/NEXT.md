# NEXT: owner reports first; otherwise N64Recomp warning-class census (engineering rung)
HYPOTHESIS-ID: n64recomp-warning-census
Context: s7081 fixed the self-branch class (tools/fixup_selfbranch.py + tools/s7081_selfbranch_test). Old regen logs
(../N64Recomp/fixup_*.log, scratch/*/regen*.log) carry other `[Warn]` lines: "branching outside" for audioCompandS16 (already
handled by s5668 fixup_label_realign), __OSGlobalIntMask, static_3_800A2FE4, lvj_checkComplexObjectives, static_3_800A50AC,
fake_func_*; plus any jump-table / unhandled-instruction warnings.
Unit (one bounded change):
1. Run one fresh N64Recomp pass into a scratch output dir (docs/REGEN-VERIFY.md recipe, do NOT touch the live tree), capture
   stderr, and group every [Warn]/[Error] by class and function.
2. For each class decide: H-handled (an existing fixup repairs it: name it), H-data (decoded data, no caller), H-live (real
   code, wrong output). For "branching outside" rows, tools/scan_selfbranch.py on the scratch tree says whether a goto
   leaves its function; lvj_checkComplexObjectives and __OSGlobalIntMask are the first suspects (real code).
3. Any H-live row gets the s7081 treatment: generic fixup + differential test with tools/s7081_selfbranch_test/mips_ref.py
   (extend its opcode set if needed; it raises on unknown opcodes, so coverage is explicit).
Discriminator: warning class x {handled, data, live}. Closes when every class has a named owner or a fix.
Controls: fixup_preempt_point.py says 6, fixup_selfbranch.py says 16, L6 boot to flight clean (sed s7081->s7082 scratch/s7081/run.zsh).
