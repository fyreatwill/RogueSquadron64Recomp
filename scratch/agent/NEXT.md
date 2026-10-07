# Next work unit: M5 Step 6 / A13 — validate default-off drain tick vs ROGUESQ_DRAIN_INLOOP_TICK=1

HYPOTHESIS-ID: m5-audio-destub-sequence

s4199 closed A15 (spin yield default-on, dormant on title+hangar). Remaining open plan rows: Step 6 (A13 drain-tick, "validation pending" since s2692), then Step 9/10.
Hypotheses: H-drain-not-entered (drainAudioAndFinalizeSpeechBuffer never runs on title+hangar -> A13 closes like A14); H-drain-clean-both (entered, both arms return, no 10M timeout); H-tick-needed (default-off arm hits the 10M timeout, tick-on does not).
Discriminator: one build, two concurrent arms (copy scratch/agent/s4199_spin_yield_default_ab.sh; arm2 adds ROGUESQ_DRAIN_INLOOP_TICK=1), count drain entries/returns and timeout logs per arm. Positive control: entry count >0 in tick-on arm; if 0 in both, A13 is dormant -> close, move to Step 9/10.
