# NEXT: G1 — discriminate stable flight from objective progress

Work unit: run a phase-gated A/B mission-1 control comparison in one iteration.
Arm A is the successful s5804 schedule (`scratch/agent/m6_keyed_hold_var.sh`
with `HOLD=600`); arm B is the same title->hangar->mission route with a denser
post-mission combat/objective schedule. Use two simultaneous captures, require
both to reach `0x00690400`, and hold each for at least 600 s or until a
legitimate results/advance transition. Do not use `ROGUESQ_MISSION_WIN`.

Competing hypotheses:

- G1a: mission completion needs more sustained combat/objective input; arm B
  reaches a legitimate results screen and advances while arm A remains stable
  or fails.
- G1b: the current mission objective path is not reachable from this input
  schedule; both arms remain alive but return to title/menu without a win.
- G1c: denser input exposes a distinct crash, stall, or softlock; capture the
  first failure phase and follow it with a backtrace-oriented work unit.

Discriminator: the first legitimate results/advance marker after a
phase-gated mission origin, compared across both arms. A result is only valid
if the route reached hangar before `0x00690400`, the framebuffer-hash and stall
positive controls fired, and the process remained alive through the result.
Record every crash/abort, VI-origin stall over 30 s, and softlock separately.

Exact starting command for arm A:

    zsh scratch/agent/m6_keyed_hold_var.sh s5805_g1a 600

Before running arm B, copy that recipe to a new scratch script and change only
the post-t=260 autopilot schedule to denser alternating stick/fire inputs;
launch both arms concurrently from `build/`, with distinct output directories.
Check `CGSSessionScreenIsLocked` first. No build or new instrumentation is
needed unless the copied recipe fails its existing positive controls.

HYPOTHESIS-ID: g1-mission-progression
