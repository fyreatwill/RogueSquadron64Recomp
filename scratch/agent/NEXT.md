# Next work unit (s4418): qualify the port selector caller/precall witness

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4417's paired run passed retail whole-RDRAM/VI/task controls and port
input/VI/selector/task controls. Retail showed `0x8008EE84 -> 0x80029E80`,
while port selector/input rows were live but port caller/precall rows were
absent. The comparison is therefore unevaluable until the port witnesses are
proven to cover the actual generated edge.

Competing hypotheses:

- H-witness-mismatch: the port caller/precall probes are attached to inactive
  generated sites or stale patch markers.
- H-divergence-before-selector: the live port caller/input/state differs from
  retail before the selector.
- H-divergence-at-selector-entry: caller/input/state match while only the
  selector entry differs.
- H-route-boundary: phase, selector, task, or image controls fail, so the
  cross-source comparison is unevaluable.

Discriminating measurement: a complete static census of the generated
functions containing `rs64_m5_selector_caller` and
`rs64_m5_selector_precall`, joined to the actual `0x80029E78` callsite and
patch markers. Live marker at the selector edge selects H-witness-mismatch;
live marker plus a paired row selects one of the two guest-divergence arms;
missing phase/selector/input/task controls selects H-route-boundary.

Exact commands:

1. `rg -n -C 4 'rs64_m5_selector_(caller|precall)' RecompiledFuncs tools` and
   enumerate each generated function, guest PC, and marker.
2. Compare that census with the selector callsite around `0x80029E78` and
   identify whether the zero caller/precall rows are a dead probe edge or a
   real missing path. Do not add another runtime field until this census
   selects which edge is live.

Do not repeat the retail range capture or caller enumeration.
