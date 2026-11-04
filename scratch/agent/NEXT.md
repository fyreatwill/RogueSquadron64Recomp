# NEXT: G3 in-flight frame diffs at the opt-in settings
HYPOTHESIS-ID: g3-optin-frame-diff

Why: ladder rung after elf-size-valid-tails (closed s6871). G3 matched retail at retail settings only. FPS60, dd2 and dd4 are what the owner plays, and nothing compares their near field to retail.
Hypotheses: H-match (near field equals the dd1 retail-matched frame; the only change is extra far terrain) / H-near (an opt-in changes geometry or colour inside the retail draw range) / H-phase (differences are camera phase only: FPS60 frames fall between retail's).
Discriminator: same pose, ROGUESQ_POSE_LOCK=1 + ROGUESQ_POSE_PIN_POSITION=1, lvl1 flight. One build, arms dd1, dd2, dd4, FPS60, FPS60+dd4. Window captures, P3 -> sRGB, `--dec shift` (see CURRENT-TRUTH G3 bullet). Score tools/g3_oracle_match.py against the dd1 arm, masked to the pixels dd1 draws, with a mismatched-frame control. Pose pin separates H-phase: a pinned pose has no phase to differ in.
Rules: join dumps to [vi]/origin (tools/g1c_fbdump_join.py). No cross-run A/B on an animating scene without the pin.
Cheap side check: add --watch-pc-range 0x8009264C:0x800934A4 to the retail arm of tools/g3_mission/run.sh (env-gated) on any mission run, with a known-hit range as its positive control. s6871 could not reach a mission by hand; that recipe does. A hit reopens the resampler defect (docs/DECODED-TAIL-CENSUS.md).
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
