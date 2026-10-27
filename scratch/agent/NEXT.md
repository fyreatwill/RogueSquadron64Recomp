# NEXT: G3c(a) fold s6354 soak (radfade2 col/row pair)
HYPOTHESIS-ID: g3c-owner-visual

s6354 decoded the AA74 position pair from code: row = callee sp+0x44, col = callee sp+0x74, height = sp+0x40. Soak s6354_g3c_r2_colrow arms: pcr (R2=18,26,116,68), prc (68,116), none. Output dirs scratch/agent/m6/g1_lvl1s6354_{pcr,prc,none}.
1. grep '[radfade2]' run.log per arm: valid pair = d varies per vertex, bounded (<~40), f 0..1 spread. Swapped orientation distinguishes col<->cam.x vs cam.z.
2. If valid: run tools/g3c_edge_score.py on far-edge frames (fbd) for pcr/prc vs none, build owner contact sheet. If faded edge is smooth => H-fade-dark; if jagged persists => footprint-only, try max(|dx|,|dz|).
3. If neither valid: the row/col offsets are wrong (callee sp at hook may differ); dump sp+0x38..0x98 (EF9_CODE 12->24 words) and rebuild.
