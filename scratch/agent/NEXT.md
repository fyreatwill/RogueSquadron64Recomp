# NEXT: fold the _zs sky-regression soaks

HYPOTHESIS-ID: g3-render-fidelity

Queued s5972: g1_lvl{1,2,3,4,5,7,8,9}_zs (default build, FIX_ZERO_SHADE OFF). When SOAK-RESULTS shows them, compare late-hold fbd frames in scratch/agent/m6/g1_lvlNzs/fbd against baseline m6/g1_lvlNctl/fbd (fix ON). H1: sky identical/fine -> flip safe, close. H2: a level has black sky/untextured terrain -> re-enable the fix narrowly for that DL (name the DL, not a global flag). Then continue G1 (c) review. No aim/steer work.
