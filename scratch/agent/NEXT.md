# NEXT work unit (s2871) — M5-route-repair-discriminator

HYPOTHESIS-ID: M5-route-repair-discriminator

## Work unit

Use one bounded source/configuration audit to identify a new, testable
post-dispatch route discriminator for the persistent port stop at VI 640.
Compare the exact image-arm launch environment and phase/input gating against
the last qualified hangar recipe, then select one changed route control to
test next. Do not interpret downstream audio nulls or change behavior in this
unit.

## Competing hypotheses and discriminator

- H-config-drift: the current launch recipe differs from the last qualified
  route in a concrete environment, working-directory, binary, ROM, or input
  control.
- H-route-state: the recipe matches, so the stop is caused by a state/control
  boundary not covered by the exhausted route angles.
- H-input-gate: the image arm reaches the input path but the phase-relative
  schedule is not delivered at the expected caller or width.

The discriminator is a single audit table with one row per launch/control
field and an explicit last-qualified value, current value, and source. A
concrete mismatch selects H-config-drift; no mismatch selects H-route-state;
an input-delivery mismatch selects H-input-gate. The next run must test the
selected field in both arms of one build if an A/B is warranted.

## Exact command

Inspect before building or running:

    rg -n 'ROGUESQ_|PROBE_|AUTOPILOT|RogueSquadron64Recomp|rogue_squadron.z64' scratch/agent/run_s2285_m5_step1_contract_pair.sh tools/probe.sh docs/REGRESSION-HARNESS.md
    stat -f '%N %z %m' build/RogueSquadron64Recomp build/rogue_squadron.z64

Then build/run only if the audit selects a concrete changed control; record
the two-arm command and phase-gated outcome under
`scratch/agent/s2871_m5_route_repair_discriminator/`.
