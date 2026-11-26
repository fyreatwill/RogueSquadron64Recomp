# NEXT (s7970)
HYPOTHESIS-ID: post-preset-class-ladder
s7969 closed class UE: the game volume vanishing mid-run. Exe on it livelocked (code pages un-pageable) -> re-exec from a local copy
(src/main/rs64_ue.h, ROGUESQ_S7969_RELOC=0 = old); saves/ on it -> one report per failure streak, "back" line, quit Retry dialog
(ROGUESQ_S7969_UE=0 = old). Gate S7969_UE, e2e tools/s7969_ue_e2e.zsh. Do not redo UE, XF, CS, DI, RO, AN, PS, SD, DR, RD, FW, CK, LC,
TF, EV.
An src/ or lib/ edit needs the FULL sweep (`python3 -u tools/s7651_gate_sweep.py --jobs 2`, ~30 min: run it in the background).
Test-script note (s7969): a zsh background job inherits SIGINT as SIG_IGN, so SDL never turns it into SDL_QUIT; drive the quit path
with SIGHUP (s7594 handler -> flush + quick_exit).
0. `python3 tools/crash_reports.py --since 2026-11-26`. Fold any new SOAK-RESULTS lines.
1. Ladder 3c, new host class SW: the process is frozen for a long time and resumed (system sleep / lid close, App Nap, a debugger
   stop). The host clock jumps by minutes between two VI ticks. Proxy without sleeping the owner's Mac: SIGSTOP the game for 60 s
   and 300 s, then SIGCONT (never `pmset sleepnow`).
   Hypotheses:
   - H-burst: VI/timer threads try to catch up on the missed time (thousands of VIs or audio buffers queued at once), so the game
     fast-forwards, spins, or the audio queue overflows.
   - H-stall: a wait with an absolute deadline or a watchdog (s3290-stall, waitForMusyXAudioTaskDone, RT64 present fences) fires on
     resume and aborts or deadlocks.
   - H-audio: the audio device stops/changes over a real sleep (SIGSTOP does not reproduce this part; note it as not covered).
   - H-moot: one long frame then normal pacing.
   Discriminator, one build, one game at a time: private copy, NO_SAVE_WRITE, present ring (ROGUESQ VI_STAMP / ring_stalls.py) and
   [ai] cadence logging on; arms: control (no stop), stop 60 s, stop 300 s, each at t=20 s on the title and once in flight (forced
   level route). Measure for 30 s after SIGCONT: VIs/s per second (burst = >>60), max present gap, audio queue depth, crash/abort.
   Fix only what is ours (e.g. clamp the catch-up to a few VIs); add a gate.
