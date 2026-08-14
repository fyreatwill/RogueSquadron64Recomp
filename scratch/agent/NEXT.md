# NEXT work unit (s1088)

HYPOTHESIS-ID: oracle-execution-gate

Run one established eleven-Start retail-oracle capture using the new
`--watch-pc` option at `0x8006D900,0x8003E018,0x8003E07C`, plus the existing
whole-RDRAM positive-control watch, mission-state read/write watch, VI trace,
and PIF trace. Do not change the schedule or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-callee-not-entered`: `0x8003E010` can execute while the callee entry stays
  silent; this selects a call/dispatch boundary before `runIdleFrames...`.
* `H-callee-does-not-return`: callee entry hits but `0x8003E018` and the gate
  stay silent; this selects a non-return or early termination in the callee.
* `H-post-return-state-gate`: entry and continuation hit, but the gate stays
  silent; this selects a branch/delay/address boundary after return.
* `H-gate-reached`: the gate hits with all controls positive; the prior null
  was a watch-address or execution-path interpretation error.
* `H-unresolved`: whole-RDRAM, PIF, or VI control fails.

Discriminating measurement: per-PC execution-hit counts from the same run,
with positive controls. A hit pattern at entry/continuation/gate selects one
of the first four hypotheses; failed controls make the result uninterpretable.

Exact command:

```sh
cmake --build tools/oracle/build --config Debug
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 120 --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B10:0x130B58 --watch-pc 0x8006D900,0x8003E018,0x8003E07C --vi-trace --pif-trace
```
