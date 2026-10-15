# Next work unit: read s5012 retry verdict (s5010 route crashed before mission in s5011)

HYPOTHESIS-ID: m5-s4540-mission-sample

s5010 was run by hand in s5011: mission_onset_t=-1, crash in updateHangarBayScene. A copy (s5012_s4540_mission_sample_retry.sh) is queued for the loop. Read SOAK-RESULTS.md / soak_results/s5012_s4540_mission_sample_retry/keys1.log. Valid only if mission_onset_t>=0 and crash=0.
If it crashes again the same way: the route is flaky; go BLOCKED with that specific question rather than a third try.
Outcomes: cur20>0 & stale32=0 -> close thread; stale32>0 -> audit that reader. No guard/mitigation.
