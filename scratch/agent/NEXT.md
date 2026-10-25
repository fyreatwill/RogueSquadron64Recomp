# NEXT: G1d step 48 - move the radar disc/crescent with the ring; derive HUD anchor A/R from width
HYPOTHESIS-ID: g1d-widescreen
s6156: ROGUESQ_HUD_ANCHOR=142,334 (w796) moves counter, ally icon, ring to the edges; grey radar disc (~575 px of 796) and crescent stay. Disc is not emitted via 0x800159B4 vp set {cdc80,cd670,138d20} (or its elem sits in vp 165ec8/cf090).
Work unit: log disc emitter: run s6156_run.sh ctl-style with ROGUESQ_HUD_LOG for ALL vps incl. 165ec8 and cf090 and also a CPOS mark (+160px all vps incl. 165ec8) to see whether the disc moves (positive control); if it moves under some vp, extend the anchor set; else find the disc's draw (mesh/matrix path, not sprite). Then A=(W-320)*? derive: A=142 at w796 (check w683, w1024 for the formula), R=(W-320)-A, and bundle into ROGUESQ_ASPECT.
Outcomes: disc moves with ring -> HUD fully anchored at 16:9; else disc is a mesh and needs matrix-translate lever.
