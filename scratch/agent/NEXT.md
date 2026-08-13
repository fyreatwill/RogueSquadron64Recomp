# NEXT work unit (s925)

HYPOTHESIS-ID: m3-filter-voice-block-class

Audit the complete `filterVoiceSampleBlock` idiom at `0x8009D7D0`, including
all generated callers, input/output bounds, helper calls, and termination.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-filter-voice-unclassified: a filter caller or helper uses an unchecked
  sample-block pointer/length or an incompatible record shape.
- H-filter-voice-classified: all callers pass the same fixed block shape and
  the helper has bounded control with only dynamic value legitimacy open.
- H-filter-voice-shape-mismatch: one caller uses a distinct sample/filter
  contract; record the exact split and stop.

Discriminating measurement: complete memory-access, helper-call, caller-
argument, and loop/termination tables, cross-checked against companion
symbols. Any omitted access, unsafe bound, unbounded control, or shape split
rejects full classification.

Exact commands: inspect `funcs_27.c` around `0x8009D7D0`, `rg` every
`filterVoiceSampleBlock` reference and helper call, then inspect the matching
`main_overlay.txt` entry. No game build or soak is planned.
