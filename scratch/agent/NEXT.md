# NEXT: G1 — why do class-1 NPCs reach destroy (msg 2 silent, 47/54) instead of the counted kill (msg 5)?
s5817: bit-3 setters are all self-despawn calls from each object's own update fn (bulk = effects). Class-1 subset callers: npcGroundTroopUpdate (45), npcProbeDriod (56), npcWakeUpdate (17), npcWingmanUpdate (4).
Hypotheses: (a) destroy follows health<=0 via a path that skips the counted msg 5 (port divergence in the kill-message send); (b) destroy by distance/off-screen/age condition inside the NPC update (design); (c) destroy because a shared state (e.g. wave timer/sibling) was mis-evaluated.
Discriminator (one build, one run): at the destroyNpcSlotByIndex call sites inside npcGroundTroopUpdate and npcProbeDriod (extend tools/apply_s5817_bit3_setters.py with per-caller site pc via backtrace address offset), log the NPC's health word, distance to player, and last damage source at destroy time. Control: s5817 counts (45/56 per 405 s) reproduce. Outcomes: health<=0 at all -> (a), follow why msg 5 is not sent; health>0 with distance large -> (b) compare threshold to retail; neither -> (c).
Command: zsh scratch/agent/g1_inv1.sh <tag> 400
HYPOTHESIS-ID: g1-mission-progression
