# NEXT work unit (s2467) — capture inherited r31 at converter/resolver boundary

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Context

s2466's complete static census selected H-CallerContextZero at ABI/context
scope: the converter's resolver input is `ctx->r31`, and its only generated
caller supplies no new `r31` before the continuation-style call. The remaining
question is which earlier caller boundary first makes the inherited value zero.

## Work unit

Add one phase-gated capture at the converter entry and terminal resolver edge
in the fixup script. Record `ctx->r31`, `ctx->r25`, `ctx->r4`, `ctx->r5`, and
the last guest PC for the first null tuple; retain the existing shared-resolver
positive-control row for `0x8009123C`. Use the qualified route and one run.
No guard, stub, dispatch, callback, or audio behavior change.

## Competing hypotheses and discriminator

- H-CallerContextZero: the inherited `ctx->r31` is already zero at converter
  entry, identifying the earlier caller/context boundary as the source.
- H-ConverterRegisterZero: converter entry has nonzero `r31` but terminal
  `r25` is zero, implying an in-body register overwrite not present in the
  static census.
- H-UnseenLoweringEdge: converter entry has nonzero `r31`/`r25`, but the
  resolver observes zero, implying an unobserved lowering edge between them.

The discriminator is one ordered table of the converter-entry and
resolver-edge tuples plus the fixed shared-resolver positive-control row.
`entry_r31==0` and `entry_r25==0` selects H-CallerContextZero;
`entry_r31!=0` with `entry_r25==0` selects H-ConverterRegisterZero; both
nonzero at entry with zero only at resolver selects H-UnseenLoweringEdge. A
missing positive-control row invalidates the run.

## Exact commands

1. Ask/verify the retail oracle whole-RDRAM control and hangar phase before
   adding the port capture; no retail behavior change is expected.
2. Add the two phase-gated rows in `fixup_game_funcs.py`, regenerate in the
   documented order, and retain `ROGUESQ_LOG_M5_PRETARGET=1` plus its phase-4
   positive-control row.
3. Run the qualified route from `build/` for 30 seconds, SIGKILLing the game
   if it remains active, and write
   `scratch/agent/s2467_m5_inherited_r31/audit.md`.
