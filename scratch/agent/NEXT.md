# Next work unit (s4398): repair the port phase capture boundary

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4397's port run was invalid for the intended three-bucket comparison:
the positive control, `0x00790400`, and `0x006AB400` were live, but no
`0x00790800` title bucket appeared and the selector rows were hangar-capped.
Run one repaired port capture with the stop-width gate removed so the brief
middle-title transition is observable and the same task/payload joins remain
phase keyed.

Competing hypotheses:

- H-port-three-buckets: removing the stop gate retains all three required VI
  buckets with valid task/image joins, enabling the retail/port comparison.
- H-port-route-boundary: the port route genuinely never presents
  `0x00790800`; positive control plus the other two buckets remain live, so
  the missing bucket is a port-path boundary rather than a null instrument.
- H-port-instrument-failure: the repaired run loses its positive control or
  either known phase, so it is invalid and selects nothing.

Discriminating measurement: one run's summary must report the positive
control, counts for `vi_width=1024 origin=0x00790400`,
`vi_width=1024 origin=0x00790800`, and `vi_width=512 origin=0x006AB400`, plus
task rows and task/image joins. All three buckets with no crash selects
H-port-three-buckets; control + 790400 + 6AB400 but zero 790800 selects
H-port-route-boundary; missing control or either known phase selects
H-port-instrument-failure.

Exact command:

    bash scratch/agent/run_s4397_m5_selector_boundary_port.sh

Before running, edit only the recipe's `ROGUESQ_AUTOPILOT_STOP_WIDTH=512`
assignment out of the `COMMON` array, then run it from the repository root.
The log must remain under
`scratch/agent/s4397_m5_selector_boundary_port/`; kill the game with SIGKILL.
