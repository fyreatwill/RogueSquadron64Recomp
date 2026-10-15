# Next work unit
HYPOTHESIS-ID: keyed-mission-route-m5-validation
Context: s4958 reached a real mission (~70 s after 0x6A2900, crash=0, N=1). Three one-run soaks are queued: scratch/agent/soak_queue/s4959_mission_run{1,2,3}.sh (do NOT babysit or re-run them).
Work unit: consume the SOAK-RESULTS.md lines + soak_results/s4959_mission_run*/keys*.log. Per run: mission onset time, crash, abort, pcm_rows/pcm_nz_rows. Hypotheses: H-stable (3/3 mission, crash=0) vs H-intermittent-stall (as s4794) vs H-mission-audio-fault (PCM zero/abort). rc=137 = 600 s timeout, not a result; if so, trim waits and re-enqueue. If fewer than 3 verdicts exist, work on something not needing them.
Then add a mission-phase row to docs/M5-AUDIO-PLAN.md.
