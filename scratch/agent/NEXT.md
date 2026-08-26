# NEXT work unit (s2466) — locate the zero-producing converter edge

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Context

s2465's fixed shared-resolver capture selected H-TargetBoundary: the first
null target occurs in `convertMat3x4ToN64Mtx`, with
`traverseSceneGraphRecursive` as its caller. The same hook resolved the
`0x8009123C` indirect positive control in phase 4. The remaining question is
which converter input or lowered indirect edge supplies zero.

## Work unit

Perform one static, bounded audit of the complete generated
`convertMat3x4ToN64Mtx` body and its direct caller. Enumerate every call,
`LOOKUP_FUNC`, register load, and continuation around the converter entry,
then identify the exact register/value that reaches the shared resolver on
the null event. If static inspection cannot name it, add one phase-gated
capture at the converter's indirect-call boundary in the fixup script, with
the existing shared-resolver positive control retained. No guard, stub,
dispatch, callback, or audio behavior change.

## Competing hypotheses and discriminator

- H-ConverterRegisterZero: the converter's generated indirect-call register
  is explicitly zeroed or loaded from a zero field before `LOOKUP_FUNC`.
- H-CallerContextZero: the converter receives a bad matrix/context pointer
  from `traverseSceneGraphRecursive`, and the converter's indirect target is
  only accidentally zero at the callee boundary.
- H-UnseenLoweringEdge: the generated body has a call/continuation lowering
  edge not visible in the first text census, producing the zero after the
  converter's normal setup.

The discriminator is one ordered table of all converter indirect-call
sites/register sources plus the fixed-run null tuple: a statically proven
zero source at the same site selects H-ConverterRegisterZero; a nonzero
converter input paired with a zero at resolver entry selects
H-CallerContextZero; no complete static source or boundary tuple selects
H-UnseenLoweringEdge. A missing positive-control row invalidates the run.

## Exact commands

1. Grep the generated converter and `traverseSceneGraphRecursive` bodies by
   function header and read bounded windows around every call, `jalr`,
   `LOOKUP_FUNC`, register write, and `after_*` continuation.
2. Build one fixup/static-audit artifact only if the complete text census
   cannot establish the source; retain `ROGUESQ_LOG_M5_PRETARGET=1` and its
   phase-4 positive-control row.
3. Run the qualified route from `build/` for 30 seconds, SIGKILLing the game
   if it remains active, and write
   `scratch/agent/s2466_m5_zero_source/audit.md`.
