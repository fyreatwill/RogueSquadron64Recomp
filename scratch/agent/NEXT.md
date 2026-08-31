# NEXT work unit — qualify initN64RspMixer caller arguments

HYPOTHESIS-ID: m5-port-setup-state-producer

Session 3425 selected `H-UpstreamCallerContract`: retail enters
`allocateSongChannelArray` from `0x80091934` with `a1=0x561F`, while both
port arms enter it with `a1=0x5622`; the port divergence exists before the
observed `0x8008F2A0` malloc-return edge.

Competing hypotheses and the single discriminating measurement:

- `H-CallerPassesPortCount`: `initN64RspMixer` supplies `a1=0x5622`; the
  mismatch is upstream of `allocateSongChannelArray`.
- `H-CalleeMutatesCount`: the caller supplies retail `a1=0x561F`, but the
  callee-entry witness differs, exposing a dispatch/wrapper boundary.
- `H-CallerUnevaluable`: caller or callee controls disappear despite the
  whole-RDRAM and phase controls, so no contract conclusion is allowed.

First run the retail oracle with whole-RDRAM control and
`--watch-pc 0x80091934,0x8008F0A0`, phase-gated to title/hangar. Add one
regeneration-safe port witness at `initN64RspMixer` entry/call and run the
existing fresh-build silent/image pair. Keep title 1024, hangar 512, audio
ABI/DMA, image-stage, and PCM controls. If the caller has `a1=0x5622`, select
`H-CallerPassesPortCount`; if it has `0x561F` but the callee has `0x5622`,
select `H-CalleeMutatesCount`; if controls disappear, select
`H-CallerUnevaluable`. Do not change waits, slots, dispatch, clear behavior,
or PCM writeback.
