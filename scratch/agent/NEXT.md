# NEXT work unit (s2471) — locate the first zero before menuOverlayInit

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Perform a static caller census for `menuOverlayInit`, then add one phase-gated
diagnostic at every statically generated callsite in the same fixup/build/run.
Record caller identity, callsite PC, `r31`, `r4`, and `r5`, retaining the
existing `0x8009123C` resolver positive-control row. The sole known live caller
is `mainGameLoop`'s dispatch path; identify the earlier caller or continuation
that supplies the zero to `menuOverlayInit`. Do not add a guard, stub,
dispatch, callback, audio, output, or task-data change.

## Competing hypotheses and discriminator

- H-MenuInitCallerZero: menuOverlayInit receives `r31=0` from an earlier caller.
- H-MenuInitCallerNonzero: menuOverlayInit receives nonzero `r31`, so the zero is introduced inside it.
- H-UnreachableMenuInitCaller: the statically selected caller does not reach phase 4; another caller or dispatch path supplies the live zero.

The exhaustive caller table plus live phase-4 rows is the discriminator.
Caller-side zero selects H-MenuInitCallerZero; caller-side nonzero with
menuOverlayInit entry zero selects H-MenuInitCallerNonzero; no live row from
the statically selected caller selects H-UnreachableMenuInitCaller. A missing
`0x8009123C` row invalidates the run.

## Commands

1. Run the retail oracle with Rice, whole-RDRAM positive control, exact range watches, and driven Start schedule; confirm the positive-control and driven VI rows.
2. Add the exhaustive `menuOverlayInit` caller probe to `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, then regenerate in order: `cd /Users/williambuckley/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`, clean `RecompiledFuncs`, `N64Recomp rogue_squadron.toml`, `python3 fixup_game_funcs.py`, and `cmake --build build --parallel 4`.
3. Run from `build/` with `ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_PRETARGET=1`, SIGKILLing the game, and write `scratch/agent/s2471_m5_menu_init_caller_boundary/audit.md`. Expected: caller-side zero selects H-MenuInitCallerZero; caller-side nonzero with menu-init entry zero selects H-MenuInitCallerNonzero; absent live rows with the positive control selects H-UnreachableMenuInitCaller.
