# NEXT: fold the edge soaks, then FPS60 k0/k1, then other levels
HYPOTHESIS-ID: g3-optin-frame-diff

First read SOAK-RESULTS for s6874_edge_dd4_lvl5 and s6874_edge_dd4_lvl10. A crash or stall there comes from the off-map window (ROGUESQ_DD_EDGE): compare against =0 on the same level before anything else. Check [ddclamp] pre/post in those logs for windows that trim real terrain.
Why: s6874 closed the dd step at k2 (ddclamp cut retail's off-map border). FPS60 at k0/k1 still differs from 30 Hz at the same pose (s6873: MAD 8.75, best alignment dy 2 sky to dy 6 ground), with no camera dump.
Hypotheses: H-camera (FPS60 camera follow state differs at equal craft pose) / H-frame-age (presented frame is a different tick; s6873 estimate says too small) / H-near (FPS60 changes geometry or colour).
Discriminator: one build, pinned arms: dump the camera block ([camlog] / 0x80138D1C, ROGUESQ XMEM spec) at the freezes in dd1 and fps60. Camera equal with frames different -> H-near; camera different by the observed dy -> H-camera, then decide if it is a rate defect or expected follow lag.
Tools: env PIN=1 FZ="..." HOLD_S=80 zsh tools/g3_optin_pose_arms.sh <RELATIVE dir> arm=...; an absolute dir voids the run (s6874). Always rerun a dd1 control after a rebuild; the first arm after a rebuild gave an unexplained frame in s6874.
Then lvl5 and lvl10 with the same tools (x crossings re-chosen from a [poselock] trace; x must rise).
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
