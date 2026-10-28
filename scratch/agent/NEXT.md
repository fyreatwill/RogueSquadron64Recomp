# NEXT: split the dd4 px crash by cap (s6550 follow-up)
HYPOTHESIS-ID: g1c-dd-phase2
Known (s6550): POOLX=4 (cap 2400) crashes 5/5 at 0x80011524 sw v0,4(a0), a0=0x80000000; BIGARENA divert does not change it (H-heap refuted).
Hypotheses: H-table (a sibling table sized for 2048 cells/600 cap overrun when cap>2048), H-ptr (larger window yields stale mesh node), H-flaky (refuted by 5/5).
Work unit: `zsh scratch/agent/s6549_run.sh 4 3` (cap 1800) then `... 4 2` (cap 1200); each run is ~6 min, run sequentially. Log is scratch/agent/m6/g1_lvl1s6549_dd4_pxN/ (summary file; fail_att*.log hold the CRASH dump).
Outcomes: px3 clean + px4 crash -> threshold between 1800 and 2400 near 2048 -> H-table: grep the generated code for 2048/0x800 sized arrays or 0x1800-sized strides reachable from renderFlatMeshFaceGroup and find the list head via [0x8011-0x5824]. px3 also crashes -> not cap threshold; bisect px2. Positive control: px1 (retail cap) must reach mission.
