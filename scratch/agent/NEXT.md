# NEXT: fog/haze scaling vs dd, then ground-missing budget at dd>=4
HYPOTHESIS-ID: g1c-dd8-limit
Closed s6485: 0x80137CE4 is the difficulty index (not LOD); mesh LOD levers already no-gain (s6421).
H-fog: game fog/haze start/end (find via setFog/G_SETFOG-equivalent writes in the F5 DL, or RDP fog color/blend) unchanged at dd>1, so far geometry washes to sky colour; the "ground missing = flat sky blue" at dd>=4 (s6468) may be fog saturation, not missing tiles.
H-budget: ground tiles dropped by DL/vertex/cell pool at dd>=4.
Discriminator (one build, one run, pose-pinned like s6469_dd_break_sheet): at dd1 and dd4 log the fog params the game submits per frame and the ground-region vertex count; ALSO run an arm with fog disabled (ROGUESQ_FORCE_FOG off / fog blend zeroed). Positive control: fog-off arm must change the sky-blue ground region colour at dd1.
Outcomes: fog-off restores ground at dd4 => H-fog (scale fog with dd); ground still missing and vertex count low => H-budget.
