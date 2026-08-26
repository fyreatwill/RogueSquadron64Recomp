# NEXT work unit (s2476) — audit the continuation bridge for the converter tail call

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Context

s2475 proved that the JAL at `0x800155E4` needs the legitimate guest link
`0x800155EC`, but the raw link write fails because that address is the
`traverseSceneGraphRecursive` `after_4` continuation and is not in the host
function map. The next work unit is a static generator/runtime audit, not
another guard or audio change.

## Competing hypotheses

- H-ContinuationMap: the runtime already supports intra-function continuation
  addresses, but this generated callsite omitted the required registration or
  lowering form. One existing working pattern can be copied into the fixup.
- H-HostContinuationOnly: direct named calls intentionally use host `goto`
  continuations, so a guest tail dispatch to `0x800155EC` requires a dedicated
  bridge/stub that restores `after_4` rather than a function-map entry.
- H-WrongTailContract: `convertMat3x4ToN64Mtx` should not dispatch through raw
  `$ra` for this callsite; the retail tail target may be a different mapped
  function or the generated function's return contract is misidentified.

## Discriminating measurement

Build one static table in one pass: enumerate every `LOOKUP_FUNC(ctx->r25)` or
equivalent indirect tail whose source `$ra` is a PC inside its caller, and for
each record caller, link/target address, whether the target is a generated
`after_N` label, and the host lowering used. An existing mapped continuation
selects H-ContinuationMap; only host `after_N` labels select
H-HostContinuationOnly; a target outside both classes selects
H-WrongTailContract. Do not build or run until this table selects one branch.

## Commands

```sh
cd /Users/williambuckley/Documents/Tools/N64Recomp
rg -n 'LOOKUP_FUNC\(ctx->r(25|31|9)\)|after_[0-9]+:|ctx->r31 = 0x8001' RecompiledFuncs --glob 'funcs_*.c' > /tmp/s2476_continuations.txt
rg -n 'get_function|func_map|continuation|after_' ../RogueSquadron64Recomp/lib/N64ModernRuntime/librecomp ../RogueSquadron64Recomp/src
```

Record the complete table in `scratch/agent/s2476_m5_continuation_audit/audit.md`.
No build, runtime patch, audio gate, output remap, task-data change, or guard
is authorized until the table selects a bridge design. The retail oracle is
still required before interpreting any later runtime null.
