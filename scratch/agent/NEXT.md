# Next work unit: complete the M5 A11 pending-slot terminal table

HYPOTHESIS-ID: m5-a11-pending-slot-terminal-table

Use the existing canonical real-audio/LLE/ungated/solo/spin-yield route and the
existing A11 phase-scoped table. Do not change the wait, cap, predicate, slot
state, guest behavior, or host writeback. Session 4142 qualified a pending
wait-cap recurrence but did not close the slot writer/terminal relationship.

Competing hypotheses and discriminator:

- H-A11-terminal-complete: a qualified title/hangar run joins the pending
  wait-cap call to a named slot writer and a complete `01/02/00` transition.
- H-A11-terminal-absent: both phase gates and the positive control pass, the
  pending call recurs, but no complete transition is observed; keep the wait
  unchanged and leave the writer boundary open.
- H-route-invalid: the positive control or either target phase gate is absent.

Before building, verify the existing A11 probe and its positive-control env
var in the tracked debug catalog. Build once, then run the paired oracle and
canonical real-audio port independently from `build/`, waiting for both arms
to reach their title and hangar gates before SIGKILL cleanup. Accept a
conclusion only if both arms have the whole-RDRAM/phase controls plus either
the complete pending transition or a qualified pending-without-terminal row.

Expected discriminating outcomes: a pending wait-cap row joined to a named
writer and `01/02/00` transition selects H-A11-terminal-complete; a qualified
pending row with no complete transition selects H-A11-terminal-absent; missing
controls select H-route-invalid.
