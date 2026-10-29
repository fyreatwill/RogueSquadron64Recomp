# NEXT: offline sunset cut for the level-4 flight
HYPOTHESIS-ID: g1-coverage-cd

s6635 selected H-new-class. The level-4 sheet is a flight and the frozen
rule rejects 7/7. Do not recapture. Do not launch the game. Do not edit
the heap or any default. No aim or steer work. No queued soak.

The binding miss is sky. On y 0.02-0.18 the phase-7 frames are about
R 215, G 155, B 120, luma 160, dark 0.01, R-G 48..67. The clause is
dark>=0.60 or (luma>=70 and R<=G+15). Oracle uses the second arm
(R-G about -64). Level 3 uses the first (dark 0.93). A third arm has
to accept this orange sky. The same-run title sky is milder and must
not become the thing that flips the canon: R 102, G 73, B 67, luma 80.5,
R-G 29, dark 0.299, and it already fails terrain (rel 0.431).

Craft is the second miss on 5/7. Pink in the center box is 0.13..0.53
because that box is the sunset, above the 0.05 engine cap. n=2350 and
n=2400 already pass craft on the metal hull (0.359 and 0.316). n=2300
also misses terrain at rel 0.065; the other six pass terrain. Do not
lower 0.08 unless the floor (rel 0.709) and the title (rel 0.410) still
fail. Prefer leaving n=2300 as a recorded near-miss.

Precontrol, before any edit. It must print canon_bad 0:

    python3 tools/g1_flight_class.py

Edit only tools/g1_flight_class.py. Then both of these must hold:

    python3 tools/g1_flight_class.py
    python3 tools/g1_flight_class.py scratch/agent/s6635_lvl4/fbd/fb_0002{300,350,400,450,500,550,600}_w512.ppm scratch/agent/s6635_lvl4/fbd/fb_0000800_w512.ppm scratch/agent/s6635_lvl4/fbd/fb_0001700_w512.ppm

H-sunset-cut: canon_bad stays 0, and every phase-7 frame except possibly
n=2300 passes. The title and the hangar craft-select still fail overall.
That closes level 4 (c) under the new rule. The next capture is level 5
with that rule frozen.
H-canon-moves: the only predicates that accept the sunset also make the
five-file table print canon_bad above 0, or make fb_0000800 or
fb_0001700 pass. Revert the edit. Level 4 (c) stays a picture only.
H-dumps-missing: the s6635 ppm files are gone. Stop. Do not recapture
in the same session; say so in the ledger.

DISCRIMINATOR: canon_bad plus the seven phase-7 lines and the two
same-run negatives. Do not add a fourth scene to the canon table in
this session. Read the existing sheet docs/g1_lvl4_flight_s6635.png
before deciding a frame is not a flight.
