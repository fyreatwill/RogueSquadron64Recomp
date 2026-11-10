# NEXT: L12 dd6 bundle horizon cut — retail reference + K sweep (image + same-run cost)
HYPOTHESIS-ID: dd6-bundle-l12-horizon
Context: s7044 frozen poses, 16:9 L12 (88x88): the auto bundle (off-map cull R=2 K=0.6 H=off) removes a curved fogged far ground band
(0.8-0.9 mean |dLum|, 1.8% px, A/A 0.00, sheet docs/owner_sheet_s7044_dd6_l12_horizon.jpg). Eye near the z map edge (win z=-65) looking
outward, so the band is OFF-MAP clamped terrain. L13 clean. On L12 the cull is load-bearing (s7042: 42.8 -> 59.7 fps), so turning it off costs ~17 fps.
Unit (one game at a time, background): copy scratch/s7044/run.zsh to scratch/s7045/run.zsh, LEVEL=12 NOREF, FZ "80 90 100 110 125 140 155 170"
(s7044 k0-k3 at 36-66 s were pre-flight black), arms: dd6off (OFFMAPCULL=-1), dd6b (auto K=0.6), k08 (auto + ROGUESQ_DD_OFFMAPCULL_K=0.8),
k10 (K=1.0), dd1 (ROGUESQ_DRAW_DISTANCE=1, no D flags: retail reference). Score tools/s7032_pose_cull_score.py --base dd6off; also score
dd6off and dd6b vs dd1 (--base dd1). Then a same-run cost hold on L12 (scratch/s7040/run_hold.zsh pattern, tog3 R=-1,2,2 K=0,0.8,1.0,
tools/g5e_cost_by_parity.py --phases 3 --skip-s 130).
Hypotheses / outcomes:
- H-ret: dd1 shows sky/fog where dd6off has the band (band is an extension artifact; dd6b is nearer retail) -> no fix needed; say so to the owner, drop the OWNER-OPT-INS caveat.
- H-K: some K (0.8/1.0) gives <=0.3 at all poses AND keeps L12 >=59 fps in the hold -> make the bundle K dims-aware or raise it globally (re-check L1/L4 cost).
- H-trade: no K is both invisible and under the VI cliff -> gate the cull by eye-to-edge distance (eye within N cells of the map edge looking out -> keep), measure.
