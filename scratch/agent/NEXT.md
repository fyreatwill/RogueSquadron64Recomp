# Next work unit: hand-port one bounded heap-guard entry point
HYPOTHESIS-ID: m3-assembly-patch-pipeline

Competing hypotheses:

1. A faithful hand-written MIPS assembly version of one existing
   `patches/heap_guards.c` entry point can be linked and consumed by N64Recomp;
   the assembly-only route is sufficient for a real patch.
2. The entry point depends on C-generated ABI/relocation behavior that the
   assembly route cannot reproduce with the current linker scripts.
3. The function is too large or semantically under-specified to port safely;
   static control-flow comparison will fail before any runtime enablement.

Discriminating measurement: choose the smallest heap-guard entry point, write
its assembly while preserving its original symbol, assemble with
`mips-linux-gnu-as -mips2 -mabi=32 -EB`, link with `patches.ld`/`syms.ld`, run
`build/N64Recomp` on the ELF, and compare the generated host function's branch
targets and referenced guest addresses with the C guard's intended path. A
successful structural match selects H1; linker/N64Recomp failure selects H2;
control-flow mismatch selects H3. Do not enable an unverified override.
