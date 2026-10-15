# Next work unit

HYPOTHESIS-ID: m5-audio-destub

s4921 result: current default 5/5 leaves VI 640 for 1024 at t=47 s, no stall/crash (H-fixed vs s4794's 2/5 stall, 1/5 crash). Runs stop at the transition, so longevity is unmeasured.

Next unit: longevity soak of the current default through hangar and mission.
- Reuse tools/run_m5_yield_ab.sh phase-gated route (title 1024 -> hangar 512) and scratch/agent/s4796_hangar_gated_mission_2c.sh (mission entry), N=3 concurrent runs, 300 s each, SIGKILL at end.
Hypotheses: H-stable (3/3 alive, update_screen counter still advancing in the last 30 s, no [audio] guard fires), H-late-crash (a crash/abort appears in hangar/mission; read the fault symbol from the log, name the writer per iron rule 11), H-late-stall (counter static >=10 s; take `sample`).
Positive control: counter advances to the hangar phase (512-wide origin) in each run.
If H-stable: pick the first remaining item from CURRENT-TRUTH Next steps; if nothing new exists, go BLOCKED with the question "which user-visible goal (mission playability, 60 Hz pacing, audio fidelity) should the loop target next?"
