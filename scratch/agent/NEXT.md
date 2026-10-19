Work unit: static + one-run trace of what gates the post-initMission manifest load ([mfst] dbg_data/data, tools/fixup_game_funcs_vendored.py:~37408) on B40. Find the caller of the manifest loader, read its branch on B40 (gCurrentLevel), and log the branch inputs in base vs f2 in ONE build (phase-gated on the 0x00690400 VI transition).
Hypotheses: H1 nonzero B40 takes a loader path that waits on state we never provide (stall) -> trace shows loader entered but not returning. H2 loader skipped for nonzero level (different branch) -> caller never reached. H3 base's 342 s transition is timing-dependent and not B40-related -> repeat base x2 to check recurrence of mfst.
Discriminator: caller-entry counter + B40 value at it, in base x2 and f2.
HYPOTHESIS-ID: second-distinct-mission-coverage
