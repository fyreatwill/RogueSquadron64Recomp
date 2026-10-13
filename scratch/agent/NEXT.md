# Next work unit — add the missing A12 second-wait branch witness

HYPOTHESIS-ID: m5-a12-second-wait-witness

The s4766 A/B run reached title and hangar in both arms, but its existing
`[waitmusyx-spin2-arm]` rows are from the producer arm site, not the
`0x8014974C` loop. The second-wait yield branch therefore has no positive
control or return marker yet.

Competing hypotheses and discriminating measurement:

- H-A12-loop-reached: a branch witness fires in both copies; default records
  yield iterations followed by flag-clear/return, while rollback records the
  non-yield path.
- H-A12-route-absent: the new witness is absent despite title/hangar controls,
  so this copy is not reached on the covered route.
- H-A12-wrong-writer: the witness fires, but default records no clear/return
  and the gate remains set or times out.

DISCRIMINATING MEASUREMENT: one rebuilt binary, two same-run phase-gated arms,
with one branch/return witness per `0x8014974C` copy plus existing producer,
task/SP, slot, PCM, and VI controls. Positive controls must include title 1024,
hangar 512, and the witness's own marked-dispatch control; absence of the new
witness is route-unevaluable, not evidence against the de-stub.

Build:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```

Add the witness through the canonical fixer and generated output, rebuild once,
then run the existing phase-gated route twice from `build/`, once with the
default and once with `ROGUESQ_AUDIO_SPIN2_YIELD=0`; kill each process with
SIGKILL. Do not change the writer, force the gate, or revisit callback
cardinality until this A12 result is recorded.
