# NEXT: pair CAPX=2 with a bigger DL-chunk pool on lvl7 dd4
HYPOTHESIS-ID: g1c-dd-phase2
State (s6586): ROGUESQ_DD_CAPX=2 crashes lvl7 dd4 5/5 (0x380000022 NULL list node) in the 2x window; 0/10 without. Cap = pool capacity.
Work unit: rerun scratch/agent/s6586_run.sh with the DLPOOLX env (see main.cpp bundle, currently 4MB@3000) doubled (find its env name via grep DLPOOLX main.cpp) and MISSION_RE=62BD00 so the harness passes. Hypotheses: H-pool (crash disappears => cap/pool pair is the lever, bundle it for lvl3/7), H-other (crash persists => another per-cell array bounds it; read pc 0x800547bc function).
Outcomes: 0 crashes with blk=1 samples >2800 cells over 300 s => bundle; crash persists => disassemble 0x800547bc.
