# NEXT: G1 - s5877: find the upstream writer that arms the player's 0.5 s crash fuse
Hypotheses: (a) legit ground impact (y descends smoothly from altitude); (c) wrong terrain/y (y snaps below terrain, or terrain query too high).
Measure: grep stores to 0x184($reg) in N64Recomp/RecompiledFuncs/funcs_*.c (swc1/sw), identify the one that writes 0.5 with flags|=0x10 for slot 0; log y, terrain(0x80067D90 result), speed, caller ra there (ROGUESQ_LOG_MTM), one build, one run of the s5876 recipe (scratch/agent/g1_pos_pdump.sh, AP_TITLE_N=17 AP_HOLD=600).
Control: [bit1] a0=1 fires in same run and the new log precedes it.
HYPOTHESIS-ID: g1-mission-progression
