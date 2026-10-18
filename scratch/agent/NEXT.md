# Next work unit: RDRAM state-diff at results-scene entry (see docs/M6-MISSION-END-TRIGGER.md)
Hypotheses: H1 timer/objective loss, H2 out-of-bounds, H3 cheat/debug path forces success.
Discriminator: one run of the z-only flight (m6_keyed_hold_zonly.sh) dumping a game-state RDRAM window at the VI-phase transition into results vs ~100 swaps earlier; positive control = same dump across title->hangar. Words that change only at results entry name the condition. One build.
HYPOTHESIS-ID: m6-mission-end-trigger
