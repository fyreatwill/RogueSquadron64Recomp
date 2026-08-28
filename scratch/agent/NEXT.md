# NEXT work unit (s2991) — M5 new grounded route edge

HYPOTHESIS-ID: m5-independent-buffer-arbiter-handoff

## Unit

Use a different retail-grounded producer/signal edge from the s2989 oracle
table, such as `bufferArbiterAllocSlot` (`0x8001BF20`) at predecessor
`0x8000C13C`. First verify the exact generated caller and obtain/inspect its
independent retail attribution, then add one phase-scoped callsite probe via
the regeneration-safe fixup path. Build and run the existing qualified port
capture with `ROGUESQ_FORCE_BUFFER_PROGRESS=0`; do not repeat the s2989 READY
or s2990 wait-on-video probes unchanged.

## Competing hypotheses and discriminator

- `H-alloc-equivalent`: the port reaches target phase and executes the alloc
  edge with a matching route/register tuple; the missing route is elsewhere.
- `H-alloc-missing`: retail executes the alloc edge in title/hangar but the
  port has no target-phase execution, selecting this signal boundary.
- `H-alloc-repair`: a bounded change at this edge reaches title/hangar without
  degrading the LLE/task positive control.

The single table must contain independent retail PC/predecessor attribution,
port alloc-callsite rows, same-run positive-control rows, VI transitions,
target route rows, and crash/abort markers. A port null is valid only when
positive controls and target phase both fire.

## Commands

Run from the repository root. Inspect `../N64Recomp/RecompiledFuncs/funcs_5.c`
and the s2989 oracle artifact first. Add the fixup and generated output, then:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Capture under `scratch/agent/s2991_m5_alloc_signal/` with `tools/probe.sh`,
`PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, `PROBE_LEAVE_OK=1`,
qualified LLE/image/task/route/passive breadcrumb variables, and SIGKILL/
watchdog cleanup.
