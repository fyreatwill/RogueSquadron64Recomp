# NEXT: offline level-18 snow-terrain arm
HYPOTHESIS-ID: g1-coverage-cd

Do not launch or recapture. s6653 recovered the existing level-18 capture.
It selects H-new-class: zero of eight dumps pass; the two flight pictures
n=2200/2250 pass sky/craft/HUD but miss terrain rel 0.046/0.068 < 0.08.
Inspect docs/g1_lvl18_flight_s6653.png. The other six frames are crest/pause.

One bounded change: test an additional snow-surface terrain arm in
 tools/g1_flight_class.py, without moving the existing [0.08,0.33] band,
 dark>=0.60, any sky arm/window, or craft/HUD cuts.

Hypotheses:
- H-snow: bright neutral snow with nonzero local relief separates the two
  flight pictures from non-flight art. An extra arm can accept both while
  preserving all controls.
- H-overlap: those surface features also accept title/floor/crest/pause
  art. Reject the candidate; retain visual-only evidence.
- H-window: relief is outside the fixed terrain window. If snow brightness
  and neutrality do not separate surfaces, do not widen windows blindly.

Discriminator: ONE offline table of terrain-window mean luma, low-chroma
fraction, bright-neutral fraction and relative edge energy for both snow
positives, every same-run negative, all CANON entries, and the 13 level-3
mission controls. Choose/test one physically meaningful conjunction from
that table; record exact thresholds and all outcomes. If it cannot
separate surfaces, do not land it. Do not turn a null into another field.

Commands:
    python3 tools/g1_flight_class.py
    python3 tools/g1_flight_class.py scratch/agent/s6653_lvl18/fbd/fb_0002200_w512.ppm scratch/agent/s6653_lvl18/fbd/fb_0002250_w512.ppm

Required pre/post control: canon_bad 0, mission 11/13. Same-run title n=800
must fail sky/terrain; craft-select n=1700 must fail HUD; crest n=2050..2150
and pause n=2300..2400 must stay overall fails. Score all eight, not only
selected positives. Any accepted change is classifier coverage, not a
runtime render fix or retail equivalence. No objective-hit run this unit.
