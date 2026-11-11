# NEXT: G3 in-flight render fidelity at RETAIL settings: RT64 presented frames vs angrylion on the same RDP stream
HYPOTHESIS-ID: g3-flight-fidelity
Why: every owner-facing G5 item now waits on the owner's look (CURRENT-TRUTH items 1-12, 26). Ladder 3c G3 "in-flight frame diffs against
retail framebuffers" has only been done for the dd4 drop question (s7098, H-stream). A whole-frame fidelity diff at retail settings has not.
Recipe: L1 and L6, dd1, 4:3, FPS60 off, no opt-ins except defaults (CULL_SPIKE is default on: also run one arm with ROGUESQ_CULL_SPIKE=0 so
the diff is vs the true retail stream). Capture with the s7098 pair: ROGUESQ_G5B_FRAME (forwarded RDP stream + RAM every N swaps) and the
presented window (scratch/s6894/g5b_capture, arm script pattern scratch/s7115/arm.zsh). Replay the dumped frames with
tools/angrylion_replay (stock 8 MB core is fine at dd1; build16.sh only for dd>1). Grep PORTING-STATE s7098 for the exact env/commands.
Hypotheses (per matched frame, angrylion vs RT64 downscaled to 320x240):
  H-equal   : residual is filtering/AA/resolution noise only (mean |diff| small, no connected region > ~0.5% of frame above 40 levels).
  H-combiner: systematic colour/alpha difference on specific materials (water, sky, cockpit/HUD, explosions): same region every frame.
  H-geom    : geometry in angrylion missing or extra in RT64 (connected regions with edge structure; check s7098 was dd4-only).
  H-fog     : depth/fog band difference along the horizon (row-profile of the diff).
Discriminator: per-frame connected-region table (area, bbox, mean diff, dominant colour both sides), pooled across >=20 frames per level.
Positive control: paint a 20x20 block into one angrylion frame -> the scorer must report exactly one region of 400 px at that bbox.
Output: owner sheet docs/owner_sheet_s7122_fidelity.png (angrylion | RT64 | diff) for the worst 4 frames, and a classified table.
