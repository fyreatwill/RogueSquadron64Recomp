# Next work unit: work-vs-contention split for the slow audio run_task at t~19-26 (s4248)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4247: audio run_task wall time per task jumps 6-11 ms -> 60-860 ms at t~19-26 s (2/2 runs); setnext stays 60/s; gfx never hits run_task.
Hypotheses: (c1) the ucode does far more RSP work per task (instruction count / voices / DMA bytes spike); (c2) same work, host contention (gfx thread shader compile, Metal) inflates wall time.
Discriminator: in run_task, count RSP instructions executed (or interpreter steps) and DMA bytes per audio task, and also thread CPU time (clock_gettime CLOCK_THREAD_CPUTIME_ID) next to wall time. Outcomes: instr count spikes ~100x => (c1), chase the command list/voice count; instr flat but CPU time ≈ wall => host-side slow path (cache/page faults); CPU time << wall => (c2) preemption/contention.
Positive control: pre-stall windows must show instr/ms stable and cpu≈wall; also log the guest audio-task data_size so it correlates.
Extend S4245Guard (lib/N64ModernRuntime/librecomp/src/rsp.cpp) + rs64_s4245_tick (ai.cpp); rebuild; run scratch/agent/s4245_rates.sh with RUN_IDS=21 then 22 (one at a time, env prefix); export.sh + commit.
