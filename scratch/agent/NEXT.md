# NEXT (s7970)
HYPOTHESIS-ID: post-preset-class-ladder
s7969 (committed 874a6e7b7 on the retry iteration) closed class UE: exe on a vanished volume re-execs from a local copy
(src/main/rs64_ue.h, ROGUESQ_S7969_RELOC=0 = old); saves/ on it -> one report per streak, "back" line, quit Retry
(ROGUESQ_S7969_UE=0 = old). Gate S7969_UE. Sweep 273: 270 GREEN + 3 REPORT, 0 RED. Do not redo UE, XF, CS, DI, RO, AN, PS, SD,
DR, RD, FW, CK, LC, TF, EV.
Lesson from s7969: the full sweep takes ~26 min. Start it in the background EARLY (right after the build), and add review rows to
s7381 (spin loops) / s7382 + s7597 (threads) / s7595 (save I/O) / s7714 (env readers) for every new loop, thread, fs call or env
name in the same edit: those 5 gates went RED on s7969's own sites.
Test-script note: background-job SIGINT is SIG_IGN; drive the quit path with SIGHUP (s7594 handler -> flush + quick_exit).

## Work unit: ladder 3c host class SW (process frozen for minutes, then resumed: sleep / lid close / App Nap / debugger)
Proxy without sleeping the owner's Mac: SIGSTOP the game, then SIGCONT (never `pmset sleepnow`).
Hypotheses:
- H-burst: VI/timer threads catch up on the missed time (thousands of VIs or audio buffers at once): fast-forward, spin, or
  audio queue overflow. Outcome: VIs/s >> 60 in the first seconds after SIGCONT, or AI queue depth jumps.
- H-stall: an absolute-deadline wait or watchdog (s3290-stall, waitForMusyXAudioTaskDone, RT64 present fences, s7593 quit
  latency) fires on resume -> abort / deadlock. Outcome: abort line, crash report, or VI frozen > 5 s after SIGCONT.
- H-audio: the audio device changes across a real sleep. SIGSTOP cannot show this; record it as not covered.
- H-moot: one long frame, then normal pacing. Outcome: VIs/s back to 60 +-2 within 2 s, max present gap ~= stop length only.

## Commands (one game at a time, private copy, owner save untouched)
0. `python3 tools/crash_reports.py --since 2026-11-26`; fold any new SOAK-RESULTS lines.
1. Write tools/s7970_sw_e2e.zsh modelled on tools/s7969_ue_e2e.zsh (private game copy under /tmp, save COPIED, env
   ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_PRESENT_RING=1 plus the [ai] cadence log). Arms: control (no stop), stop 60 s, stop 300 s
   at t=20 s on the title; then the same three in flight via the forced level route (ROGUESQ_FORCE_UNLOCK=1
   ROGUESQ_FORCE_SAVE_MISSION=1, s5705 recipe). Per arm: `kill -STOP $pid; sleep N; kill -CONT $pid`, watch 30 s,
   then SIGHUP and measure HUP->exit; SIGKILL after 15 s.
2. Score each arm: VIs/s per second for 30 s after SIGCONT, max present gap (tools/g1e_present_cadence.py on the ring),
   AI queue depth, abort/crash lines, quit latency. Positive control: a planted burst (e.g. an env-gated "inject 600 VIs"
   test plant, or the control arm's own 60/s) must score as burst / normal respectively in the same harness.
3. Fix only what is ours (e.g. clamp the VI/audio catch-up to a few ticks; env =0 restores old). Add gate tools/s7970_sw_gate.py
   (STATIC + E2E + planted-FAIL CONTROL) to s7651 ARGS + EXTRA_GATES, add review rows for new sites, then
   `python3 -u tools/s7651_gate_sweep.py --jobs 2 > /tmp/s7970_sweep.txt 2>&1` in the background. Target: 0 RED.
If H-moot holds on all 6 arms with the control passing, close class SW with no code change (the e2e + gate are the deliverable).
