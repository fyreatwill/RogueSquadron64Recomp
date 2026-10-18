# Next work unit: read the queued s5371 path-census soak and close or escalate
HYPOTHESIS-ID: patcheslib-shadowed
s5370/s5371: title-window census shows ent=12288 slot0=0 g2=g3=0 (cached slot 0x801163B0 never empty). Mission unmeasured; manual run_a5370.sh route fails (nohangar) - the loop runs soak_queue/s5371_path_census_mission.sh instead.
Unit: after SOAK-RESULTS has an s5371 line, `grep -a '^\[a5370\]' scratch/agent/soak_results/s5371_path_census_mission/run1.log | tail`. Outcomes: mission reached + slot0=0 -> close thread (walk guards dead route-wide); slot0>0 and g2>0 -> read g2bad/g3bad, name the writer; route fails again -> go BLOCKED/pivot (M5 de-stub per docs/M5-AUDIO-PLAN.md), stop retrying the route.
