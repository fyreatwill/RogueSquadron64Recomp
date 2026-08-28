# NEXT work unit (s2992) — M5 producer-mark route edge

HYPOTHESIS-ID: m5-independent-buffer-arbiter-handoff

## Unit

Use the next retail-grounded edge, `bufferArbiterProducerMark` (`0x8001BCE4`),
at dominant predecessor `0x8000C0C4` from the s2989 oracle table. Verify the
exact generated caller, add one phase-scoped probe through the regeneration-
safe fixup path, build, and run the qualified port capture with
`ROGUESQ_FORCE_BUFFER_PROGRESS=0`. Do not repeat the READY, wait-on-video, or
alloc probes unchanged.

## Competing hypotheses and discriminator

- `H-producer-equivalent`: the port reaches target phase and executes the
  producer edge with a matching route/register tuple; the missing route is
  elsewhere.
- `H-producer-missing`: retail executes the producer edge in title/hangar but
  the port has no target-phase execution, selecting this signal boundary.
- `H-producer-repair`: a bounded change at this edge reaches title/hangar
  without degrading the LLE/task positive control.

The single table must contain independent retail attribution, all producer
callsite rows, same-run positive-control rows, VI transitions, target route
rows, and crash/abort markers. A port null is valid only when positive
controls and target phase both fire.

## Commands

Inspect `../N64Recomp/RecompiledFuncs/funcs_3.c` and
`scratch/agent/s2989_m5_new_handoff/RESULTS.md`, then add the fixup and
generated output. Build with:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Capture under `scratch/agent/s2992_m5_producer_signal/` with `tools/probe.sh`,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, `PROBE_LEAVE_OK=1`, the
qualified LLE/image/task/route/passive breadcrumb variables, and SIGKILL /
watchdog cleanup.
