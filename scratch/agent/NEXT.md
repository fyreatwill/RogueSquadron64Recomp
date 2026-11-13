# NEXT (s7246): crack-free WIDEWIN merge: flatness gate
HYPOTHESIS-ID: widewin-heavy-window-cost
State (s7245): MERGE=0.4 cracks visibly (two runs, tools/s7245_merge_cracks.py control PASS 112/112): side-third bright seam px/frame
off->on 24.5->55.0 (m40+R56), 24.4->47.4 (m40 alone); zoom docs/owner_sheet_s7245_merge_cracks_zoom.png shows slivers on mid-distance
hillsides + the L4 shoreline. Cause: T-junction at every merged-edge midpoint, gap |h_mid - (h_end1+h_end2)/2| (abs y = ybase<<4 + h<<4,
WIDEWIN-MERGE-PLAN.md lines 18-25), merge boundary at ~0.4 of window radius = in clear view.
Before any rs64_s7239 edit and after it: `zsh tools/s7241_merge_test/run.sh` must print 0 failures; add cases for the new gate.
Work unit (ONE build, ONE run when owner idle >= 180 s, screen unlocked):
1. In rs64_s7239_group (src/main/upstream_compat.cpp ~539), for each candidate 2x2 block read the four partners' corner heights (elem+0x24
   bytes 0,4,20,24, s8) and y bases (hw+0x0A) -> absolute corner y. Deviation = max over the 4 edge midpoints (shared corners between partners)
   of |y_mid - avg(outer ends)| and the centre vs the merged quad's diagonal. Merge only if dev <= E. Env ROGUESQ_DD_WIDEWIN_MERGE_E=<units>
   (default: 0 = exact-planar only; log `flatrej=` in [s7239]). Unit test: planar block merges, one raised midpoint rejects, negative control.
2. Run arms with tools/g1e_owner_quiet_arms.zsh or the scratch/s7245/arm.zsh capture route (same-run MERGE_TOG): E=0, E=16, E=64 (frac 0.4),
   each scored by tools/s7245_merge_cracks.py (seams on-off vs A/A) AND [g1b]/[g1cf] window dsd via tools/s7233_widewin_r.py --merge.
Hypotheses / outcomes: H-flat-works (some E gives seam on-off within A/A noise and window dsd <= -1.5 ms) -> owner sheet + OWNER-OPT-INS line;
H-flat-empty (E small enough to be crack-free merges ~nothing, dsd ~0) -> merge is dead; fall back to R (r48 -4.12 ms, single run; needs its
own seam/hole check with the s7245 scorer) or skirts (emit a vertical skirt strip along merged edges facing unmerged cells);
H-shore (shoreline seams persist at E=0) -> water/land cell type differs inside a block: also require equal material (elem+0x2C) across partners.
Raws are ~35 GB per 240 s capture: delete them after scoring.
