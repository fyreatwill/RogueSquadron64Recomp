# NEXT work unit (s2483) — trace the scheduler task handoff after SP receive

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Use the completed s2481 capture plus the generated tree to trace the pending
task pointer loaded after `spTaskSchedulerThread` receives the fixed SP event.
Identify the first generated task/slot/voice/PCM/output field consumer and
determine whether its key joins the image task's DMA identity or is a distinct
later identity. This is one bounded provenance audit; do not change code, add
a runtime API, add a NULL guard, or remap audio/output.

## Competing hypotheses

- H-ImageTaskHandoff: the pending task pointer is the image task and its first
  generated consumer retains the image DMA identity.
- H-LaterTaskHandoff: the scheduler loads a distinct later task/slot identity,
  so the image identity is not retained after the receive.
- H-UnresolvedHandoff: the static tree cannot identify the pending-task writer
  or first consumer; no output remap is justified.

## Discriminator

Produce a complete path from the target `guest-receive` row through the
pending-task writer, `osSpTaskLoad`, and the first generated consumer. Join
the task/consumer key to the target image DMA key or to a distinct later
identity. A direct image join selects H-ImageTaskHandoff; a distinct later
task/slot/voice/PCM key selects H-LaterTaskHandoff; an incomplete path selects
H-UnresolvedHandoff. The passed positive controls are recorded in
`scratch/agent/s2481_m5_runtime_sp_lifecycle/audit.md`.

## Exact commands

Build is not needed. From the repo root:

```sh
rg -n '0x8011A420|0x80128C70|guest-receive|sp-complete|audio-route|audtask-join' \
  scratch/agent/soak_results/s2481_runtime_sp_lifecycle/run.log | tail -160
rg -n '0x8011A420|0x80128C70|0x801372D8|osSpTaskLoad|osSpTaskStartGo' \
  ../N64Recomp/RecompiledFuncs src lib/N64ModernRuntime | head -260
```
