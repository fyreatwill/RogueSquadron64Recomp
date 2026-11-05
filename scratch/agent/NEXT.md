# NEXT: fold lvl10 same-pose pair, then split the FPS60 cost between logging and ASYNC
HYPOTHESIS-ID: g1d-wide-fps60-cost
Why: s6883 fixed the span overrun. Q219 hits p50 60 on the no-logging bundle, but p10 is 47 and the 30 -> 60 change bundles logging, ASYNC, NODRAIN, FAST, PROBES.
First: read SOAK-RESULTS for s6883_l10z / s6883_l10d (HOLD_S=215, frames in scratch/s6883/e). Needs caps=6 on both. Score with scratch/s6883/ref2.py style cmp and tickdiv.py (scratch is gitignored, both live there). If a soak got caps=0, x never reached 189.7: raise HOLD_S, 600 s cap allows it.
Hypotheses: H-log (recipe logging alone holds wf at 30) / H-async (non-ASYNC RDP drain holds it at 30) / H-both.
Measure, one build (no rebuild needed), same-pose where possible: lvl1 21:9 dd4 FPS60, four arms: recipe, recipe + ASYNC/NODRAIN, no-logging without ASYNC/NODRAIN, no-logging bundle. Pin dt 1/60 so arms share a path, and gate the window on phase and pose, not on harness mission_t (TITLE_ORIGIN regex counts mission from t=6 s, which is why the s6883 q arm capture missed the game). Take a capture in flight per arm.
Control: q219 repeat must land within its own p50 and p10, or rate differences say nothing.
Also: what the 14 s below 50 in q219 are (dense scene, ucode 11.8 p90 is under 16.7, so look at Gfx busy and present wait). ns/cmd 224 vs s6810's 178 unexplained.
Outcomes: H-log -> report that owner play is fine and recipe figures understate; H-async -> OWNER-OPT-INS must say FPS60 wide needs ASYNC+NODRAIN; H-both -> record both terms.
Small open item: best sx 1.00% under sy at both widths; measure the 4:3 picture box (1106 px wide; 512:448 x 960 would be 1097).
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree; regen trees compared by object at s6881 only, never linked or run.
Owner judges: docs/owner_sheet_s6883_spancell.png, docs/owner_sheet_s6882_219_dd4.png, docs/owner_sheet_s6881_wide_dd4.png, docs/owner_sheet_s6880_219_depth.png, docs/owner_sheet_s6879_wide_depth.png, docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous, 21:9 lvl5/lvl10 at 300 s. Owner can lift the park for these. lvl10 cloud clock only on an owner report.
