Work unit: read mainGameLoop dispatch at L_8003E114 (0x8003E114..0x8003E1F0, generated funcs_8.c ~21100-21470) for how B40 selects the loop arm; then ONE build logging arm-entry PCs (0x8003E274, 0x8003E2A8, 0x8003E320, 0x8003E3F0) with B40, base vs f2 (ROGUESQ_FORCE_INITMISSION_SEL), phase-gated on the 0x00690400 VI transition.
Hypotheses: H1 nonzero B40 enters an arm that waits (stall); H2 it skips the manifest/initMission arm; H3 base is timing-dependent.
Discriminator: which arm-entry PCs fire in f2 vs base (positive control: 0x8003E2A8 must fire in base).
HYPOTHESIS-ID: second-distinct-mission-coverage
