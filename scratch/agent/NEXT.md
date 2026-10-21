# NEXT: G1 fold s5716_lvl{8,9}{a,b} soak results (SOAK-RESULTS.md tail; per-run log scratch/agent/m6/<tag>/{run.log,summary}: grep -a lvsel for control a1==1<<N, SIGSEGV/CRASH, vi_stalls30s). lvl1-7 folded clean. Each distinct failure: backtrace, name the writer, fix root cause. If all clean (lvl1-9 done), design the real-input level-select route (no ROGUESQ_FORCE_SAVE_MISSION).
H1: lvl8/9 hit a new crash family; H2: clean like lvl1-7.
HYPOTHESIS-ID: g1-level-select
