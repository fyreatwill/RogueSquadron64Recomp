# NEXT work unit (s1089)

HYPOTHESIS-ID: oracle-execution-gate

Run one established eleven-Start retail-oracle capture with the same
whole-RDRAM, mission-state, VI, and PIF controls, retaining the call entry /
continuation / gate watches and adding four execution milestones inside
`runIdleFramesAndLoadSaveData`: `0x8006D9B0,0x8006DA7C,0x8006DAB8,0x8006DAF0`.
Use `tools/oracle/build.sh` before the run; `tools/oracle/build` is not a
CMake build directory.

Competing hypotheses and discriminator:

* `H-first-loop-or-subcall`: entry hits, but `0x8006D9B0` stays silent; the
  callee is blocked before its first 32-frame-loop exit test.
* `H-save-tail-boundary`: `0x8006D9B0` hits but `0x8006DA7C` stays silent; the
  callee exits its first loop but blocks in reset/save/load handling.
* `H-writer-reached`: `0x8006DAB8` hits; the known `0x80130B30` writer runs,
  proving the callee reaches its post-save tail even if it never returns.
* `H-final-loop-boundary`: `0x8006DAF0` hits while continuation/gate remain
  silent; the callee reaches its final eight-frame loop and blocks there or in
  its frame subcalls.
* `H-unresolved`: whole-RDRAM, PIF, or VI controls fail.

Discriminating measurement: same-run hit pattern for all four internal
milestones plus the existing entry/continuation/gate PCs. Do not arm a
freelist watch without an independently observed `0x6abxxx` hangar-origin 512
transition.

Exact command:

```sh
tools/oracle/build.sh
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 120 --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B10:0x130B58 --watch-pc 0x8006D900,0x8003E018,0x8003E07C,0x8006D9B0,0x8006DA7C,0x8006DAB8,0x8006DAF0 --vi-trace --pif-trace
```
