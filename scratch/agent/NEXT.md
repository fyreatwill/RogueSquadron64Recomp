# NEXT: find the next binding limit above px3 (px4 / dd=8)
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6573): px3+spill dd6 is 4/4 clean after the TO_PTR mask widening (s6572, s6573).
Work unit: run `zsh scratch/agent/s6553_run.sh 8 4 "ROGUESQ_RAMTOP_MB=16 ROGUESQ_DLPOOLX=1 ROGUESQ_DLPOOLX_MB=4 ROGUESQ_DLPOOLX_AT=3000 ROGUESQ_MALLOC_SPILL=1" A` (one at a time; check run.log for crashlines/vi_stalls30s). Hypotheses: heap/pool exhaustion (raise DLPOOLX_MB), DL segment >16 MB physical, ucode cap, RSP host cost.
Outcomes: clean => try px5/dd=12 and capture terrain-fraction sheet; crash => lldb backtrace, name the writer.
