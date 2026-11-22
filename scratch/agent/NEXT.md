# NEXT (s7827)
HYPOTHESIS-ID: g3-reticle-half-pixel
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7826 found the only port/retail element difference in lvl1 flight: the green reticle (00FF0064) is +0.5 px lower in Y, on
retail's exact path (tools/s7826_rect_path_offset.py, captures scratch/s7826/{retail,port}.bin.zst, R 3521:3825 / P 4378:4702).
Pure-Y constant, so screen space, not timing. Bounded: at most 2 iterations, then close single-source.
Hypotheses:
 H-anchor: our HUD anchor chain (apply_s6155_hudcpos / s6156 / apply_s6860_hudelem in funcs_4.c, vp 0x80138D20) touches the
   reticle elements at 4:3 (e.g. a y rounding or a +0.5 from a centre computation) even though r19 < bound should exempt them.
 H-vp: the port's flight viewport/projection centre y differs by 0.5 px (our vpw/far patches, apply_s6031_far.py apply4, or
   FP_XSCALE leaking a y term) -> but then world tris would shift too; check s7826 tris' Y edge words via s7825_tri_shift_bias.
 H-cpu: the reticle's own screen-y math (float->int trunc of a .5 value) rounds differently: would show as a 0.25/0.5 flip
   depending on position, not constant -> s7826 says constant, so lowest prior.
Discriminator (offline first, then ONE run if needed): (1) read the anchor chain code in N64Recomp/RecompiledFuncs/funcs_4.c around
`rs64_s6860_hud_elem_top` + main.cpp:2525 and list every path that edits a texrect/element y at ASPECT unset; (2) run
s7825_tri_shift_bias.py on the mission window for Y-only shifts of world tris (H-vp predicts one-signed Y); (3) if (1) names a
candidate env switch (e.g. ROGUESQ_G1D_HUD_ELEMTOP=1 or the anchor off), one det pair with the port arm XE carrying it, same
command as s7826 (scratch/agent NEXT s7826 in PORTING-STATE), scored with tools/s7826_rect_path_offset.py: offset -> 0 selects H-anchor.
