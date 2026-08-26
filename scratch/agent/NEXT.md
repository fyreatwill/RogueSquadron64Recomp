# NEXT work unit (s2447) — identify the target-phase rs_memset callsite

HYPOTHESIS-ID: m5-port-static-rsmemset-callsite

## Work unit

Add one regeneration-safe, observation-only table at `rs_memset` entry that
records `ctx->r31`, the current guest-PC breadcrumb, route identity, and the
entry's caller site for every generated static callsite. Cover all 88
`rs_memset` callsites in one build/run and join target-phase rows to the
existing `0x800078EC` second-range rows and image/DMA identity. Do not change
audio, output, task data, dispatch, or guards.

## Competing hypotheses and discriminator

- H-StaticCallerKnown: one or more target-phase callsites have a stable
  generated caller identity and the zero `ra` rows join those callsites.
- H-StaticCallerContextLost: target-phase entry rows exist, but `ctx->r31` is
  zero or otherwise unchanged across all contributing callsites; the loss is
  at the generated call/entry ABI boundary.
- H-StaticCallerOtherPath: the target-phase second-range rows do not join any
  `rs_memset` entry row, so they come from a different resident or stale path.

The discriminator is a single table covering all static callsites in both
stub/image arms. A stable callsite joined to the second-range identity selects
H-StaticCallerKnown; joined entries with zero/unchanged `ra` select
H-StaticCallerContextLost; no joined entry with all route and image controls
valid selects H-StaticCallerOtherPath. The same-run `get_function(0x8009123C)`
positive control must fire, and a null is valid only with retail whole-RDRAM,
title/hangar, exact-range, writer-PC, and both port route controls passing.

## Exact commands

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_LOG_M5_STATIC_CALLS=1 zsh scratch/agent/run_s2325_m5_task_output_join.sh s2447_m5_static_rsmemset_callsites`

Keep the established eleven-Start schedule and retail controls. Keep
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1` on both port arms. Use phase-gated budgets and SIGKILL
cleanup.
