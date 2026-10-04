# Next work unit: qualify title audio playback/drain timing

HYPOTHESIS-ID: m5-title-audio-playback-drain

Session 4064 selected Hqueue for the host endpoint discriminator. Retail passed
the whole-RDRAM/title/hangar controls, and the schedule-gated declared-real port
reached both target phases. Device 2 opened; host rows had positive queue
deltas in title and hangar, and consumer PCM was nonzero.

Competing hypotheses:

- Hdrain: `[m5-audio-drain-raw]` shows queue depth repeatedly reaching zero or
  failing to track the positive host enqueue calls while consumer PCM is
  nonzero. This selects a playback/drain timing defect.
- Hplay: drain rows show queued bytes/frames advancing through title while host
  calls remain positive. This rules out an immediate drain starvation defect
  and moves the question to the device callback/output path.
- Hroute: the declared-real arm fails before both target phases or lacks
  nonzero consumer rows. This makes the run unevaluable.

Discriminating measurement:

- Keep the retail oracle in the same run with the whole-RDRAM positive control,
  title `0x00790400:1024`, and hangar `0x006AB400:512` controls. Keep its
  `osAiSetNextBuffer` witness enabled so retail title nonzero PCM remains an
  independent control.
- Run `env RS64_S4064_OUT=... zsh scratch/agent/run_s4064_m5_arm_sink.sh`;
  its schedule gate waits for the retail positive-control marker before
  launching the declared-real arm. Add `ROGUESQ_LOG_M5_AUDIO_DRAIN=1` to the
  port environment. Require retail controls, both port phases, and nonzero
  consumer rows before interpreting drain data.
- Compare phase-scoped `[m5-audio-drain-raw]` `queued_bytes`/`frames` against
  `[m5-audio-host]` `queued_before`/`queued_after`/`call_delta`. Hdrain requires
  the drain-zero pattern; Hplay requires advancing queue depth with positive
  enqueue calls. Missing controls is unevaluable.

Exact checks after the run:

```sh
grep -E '\[oracle\] (positive-control|done|ai-output-summary)|\[ai-output\]' scratch/agent/s4065_arm_drain/retail.log
grep -E '\[phase\].*(1024|512)|\[pcm-boundary-consumer\]|\[m5-audio-host\]|\[m5-audio-drain-raw\]|\[CRASH\]|\[ABORT\]' scratch/agent/s4065_arm_drain/declared-real.log
```

The existing drain logger is the instrument; no new counter is needed.
