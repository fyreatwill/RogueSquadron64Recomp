# NEXT work unit (parser-consumer ordering trace)

HYPOTHESIS-ID: m3-e9-consumer-ordering

Make one bounded telemetry-only source change that records the parser-consumer
ordering around each LLE task: reset epoch, first
RT64 E9 consumer fetch in that epoch, and the later `[e9-task-join]` row. Keep
game logic, RDP behavior, and mitigation code unchanged. Build once and run
the existing post-sec2 recipe once with all passive breadcrumbs and the
positive controls.

Competing hypotheses and the discriminating measurement:

- H-parser-async-order: the render-thread consumer processes submitted ranges
  after the producer's task callback. The epoch/order trace will show the
  parser reset and consumer records crossing the guest task callback boundary.
- H-parser-filter-remains: even within one consumer epoch, raw-opcode E9
  accounting omits legitimate parser forms. Positive controls will align in
  epoch, but the keyed parser count will still be lower than the aligned guest
  count without a reset/order explanation.
- H-parser-reset-missed: reset timing is not the task boundary; the trace will
  show a reset after task work or a consumer fetch attributed to another epoch.

Discriminator: one capture with positive controls (`emit/raw/dispatch/match`),
keyed reset-to-consumer-to-join ordering trace. Do not conclude from the old
`parser_delta` field alone.

Expected commands: edit the telemetry source; run
`./submodule-patches/export.sh`; build the Debug target with the documented
CMake command; run `zsh scratch/agent/s790_postsec2_reachability.sh` once;
inspect only bounded log slices; update the ledger. Do not run this unit during
a future maintenance iteration.
