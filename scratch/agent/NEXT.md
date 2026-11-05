# NEXT: why is present-to-screen 57 ms at 60 fps? Measure drawable depth
HYPOTHESIS-ID: g1e-present-latency
Why: s6885 ring shows Q stamp to presentedTime p50 ~57 ms in FPS60 arms, 26-36 at 30 fps, acq p99 ~16 ms (present thread waits in nextDrawable). One arm (w43d4) read p50 36.7, p99 56.8. That is ~3 frames of input lag at 60 fps, if real. Single-source so far.
First: fold SOAK-RESULTS for s6884_job_lvl5 (log scratch/agent/m6/g1_lvl5s6884_joblvl5). It ran on the s6885 binary; score with tools/g1e_arm_rate.py s6884 joblvl5 --lvl 5. A crash there outranks this.
Hypotheses: H-depth (CAMetalLayer queue full: 3 drawables, steady state 3 frames deep) / H-sched (present goes out via addScheduledHandler after the wait, so it misses a vsync) / H-bistable (depth settles at 2 or 3 by startup phase).
Measure, one build: env knob for layer maximumDrawableCount 2 vs 3 in plume_metal.cpp, plus per-second latency in tools/g1e_present_ring.py to see if it switches level inside a run. Arms, lvl1 4:3 dd1 and 21:9 dd4, scratch/s6885/bridge.zsh with ROGUESQ_PRESENT_RING. Control: 30 fps arm. Any lib/ edit needs export.sh + commit.
Outcomes: H-depth -> depth 2 lowers p50 ~17 ms; check on-screen stays 60 and game rate holds, opt-in first. H-sched -> present earlier. H-bistable -> find what sets the level, pin the low one. Note the stamp is taken after the present call, so true latency is longer by tp_ms.
Also open: 16:9 not run through the ring (VI width 768, excluded by reasoning only); add one arm.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: does 21:9 flight feel smoother after s6885 (ROGUESQ_WIDE_EARLY=0 compares); SCREEN_JOB default; add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6883_spancell.png, docs/owner_sheet_s6882_219_dd4.png, docs/owner_sheet_s6881_wide_dd4.png, docs/owner_sheet_s6880_219_depth.png, docs/owner_sheet_s6879_wide_depth.png, docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open from s6884: decodeVI now runs on the worker up to one tail after the VI. FAST vs PROBES not split. Best sx gap: 4:3 box 1106 px is +0.82%, not closed.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous, 21:9 lvl5/lvl10 at 300 s. lvl10 cloud clock only on an owner report.
