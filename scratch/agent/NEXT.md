# NEXT: G1 (c) flight framebuffer for the next uncovered level
HYPOTHESIS-ID: g1-coverage-cd

s6631 closed g1d-levelselect-heap. Do not reopen it and do not edit the
heap cap. Heap `8010FEFC` stops at `801163E4` for aspect wider than 4:3
(`did=3`, terminator at e4-0x10). Evidence:
scratch/agent/s6631_heapcap_at/ownership_verdict.json. Level 1 flight
already has a retail match in docs/G3-INFLIGHT-DIFF.md. This unit is the
next level that does not.

ONE run, retail 4:3 (do not set ROGUESQ_ASPECT or ROGUESQ_DRAW_DISTANCE).
Screen unlocked. From build/ with the ROM beside it. SIGKILL. One game.
Copy the key path in tools/agent/m6_mission_tmpl.sh.in (title origin
0x790400, hangar 0x6AB400, mission 0x690400) but stop 30 s after the
mission origin. Do not hold 555 s. Env, plus the COMMON list in that
template:

    ROGUESQ_FORCE_UNLOCK=1
    ROGUESQ_FORCE_SAVE_MISSION=2
    ROGUESQ_NO_SAVE_WRITE=1
    ROGUESQ_FB_DUMP_DIR=scratch/agent/s6632_lvl2/fbd
    ROGUESQ_FB_DUMP_EVERY=50
    ROGUESQ_FB_DUMP_VI=1

Output root scratch/agent/s6632_lvl2. If level 2 never reaches
origin 0x690400, record the last origin and stop. Do not add a patch.

DISCRIMINATOR, same run:
- H-present: a dump whose `[vi]` / `[fbdump]` origin is the mission
  (0x690400), not the hangar or the attract demo, shows sky, terrain,
  a craft-sized body and a HUD cluster. Score pixel classes; do not
  eyeball only. Positive control: the level-select floor ppm
  scratch/agent/s6631_heapcap_at/wide16/fbd/fb_0001400_w796.ppm is
  non-empty, and a pre-mission dump in this same log has a different
  VI origin.
- H-absent: the mission-origin frame is missing terrain, craft or HUD
  as a class. Name which class, keep the ppm, and do not patch in
  that run.
- A hangar-only or attract-only origin is incomplete, not a pass.
  docs/g3_retail_lvl1_flight_oracle.png is a method reference for a
  different level, not the comparison target.

No heap edit, no aim or steer work, no default change, no queued soak.
