# NEXT: is the HUD visible and centred during lvl16's paused window at wide aspect?
HYPOTHESIS-ID: g1d-lvl16-paused-hud-window

Why: s6860 lvl16 sweep dump VI 3000 showed ring 648..731, icon 308, disc in ring, one or two swaps before the gate reopened. [region-gate] is off with
paused=1 for swaps ~2556-3000 and ~3164-3348 in all three lvl16 runs. The s6721 pause gate holds the anchor off while the pause byte is set; if the race intro
draws the flight HUD with that byte set, the owner sees a centred HUD for several seconds at race start.
Hypotheses: H-edge (HUD not drawn inside the window; only the frame at the edge shows it, one-frame flash at most) / H-window (HUD drawn centred through the
window: anchor must follow something other than the pause byte) / H-nonhud (window is a non-HUD screen, nothing to fix).
Discriminator: one run, same binary: copy scratch/s6860/arm.sh with FBD_EVERY_V=30, `arm.sh 16 win 21:9 1024`, then scratch/s6860/ring.py on the run dir over
VI 2500-3400, joined to the [region-gate] swaps. Control: frames after the gate reopens must read ring ~903 in the same run. Check other levels' paused windows from the same log line.
Outcomes: H-window -> gate on the real pause-menu state, same-build A/B, frame check lvl16 + pause menu lvl1 (s6721 must not regress); H-edge -> measure flash length, fix only if >1 frame.
Then: audit hard-coded heap-address tests in host patches (tools/apply_s*.py, src/main, src/rsp) as a class; s6860 lvl10 is the model. Also list vp 0x80138D20 elements on two
more levels (ROGUESQ_HUD_LOG=1) to check nothing projected sits in 0x80110000..0x80300000.
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png.
