# NEXT work unit (s2614) — retail writer attribution for the PCM handoff

HYPOTHESIS-ID: m5-audio-contract-output-edge

## Single work unit

Run one ground-truth-first, phase-gated retail writer attribution for the
PCM spans observed in s2613. Do not change guest writers, C88, or audio
dispatch. Arm the oracle whole-RDRAM positive control first, then add narrow
physical watches for the title/hangar PCM ring spans and retain the validated
Start schedule and both VI phases. In the port, retain the image-stage,
DMA-range, task-join, PCM source/consumer, and host/guest writer controls in
one Debug run. Join retail writer PCs/values and port task/event ordering by
physical span; report whether a named legitimate writer publishes nonzero
PCM before consume.

## Competing hypotheses and discriminator

- `H-RetailLegitimateWriter`: retail has a named writer for the sampled PCM
  spans before consume; the port's zero host writer is a separate edge.
- `H-PortPublicationGap`: retail writes the spans, but the port has no matching
  legitimate publication edge before its consumer.
- `H-JoinAccountingGap`: retail and port spans/payloads agree, but event/task
  ordering prevents the existing join from closing.

The discriminator is a phase-keyed table containing whole-RDRAM control,
retail narrow-watch PC/value/timing rows, port image DMA destination/source
hashes, guest/host writer rows, exact PCM source/consumer spans, and task/event
ordering. Select a writer hypothesis only with a named legitimate retail PC
and value; select a port gap only if the corresponding port edge is absent;
select an accounting gap only when independent address/hash/order evidence
closes the relation. Both port phases and the oracle control are mandatory.

## Exact checks

1. Run the oracle with `--watch-write 0x0:0x800000` plus narrow watches for
   `0x166450:0x169450` and `0x1798B0:0x179A48`, Rice video, the validated Start
   schedule, and `--vi-trace`; record the positive-control callback, writer
   PCs/values, and title/hangar rows.
2. Run `python3 tools/check_jr_t9_host_return.py` and
   `python3 tools/check_c88_default_store.py`.
3. Build `cmake --build build --config Debug --target RogueSquadron64Recomp`.
4. Run the image arm from `build/` for 90 seconds with `LLE_FORCE=1`,
   `SPIN_YIELD=1`, `LLE_UNGATED=1`, `LLE_SOLO=1`, the compiled default C88,
   the full existing M5 contract/PCM log set, and in-process AUTOPILOT. Do
   not set `AUTOPILOT_STOP_WIDTH`. Terminate with SIGKILL and capture under
   `scratch/agent/s2614_m5_pcm_writer/`.
5. Report title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` rows,
   retail writer attribution, image completion/DMA destination and payload
   fields, join closure, PCM source/consumer tuples, and crash/abort/missing-
   function counts.
