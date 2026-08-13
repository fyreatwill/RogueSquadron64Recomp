# NEXT work unit (s869)

HYPOTHESIS-ID: m3-coalesce-phase-driver

Run one 70-second retail-oracle input-validation experiment using the
phase-appropriate schedule. Preserve the whole-RDRAM positive control, VI
trace, and retail ROM; add `--pif-trace` and use:
`6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`.
Do not add target watches or change emulated game behavior.

Competing hypotheses:

- H-pif-start: PIF shows Start-bit transitions and VI advances beyond width 320.
- H-input-map: presses are delivered but PIF never shows Start.
- H-game-state: PIF shows Start but VI remains width 320 under the
  phase-appropriate schedule.

Discriminating measurement: whole-RDRAM must fire, PIF must show each scheduled
Start bit, and VI must show a post-320 width/origin transition. Missing PIF
Start selects H-input-map; present PIF Start with no transition selects
H-game-state; both controls plus a transition validate the driver and permit
the later writer-watch experiment.

Exact command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 70 --watch-write 0x0:0x800000 --vi-trace --pif-trace \
  --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
  2>&1 | tee scratch/agent/oracle_s869_pif.log
```
