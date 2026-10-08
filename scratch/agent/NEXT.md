# Next work unit: why does the audio ucode produce ~1 buffer per 2 AI periods? (s4245)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4244 (two-line evidence): audible 16-buffer periodicity is stale ring re-DMA; ~171 ucode writes served ~345 AI queue calls in hangar phase. See PORTING-STATE Session 4244.
Hypotheses: (a) audio tasks are submitted at half the AI rate (game audio thread blocked/starved, e.g. waiting on a message the port delivers late); (b) tasks submitted at full rate but scheduler skips/drops some; (c) AI queue/DMA path runs too fast (pacing ungated by ucode completion) while task rate is nominal for the port's frame rate.
Discriminator: in ONE run, per phase, count (1) audio task submits (osSpTaskLoad/scheduler enqueue with ucode=audio), (2) completions, (3) osAiSetNextBuffer calls, (4) queue_samples calls, (5) VI frames. Positive control: queue count must equal (3) and writes must equal (2) (known from s4244). Outcomes: (1)~(2)~half of (3) => a; (1)>(2) => b; (1)~(2)~(3) but writes<queues => c is wrong, recheck.
Reuse s4244_stage.sh (flags above); find existing audio-task counters via grep '\[m5-audio-stage\]' and '\[m5-frame-sync\]' before adding any.
