# Next work unit: repair the paired M5 source-producer route

HYPOTHESIS-ID: m5-source-producer-context

The M3 runtime discriminator is closed for this host: do not repeat a
host-only PatchesLib check. Repair the paired retail/port source-producer
capture, keeping guest behavior and all mitigations unchanged.

Competing hypotheses and discriminator:

- H-retail-port-writer-match: the same phase-keyed source writer/context table
  matches between retail and a qualified canonical port hangar run.
- H-port-writer-context-split: both routes reach the phase, but the writer PC,
  source span, or value-producing context differs.
- H-route-invalid: the port does not reach hangar or the retail watch is not
  phase-keyed, so the comparison is unevaluable.

The single discriminating measurement is one rebuilt run containing the full
retail-gated phase-keyed writer/context table and the canonical port arm with
route controls sufficient to reach title 1024 and hangar 512. A qualified
retail/port match selects H-retail-port-writer-match; a qualified split selects
H-port-writer-context-split; either missing phase or missing phase-keyed retail
join selects H-route-invalid. The oracle whole-RDRAM positive control must fire
in the same run.

Use the existing source-producer capture recipe and fix its oracle watch-index
table before trusting post-value rows. Batch all counters in one build/run;
do not alter image, wait, cap, predicate, slot state, guest behavior, or host
writeback.
