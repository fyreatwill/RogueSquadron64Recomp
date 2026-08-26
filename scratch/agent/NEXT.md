# NEXT work unit (s2472) — locate the first zero before mainGameLoop

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Perform a static caller census for `mainGameLoop`, then add one diagnostic at
every generated callsite in the same fixup/build/run. Record caller identity,
callsite PC, `r31`, `r4`, and `r5`, retaining the existing `0x8009123C` resolver
positive-control row. The live menu-init boundary is `mainGameLoop` callsite
`0x8003E090` with `r31=0`; identify the earlier caller or continuation that
supplies that zero to `mainGameLoop`. Because the live call is phase 2, the
capture must be phase-unconditional and capped at 256 rows. Do not add a
guard, stub, dispatch, callback, audio, output, or task-data change.

## Competing hypotheses and discriminator

- H-MainLoopCallerZero: mainGameLoop receives `r31=0` from an earlier caller.
- H-MainLoopCallerNonzero: mainGameLoop receives nonzero `r31`, so the zero is introduced inside it.
- H-UnreachableMainLoopCaller: the statically selected caller does not reach the live menu route; another caller or dispatch path supplies the zero.

The exhaustive caller table plus the live `0x8003E090` route is the
discriminator. Caller-side zero selects H-MainLoopCallerZero; caller-side
nonzero with the menu-init boundary still zero selects H-MainLoopCallerNonzero;
no live row from the statically selected caller selects
H-UnreachableMainLoopCaller. A missing `0x8009123C` row invalidates the run.

## Commands

1. Run the retail oracle with Rice, whole-RDRAM positive control, exact range watches, and driven Start schedule; confirm the positive-control and driven VI rows.
2. Add the exhaustive `mainGameLoop` caller probe to `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, then regenerate in order: `cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`, clean `RecompiledFuncs`, `N64Recomp rogue_squadron.toml`, `python3 fixup_game_funcs.py`, and `cmake --build build --parallel 4`.
3. Run from `build/` with `ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_PRETARGET=1`, SIGKILLing the game, and write `scratch/agent/s2472_m5_main_loop_caller_boundary/audit.md`. Expected: caller-side zero selects H-MainLoopCallerZero; caller-side nonzero with the menu-init boundary still zero selects H-MainLoopCallerNonzero; absent live rows with the positive control selects H-UnreachableMainLoopCaller.
