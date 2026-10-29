# NEXT: level-10 flight capture, class rule frozen
HYPOTHESIS-ID: g1-coverage-cd

s6642 accepted level 9 on one retail capture (8/13 phase-7 dumps).
This session captures level 10. Do not edit `tools/g1_flight_class.py`.
No heap, aim, draw-distance, aspect, or default change. Do not move
0.08, 0.33, the luma>=70 blue arm, the luma>=80 orange arm, or the
edge>=0.05 cut.

Copy `scratch/agent/s6642_lvl9.sh` to `scratch/agent/s6643_lvl10.sh`.
Change the output directory, the two level selectors, the planet
unlock, and the shell wall:

    ROGUESQ_FORCE_UNLOCK=10
    ROGUESQ_FORCE_SAVE_MISSION=10
    ROGUESQ_FORCE_PLANET_UNLOCK=0xFF

In the mission-wait loop, change `-lt 420` to `-lt 720`. Level 10
without the planet unlock sits in a planet viewer for ~790 s.
With the unlock, onset has still taken up to ~400 s, so the old
420 s wall can expire before the 30 s hold. Do not change
`PROBE_PHASE_TIMEOUT`. Retail 4:3. Draw distance stays unset.
Aspect stays unset. Run from `build/` with the ROM beside it.
SIGKILL the game. Before launch, `python3 tools/g1_flight_class.py`
must print `canon_bad 0` and `mission 11/13`. Refuse the run if
`IOConsoleLocked` is Yes or `CGSSessionScreenIsLocked` is true.

After the run, score every phase-7 dump, plus the same-run title
and the craft-select or hangar dump, with:

    python3 tools/g1_flight_class.py <those files>

H-rule-holds: at least one phase-7 frame passes all four clauses,
the same-run title fails overall, crash count is 0, and the sheet
shows sky, terrain, craft and HUD. Leave the tool frozen. The
session after that captures level 11. Do not start level 11 here.
H-new-class: the sheet is a flight and every phase-7 frame fails.
Record sky, terrain, craft, HUD, edge, luma and R-G for each
phase-7 dump. Do not edit the tool in this session.
H-no-picture: no post-hangar flight dump. Record the last VI
origin and the keys.log line (`notitle`, `nohangar`, or
`nomission`). Do not retune the route or the classifier.

DISCRIMINATOR: the frozen tool's pass/fail lines on the phase-7
dumps and the same-run title, plus crash count from that run's
log. A visible flight that scores 0/N is not a license to edit
the classifier in the capture session.
