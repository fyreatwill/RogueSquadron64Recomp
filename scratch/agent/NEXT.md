# Next work unit (s4474): M5-AUDIO-PLAN Step 10 qualification (AI source -> callback -> SDL join)

HYPOTHESIS-ID: m5-ai-sdl-join

Step 7 closed in s4473. Read docs/M5-AUDIO-PLAN.md Step 10 and A16.
Hypotheses: H1 nonzero PCM at osAiSetNextBuffer reaches SDL intact (addr/count/hash); H2 source nonzero but consumer/SDL loses it; H3 source all zero (go to Step 8).
Discriminator: one run logging per submit addr/len/hash/nonzero-span at AI source and SDL callback; positive control = a nonzero-span submit in title phase.
If Step 10 already qualified (grep PORTING-STATE), do Step 8 voice-base guard class audit instead.
