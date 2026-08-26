# NEXT work unit (s2407) — audit downstream range and slot identity

HYPOTHESIS-ID: m5-downstream-range-identity

## Work unit

Run one ground-truth-first, same-build diagnostic audit of the first same-
identity PCM source/consumer and slot/key-on event after each exact image DMA.
Do not change task data, audio, gate, fallback, dispatch, VI, output behavior,
or the nonzero predicate.

## Competing hypotheses and discriminator

- H-ImageRangeIsConsumer: the image DMA destination is the legitimate
  downstream range, but the PCM/slot reporter is observing a different alias or
  range.
- H-DownstreamWriterMissing: a later legitimate writer populates the
  same-identity consumer range and the current port misses that writer.
- H-ConsumerRangeIsIntentional: the image zero row is an intermediate buffer;
  the same-identity PCM range is the intended consumer input and its slot/key-on
  event follows it.
- H-RouteInvalid: either arm lacks title/hangar target controls.

The discriminator is a phase-keyed table keyed by arm + ordinal + row, with
exact image DMA event/destination, first same-identity PCM source/consumer,
first slot/key-on event, and event ordering. The retail oracle must first pass
whole-RDRAM, title/hangar VI, and the four exact windows. An exact image-range
consumer selects H-ImageRangeIsConsumer; a later same-range writer selects
H-DownstreamWriterMissing; an ordered different-range PCM plus slot/key-on
selects H-ConsumerRangeIsIntentional; missing controls select H-RouteInvalid.

## Exact command shape

1. Run the retail oracle first with `--watch-write 0x0:0x800000` and exact
   windows `0x166450:0x300`, `0x167050:0x300`, `0x166D50:0x300`, and
   `0x1935E0:0x198`, plus title/hangar VI trace.
2. Add the complete bounded downstream table and positive activation control,
   then build once with `cmake --build build -j2`; export submodule patches if
   `lib/` changes.
3. Run validated stub and image arms from `build/` with the repository Start
   driver, `ROGUESQ_STUB_MISSING_FUNCS=1`, `PROBE_PHASE_WIDTH=1024`, and
   `PROBE_KEYS_FROM_PHASE=1`. Preserve logs under
   `scratch/agent/s2407_downstream_range_identity/` and kill survivors with
   SIGKILL.

Do not use `ROGUESQ_LOG_ALL`; both arms must pass target controls before a null
or mismatch is interpreted.
