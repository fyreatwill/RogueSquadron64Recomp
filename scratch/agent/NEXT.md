# Next work unit
HYPOTHESIS-ID: keyed-mission-route-m5-validation
Context: s4954 showed the s4950 "mission" 512 phase is the attract demo. A keyed hangar->mission run is the real mission.
Work unit: take the s4943/s4944 keyed route recipe (scratch/agent/s4944_aux_ab.sh), run N=3 solo with VI-progress (tools/vi_progress.py) and a key-injection timestamp log; competing: H-keyed-mission-stable (512 phase persists >30 s after Start, no title bounce) vs H-keyed-bounce (bounces to title like the demo => real port defect) vs H-route-flaky (VI-640 stall, relaunch).
Discriminator: after the hangar Start key, does origin 0x690400 persist past 30 s with VI advancing? Positive control: hangar 0x6AB400 phase reached before keys.
Add the result as a mission-phase row in docs/M5-AUDIO-PLAN.md.
