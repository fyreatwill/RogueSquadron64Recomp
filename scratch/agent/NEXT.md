# NEXT: G1 - s5862: does debris shadow troops in the bolt closest-hit loop? (H23 vs H22)
s5861: 285/1793 bolts hit; winners debris/troop/other = 278/0/7, but the troop classifier used the wrong fn. tools/apply_s5861_shadow.py now classifies troop = fn 800cabd4/800d93c0/800e7860 (edited in the tool only; funcs_13.c must be regenerated or patched: revert the s5861 block in RecompiledFuncs/funcs_13.c by re-running the regen fixup, or sed the kind line).
Hypotheses: H23 troop spheres are hit but a nearer debris node wins (shadowed>0, gap small); H22 troops are never hit (troophit_bolts~0) -> aim/altitude.
Run: rebuild, then env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fireall.sh s5862 300; read last [s5861] line. Control: D win count ~270+.
Outcomes: shadowed>0 -> H23 (fix: why debris spheres persist/oversized); troophit_bolts~0 with T win 0 -> H22.
HYPOTHESIS-ID: g1-mission-progression
