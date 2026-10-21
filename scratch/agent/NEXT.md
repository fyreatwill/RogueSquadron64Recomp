# NEXT: read s5705_unlock3 / s5705_unlock5 soak logs (scratch/agent/soak_results/). Control: `[lvsel] B2F=N forced=N` present. Then: init a3==N, tick ret==N, B40 stays N, and [mfst]/initMission names for level N vs level 2.
Hypotheses: H5 level N initialises when unlock=N; H6 mission load fails/crashes for N>2 (then capture backtrace, name writer).
Discriminator: grep '\[lvsel\]' and '\[mfst\]' in both logs; compare to s5704_lvsel_f0 baseline.
HYPOTHESIS-ID: g1-level-select
