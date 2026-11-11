# NEXT: G3 owner-recipe fidelity at 21:9 (CURRENT-TRUTH item 29)
HYPOTHESIS-ID: g3-owner-recipe-219
State (s7131): owner recipe (FPS60 dd4 16:9) RT64 == angrylion on L1, L4, L6. 21:9 (the owner's monitor) is unmeasured.
Hypotheses: H-equal (at floor), H-wide (21:9-only diff: HUD anchor walker, extra guard band, W_SHEET corners at the wider viewport), H-tool (capture rect / window size wrong at 21:9).
Discriminator: frac>40 and region locations vs angrylion on L6 at 21:9; diffs confined to HUD -> anchor walker; at the sides -> guard band; whole-frame offset -> rect.
Commands: copy tools/s7131_arm.zsh, pass extra env "ROGUESQ_ASPECT=21:9 ROGUESQ_G5B_FRAME_EVERY=1 ROGUESQ_G5B_FRAME_FROM=7500 ROGUESQ_G5B_FRAME_MAX_MB=12000"
  (later env wins over the script's 16:9). Then: tools/s7123_present_rect.py for the window rect; capture size may need 504x216-class (edit the g5b_capture args).
  Replay in chunks of 60 swaps with scratch/s7124/al16/frame_replay16; score with tools/s7122_fidelity.py --rect <measured>; drop pframe==0 rows.
CURRENT-TRUTH ~58.9 KB: keep edits net-zero. Owner save rule applies.
