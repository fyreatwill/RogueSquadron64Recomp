# Next work unit: is the objectives-complete trigger legitimate?
Hypotheses: H1 autopilot genuinely met level-0 objectives; H2 a counter/flag read by lv0_checkComplexObjectives (0x8010119C, size 0x750) is zeroed/stale so it fires early; H3 timer-based. Discriminator: list the memory words it tests, then in a TRAPSWAP=2500 run read them just before the setHudEnableBit4 hit (positive control: 0x3470 hit). Also record what renders after phase 6.
HYPOTHESIS-ID: m6-mission-end-trigger
