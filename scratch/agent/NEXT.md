# NEXT work unit (s868)

HYPOTHESIS-ID: m3-coalesce-phase-driver

Run one 20-second retail-oracle input-validation experiment. Preserve the
whole-RDRAM positive control, VI trace, and retail ROM; add `--pif-trace` and
use: `2:start,4:start,6:start,8:start,10:start,12:start,14:start,16:start,18:start`.
Do not add target watches or change emulated game behavior.

Competing hypotheses:

- H-pif-start: PIF shows Start-bit transitions and VI advances beyond width 320.
- H-input-map: presses are delivered but PIF never shows Start.
- H-game-state: PIF shows Start but VI remains width 320.

Discriminating measurement: whole-RDRAM must fire, PIF must show each scheduled
Start bit, and VI must show a post-320 width/origin transition. Missing PIF
Start selects H-input-map; present PIF Start with no transition selects
H-game-state; both controls plus a transition validate the driver.

Exact command:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 20 --watch-write 0x0:0x800000 --vi-trace --pif-trace \
  --press '2:start,4:start,6:start,8:start,10:start,12:start,14:start,16:start,18:start' \
  2>&1 | tee scratch/agent/oracle_s868_pif.log
```
