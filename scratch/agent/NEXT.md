# Next work unit: complete the bounded assembly port of allocateDisplayListBuffer
HYPOTHESIS-ID: m3-assembly-patch-pipeline

Competing hypotheses:

1. The remaining original `allocateDisplayListBuffer` path can be hand-written
   in MIPS assembly and consumed by N64Recomp with the existing linker scripts.
2. Absolute game-data references or the helper call need relocation handling
   that the assembly pipeline cannot provide.
3. The existing patch's queue semantics are too under-specified to reproduce
   faithfully from the recovered control flow, so the port should remain
   disabled.

Discriminating measurement: extend `patches/heap_guard_asm.S` to cover the
known original `0x80007D74–0x80007E58` path, assemble with
`make -C patches ASM_ONLY=1 AS=/opt/homebrew/bin/mips-linux-gnu-as LD=/opt/homebrew/bin/mips-linux-gnu-ld patches.elf`,
run `build/N64Recomp patches.toml`, and compare emitted size, branch targets,
and references against the recovered generated translation. Full
control-flow/store coverage selects H1; relocation failure selects H2; any
unmatched queue publication selects H3. Do not enable the override.
