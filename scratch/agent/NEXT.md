# Next work unit
HYPOTHESIS-ID: keyed-mission-route-m5-validation
Context: s4958 reached a real mission by waiting ~70 s after 0x6A2900 (scratch/agent/s4958_after_6a2900.sh), crash=0, N=1.
Work unit: repeat that recipe N=3 sequentially (one game at a time) with M5 audio counters armed (flags from s4944_aux_ab.sh). Per run: mission onset time, origin line counts, PCM nonzero count, crash/abort. Hypotheses: H-stable (3/3 mission, crash=0) vs H-intermittent-stall (VI640 stall as in s4794) vs H-mission-audio-fault (PCM zero or abort). Positive control: hangar 0x6AB400 before 0x6A2900.
Then add a mission-phase row to docs/M5-AUDIO-PLAN.md.
