# NEXT: G1 — map counter-1 bool ids (0x18..0x2B) to lv0 DAT descriptors/positions
s5827: counter 1 counts distinct bool ids (44 class-1 spawns -> 8 distinct sets). Need ~21 distinct ids.
Hypotheses: (a) unreached ids are NPCs placed beyond reach of a 2.2 u/s ship; (b) unreached ids need a different trigger (scripted/later spawn); (c) counter 10 (arm C get(10)>=6) is a separate objective path.
Discriminator (offline first): read lv0 DAT descriptor table (see tools/apply_s5809_ctr1_log.py for the datItem hook) -> list id, position; compare with player start (42.7,45.0) and distance travelled. Then one run with the autopilot logging which ids set, positive control: the 8 known ids.
HYPOTHESIS-ID: g1-mission-progression
