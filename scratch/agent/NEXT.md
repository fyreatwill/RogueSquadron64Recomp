# NEXT: G5i at 21:9 (owner's ultrawide) and an abort from a second mission
HYPOTHESIS-ID: g5i-hangar-reentry
Context: s6995 fixed the hangar re-entry fish-eye (release keyed on the raw view reaching the craft); s6997 held at fullscreen
16:9 dd2/dd4. Not covered: 21:9 (owner plays a 21:9 ultrawide) and aborting from a mission other than the route's default.
Hypotheses:
- H-holds: 21:9 and the other mission's re-entry give every scroll <=~5 deg post-turn off-axis, like 16:9.
- H-wide: 21:9 width changes the hangar camera path (G1D_340PERSP / showroom width) so the raw view never "reaches" the craft
  within the fix's tolerance -> aim never releases or releases late (look for stuck aim / off-axis > 10 deg).
- H-mission: the re-entry cursor/craft list differs after another mission's abort (different start craft) -> longer pan.
Discriminator, one binary, 3 runs back to back: scratch/s6995/arm.zsh with route_long.txt, ROGUESQ_ASPECT=21:9 (+ MISSION_WIDTH
/ WIDE_ROUTE per CURRENT-TRUTH recipes), FPS60, dd2: arm new, arm ROGUESQ_G5G_RELMODE=time (positive control, must show >20 deg
on scroll 8/9), and arm new with the abort taken from a different mission (edit the route copy). Score tools/g5i_pan_metric.py;
owner sheet of the re-entry scrolls at 21:9.
