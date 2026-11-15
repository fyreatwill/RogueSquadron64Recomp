# NEXT (s7384)
HYPOTHESIS-ID: host-static-shared-state

s7383 closed class AY (atomic memory ordering): 249 atomics / 585 explicit-order ops + 16 static volatiles, census
tools/s7383_atomic_order_census.py --check rc 0 (verdicts tools/s7383_atomic_reviewed.tsv). One default-path defect fixed:
the last-drawn framebuffer tuple (addr / width / siz as three relaxed atomics) read unlocked by follow-draw mode 3 ->
now one packed 64-bit word, store-release / load-acquire (ROGUESQ_S7383_FBPACK=0 old; tear counter ROGUESQ_S7383_LOG=1,
control ROGUESQ_S7383_TEAR_CTL=1).

Work unit: class AZ, every NON-atomic function-local `static` or file-scope mutable variable (not const, not
std::atomic, not thread_local) in src/main, src/rsp, lib/rt64/src/{hle,render}, lib/N64ModernRuntime/{ultramodern,librecomp}/src
that is written in a function reachable from more than one host thread (game thread, Gfx/RSP task thread, VI thread,
RT64 workload / present threads, audio callback). AY only covered variables that are already atomic; a plain static
counter or "seen" cache written from two threads is a data race TSan only reports if the route exercises both writers.
Hypotheses: H-confined (every such static is touched by one thread; the thread is named in the verdict),
H-locked (a mutex covers every writer), H-race (a plain static is written by >=2 threads with no lock: fix to atomic /
thread_local / lock), H-diag-only (races exist only in env-gated logging statics: rate-limit counters).
Discriminator: census tool tools/s7384_static_state_census.py (thread attribution by entry-point call graph roots:
osViSwapBuffer / recomp game funcs, rsp task entry, vi_thread_func, WorkloadQueue::threadLoop, PresentQueue::threadLoop,
audio callback) with --check (exit 1 on an unreviewed multi-thread non-diag row) and --controls (a planted static written
from two planted thread roots must classify MULTI; a planted static under a lock_guard must classify LOCKED). For every
H-race row on a default path: fix, then TSan arm (tools/build_tsan.sh, scratch/s7377/tsan_run.zsh t1 480,
ROGUESQ_S7354_RACE_CTL=1 must report) and smoke `env SECS=200 zsh scratch/s7326/run.zsh s7384_smoke ''` (crash 0).
Expected: H-confined/H-locked/H-diag-only -> close with the table; H-race -> fix list + TSan before/after.
