# NEXT work unit (s1090)

HYPOTHESIS-ID: oracle-save-tail-boundary

Run one established eleven-Start retail-oracle capture with the same
whole-RDRAM, mission-state, VI, and PIF controls, retaining the entry /
continuation / gate watches and four existing milestones. Add a dense,
same-run PC bracket between `0x8006D9B0` and `0x8006DA7C` (choose exact
instruction PCs from the ROM function's bounded `0x8006D900..0x8006DB2B`
range, without changing the schedule). Use `tools/oracle/build.sh` before
the run; `tools/oracle/build` is not a CMake build directory.

Exact command after rebuilding:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 120 --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B10:0x130B58 --watch-pc 0x8006D900,0x8003E018,0x8003E07C,0x8006D9B0,0x8006DA7C,0x8006DAB8,0x8006DAF0,0x8006D9C0,0x8006D9D0,0x8006D9E0,0x8006D9F0,0x8006DA10,0x8006DA30,0x8006DA50,0x8006DA70 --vi-trace --pif-trace
```

Competing hypotheses and discriminator:

* `H-loop-body-subcall`: a bracket PC between `0x8006D9B0` and `0x8006DA7C`
  fires while the later milestone remains silent, locating the block in a
  loop-body call or its return path.
* `H-loop-exit-path`: `0x8006D9B0` fires but every interior bracket PC stays
  silent, locating the boundary in the loop's exit/branch sequence.
* `H-save-tail-reached`: `0x8006DA7C` or a later existing milestone fires,
  overturning the prior boundary and selecting a later save/load subpath.
* `H-unresolved`: whole-RDRAM, PIF, or VI controls fail, invalidating the
  target-watch nulls.

Discriminating measurement: same-run hit pattern for the dense bracket plus
all four existing internal milestones and the entry/continuation/gate PCs.
Before building, inspect the ROM/function instruction map and write the exact
bracket addresses into this file. Do not arm a freelist watch without an
independently observed `0x6abxxx` hangar-origin 512 transition.

Exact command:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 120 --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B10:0x130B58 --watch-pc 0x8006D900,0x8003E018,0x8003E07C,0x8006D9B0,0x8006DA7C,0x8006DAB8,0x8006DAF0 --vi-trace --pif-trace
```
