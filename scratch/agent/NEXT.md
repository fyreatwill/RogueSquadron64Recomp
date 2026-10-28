# NEXT: confirm the TO_PTR 8 MB-alias fix (s6572) and re-measure dd3/dd4
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6572): TO_PTR mask 0x7FFFFF aliased >8 MB guest queues onto low RAM; widened to 0x1FFFFFF; px3+spill 1/1 clean (was 8/8 fault).
Work unit: (1) 3 more runs of `zsh scratch/agent/s6553_run.sh 6 3 "ROGUESQ_RAMTOP_MB=16 ROGUESQ_DLPOOLX=1 ROGUESQ_DLPOOLX_MB=4 ROGUESQ_DLPOOLX_AT=3000 ROGUESQ_MALLOC_SPILL=1" A|B|C` ONE AT A TIME (kill old drivers by PID first); expect 0 CRASH each. (2) Same at px4 / dd=8 to find the next binding limit. (3) grep the same bug class: host `& 0x7FFFFF` on guest pointers in lib/N64ModernRuntime and src/main (ultramodern/librecomp send/recv/thread paths); classify each as aliasing >8 MB or not.
Outcomes: 3/3 clean => close px3 fault, move on to px4; any crash => take its backtrace, the alias class may have more members.
