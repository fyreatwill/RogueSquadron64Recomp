# NEXT: G1c phase 2 - next binding limit past dd4 (dd6, 0x80800000 pool)
HYPOTHESIS-ID: g1c-dd-phase2
State: s6546 settled cap0 vs inf (inf draws the terrain; owner to choose default, ~1.7x wall). Owner question pending: make dd>1 default cap inf?
Work unit: run lvl1 pinned recipe (scratch/agent/s6546_run.sh, CAP_ALT off, ROGUESQ_BYPASS_MAXCELLS=-1 i.e. inf) at ROGUESQ_DRAW_DISTANCE=6 with ROGUESQ_DD_UNSAFE=1; record crash point / heap exhaustion (s6062 8 MB heap). If heap, carve terrain pool from 0x80800000+ (DL-read data must stay <0x81000000). Positive control: dd4 same recipe passes.
Outcomes: clean -> measure terrain fraction + wall vs dd4; heap exhaust -> implement second arena; then switch to G3c(b)/(c).
