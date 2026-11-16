# NEXT (s7435)
HYPOTHESIS-ID: host-spin-loops

Class CR (CURRENT-TRUTH Next steps item 1): host busy-wait / poll loops (G1b H-host: only 5 P-cores; every spinning host
thread competes with the guest MAIN and Gfx threads). s7434 lead from the s7433 sample(1) captures (scratch/s7433/sample_{4,8}.txt,
owner recipe dd4 16:9 FPS60, lvl1 flight): the VI Thread shows ~290 samples per 12 s window as self time in mach_continuous_time /
clock_gettime_nsec_np, i.e. a clock-polling loop (~3% of one core). wait_for_resumed self 7% on guest threads is the moodycamel
semaphore spin (s7433 note).
Step 1 (offline, no build): grep-enumerate the whole idiom class in src/ and lib/N64ModernRuntime (and lib/rt64/src only for
rs64-patched code): `while (...clock|mach_absolute_time|mach_continuous_time|now()...)` loops, `std::this_thread::yield` /
`sched_yield` / `__builtin_arm_yield` / `_mm_pause` loops, spin-count semaphores (moodycamel LightweightSemaphore spin count),
`while (!flag.load())` without a wait. Classify every site: tail-spin (bounded, after a sleep), unbounded spin, diag-only
(env-gated), dead. Table in the session entry, with file:line.
Step 2: per live default-on site, its CPU from the s7433 samples (tools/s7434_gfx_glue.py --threads '<thread name>' gives the
owned-frame split). Hypotheses: H-tail (every live spin is a bounded tail after a sleep, total < 0.05 core -> close),
H-spin (a site spins unbounded or for > 1 ms per wake, >= 0.1 core -> fix to a timed wait, kill-switch env, same-run toggle
qualification with a control), H-sem (the moodycamel spin count before blocking is the largest term -> lower it behind an env and
measure tasks/s + thread CPU in one toggled run).
Discriminator: per-site share of a core; positive control in any run: a planted ROGUESQ_DIAG_BUSY_US spin must read back.
If H-tail: close CR and take the next 3c rung (new idiom class; renaming is closed since s6868).
