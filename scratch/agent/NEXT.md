# Next: find a mission state witness (ship/camera words) that moves under held stick but is stable in ctl
HYPOTHESIS-ID: m6-mission-input
s5069: whole-frame hash saturated (every frame unique in ctl too) -> no headroom; pixels are the wrong witness.
Hypotheses: H1 mission reacts (some RDRAM words change only under input); H2 pad read but ignored (no ctl-stable word moves under W/D/Z/Return).
Discriminator: add ROGUESQ_RDRAM_SNAP=<dir> env: on a signal file / at script-chosen times dump 8 MB RDRAM; snapshots: ctl1, ctl2 (10 s apart, no keys), keyW (during W held 4 s), keyD. Offline: words equal ctl1==ctl2 but differing in keyW/keyD = candidate witnesses. Positive control: a word known to change (frame counter) must show in ctl1!=ctl2.
Script base: scratch/agent/s5069_mission_fbhash.sh (route ~260-290 s).
