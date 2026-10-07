# Next work unit: capture the M5 A11 pending-slot recurrence

HYPOTHESIS-ID: m5-a11-pending-slot-recurrence

Use the existing canonical real-audio/LLE/ungated/solo/spin-yield route and the
existing A11 phase-scoped table. Do not change the wait, cap, predicate, slot
state, guest behavior, or host writeback. The s4141 source-context route is
parked after two retries failed to reach a paired hangar phase.

Competing hypotheses and discriminator:

- H-A11-pending-reproduced: a qualified title/hangar run records the pending
  `chCount=16` call and the complete slot `01/02/00` writer/terminal sequence.
- H-A11-not-reproduced: both phase gates and the positive control pass, but no
  pending `chCount=16` call appears; this parks the recurrence without
  changing the wait.
- H-route-invalid: the positive control or either target phase gate is absent.

Before building, verify the existing A11 probe and its positive-control env
var in the tracked debug catalog. Build once, then run one bounded canonical
real-audio route from `build/` with the existing phase and A11 env vars. Kill
the process group with SIGKILL. Accept a conclusion only if the run has the
whole-RDRAM/phase controls plus either the complete pending transition or a
qualified null.

Expected discriminating outcomes: pending `chCount=16` plus a complete
writer/terminal table selects H-A11-pending-reproduced; qualified absence
selects H-A11-not-reproduced; missing controls select H-route-invalid.
