# NEXT work unit (s2403) — audit exact image-stage nonzero predicate

HYPOTHESIS-ID: m5-image-stage-nonzero-contract

## Work unit

Run one ground-truth-first, same-build audit of the image-stage `nonzero`
predicate. Determine whether the retained zero payloads are a legitimate
output-contract requirement or a capture/reducer artifact. Do not change task
data, audio, gate, fallback, dispatch, VI, output behavior, or mitigation.

## Competing hypotheses and discriminator

- H-StageBytesLegitimatelyZero: the image producer and destination bytes are
  legitimately zero for the captured stage.
- H-StageBytesCaptureMismatch: the producer has nonzero bytes, but the logger
  hashes the wrong DMEM/RDRAM span or joins the wrong destination.
- H-StageBytesWrittenThenCleared: nonzero producer bytes exist briefly and are
  cleared before the current destination snapshot.
- H-StageBytesRouteInvalid: either arm fails the target controls, so no byte
  null is interpretable.

The discriminator is one phase-keyed table joining, in both same-build arms,
the image-stage DMEM source span, generated DMA destination/length, immediate
destination bytes, and a bounded post-stage destination snapshot. The oracle
must arm whole-RDRAM positive control first, then a target-origin control and
the matching physical destination windows. Both port arms must emit lifecycle
activation and target-origin/stage controls. A nonzero source with matching
nonzero destination selects legitimate producer output; nonzero source with
zero destination selects writeback/clear; zero source and destination with
independent exact-window retail activity selects capture mismatch. Missing
route controls selects H-StageBytesRouteInvalid and forbids interpretation.

## Exact command shape

1. Read `docs/F5-UCODE-REFERENCE.md` and the current M5 plan before adding
   any probe. Run the oracle recipe from `tools/oracle/README.md` with the
   whole-RDRAM positive control, title origin `0x00790400`, and exact stage
   destination watches.
2. Build once with `cmake --build build -j2`.
3. Run both concurrent arms from `build/` using the qualified LLE/image route,
   `ROGUESQ_STUB_MISSING_FUNCS=1`, `PROBE_PHASE_WIDTH=1024`,
   `PROBE_KEYS_FROM_PHASE=1`, and the existing stage/identity controls plus
   one bounded exact-byte table.
4. Reduce only target-phase rows. Kill with SIGKILL and preserve logs under
   `scratch/agent/s2403_stage_bytes/`.
