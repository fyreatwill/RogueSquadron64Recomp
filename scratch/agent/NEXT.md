# NEXT work unit (classify the 0x11 VI feature request)

HYPOTHESIS-ID: m3-vi640-transition-writer

Run one bounded source-to-caller audit and then one batched phase-gated capture
focused on the reachable `requestViFeatureChange(a0=0x11)` →
`applyPendingViChanges` path. Keep the s808 writer markers, host VI/mode
positive control, `[vi-gate]` controls, E9 provenance controls, and phase-gated
key schedule. Do not add a mitigation or change the requested mask.

## Competing hypotheses

- H-0x11-intended-640: all callers that issue `a0=0x11` are legitimate 640-mode
  requests. Prediction: source caller classification plus the capture show
  the same request/value/order and no alternate 1024 request.
- H-0x11-misrouted: a caller supplies `0x11` on a route that should request a
  1024-capable mode. Prediction: the caller audit identifies a scene/render
  route whose surrounding state differs from the observed capture, or the
  capture shows an unexpected caller/return ordering.
- H-later-1024-route: the 1024 request is a later, currently unexercised
  caller. Prediction: the capture remains 640-only, while source inventory
  identifies a concrete caller and predicate that can publish a 1024 row.

## Discriminating measurement

The complete caller list for `requestViFeatureChange(a0=0x11)`, joined to the
first post-transition writer and next `[vi-gate]` row, splits the hypotheses.
The source audit must identify the caller's scene/render role and predicate;
the runtime capture must confirm ordering. A marker proving only that the
writer is reachable is insufficient.

## Exact commands

```sh
# Before editing/building, confirm the s807 inventory remains unchanged:
rg -n 'MEM_W\(-0X716C|MEM_W\(-0X7170|MEM_B\(-0X579B|MEM_B\(-0X579C|MEM_B\(-0X579E' ../N64Recomp/RecompiledFuncs/funcs_*.c

# Enumerate requestViFeatureChange callers and the a0=0x11 callsites, then run
# the existing phase-gated recipe with ROGUESQ_LOG_VI_WRITERS=1 and positive
# controls/SIGKILL watchdog.
```

Expected outcomes: a classified intended-640 caller advances
H-0x11-intended-640; a mismatched caller/predicate advances H-0x11-misrouted;
a clean 640-only run plus a concrete later 1024 caller advances
H-later-1024-route. No skip, guard, restore, or other mitigation is authorized.
