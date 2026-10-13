# Build one new mission-route input discriminator for overlay 0x2C

HYPOTHESIS-ID: overlay-0x2c-mission-route

The generated-symbol sweep is closed for the remaining exact-address
placeholders: session 4795 found only deliberate `fake_func_*` entries in the
last bounded mission-overlay range, with no safe mapping. The next unit is one
new mission-route input/driver discriminator, retaining the resident overlay
0x2C splice and the existing phase/VI positive controls. Do not change the
splice or infer its visual effect from hangar-only runs.

Competing hypotheses and discriminator:
- H1: the current input driver reaches the mission route but fails to emit
  overlay-0x2C because the task family is not the triggering one.
- H2: the driver reaches the route and emits `res=0x2C`, but the resident
  splice does not alter the runaway/DL outcome.
- H3: the driver reaches the route and emits `res=0x2C`; the splice removes the
  runaway and produces bounded task completion.
The discriminating measurement is one same-build, phase-gated capture of VI
512 origin, `res=0x2C` dispatch count, overlay-0x2C arrival count, and per-task
DL fetch/runaway classification, with the existing task/VI controls. Every
arm needed for the comparison must be built before the run.

Commands: inspect the existing mission-route driver and `scratch/agent/s4788_drop1_mission_2c.sh`; verify the resident splice is present; make one bounded driver change with `apply_patch`; build the Debug target; run from `build/` with SIGKILL cleanup and capture under `scratch/agent/soak_results/`. No wall-clock-only verdicts.
