# NEXT: G1d close-out sweep — owner-judgement contact sheet of every menu at 4:3 / 16:9 / 21:9
HYPOTHESIS-ID: g1d-menu-sweep

s6726 fixed the game-over pillars (latched crop) and the 4:3 debrief edge line (scissor xh 511 trim). Remaining:
1. The 1-frame white sliver at the top-right of the centred game-over backdrop on entry (fin219 / go219c w132, 21:9).
   ROGUESQ_LOG_G1D_RECT=1 ROGUESQ_G1D_RECT_CAP=100000 on the 21:9 route; find the swap where the backdrop first shows
   (epoch 26/27 boundary) and name the draw at x>=640 y<16. Hypotheses: H-transition (one swap before the crop latches,
   draws<64 -> uncropped heap row) vs H-draw (a real game rect in the corner) vs H-stale (RT64 target row 0).
2. One run each at 4:3, 16:9, 21:9 of scratch/s6726/gameover.sh <tag> <aspect|none> "ROGUESQ_LIVES_CAP=1" plus the
   title/options captures from s6720/s6721 recipes -> one contact sheet per aspect in screenshots/ for the owner.
   Every screen: centred, no residue, HUD anchored only in flight.
3. Then G1d is done pending owner judgement; next ladder rung G3 render fidelity (hangar artifacts list in CURRENT-TRUTH).
