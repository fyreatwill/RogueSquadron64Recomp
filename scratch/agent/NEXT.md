# NEXT: level 15 flight framebuffer, rule frozen
HYPOTHESIS-ID: g1-coverage-cd

s6648 accepted the level-14 overcast flight with the rule frozen
(6/9). Do not edit `tools/g1_flight_class.py` in this session.
The terrain-floor miss (rel 0.065), the terrain-ceiling miss
(rel 0.357) and the ground-view frame are not a license to move
0.08 or 0.33. No heap, aim, draw-distance, aspect, or default
change. Do not start level 16.

Level 15 needs the planet unlock. Clone `scratch/agent/s6643_lvl10.sh`
to `scratch/agent/s6649_lvl15.sh`. Change the output dir to
`scratch/agent/s6649_lvl15` and set `ROGUESQ_FORCE_UNLOCK=15` and
`ROGUESQ_FORCE_SAVE_MISSION=15`. Keep
`ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Keep the 420 s mission wait
and the 30 s hold. Retail 4:3, draw distance unset, aspect unset.

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
`docs/g1_lvl15_flight_s6649.png` only if a post-hangar flight
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
not drop the planet unlock in this session.

DISCRIMINATOR: the pass/fail lines on the phase-7 dumps plus
the same-run title. A visible flight that scores 0/N is not
a license to edit the classifier in the same session.
