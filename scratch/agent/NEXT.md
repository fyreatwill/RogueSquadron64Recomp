# Next work unit
HYPOTHESIS-ID: keyed-mission-route-m5-validation
s4962: s4959 run1/run2 failed only because loop.sh runs recipes under /bin/bash (zsh-only ${0:A:h} -> empty ROOT). Recipes patched (zsh self-re-exec) and re-queued: s4959_mission_run{1,2,3}.sh in scratch/agent/soak_queue/.
Consume SOAK-RESULTS.md lines + soak_results/s4959_mission_run*/keys*.log. FIRST check the log has no "No such file" errors (invalid run). Per run: mission_onset_t, crash, abort, pcm_rows/pcm_nz_rows. Hypotheses: H-stable (3/3 mission, crash=0) vs H-intermittent-stall (as s4794) vs H-mission-audio-fault (PCM zero/abort). rc=137 = timeout, not a result.
Then add a mission-phase row to docs/M5-AUDIO-PLAN.md.
