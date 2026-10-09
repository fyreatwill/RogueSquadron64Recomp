# Next work unit (s4359): locate the retail task-consumer PC

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4358 oracle build repaired the join boundary: whole-RDRAM control fired,
the hangar phase was reached, and 512 bounded C904/C950 witness rows were
captured. The presumed `0x80033FCC` task watch still produced zero rows, so the
new C904/C950-to-task join produced zero matches. The port arm remained live
through hangar with task/ABI and image-DMA rows.

Competing hypotheses:

- H-consumer-nearby: the retail task handoff is a nearby PC around
  `0x80033FCC`, and a range census will find valid type-2 task rows that can be
  joined to the C904/C950 phase rows.
- H-consumer-other-overlay: the handoff is outside that presumed local range;
  the local census is empty despite qualified C904/C950 and whole-RDRAM controls.
- H-pre-filter-origin: a live nearby task row appears, but its source fields
  already disagree with the C904/C950 input/selected fields before the consumer.

Discriminating measurement: build one bounded `--watch-pc-range` census for
`0x80033C00:0x80034100`, with exact PC, type, task pointer, and task fields for
every phase-gated execution, while retaining `--c904-witness`, the new
`--c904-task-join`, whole-RDRAM, title/hangar VI controls, and the port ABI/DMA
rows in the same capture. Nearby valid rows select H-consumer-nearby; no rows
select H-consumer-other-overlay/instrument boundary; source disagreement in a
joined row selects H-pre-filter-origin.

Exact pre-build ground-truth check: run the existing whole-RDRAM positive
control and C904/C950 witness watches first; accept the range result only if
the control and both title/hangar phase witnesses fire in that same capture.

Expected commands: extend `tools/oracle/rs64_oracle.c` with one bounded task
range option, run `./tools/oracle/build.sh`, then repeat the s4358 paired
capture from `scratch/agent/s4358_m5_selector_join/` with SIGKILL watchdogs.
