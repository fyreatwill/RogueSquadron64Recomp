# NEXT: G3 cinematic sky seam (port-only RT64 defect), split raster vs texture
HYPOTHESIS-ID: g3-cinematic-sweep

s6793: the AT THE MOVIES line is a port-only RT64 defect at a shared vertical sky-tri edge (x=318.0 in the shot at port wall
348-352 s, recipe tools/g3_seam/port_arm.zsh SECS=362 CAP0=340; retail clean, RDP streams identical, persists at native 1x
with ROGUESQ_RESMULT=1, now a working knob).

Hypotheses at native 1x:
- H-raster: RT64 decodeTriangles (lib/rt64/src/gbi/rt64_gbi_rdp.cpp ~l.480-530) rebuilds v1/v2 from the H edge and v3=(xl,ym),
  ignoring xm; somewhere along the shared column neither tri covers the pixel centre -> clear colour (black) shows.
- H-texsample: column 318 is covered but samples a wrong texel (S~0 of a wrapped 32x32 RGBA32 tile; TMEM decode of texel
  column 0, or wrap to texel 31).
Discriminator (ONE build, ONE run, both arms in-run): env ROGUESQ_SEAM_PROBE=1 in RT64 decodeTriangles: for op 0E tris in 640-wide
images with an edge within 0.01 of an integer x and height >=100, log RDP edge words and the reconstructed vertices x1,x2,x3
(budget 200/phase); plus ROGUESQ_SEAM_TOG=N that alternates every N frames between normal draw and forcing these tris'
combiner to shade-only/white (texture off). Line present with texture off -> H-raster (fix vertex reconstruction: use xm
for the M edge start / exact shared-edge x); line gone -> H-texsample (inspect wrap/TMEM decode). Positive control: the
detector (tools/g3_seam/seamscan.py) must still fire on the normal-phase frames of the same run.
Then: TRI shots 48/64. DUR shots stay single-source oracle-side.
