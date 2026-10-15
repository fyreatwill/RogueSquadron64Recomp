# Next work unit
HYPOTHESIS-ID: keyed-mission-route-m5-validation
Unchanged from s4960: consume SOAK-RESULTS.md lines + soak_results/s4959_mission_run*/keys*.log (queued, NOT yet run as of s4961). Per run: mission_onset_t, crash, abort, pcm_rows/pcm_nz_rows. Hypotheses: H-stable (3/3 mission, crash=0) vs H-intermittent-stall (as s4794) vs H-mission-audio-fault (PCM zero/abort). rc=137 = timeout, not a result (worst-case budget is 515 s, so unlikely).
If still no verdicts: check loop.sh queue glob/ordering and go BLOCKED with that specific question (a 2nd SUBSTITUTED stops the loop).
Then add a mission-phase row to docs/M5-AUDIO-PLAN.md.
