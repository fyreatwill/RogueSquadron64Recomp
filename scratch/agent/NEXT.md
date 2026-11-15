# NEXT (s7417)
HYPOTHESIS-ID: control-flow-emission-semantics-closed

STEP 0 FIRST: docs/CURRENT-TRUTH.md is 60.3 KB (>60000), so s7417 is a MAINTENANCE iteration. Compact it toward ~35 KB:
migrate the closed audit classes BB-BZ (Next steps items ~1-25) to PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417
maintenance)" verbatim, keep a 1-2 line summary each, renumber into one sequence. No experiments.

After maintenance (s7418+), class CA = opcode-coverage residue (HYPOTHESIS-ID: opcode-coverage-residue):
1. Census every distinct disasm mnemonic in ../N64Recomp/RecompiledFuncs (full-line + mid-line `// 0x...: op` comments).
2. Subtract the ops scored by tools/s7411_unaligned_contract.py, s7412_int_emission.py, s7413_aligned_ldst.py,
   s7414_fp_compare.py, s7415_fp_arith.py, s7416_ctrl_flow.py, s7408_cvt_contract.py (read each tool's op list).
3. For each remaining op (expected: mfc0/mtc0, cache, sync, teq/tne/trap family, eret, .word, sc/ll, cfc1 beyond RM, ...):
   site count, live vs data_gap, emitted form, and whether it matches VR4300 semantics or is a deliberate no-op.
   Compile any arithmetic-bearing residue against a model with a mutant control, like s7412.
Hypotheses: H-equal (all residue is no-op-safe or exact) / H-gap (a live op is emitted wrong or as do_break on a live path).
Known LATENT from s7416: jr/jalr emit the slot BEFORE reading rS (only in dead data_gap_80024A0C). Re-run
tools/s7416_ctrl_flow.py (rc 0 expected) after any ROM/asm/generator change.
