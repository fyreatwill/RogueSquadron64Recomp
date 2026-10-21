# NEXT: fold s5712_lvl7a/b/c soak verdicts (history-desync fix).
Check scratch/agent/m6/s5712_lvl7*/run.log: grep -c 'SKIP_WILD_W' (positive control, must be >=1 in some run) and grep -c 'exceeds readback' (expect 0; s5710 had 2 in 1/2 runs). If 0 with control present -> fix confirmed; the guard stays as defence.
Then remaining open: who emits the w=442 SetColorImage (H1 misparsed data vs H2 real). Log raw RDP word + DL ptr at first SKIP_WILD_W in rt64_state.cpp rs64_writeback_sane caller, one build, lvl7 x3.
Any lib/ edit => ./submodule-patches/export.sh + commit.
HYPOTHESIS-ID: g1-level-select
