# NEXT work unit (s2479) — audit containing-task completion after the bridge

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Perform one bounded static audit of the generated Factor 5 image-task
completion path implicated by the s2478 target rows. Start from the existing
`break_pc=0x1328` and the image-arm task/join logging sites; enumerate every
generated function and branch that can publish task completion, return SP
status, or hand off output after the two image DMAs. Do not change code, add a
runtime API, add a NULL guard, or remap audio/output in this unit.

## Competing hypotheses

- H-ContainingTaskGenerated: the completion edge is present in generated code
  but the image task exits before reaching it; a concrete missing/conditional
  edge can be named statically.
- H-ContainingTaskRuntime: completion is published by a runtime callback or
  scheduler path outside the generated tree.
- H-ImageArmContract: `break_pc=0x1328` is a legitimate task exit before any
  completion publication, so the missing row is an image-arm contract gap
  rather than a lost continuation.

## Discriminator

The audit must produce a complete table of completion writers/edges, their
generated or runtime ownership, and whether each is reachable after
`break_pc=0x1328`. A reachable generated edge selects
H-ContainingTaskGenerated; only runtime-owned publication selects
H-ContainingTaskRuntime; an explicit terminal image-task contract selects
H-ImageArmContract. An incomplete table is not a result and must not trigger a
code change.

## Exact command

Use the s2478 capture as the dynamic anchor, then run:

```sh
grep -n -E 'break_pc=0x1328|task_complete|output_pcm|audtask-(image-join|join)' \
  scratch/agent/s2478_m5_continuation_bridge_validation/image.log | tail -80
rg -n -S 'break_pc|task_complete|output_pcm|audtask-image|RspExitReason::Broke|SP.*status|audio.*complete' \
  src lib RecompiledFuncs ../N64Recomp/fixup_game_funcs.py
```

Ground truth is not needed for this static audit because no new runtime
instrument or claim about retail memory ownership is being introduced. If the
table shows a missing dynamic edge, the next unit must obtain retail controls
before instrumenting it.
