# NEXT work unit (s2664) — audit the named retail writer call-sites

HYPOTHESIS-ID: m5-retail-output-writer-attribution

## Work unit

Perform one bounded static call-site audit of the named retail writers from
s2663 (`0x800078EC`, `0x8001E2C0`, and `0x8001FAxx–0x8001FD2C`) against the
companion source/symbols and the port-side generated tree. Identify which
stores are memset/metadata churn versus a plausible PCM or MORT publication
edge, and map caller/ordering evidence to the s2662 port rows. Do not change
port behavior, task fields, writeback, remap, gates, waits, or generated code.

## Competing hypotheses and discriminator

- `H-800078EC-MORT`: the named writer's callers/arguments establish a CPU-MORT
  publication edge matching the secondary span.
- `H-800078EC-utility`: the writer is generic memset/utility activity and does
  not publish the target output.
- `H-Secondary-writer-edge`: one of the other named secondary-span writers is
  the legitimate publication edge.

The discriminator is one call-site table keyed by writer PC with companion
name/body, callers, destination span, value semantics, and ordering relation to
the s2662 port stage/consumer rows. Select an edge only if one row closes all
of those fields; otherwise retain `H-RetailWriterUnresolved`.

## Exact commands

1. Locate the companion and generated definitions/callers with `rg -n
   '800078EC|8001E2C0|8001FA|8001FB|8001FC|8001FD'` in the companion and
   repository trees; inspect only bounded windows around each hit.
2. Build one table including every named writer, its caller chain, and the
   s2662 port row it could explain; use `scratch/agent/s2663_m5_retail_output_writer_attribution/oracle.log`
   for the measured phase/value columns.
3. Select exactly one hypothesis. No behavior change is authorized by this
   audit alone.

## Expected outcomes

- A CPU-MORT caller/argument chain selects `H-800078EC-MORT`.
- A utility body with no publication semantics selects `H-800078EC-utility`.
- A distinct secondary writer with a closed payload/order relation selects
  `H-Secondary-writer-edge`; otherwise retain `H-RetailWriterUnresolved`.
