# NEXT: level 17 flight framebuffer, rule frozen
HYPOTHESIS-ID: g1-coverage-cd

s6650 accepted the level-16 Beggar's Canyon race with the rule
frozen (3/11 of the post-hangar mission-origin dumps). The flight
stayed phase=5 because `rs64_phase_ord` bumps only on a VI-width
change and both the hangar and the flight are width 512. Do not
require phase==7. Score every post-hangar dump whose origin field
is `0x620400` or `0x690400`.

Do not edit `tools/g1_flight_class.py`. Do not move 0.08. The
level-16 pass at rel 0.083 is inside the band. Pause overlays
(radar 0, rebel-crest menu) are the start-key schedule, not a
missing HUD. Do not add an arm for them. Do not set
`ROGUESQ_FORCE_PLANET_UNLOCK` (level 17 is not 10 or 15). Do not
start level 18. No heap, aim, draw-distance, aspect, or default
change.

Clone `scratch/agent/s6650_lvl16.sh` to
`scratch/agent/s6651_lvl17.sh`. Change the output dir to
`scratch/agent/s6651_lvl17` and set `ROGUESQ_FORCE_UNLOCK=17`
and `ROGUESQ_FORCE_SAVE_MISSION=17`. Keep the 420 s mission
wait and the 30 s hold. Retail 4:3, draw distance unset, aspect
unset.

Before launch, the screen must be unlocked
(`IOConsoleLocked` / `CGSSessionScreenIsLocked`) and
`python3 tools/g1_flight_class.py` must print `canon_bad 0` and
`mission 11/13`. Abort if either fails. Run from `build/` with
the ROM beside the binary. SIGKILL the game. One instance.

After the run, score the post-hangar mission-origin dumps. Also
score the same-run title and the craft-select dump.

    python3 tools/g1_flight_class.py <mission dumps> <title> <craft-select>

Write a contact sheet of four flight frames to
`docs/g1_lvl17_flight_s6651.png` only if a post-hangar flight
picture exists.

H-rule-holds: at least one mission-origin frame passes all four
clauses, the same-run title fails overall, and the run has
0 crashes. Record the pass count. The rule stays frozen.
H-new-class: the sheet is a flight and zero mission-origin
frames pass all four clauses. Record which clause fails and,
for a sky miss, luma / R-G / R-B / G-B of the sky box. Do not
add an arm in this session.
H-no-picture: no post-hangar `0x690400` inside 420 s. Record
the last VI origin and stop. Do not raise the wait in this
session.

DISCRIMINATOR: the pass/fail lines on the mission-origin dumps
plus the same-run title. A visible flight that scores 0/N is
not a license to edit the classifier in the same session. A
pause overlay with radar 0 is not H-new-class if another frame
in the same window passes.
