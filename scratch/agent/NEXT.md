# NEXT: does the dd6 bundle hold at 16:9 (the owner's 65" TV), where WIDEWIN matters less? frozen poses + same-run cost
HYPOTHESIS-ID: dd6-bundle-169-check
Context: s7034-s7039 qualified the dd>=6+WIDEWIN auto bundle (off-map fog-depth cull R=2 K=0.6 H=off) at 21:9 only (flight poses L1/L4, 300 s holds L1/L4/L5,
cutscene playlist). The owner also plays on a 16:9 TV; the bundle arms whenever WIDEWIN is set, regardless of aspect. Unmeasured at 16:9: image (does the narrower
frustum see different off-map cells?) and cost (is dd6 at 16:9 already 60 fps without the cull?).
Unit, one game at a time:
 1. Frozen poses: copy scratch/s7038/run.zsh to scratch/s7040/run.zsh with ROGUESQ_ASPECT=16:9; arms dd6off (OFFMAPCULL=-1), dd6b (auto), dd6b2 (A/A), dd4 (cap 8192);
    L1 then L4 (L4 is NOREF: score against a same-path base, check [posefreeze] pos).
 2. Cost: s7036-style same-run hold (scratch/s7036/run_hold.zsh, tog3 R=-1,2,2 K=0,0.6,0.6) at 16:9 on L1, g5e_cost_by_parity --phases 3 --skip-s 130.
Outcomes: H-clean (dd6b vs dd6off <= A/A + 0.3 at every pose, cull fires) -> OWNER-OPT-INS 16:9 line with fps; H-cut (a pose loses ground) -> gate the bundle by
aspect; H-moot (16:9 dd6off already ~60 fps, cull saves nothing) -> note it, the bundle stays harmless.
