# NEXT (s5885): who calls destroyNpcSlotByIndex for the class-2 objectives under held fire?
Context (s5884): msg-5 SEND path excluded (656 sends, 0 descriptor-bearing victims; class-2 destroys at el 337-356 still occur).
Hypotheses: (a) wave/script logic (timer or counter from class-1 teardowns) destroys class-2 directly; (b) proximity/collision handler (player or NPC body overlap) destroys them; (c) another damage routine other than SEND (area-damage/explosion loop) hits them.
Discriminator: in apply_s5810_npc_supply.py B2 (destroy hook) also print ctx->r31 (ra) and the caller's caller if cheap (stack word), plus node id, for every destroy; run s5884_hits.sh again (positive control: class-1 destroys print ra too). Group ra by class: class-2 ra == class-1 ra => same teardown routine (then look upstream at its trigger); distinct ra => name that function.
HYPOTHESIS-ID: g1-mission-progression
