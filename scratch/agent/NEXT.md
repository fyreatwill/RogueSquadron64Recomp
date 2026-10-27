# NEXT: dd4 low-ground frames: fewer passing cells (H-data) or cells pass but not drawn (H-budget)?
HYPOTHESIS-ID: g1c-dd8-limit
s6487: ~52% of dd4 frames are low-ground vs 2% at dd1; pool size irrelevant.
Discriminator: within ONE dd4 run (scratch/agent/m6/g1_lvl1s6487p_d4), join each fbdump frame's ground score with the exitlog/gatesplit pass-cell and tri counts for that VI (tools/g1c_fbdump_join.py pattern). Low frames with fewer pass cells => H-data; same pass cells but fewer tris drawn => H-budget (check ROGUESQ_UCODE_CAP). Positive control: dd1 pass counts > 0.
