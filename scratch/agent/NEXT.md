# NEXT: level-9 flight capture, class rule frozen
HYPOTHESIS-ID: g1-coverage-cd

s6641 accepted level 8 offline (6/7 phase-7 dumps). This session
captures level 9. Do not edit `tools/g1_flight_class.py`. No heap,
aim, draw-distance, aspect, or default change. Do not move 0.08,
0.33, the luma>=70 blue arm, the luma>=80 orange arm, or the
edge>=0.05 cut.

Copy `scratch/agent/s6640_lvl8.sh` to `scratch/agent/s6642_lvl9.sh`.
Change only the output directory and the two level selectors:

    ROGUESQ_FORCE_UNLOCK=9
    ROGUESQ_FORCE_SAVE_MISSION=9

Retail 4:3. Draw distance stays unset. Aspect stays unset. Run from
`build/` with the ROM beside it. SIGKILL the game. Before launch,
`python3 tools/g1_flight_class.py` must print `canon_bad 0` and
`mission 11/13`. Refuse the run if `IOConsoleLocked` is Yes or
`CGSSessionScreenIsLocked` is true.

After the run, score every phase-7 dump, plus the same-run title
and the craft-select or hangar dump, with:

    python3 tools/g1_flight_class.py <those files>

H-rule-holds: at least one phase-7 frame passes all four clauses,
the same-run title fails overall, crash count is 0, and the sheet
shows sky, terrain, craft and HUD. Leave the tool frozen. The
session after that captures level 10, which needs
`ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Do not start level 10 here.
H-new-class: the sheet is a flight and every phase-7 frame fails.
Record sky, terrain, craft, HUD, edge, luma and R-G for each
phase-7 dump. Do not edit the tool in this session.
H-no-picture: no post-hangar flight dump. Record the last VI
origin and do not retune the route.

DISCRIMINATOR: the frozen tool's pass/fail lines on the phase-7
dumps and the same-run title, plus crash count from that run's
log. A visible flight that scores 0/N is not a license to edit
the classifier in the capture session.
