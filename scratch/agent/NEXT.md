# NEXT (s5884): why does held player fire make NPC bolts kill class-2 objectives (nofire: 0 destroys in 413 s)?
Context (s5883): class-2 kills are NPC bolts (12/12 who=N); class-2 descriptor set varies per run (e5c/c1c/5dc vs a9c/cdc/e5c).
Hypotheses: (a) player fire wakes/aggroes enemy groups whose bolts then hit nearby class-2; (b) fire spawns/activates enemies by a trigger that nofire never crosses (only class-1 teardowns count); (c) class-2 objects are the enemy's targets only once engaged.
Discriminator: in one fire run log shooter desc/vt + victim desc per SEND (not capped at 24) and the first-fire time vs first N-SEND; positive control = N sends fire. Compare with nofire window phase-gated on the same VI origin.
HYPOTHESIS-ID: g1-mission-progression
