# G1d: wide-title background tiling + white corners
HYPOTHESIS-ID: g1d-widescreen
s6246: WB_CLEAR dropped lower-band non-black 0.819->0.545 (stale RAM part); remaining picture = tiled hangar bg with seams at x~65/130/195/705/770 + white corner blocks (x<65,x>770,y>255).
Hypotheses: H-bg-wrap (bg texrect/tri S-range repeats at 512-wide span; widen or clamp edge); H-native-white (RT64 native fb cleared white / not cleared for wide span).
Discriminator: use s6244 skip arms (texrect-all / tri-all in ph4) to see which class paints the tiled strips and the white corners; control = none arm. Then clear RT64 native target colour to black at wide alloc (arm ROGUESQ_WB_NATIVE_BLACK).
