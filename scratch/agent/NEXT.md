# NEXT (s7880)
HYPOTHESIS-ID: g3-det-render-coverage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State: 9 missions render-exact on det-tick flight frames (b17, m12, m6, m11, m3, m8, m4 pre-fork, m5, m1; s7879).
Unit (offline, no game run): explain s7879's longer mission-1 pre-flight. In the port the 640-wide pre-flight scene runs ~2551
frames longer than in retail (port phase 6 = 3417 frames, retail 640@2864 = 866 frames; flight offset -3082 vs pre-flight -531).
Data in scratch/s7879/v0: r1/oracle.log (retail, press schedule PP 19.5..91.5), p1/run.log (port, AP schedule), frame_cmp.txt.
Hypotheses: H-latch (a retail Start press that skips the scene is dropped/not latched by the port: find which press time ends
retail's scene and whether the port's phase change lines up with a later press), H-sched (the AP and PP schedules differ in
offset for this mission, i.e. recipe not port: compare the press times against each side's phase starts), H-scene (scene
length not input-driven: then both sides end without a press near the transition).
Discriminator: press times vs scene-end times on both sides. H-latch -> look at the port's input latch at that scene
(real defect, owner-relevant). H-sched -> fix the schedule (AP_OVR) and rerun the pair to cover all 5556 ticks.
Then the next hand row: 1 or 2 (s7840) with `env RBIN=1 zsh tools/s7849_det_pair.sh <v> scratch/s7880/v<v>` (~40 min, screen unlocked).
Parked: g3-cinematic-half-frame-phase (s7874 table).
