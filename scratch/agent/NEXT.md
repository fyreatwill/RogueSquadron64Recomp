# NEXT (s7310): why the clipped left-edge sky-dome tris get texture W <= 0 at 21:9 dd>1 (H-geom vs H-rsp-emu)
HYPOTHESIS-ID: g5f-219-left-sliver
State (s7309): the sliver = tris 1/3/4 of swap 4064 (L1 PIN=1 freeze FZ=106.28), sky-dome panels clipped at fb x=0, start W 0/-0.0015/-0
(all other 6604 textured tris W >= 12). In the RDP stream (angrylion replay agrees). Not CULL_SPIKE/W_SHEET/MELT/WIDEWIN/RT64.
Tools: tools/s7309_tri_texcoef.py <cap> <swap> all|i,j ; frozen swap = last swap before the ~15 s gap in G5B_TRIS (snippet in s7309 entry).
Hypotheses:
 H-geom: dd auto-far (or the 21:9 frustum x-widening) moves the sky dome / far scale so the F5 clip legitimately makes a vertex at w<=0;
   retail ucode on hardware would do the same. Predicts: left-edge sky tri W shrinks monotonically dd1 -> dd4 -> dd8 and crosses 0.
 H-rsp-emu: our LLE RSP clip math (VRCP/VRCPH, VMULF clamp) emits w<=0 where hardware would not. Predicts: W jumps (not a trend) and the
   clip input vertex has a sane positive w; check the vertex buffer / ucode clip path with docs/F5-UCODE-REFERENCE.md.
 H-wide: only the 21:9 widened frustum exposes the dome edge (16:9 dd8 has none at this pose): 16:9 dd8 left sky tris keep W >> 0.
Unit, ONE pass, env only (B from scratch/s7309/run3.zsh, minus the ASPECT for the 16:9 arm):
 env PIN=1 TAGP=s7310 FZ=106.28 zsh tools/g3_optin_pose_arms.sh scratch/s7310/a \
   d1=<B21:9>+DRAW_DISTANCE=1+G5B_FRAME=..d1.cap+G5B_TRIS=..d1.bin  d4=..dd4  d8=..dd8  w8=<B16:9>+dd8   (FRAME_FROM 3900 EVERY 5 MAX_MB 1500 each)
 For each: frozen swap; list textured tris with any vertex at x<=1, their W, dWdx, and W of the tri covering (2,290). Table W vs dd and aspect.
Then fix at the origin (H-geom: clamp/skip sky-dome clip output with w<=0 in the opt-in dd path, or keep the dome inside the far scale;
H-rsp-emu: fix the vector op). Owner sheet before/after. dd1 stays retail.
Needs an unlocked screen and idle host (the arms script gates on both). Delete the .cap files after decoding (1.5 GB each).
