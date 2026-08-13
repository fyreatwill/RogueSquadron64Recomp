# NEXT work unit (s926)

HYPOTHESIS-ID: m3-apply-voice-delay-class

Audit the complete `applyVoiceDelayFilter` idiom at `0x8009D8C4`, including
all generated callers, record/table bounds, helper calls, and termination.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-apply-delay-unclassified: a caller or helper uses unchecked channel,
  delay-buffer, or output pointers/lengths.
- H-apply-delay-classified: all callers share one fixed channel/filter shape
  and every local walk is bounded, with only dynamic value legitimacy open.
- H-apply-delay-shape-mismatch: one caller uses a distinct delay/filter
  contract; record the exact split and stop.

Discriminating measurement: enumerate every memory access, indirect/direct
helper edge, caller argument setup, and loop/termination condition in the
generated body; cross-check `main_overlay.txt` and companion symbols. Any
omitted access, unsafe bound, unbounded control, or shape split rejects full
classification.

Exact commands: inspect `funcs_27.c` around `0x8009D8C4`, `rg` every
`applyVoiceDelayFilter` reference and helper call, then inspect the matching
`main_overlay.txt` entry. No game build or soak is planned.
