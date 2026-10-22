# NEXT (s5888): who creates class-2 NPCs (desc+0x70==2), and can class-1 be killed without hitting them?
Context (s5887): class-2 NPCs sit within ~2 xz units of class-1 descs (7/7); spawn arm L_800CAC40 only makes class-1.
Hypotheses: (a) class-2 = shield/decoy companion placed on each class-1 group by a second spawner; (b) class-2 = same object seen through a second descriptor view; (c) class-2 spawned by level script (static 0x80319xxx desc table) unrelated to class-1 yet map-overlapping.
Discriminator: offline first - grep RecompiledFuncs for other rs_malloc 0x11C sites / writers of NPC+0x34 (npc desc ptr); then [npcd] msg=3 npc+0x0C..: does class-2 carry a parent link (npcv parent=) to a class-1 npc? Control: npcv parent field is already logged for class-1.
Then: protect-class-2 (ROGUESQ_NPC_INVULN class-2 only) + fire run: does c1 climb past 8 toward 21?
HYPOTHESIS-ID: g1-mission-progression
