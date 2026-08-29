# NEXT work unit — obtain a new M5 target-phase discriminator

HYPOTHESIS-ID: m5-target-phase-edge

Session 3240 closed the MusyX null-consumer class as static and non-patchable.
The next unit returns to M5 only with a genuinely new independent retail
target-phase discriminator; do not repeat the parked port pair or add a port
counter before ground truth.

## Competing hypotheses

- `H-PortBoundary`: a new target-phase retail writer/ordering row identifies
  the missing port boundary.
- `H-RetailRouteMismatch`: the observed retail target transition is not
  comparable to the port's pre-title VI and must be rejoined at a different
  execution edge.
- `H-NoDiscriminator`: the available oracle route still cannot reach or join
  the target phase, so no port behavior change is authorized.

## Discriminator

Ask the independent retail oracle for one new target-phase execution watch or
join around the known `0x00790A00` transition, with the whole-RDRAM positive
control armed in the same run. The result must expose writer PC, destination
span, payload polarity, and completion ordering. A complete row selects
`H-PortBoundary`; a valid alternate join selects `H-RetailRouteMismatch`; a
missing positive-controlled target transition selects `H-NoDiscriminator` and
parks M5 without changing port behavior.

## Exact commands

1. Read `tools/oracle/README.md` and the existing target-phase oracle recipe;
   identify the exact watch/join site before instrumenting.
2. Build every oracle arm in one change, retaining the whole-RDRAM positive
   control and phase gate; run the retail recipe once and capture the bounded
   result under `scratch/agent/soak_results/`.
3. Record the selected hypothesis and its two evidence lines in the ledger.
