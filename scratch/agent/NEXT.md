# NEXT: find where dt enters the camera pitch, starting at buildEffectObjectWorldTransform
HYPOTHESIS-ID: g3-optin-frame-diff

Why: s6876 refuted the attitude dead-band and named the in-place writer of 0x80138480 (buildEffectObjectWorldTransform, 8/10 [camcaller] rows). Pitch at dt 1/20, 1/30, 1/60: 0.06233, 0.06316, 0.06055, not monotonic. dt only takes 1/60 multiples (the game rounds it), so do not use 1/45.
Hypotheses: H-build (the temp matrix a1 0x80165DF8 carries the dt term) / H-quat (updateEffectObjectOrientationQuat's two rare sites set the pitch, then it holds; lvl5 ufix steps once at camlog row 21, which fits) / H-early (set during launch before camlog starts, by another path).
Measure, one build: print [camcaller] every call for the first ~200 ticks of flight, with the word-5 value before and after each call, per host return. The call that changes word 5 selects. Arms u20, u30, u60: lvl1, PIN=1, FZ=99999, HOLD_S=70, ROGUESQ_G3C_CAMLOG=1 ROGUESQ_CAM_CALLER=1 ROGUESQ_WATCH_LOG=1. Resolve: atos -o build/RogueSquadron64Recomp -l 0x100000000 <hra>. Compare with tools/g3_cam_align.py.
Budget: 0.15-0.26 deg of pitch. Name it, do not fix it; a fix is the owner's call. If this does not select in one iteration, close the thread as measured and take the next ladder rung.
Also open: lvl10 cloud clock (VI or wall): only worth a run if an owner report points at clouds.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
