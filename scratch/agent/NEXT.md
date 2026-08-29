# NEXT work unit — upstream VI-mode publication/consumer handoff

HYPOTHESIS-ID: m5-vi-mode-publication-edge

## Single work unit

Use a genuinely new VI-mode publication/consumer edge upstream of
ProducerMark to explain the reproducible port VI-640 stop. Do not repeat the
ProducerMark callsite, selector-byte watch, or M5 audio A/B; do not modify
audio behavior.

## Competing hypotheses

- H-ModeWriter: the port never publishes the VI mode/input that leads to the
  retail target width/origin.
- H-ModeConsumer: publication exists, but the port consumer reads a different
  value or misses the handoff.
- H-Ordering: publication and consume values match, but retrace/message
  ordering differs.
- H-UpstreamElsewhere: this complete handoff matches; move beyond it.

## Discriminating measurement

One phase-keyed table must join independent-retail writer PC/value, port
writer/value, mode record and pending values, consumer entry/value, live VI
width/origin, and the first target-route predicate result. Whole-RDRAM,
retail title/hangar, port AUTOPILOT, and selector-positive controls are
mandatory. The first divergent writer/consumer row selects H-ModeWriter,
H-ModeConsumer, or H-Ordering; matching rows select H-UpstreamElsewhere.
If the port never reaches the target phase, downstream rows are unevaluable.

## Exact commands

1. Inspect the existing oracle VI-mode writer/consumer recipes and port route
   diagnostics; read `tools/oracle/README.md` and do not add a field without a
   corresponding phase/join key and independent retail attribution.
2. Build one Debug target:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`.
3. Run the retail oracle and port capture with
   `PROBE_PHASE_WIDTH=1024`, `PROBE_KEYS_FROM_PHASE=1`, whole-RDRAM positive
   control, and the existing AUTOPILOT/title/hangar schedule. Build all A/B
   arms together and run them concurrently if an A/B is required.
4. Write `scratch/agent/s<session>_m5_vi_mode_publication/AUDIT.md` with
   controls, complete joined rows, selected/refuted hypotheses, and
   unevaluable phases.
