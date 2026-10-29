# NEXT: level-10 tan cloud sky, offline
HYPOTHESIS-ID: g1-coverage-cd

s6643 captured level 10. The sheet is a flight (tan clouds, station,
A-wing, radar, reticle) and the frozen rule scores 0/12. Every
phase-7 frame fails the sky clause. Do not run the game. Do not
move 0.08, 0.33, the luma>=70 blue arm, the luma>=80 / R-G>=40
orange arm, or the edge>=0.05 cut. No heap, aim, draw-distance,
aspect, or default change. Do not start level 11.

Sky box on n=2850..3400 (step 50), all 512x444 at origin
0x00620400:

    dark 0.063..0.248
    luma 72.7..104.0
    R-G 23.1..28.5

That misses dark>=0.60, the blue arm (needs R-G<=15) and the
orange arm (needs R-G>=40). Terrain and HUD pass on 12/12. Craft
passes on 11/12. n=2900 also misses craft (edge 0.013): the ship
is beside the station. Not required.

Same-run title `scratch/agent/s6643_lvl10/fbd/fb_0000800_w512.ppm`
fails sky and terrain (luma 78.1, R-G 27.1, rel 0.419). That sky
sits inside the flight's chroma band, so a bare R-G window of
23..28 also marks the title sky as sky. The title still fails
terrain, so the overall verdict can stay fail. Craft-select
`fb_0001700_w512.ppm` fails HUD only (radar 0.002, luma 77.3,
R-G -1.5). It already passes sky by the blue arm.

Before the edit, `python3 tools/g1_flight_class.py` must print
`canon_bad 0` and `mission 11/13`. After the edit, the same
command must still print both. Then score:

    python3 tools/g1_flight_class.py \
      scratch/agent/s6643_lvl10/fbd/fb_0002850_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0002900_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0002950_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003000_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003050_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003100_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003150_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003200_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003250_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003300_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003350_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0003400_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0000800_w512.ppm \
      scratch/agent/s6643_lvl10/fbd/fb_0001700_w512.ppm

H-chroma: one added sky arm accepts at least 11 of the 12
phase-7 frames, canon_bad stays 0, mission stays 11/13, the
title still fails overall, and the craft-select still fails HUD.
Land that arm. The session after that captures level 11 with
the rule frozen. Do not start level 11 here.
H-canon-break: the arm that accepts the clouds also makes
canon_bad nonzero, or makes the title or the craft-select pass
overall. Revert that arm in this session and try one spatial
feature of the cloud box (local variance, or a dark-cloud
fraction) that the title photo does not share. If that also
breaks canon, leave the tool as it was at s6643 and record the
two failed arms. Do not add a third.
H-no-accept: the new arm still scores 0/12 on these dumps.
The measurement was wrong. Record the sky-box numbers the arm
actually saw and do not loosen 0.08 or 0.33 to compensate.

DISCRIMINATOR: `canon_bad`, `mission 11/13`, and the pass/fail
lines on the twelve phase-7 dumps plus the same-run title and
the craft-select. A flight that still scores 0/12 is not a
license to move the terrain cuts.
