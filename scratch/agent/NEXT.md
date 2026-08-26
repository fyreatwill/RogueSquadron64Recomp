# NEXT work unit (s2369) — M5 A1 pre-target get_function route boundary

HYPOTHESIS-ID: m5-a1-pre-target-route-boundary

## Work unit

Design and run one ground-truth-first capture of the shared pre-A1
`get_function` abort at guest PC `0x80001F88`. Keep one build and two port
arms (control/alternate), positively control the oracle's whole-RDRAM and both
target origins, and capture the requested function address plus resident
overlay/load rows at the abort. Do not repeat the four-arm/two-wave matrix,
alter VI selection, write back a field, or add a guard. If the abort marker is
not positive in both port arms, select `H-AbortInstrumentInvalid`; if the
requested address is outside the resident overlay, select
`H-MissingOverlayFunction`; otherwise select `H-ResidentOverlayWrongDispatch`.

## Competing hypotheses and discriminating measurement

- H-AbortInstrumentInvalid: the two port arms do not both emit the abort
  marker, so the requested-function table is not trustworthy.
- H-MissingOverlayFunction: both arms emit the marker and the requested
  address is not registered in any resident overlay section.
- H-ResidentOverlayWrongDispatch: both arms emit the marker and the address
  is registered, but the resident overlay/load table points at a different
  dispatch target.

The discriminator is one table keyed by arm and abort ordinal containing the
abort marker, requested guest address, resident overlay/load rows, early 640
transition control, and oracle origin controls. Select a hypothesis only when
the oracle and both port controls pass; otherwise select
`H-AbortInstrumentInvalid`.

## Exact commands

    apply_patch < persistent pre-A1 abort table parser and driver patch
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s2369_m5_a1_pre_target_route_boundary.sh s2369_m5_a1_pre_target_route_boundary
    grep -E '^(controls|table|verdict) ' scratch/agent/s2369_m5_a1_pre_target_route_boundary/driver.log

The driver must run the retail oracle before the port arms, arm whole-RDRAM
and both target-origin controls, use phase-gated budgets, launch both arms
from one build, and kill game processes with SIGKILL. A null without same-run
positive controls is invalid. No behavior change is authorized.
