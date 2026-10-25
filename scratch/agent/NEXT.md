# NEXT: G1d step 47 - correct HUD centre/filter at 0x800159B4 and anchor to screen edges
HYPOTHESIS-ID: g1d-widescreen
s6155: emitter verified; CPOS lever shifts ally counter + radar ring; but centre=160*scale wrong (all shifted left) and world sprites also pass through it.
Work unit: edit tools/apply_s6155_hudcpos.py: only bias when vp (r17)==0x800cf090 (HUD list; log shows world sprites use 0x80165ec8); centre = (virtual width 320 * scale)/2 plus the VPW/aspect offset - log x of the radar ring and counter in a 4:3 control to learn their native x, then bias left items by +delta and right items by -delta where delta=(wide-4:3 width)/2*scale. Run ctl vs cpos with scratch/agent/s6155_hudcpos.sh pattern at 16:9; judge by a fbdump (not window screenshot) so the scene phase matches.
Outcomes: ring+counter reach the wide-frame edges -> wire into ROGUESQ_ASPECT default; else examine the vp list ordering.
