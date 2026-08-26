# NEXT work unit (s2468) — locate the first zero before the converter

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Add one phase-gated, diagnostic-only capture at the `setupCameraMatrices` callsite into `traverseSceneGraphRecursive` and at `traverseSceneGraphRecursive` entry. Record `r31`, `r4`, and `r5` at both boundaries, retaining the existing `0x8009123C` resolver positive-control row. Use one clean regeneration, one build, and one qualified-route run. Do not add a guard, stub, dispatch, callback, audio, output, or task-data change.

## Competing hypotheses and discriminator

- H-SetupCallerZero: the callsite already has `r31=0`, so the zero is supplied before the traverse call.
- H-TraverseLoweringZero: the callsite has nonzero `r31` but traverse entry has zero, identifying the call-lowering boundary.
- H-ContextClobber: both callsite and traverse entry have nonzero `r31`, so the zero must be introduced between traverse entry and the converter call.

The ordered callsite/entry table is the discriminator. Callsite zero selects H-SetupCallerZero; nonzero callsite with zero entry selects H-TraverseLoweringZero; both nonzero selects H-ContextClobber. A missing `0x8009123C` row invalidates the run.

## Commands

1. Run the retail oracle with Rice, the whole-RDRAM positive control, freelist watch, and driven Start schedule; confirm positive-control and hangar rows.
2. Add the two rows in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, then regenerate in order: `python3 tools/make_elf.py`, clean `RecompiledFuncs`, `N64Recomp rogue_squadron.toml`, `python3 fixup_game_funcs.py`, and `cmake --build build --parallel 4`.
3. Run from `build/` for 30 seconds with `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_PRETARGET=1`, SIGKILLing the game, and write `scratch/agent/s2468_m5_setup_traverse_boundary/audit.md`.
