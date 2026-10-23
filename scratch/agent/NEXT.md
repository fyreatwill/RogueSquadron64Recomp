# NEXT: loop title boots under lldb until the plume SIGSEGV (si_addr=0x58) recurs
HYPOTHESIS-ID: g4-mission-soaks
Levels 0-9 hold clean (s5985). Queue a soak script in scratch/agent/soak_queue/ that boots to title N times (~1/7 rate, so >=14 boots) under lldb batch mode, SIGKILLs each, and on a crash saves `bt all` + registers. If it recurs: name the writer of the faulting pointer, root-cause. Positive control: lldb must attach and report exit status on a deliberately killed run. After that: G1 (d) forced-hit objective counters per level (s5841 TELE lever).
