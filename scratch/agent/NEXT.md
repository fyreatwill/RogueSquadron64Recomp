# NEXT work unit (s2469) — locate the first zero before setupCameraMatrices

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Work unit

Perform a static caller census for `setupCameraMatrices`, then add one
phase-gated diagnostic at its earliest reachable caller boundary. Record the
caller identity, `r31`, `r4`, and `r5`, retaining the existing
`0x8009123C` resolver positive-control row. If the complete static caller set
is small enough, instrument every caller in the same fixup/build/run so the
first-zero table is exhaustive. Do not add a guard, stub, dispatch, callback,
audio, output, or task-data change.

## Competing hypotheses and discriminator

- H-SetupCallerZero: setupCameraMatrices receives `r31=0` from an earlier caller.
- H-SetupCallerNonzero: setupCameraMatrices receives nonzero `r31`, so the zero is introduced inside setupCameraMatrices.
- H-UnreachableCaller: the statically selected caller does not reach phase 4; another caller or dispatch path supplies the live zero.

The exhaustive caller table plus live phase-4 rows is the discriminator.
Caller-side zero selects H-SetupCallerZero; caller-side nonzero with setup
entry zero selects H-SetupCallerNonzero; no live row from the statically
selected caller selects H-UnreachableCaller. A missing `0x8009123C` row
invalidates the run.

## Commands

1. Run the retail oracle with Rice, the whole-RDRAM positive control, freelist watch, and driven Start schedule; confirm positive-control and hangar rows.
2. Add the two rows in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`, then regenerate in order: `python3 tools/make_elf.py`, clean `RecompiledFuncs`, `N64Recomp rogue_squadron.toml`, `python3 fixup_game_funcs.py`, and `cmake --build build --parallel 4`.
3. Run from `build/` for 30 seconds with `ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_LOG_M5_PRETARGET=1`, SIGKILLing the game, and write `scratch/agent/s2469_m5_setup_caller_boundary/audit.md`.
