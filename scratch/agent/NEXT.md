# Next work unit: qualify the M3 patch target and sentinel guard on a MIPS host

HYPOTHESIS-ID: m3-active-queue-sentinel-predecessor

The CMake graph now discovers native tool names and repairs stale Windows
`N64RECOMP_EXE` cache values. This host still lacks the MIPS compiler/linker;
the next run requires a supplied/installable toolchain or a host that has one.
Do not run an M5 route permutation or writer census in that unit.

Competing hypotheses:

- H1: with `mips64-elf-gcc` and `mips64-elf-ld` available, the repaired graph
  creates and builds `PatchesLib`, enabling runtime qualification.
- H2: the sentinel may legitimately carry a predecessor during a non-empty
  queue, so source inspection will require redesign before qualification.
- H3: the host still lacks a usable MIPS toolchain or another build dependency,
  leaving runtime qualification blocked despite the repaired graph.

Discriminator: configure and build `PatchesLib` after placing a usable MIPS
toolchain on PATH or passing `-DMIPS_TOOLCHAIN_DIR`. H1 requires a generated
patch ELF, generated `RecompiledPatches/patches.c`, and a successful patch
library build before runtime qualification; H2 requires a concrete legitimate
predecessor path; H3 is the exact remaining configure or toolchain failure.
This iteration observed H3: both MIPS tools were absent and CMake omitted the
target. A repeated run on this host is not informative until that prerequisite
changes.

Commands:

```sh
rg -n "PatchesLib|heap_guards|active_queue|heap_tail_loc" CMakeLists.txt patches build
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug --target RogueSquadron64Recomp
cmake --build build --config Debug --target PatchesLib
```

If the target is absent, record the exact toolchain/configure blocker and do
not infer runtime behavior from the ordinary host build.
