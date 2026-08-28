# NEXT work unit (s2971)

HYPOTHESIS-ID: m5-route-qualification

## Unit

Perform one new M5 route-qualification investigation. Ground-truth the
previously unqualified framebuffer-arbiter producer handoff
`bufferArbiterProducerMark` at guest PC `0x8001BCE4` in retail, using the
verified title/hangar input route. Do not repeat the rejected s2903 candidate
PCs, broad main-text range, or the route-invalid s2949/s2950 field probe. Do
not add port instrumentation unless this watch is positively attributed in a
target phase.

## Competing hypotheses and discriminator

- H-retail-handoff: the independent oracle attributes `0x8001BCE4` in one or
  both target phases, making this a live route handoff for a later port join.
- H-port-handoff: the oracle's whole-RDRAM and title/hangar controls pass, but
  `0x8001BCE4` has zero target-phase executions; this candidate is not the
  target boundary and receives no port instrumentation.
- H-stale-route: the oracle fails its whole-RDRAM positive control or misses
  the title/hangar controls, so this run cannot evaluate the candidate.

The discriminator is the same-run retail oracle table: whole-RDRAM positive
control, title and hangar phase controls, and phase-gated execution rows for
`0x8001BCE4`. A target-phase hit selects H-retail-handoff; healthy controls
with zero target-phase hits select H-port-handoff; a failed control selects
H-stale-route.

## Commands

1. Run `grep -n '^## Session ' PORTING-STATE.md | tail -15`; if all 15 titles
   are sweep-scoped, perform the mandated external retail-entry or M4
   accumulator-boundary revisit instead of another sweep step.
2. Run the retail oracle with its whole-RDRAM positive control and the new
   execution watch, using SIGKILL and a capture path under
   `scratch/agent/s2971_m5_route_qualification/`:
   `tools/oracle/build/rs64_oracle --core /opt/homebrew/opt/mupen64plus/lib/
   libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/
   rogue_squadron64/rogue_squadron.z64 --secs 180 --video
   /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib
   --watch-write 0x0:0x800000 --watch-pc 0x8001BCE4
   --pc-phase-log-width 1024,512 --press 6:start,11:start,16:start,21:start,
   26:start,31:start,36:start,41:start,46:start,51:start,56:start`.
3. Only if the oracle positively attributes the handoff, design the paired port
   measurement for the next iteration; otherwise record the negative result
   without adding runtime instrumentation.
4. Write the oracle table under `scratch/agent/s2971_m5_route_qualification/`.

Expected outcomes: a positive oracle PC attribution selects H-retail-handoff;
an otherwise healthy oracle that misses the candidate selects H-port-handoff;
and a failed positive control selects H-stale-route. Do not add port code on a
negative or stale-route result.
