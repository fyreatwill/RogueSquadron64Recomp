# NEXT: force max-unlocked byte 0x80130B2F=N (env ROGUESQ_FORCE_UNLOCK) at the [lvsel] init hook (fixup script + live tree), print B2F in the init line, run with ROGUESQ_FORCE_SAVE_MISSION=N for N=3 and 5.
Hypotheses: H1 confirmed (s5704b). Open: does ret=N then B40 stay N and lvN initialise (H5), or does the mission load fail for N>2 (H6)?
Discriminator: init a3==N and ret==N, then initMission/[mfst] names for level N vs level 2.
HYPOTHESIS-ID: g1-level-select
