# NEXT work unit (s2482) — trace the post-receive image-task consumer

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Use the completed s2481 capture plus the generated tree to identify the first
game-side consumer after the target SP receive, and determine whether it joins
the image task's DMA identity or a later slot/voice/PCM/output identity. This
is one bounded provenance audit; do not change code, add a runtime API, add a
NULL guard, or remap audio/output.

## Competing hypotheses

- H-ImageConsumer: the first post-receive generated consumer retains the image
  task identity and leads to a legitimate output contract.
- H-LaterConsumer: the receive returns into a generic scheduler/slot path and
  the image identity is not retained at the first consumer boundary.
- H-UnresolvedConsumer: the capture/static tree cannot join the receive to a
  consumer without a new instrument; no output remap is justified.

## Discriminator

Produce a complete caller/return path from the target `guest-receive` row
through the generated consumer and join its data key to the target image-task
key, a slot/voice/PCM key, or neither. A direct joined image identity selects
H-ImageConsumer; a generic handoff with a distinct later identity selects
H-LaterConsumer; an incomplete path selects H-UnresolvedConsumer. The passed
positive controls are recorded in
`scratch/agent/s2481_m5_runtime_sp_lifecycle/audit.md`.

## Exact commands

Build is not needed. From the repo root:

```sh
rg -n '0x8011A420|0x80128C70|guest-receive|sp-complete|audio-route|audtask-join' \
  scratch/agent/soak_results/s2481_runtime_sp_lifecycle/run.log | tail -160
rg -n '0x8011A420|0x80128C70|osRecvMesg|guest-receive|sp_complete' \
  RecompiledFuncs src lib/N64ModernRuntime | head -240
```
