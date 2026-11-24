# NEXT (s7909; carried over from s7908, which only closed the gate contract)
HYPOTHESIS-ID: g3-preflight-frame-count
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, docs/OWNER-REVIEW-QUEUE.md answers,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7907): island B CLOSED (harness frame/VI-alignment class, flight exact both classes). In the m11 SNAP=3 pair the port
renders 1047/1048 frames between the press-7 segment start (port ~1916, retail 1845) and the crawl start (port ~2963, retail
2864); retail renders 1019. The same VI window, so the port makes ~28 more frames (fewer 3-VI frames?).
Work unit (offline first, kept bins: scratch/s7905/s7905_island_b_rep3/p1.bin.zst, scratch/s7895/m11k/r1/retail.bin.zst):
  per-frame VI spacing in that window on both sides (port: VI_STAMP / [dt7835] fr in p1/run.log; retail: oracle.log VI per
  fullsync), histogram of 2-VI vs 3-VI frames, and where in the window the extra frames cluster (which sub-scene).
Hypotheses:
  H-cost: retail drops to 3 VI/frame where the RSP/RDP load is heavy (hardware cost), the port does not -> retail-faithful
    only by modelling cost; not a defect, close.
  H-scene: the port renders frames retail does not (e.g. a fade or load held longer, extra blank frames) -> port defect, name it.
  H-dt: the game's dt per frame differs in the window (would contradict s7906 dt-equal crawl; check pre-crawl only).
Discriminator: extra frames spread evenly with retail showing 3-VI frames at the same scene content -> H-cost; extra frames
  contiguous at one scene transition / blank or duplicate content -> H-scene.
Budget: one iteration; if H-cost, close and take the next CURRENT-TRUTH item (island A H-index, or owner-queue work).
