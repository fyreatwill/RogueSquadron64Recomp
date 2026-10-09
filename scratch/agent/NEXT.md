# Next work unit (s4417): locate the first port/retail selector-path divergence

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4416's qualified port run passed input, VI, task, and image controls.
It entered exact `0x80029E78` 3 times in title and 2 times in hangar, with no
`0x80029E80` hits. Retail s4414 entered `0x80029E80` in title. The two sources
therefore diverge, but the first divergent caller/input/state is still open.

Competing hypotheses:

- H-divergence-before-selector: port and retail receive different caller,
  input, or state before the selector.
- H-divergence-at-selector-entry: the selector entry differs while its inputs
  match, implying dispatch/control-flow divergence at the boundary.
- H-route-boundary: phase, selector, task, or image controls fail, so the
  cross-source comparison is unevaluable.

Discriminating measurement: one paired port/retail boundary capture with
phase-gated caller, precall, selector input, and state fields, plus VI,
task/image, and input controls. A differing caller/input/state before the
selector selects H-divergence-before-selector; matching fields with only the
entry differing selects H-divergence-at-selector-entry; missing controls
select H-route-boundary.

Exact commands:

1. Reuse the existing selector boundary instrumentation and add no fields
   until the paired caller/input/state table is specified; run the port arm
   and retail arm in the same iteration.
2. Count phase-keyed caller/precall/selector rows and verify input, VI,
   task, and image controls before interpreting any null.

Do not repeat the retail range capture or caller enumeration.
