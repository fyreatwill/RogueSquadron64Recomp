# NEXT work unit (s2613) — qualify the Factor-5 zero-payload handoff

HYPOTHESIS-ID: m5-audio-contract-output-edge

## Single work unit

Run one ground-truth-first, phase-gated qualification of whether the
zero-valued Factor-5 image DMA spans are legitimate source data or a missing
publication edge. Do not change guest writers, C88, or audio dispatch. Use
the existing image-stage, DMA-range, task-join, and PCM boundary controls in
one Debug run, with the oracle whole-RDRAM control first and both title and
hangar transitions required. Join image-stage destination/hash/nonzero rows
to PCM source/consumer rows by exact physical span and task ordinal; report
the complete/incomplete join table and identify the writer of any intervening
nonzero store before proposing a behavior change.

## Competing hypotheses and discriminator

- `H-PublishedByInterveningWriter`: the image span is scratch/zero by design;
  a named guest writer publishes the legitimate PCM payload before consume.
- `H-MissingImagePublication`: the image span is the intended PCM source, but
  no legitimate writer publishes nonzero data before the consumer.
- `H-JoinAccountingGap`: the image and PCM spans/payloads agree, but task
  ordinal or event ordering prevents the existing join from closing.

The discriminator is a phase-keyed table joining every image completion to its
DMA destination/range, payload hash/nonzero, exact PCM source/consumer span,
intervening guest writer PC/value, and task/event ordering. A zero image row
alone is not enough: select `H-PublishedByInterveningWriter` only with a
named legitimate writer, `H-MissingImagePublication` only when the intended
span has no such writer, and `H-JoinAccountingGap` only when independent
address/hash/order evidence closes the relation. The oracle positive control
and both port route phases are mandatory.

## Exact checks

1. Run the oracle with `--watch-write 0x0:0x800000`, Rice video, the validated
   Start schedule, and `--vi-trace`; record its positive-control callback and
   title/hangar rows.
2. Run `python3 tools/check_jr_t9_host_return.py` and
   `python3 tools/check_c88_default_store.py`.
3. Build `cmake --build build --config Debug --target RogueSquadron64Recomp`.
4. Run the image arm from `build/` for 90 seconds with `LLE_FORCE=1`,
   `SPIN_YIELD=1`, `LLE_UNGATED=1`, `LLE_SOLO=1`, the compiled default C88,
   the full existing M5 contract/PCM log set, and the in-process AUTOPILOT
   route. Do not set `AUTOPILOT_STOP_WIDTH`.
   Terminate with SIGKILL and capture under
   `scratch/agent/s2612_m5_output_edge/`.
5. Report title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` rows,
   image completion/DMA destination and payload fields, join closure, PCM
   source/consumer tuples, and crash/abort/missing-function counts.
