# Next work unit (s4295): restore the ODD positive control, then decide on WRAP_RESTORE

HYPOTHESIS-ID: m5-audio-destub-sequence

s4294: seeded hangar A/B reached 512 at 47.4s in both arms but the WRAP_RESTORE=0 arm had oddCommits=0 (even at 640), so the A/B is non-discriminating. Differences vs s4286/s4290 (odd 58-60): SPIN_YIELD/Y8000_WIDTH env, key route.
Hypotheses: H1) SPIN_YIELD/Y8000 suppress the ODD condition; H2) seeded saves change 640-phase content; H3) ODD is intermittent run to run.
Discriminator: variants of scratch/agent/s4294_hangar_ab.sh, both arms RESTORE=0: (a) drop SPIN_YIELD+Y8000, seeded; (b) s4286 env (autopilot) with seeded saves. Whichever shows odd>0 becomes the control for the hangar A/B (RESTORE 0 vs 1, maxFbs added).
