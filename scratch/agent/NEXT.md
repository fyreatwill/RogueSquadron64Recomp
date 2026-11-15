# NEXT (s7377)
HYPOTHESIS-ID: present-thread-shared-maps

s7376 closed class AS2 (lock-free-file containers, 126 verdicts) and fixed the port's present-thread INSERTS into the shared
RT64 targetManager/fbManager (now under workloadMutex; ROGUESQ_S7376_PQLOCK=0 = old). It left the READS: the present thread
still calls fbManager.find / targetManager lookups before it locks workloadMutex.

Work unit: class AT. Enumerate EVERY access to ext.sharedResources-> {framebufferManager, renderTargetManager,
interpolatedColorTargets, fbConfigChanged ...} in lib/rt64/src/hle/rt64_present_queue.cpp (threadPresent, threadLoop) with the
lock held at that line (none / workloadMutex / managerMutex / interpolatedMutex). One small python tool
(tools/s7377_present_lock_table.py) that walks threadPresent tracking `workloadMutex.lock()/unlock()`, scoped_lock and unique_lock
scopes, prints file:line, access, lock state, upstream-or-port (git blame vs upstream tag, or the s/session comment), and a
--check against a reviewed TSV.
Per row verdict: LOCKED / UPSTREAM-UNLOCKED (upstream's own design: viFb find ~line 266, present-time colorFb find) / FIXED.
Candidate fix: in the non-interpolated path (this port never enables RT64 interpolation? VERIFY: grep interpolationEnabled=true
fires; log presentFb->interpolationEnabled once), take workloadMutex at the start of the lookup phase (pqVisibleGate) instead of
at ~line 708, so every find runs under it. Deadlock reasoning from s7376 holds (workload thread under workloadMutex only waits on
GPU workers).
Hypotheses: H-upstream-ok (the unlocked reads are upstream design and only race with map rehash: fix only port-added sites),
H-move-lock (moving the lock earlier is safe and covers all: one change), H-interp (interpolation is live in some arm, so the
present thread must stay lock-free there: per-site locks only).
Gate: rebuild, smoke `env SECS=260 zsh scratch/s7326/run.zsh s7377_dd8 ''` (crash 0, present-1024 rt=yes count ~ s7376),
TSan `zsh tools/build_tsan.sh` + `zsh scratch/s7376/tsan_run.zsh t1 480 ''` copied to scratch/s7377 (foreground, long timeout),
`python3 tools/s7354_tsan_report.py ...` rc 0, CTL fires, 0 lock-order-inversion. Watch frame time: present now waits on the
workload thread earlier; compare heaviest20 / VI rate against s7376 smoke in the same recipe.
Positive control for the tool: the s7376-fixed sites must come out LOCKED, and line ~266 viFb find must come out UNLOCKED.
