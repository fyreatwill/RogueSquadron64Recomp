# Next work unit (s4441): validate ROGUESQ_AI_EVENT_HZ=115 (m5-ai-event-cadence)

HYPOTHESIS-ID: m5-ai-event-cadence

s4440 showed the guest loop submits a fixed 768 B per AI event and the port posts AI events at 60 Hz; the env knob ROGUESQ_AI_EVENT_HZ=115 gives 110.6 buffers/s. Open:
(a) 115 Hz is stable (queue depth bounded, title+hangar reachable, no new crash family) vs (b) the 2x submit rate surfaces new guest races (e.g. fillSampleStreamRange Bus error appears sooner) vs (c) retail really runs ~60/s (mupen witness) and 115 over-feeds the mixer.
Discriminator: mupen CPU Count per submit in oracle (emulated cycles/submit; 46.875 MHz /60 = 781k per VI as positive control) -> ~8.7 ms means retail is 115/s; ~16.5 ms means mupen artifact is NOT the explanation. Plus a soak of the 115 arm vs unset arm counting fillSampleStreamRange crashes in each (run both in one iteration, scratch/agent/s4440/run_A.sh / run_B.sh as templates).
Note: arm A (env unset) crashed in fillSampleStreamRange+15116 twice before phase 4 — the crash family is live in the baseline.
