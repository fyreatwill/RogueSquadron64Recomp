# Next work unit (s4439): why 192 frames per AI buffer? (m5-sdl-consume-rate, closing)

HYPOTHESIS-ID: m5-sdl-consume-rate

s4438: dacrate/cadence/length equal retail; retail AI idle at every submit. Remaining: 192 frames vs 367 expected per 60 VI/s. Hypotheses: (a) game mixes 192 frames/tick by design (compare the mixer frame-count argument retail vs port in one title phase), (b) AI_LEN always 0 is an oracle artifact (needs a nonzero control: sample mid-buffer). If (a) equal in both arms, close the thread and move to the next docs/M5-AUDIO-PLAN.md step.
