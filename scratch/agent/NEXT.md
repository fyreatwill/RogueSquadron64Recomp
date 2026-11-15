# NEXT (s7416)
HYPOTHESIS-ID: control-flow-emission-semantics

s7415 closed class BY (tools/s7415_fp_arith.py rc 0). If scratch/agent/SOAK-RESULTS.md has a s7415_ioc_levels line, fold it
(pass = alive, 0 crash, CONTROL PASS + VERDICT H-none x3 on L5/L10/L15). NOTE: CURRENT-TRUTH is 59.9 KB; if Step 0 prints
>60000 this iteration is MAINTENANCE instead.
Class BZ: control-flow emission. Offline, the s7412/s7414 way (harvest skeleton in tools/s7414_fp_compare.py /
tools/s7415_fp_arith.py: fnpat incl. `static void` inner bodies, mid-line disasm comments, pass-through prefixes).
1. Census every conditional branch (beq/bne/blez/bgtz/bltz/bgez + likely variants, bltzal/bgezal, b/bal) and jal/jalr/jr/j.
2. Per site check vs disasm: condition operands and width (MIPS compares full 64-bit GPRs: the emitted test must read the
   64-bit gpr, signed for blez/bgtz/bltz/bgez), target label, delay-slot placement: non-likely -> delay slot runs on both
   paths; likely -> delay slot only on the taken path. HAZARD to grep for: a delay slot that writes a source register of
   its own branch (MIPS evaluates the condition BEFORE the slot) -- the emission must evaluate first (look for a temp or
   ordering). Also jalr rd,rs where the slot writes rs, and jr through a register the slot overwrites.
3. Compile distinct condition forms verbatim (game flags) and drive with 64-bit edge values (0, +-1, INT32 edges with
   non-canonical upper words, INT64 min/max) vs a MIPS model.
4. Positive control: mutants (32-bit compare, signed/unsigned swap, slot-after-condition swap, likely slot on both paths)
   must flag. Hypotheses: H-equal / H-slotorder / H-width / H-likely.
