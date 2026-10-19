Single next unit: explain what initMission (funcs_42.c) does with a0 = 0x32/0xD3/0xE3 under ROGUESQ_FORCE_CINE_A0=1/2 and why f2 emits no [mfst] lines. Offline read first (grep initMission body), then add one content-aware metric (level/DL name or fbhash at phase 7) and rerun base/f1/f2 via scratch/agent/s5525_*.sh.
Hypotheses: H1 a0 picks a different mission whose data load is not visible to [mfst]; H2 initMission a0 is a pointer (the values are heap addresses, not mission ids) so differences are allocator noise; H3 f2 hits an early-out path.
Discriminator: fbhash/DL hash differs between base and f1 at the same VI phase.
HYPOTHESIS-ID: second-distinct-mission-coverage
