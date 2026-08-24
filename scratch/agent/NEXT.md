# NEXT work unit (s2238) — port writer/order audit for field348 spans

HYPOTHESIS-ID: m5-audio-image-contract

## Work unit

Add one phase-gated, bounded guest-store attestation for the two exact
physical spans derived from the port image arm's `field348` values, then run
one qualified image-arm capture. The attestation must record the span,
target phase/origin, guest-store width and value summary, writer PC/callsite,
and a monotonic store ordinal so each store can be ordered against the
existing `audtask-image-stage` row. Keep the existing stage/ABI/DMA/PCM
instrumentation and its positive controls in the same build and run.

If the lowest common guest-store hook is under `lib/`, export its submodule
patches with `./submodule-patches/export.sh` in the same iteration. If the
generated-store path needs regeneration, use the documented order
`make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake`; do not hand-edit
generated functions.

## Competing hypotheses and discriminating measurement

- **H-PortNoField348Writer:** ABI, DMA, image-stage, PCM, title, and hangar
  controls fire, but no guest stores target either exact span. The port source
  is never populated; audit the upstream producer next.
- **H-PortWriterThenZero:** controls fire and one or both spans receive
  nonzero guest stores before the matching stage row, but the stage snapshot
  is zero. This selects an overwrite, address-order, or stage-read contract
  defect and requires the writer/order table before any mitigation.
- **H-PortWriterPayloadZero:** controls fire and stores target the spans, but
  the recorded store values and stage snapshots are zero. This selects a
  port-side producer-input/data contract gap rather than a missing store edge.
- **H-PortOriginSplit:** controls fire, but the two target origins differ in
  span hit/nonzero/order behavior. The next analysis remains origin-keyed;
  do not combine the source addresses into one contract.
- **H-PortWriterInstrumentGap:** the existing stage controls fire but the new
  writer census has no positive-control store outside the two spans or cannot
  produce ordered rows. The instrument is unevaluable and must be fixed
  before interpreting exact-span nulls.

The discriminator is one table keyed by
`(phase,width,origin,field348_span,writer_pc,store_ordinal)`, joined to the
stage row's `field348_fnv/field348_nz` and to the store value FNV/nonzero
summary. Positive controls are the whole route, nonzero ABI DMEM change,
DMA completion, image-stage rows, and PCM-boundary rows. A null exact-span
result is valid only if those controls and a writer-hook positive control are
present in the same run.

## Build and run

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_M5_C88_VALUE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_M5_HOST_BOUNDARY=1 ROGUESQ_LOG_PCM_BOUNDARY=1 PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2238_field348_writer 30 12 > /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/agent/s2238_field348_writer_driver.log 2>&1
```

Do not change the image default, task fields, writeback/consumer behavior,
or add a guard. A source-writer attribution must name the writer and retain
the before/after ordering evidence.
