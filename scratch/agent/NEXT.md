# NEXT (s5893): is the class-1 msg5 cap of 8-9 a one-shot-per-kind limit?
Context (s5892): pos pokes (s5891 beside, s5892 ring x/z +/-7) leave tmsg5 at 8-9 over ~100 windows; no direction preference; ship has no yaw field (tilt only).
Competing: (a) msg5 is delivered at most once per distinct id/type (cap = count of kinds, ~8-9) so kills beyond are not msg5-driven; (b) msg5 needs a state the player never creates (e.g. NPC phase flag) and the 8 are incidental; (c) class-1 shapes unhittable.
Discriminator: extend the [npcmsg] tally (src/main/main.cpp / its fixup site) to log per-NPC id+type on every msg5 and the NPC's st10/st14 at that moment; offline, check whether the 8-9 events are 8-9 distinct ids (a) or repeats (b). Also read the class-1 update fn's msg5 branch (grep the msg5 case in funcs where npcProbeDriod is called). Positive control: msg3/4 (73k each) must show per-id counts in the same run.
HYPOTHESIS-ID: g1-mission-progression
