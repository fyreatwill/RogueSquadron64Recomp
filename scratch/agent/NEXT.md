# NEXT work unit (s1034)

HYPOTHESIS-ID: retail-oracle-phase-input-discriminator

Run one bounded retail-oracle input discriminator. Do not build or change the
recomp runtime. The s1033 capture proved callback liveness, threshold removal,
and PIF-visible Start edges, but retail stayed at width 320; do not arm or
interpret the freelist watch until a 512 hangar-origin phase is reached.

## Competing hypotheses and discriminator

* `H-start-not-consumed`: PIF receives Start, but the retail title path does
  not consume the edge; Start-only attempts stay at width 320.
* `H-a-confirmation-required`: Start is not sufficient in this current input
  configuration; an A edge after Start causes a VI transition.
* `H-retail-phase-independent`: neither input arm leaves width 320, so the
  documented phase timeline is not reproducible with this core/config/ROM
  combination and needs a separate environment audit.

Discriminating measurement: one run must show the 10,000-callback
positive-control/removal marker, PIF-visible button words for both arms, and VI
transitions. Send three Start-only edges at 6/11/16 seconds, then three
Start-then-A pairs at 21/26/31 seconds. A width transition after the paired
arm selects `H-a-confirmation-required`; a transition during Start-only makes
the Start path live; no transition after both validated arms selects
`H-retail-phase-independent`. A missing positive-control marker invalidates
the run.

## Exact command

```sh
rm -rf /tmp/rs64-oracle-s1034
mkdir -p /tmp/rs64-oracle-s1034
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/rogue_squadron.z64 \
  --rsp /opt/homebrew/Cellar/mupen64plus/2.6.0/lib/mupen64plus/mupen64plus-rsp-hle.dylib \
  --datadir /opt/homebrew/share/mupen64plus \
  --configdir /tmp/rs64-oracle-s1034 \
  --secs 90 \
  --watch-write 0x0:0x800000 \
  --press 6:start,11:start,16:start,21:start,21.2:a,26:start,26.2:a,31:start,31.2:a \
  --hold-ms 150 --vi-trace --pif-trace \
  > scratch/agent/oracle_s1034_capture.log 2>&1
```

Do not interpret the whole-RDRAM watch as a target; it must be removed at the
validated threshold. If the generated config has `Start = "key(13)"`, patch
that temporary config to `Start = "key(40)"` before the run, as in s1033.
