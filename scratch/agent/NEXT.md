# NEXT work unit (s927)

HYPOTHESIS-ID: m3-run-voice-lattice-class

Audit the complete `runVoiceLatticeFilter` idiom at `0x8009D980`, including
all generated callers, record/table bounds, helper calls, and termination.
Source-only; do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-lattice-unclassified: a caller or helper uses unchecked lattice,
  coefficient, state, or output pointers/lengths.
- H-lattice-classified: all callers share one fixed lattice/filter shape and
  every local walk is bounded, with only dynamic value legitimacy open.
- H-lattice-shape-mismatch: one caller uses a distinct lattice/filter
  contract; record the exact split and stop.

Discriminating measurement: enumerate every memory access, indirect/direct
helper edge, caller argument setup, and loop/termination condition in the
generated body; cross-check `main_overlay.txt` and companion symbols. Any
omitted access, unsafe bound, unbounded control, or shape split rejects full
classification.

Exact commands: inspect `funcs_27.c` around `0x8009D980`, `rg` every
`runVoiceLatticeFilter` reference and helper call, then inspect the matching
`main_overlay.txt` entry. No game build or soak is planned.
