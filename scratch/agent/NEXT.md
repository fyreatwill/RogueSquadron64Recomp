# NEXT: level-5 flight capture under the frozen class rule
HYPOTHESIS-ID: g1-coverage-cd

s6636 closed the level-4 sunset offline. The rule in
tools/g1_flight_class.py now accepts a bright orange sky (luma >= 140,
R >= G+40, R >= B+20) and a dark hull against a bright chase band
(median >= 120, fraction >= 0.06 at least 50 below that median).
canon_bad stayed 0. Six of seven s6635 phase-7 frames pass. n=2300
stays a terrain near-miss at rel 0.065. Do not edit the classifier
in this session. Do not lower 0.08. No heap edit, no aim, no
draw-distance, no aspect, no default change. No objective (d).

Precontrol, before any launch. It must print canon_bad 0:

    python3 tools/g1_flight_class.py

If the screen is locked, stop and write BLOCKED with NEEDS-HUMAN:
physical. Check both of these; either Yes/true means locked:

    ioreg -n Root -d1 | grep IOConsoleLocked
    ioreg -n Root -d1 -a | grep -A1 CGSSessionScreenIsLocked

Adapt scratch/agent/s6635_lvl4.sh into scratch/agent/s6637_lvl5.sh.
Change the output directory, and set ROGUESQ_FORCE_UNLOCK=5 and
ROGUESQ_FORCE_SAVE_MISSION=5. Delete the inline Python classifier
in that script. Its precontrol is the command above, and a non-zero
exit must abort before the game starts. Keep the retail 4:3 route:
menu start/z schedule, no stick, SIGKILL 30 s after the first
post-hangar origin 0x690400, dumps every 50 VIs. Run from build/
with the ROM beside the binary. Kill with SIGKILL only.

One game run. Then:

    python3 tools/g1_flight_class.py <phase-7 ppm paths> <one title ppm> <one hangar ppm>

Read the contact sheet before calling a frame a flight. Build it
from four post-hangar dumps the way docs/g1_lvl4_flight_s6635.png
was built, and write it to docs/g1_lvl5_flight_s6637.png.

H-rule-holds: the post-hangar frames that show sky, terrain, craft
and HUD pass, and the same-run title and hangar dumps fail overall.
Level 5 (c) closes. The next capture is level 6 with the rule
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
