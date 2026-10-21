# NEXT: G1 fold s5715_lvl{2,3,5}{a,b} soak results (tail SOAK-RESULTS.md, grep CRASH/SIGSEGV/stall in logs, confirm [lvsel] init control a1==1<<N). Each distinct failure: backtrace, name the writer, fix root cause. If all clean, queue lvl8+/remaining missions and real-input (non-forced) route.
H1: other missions crash on a new family; H2: soak clean like lvl1/4/6/7.
HYPOTHESIS-ID: g1-level-select
