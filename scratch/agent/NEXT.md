# NEXT work unit (s2448) — capture caller-side `rs_memset` ABI state

HYPOTHESIS-ID: m5-port-static-rsmemset-callsite

## Work unit

Add one regeneration-safe, observation-only caller-side table around all 88
generated `jal 0x800078E0` callsites. Record the static callsite address,
`ctx->r31` immediately before the generated call, breadcrumb, route identity,
and the matching `rs_memset` entry ordinal. Join the table to the corrected
s2447 phase-scoped entry rows and the existing second-range rows. Do not change
audio, output, task data, dispatch, or guards.

## Competing hypotheses and discriminator

- H-CallsiteWritesRA: caller-side rows show a nonzero `ctx->r31` that is lost
  between the generated call and `rs_memset` entry.
- H-CallsiteAlreadyZero: all 88 caller-side rows show zero `ctx->r31`, proving
  the generated caller path does not materialize the guest return address.
- H-EntryWrapperClearsRA: caller-side rows show a nonzero return value, while
  entry rows remain zero, locating the loss in the host call/wrapper boundary.

The discriminator is a single table covering every static callsite in both
stub/image arms, with the known indirect target `0x8009123C` positive control
still required. A nonzero caller value plus zero entry value selects
H-EntryWrapperClearsRA; zero at both sides selects H-CallsiteAlreadyZero; a
nonzero joined entry selects H-CallsiteWritesRA. A null is valid only with the
retail whole-RDRAM, title/hangar, exact-range, writer-PC, and both port route
controls passing.

## Exact commands

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`env ROGUESQ_LOG_M5_STATIC_CALLS=1 zsh scratch/agent/run_s2325_m5_task_output_join.sh s2448_m5_static_rsmemset_callsite_abi`

Keep the established eleven-Start schedule, phase-gated budgets, SIGKILL
cleanup, and qualified route:
`ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1
ROGUESQ_LLE_SOLO=1`.
