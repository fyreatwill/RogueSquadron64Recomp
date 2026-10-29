# NEXT: level 14 flight framebuffer, rule frozen
HYPOTHESIS-ID: g1-coverage-cd

s6647 accepted the level-13 lava flight with the rule frozen
(2/9). Do not edit `tools/g1_flight_class.py` in this session.
The seven terrain-ceiling misses (rel 0.362..0.611) are not a
license to raise the 0.33 cap. No heap, aim, draw-distance,
aspect, or default change. Do not start level 15. Do not set
`ROGUESQ_FORCE_PLANET_UNLOCK` (only levels 10 and 15 need it).

Clone `scratch/agent/s6647_lvl13.sh` to `scratch/agent/s6648_lvl14.sh`.
Change the output dir to `scratch/agent/s6648_lvl14` and set
`ROGUESQ_FORCE_UNLOCK=14` and `ROGUESQ_FORCE_SAVE_MISSION=14`.
Keep the 420 s mission wait and the 30 s hold. Retail 4:3,
draw distance unset, aspect unset.

Before launch, the screen must be unlocked
(`IOConsoleLocked` / `CGSSessionScreenIsLocked`) and
`python3 tools/g1_flight_class.py` must print `canon_bad 0` and
`mission 11/13`. Abort if either fails. Run from `build/` with
the ROM beside the binary. SIGKILL the game. One instance.

After the run, score every phase-7 dump whose VI origin is the
mission buffer (the dump's own origin field may be the other
of `0x690400` / `0x620400`). Also score the same-run title and
the craft-select or hangar dump.

    python3 tools/g1_flight_class.py <phase-7 dumps> <title> <craft-select>

Write a contact sheet of four flight frames to
`docs/g1_lvl14_flight_s6648.png` only if a post-hangar flight
picture exists.

H-rule-holds: at least one phase-7 frame passes all four
clauses, the same-run title fails overall, and the run has
0 crashes. Record the pass count. The rule stays frozen.
H-new-class: the sheet is a flight and zero phase-7 frames
pass all four clauses. Record which clause fails and, for a
sky miss, luma / R-G / R-B / G-B of the sky box. Do not add
an arm in this session.
H-no-picture: no post-hangar `0x690400` inside 420 s. Record
the last VI origin and stop. Do not raise the wait and do
not add the planet unlock in this session.

DISCRIMINATOR: the pass/fail lines on the phase-7 dumps plus
the same-run title. A visible flight that scores 0/N is not
a license to edit the classifier in the same session.
