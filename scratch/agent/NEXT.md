# NEXT work unit (s2514) — resolve image-stage/DMA payload attribution

HYPOTHESIS-ID: m5-rsp-image-payload-validation

## Context

s2513 selected the RSP/image payload path: image ordinal 606 had nonzero
stage-2 output at `0x168B50` matching a PCM source/consumer pair, with no
guest CPU writer. The lower-level image-DMA join nevertheless reported
`nz=0`, so the exact event attribution is unresolved.

## Single work unit

Perform one bounded static/runtime attribution audit of the stage-2 DMA
observer. Trace the exact `rs64_m5_pcm_writer_dma` call and its
`audtask-image-dma-join` publication, then determine whether the nonzero
stage-row payload at `0x168B50` is the same transfer or a later overwrite.
Use the existing s2513 log and source paths first; if a code-level mismatch
is found, make one bounded instrumentation fix and rebuild. No mitigation or
audio behavior change is authorized.

## Competing hypotheses and discriminator

- `H-same-dma`: stage-row and DMA-join payload fingerprints identify one RSP
  transfer at the same destination and event.
- `H-later-overwrite`: the stage row is a later-memory snapshot and the DMA
  observer saw a different zero payload.
- `H-observer-contract`: the DMA observer drops or mislabels nonzero metadata.

The discriminator is one phase-scoped table keyed by image ordinal and
destination containing stage event, DMA event, stage/DMA FNV and nonzero count,
and first matching PCM source/consumer event. Same-event identity selects
`H-same-dma`; differing event or payload selects `H-later-overwrite`; a
reproducible metadata mismatch with source confirmation selects
`H-observer-contract`.

## Exact commands

```sh
rg -n "rs64_m5_pcm_writer_dma|audtask-image-dma-join|rs64_audio_join_image_dma" \
  src/main/main.cpp lib/N64ModernRuntime/librecomp/src/rsp.cpp
grep -a -E '^\[(audtask-image-stage-row|audtask-image-dma-join|pcm-boundary-(source|consumer))\]' \
  scratch/agent/s2513_m5_payload_writer/pair-image/run.log | grep -E '168B50|ordinal=606'
```

Do not infer a writer from a missing DMA row; preserve the existing positive
controls and phase gates if a follow-up capture is needed.

This is iteration 1 on slug `m5-rsp-image-payload-validation`. If the DMA
event cannot be joined after one audit, stop adding fields and pivot to the
next M5 de-stubbing step with the mismatch recorded as an observer-contract
limitation.
