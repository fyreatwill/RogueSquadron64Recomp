# NEXT (s7375)
HYPOTHESIS-ID: nolock-container-threads

s7374 closed class AR (lazy-init statics; tools/s7374_lazy_static_census.py, 1 multi-thread site fixed: rs64_s7012_cap).

Work unit: idiom class AS, the s7366 NOLOCK containers. `python3 tools/s7366_lockset_census.py` reports 158 containers:
CONSISTENT 21, MIXED 39 (reviewed s7366/s7373), **NOLOCK 98 never reviewed** — s7366 assumed "thread-confined or handed off by
queue". That assumption is exactly what s7374 found false for rs64_s7012_cap (a guest-only helper later given a gfx-thread caller).
Steps (offline census + one build + one TSan run):
 1. tools/s7375_nolock_threads.py: for each NOLOCK container, list its accessing functions (reuse s7366 scan rows) and give each
    function a calling thread with the s7374 method: gfx_thread (events.cpp gfx_thread_func -> send_dl / update_screen / RT64 State
    / factor5_gfx_runner / factor5 ucode TUs), task_thread (task_thread_func -> rsp.cpp run_task, audio ucode), main (SDL pump,
    poll_input, window), present (rt64 present queue), audio SDL callback, vi_thread, GUEST-SERIAL (recompiled hooks, get_input,
    os*_recomp). Auto-attribute by a caller walk over the scope (call graph by name, depth <= 4), hand-verdict the rest in
    tools/s7375_nolock_reviewed.tsv. --selftest with planted one-thread / two-thread / queue-handoff containers.
 2. Classes: CONFINED (one thread), GUEST-SERIAL, HANDOFF (moodycamel/blocking queue or a join/semaphore between the threads,
    cite the line), INIT-ONLY (filled before the second thread is created), MULTI (defect -> fix with a mutex or thread_local).
 3. Fix every MULTI; lib/ edits -> ./submodule-patches/export.sh + commit.
 4. Gate: rebuild build/, host censuses --controls, s7374 census --check, 260 s smoke
    (`env SECS=260 zsh scratch/s7326/run.zsh s7375_dd8 ''`), TSan arm (`zsh tools/build_tsan.sh` then
    `zsh scratch/s7374/tsan_run.zsh t1 600 ''` adapted) with RACE_CTL control firing and 0 unclassified groups.
Hypotheses: H-confined (all 98 CONFINED/GUEST-SERIAL/HANDOFF/INIT-ONLY: AS closes with 0 fixes), H-diag-multi (MULTI only behind
diag env gates, like s7374: fix anyway), H-live-multi (a MULTI container on the owner path: candidate for the parked rare dd4/dd8
gfx SIGBUS; list it against that report).
Positive control for the walker: rs64_s7012_cap must attribute to guest + gfx_thread (the s7374 hand result) when fed as a
synthetic row.
