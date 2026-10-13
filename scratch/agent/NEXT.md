# Next work unit — validate the A12 second-wait de-stub

HYPOTHESIS-ID: m5-a12-second-wait-yield

The s4765 change makes both `0x8014974C` MusyX wait copies yield by default;
`ROGUESQ_AUDIO_SPIN2_YIELD=0` is the rollback. The build succeeded, but no
runtime result has been claimed.

Competing hypotheses and discriminating measurement:

- H-A12-producer: default yield lets `musyxSynthFrame` clear the gate and the
  waiting function returns; rollback reproduces the old spin boundary.
- H-A12-route-absent: neither arm reaches the second wait in the target phase;
  both are route-invalid and the change is unevaluable.
- H-A12-wrong-writer: default yield reaches the wait but the named producer
  does not clear the gate; the run records a timeout or unchanged gate while
  the rollback remains a spin.

DISCRIMINATING MEASUREMENT: one rebuilt binary, two same-run phase-gated arms,
joining second-wait entry, `musyxSynthFrame` arm/clear, wait return/timeout,
task/SP completion, slot transitions, PCM joins, and VI phase. Positive
controls must include title 1024 and hangar 512 or the arm is route-invalid.

Build:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run the existing phase-gated route twice from `build/`, once with the default
and once with `ROGUESQ_AUDIO_SPIN2_YIELD=0`; kill each process with SIGKILL.
Do not change the writer, force the gate, or revisit callback cardinality
until this A12 result is recorded.
