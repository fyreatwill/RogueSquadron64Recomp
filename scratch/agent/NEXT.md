# NEXT work unit (s2465) — isolate the earliest pre-target null-dispatch boundary

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Context

s2463 selects H-PhaseMismatch as route diagnosis: the port fires the indirect
resolver positive control, reaches phase 4, then aborts in `get_function(0)`
through `convertMat3x4ToN64Mtx` before any target-phase slot, callback, or
dispatch tuple. The pre-target abort must be characterised before the callback
hypothesis set (H-ZeroWriter / H-ValidWriter / H-UnresolvedWriter) is
evaluable.

## Work unit

Build one phase-gated capture at the earliest reachable pre-target boundary:
log every `get_function(N)` call with its requested address and its native
backtrace from within `convertMat3x4ToN64Mtx`, retaining the indirect resolver
positive control and the phase transition control. Do not add guards or change
dispatch/audio behaviour.

## Competing hypotheses and discriminator

- H-TargetBoundary: the first `get_function(0)` before the abort is in
  `convertMat3x4ToN64Mtx` itself, so the pre-target boundary is already named.
- H-EarlierBoundary: a different indirect call in the menu model-viewer path
  (`traverseSceneGraphRecursive` → `setupCameraMatrices` →
  `runMenuModelViewerScreen`, as established in s2457) reaches `get_function(0)`
  first.
- H-PhaseMismatch: the phase-4 abort is unrelated to the audio target and the
  callback boundary remains unevaluable in this configuration.

The discriminator is the ordered same-run tuple
`(phase, named callsite, requested target, positive-control-fired, crash/return)`.
A `get_function(0)` row at any named site BEFORE the abort selects
H-TargetBoundary (if in `convertMat3x4ToN64Mtx`) or H-EarlierBoundary (if
earlier). A valid phase-4 crash with no `get_function(0)` row is a non-result
and selects H-PhaseMismatch only as a route diagnosis.

## Exact commands

1. Grep the generated body of `convertMat3x4ToN64Mtx` and its direct callers
   in `RecompiledFuncs/` (established chain: `runMenuModelViewerScreen` →
   `setupCameraMatrices` → `traverseSceneGraphRecursive` →
   `convertMat3x4ToN64Mtx`) for `LOOKUP_FUNC` / `get_function` expansions.
2. In one fixup pass, add a phase-gated `get_function`-call capture that logs
   `(phase, requested_addr, native_backtrace_depth_2)` before the resolver is
   called; bound the log to 64 rows per phase; retain the existing indirect
   resolver positive control.
3. Rebuild with `make_elf.py` → N64Recomp → `fixup_game_funcs.py` → cmake.
4. Run the qualified route (`ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1
   ROGUESQ_LLE_SOLO=1 ROGUESQ_SPIN_YIELD=1`) from `build/` with the ROM
   present; SIGKILL after 30 s.
5. Write `scratch/agent/s2465_m5_pre_target_capture/audit.md` with the
   ordered tuple rows and the hypothesis selection.
