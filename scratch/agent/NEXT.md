# NEXT: 21:9 abort -> hangar transition lacks retail's right-to-left black wipe
HYPOTHESIS-ID: g3-wide-abort-wipe

Context: s6841 fixed the striped depth frame (initVideoSubsystem half clear). Same runs show that after ABORT LEVEL -> YES
retail and port 4:3 draw: emblem spins away -> flight -> a soft black wipe sweeping in from the right -> black -> hangar
(scratch/s6841/retail_trans.png, p43_trans.png). At 21:9 the emblem spin is right, but the flight picture brightens and
cuts to black with no wipe (scratch/s6841/f1_yes.png, p21/p21x likewise).

Hypotheses:
- H-native-x: the wipe is a texrect/fill or a quad in native 512 screen coords; at 1024 wide it lands off-screen or is
  clipped by a native scissor (s6694 scissor patch scope).
- H-tex: the wipe is a screen-space texture effect (copy of the framebuffer / colour-image-as-texture at 512 wide); at
  1024 RT64 samples the wrong span, which brightens instead of darkening.
- H-blend: the wipe uses a fog/prim colour ramp that our wide path or EXACT_EDGES changes (check with plain 21:9 = p21).

Discriminator, OFFLINE first (capture once, analyze many): the RDP streams already exist:
  scratch/s6841/p43/port.bin (4:3), scratch/s6841/p21x/port.bin and p21/port.bin (21:9), VI-stamped.
  The wipe frames are the last ~30 flight frames before the first texrect-only hangar frame (p43 frames 1121-1150 in
  scratch/s6841/p43_frames.txt carry 'fill 5'; p21x 1103-1129 also 'fill 5'). Dump every non-triangle command in
  those frames (fill/texrect coords, scissor, SetPrimColor/EnvColor/Fog, SetTextureImage address/width, other modes)
  for both aspects and diff. A wipe whose x edge moves frame to frame is the thing to find; the fill-5 vs fill-4 count
  change is a lead (the 5th fill appears exactly in the wipe window).
Outcomes: coords in 0..511 at 21:9 -> H-native-x (widen the wipe's x range in the game code that builds it);
texture-image = a framebuffer address -> H-tex; colours differ -> H-blend. Then one fix + same-build A/B like s6841.
Tools: scratch/s6841/frames.py (per-frame summary), tools/g3_magenta_scan.py. Defaults stay retail.
