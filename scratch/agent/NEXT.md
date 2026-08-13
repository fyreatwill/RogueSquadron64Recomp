# NEXT work unit (trace the frame-state value supplied as VI argument a1)

HYPOTHESIS-ID: m3-vi-argument-state-origin

Perform one bounded source audit. Trace `runVideoFrameTick`'s callers and the
frame-structure value loaded at offset `0x4` that becomes `advanceVideoFrame`
argument `a1`, and identify the stores or ROM/data initialization that produce
that field. Do not add a probe, guard, or game-logic change.

## Competing hypotheses

- H-frame-field-legitimate: offset `0x4` is a documented/intentional scalar
  mode or video-state field, and the observed values are valid inputs.
- H-frame-field-corrupt: the field is populated by an invalid/stale writer or
  malformed initialization, so the small values are not legitimate state.
- H-frame-field-unresolved: the generated tree cannot identify the producer or
  the frame object, leaving the value's meaning unevaluable.

## Discriminating measurement

The audit must identify every `runVideoFrameTick` caller, the frame object
passed as `a0`, and every writer/initializer for its `+0x4` halfword. A
documented mode/state writer splits legitimate from corrupt; an unresolved
object or writer remains unevaluable. Do not infer legitimacy from the clean
run.

## Exact commands

```sh
rg -n -C 18 "runVideoFrameTick\(rdram, ctx\)|0x80001354|lhu +\$s6, 0x4\(\$s3\)" ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -C 12 "0x4\(\$s3\)|runVideoFrameTick|thread3_video_handle" ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n "0x8001[0-9A-Fa-f]{4}|video.*frame|runVideoFrameTick" syms docs PORTING-STATE.md | tail -80
```

Use the regenerated source currently under test. No build or run is needed
for this source-only unit.
