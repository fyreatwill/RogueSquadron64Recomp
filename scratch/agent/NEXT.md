# NEXT work unit (s1085)

HYPOTHESIS-ID: oracle-512-state-gate-owner

Run exactly one retail-oracle measurement using the established eleven-Start
schedule. Do not build the port or change the schedule. Use the debugger-on
oracle with a whole-RDRAM positive-control write watch, the existing PIF and VI
controls, and a physical read/write watch on `0x130B30:0x130B31`.

Competing hypotheses and discriminator:

* `H-gate-write-exec`: target writes occur with a guest PC before/around the
  expected transition.
* `H-gate-not-reached`: whole-RDRAM/PIF/VI controls pass, but neither target
  read nor write occurs and the run remains width 320.
* `H-gate-unresolved`: controls or phase transition fail, so the target result
  is not interpretable.
* `H-gate-read-exec`: a target read with no write proves the gate is reached and
  narrows the issue to the runtime byte value or branch outcome.

Discriminating measurement: a target write with an attributed guest PC selects
`H-gate-write-exec`; a target read without a write selects `H-gate-read-exec`;
neither read nor write with positive controls selects `H-gate-not-reached`; failed
controls select `H-gate-unresolved`.

Exact command:

```sh
CORE=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib
ROM=/Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64
tools/oracle/build/rs64_oracle --core "$CORE" --rom "$ROM" --secs 120 \
  --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
  --hold-ms 150 --watch-write 0x0:0x800000 --watch-rw 0x130B30:0x130B31 \
  --vi-trace --pif-trace
```
