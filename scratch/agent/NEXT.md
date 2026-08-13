# NEXT work unit (trace reachable direct VI mode callers)

HYPOTHESIS-ID: m3-vi640-transition-writer

The s803 source audit found six generated `osViSetMode_recomp` callsites. The
selector route at `0x800186C0` → `selectAndApplyViMode` is not reached in the
tested recipe; the reachable candidates are the three direct callers below.
Instrument all three in one build and run, phase-gated at VI 640.

## Competing hypotheses

- H-direct-caller: one reachable direct caller owns the missing transition.
  Prediction: a callsite marker fires after VI 640 and its mode data decodes to
  1024.
- H-overlay-dispatch: the direct callsites fire only for 640 and the intended
  1024 path remains absent. Prediction: no direct marker carries 1024, despite
  the selector's static 1024-capable table.
- H-recipe-state: all three direct callers fire only 320/640 in this recipe.
  Prediction: no post-640 1024 mode request exists anywhere in the batched
  trace.

## Discriminating measurement

The same-run callsite-to-width rows are the discriminator: a direct marker with
width 1024 selects H-direct-caller; only 640 rows while the selector remains
silent selects H-overlay-dispatch; 320/640-only rows across all three selects
H-recipe-state. The existing `osViSetMode` logger and phase transition are the
positive controls; retain the oracle whole-RDRAM watch and VI trace as the
independent ground-truth control.

## Exact commands

```sh
rg -n -S "osViSetMode_recomp|initVideoSubsystem|applyPendingViChanges|swapBufferWithViMode|selectAndApplyViMode" \
  ../N64Recomp/RecompiledFuncs src
```

The next iteration must add the three direct-callsite markers through the
regeneration-safe fixup path, batch them with `[osViSetMode]`, and retain the
oracle `--watch-write 0x0:0x800000 --vi-trace` positive control. Use
`PROBE_PHASE_WIDTH=640 PROBE_LEAVE_OK=1`, never a stopwatch.
