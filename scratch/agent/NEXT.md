# NEXT work unit (s2693) — phase-qualified validation of drain-loop tick de-stub

HYPOTHESIS-ID: m5-drain-tick-destub-validation

## Work unit

Validate the s2692 runtime change. The host-injected
`tickMusyXIfActive` inside `drainAudioAndFinalizeSpeechBuffer` is disabled by
default; `ROGUESQ_DRAIN_INLOOP_TICK=1` is the rollback/control arm. The prior
same-build probes were unevaluable because both stopped at VI width 640 before
the 1024 title phase. Use a phase gate that reaches 1024, then drive through
the route far enough to observe the complete discriminator.

## Competing hypotheses and discriminator

- `H-drain-injection`: the injected tick is required for slot progress; default
  off causes a missing status transition or drain return.
- `H-retail-equivalent`: the injected tick is unnecessary once the real task
  and worker paths are active; default off preserves the route and controls.
- `H-route-only`: the tick changes scheduler/route reachability but not the
  audio contract; only phase or host-message fields move.

The discriminator is one same-build, phase-keyed A/B row: gate setting,
drain entry/return, loop/tick counts, named slot/status transitions, task
dispatch/SP completion, nonzero PCM source and consumer joins, and title/
hangar route origins. A 640-only timeout is invalid and selects nothing.

## Exact commands

1. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Run the existing AUTOPILOT validation with the phase gate widened to allow
   the known 640→1024 transition, once with `ROGUESQ_DRAIN_INLOOP_TICK=0` and
   once with `=1` from the same build; capture logs and terminate each process
   group with SIGKILL.
3. Compare the complete discriminator row. A 640-only timeout is invalid and
   must not select a hypothesis.
