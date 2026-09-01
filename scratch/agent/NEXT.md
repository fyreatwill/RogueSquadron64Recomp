# NEXT work unit — restore a phase-valid port route for caller/input capture

HYPOTHESIS-ID: m5-preclear-caller-input-producer

Session 3547 selected `H-CaptureInvalid` for the new caller comparison: the
retail oracle was phase-valid, but the real-audio port SIGBUSed in
`parseHmtMaterials+3588` before target entry. Do not repeat the caller table
until the port route is phase-valid.

Do exactly one bounded work unit: identify and correct the existing pre-title
port launch/runtime condition that produces `parseHmtMaterials+3588` with
`last-guest-pc=0x80001F88`, using one controlled real-audio run. Preserve the
caller witness in the generated fixup and keep all audio, PCM, image-task,
output, and texture-record writes unchanged.

Competing hypotheses and discriminator:

- `H-PortRouteRestored`: the port reaches title and hangar with positive
  controls, so the caller table can be rerun next.
- `H-PortPreTitleCrash`: the same pre-title HMT crash reproduces before any
  phase; the route repair hypothesis is not yet tested.
- `H-PortLaunchInvalid`: the process fails to launch or the positive control
  is absent, so no runtime conclusion is allowed.

The single discriminating measurement is the phase/control/crash table:
positive control, title VI, hangar VI, crash PC, and last guest PC. A restored
route selects `H-PortRouteRestored`; the same SIGBUS selects
`H-PortPreTitleCrash`; missing launch/control selects `H-PortLaunchInvalid`.

The single discriminating table must include caller PC, predecessor, phase/VI,
caller inputs/returns, the fields feeding the index, and the first family
store. A matching caller tuple selects `H-CallerParity`; a first differing
input or returned field selects `H-CallerDivergence`; retail-only execution
selects `H-RetailOnlyFamily`; missing controls select `H-CaptureInvalid`.

Before building, retain `scratch/agent/retail_preclear_groundtruth.log` and
read the existing producer injection in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
Batch the instrumentation, then build and run both oracle and port arms in one
iteration. Use VI phase gates, SIGKILL cleanup, and capture under:

    scratch/agent/s3546_m5_caller_input_producer

The intended oracle arm is `tools/oracle/build/rs64_oracle` with
`--watch-write 0x0:0x800000`, the retained source-span watch, and execution
watches for `0x80022ACC`, `0x8001F954`, `0x8001FAA0`, `0x8001FAB4`, and
`0x8001FAC4`, phase-gated to origins `0x00790400:1024` and
`0x006AB400:512`. The port arm must enable the new caller witness on the
validated real-audio route. Positive controls and both target VIs are required
before interpreting a missing caller row.
