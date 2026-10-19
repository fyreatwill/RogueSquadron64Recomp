Work unit 1 (fold): read scratch/agent/m6/s5508_im_{base,f2,f7}/run.log. Control = base shows the [mfst] manifest-name log; differing name sets between f2/f7 => B40/initMission override selects content. Record in PORTING-STATE + CURRENT-TRUTH.
Work unit 2: static grep for writers of bit 0x02000000 in word 0x18($s3) of mainGameLoop state struct; classify each writer; name which one the hangar mission pick reaches.
Hypotheses: H1 flag set by hangar via menu overlay with mission index in sibling field; H2 mission chosen inside cinematicLoopBody arg from save data; H3 only one mission in this path.
Discriminator: writer list + sibling index field; positive control = base run shows the writer firing before 0x00690400.
HYPOTHESIS-ID: second-distinct-mission-coverage
