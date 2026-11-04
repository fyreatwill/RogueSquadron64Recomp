# NEXT: same exact-match check on lvl5 and lvl10, then name the camera pitch writer
HYPOTHESIS-ID: g3-optin-frame-diff

Why: s6875 found an exact test on lvl1. FPS60 with dt pinned 1/30 (arm ufix) must equal 30 Hz frozen one tick later (arm n1), 0.00. Only lvl1 has been checked.
Hypotheses for lvl5/lvl10: H-match (0.00 again) / H-level (a level draws something tied to the limiter, residual above ~0.1 with camera equal).
Steps: get x crossings from a [poselock] trace (x must rise) and pick them on straight stretches. g3_optin_pose_arms.sh hardcodes LEVEL=1, so add a LEVEL variable first (REF poseref is lvl1 only; use NOREF=1 elsewhere). One batch per level: ufix, n1, n2 as the adjacent-tick control. FZ for n1 = the tick after ufix's freeze pose. MS stays 15000 (4000 is too short). Relative outdir only.
Commands: C=ROGUESQ_G3C_CAMLOG=1; P=ROGUESQ_XTRACE_POKE=800FA730:29:30; env PIN=1 HOLD_S=80 FZ="..." TAGP=s6876 zsh tools/g3_optin_pose_arms.sh scratch/s6876/lvl5 ufix=ROGUESQ_FPS60=1+$C+$P:3d088889 ; then tools/g3_optin_diff.py <dir> --base ufix and tools/g3_cam_at_freeze.py.
Then the pitch: find the writer of 0x80138458 +0x28..+0x48 in flight (a guest write hook or the oracle write watch at physical 0x138458+0x28, whole-RDRAM positive control first). Pitch is 0.06316 at dt 1/30 and 0.06055 at 1/60, craft attitude equal. Add a third dt to test linearity. Do not fix before naming it; 0.15-0.26 deg may not be worth a change, and that is the owner's call.
Also open: lvl5 dd4 cap 2400 trims on-map rows in 5/179 windows (s6875). Check if any such window is on screen in flight.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
