# NEXT (s7628)
HYPOTHESIS-ID: g6-upstream-features

G6c step 3 proof: stand-ins are visible early instead of popping. s7627 showed they draw RDP pixels (flicker/triplet P 1071, N 547
vs ~108 forced-off; real-object control C 180891; docs/G6C-STANDINS-PLAN.md "Step 3d result").
1. One recipe (scratch/agent/soak_queue/s7628_standins_proof.sh, SOAK_NEEDS_IDLE=300, HOLD=150 (60 never reaches the mission),
   built on the s7626_standins_pixels script in soak_queue/done/): arms L1 dd2, L1 dd4, L4 dd2, L4 dd4 (the LEVEL selector of
   tools/g1e_owner_quiet_arms.zsh), each ROGUESQ_STANDINS=frame+ROGUESQ_STANDINS_LOG=1+ROGUESQ_STANDINS_DUMP=10:16:90+FB_DUMP_DIR.
   Same-run on/off pairs = adjacent window-1 frames (labels 0/1).
2. Offline: per arm, the flicker score (tools/s7624_flicker_score.py, with --control) and a contact sheet of 4 on/off adjacent pairs
   cropped around the hot mask (python + PIL; owner-viewable PNG in scratch/s7628_sheet/). Also fold [standins-spawn] early_s
   (seconds a stand-in was visible before the real object spawned) per arm.
3. Confirm by eye that the N-arm (true-depth) excess is stand-in shaped (s7627 hot mask only 36 px at L1 dd4).
Outcomes:
- excess > 0 and early_s > 0 on both levels at both dd -> step 3 proof done; next: 300 s holds on all 19 levels with STANDINS=1 at dd4
  (queue as soaks, 2 levels per recipe to stay under the 600 s cap), then the owner sheet.
- excess only at dd4, not dd2 -> stand-ins at dd2 lie inside the game's own spawn radius (expected little gain); report, still hold.
- excess but sheet shows wrong shapes/positions -> placement bug (place_on_path / build_state in src/main/rs64_standins.cpp).
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; check idle first (owner active ~21:38).
