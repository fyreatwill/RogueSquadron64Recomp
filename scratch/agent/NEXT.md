# NEXT: level-8 dusk class rule, offline
HYPOTHESIS-ID: g1-coverage-cd

s6640 captured level 8. The sheet `docs/g1_lvl8_flight_s6640.png`
is a flight (desert, orange dusk, X-wing, radar, reticle) and the
frozen rule scores 0/7. This session edits `tools/g1_flight_class.py`
only. No game run. No heap, aim, draw-distance, aspect, or default
change. Do not move 0.08, 0.33, or the luma>=70 blue arm. Do not
add a file to the five-file canon table.

Dumps, already on disk:

    scratch/agent/s6640_lvl8/fbd/fb_0002600_w512.ppm
    through fb_0002900_w512.ppm

Same-run negatives:

    scratch/agent/s6640_lvl8/fbd/fb_0000800_w512.ppm
    scratch/agent/s6640_lvl8/fbd/fb_0001700_w512.ppm

Before editing, `python3 tools/g1_flight_class.py` must print
canon_bad 0.

Sky is measured. Lower the sunset luma floor from 140 to 80 and
keep R>=G+40 and R>=B+20. That accepts all seven level-8 skies
(luma 84.4..97.0, R-G 86.8..94.3, R-B 133.7..154.7, dark<=0.014).
It rejects the canon floor, both title dumps, the craft-select
frame, the oracle, level 2 and level 3. luma>=90 misses n=2600
(luma 84.4). Do not drop the chroma gates: the same-run title is
luma 85.2 with R-G only 32.1.

Craft is the open clause. Do not raise the pink cap. Pink
0.184..0.328 is the orange sky in the center box. Chase-band
median is 68.3..81.7, so the median>=120 dark-hull arm does not
fire. A median>=80 dark-hull test hits only n=2600 (0.140); the
other six hulls sit below y 0.62. Saturated green (9..33 pixels,
g>=80, r<=50, b<=50) is the top-left HUD icon at y 0.10-0.30, not
a center reticle. The title and the craft-select frame have zero
of those pixels. That icon is not a craft signal. Terrain already
passes (rel 0.095..0.310). Do not retune the HUD cut: radar
0.665..0.993 matches the orange sky, and the ring is visibly there.

H-craft-found: one new craft clause, plus the luma>=80 orange
arm, makes at least one phase-7 frame pass all four clauses.
`python3 tools/g1_flight_class.py` prints canon_bad 0 and
mission 11/13. The same-run title and craft-select dumps still
fail overall. Land that edit.
H-no-craft: every craft clause that accepts a chase frame also
makes canon_bad nonzero, flips a level-3 mission line, or makes
the title or the craft-select frame pass overall. Do not land
the sky arm alone. Record the clause and the file it broke.

DISCRIMINATOR: the tool's pass/fail lines on the seven phase-7
dumps and the two same-run negatives, plus canon_bad and
mission 11/13 from a no-arg run. A sky-only edit that still
scores 0/7 is not a result to land.

If H-craft-found, the session after that captures level 9 with
the new rule frozen. Do not start level 9 in this session.
