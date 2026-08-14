# NEXT work unit (s1084)

HYPOTHESIS-ID: oracle-512-state-gate-owner

Run exactly one retail-oracle measurement using the established eleven-Start
schedule. Do not build the port or change the schedule. Use the debugger-on
oracle with a whole-RDRAM positive-control write watch, the existing PIF and VI
controls, and a physical write watch on `0x130B30:0x130B31`.

Expected command shape (use the configured core path from prior oracle
recipes):

```sh
tools/oracle/build/rs64_oracle --core "$ORACLE_CORE" --rom \
  /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 120 --press 6:start,11:start,16:start,21:start,26:start,31:start,\
36:start,41:start,46:start,51:start,56:start --hold-ms 150 \
  --watch-write 0x0:0x800000 --watch-write 0x130B30:0x130B31 \
  --vi-trace --pif-trace
```

Competing hypotheses and discriminator:

* `H-gate-write-exec`: target writes occur with a guest PC before/around the
  expected transition.
* `H-gate-not-reached`: whole-RDRAM/PIF/VI controls pass, but the target write
  is absent and the run remains width 320.
* `H-gate-unresolved`: controls or phase transition fail, so the target null is
  not interpretable.

Discriminating measurement: a target write with an attributed guest PC selects
`H-gate-write-exec`; an absent target write with positive controls and no 512
hangar transition selects `H-gate-not-reached`; failed controls select
`H-gate-unresolved`.
