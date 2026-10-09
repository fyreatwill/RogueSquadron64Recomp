# Next work unit (s4471): M5-AUDIO-PLAN step 7 - decode the port's status-03 worker entries

HYPOTHESIS-ID: m5-status03-service-reaping

State: s4470 made the s4104 route valid (run: `env RS64_SOAK_OUT=<abs dir> zsh scratch/agent/soak_queue/done/s4104_*.sh`; results in scratch/agent/soak_results/s4470_status03/). Retail never hits 0x8009B30C/B7CC/B7EC in title+hangar; the port s2020 worker is entered with status 0x03 five times in phase 5.
Hypotheses: (A) port status 0x03 is the same worker state as retail B30C and the port reaches it spuriously (divergence -> reaping); (B) s2020 "status" is a different field than the one B30C stores, so the 5 entries are benign; (C) retail reaches it only after the 75 s window.
Discriminator: by code reading identify what the s2020 status is (grep the s2020-svc emitter); then one run with uncapped port counters at B30C/B7CC/B7EC equivalents vs retail's 0, phase-gated on VI 512, plus a retail run extended to --secs 150 with the same watches (positive control: B600 must hit). A: port counter >0 and retail 0 at 150 s. B: port counters 0. C: retail B30C hits after 75 s.
