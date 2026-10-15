# Next work unit: consume the s5010 soak verdict (m5-s4540-mission-sample)

HYPOTHESIS-ID: m5-s4540-mission-sample

The soak `soak_queue/s5010_s4540_mission_sample.sh` is enqueued; the loop runs it between iterations.
Read the new SOAK-RESULTS.md line and soak_results/s5010_s4540_mission_sample/keys1.log.
Valid only if mission_onset_t>=0, s4994arm>=1, crash=0 (else route-unevaluable: do NOT conclude; fix the route, re-enqueue once).
Outcomes: rows with 0x8018C720 (cur20>0, stale32=0) -> mission path is current, stale pair pre-mission-only, close thread.
stale32>0 -> uninstrumented reader/propagation, audit that reader. s4994rows=0 with controls passed -> no ordinary caller in mission.
No guard, rewrite, or mitigation. Owner question (declare M5 done) is non-gating.
