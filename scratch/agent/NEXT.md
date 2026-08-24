# NEXT work unit (s2225) — paired key-on census coverage-boundary test

HYPOTHESIS-ID: m5-audio-keyon-contract

## Work unit

Run a same-build concurrent A/B of the existing port census to determine
whether s2224's tuple-detail logging caused the early coverage boundary. Both
arms must keep `ROGUESQ_AUDIO_UCODE=1`, `ROGUESQ_M5_C88_VALUE=1`,
`ROGUESQ_SPIN_YIELD=1`, and `ROGUESQ_LOG_M5_KEYON_CENSUS=1`; the detail arm sets
`ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1`, while the quiet arm sets it to `0`.
Use explicit categories instead of `ROGUESQ_LOG_ALL=1` so the A/B differs in
only the new transfer-row output. No generated function logic or guard changes
are allowed.

Competing hypotheses and the single discriminator:

- H-TransferLogOverhead: the detail arm dies before later phase buckets while
  the quiet arm reaches the second target or hangar.
- H-ExistingRouteBoundary: both arms pass the first-target controls and stop at
  the same `renderLitMeshFaceGroup`/guest-PC boundary.
- H-PortCoverageFailure: one or both arms lack the positive first-target
  controls, or both arms stop before the phase matrix can reach the required
  second-target and hangar buckets for an independent comparison.
- H-PortCoverageRecovered: both arms reach all required buckets; use their
  phase-keyed transfer/divide/guard/tuple rows to resume the retail comparison.

The discriminator is the paired outcome plus the same phase-keyed matrix:
both arms must show entry/tail/slot controls and the first target; later target
and hangar phases are required before interpreting tuple parity. Detail-only
failure selects H-TransferLogOverhead; identical early failure selects
H-ExistingRouteBoundary; missing controls selects H-PortCoverageFailure; full
coverage reopens the retail/port tuple comparison.

## Exact commands

Use the existing s2224-built binary; no rebuild is needed unless the generated
tree or fixer changes before the run. Launch both arms concurrently from the
repository root:

~~~sh
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2225_keyon_detail 30 12 > scratch/agent/s2225_keyon_detail_driver.log 2>&1 &
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_M5_KEYON_CENSUS=1 ROGUESQ_LOG_M5_KEYON_PORT_TUPLES=0 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2225_keyon_quiet 30 12 > scratch/agent/s2225_keyon_quiet_driver.log 2>&1 &
wait
~~~

Use each port log's positive controls first, then compare phase keys and the
terminal crash/guest-PC markers. Do not infer a branch or authorize a return
change from a partial matrix.
