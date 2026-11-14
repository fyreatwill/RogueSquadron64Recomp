# NEXT (s7354): idiom-class audit - class AE, data races on non-atomic host globals shared across host threads
HYPOTHESIS-ID: host-global-data-race
Context: s7353 closed class AD (tools/s7353_boolenum_census.py: 19 sites, 0 open, UBSan control tools/s7353_boolenum_ctl.cpp PASS).
Idiom: a non-atomic, non-const file-scope global / class static / function-local static written on one host thread and read
(or written) on another with no mutex / atomic / happens-before (thread start, join, condvar). UB; on arm64 it gives torn or stale
reads, and clang may hoist loads out of polling loops (a `while (!flag)` that never exits = a hang).
Threads (grep std::thread, s7353): game thread (recomp.cpp:876, guest threads in ultramodern threads.cpp), events.cpp gfx_thread /
task_thread (:593-594) + VI thread (:503) + timer.cpp:43, pi.cpp saving_thread (:415), mesgqueue.cpp :632/:788 watchdogs,
RT64 present/workload threads (lib/rt64/src/hle/rt64_*_queue.cpp), src/main/rt64_render_context.cpp:1627 worker,
upstream_compat.cpp diag threads (:2658/:2685/:2792/:5619/:6266/:8053/:8388), main.cpp:2107 s4578_poll, s7331_reset_writer poll,
threads.cpp sampler (:288) + thread_cleaner (:744), mods.cpp:935.
Hypotheses: H-safe (every cross-thread global is std::atomic / under a mutex / written once before the reader thread starts),
H-diag (racy globals exist only in env-gated diag threads / counters, retail recipe unaffected), H-race (a default-on global
shared by gfx/task/VI/game threads with plain loads/stores: fix with std::atomic + the right memory order).
Method: new tools/s7354_race_census.py on the s7343 scope + RT64 shared. (1) Thread map: for each thread entry above, the set of
functions reachable within the same file + 1 cross-file call level (name match). (2) Globals: file-scope / static-member / static-
local non-const non-atomic, non-thread_local declarations (reuse s7344 decl). (3) Site = a global written in a function reached from
thread A and accessed in a function reached from thread B != A. Classes: ATOM (std::atomic / volatile sig_atomic), MTX (every access
in a scope holding a lock_guard/unique_lock/scoped_lock on the same mutex), ONCE (written only before the thread is started or under
call_once, read after), ST (all accessors on one thread), D/G/P (diag-gated), H, B, ?.
Controls: planted `static int g_flag; void a(){ g_flag = 1; } void b(){ while(!g_flag){} }` with std::thread(a) / std::thread(b)
('?'), std::atomic twin (ATOM), mutex twin (MTX), single-thread twin (ST), gated twin (G).
Second line: TSan standalone control for any B fix (clang++ -fsanitize=thread) reproducing the race shape, then
`env SECS=260 zsh scratch/s7326/run.zsh s7354_dd8 ''`.
Exit: PORTING-STATE s7354, CURRENT-TRUTH item 27s -> closed/fixed, commit.
