# NEXT work unit (s2404) — identify zero-output writer/consumer contract

HYPOTHESIS-ID: m5-zero-output-contract

## Work unit

Run one ground-truth-first, same-build audit of the zero-valued image output
after s2403 closed the source/destination span mismatch for retained stage
rows. Do not change task data, audio, gate, fallback, dispatch, VI, output
behavior, or mitigation.

## Competing hypotheses and discriminator

- H-ZeroOutputIsLegitimate: the image task's zero source and destination are
  the intended contract for this task/phase, and downstream consumers treat
  zero as a valid payload.
- H-ZeroOutputWriterMissing: a legitimate writer should populate the image
  source or destination after the captured stage edge, but the port misses it.
- H-ZeroOutputConsumerMismatch: the zero payload is valid, but the port joins
  or routes the downstream consumer incorrectly.
- H-ZeroOutputRouteInvalid: either same-build arm fails target activation or
  phase controls, so no zero-output conclusion is interpretable.

The discriminator is one phase-keyed table joining each retained zero stage
row to: image completion, every generated DMA range, the exact destination
write watcher, PCM source/consumer rows, and the first downstream slot/key-on
consumer event. The retail oracle must first pass whole-RDRAM, title, hangar,
and exact destination-window writer controls. Both port arms must pass
activation and target-origin controls. A zero stage with no retail-equivalent
writer but ordered consumer use selects legitimate zero output; a later
nonzero writer selects missing writer; a valid zero stage with consumer rows
but no matching port consumer selects consumer mismatch.

## Exact command shape

1. Read `docs/F5-UCODE-REFERENCE.md`, `docs/M5-AUDIO-PLAN.md`, and
   `tools/oracle/README.md`. Run the retail oracle with whole-RDRAM first,
   title/hangar VI controls, and exact windows `0x166450:0x300`,
   `0x167050:0x300`, `0x166D50:0x300`, and `0x1935E0:0x198`.
2. Build once with `cmake --build build -j2` after adding only the complete
   bounded join table and its activation control.
3. Run stub and image concurrently from `build/` using the qualified
   LLE/image route, `ROGUESQ_STUB_MISSING_FUNCS=1`,
   `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, and all existing
   task/PCM/identity controls. Kill with SIGKILL and preserve logs under
   `scratch/agent/s2404_zero_output_contract/`.
