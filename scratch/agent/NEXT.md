# NEXT: one offline sky arm for the level-17 chase
HYPOTHESIS-ID: g1-coverage-cd

s6651 captured the Death Star trench. The sheet is a flight and
the frozen rule scores 0/10. Do not recapture. Do not launch the
game. Do not start level 18. Do not move 0.08, 0.33, or the
dark >= 0.60 cut. Do not change the sky sample window
(y 0.02-0.18, x 0.15-0.85). A window change would rescore every
earlier level.

The chase frame is
`scratch/agent/s6651_lvl17/fbd/fb_0002300_w512.ppm`. It passes
terrain (rel 0.224), craft (metal 0.180) and HUD (radar 0.078)
and misses sky only. Sky box: luma 42.5, R-G 1.4, R-B 0.7,
G-B -0.7, dark 0.304. The top 4% of that frame is the same grey
trench surface (luma 34.1, dark 0.336), not a starfield. Lowering
0.60 to catch n=2250 (dark 0.590) does not accept n=2300.

n=2250 is a flight that misses sky and craft. It is not required.
The six pause dumps (radar 0) and the two crest dumps are not
required. Same-run title `fb_0000800_w512.ppm` fails sky
(luma 73.4, R-G 23.6, R-B 29.1, G-B 5.5, dark 0.301).
Craft-select `fb_0001550_w512.ppm` fails overall.

H-grey-arm: one new sky arm accepts n=2300 and keeps both title
skies false.
H-no-separation: every cut that accepts n=2300's sky box also
makes a title sky true, or makes canon_bad nonzero, or makes a
pause dump pass all four clauses.

Before editing, `python3 tools/g1_flight_class.py` must print
`canon_bad 0` and `mission 11/13`. Edit `tools/g1_flight_class.py`
with one arm. Then run that same command again, and:

    python3 tools/g1_flight_class.py \
      scratch/agent/s6651_lvl17/fbd/fb_0002300_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002250_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002050_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002100_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002150_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002200_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002350_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002400_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002450_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0002500_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0000800_w512.ppm \
      scratch/agent/s6651_lvl17/fbd/fb_0001550_w512.ppm

DISCRIMINATOR: n=2300 passes all four clauses, canon_bad stays 0,
mission stays 11/13, both title skies stay false, craft-select
stays an overall fail, and every pause dump stays an overall
fail. That selects H-grey-arm. Record the new pass count and
stop. If the arm fails any of those, revert it. That selects
H-no-separation. Do not ship a dirty classifier. Do not start
level 18 in the same session.
