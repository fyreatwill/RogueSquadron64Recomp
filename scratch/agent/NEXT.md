# NEXT (s7436)
HYPOTHESIS-ID: host-alloc-cost

Class CS (CURRENT-TRUTH Next steps item 1): per-frame host heap allocation cost (G1b H-host family after CM-CR). On 5 P-cores,
malloc/free churn on the Gfx, guest MAIN and RT64 threads is CPU the game threads compete for, and macOS xzm/nanov2 locks can
serialize threads.
Step 1 (offline, no build, no run): new tools/s7436_alloc_cost.py over scratch/s7435/sample_*.txt (+ samples.idx, run.tlog flip
lines; owner recipe FPS60 dd4 16:9, lvl1 flight, 8 x 12 s windows; reuse the parse() of tools/s7435_spin_cost.py). Per thread and
per window: self samples in allocator frames (malloc, free, calloc, realloc, operator new/delete, _xzm_*, xzm_*, nanov2_*, szone_*,
_malloc_zone_*, mfm_*), plus the innermost OWNED caller of every allocator sample (std::vector growth -> its owner frame).
In-capture positive control: the ctrl column (rs64_diag_spin_us, busy=1 minus busy=0) must read back ~0.030 core as in s7435.
Hypotheses: H-free (allocator total < 0.02 core, close), H-hot (one owned caller >= 0.01 core / >= 0.15 ms/frame on Gfx or MAIN ->
fix: reserve/reuse the buffer, kill-switch env, then a same-run toggled run with the control), H-lock (allocator samples sit in
lock waits (__ulock_wait / _os_unfair_lock_lock_slow under malloc) >= 0.01 core -> contention, name the two threads).
Discriminator: allocator share per thread + top owned callers. If H-free: close CS and take the next 3c rung (new idiom class).
