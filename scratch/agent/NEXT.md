# NEXT: finish the FPS60 same-pose comparison, then other levels
HYPOTHESIS-ID: g3-optin-frame-diff

Why: s6872 closed dd4 on lvl1 (H-match, two exact poses) but FPS60 k2 stayed unresolved (13.5, pose differs in y), and the floor exists at k0 only.
Hypotheses: H-phase (FPS60 residual is presented-frame phase plus the y offset) / H-near (FPS60 changes near-field geometry or colour) / H-fork (the two no-input paths explain it).
Discriminator: one build. Fix the fork first: log player pos, hull and hit events per tick between k0 and k1 from rand.txt (ROGUESQ_XTRACE_MEM) in dd1 x3 and fps60 x3, and find what splits z 78.39 / 81.55. Then choose freeze x values on the shared stretch before the fork (x < 58, several points), so every arm has a same-pose pair. Repeat dd1 twice for a floor at each k.
Tools: env FZ="..." MS=15000 zsh tools/g3_optin_pose_arms.sh <dir>; python3 tools/g3_optin_diff.py <dir> --base <arm> --out sheet.png. Compare within a branch only. Holds under 15 s fail: screencapture takes ~4 s.
Then lvl5 and lvl10 with the same tools (the x crossings must be re-chosen from a [poselock] trace; x must rise).
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
