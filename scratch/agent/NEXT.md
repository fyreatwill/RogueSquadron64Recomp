# Next work unit (s4399): classify the port VI-origin/action boundary

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4398 removed the stop-width gate and still observed the positive
control, `0x00790400`, and `0x006AB400`, but zero `0x00790800`; task and image
joins remained live. The next unit must establish whether the port emits a
distinct middle-title VI origin/action or transitions directly from the first
title origin to hangar.

Competing hypotheses:

- H-port-middle-origin: a phase-gated run exposes a distinct nonzero VI origin
  or action between `0x00790400` and `0x006AB400`, identifying the route under a
  different origin label.
- H-port-direct-transition: the complete phase/action sequence contains only
  the known first-title and hangar origins, proving the middle-title route is
  absent from this port path.
- H-port-instrument-failure: the run loses the positive control or either known
  phase, so the sequence is not qualified.

Discriminating measurement: one run must retain a phase-gated ordered table of
every `vi_width/origin` transition and autopilot action, plus the positive
control, task rows, and task/image joins. A distinct intervening origin/action
selects H-port-middle-origin; only the known first-title-to-hangar sequence
selects H-port-direct-transition; missing control or either known phase selects
H-port-instrument-failure.

Exact command: create a new self-contained recipe by copying
`scratch/agent/run_s4397_m5_selector_boundary_port.sh`, change only its output
directory/name to `s4399_m5_port_vi_origin_sequence`, and replace the summary
grep with a phase-gated ordered extraction of all `[phase]`/VI-origin and
`[autopilot]` lines. Run it from the repository root for 85 seconds; keep the
existing positive-control/task/image logging, and kill the game with SIGKILL.
