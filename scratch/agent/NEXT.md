# NEXT work unit (s1150)

HYPOTHESIS-ID: vi-post640-owner-audit

Audit the active post-640 loop owner that continues phase-6 slot dispatch after
the final 640 producer call without entering `freeRenderSubsystemResources`.
Do not repeat the NPC boundary test or add a runtime guard.

Competing hypotheses and discriminator before the work unit:

- H1/known owner: the continuing slot/task path has a statically identifiable
  caller or state predecessor that should invoke the VI selector, but its
  transition condition is false.
- H2/separate owner: the continuing phase-6 path belongs to a separate frame or
  scheduler owner with no selector edge; the missing selector is architectural
  path separation.
- H3/generated omission: the expected owner edge exists in the retail/decomp
  symbol inventory but is absent from generated output or overlay registration.

Discriminating measurement: enumerate all generated callers and state-machine
predecessors of the phase-6 slot-dispatch entry and the task-control E9 producer,
then compare that graph against the companion symbol inventory and overlay
registration. One complete census must classify the owner as known-with-gate,
separate-without-selector, or missing-from-generation. Do not add a marker until
the census identifies a single highest-information edge.

Exact commands:

```sh
rg -n 'slotDispatcherIter|0x8003E8DC|submit.*Task|osViSetMode_recomp|freeRenderSubsystemResources|selectAndApplyViMode' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h src
rg -n 'slotDispatcherIter|freeRenderSubsystemResources|selectAndApplyViMode|0x8003E8DC|0x80018650|0x8001BB6C' /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files /Users/williambuckley/Documents/Tools/rogue_squadron64 2>/dev/null | head -240
rg -n 'slotDispatcherIter|submit_rsp_task|task-control|E9' src lib/N64ModernRuntime /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | head -300
```

Expected outcomes:

- KNOWN-WITH-GATE/H1: a complete generated predecessor chain reaches the
  active owner and exposes one state/condition to audit next.
- SEPARATE-WITHOUT-SELECTOR/H2: slot/E9 activity has a distinct owner graph
  with no selector edge; close the missing-selector theory and pivot to that
  owner's intended VI lifecycle.
- MISSING-FROM-GENERATION/H3: the companion symbols or overlay table contains
  an owner edge absent from generated output; identify the durable regeneration
  input correction before any runtime test.
