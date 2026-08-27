# NEXT work unit (s2612) — identify one Factor-5 output-to-PCM edge

HYPOTHESIS-ID: m5-audio-contract-output-edge

## Single work unit

Run one ground-truth-first, phase-gated audit of the image arm's output
writeback/consumer relation selected by s2611. Do not change guest writers,
C88, or audio dispatch. Use the existing `audtask-image-stage`,
`audtask-dma-range`, `audtask-join`, and PCM boundary controls in one Debug
build/run. First arm the oracle whole-RDRAM positive control and require title
and hangar transitions; then run the image arm with AUTOPILOT and
`ROGUESQ_AUDIO_UCODE=1`.

## Competing hypotheses and discriminator

- `H-OutputWritebackGap`: image DMEM/DMA completes, but no legitimate image
  output span is the PCM source/consumer span.
- `H-PCMConsumerJoinGap`: image output overlaps or precedes the PCM span, but
  the consumer/source join loses the relation.
- `H-ZeroPayloadLegitimate`: the image and PCM spans are correctly joined, and
  the sampled zero payload is an actual guest result rather than a missing
  handoff.

The discriminator is a phase-keyed table joining every image completion to its
DMA destination/range, payload nonzero/hash, `audtask-join` source/consumer
matches, and PCM source/consumer address/hash/nonzero fields. A positive image
completion plus a zero PCM row alone is not enough: select the first
hypothesis only when the destination relation is absent, the second when the
relation exists but the join fails, and the third only when both independent
address/hash joins close with zero payload. The oracle whole-RDRAM control and
both port route phases are mandatory.

## Exact checks

1. Run the oracle with `--watch-write 0x0:0x800000`, Rice video, the validated
   Start schedule, and `--vi-trace`; record its positive-control callback and
   title/hangar rows.
2. Run `python3 tools/check_jr_t9_host_return.py` and
   `python3 tools/check_c88_default_store.py`.
3. Build `cmake --build build --config Debug --target RogueSquadron64Recomp`.
4. Run the image arm from `build/` for 90 seconds with `LLE_FORCE=1`,
   `SPIN_YIELD=1`, `LLE_UNGATED=1`, `LLE_SOLO=1`, `M5_C88_VALUE=0`, the full
   existing M5 contract/PCM log set, and the in-process AUTOPILOT route.
   Terminate with SIGKILL and capture under
   `scratch/agent/s2612_m5_output_edge/`.
5. Report title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` rows,
   image completion/DMA destination and payload fields, join closure, PCM
   source/consumer tuples, and crash/abort/missing-function counts.
