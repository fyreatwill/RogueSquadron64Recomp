# M5 session 3758 — native task-data watch coverage

The native task-data page watcher was extended with bounded target-window
entry, heartbeat, exit, arm, re-arm, and coverage-gap counters. The same Debug
build ran real (`ROGUESQ_AUDIO_UCODE=1`) and silent (`=0`) arms concurrently for
75 seconds with the validated LLE/autopilot route.

The real arm crashed before a target VI window in `spTaskSchedulerThread+9556`
(`SIGSEGV`, `si_addr=0x400128d47`). The silent arm passed the page positive
control, held the target page armed for 24,125 title ticks, and reached hangar
with 14,487 later target ticks/re-arms. Neither arm emitted a target-range
fault, decoded store, or post-store sample.

This is incomplete paired coverage, not a global no-store result: silent is the
no-audio control and real did not reach target. No mitigation is authorized.

Raw logs: `scratch/agent/s3757_m5_task_value_retry/{real,silent}.log`.
