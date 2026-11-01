# NEXT: G3 -- mission-start intro-mode swap edge lines: guest RDRAM (retail) or RT64 render-target edge?
HYPOTHESIS-ID: g3-intro-swap-edge-lines

G1d is closed pending owner judgement (s6733 fixed the last residual, the abort fly-out pause-texrect shift).
s6732: during the hangar->mission load the shown frame is ONE swapBufferWithViMode through the intro mode 0x80128C90
of a freshly allocated flight buffer; it carries thin light lines on the intro region's right edge and bottom line,
at 4:3 too (so not G1d).
Hypotheses: H-rdram (the lines are in guest RDRAM, i.e. the game/RDP drew them; retail shows them too),
H-rt64 (RDRAM is clean/black at those pixels; RT64 samples or presents the intro render-target edge = RT64 artifact).
Discriminator, one run at 4:3 (no ASPECT): scratch/s6733/dense.sh i43 none "ROGUESQ_LIVES_CAP=1
ROGUESQ_FB_DUMP_DIR=<abs>/scratch/s6733/i43/fbd ROGUESQ_FB_DUMP_EPOCH=<intro epoch> ROGUESQ_FB_DUMP_EPOCH_N=40 ROGUESQ_FB_DUMP_VI=1"
(intro epoch: the one following the E40 epoch, ~42/43; find it first from [g1d-*] epoch lines in
scratch/agent/m6/g1_lvl1s6732_d43/run.log at the [fbw] pfm a2=512 point). Positive control: the window captures of the
same run must show the line (s6732 d43 w255..w256 did). Then scan the RDRAM ppm for the line pixels (x=content right
edge, y=340 row): present -> H-rdram (retail; close as not-ours unless the owner objects); absent -> H-rt64 (find
the RT64 path that presents the intro-mode swap; fix or clear the target edge).
