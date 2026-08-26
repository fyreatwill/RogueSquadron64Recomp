# NEXT work unit (s2406) — disambiguate zero-output joins

HYPOTHESIS-ID: m5-zero-output-identity

## Work unit

Run one ground-truth-first, same-build audit that replaces the repeated
all-zero tuple as the identity key for image stage rows. Diagnostic only: do
not change task data, audio, gate, fallback, dispatch, VI, output behavior, or
the nonzero predicate.

## Competing hypotheses and discriminator

- H-ZeroOutputIsLegitimate: the exact image DMA and zero PCM source/consumer
  rows are ordered for the same stage ordinal and downstream slot/key-on use.
- H-ZeroOutputWriterMissing: the exact stage DMA is followed by a legitimate
  nonzero writer or consumer payload that the port misses.
- H-ZeroOutputConsumerMismatch: exact zero stage/DMA rows are valid, but the
  port's first downstream slot/key-on event does not consume that row.
- H-ZeroOutputRouteInvalid: either arm lacks target activation or target-origin
  controls, making the table unevaluable.

The discriminator is one phase-keyed table keyed first by arm + audio ordinal
and row, then exact generated DMA event/range and destination. Only after that
key is fixed may PCM source/consumer and the first slot/key-on event be joined.
All rows must report event ordering and whether the destination is one of the
retail-controlled windows. A same-ordinal exact zero row with ordered consumer
use selects legitimate zero output; a later exact nonzero writer selects
missing writer; a valid exact row with no matching consumer selects consumer
mismatch; missing arm controls select route-invalid.

## Exact command shape

1. Run the retail oracle first with whole-RDRAM control, title/hangar VI
   controls, and exact windows `0x166450:0x300`, `0x167050:0x300`,
   `0x166D50:0x300`, and `0x1935E0:0x198`.
2. Add the complete bounded ordinal/row-to-DMA table and positive activation
   control in the fixup/runtime instrumentation, then build once with
   `cmake --build build -j2`.
3. Run stub and image concurrently from `build/` with the proven s2403 control
   set, `ROGUESQ_STUB_MISSING_FUNCS=1`, `PROBE_PHASE_WIDTH=1024`, and
   `PROBE_KEYS_FROM_PHASE=1`; use the Start driver, SIGKILL any survivors,
   and preserve logs under `scratch/agent/s2406_zero_output_identity/`.

Expected outcomes: both arms reach target controls and the exact table selects
one hypothesis; otherwise record the failed control and do not interpret a
null. Do not use `ROGUESQ_LOG_ALL`.
