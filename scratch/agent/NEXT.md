# NEXT work unit (s971)

Compile the oracle `memory.c` and `dbg_breakpoints.c` once with the exact
successful compile flags but `-fno-lto -S`, then inspect the emitted ARM64
assembly call and compare it with the current LTO dylib call. Do not edit the
recomp runtime or retry retail PIF/callback hypotheses.

HYPOTHESIS-ID: oracle-pif-link-artifact

Competing hypotheses:

- H-pif-nonlto-correct: non-LTO compile emits the required `w2=4,w3=3`, so
  LTO is the transformation boundary.
- H-pif-source-abi: non-LTO compile reproduces the shifted/missing argument,
  so the source's effective declaration or ABI state is not what preprocessing
  suggests.
- H-pif-other-link-input: non-LTO compile is correct but the current linked
  image differs for an input or link-state reason not visible from symbol
  binding.

Discriminating measurement: compare the fresh non-LTO assembly call with the
LTO dylib call. Correct non-LTO `w2=4,w3=3` selects an LTO transformation;
the same shifted call selects an effective source/ABI defect; a different
non-LTO result or link discrepancy selects another link-input/state defect.

Exact commands:

`cd /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix && gcc -O3 -fno-lto -S -arch arm64 -mmacosx-version-min=10.16 -isysroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk -DDBG -I../../src -I../../src/asm_defines -I../../subprojects ../../src/device/memory/memory.c -o /tmp/rs64-memory-nonlto.s`

`rg -n -C 12 "check_breakpoints_on_mem_access" /tmp/rs64-memory-nonlto.s`

`otool -tvV libmupen64plus.dylib | sed -n '19840,19930p'`

`nm -an libmupen64plus.dylib | rg "check_breakpoints_on_mem_access|read_with_bp_checks"`
