# NEXT: level-6 flight capture under the frozen class rule
HYPOTHESIS-ID: g1-coverage-cd

s6637 closed level 5 (c) under the frozen rule. Seven of nine phase-7
dumps pass. n=2800 (rel 0.338) and n=2850 (rel 0.331) miss only the
0.33 terrain ceiling and are not required. Do not edit
tools/g1_flight_class.py in this session. Do not move 0.08 or 0.33.
No heap edit, no aim, no draw-distance, no aspect, no default change.
No objective (d).

Precontrol, before any launch. It must print canon_bad 0:

    python3 tools/g1_flight_class.py

If the screen is locked, stop and write BLOCKED with NEEDS-HUMAN:
physical. Check both of these; either Yes/true means locked:

    ioreg -n Root -d1 | grep IOConsoleLocked
    ioreg -n Root -d1 -a | grep -A1 CGSSessionScreenIsLocked

Adapt scratch/agent/s6637_lvl5.sh into scratch/agent/s6638_lvl6.sh.
Change the output directory, and set ROGUESQ_FORCE_UNLOCK=6 and
ROGUESQ_FORCE_SAVE_MISSION=6. Keep the precontrol as
`python3 tools/g1_flight_class.py`; a non-zero exit must abort
before the game starts. Do not paste an inline classifier. Keep
the retail 4:3 route: menu start/z schedule, no stick, SIGKILL
30 s after the first post-hangar origin 0x690400, dumps every
50 VIs. Run from build/ with the ROM beside the binary. Kill
with SIGKILL only.

One game run. Then:

    python3 tools/g1_flight_class.py <phase-7 ppm paths> <one title ppm> <one hangar ppm>

Read the contact sheet before calling a frame a flight. Build it
from four post-hangar dumps the way docs/g1_lvl5_flight_s6637.png
was built, and write it to docs/g1_lvl6_flight_s6638.png.

H-rule-holds: the post-hangar frames that show sky, terrain, craft
and HUD pass, and the same-run title and hangar dumps fail overall.
Level 6 (c) closes. The next capture is level 7 with the rule
still frozen.
H-new-class: the sheet is a flight and the frozen rule rejects it.
Record which clause misses and the measured numbers. Do not edit
tools/g1_flight_class.py in this session.
H-no-picture: the post-hangar dumps are a menu, a hangar, or a
black frame. Say which origin they carry. Do not retune the rule.
H-screen-locked or H-route-miss: no phase-7 flight dumps. Do not
invent a score. One retry is allowed only if the first run died
before the hangar and the screen was unlocked.

DISCRIMINATOR: the frozen tool's pass/fail lines on the phase-7
dumps plus the two same-run negatives, joined to the sheet. Do not
add a file to the five-file canon table in this session.
