Work unit: fold s5519_save_f7 (SOAK-RESULTS.md), then trace the writer of initMission B40 (the real mission selector; save byte f2 did not change it).
Hypotheses: H1 f7 also identical -> save slot is irrelevant, selector is B40 via a different source; H2 f7 differs -> value-dependent selector (f2 was just an invalid slot).
Discriminator: grep 'saveslot|initMission|mfst' scratch/agent/m6/s5519_save_f7/run.log vs base.
HYPOTHESIS-ID: second-distinct-mission-coverage
