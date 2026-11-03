# NEXT: is the lvl17 radar-region rect HUD or a world sprite wrongly shifted by the s6159 region box?
HYPOTHESIS-ID: g1d-region-shift-scope

State (s6851): the s6850 residual wrapped texrect is a game-DL G_TEXRECT/FLIP at ul.x ~760, ul.y ~85, 16x30 px, that
rs64_region_scan (s6159 HUD anchor, auto with ROGUESQ_ASPECT; region 669..810 x 20..135 at w1024, shift +256) moves to
ul.x ~1016. Saturation (ROGUESQ_G1D_SHIFT_SAT, default on) now clips it at the edge instead of dropping it. But the
region box is a fixed screen rectangle (s6695 caveat), so a WORLD sprite passing behind the radar disc also moves +256.
First fold scratch/agent/SOAK-RESULTS.md lines for s6851_shiftsat_lvl5 / lvl9 (expect out WRAP=0; lvl5 control may
not fire, as in s6850).

Hypotheses:
- H-radar: the rect is radar HUD (a blip, sweep or disc part) drawn inside renderRadarMinimap's DL span -> shifting it is
  right and the edge clip is right.
- H-world: it is a world billboard/texrect (smoke, explosion, target bracket) from the 3D pass that happens to sit in the
  box -> the shift is wrong; it belongs at ul.x 760 and the box gate must exclude it.
Discriminator (one instrument, one run, lvl17 scratch/s6851/abd.sh with ROGUESQ_G1D_SPRITE_DIAG=2): in rs64_region_scan,
for every shifted texrect log the last G_SETTIMG address + format/size before it, the tile size, and whether the rect
lies between the radar's first and last texrect of that swap (rs64 already stamps renderRadarMinimap: g_rs64_radar_swap;
add an RDP-offset bracket if needed). Also log the shifted TRIs' count per swap as a control (the disc tris are known
radar content and must be classified H-radar). Compare with a world sprite's texture image (G_SETTIMG of a known
explosion billboard, e.g. the s6850 TexrectGen sprites at off=733CD0).
Fix by result: H-world -> restrict the shift to the radar's own DL span (bracket by RDP offset or texture image);
H-radar -> close, owner sheet of before/after (SAT=0 vs 1) at the right edge.
Budget: 1 iteration; if not discriminated, close as "clipped at edge, owner judges".
