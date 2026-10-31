# NEXT: 21:9 level-select right-edge residual (after the s6694 scissor fix)
HYPOTHESIS-ID: g1d-levelselect-right-residual

s6694 fixed the floor tear (game scissor lrx (w*4)&0xFFF wrapped to 0 at w=1024; clamped to 0xFFF at
0x80017370/0x80017814). Remaining in the 21:9 select frame (scratch/agent/s6694_clr/w21/wide21/fbd/
fb_0001450_w1024.ppm, screenshots/s6694_21x9_levelselect_before_after.png middle row): noise block at
x~690-760 rows 0-60 and a noise column x>~950. vhf 7.2-8.0 vs target <7.

Hypotheses:
- H-wrap2: another game-built 12-bit x field (fill rect, tex rect, viewport scale/translate) encodes
  1024*4 and wraps, so something meant to cover the right edge (backdrop clear / wall rect) is clipped.
- H-fov: the 3D geometry genuinely ends before x=1024 (camera not widened enough for 1024), so those pixels
  are never drawn and only the colour clear would hide them (is the colour image cleared at all here?).
- H-stale: the pixels are drawn, but RT64 write-back/read-in at w=1024 leaves stale rows (old s6625 class).
Discriminator (one run, python3 scratch/agent/s6694_clr/run.py w21 with ROGUESQ_LOG_FILLALL=1): list every
fill/tex rect on the 1024 colour images with lrx<ulx or lrx==0 (H-wrap2); [floor-frame]/RDP tri x-extent max
per frame vs 1023 (H-fov); compare the noise pixels against the previous frame dump (stale = identical, H-stale).
Then fix and send the owner the before/after. After that: G3d turning-shake (ITERATION 3c).
