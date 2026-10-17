# UNBLOCK (s5356): route 3 (re-scope)
Block: BLOCKED.md asked a human to pick A (install MIPS toolchain) / B (new target) / C (stop).
Route 1: A only gates fresh PatchesLib source qualification, already marked NOT blocking in
CURRENT-TRUTH; the existing-artifact qualification stands. Option C is not warranted.
Route 2: searched the four allowed working dirs for a MIPS gcc/ld: only docs/mips_to_c found
(a doc, not a toolchain). Searching /opt/homebrew was blocked by the sandbox, and installing
software is a human decision, so not obtained.
Route 3: B was available without a human: NEXT.md re-scoped to an offline audit of the remaining
M3 idiom classes (jr/jalr, unaligned pairs, branch-likely). Toolchain stays an open dependency.
Refuting experiment: `brew install mips64-elf-gcc` would make fresh PatchesLib qualification possible.
