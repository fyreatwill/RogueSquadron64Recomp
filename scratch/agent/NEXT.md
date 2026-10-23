# NEXT: G3 hangar rim band — name the writer
HYPOTHESIS-ID: g3-hangar-rim-band
G4 hangar route closed (s6011, 9/9 clean). Take the rim band from CURRENT-TRUTH line ~71.
Hypotheses: H1 RDP triangles/rect emitted by the game DL cover the band (game-side data); H2 renderer scissor/viewport edge handling (RT64 port); H3 stale framebuffer region not cleared (ucode/VI origin). 
Discriminator: capture one hangar frame with the raw RDP bin dump (tools/rdpbin_top_groups.py, rdpbin_tri_colors.py) and check whether any command touches the band's pixel rows; positive control = a command known to cover a visible object. Band covered by cmds => H1; none => H2/H3 (then compare VI origin/scissor).
