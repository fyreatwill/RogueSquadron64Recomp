# NEXT: lvl1 ground — framebuffer pixel vs predicted colour for one ord-7 CI group
HYPOTHESIS-ID: g3-lvl1-mesh-ground
s5992 result: TLUT/texels bright (H3' dead). Remaining: H4 renderer-side darkening (rt64 combine/blend/othermode), H1 legit (scene is just that colour).
Work unit: from scratch/agent/s5991/lvl1_rdp.bin pick one large ord-7 CI tri group (tools/rdpbin_tri_colors.py), extract its screen bbox from the tri edge coeffs, read the same pixels from the matching port framebuffer capture (rdram fb dump, fb addr in file name), compare to predicted texel*shade.
Outcomes: pixels ~ predicted => H1, close the thread and move to next G1/G3 item (mission (c)+(d) coverage); pixels much darker => H4, inspect rt64 combiner path for that comb/othermode. Control: pick an unambiguous bright group (e.g. HUD/sky) and confirm the pixel readback matches.
