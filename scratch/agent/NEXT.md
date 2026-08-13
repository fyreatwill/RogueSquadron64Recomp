# NEXT work unit (s870)

HYPOTHESIS-ID: m3-coalesce-phase-driver

Run one 70-second retail-oracle pulse-duration experiment. Preserve the
whole-RDRAM positive control, VI trace, PIF trace, and retail ROM; use the
same schedule with `--hold-ms 1000`:
`6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start`.
Do not add target watches or change emulated game behavior.

Competing hypotheses:

- H-short-pulse: longer Start holds produce a post-320 VI transition.
- H-game-state: sustained Start reaches PIF but VI remains width 320.
- H-input-queue: sustained holds alter the PIF pattern or produce repeated
  transitions, showing injector pulse semantics are the driver.

Discriminating measurement: whole-RDRAM must fire; PIF must show sustained
Start for each scheduled press; and VI must show a post-320 width/origin
transition. A transition only with long holds selects H-short-pulse; sustained
PIF Start with no transition selects H-game-state; an altered/repeated PIF
pattern selects H-input-queue.

Exact command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 70 --watch-write 0x0:0x800000 --vi-trace --pif-trace \
  --hold-ms 1000 \
  --press '6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start' \
  2>&1 | tee scratch/agent/oracle_s870_longhold.log
```
