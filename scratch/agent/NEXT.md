# NEXT work unit — trace the upstream producer feeding zero PCM RSP-DMA input

HYPOTHESIS-ID: m5-port-zero-pcm-source

Session 3376's batched source-DMEM/DMA join reached both target phases with
all controls live. Joined stage-2/3 DMA events had zero source-DMEM, zero
post-transform DMEM, and zero destination payload, while retail independently
wrote nonzero primary PCM spans. The next question is which upstream producer
leaves the active RSP input DMEM zero; do not modify output, waits, slots,
status, or consumer dispatch.

Competing hypotheses:

- `H-PortRSPSourceZero`: selected at the observed boundary; the upstream
  producer feeding the RSP input is absent or writes zero.
- `H-PortRSPTransformZero`: the source is nonzero, but the active transform
  emits zero; currently unevaluable because no nonzero source was observed.
- `H-PortDMADestinationMismatch`: the observed zero DMA is not the PCM source
  span consumed by the audio callback; refuted for joined stage-2/3 rows.

Discriminating measurement: enumerate the upstream writes/DMAs that populate
the stage-2/3 RSP input-DMEM windows (`0x6F0` and `0xCB0`) and join them to
the same audio task ordinal/row, with the existing phase, task, PCM, and
image-DMA controls. A producer never populating the window selects the
upstream-input gap; a nonzero producer followed by zero at the stage call
selects `H-PortRSPTransformZero`; a producer targeting a different DMEM
window reopens the DMA/source identity question.

Preparation: identify the existing RSP DMEM write/DMA hooks before building
the instrument. Follow the regeneration order and batch the complete producer
census in one build and one run. Positive controls must include phase,
audio-task/ABI, PCM, image stage/DMA join, title, and hangar markers. Do not
change waits, slots, status handling, consumer dispatch, or PCM writeback.
