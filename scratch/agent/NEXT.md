# NEXT (s7376)
HYPOTHESIS-ID: lockless-file-containers

s7375 closed class AS (the 98 s7366 NOLOCK containers; 1 fix: depth-hist diag g_depthMu). It found that s7366 never looked at
files containing no lock at all: 144 containers in 48 files.

Work unit: class AS2. `python3 tools/s7375_nolock_threads.py --lockless -v` lists every container with its accessing functions
and walker thread labels (AUTO-CONFINED / AUTO-GUEST / REVIEW).
Steps (offline census + one build + one TSan run only if a fix lands):
 1. Hand-verdict every REVIEW row in tools/s7375_nolock_reviewed.tsv (same classes: CONFINED / GUEST-SERIAL / HANDOFF /
    INIT-ONLY / CALLER-LOCKED / NOT-SHARED / CFG-DEAD / FIXED); then `--lockless --check` must print OPEN 0. Expect most rows
    NOT-SHARED (name collisions) and RT64 State-driver / per-instance CONFINED (s7375 reasoning: State is driven by one thread at a
    time, the gfx thread or the s6705 RDP-async consumer with rs64_rdpq_drain; the two FramebufferRenderer instances are per thread).
    Watch especially: librecomp (31 rows: overlays/func_map, mods, config, input, save), rt64 common/preset (config read by the
    present thread vs written by the inspector or window events), src (4).
 2. Fix every MULTI (mutex, thread_local, or a magic static); lib/ edits -> ./submodule-patches/export.sh + commit.
 3. Gate: rebuild build/, s7366/s7374/s7375 --check, 260 s smoke (`env SECS=260 zsh scratch/s7326/run.zsh s7376_dd8 ''`); if a
    fix landed, TSan arm `zsh tools/build_tsan.sh` then `zsh scratch/s7375/tsan_run.zsh t1 480 ''` (run it in the foreground with
    a long timeout or with an explicit SIGKILL: s7375's 600 s hold hit the background-task limit and ended by SDL_QUIT) and
    `python3 tools/s7354_tsan_report.py scratch/s7375/t1/run.log` rc 0 with CTL firing.
Hypotheses: H-confined (all 144 resolve to one thread / name collision / handoff: AS2 closes with 0 fixes), H-diag-multi (MULTI only
behind diag env gates: fix anyway), H-live-multi (a MULTI container on the owner path: list it against the parked rare dd4/dd8 gfx
SIGBUS report).
Positive control: the s7375 selftest (planted two-thread container -> REVIEW {gfx, task}; s7374 rs64_s7012_cap shape -> {gfx, guest}).
