# NEXT: G3 wide-aspect (21:9) menus/hangar seam + artifact pass
HYPOTHESIS-ID: g3-wide-menus

State: s6797 closed the exact-edge thread at 4:3 (no seam change on any menu/hangar screen, negligible cost). The owner plays
on 21:9; s6601/s6602 found wide-only hangar framebuffer bands, never re-checked after s6735 (horizontal line), s6736
(cw-1 column) and s6794 (exact-edge fan).

Hypotheses:
- H-clean: 21:9 seam inventory per screen = the 4:3 inventory (content features only), arms equal -> close G1d render side.
- H-wide-seam: 21:9 adds lines at the widened-region boundaries (old 4:3 edge x, cw-1 at the wide width) or bands on the
  hangar (s6602), absent at 4:3.
- H-fan-wide: on/off arms differ at 21:9 (fan interacts with the wide x scale).
Discriminator, ONE run: `zsh scratch/s6797/menus.sh tog21 21:9 "ROGUESQ_LIVES_CAP=1 ROGUESQ_EXACT_EDGES=tog ROGUESQ_G1B=1"`
(copy to scratch/s6798/ and change paths; check the run.log echoes the aspect), then
`python3 tools/g3_seam_intra.py <dir>` (pos ctl must be ~100%) and compare its per-screen line set with the 4:3 run
(scratch/s6797/tog: off 25/112, on 24/108 frames with lines; features listed in PORTING-STATE s6797). Lines are content if
they appear at the same relative positions in 4:3; wide-only lines -> view the frame, name the screen and the draw (RDP
dump RS64_RDP_BIN_PORT on that screen) before any fix.
Outcomes: same inventory + equal arms -> H-clean; new wide-only lines -> H-wide-seam (root-cause); arm difference -> H-fan-wide.
