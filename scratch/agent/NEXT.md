# NEXT (s7767)
HYPOTHESIS-ID: owner-report-triage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner answer to docs/OWNER-REVIEW-QUEUE.md
rows, then new SOAK-RESULTS lines after the s7750 fold. Any of those outranks everything (arm table, discriminator, root fix;
an owner "close" -> close that row in the queue + CURRENT-TRUTH).
Do NOT add coverage units, crash-hunt soaks (G4 parked) or repeat holds.
Unit if nothing arrived (G1e latency follow-up, s7766): the present-queue -> photon leg is 26-28 ms (~1.6 VIs) and is the largest
port-only latency term. Hypotheses: H-compositor (CoreAnimation composites the borderless-fullscreen window, +1 frame; direct
scan-out would drop it) vs H-vsync-phase (the wait is the present thread missing the vsync edge; VI_LOCK=1 already moved it -5 ms)
vs H-drawable-wait (nextDrawable blocks; refuted-ish by s7766 DRAWABLES=2 moving the wait upstream).
Discriminator: same tool, same recipe, arms in one session: FULLSCREEN=1 (borderless) vs FULLSCREEN=0 windowed vs any native/
exclusive fullscreen mode RT64/SDL offers, each with VI_LOCK=1; read queue->photon and the ring acq_ms/tp_ms columns.
Commands: `env R=$PWD/scratch/s7767 HOLD=170 ARMS="4:fs:ROGUESQ_VI_LOCK=1+ROGUESQ_G3C_LOG=1+ROGUESQ_S7766_INLAT=1 4:win:ROGUESQ_FULLSCREEN=0+ROGUESQ_VI_LOCK=1+ROGUESQ_G3C_LOG=1+ROGUESQ_S7766_INLAT=1" zsh tools/g1e_owner_quiet_arms.zsh`
then `python3 tools/s7766_inlat.py scratch/s7767/log_<arm>.txt scratch/s7767/ring_<arm>.txt --ctl`.
If windowed == fullscreen, H-compositor is refuted for borderless and the leg is vsync phase; stop there (owner opt-in VI_LOCK already covers it).
