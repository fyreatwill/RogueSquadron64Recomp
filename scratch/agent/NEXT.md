# NEXT: s7208 follow-up — 4:3 Elite Rogues field screen: is the presented weave the retail image?
HYPOTHESIS-ID: interlaced-still-present
Context: s7208 fixed the 4:3 double present (ROGUESQ_PE_DEDUPE, default on; pairs 1376 -> 4, distinct images equal). Elite Rogues
at 4:3 (VI width 1024, fb 512 at 790000) presents 30/s with ~28-30 distinct/s while the game submits two field workloads per image
(ring W fbs 790000,620000|690000 alternating). s7207 scored G3 frac equal within a slideshow-phase confound (single-source).
Hypotheses:
 H-equal: presented image == angrylion weave of the same RDP stream (close the thread).
 H-field-mix: RT64 presents one field's fb with the other field's rows stale (row-parity residual vs angrylion).
 H-phase: residual is only the slideshow phase (content-matched frames equal).
Discriminator, ONE run: scratch/s7207/er43.zsh-style ER route, ER1 arm only, WITH ROGUESQ_G5B_FRAME_EVERY=1 FROM=4450 (s7207 recipe),
replay through tools/angrylion_replay, score with tools/s7122_fidelity.py and the s7207 parity tools (scratch/s7207/parity_*.txt
format): row-parity split of the residual on content-matched frames.
Outcomes: even/odd residual equal and at floor -> H-equal, close; odd rows only -> H-field-mix (fix the weave); unmatched -> H-phase.
If closed, take the next backlog item from CURRENT-TRUTH (owner items await the owner; ladder 3c).
