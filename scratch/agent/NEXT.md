# NEXT work unit (audit the two VI caller pointer origins)

HYPOTHESIS-ID: m3-vi1024-boot-crash-pivot

Perform one bounded source audit. Trace the two reachable
`initVideoSubsystem` callers at `0x80018378` and `0x80018564` backward to the
definitions and stores that produce `ctx->r5`, and map the observed pointer
values (`0xE0`, `0x1E0`, `0x154`, `0x1C0`) to the caller's register/stack
state. Do not add a probe, guard, or game-logic change.

## Competing hypotheses

- H-pointer-is-guest-structure: the values are legitimate guest addresses
  after the normal host address transform, and the earlier crash was solely
  the probe dereferencing an invalid host translation.
- H-pointer-is-small-offset: the values are small offsets or stale scalar
  values passed as pointers; the pointer-only run survived because the new
  probe no longer consumed them, while the game's downstream use remains
  unsafe or bypassed.
- H-caller-state-stale: the two callers load `ctx->r5` from a stale or
  phase-dependent register/stack slot, and the observed values differ by
  caller timing rather than by a stable argument structure.

## Discriminating measurement

The audit must identify, for each callsite, the exact instruction that sets
`r5`, its source register/stack/global, and whether that source is a guest
address under the runtime's address transform. A concrete guest-structure
base or a scalar/stack-slot origin splits the hypotheses; if the generated
source cannot resolve the origin, report it as unevaluable rather than infer
legitimacy from the clean run.

## Exact commands

```sh
rg -n -C 35 "0x80018378|0x80018564|initVideoSubsystem\(rdram, ctx\)" ../N64Recomp/RecompiledFuncs/funcs_4.c
rg -n -C 12 "ctx->r5|MEM_[BHW](\([^)]*ctx->r5|0x8001A098" ../N64Recomp/RecompiledFuncs/funcs_4.c
rg -n "advanceVideoFrame|initVideoSubsystem" docs/CURRENT-TRUTH.md PORTING-STATE.md | tail -40
```

Use the regenerated source currently under test. No build or run is needed
for this source-only unit.
