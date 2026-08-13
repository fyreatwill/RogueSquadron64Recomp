# NEXT work unit (attribute the reachable VI state writers)

HYPOTHESIS-ID: m3-vi640-transition-writer

Run one batched, phase-gated capture that marks every call to the complete
pending-mask and selector/config writer inventory identified in s807. Do not
instrument a new address class: the source audit found no other absolute
stores. Retain the existing host VI/mode positive control, `[vi-gate]` direct
caller controls, and the oracle whole-RDRAM positive control. Build all writer
markers in one regeneration-safe fixup change and run the arms concurrently
if the recipe requires an oracle comparison.

## Competing hypotheses

- H-state-writer: a reachable scene/render caller writes the 640-only pending
  mask or selector state. Prediction: a writer marker precedes the first
  post-transition 640 row and identifies its caller/value.
- H-missing-1024-writer: the 1024-capable writer exists but its caller or
  overlay route is absent. Prediction: no 1024-producing writer marker fires,
  while only initialization/640 callers fire.
- H-recipe-state: the observed 640 values are legitimate for this port
  recipe. Prediction: writer markers match the expected initialization/640
  sequence and no unexplained state mutation occurs.

## Discriminating measurement

The first writer event after the phase-gated 640 transition, correlated with
its function, argument, pending-mask/selector values, and the next `[vi-gate]`
row, splits the hypotheses. A marker proving only that a writer function is
reachable is insufficient; it must capture the state value and ordering.

## Exact commands

```sh
# Before editing/building, confirm the s807 inventory remains unchanged:
rg -n 'MEM_W\(-0X716C|MEM_W\(-0X7170|MEM_B\(-0X579B|MEM_B\(-0X579C|MEM_B\(-0X579E' ../N64Recomp/RecompiledFuncs/funcs_*.c

# Then use the repository regeneration/fixup flow, build Debug, and run the
# existing phase-gated recipe with positive controls and SIGKILL watchdog.
```

Expected outcomes: a concrete writer/value/order advances H-state-writer; a
missing 1024-capable route advances H-missing-1024-writer; a complete
initialization/640 sequence with no unexplained mutation advances H-recipe-state.
No skip, guard, restore, or other mitigation is authorized by this unit.
