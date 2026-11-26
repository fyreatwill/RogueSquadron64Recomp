# NEXT (s7971)
HYPOTHESIS-ID: post-preset-class-ladder
s7970 closed class SW (process frozen then resumed, SIGSTOP/SIGCONT proxy): video, game clock and quit were fine on resume;
audio was not. After a stop the device drained the SDL queue at ~3.3x real time for ~0.18x the stop length (15 s -> 3 s, 60 s ->
10.5 s, 300 s -> the whole 30 s watch), so the game posted 3.3x audio with ~94 empty-queue posts/s (skipping audio). Sometimes
the drain-stall watchdog fired instead (a 180 ms reopen as "drain-stall"), which had no burst. Fix (main.cpp s7970): a 50 ms
heartbeat thread sees a > 1 s whole-process freeze; the next audio post resets the drain-stall clock and reopens the device once
with why=resume. ROGUESQ_S7970_SW=0 = old. Gate S7970_SW. Do not redo SW, UE, XF, CS, DI, RO, AN, PS, SD, DR, RD, FW, CK, LC, TF, EV.
Not covered by SW: a REAL system sleep (the audio device and display stop too; the SIGSTOP proxy cannot show that).

## Work unit: ladder 3c host class MP (system memory pressure while the game runs)
Proxy without harming the owner's Mac: `memory_pressure -S -l warn` then `-l critical` (simulated pressure notification, no real
allocation), and a bounded real-allocation arm (a helper that mallocs + touches N GB and holds it for 60 s, N sized from
`sysctl hw.memsize` and `vm_stat` free pages so the host never swaps hard). Run in flight (forced route, tools/s7970_sw_e2e.zsh is the
template: private game copy, save COPIED, ROGUESQ_NO_SAVE_WRITE=1, present ring + ROGUESQ_AI_TRACE, SIGHUP quit timing).
Hypotheses:
- H-jetsam: the game is killed or a Metal resource allocation fails (RT64 texture/pipeline creation returns nil) -> crash or
  missing draws. Outcome: death, crash report, `[RT64]` alloc errors, or a black frame.
- H-compress: the 512 MB rdram mapping / texture caches get compressed or swapped out -> long frames when touched again.
  Outcome: present gaps > 250 ms, VI holds, AI underruns during or just after pressure.
- H-handler: someone registered a memory-pressure dispatch source (SDL, RT64, MoltenVK-free Metal path) that drops caches and
  rebuilds them badly. Outcome: a log line at the notification plus a frame-time spike right after it.
- H-moot: presents 60/s, swaps unchanged, 0 underruns, quit < 1 s.
Positive control: a planted present gap / underrun in the scorer selftest (reuse s7970_sw_score.py's planted cases) and a control
arm with no pressure in the same run set.

## Commands (one game at a time)
0. `python3 tools/crash_reports.py --since 2026-11-26`; fold any new SOAK-RESULTS lines.
1. `memory_pressure -h` (check it runs without sudo; if it needs sudo, use only the real-allocation arm and say so).
2. Write tools/s7971_mp_e2e.zsh (template s7970_sw_e2e.zsh; arms control / warn / critical / alloc), score with
   tools/s7970_sw_score.py-style windows anchored on the pressure start time instead of a ring gap.
3. Fix only what is ours; gate tools/s7971_mp_gate.py (STATIC if a fix lands, E2E, CONTROL), add S7971_MP to s7651 ARGS +
   EXTRA_GATES, review rows for any new thread/loop/atomic/env (s7381/s7382/s7383/s7597/s7714 went UNREVIEWED on s7970's heartbeat
   until rows were added), then `python3 -u tools/s7651_gate_sweep.py --jobs 2 > /tmp/s7971_sweep.txt 2>&1` in the background
   AFTER the last game run (one game at a time; the sweep itself is 2 jobs).
If H-moot holds on every arm with the control passing, close MP with no code change (the e2e + gate are the deliverable).
