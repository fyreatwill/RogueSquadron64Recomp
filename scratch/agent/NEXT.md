# NEXT work unit (s2990) — M5 wait-on-video signal edge

HYPOTHESIS-ID: m5-independent-buffer-arbiter-handoff

## Unit

Use the already grounded retail `waitOnVideoQueue` edge as a different
producer/signal candidate. The oracle saw 11 target-phase executions, mostly
from predecessor `0x8000BFFC`; static recomp maps that to the call at
`0x8000BFFC` before `waitOnVideoQueue` (`0x8001BE80`). First add one
phase-scoped callsite probe there through the regeneration-safe fixup path,
then build and run the existing port capture. Keep
`ROGUESQ_FORCE_BUFFER_PROGRESS=0`; do not repeat the s2989 READY probe or the
s2988 forced transition driver.

## Competing hypotheses and discriminator

- `H-wait-equivalent`: the port reaches the same target phase and executes the
  wait edge with a matching queue/register/state tuple; the missing route is
  elsewhere.
- `H-wait-missing`: retail executes this wait edge in title/hangar but the port
  has no target-phase execution, selecting this signal boundary.
- `H-wait-repair`: a bounded change at this signal edge reaches title/hangar
  without degrading the LLE task positive control.

The one discriminating table must contain retail PC/predecessor attribution,
port wait-callsite rows, the same-run positive-control rows, VI transitions,
target route rows, and crash/abort markers. A port null is valid only if the
positive controls and target phase both fire.

## Commands

Ground truth is already recorded in
`scratch/agent/s2989_m5_new_handoff/oracle.log` and `RESULTS.md`. Inspect the
existing `waitOnVideoQueue` call at `../N64Recomp/RecompiledFuncs/funcs_3.c`
and its callers. Add the probe to `../N64Recomp/fixup_game_funcs.py` and the
generated output, build with:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run from the repo root with `tools/probe.sh`, using
`PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1` plus the
qualified LLE/image, task, route, phase, and passive breadcrumb variables.
Use SIGKILL/watchdog semantics and write results under
`scratch/agent/s2990_m5_wait_signal/`.
