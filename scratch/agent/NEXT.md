# NEXT (s5913): get real-input bolts to cross class-1 spheres (aim/steer)

HYPOTHESIS-ID: g1-mission-progression

s5912: shadowing refuted; hit->win->send works for class-1 when a bolt crosses (6/6). Remaining: bolts never cross the other class-1 spheres.
Hypotheses: H-aim (autopilot flies a fixed key table, never points at class-1 targets); H-range (class-1 NPCs are beyond bolt life ~ few units); H-spawn (those NPCs are not yet spawned/active in 420 s window).
Discriminator: in one run log, per class-1 id (fn cabd4/d93c0/e7860), player-to-NPC distance at closest approach (ROGUESQ_PLAYER_DUMP + slot-table pos) next to bolt max life distance (s5897 hist). If closest approach >> bolt reach, H-range/H-aim; then add autopilot steering (tools in scratch/agent/g1_approach.sh) toward nearest class-1 and re-run g1_fireall with the s5912 tally as the measure (control: class-1 crossings must exceed 6).
Instrument already present: tools/apply_s5912_shadow.py (ROGUESQ_LOG_HUDBIT=1), run: zsh scratch/agent/g1_fireall.sh <tag> 420
