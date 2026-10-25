# NEXT: G1d step 49 - find the radar disc draw (mesh/matrix, not 0x800159B4 sprite)
HYPOTHESIS-ID: g1d-widescreen
s6157: disc unmoved by anchoring any of vps cdc80/cd670/138d20/cf090/165ec8. Hypotheses: H-mesh (disc = textured mesh/quad with a matrix translate built in initHudStruct 0x800C0084 area or a radar-update fn), H-other-emitter (another sprite/DL fn than 0x800159B4), H-baked (disc drawn inside a larger HUD display list with absolute RDP coords).
Work unit: RDP-level discriminator in one run: log RDP tris/rects whose screen bbox lies in the disc region (x 535-615, y 30-125 at w796) with the emitting task/DL address, plus a mark arm that shifts screen x of those tris +150 (positive control: the disc visibly moves). Then trace the DL source back to its builder.
Then derive A/R from width (A=142 @w796; check w683,w1024), bundle into ROGUESQ_ASPECT.
