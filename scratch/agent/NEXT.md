# NEXT work unit (s2484) — capture the scheduler event payload/task identity

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Use one qualified eleven-Start image-arm capture to record the event object's
`0x80128C70 + 4` payload and the task pointer/data identity passed by the
`spTaskSchedulerThread` event-type-1 path to `osSpTaskLoad`/`osSpTaskStartGo`.
Join that value to the existing image-stage DMA key in the same run. Do not
change scheduler behavior, add a NULL guard, or remap audio/output.

## Competing hypotheses

- H-ImageTaskHandoff: the event `+4` payload/task pointer equals the image
  task identity and reaches the first SP consumer.
- H-LaterTaskHandoff: the event `+4` payload/task pointer is a distinct later
  task identity, not the image task's DMA-associated identity.
- H-UnresolvedHandoff: the payload or task identity is absent/ambiguous even
  though the scheduler path is observed.

## Discriminator

The same-run positive controls must include the target SP registration and
guest receive, plus at least one image-stage DMA row. A payload/task value that
equals the image task key selects H-ImageTaskHandoff; a non-equal stable task
key selects H-LaterTaskHandoff; missing or non-joinable values select
H-UnresolvedHandoff. The passed controls are recorded in
`scratch/agent/s2481_m5_runtime_sp_lifecycle/audit.md`.

## Exact commands

Before building, ask the retail oracle for the corresponding event-object/task
payload ground truth and arm its positive control. Then batch the port capture
in one build/run using the existing probe/fixup path; do not run separate
counter builds. Static references are:

```sh
rg -n '0x8011A420|0x80128C70|0x80128D38|osSpTaskLoad|osSpTaskStartGo' \
  ../N64Recomp/RecompiledFuncs src lib/N64ModernRuntime | head -260
```
