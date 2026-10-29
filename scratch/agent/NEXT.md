# NEXT: one retail capture of level 18
HYPOTHESIS-ID: g1-coverage-cd

s6652 accepted the level-17 trench chase offline. Do not recapture
level 17. Do not edit `tools/g1_flight_class.py`. Do not move 0.08,
0.33, or dark >= 0.60. Do not change the sky sample window
(y 0.02-0.18, x 0.15-0.85). Do not lower the new luma floor from 38
to chase n=2250. n=2250 is not required.

The grey-trench arm is already in the classifier: luma in [38, 55],
|R-G| <= 8, |R-B| <= 8, |G-B| <= 8, and at least 0.80 of the
sky-window samples have channel spread <= 8. It accepted
`scratch/agent/s6651_lvl17/fbd/fb_0002300_w512.ppm` (1/10). mission
stayed 11/13 because m3150's neutral8 is 0.613. Both title skies
stayed false.

This session captures level 18 only. Copy
`scratch/agent/s6651_lvl17.sh` to `scratch/agent/s6653_lvl18.sh`.
Change the output directory to `scratch/agent/s6653_lvl18` and set
`ROGUESQ_FORCE_UNLOCK=18` and `ROGUESQ_FORCE_SAVE_MISSION=18`. Leave
draw distance unset, aspect unset, and do not set
`ROGUESQ_FORCE_PLANET_UNLOCK`. The screen must be unlocked
(`IOConsoleLocked` is not Yes, and `CGSSessionScreenIsLocked` is not
true) or the run is void.

Before launch:

    python3 tools/g1_flight_class.py

That must print `canon_bad 0` and `mission 11/13`. Then:

    zsh scratch/agent/s6653_lvl18.sh

Confirm `run.log` echoes `[dd] ROGUESQ_DRAW_DISTANCE multiplier 1`,
`[g1d-drop] aspect=<unset>`, `[lvsel] cursor=18`, and
`[initMission] call#1 B40=0x12`. Score every post-hangar dump with
the frozen classifier. Levels 16 and 17 stayed phase 5 because the
hangar and the flight were both width 512. Do not require phase 7.
A dump whose own origin field is the other buffer is still the
flight picture when `0x690400` is in the VI log.

H-rule-holds: at least one post-hangar dump passes sky, terrain,
craft and HUD. Record the pass count and stop. Do not edit the
classifier.
H-new-class: the sheet is a flight (terrain, craft, HUD visible)
and zero dumps pass all four clauses. Leave the classifier frozen.
Name which clause misses on the clearest chase frame, with the
numbers. The next session tries one arm.
H-no-picture: no post-hangar `0x690400`, or the dumps are not a
flight. Record the last origin and stop.

Do not start an objective-hit run in the same session.
