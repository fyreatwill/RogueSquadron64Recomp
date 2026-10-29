# NEXT: level 4 flight capture under the extended class rule
HYPOTHESIS-ID: g1-coverage-cd

s6634 closed the level-3 numeric proxy. Do not retune
tools/g1_flight_class.py and do not recapture level 3. Do not edit the
heap or any default. No aim or steer work. No queued soak.

Precontrol, before any game launch. It must print canon_bad 0:

    python3 tools/g1_flight_class.py

That table is oracle pass, level-2 fb_0002700 pass, level-3 fb_0002700
pass, level-select floor fail, s6633 title dump fail. If it does not
hold, the tool on disk is not the s6634 rule. Stop and do not launch.

Then one retail 4:3 capture. Copy scratch/agent/s6633_lvl3.sh to a new
script, change only the mission index and the output directory:

- ROGUESQ_FORCE_UNLOCK=4
- ROGUESQ_FORCE_SAVE_MISSION=4
- output scratch/agent/s6635_lvl4/ (do not rm the s6633 dumps)
- same in-process start/z schedule, draw distance unset, aspect unset
- SIGKILL 30 s after the first post-hangar origin 0x690400
- run from build/ with the ROM beside it; one game; screen unlocked

After the run, score every mission-origin dump:

    python3 tools/g1_flight_class.py scratch/agent/s6635_lvl4/fbd/fb_*.ppm

and build one contact sheet of four of those frames. Read the sheet.

H-rule-holds: the mission frames that show sky, terrain, a craft and
the radar also pass the tool, and title or hangar frames from the same
run fail it.
H-new-class: the sheet shows a flight (terrain, craft, HUD) but the
tool rejects those frames. Record the miss. Do not edit thresholds in
this session.
H-no-picture: the route never reaches a post-hangar 0x690400, or the
dumps are empty or a menu. That is a route failure, not a scorer
failure.

DISCRIMINATOR: the sheet plus the tool lines for the mission dumps.
H-rule-holds advances level 4 (c) and the next capture is level 5 with
the same frozen rule. H-new-class leaves level 4 (c) as a picture only.
H-no-picture does not change the class rule.
