Single next work unit (s5635): fold s5633_force2_b from SOAK-RESULTS.md, then find the WRITER of objective boolean[7] (R refuted s5634: id 1 forced, 0/2 fails).
Hypotheses: (W1) bool 7 is set by an in-mission event/timer path via direct array store (not setObjectiveBoolean); (W2) bool 7 is a side effect of a mission-state object (e.g. ship damage/ally-loss) -- fail = real loss condition; (W3) stray write (corruption).
Discriminator: a store watch on the boolean array slot 7 in the ccosnap instrument (positive control: watch slot 0x20 which is known set at call#1), run in a soak long enough to catch a failing run (~2/5).
Alternatively grep recompiled code offline for stores indexed by the boolean array base with constant 7.
HYPOTHESIS-ID: m6-mission-endurance
