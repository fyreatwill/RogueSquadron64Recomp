# NEXT: offline class rule for the level-3 night flight
HYPOTHESIS-ID: g1-coverage-cd

s6633 captured level 3. Do not recapture it, do not launch the game, and
do not edit the heap or any default. The picture is a night flight
(dark sky, dark ground, a craft, radar). The bright-scene numeric rule
scores 0/13. Evidence: scratch/agent/s6633_lvl3/keys.log and
docs/g1_lvl3_flight_s6633.png. Selector B40=3. Mission dumps are the
13 files n=2550..3150 at VI origin 0x690400, 512x444. The other buffer
0x620400 was not sampled.

ONE offline pass. Start from the operational scorer in
scratch/agent/s6633_lvl3.sh (sky y 0.02-0.18, ground y 0.45-0.95,
radar-red >= 0.02, pink engines in [0.003, 0.05] or near-white yellow
r>=230 g>=210 150<=b<230 in [0.002, 0.015] with pink < 0.001, terrain
luma stddev >= 18). Change only the terrain and craft tests. Print one
line per file: pass/fail and the four class booleans.

Must all hold:
- pass: docs/g3_retail_lvl1_flight_oracle.png
- pass: scratch/agent/s6632_lvl2/fbd/fb_0002700_w512.ppm
- pass: scratch/agent/s6633_lvl3/fbd/fb_0002700_w512.ppm
  and report how many of the 13 mission dumps pass
- fail: scratch/agent/s6631_heapcap_at/wide16/fbd/fb_0001400_w796.ppm
- fail: scratch/agent/s6633_lvl3/fbd/fb_0000450_w512.ppm
  (title, origin 0x00790400, same run)

H-local-contrast: a darker ground measure (local edge energy, not global
stddev) and a craft measure other than pink/white-yellow (the level-3
center is mid-gray metal, not an engine bloom) accept the night frame
and still reject both negatives.
H-inseparable: every change that passes fb_0002700_w512.ppm from s6633
also passes the floor or the title dump.

DISCRIMINATOR: the five-file table. H-local-contrast closes level 3 (c)
under the extended rule; write the predicate into CURRENT-TRUTH and
move on to level 4 with that rule. H-inseparable leaves the numeric
proxy unclosed. The next capture is then level 4 as a picture, judged
by looking at the sheet, and this scorer is not tuned again.

No game run, no heap edit, no aim or steer work, no default change,
no queued soak.
