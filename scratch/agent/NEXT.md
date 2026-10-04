# Next work unit: qualify the title host audio sink

HYPOTHESIS-ID: m5-title-audio-host-sink

Session 4063 selected H2 for the prior endpoint discriminator: retail title
AI output was nonzero, and the qualified declared-real port produced nonzero
PCM at `osAiSetNextBuffer` and at `queue_samples`. The next bounded unit is to
qualify whether the host SDL queue accepts that PCM.

Competing hypotheses:

- Hsink: `SDL_OpenAudioDevice` failed (`device=0`) or title queue calls report
  zero `call_delta`/no queue growth despite nonzero consumer PCM. This selects
  a host sink defect and the next step is the device/backend setup.
- Hqueue: title queue calls report positive `call_delta` and a live device,
  with nonzero consumer PCM. This rules out the sink enqueue boundary and moves
  the investigation to playback/drain timing.
- Hroute: the declared-real arm fails before title or lacks the phase-scoped
  consumer rows. This makes the run unevaluable; do not interpret it as a sink
  null.

Discriminating measurement:

- Keep the retail oracle in the same run with the whole-RDRAM positive control,
  title `0x00790400:1024`, and hangar `0x006AB400:512` controls. Keep its
  `osAiSetNextBuffer` witness enabled so retail title nonzero PCM remains an
  independent control.
- Run the previously qualified declared-real arm from
  `scratch/agent/run_s4054_m5_arm_isolation.sh`, with
  `ROGUESQ_LOG_M5_AUDIO_HOST=1` and `ROGUESQ_LOG_PCM_BOUNDARY=1`. Do not use
  the incomplete manual launch recipe. Require the port's title phase and
  nonzero `[pcm-boundary-consumer]` rows before reading `[m5-audio-host]`.
- Record title rows' `device`, `queued_before`, `queued_after`, `call_delta`,
  `pcm_bytes`, and `samples`. Positive retail control + qualified port title
  phase + Hsink fields selects Hsink; positive queue deltas selects Hqueue;
  missing controls is unevaluable.

Exact checks after the run:

```sh
grep -E '\[oracle\] (positive-control|done|ai-output-summary)|\[ai-output\]' scratch/agent/s4064_arm_sink/retail.log
grep -E '\[phase\].*(1024|512)|\[pcm-boundary-consumer\]|\[m5-audio-host\]|\[CRASH\]|\[ABORT\]' scratch/agent/s4064_arm_sink/declared-real.log
```

The existing runtime host logger is the instrument; no new counter is needed
unless its title rows are absent despite a qualified consumer witness.
