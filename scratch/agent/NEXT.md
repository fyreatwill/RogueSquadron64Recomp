# Resume next work unit — measure VI-retrace callback dispatch cardinality

HYPOTHESIS-ID: m5-callback-dispatch-cardinality

Checkpoint status: the s4768 retry did not rerun the experiment and produced no
new runtime artifact. Resume from the existing s4767 evidence: the wait copy
was positively reached with gate 0, the shutdown copy was absent, and no A12
writer or gate change was selected. The next M5 unit is the callback-dispatch
question left open by s4764.

Competing hypotheses and discriminating measurement:

- H-dispatch-all: the marked VI-retrace walker emits two invocation ordinals
  for the duplicate live callback slots.
- H-first-live-slot: it emits exactly one ordinal for the first live slot.
- H-stale-source: synth entries continue after the marked table dispatch is
  empty, without a corresponding live-slot ordinal.

DISCRIMINATING MEASUREMENT: one rebuilt binary and one phase-gated default-B40
title/hangar capture, with one bounded invocation ordinal per callback-table
slot in the actual VI-retrace dispatcher, plus table registration/
deregistration, synth-entry, title 1024, hangar 512, and no-crash controls.
The marked dispatcher row must fire before interpreting zero ordinals; a
missing target phase is route-invalid, not evidence for a dispatcher model.

Build:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Add the ordinal witness through the canonical fixer and generated output,
rebuild once, then run the existing default-B40 phase-gated route from
`build/`; kill the process with SIGKILL. Do not change first-match
deregistration or add a guard. The prior retry did not add this witness, so
the next iteration must do the instrumentation before running the command.
