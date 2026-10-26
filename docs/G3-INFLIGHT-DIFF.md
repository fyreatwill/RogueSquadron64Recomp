# G3 in-flight port vs retail comparison (s6266, eyeball level, single-source)

Frames: retail docs/g3_retail_lvl1_flight_oracle.png and docs/g3_retail_lvl1_paused_oracle.png
(angrylion, 512x412); port scratch/agent/m6/g1_lvl0orc/fbd/fb_000{3000,3500,5000}_w512.ppm (512x358).

| Item | Retail | Port | Verdict |
|---|---|---|---|
| Sky, terrain, HUD, radar, reticle, craft present | yes | yes | match |
| Pause emblem, PAUSED / CONTINUE / ABORT layout | yes | yes (port frame cropped to 358 rows, lower menu rows cut) | match; crop is the capture extent |
| Mission-goal bullet text | 2 lines | absent | NOT a defect: s5433 shows the port goals screen is the mission-failed overlay after fade, retail frame is a real pause on a different level/state |
| Craft livery | dark grey/black X-wing | light grey with orange/red panels | UNEXPLAINED: could be different craft/level (retail frame is Tatooine mission 1; port lvl0 forced) or a shade/lighting delta. Not provable from non-matching frames |
| Ground haze | visible distance haze | port frames mostly sky | not comparable (camera) |

Conclusion: no port-only missing-geometry/HUD defect found; the one open question is craft
shading. Discriminator for a future unit: capture retail and port of the SAME mission at the
SAME tick after mission start (retail: s5978 recipe flight origin 0x690400 at ~77 s with a fb-dump
delay measured from the first 512-wide VI poll; port: ROGUESQ_FB_DUMP_EVERY=10, level forced to
the retail first mission) and compare craft mean luminance over the craft bounding box. Positive
control: the same measurement on the HUD radar ring, which should match within noise.

## s6267 resolution
Craft shade matches: bbox dark-pixel (<150 luma) median retail 74.9 vs port 76.0/75.8 (mean 81.2 vs 79.0/78.9); radar-ring control 889px (177,16,11) vs 842px (181,16,13). Earlier light livery was the lvl0 frame. G3 closed (not tick-matched; two evidence lines: numeric + visual).
