# NEXT work unit — M5 VI-mode publication edge

HYPOTHESIS-ID: m5-vi-mode-publication-edge

## Single work unit

Use a genuinely new upstream VI-mode publication/consumer edge to explain
the reproducible pre-title VI-640 stop. ProducerMark is present at the
dominant port caller, so do not repeat its callsite or the selector-byte
watch, and do not modify audio.

## Competing hypotheses

- H-ModeWriter: the port never publishes the VI mode/input that would lead to
  target width/origin, while retail does.
- H-ModeConsumer: the mode publication exists, but the port consumer reads a
  different value or misses the handoff.
- H-Ordering: publication and consume values match, but retrace/message
  ordering differs.
- H-UpstreamElsewhere: the complete mode table matches; move beyond this edge.

## Discriminating measurement

One phase-keyed table must join retail and port VI-mode writer input,
mode-record/pending values, consumer entry/value, live VI width/origin, and
the first target-route predicate result. Whole-RDRAM, title/hangar, AUTOPILOT,
and selector-positive controls are required. The first divergent row selects
H-ModeWriter, H-ModeConsumer, H-Ordering, or H-UpstreamElsewhere; missing
target phase makes downstream rows unevaluable.

## Exact commands

1. Inspect existing retail VI-mode writer/consumer oracle recipes and port
   route diagnostics; do not add a field without a corresponding join key.
2. Build one Debug `RogueSquadron64Recomp` target carrying the complete table.
3. Run retail and port with `PROBE_PHASE_WIDTH=1024`,
   `PROBE_KEYS_FROM_PHASE=1`, whole-RDRAM positive control, and the existing
   AUTOPILOT/title/hangar schedule.
4. Write `scratch/agent/s<session>_m5_vi_mode_publication/AUDIT.md` with all
   rows, controls, selected/refuted hypotheses, and unevaluable phases.
