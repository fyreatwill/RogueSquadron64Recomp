# NEXT: does the default WIDEWIN cap 10240 itself shave the L4 21:9 far shoreline? (POOLX_MAX=6 / cap 12288 arm, frozen poses)
HYPOTHESIS-ID: dd6-219-l4-cap-saturation
Context: s7052 closed the 21:9 L12 cost thread (~59 fps accepted): cap 9216 lowers the L4 21:9 far-left shoreline (0.26-0.39,
rows ~716-800), cap 8192 more (0.74-1.15). The band is cap-sensitive on L4 at 21:9, so 10240 (the POOLX clamp 5) may also be cutting it.
s7037 found 12288 (ROGUESQ_DD_POOLX_MAX=6) bought nothing on the L1 dd8 edge score, but L1 does not bind on the cap (s7052: 8192 = 0.02 on L1).
Hypotheses:
 H-saturated: c12288 vs c10240 <= 0.1 at every L4 pose while c9216 (control, 0.26-0.39 in s7052) fires -> 10240 is enough, note it, pick next rung.
 H-more: c12288 vs c10240 > 0.3 in the same band, ADDING ground -> measure cost (same-run tog3 hold L4 21:9 cap 10240/12288) and offer
   POOLX_MAX=6 as an owner opt-in for 21:9 (default unchanged without the owner).
 H-unsafe: c12288 crashes / heap or spill failure -> record, no opt-in.
Unit (no build):
1. cp scratch/s7052/run.zsh scratch/s7053/run.zsh; sed s7052->s7053; arms c10240 (CAP=10240) / c12288 (+ROGUESQ_DD_POOLX_MAX=6
   +ROGUESQ_DD_WIDEWIN_CAP=12288) / c9216 ctl; `zsh scratch/s7053/run.zsh 4` (~15 min). Check [ddbundle] px=6 in the c12288 log.
2. python3 tools/s7032_pose_cull_score.py scratch/s7053/L4 --base c10240; band bbox with the PIL snippet from s7052 (threshold 24).
3. Sheet docs/owner_sheet_s7053_*.jpg rows 10240 | 12288 | 9216 | diff, same crop as s7052 (H 0.40-0.75).
Owner-gated items (G5a-G5i, L15 21:9, G1d) still need nothing run; check them first.
