# NEXT: s7204 side datum — the 20/s non-flight screen (VI origin B517C8) and the R0-only 60/s presents
HYPOTHESIS-ID: retina-nonflight-present
Context: s7204 L6r0/L6r1 (owner recipe, tools/g1e_owner_quiet_arms.zsh) hit an 8 s non-flight screen at t=205-213 (autopilot
backdrop/menu cycle, tr=31) where the game makes a new image at 20/s in both arms (VI origin B517C8). Single-source: L6r0 also
queued 60/s presents with vi=B51E00 there that L6r1 (RETINA=1) did not. s7205 owner sheet done; Retina default is the owner's call.
Hypotheses: H-retina (RETINA=1 changes which VI origins RT64 presents on that screen: a real present-path difference),
H-phase (the two arms entered the screen in different states, e.g. a fade, so the extra presents are scene, not setting),
H-retail (the screen is a retail 20/s menu; the B51E00 presents are the old fb being re-presented, harmless).
Discriminator: replicate L6 with HOLD 240 in both arms x2 (ARMS "4:a0:ROGUESQ_FORCE_SAVE_MISSION=6 4:a1:...+ROGUESQ_RETINA=1" twice,
order reversed), SHOTS at 205,209 to name the screen; from ring rows count per arm Q rows by vi origin in the B517C8 window
(tools/s7204_ring_cost.py as base). R0-only B51E00 in all R0 runs -> H-retina; mixed across replicates -> H-phase; then compare
with the angrylion/retail path to decide H-retail. Positive control: the flight window must show 60/s Q rows in every arm.
