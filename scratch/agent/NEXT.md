# NEXT (s5920): per-frame ship yaw + object id in class-1 sphere log

HYPOTHESIS-ID: g1-mission-progression

Context (s5919): class-1 spheres r 0.06-0.68; track (30-frame samples) never within 1.5 of any centre. H-range favoured, H-heading/H-lifetime untested (log lacks yaw and object id; plpos sparse).
Work unit: extend [plpos] emitter to every frame during a short window and add ship yaw; tag [sph] P rows with owning object ptr; rerun tools/g1_steer.sh; tabulate per-object min range and angle(heading, ship->obj) with tools/g1_track_vs_spheres.py.
Control: the 13-sphere / 20 P-row shape reproduced.
