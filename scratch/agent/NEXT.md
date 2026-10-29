# NEXT: G1 (c) flight framebuffer for level 3
HYPOTHESIS-ID: g1-coverage-cd

s6632 closed level 2 (c). Do not redo it and do not edit the heap cap.
Level 2 evidence: scratch/agent/s6632_lvl2/keys.log and
docs/g1_lvl2_flight_s6632.png. Selector B40=2. 7/8 post-hangar dumps at
VI origin 0x620400 (the buffer interleaved with the route key 0x690400)
pass all four classes. 0/49 dumps at other origins in that run pass.

ONE run, retail 4:3. Do not set ROGUESQ_ASPECT or ROGUESQ_DRAW_DISTANCE.
Screen unlocked (IOConsoleLocked is not Yes). From build/ with the ROM
beside it. SIGKILL. One game. Stop 30 s after the first post-hangar
0x690400. Output root scratch/agent/s6633_lvl3.

Env, plus the COMMON list in tools/agent/m6_mission_tmpl.sh.in:

    ROGUESQ_FORCE_UNLOCK=3
    ROGUESQ_FORCE_SAVE_MISSION=3
    ROGUESQ_NO_SAVE_WRITE=1
    ROGUESQ_FB_DUMP_DIR=<absolute scratch/agent/s6633_lvl3/fbd>
    ROGUESQ_FB_DUMP_EVERY=50
    ROGUESQ_FB_DUMP_VI=1

Drive menus with the in-process schedule that reached level 2 (start/z
from t=10 s, hold 1800 ms, z only after t=74). winctl is trusted on this
machine but s6604 and s6631 saw no winctl key, and s6632 did not use it.
Require hangar origin 0x6AB400 before counting 0x690400, or the hit is
the attract demo. Confirm [saveslot] force=3 and [lvsel] cursor=3 /
initMission B40=3. If the cursor is not 3, the capture is the wrong
level: do not score it as level 3.

CLASS RULE (frozen in s6632; a frame passes only if all four pass):
- sky: upper-band dark fraction >= 0.60, or upper mean luma >= 70 and
  mean R <= mean G+15
- terrain: lower-band luma stddev >= 18
- craft: center pink-engine fraction in [0.003, 0.05], or yellow-engine
  fraction in [0.002, 0.015] with pink < 0.001
- HUD: top-right radar-red fraction >= 0.02
Positive control, same scorer: docs/g3_retail_lvl1_flight_oracle.png and
scratch/agent/s6632_lvl2/fbd/fb_0002700_w512.ppm pass; the level-select
ppm scratch/agent/s6631_heapcap_at/wide16/fbd/fb_0001400_w796.ppm fails;
a pre-mission dump in THIS log has a different VI origin and fails.
A hangar-only or attract-only origin is incomplete, not a pass.

DISCRIMINATOR:
- H-present: at least one post-hangar dump (0x690400 or the buffer
  interleaved with it, as in s6632) passes all four classes, and the
  pre-mission dumps do not.
- H-absent: the mission-window frames miss a class. Name which class,
  keep the ppm, and do not patch in that run.

No heap edit, no aim or steer work, no default change, no queued soak.
