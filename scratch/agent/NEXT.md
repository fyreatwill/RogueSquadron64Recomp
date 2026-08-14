# NEXT work unit (s1087)

HYPOTHESIS-ID: oracle-execution-gate

Implement one bounded capability change in the retail oracle: a guest-PC
execution breakpoint/watch that records hits and resumes, exposed by a CLI
option. Then build it and run one established eleven-Start capture with the
whole-RDRAM positive-control write watch, PIF trace, VI trace, and execution
watches at `mainGameLoop`'s gate read (`0x8003E07C`) plus its preceding state
transition (`0x8003E010`). Do not change the input schedule or arm a freelist
watch.

Competing hypotheses and discriminator:

* `H-main-loop-gate-reached`: a hit at `0x8003E07C` with positive controls
  proves the retail route reaches the state machine; the silent physical RAM
  watch is then an address/alias mismatch or a different generated access.
* `H-pre-main-loop-state-gate`: the preceding transition executes but the gate
  read does not, selecting an earlier state/return gate.
* `H-route-before-state-machine`: neither execution watch hits while the
  whole-RDRAM, PIF, and VI controls pass, confirming the route exits before
  this state machine.
* `H-unresolved`: any positive control or VI/PIF control fails, so execution
  results are not interpretable.

Discriminating measurement: execution-hit PCs in the same run, phase-gated by
the first VI width/origin transition. A gate-PC hit selects
`H-main-loop-gate-reached`; a preceding-PC-only hit selects
`H-pre-main-loop-state-gate`; zero hits with positive controls selects
`H-route-before-state-machine`.

Exact validation commands after the implementation:

```sh
cmake --build tools/oracle/build --config Debug
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 120 --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B10:0x130B58 --watch-pc 0x8003E010,0x8003E07C --vi-trace --pif-trace
```
