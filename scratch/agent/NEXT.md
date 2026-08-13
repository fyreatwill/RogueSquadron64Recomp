# NEXT work unit (audit the later 1024 initVideoSubsystem selection)

HYPOTHESIS-ID: m3-vi1024-init-selection

Run one bounded source-to-predicate audit of the reachable
`initVideoSubsystem` call at `0x8001B720`, then one batched phase-gated capture
of the predicate and selected row. Keep the s808 writer markers, host VI/mode
positive control, `[vi-gate]` controls, E9 provenance controls, and phase-gated
key schedule. Do not change mode data or add a mitigation.

## Competing hypotheses

- H-init-1024-intended: `initVideoSubsystem` legitimately selects the 1024 row
  when its stack/config predicate is true. Prediction: source and capture agree
  on the predicate values and selected `0x80128DA0` row.
- H-init-state-misrouted: the reachable predicate selects 640 despite state that
  should select 1024. Prediction: source identifies a mismatched branch/value,
  and the capture shows the wrong row for the observed state.
- H-missing-1024-state: the 1024-capable row is reachable only through a later
  state/config writer not yet identified. Prediction: the callsite is valid, but
  source inventory finds a concrete missing writer or gate feeding its selector.

## Discriminating measurement

The complete `initVideoSubsystem` selector/branch inventory, joined to the
first post-transition `[vi-gate]` row and host `osViSetMode` record, splits the
hypotheses. The source audit must name each predicate input and row; the
runtime capture must confirm those values at the 1024 transition. A marker
proving only that `initVideoSubsystem` ran is insufficient.

## Exact commands

```sh
# Before editing/building, inventory the reachable selector and mode-row inputs:
rg -n 'MEM_W\(-0X716C|MEM_W\(-0X7170|MEM_B\(-0X579B|MEM_B\(-0X579C|MEM_B\(-0X579E' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -C 30 'initVideoSubsystem|0x8001B720|0X80128DA0|0X80128E40' ../N64Recomp/RecompiledFuncs/funcs_5.c

# Then run the existing phase-gated recipe with the batched selector marker,
# ROGUESQ_LOG_VI_WRITERS=1, host VI/mode and E9 positive controls, and SIGKILL
# watchdog. Compare the predicate values directly to the selected row width.
```

Expected outcomes: matching predicate and 1024 row advances H-init-1024-intended;
a mismatched predicate/row advances H-init-state-misrouted; a concrete missing
state writer advances H-missing-1024-state. No skip, guard, restore, or other
mitigation is authorized.
