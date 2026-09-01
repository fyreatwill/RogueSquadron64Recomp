# NEXT work unit — qualify audio-enabled route for selector writer join

HYPOTHESIS-ID: m5-task-field-writer

Session 3487 qualified retail but both prescribed audio-enabled port retries
crashed before title in `fillSampleStreamRange` at guest PC `0x8000B650`.
The next unit tests whether disabling the audio image makes the route reach
title; only then can the writer join resume.

Competing hypotheses and discriminating outcomes:

- `H-AudioRouteBlocker`: the audio-enabled port route crashes before title; a
  silent route reaches title while the same schema controls fire.
- `H-OtherRouteBlocker`: disabling audio still crashes before title, so the
  current writer join remains unevaluable.
- `H-WriterInputDivergence`: if title becomes reachable, joined writer rows
  differ from retail in source inputs or stored values.
- `H-SharedWriterTransform`: if title becomes reachable and writer rows match,
  but selector operands diverge afterward.

Discriminating measurement: one port run with `ROGUESQ_AUDIO_UCODE=0`, using
the existing positive controls and title phase gate. Title rows select
`H-AudioRouteBlocker`; a pre-title crash selects `H-OtherRouteBlocker` and
leaves the join unevaluable. If title is reached, the existing writer rows
split `H-WriterInputDivergence` from `H-SharedWriterTransform`.

Expected command: run the built port from `build/` with the prescribed
LLE/spin-yield flags, but `ROGUESQ_AUDIO_UCODE=0`, plus
`ROGUESQ_LOG_M5_TASK_WRITER=1` and the existing title phase controls. Use a
SIGKILL watchdog and do not compare sequential animation ordinals. If title
is reached, perform the writer-input/value join in that same iteration.
