# NEXT: G1d defects from s6426 sheet
HYPOTHESIS-ID: g1d-widescreen
Hypotheses for garbled menu frames at ASPECT=16:9/21:9: H-stride (menu FB width differs from the widened width used by VI/scaler), H-hudclip (menu draws use 4:3 scissor but wide origin), H-capture-only (fbdump reads RDRAM at wrong width; on-screen image fine). Discriminator: dump the same menu frame via fbdump and a screen capture of the window; if screen is fine -> capture-only. Also: find the HUD radar x anchor/scissor at 16:9 (radar clipped at right border; 21:9 OK) and fix. Then hangar 21:9, G1e.
