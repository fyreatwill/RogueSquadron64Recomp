# NEXT work unit (s2663) — attribute retail output-span writers by phase

HYPOTHESIS-ID: m5-retail-output-writer-attribution

## Work unit

Run one oracle-only, phase-gated ground-truth capture that adds writer-PC and
post-store value attribution for both output spans, while retaining the whole-
RDRAM control and title/hangar transitions. Correlate those rows after the run
with the existing s2662 port image/PCM artifact. Do not change port behavior,
task fields, writeback, remap, gates, waits, or generated code.

## Competing hypotheses and discriminator

- `H-RetailWriterIsImageEdge`: a named retail writer in a target phase writes
  the same legitimate destination/payload class as the port image stage.
- `H-RetailWriterIsCpuMortEdge`: a named retail writer instead publishes a
  CPU-side MORT descriptor/sample buffer, independent of image completion.
- `H-RetailWriterIsUnresolved`: writer PCs or values remain mixed/ambiguous, so
  the s2662 destination overlap cannot select an edge.

The discriminator is one table keyed by phase and watch span containing writer
PC, physical address, post-store value/polarity, hit count, and phase bucket.
The whole-RDRAM watch and title/hangar transitions are mandatory controls. A
writer count without phase and value is unevaluable; select an edge only when
the writer, legitimate value, destination class, and ordering can be tied to
the s2662 port row.

## Exact commands

1. Inspect the oracle options: `sed -n '1,180p' tools/oracle/README.md`.
2. Use one oracle invocation from the established driver with
   `--watch-write 0x0:0x800000`, both output-span watches,
   `--pc-hist-watch` for each span, `--pc-hist-phase 0x00790400:1024`,
   `--pc-hist-phase 0x006AB400:512`, and `--post-value-watch` for each span;
   retain the verified Start schedule and `--vi-trace`.
3. Require whole-RDRAM hits, both span watches, both target origins, and the
   oracle execution controls before interpreting any narrow result.
4. Produce the phase/writer/value table and compare it to
   `scratch/agent/s2662_m5_output_publication_boundary_fixed/`; select exactly
   one hypothesis. No behavior change is authorized by this capture alone.

## Expected outcomes

- A phase-matched named writer with legitimate payload and port ordering selects
  `H-RetailWriterIsImageEdge` or `H-RetailWriterIsCpuMortEdge`.
- Mixed writers, zero/ambiguous values, or no ordering selects
  `H-RetailWriterIsUnresolved`; keep all runtime behavior unchanged.
