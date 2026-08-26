# s2480 — runtime SP lifecycle capture

## Run

The qualified image-arm environment was launched from `build/` for the
prescribed 180-second bounded capture with `ROGUESQ_AUDIO_UCODE=1`,
`ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, `ROGUESQ_LLE_SOLO=1`, and
the M5, event-wiring, and audio-return logs enabled. The output is
`scratch/agent/soak_results/s2480_runtime_sp_lifecycle/run.log`.

## Evidence

- Positive control: `[event-wiring] register kind=SP event=4 mq=0x8011A420
  msg=0x80128C70` fired once.
- Positive control: `[event-wiring] complete kind=SP mq=0x8011A420
  msg=0x80128C70` fired 64 times.
- The run emitted repeated `[audtask-dispatch] ... real_ucode=1` rows, but
  emitted zero `audio-route`, `audtask-abi`, or target image-task lifecycle
  rows.
- The run reached the title/640-width route and never reached the target
  image-arm phase. No target-route SP publication/consumption pairing can be
  inferred from the early SP rows because their task identity is not logged by
  this capture.

## Verdict

The event-wiring control proves that registration and runtime SP publication
are live in this process, but the target-route discriminator is unevaluable.
This run selects none of `H-SPConsumed`, `H-SPPublishedUnconsumed`, or
`H-SPRegistrationGap`. The next capture must use the known eleven-Start
`tools/probe.sh` route so the image task is reached before interpreting its
SP lifecycle.
