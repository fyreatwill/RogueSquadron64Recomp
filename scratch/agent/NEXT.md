Work unit: M5 audio de-stubbing - write docs/M5-AUDIO-PLAN.md (survey every audio stub/trap/gate in force, plan incremental de-stub steps with a validation soak each), then execute step 1. M6 first-mission endurance (flight, MISSION FAILED, retry, results hold) is CLOSED as of s5498.
Hypotheses: (A) audio-disabled degenerate paths cause crash families - de-stubbing dissolves guards; (B) guards are unrelated to audio - de-stub changes nothing. Discriminator: soak with first de-stub arm vs control in one iteration, counting guard breadcrumbs fired.
HYPOTHESIS-ID: m5-audio-destub
