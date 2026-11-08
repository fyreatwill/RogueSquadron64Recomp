# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — fold s6979_219_async_r1/r2 (async stderr default on, whole run, 21:9 lock+QoS1), then name the residual "runnable but no CPU" late leg.
HYPOTHESIS-ID: g1e-gfx-residual-runnable
State (s6979): the Gfx thread's 2-5 ms UNINTERRUPTIBLE waits in late send_dl windows were its own stderr write()s; ROGUESQ_STDERR_ASYNC
default on removed them (same run 12.9 -> 0/min, gaps>3 ms 4.3 -> 0/min). Late presents per run vary 0-5, so their rate needs the soaks.
1. Read SOAK-RESULTS lines for s6979_219_async_r1/r2; logs in scratch/agent/soak_results/, data in scratch/s6979q/. Pooled late30-40/min
   vs 1.04/min (s6978): <~0.3 -> async fixed the 21:9 lates (tell the owner; reconsider whether GFX_QOS still matters at 16:9 with async on);
   ~1/min -> residual lates are the other kind.
2. If residual lates remain: per late window run `python3 tools/g1e_thread_census.py thr.bin win.txt` - the strip shows 'r' samples
   (TH_STATE_RUNNING with <0.2 ms CPU in 1 ms) while CPUs are mostly idle. Hypotheses: H-wake (thread woken from the fullSync GPU semaphore
   but dispatch latency: the strip 'r' follows a 'w'), H-cluster (scheduled onto a parked/idle cluster that has to wake: per-CPU tick
   columns 5-9 are always ~0), H-sampler (the sampler's own thread_suspend/task_threads cost: compare 'r' fraction with
   ROGUESQ_G1E_THREADS_US=4000 vs 1000 in one run each - not same-run, so only a gross change counts), H-rsp-work (sdc high, e.g. T2 661020).
   Discriminator: for each 'r' sample, the previous Gfx state (w -> r = wake latency) and whether any CPU in its cluster was idle.
3. Owner: GFX_QOS default at 16:9 still the owner's call; ask whether the 2>/dev/null tip helped (Terminal held 26 GB).
Defaults: STDERR_ASYNC on (=0 off), everything else unchanged.
