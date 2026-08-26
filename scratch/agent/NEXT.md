# NEXT work unit (s2464) — isolate the earliest pre-target null-dispatch boundary

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

The s2463 callback tuple was qualified but blocked before the target phase.
Build one phase-gated capture at the earliest reachable pre-target boundary
around `convertMat3x4ToN64Mtx` and its indirect calls, retaining the indirect
resolver positive control and the phase transition control. Do not add guards
or change dispatch/audio behavior.

## Competing hypotheses and discriminator

- H-TargetBoundary: the next null dispatch is the same pre-target boundary and
  can be captured before the target phase.
- H-EarlierBoundary: a different indirect call in the menu model-viewer path
  reaches `get_function(0)` first.
- H-PhaseMismatch: the existing phase-4 crash is outside the target route and
  the callback boundary remains unevaluable in this run.

The discriminator is the ordered same-run tuple `(phase, named callsite,
requested target, positive-control-fired, crash/return)`. A target-boundary
row immediately before the abort selects H-TargetBoundary; an earlier named
zero-target row selects H-EarlierBoundary; no row before a valid phase-4 crash
or a missing positive control is a non-result and selects H-PhaseMismatch only
as a route diagnosis, not as a callback conclusion.

## Exact commands

1. Run the retail oracle positive-control recipe from `tools/oracle/README.md`
   and retain its whole-RDRAM and hangar-phase counts.
2. Grep the generated `convertMat3x4ToN64Mtx` body and its direct callers;
   add all selected pre-target capture points in one fixup build, with bounded
   phase rows and the indirect resolver positive control.
3. Run the qualified route from `docs/CURRENT-TRUTH.md`, compare the ordered
   rows, and write `scratch/agent/s2464_m5_pre_target_boundary/audit.md`.
