# Next: implement ROGUESQ_EDGE_FADE in the 0x8004A6C0 epilogue (L_8004AA74)
HYPOTHESIS-ID: g3c-owner-visual
s6314 established 0x8004A6C0 owns terrain lit colour. Hypotheses for the fade input: H-pos (a1 world position vs camera gives distance; need camera pos source), H-cell (fade by cell ring index), H-fog-colour (blend toward sky/fog colour instead of black).
1. Find the camera position address (POSLOG pattern; a1 in A6C0 = pos ptr at 0($a1)) and the haze colour; blend rgb toward haze colour by smoothstep(dist, start, end) scaled by dd.
2. Arms (one build, env): retail-neutral (unset), dd3 no fade, dd3 + EDGE_FADE. Score with tools/g3c_edge_score.py; control: fade arm edge excess must drop, near terrain unchanged.
3. Ask owner re ROGUESQ_CULL_SPIKE default.
