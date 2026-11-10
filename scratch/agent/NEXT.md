# NEXT: owner reports first; otherwise the residual-opcode census (closes the N64Recomp lowering series)
HYPOTHESIS-ID: n64recomp-residual-op-census
Context: s7082-s7086 closed warnings, control flow, FPU, integer, and memory/immediate/branch lowering
(docs/N64RECOMP-WARNING-CENSUS.md). A mnemonic coverage pass over scratch/s7082/regen against the four census tools leaves
only: and 889, xor 96, negu 79, nor 44, mfc0 12, .word 7, scd 2. Regenerate the front-end output with tools/regen_front.sh
if scratch/s7082/regen is gone. Model on tools/s7086_mem_branch_census.py (operand-checked expectations, KNOWN classes,
positive + mutation controls).
Unit (offline, one bounded change):
1. and/xor/nor/negu: operand-checked shape (nor must be ~(rs | rt) on the full 64 bits; negu = SUB32(0, rt)).
   Add them to a small host test (nor/negu of sign-extended inputs keeps the result sign-extended).
2. mfc0 (12 sites): list the COP0 register per site and what the lowering reads (Count/Status/Cause...). Count is the one
   that matters: osGetCount/osGetTime timing. Check the host value source and that it is 32-bit and sign-extended.
3. .word (7) and scd (2): where they sit (decoded data or a real function), and what C each emits (do_break? nothing?).
4. Then write "series CLOSED" with a coverage table (every mnemonic -> census) in N64RECOMP-WARNING-CENSUS.md.
Discriminator: per site {matches, differs-unreachable, differs-live}. Positive control: osGetCount's mfc0 $9 site enumerated.
After this the series is done: take the next ITERATION.md 3c rung (owner items are all awaiting owner).
