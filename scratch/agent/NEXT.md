# NEXT work unit (consumer-scoped E9 epoch join)

HYPOTHESIS-ID: m3-e9-parser-epoch-join

Make one bounded telemetry-only source change that gives the RT64 parser E9
counter an explicit reset epoch at `rs64_rdp_advance_reset`, and reports that
epoch alongside the post-parser count used by `[e9-task-join]`. Keep game logic,
RDP behavior, and mitigation code unchanged. Build once and run the existing
post-sec2 recipe once with all passive breadcrumbs and the positive controls.

Competing hypotheses and the discriminating measurement:

- H-parser-epoch-join: the prior mismatch was a producer/task versus consumer
  epoch error. A keyed row whose parser count is delimited by one parser epoch
  will align with the guest task population.
- H-parser-async-order: the render-thread consumer processes submitted ranges
  after the producer's task callback. The epoch/order trace will show the
  parser reset and consumer records crossing the guest task callback boundary.
- H-parser-filter-remains: even within one consumer epoch, raw-opcode E9
  accounting omits legitimate parser forms. Positive controls will align in
  epoch, but the keyed parser count will still be lower than the aligned guest
  count without a reset/order explanation.

Discriminator: one capture with positive controls (`emit/raw/dispatch/match`),
an explicit parser epoch on reset and join rows, and a reset-to-consumer-to-join
ordering trace. Do not conclude from the old `parser_delta` field alone.

Expected commands: edit the telemetry source; build the Debug target with the
project's documented cmake command; run the existing queued post-sec2 recipe
with passive breadcrumbs; inspect only bounded log slices; update the ledger.
