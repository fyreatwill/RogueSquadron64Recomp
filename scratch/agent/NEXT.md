# NEXT: G1d step 2b - read s6104 soaks, then widen the framebuffer
HYPOTHESIS-ID: g1d-widescreen
Read SOAK-RESULTS lines s6104_g1d_scale / s6104_g1d_scaleexp and their fb dumps vs s6103_g1d_expand_l1. Positive control: dump is horizontally squeezed (aspect x1.333 reached guPerspective). If not squeezed, find who overwrites r7 / the real aspect source. If squeezed: next ONE build widens the game's colour image/scissor/VI width (grep PORTING-STATE for VI_WIDTH/osViSetMode/setScissor) under ROGUESQ_ASPECT, then window screenshot at 16:9 (extra width drawn, not stretched). HUD x anchoring after.
