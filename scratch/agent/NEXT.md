# NEXT: G3 menu/cutscene fidelity at RETAIL settings (4:3, dd1, FPS60 off) (CURRENT-TRUTH item 37)
HYPOTHESIS-ID: g3-retail-43-menus
Why: flight is H-equal at 4:3, 16:9 and 21:9 (items 33/34/36), and menus/cutscenes are H-equal at 21:9 and 16:9 (items 31/32,
s7142-s7156). Nothing has measured the menus/cutscenes at retail 4:3. s7180 saw one incidental single-source datum: AVAILABLE CRAFT /
SELECT YOUR CRAFT at 4:3, centre 0.032, 0 >0.05, identical by eye.
Plan (reuse the s7155/s7156 recipe, swapping the env to retail): tools/s7146_arm.zsh default boot, with ROGUESQ_FPS60=0
ROGUESQ_DRAW_DISTANCE=1 ROGUESQ_ASPECT=4:3, capture 320x240, then s7152_post + s7143_affine fit. Screens: logo recede, chapter title,
crawl, title, SELECT GAME, SELECT LEVEL, AVAILABLE CRAFT, level description (512x448 INTERLACED field: check that RT64 presents both
fields, not every other row doubled), mission intro cutscene, pause menu, MISSION FAILED.
Read the s7155 + s7156 entries (grep '^## Session 715[56]' PORTING-STATE.md) for exact args before running.
Hypotheses: H-equal (all screens within the s7155 band after one fit), H-rect (RECT_ASPECT must be inert at 4:3: arm R1 = +ROGUESQ_RECT_ASPECT=0
gives identical scores), H-interlace (the 448-line field screen differs: RT64 line-doubles one field or shows a wrong field order),
H-tool (painted-square control fails, or the crop collapses on interlaced frames: s7180 control fix skips them, but score still crops).
Disk >= 20 GB per run; one game run at a time; never write WORKING to STATUS; owner save rule stands.
