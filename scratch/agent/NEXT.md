# NEXT (s5673): re-measure speech/dialogue with correct AI cadence
Facts (s5672): AI event cadence fixed (DRAIN=2048 default, underrun 72% -> ~0%). Fuzz likely resolved; owner listen pending.
Hypotheses: H-d1 dialogue now audible (speech voice cadence was starved); H-d2 dialogue still absent because playObjectiveVoiceLine callers never fire (s5637); H-d3 voice DMA/decode path still empty.
Discriminator: one mission soak with [pcm-dense] + speech enqueue counters (s5670 recipe) on the new default; compare speech-window loudness at AI output vs s5670 baseline, and re-check caller counts.
HYPOTHESIS-ID: g2-speech-audible
