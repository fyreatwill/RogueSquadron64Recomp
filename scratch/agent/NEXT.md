# NEXT (s7216): G3 21:9 front-end fidelity on the long route (MISSION FAILED, Elite Rogues) vs angrylion
HYPOTHESIS-ID: g3-21x9-frontend-fidelity
Context: present-shape thread closed s7215 (logs + pixels clean). The G3 presented-frame matrix (s7122-s7186) scored flight and the
front-end mostly at 16:9/4:3; the 21:9 fail screen, ER list and the fail wipes were never scored against the oracle. At 21:9 these
screens draw centred content (game scissor 341..1019 of 1360) and a 1024-wide fb (16:9 used 796, B51E00).
Hypotheses: H-match (RT64 central band matches angrylion within the s7141 scoring floor, bars black);
H-shift (band offset/scaled vs oracle: wide-width patches move the 4:3 content); H-field (ER interlaced field handling at 1024 wide
differs from the 16:9 progressive result of s7210, e.g. weave/bob rows).
Discriminator, 1 run: tools/s7141_arm.zsh 17 FE21 "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=<swap of
MISSION FAILED>" 150 80 (CW=1680 CH=720; find the swap from the s7210 census timings ~125 s / ~205 s), then
tools/s7141_post.zsh with the central-band rect (s7210_regfit.py first, TRAP in CURRENT-TRUTH), tools/s7122_fidelity.py.
Positive control: a deliberately shifted replay (+4 rows) must score worse. Each outcome names its hypothesis; fix H-shift/H-field in
the same iteration.
