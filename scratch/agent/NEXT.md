# NEXT work unit (s2470) — locate the first zero before runMenuModelViewerScreen

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Perform a static caller census for `runMenuModelViewerScreen`, then add one
phase-gated diagnostic at every statically generated callsite in the same
fixup/build/run. Record caller identity, callsite PC, `r31`, `r4`, and `r5`,
retaining the existing `0x8009123C` resolver positive-control row. The live
setup caller is `runMenuModelViewerScreen` at `0x800C2D84`; identify the
earlier caller that supplies its zero. Do not add a guard, stub, dispatch,
callback, audio, output, or task-data change.

## Competing hypotheses and discriminator

- H-ModelViewerCallerZero: runMenuModelViewerScreen receives `r31=0` from an earlier caller.
- H-ModelViewerCallerNonzero: runMenuModelViewerScreen receives nonzero `r31`, so the zero is introduced inside it.
- H-UnreachableModelViewerCaller: the statically selected caller does not reach phase 4; another caller or dispatch path supplies the live zero.

The exhaustive caller table plus live phase-4 rows is the discriminator.
Caller-side zero selects H-ModelViewerCallerZero; caller-side nonzero with
model-viewer entry zero selects H-ModelViewerCallerNonzero; no live row from
the statically selected caller selects H-UnreachableModelViewerCaller. A
missing `0x8009123C` row
invalidates the run.

## Commands

1. Run the retail oracle with Rice, whole-RDRAM positive control, exact range watches, and driven Start schedule; confirm the positive-control and driven VI rows.
2. Add the exhaustive `runMenuModelViewerScreen` caller probe to `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, then regenerate in order: `python3 tools/make_elf.py`, clean `RecompiledFuncs`, `N64Recomp rogue_squadron.toml`, `python3 fixup_game_funcs.py`, and `cmake --build build --parallel 4`.
3. Run from `build/` with `ROGUESQ_AUDIO_UCODE=0 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_PRETARGET=1`, SIGKILLing the game, and write `scratch/agent/s2470_m5_model_viewer_caller_boundary/audit.md`. Expected: caller-side zero selects H-ModelViewerCallerZero; caller-side nonzero with model-viewer entry zero selects H-ModelViewerCallerNonzero; absent live rows with the positive control selects H-UnreachableModelViewerCaller.
