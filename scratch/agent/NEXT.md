# NEXT work unit (s1086)

HYPOTHESIS-ID: oracle-512-state-gate-owner

Run exactly one retail-oracle measurement using the established eleven-Start
schedule. Do not build the port or change the schedule. Use the debugger-on
oracle with a whole-RDRAM positive-control write watch, the existing PIF and VI
controls, and a physical read/write watch on the full mission-state block
`0x130B10:0x130B58`.

Competing hypotheses and discriminator:

* `H-state-block-active`: mission-state reads/writes occur, but the gate byte
  remains untouched, identifying a pre-gate state path.
* `H-gate-not-reached`: controls pass and the entire mission-state block is
  silent, confirming the route never touches this state object.
* `H-gate-read-exec`: the block and gate are read with no gate write, proving
  the gate is reached with an unresolved runtime value/branch.
* `H-gate-write-exec`: a gate write with an attributed guest PC occurs.
* `H-unresolved`: controls or the phase signal fail, so the target result is
  not interpretable.

Discriminating measurement: block activity without gate access selects
`H-state-block-active`; block silence with positive controls selects
`H-gate-not-reached`; a gate read without a write selects `H-gate-read-exec`; a
gate write selects `H-gate-write-exec`; failed controls select `H-unresolved`.

Exact command:

```sh
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
tools/oracle/build/rs64_oracle --core "$CORE" --rom "$ROM" --secs 120 \
  --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
  --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B10:0x130B58 \
  --vi-trace --pif-trace
```
