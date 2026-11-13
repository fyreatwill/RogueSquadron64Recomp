# NEXT (s7240): score the WIDEWIN_R bracket (soak s7237_widewin_r2: R=48/64/72); if no R meets the bar, build the 2x2 merge (docs/WIDEWIN-MERGE-PLAN.md)
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7239): r40 window -3.19 ms / -8.6% kpx, r56 -1.94 ms loss-free (s7237). Per-cell coarsening is impossible (s7238). Merge mesh designed
from a static read (s7239, docs/WIDEWIN-MERGE-PLAN.md: hooks H1-H4 in renderFlatMeshFaceGroup + buildGridCellMeshForFace, knob ROGUESQ_DD_WIDEWIN_MERGE=<frac>).
Step 1: tail SOAK-RESULTS.md for s7237_widewin_r2. rc=0: read the scorer block at the end of its soak_results log (data in scratch/s7237q/).
rc=2 or still queued: if `ioreg -c IOHIDSystem | awk '/HIDIdleTime/{print $NF/1e9; exit}'` >= 180, run
`zsh scratch/agent/soak_queue/s7237_widewin_r2.sh > scratch/s7237q/soak.log 2>&1` in the background, then move it to done/. A partial run still
scores any arm past t=97 (`python3 tools/s7233_widewin_r.py scratch/s7237q/log_r*.txt`).
Decide:
- H-radius: some R gives `s7238 BAR MET`. Owner sheet at that R, opt-in in OWNER-OPT-INS. Merge plan shelved.
- No R meets the bar, OR the owner stays active (the bracket can't run): BUILD the merge per the plan. That is an engineering change and doesn't need a run:
  tools/apply_s7239_widewin_merge.py (wire into fixup_game_funcs_vendored.py after apply_s7233_widewin_r) + host rs64_s7239_* in
  src/main/upstream_compat.cpp, regen order make_elf -> N64Recomp -> fixup -> cmake. Then queue soak s7240_widewin_merge.sh (SOAK_NEEDS_IDLE=180,
  arms MERGE=0.5 / 0.7 with _TOG=1, same base B as s7237_widewin_r2). Extend tools/s7233_widewin_r.py to read [s7239].
- Positive control: CONTROL PASS per arm (WIDEWIN_R); for the merge, ph1 drops ~= 3x anchors, ph0 anchors 0.
