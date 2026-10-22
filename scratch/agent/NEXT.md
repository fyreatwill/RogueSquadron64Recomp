# NEXT (s5901): true per-bolt speed/lifetime/hit distance in the segment-vs-sphere loop
Context (s5900): r17 is one emitter (0x8035581c); pp (arg r6) is each bolt's segment origin; ~24 distinct pp per cycle, 13 collider rows each. s5897/5898 life stats void.
Competing: (H-range) bolts move too little/expire before reaching troops; (H-aim) bolts pass beside targets; (H-ok) bolts travel fine and survivors are another cause (e.g. NPC invuln flag, ROGUESQ_NPC_INVULN is armed in the recipe!). Check the boring thing first: recipe sets ROGUESQ_NPC_INVULN=1 - confirm it does not explain survivors.
Discriminator (one build, one run): replace rs5897_track keying with nearest-neighbour matching of pp across successive cycles (a cycle = new pp != previous pp); per bolt log displacement per cycle, age in cycles, and distance to nearest collider centre at last sample; positive control: >=100 bolts with age>=3.
Recipe: scratch/agent/s5897_life.sh; edit both tools/apply_s5835_sphere_probe.py and live N64Recomp/RecompiledFuncs/funcs_16.c.
HYPOTHESIS-ID: g1-mission-progression
