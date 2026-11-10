# NEXT: are there other levels below 60 fps at 21:9 with the dd6 bundle (KLEVEL candidates)?
HYPOTHESIS-ID: dd6-219-levelK-survey
Context: s7057 auto KLEVEL = 12:0.5,13:0.5 (both: K0.5 +0.5..+0.9 fps same run, poses clean). Measured at 21:9 so far: L1, L4 (K0.5 visible,
stays 0.6), L5, L12, L13 (L15 has the 21:9 crash, owner-gated). At 16:9, L2 and L3 gained ~1 fps from the cull (s7041): the next likely 21:9 laggards.
Hypotheses:
 H-more: L2 and/or L3 at 21:9 sit < 59.5 fps at K0.6 and K0.5 gains >= +0.5 fps same run -> pose-qualify (K0.3 control) and add to KLEVEL.
 H-done: both ~60 at K0.6 -> KLEVEL stays 12,13; survey the rest only if the owner reports a slow level.
Unit: edit KLEVEL in scratch/s7057/run_hold.zsh tog line to 2:0.5,3:0.5 (copy to scratch/s7058), then
  zsh scratch/s7058/run_hold.zsh L2t 2 tog ; zsh scratch/s7058/run_hold.zsh L3t 3 tog   (~9 min each, run sequentially, timeout >= 1200 s)
  score: python3 tools/g5e_cost_by_parity.py --phases 3 --skip-s 130 --split xor8 scratch/s7058/tl_L2t.bin* scratch/agent/m6/g1_lvl2s7031L2t/run.log
Poses (only on H-more): scratch/s7057/run.zsh <LV> (arms k06/k05/k03; ~14 min, timeout >= 1500 s); score with tools/s7032_pose_cull_score.py --base k06
  plus the dLum>8 pixel count (PIL ImageChops, no numpy in this python).
Owner-gated items (G5a-G5i, L15 21:9, G1d) still need nothing run.
