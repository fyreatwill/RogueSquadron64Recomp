# NEXT work unit (s2945) — ground-truth M5 route-state handoff census

HYPOTHESIS-ID: m5-route-state-repair

M5 remains the strategic priority, while the current port route is invalid
for title/hangar audio interpretation. Run one independent retail-oracle
census for a new post-dispatch route-state handoff, using the verified Rice
video and Start schedule. Do not add port instrumentation or change behavior
in this work unit.

## Competing hypotheses and discriminator

- H-RouteState: a distinct retail CPU handoff/return changes the route into
  title or hangar; its execution and return fields differ between the verified
  Start-driven route and the undriven control.
- H-RouteInput: the handoff is reached identically, and only input delivery or
  timing differs; route-state fields do not explain the port stop.
- H-RouteAbsent: the candidate handoff is not executed in the target phase, so
  this candidate cannot repair the route explanation.

The discriminator is one phase-keyed table containing the candidate PC,
previous PC, `$v0/$s1/$a0/$a2`, VI width/origin, and execution counts for both
the undriven and verified Start schedules, with the whole-RDRAM watch as the
same-run positive control. H-RouteState requires a target-phase execution and
distinct handoff fields; identical fields select H-RouteInput; no target-phase
execution selects H-RouteAbsent. A missing whole-RDRAM control invalidates the
run.

## Exact command

```sh
mkdir -p scratch/agent/s2945_m5_route_state
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 60 --watch-write 0x0:0x800000 \
  --watch-pc-range 0x80019C00:0x8001A000 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2945_m5_route_state/RESULTS.md 2>&1
```

Record the control count, target phases, and candidate-PC table in
`RESULTS.md`. If the selected range is not a genuinely new handoff after the
static audit, stop and replace it before running.
