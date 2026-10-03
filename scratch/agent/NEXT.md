# Next work unit: M5 silent-route crash repeatability

HYPOTHESIS-ID: m5-step1-silent-qualification

Repeat the existing same-build paired Step 1 capture once to distinguish a
stable silent-route failure from run instability. s3761 had valid oracle and
image coverage, while silent crashed before title at
`spTaskSchedulerThread+9556`; do not add task-data fields or change an audio
gate.

Competing hypotheses:

- `H-M5-SilentRouteStable`: silent again crashes before title at the same
  scheduler boundary with valid oracle/image controls; repeated boundary
  supports a stable silent-route defect.
- `H-M5-SilentCanReachTarget`: silent reaches title and hangar in a valid
  paired run; this refutes a deterministic pre-target crash and reopens the
  Step 1 contract comparison.
- `H-M5-SilentRunInstability`: silent fails at a different boundary or the
  oracle/image controls fail; this leaves the crash explanation unresolved and
  requires a new discriminator.

Discriminator: oracle whole-RDRAM positive control (`10000` callbacks) plus
same-build image/silent target phases. Require oracle title/hangar and image
title/hangar before interpreting silent nulls. Compare silent phase markers,
crash PC, `si_addr`, and task/DMA/service/slot/voice/MORT/PCM controls.

Exact commands:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s2285_m5_step1_contract_pair.sh s3762_m5_step1_silent_repeat`

Use the existing LLE-solo, spin-yield, autopilot, phase-gated, oracle-control,
and SIGKILL cleanup recipe. Report both arms and the oracle positive-control
status before interpreting any silent absence.
