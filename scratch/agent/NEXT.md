# Next work unit: read s5443_res_a/b (results-screen advance + post-results transition)
HYPOTHESIS-ID: m6-flown-render-fidelity

s5442 post_late soaks stayed in flight (no transition); see PORTING-STATE s5443. Queued m6_res_late_a/b: LATE=340, 540 s hold.
- Read SOAK-RESULTS.md tail + scratch/agent/m6/s5443_res_*/summary; convert fbd dumps near the end with `python3 -I tools/ppm2png.py in.ppm out.png` and look at them (results screen vs hangar vs title vs frozen).
- Hypotheses: (H1) fail fires ~swap 8100 and a/start advance it to hangar/title -> transition endurance data, check crashlines/vi_stalls30s and fbhash maxrun; (H2) fail does not fire (z-drop timing/variance) -> still flight, change recipe to keep z and add a at 380 s; (H3) results screen persists despite a/start -> input path at results is the defect.
- Any CRASH/stall: ASan arm in a separate build dir for a backtrace, name writer, root-cause fix.
