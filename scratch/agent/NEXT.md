# Next work unit: title-boot plume SIGSEGV (si_addr=0x58) lldb loop
HYPOTHESIS-ID: m6-title-boot-plume-sigsegv

- Flight endurance is closed as clean (s5445: 2/2 nostart holds, ~10 total runs, no crash/stall). Pivot to the secondary M6 item.
- Write soak_queue recipe that boots to title ~8x under lldb (batch mode, `process handle SIGSEGV -s true`), exits at first SIGSEGV with `bt all` + registers into scratch/agent/soak_results; otherwise SIGKILL after title+30 s and re-launch.
- Hypotheses: (H1) null-ish struct deref in plume emitter before init (si_addr 0x58 = field offset in NULL object); (H2) race with audio/VI thread; discriminator = the real backtrace + faulting register source.
- Positive control: lldb must catch a deliberately raised SIGSEGV (kill -SEGV) in the same recipe.
