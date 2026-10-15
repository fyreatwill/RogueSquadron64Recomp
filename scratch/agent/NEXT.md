# Next work unit
HYPOTHESIS-ID: keyed-mission-route-m5-validation
Context: s4955 confirmed (3/3) that sending keys only after the first vi_width=512 line never reaches the hangar; 512/0x690400 is the attract demo (bounces to title 3-5 s after onset regardless of keys).
Work unit: copy scratch/agent/s4955_keyed_solo.sh; send winctl keys (36 then 6, as in s4944_aux_ab.sh) starting when the title phase (origin=0x00790400) first appears (~t=50 s), NOT after 512. Control: hangar origin 0x006AB400 appears before the mission claim. Then competing: H-keyed-mission-stable (a non-demo phase persists >30 s, VI advancing) vs H-keyed-bounce (returns to title => port defect) vs H-route-flaky (no hangar). Check s4943/s4944 logs for which phase the keys were sent in first (grep tools/probe.sh PROBE_KEYS_FROM_PHASE).
Record as a mission-phase row in docs/M5-AUDIO-PLAN.md.
