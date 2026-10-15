# Next work unit

HYPOTHESIS-ID: m5-audio-destub

s4922: 3/3 concurrent runs alive 300 s through title+hangar, 0 crashes/guard fires, counter advancing. Mission phase NOT reached (autopilot cannot enter a mission).

Next unit: mission-phase longevity, N=1 at a time (winctl keys are per-keyboard).
- Run scratch/agent/s4796_hangar_gated_mission_2c.sh (reaches origin 0x00690400), then extend: hold 120 s after mission entry, sampling update_screen counter every 10 s.
Hypotheses: H-stable (alive, counter advancing, no CRASH/ABORT), H-mission-crash (read fault symbol, name the writer per iron rule 11), H-mission-stall (counter static >=10 s; take `sample`).
Positive control: mission origin 0x00690400 appears in log.
If H-stable: go BLOCKED asking "which user-visible goal (mission playability, 60 Hz pacing, audio fidelity) should the loop target next?"
