# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5a-G5f first. G5a is fixed pending owner re-flight (s6893). G5b sheets fixed s6896, owner confirmation pending. The paused unit is at the bottom.

# NEXT: G5b, do black steps go with the s6896 edge fix, then what is left at dd3 and past the map edge
HYPOTHESIS-ID: g5b-terrain-drops
State: read PORTING-STATE s6896 first. Sheets = last + edge quad wrapping s16 in TriGen, fixed at dd>1 (ROGUESQ_G5B_TG_FIX, =tog for same-run). Arm template scratch/s6896/arm.zsh <lvl> <dd> <name> "<env>" <delay> <dur>; score tools/g5b_tg_join.py tg sh, tools/g5b_tg_tog.py sh; frames scratch/s6896/onoff.py. Captures are ~1.9 GB each: delete when scored.
Unit, one iteration:
1. Black steps: reach the post-MISSION FAILED scene at dd4 with TG_FIX=tog. H-sheet: steps gone in on seconds. H-other: steps in both, then look for a second cause. Same scene at dd1 is the control s6895 still owes.
2. dd3 arm on the fix: expect 0 sheets. dd3 has never run with it.
3. Quads past the + edge: base wraps whole, so they draw at the far - side of the map. Count them in the witness (window cells >= 64, or bases in the - half with the camera near the + edge) and look for stray terrain there. If real, drop them at dd>1 or spend the DD_EDGE budget on the - side only.
4. Is the s6895 span rule still needed? ROGUESQ_W_SHEET_PX off at dd4 with TG_FIX on, look at frames for bands: long mixed-sign tris may have been these quads.
5. G5f: with sheets gone, score spike-shaped lines on frames, then an owner sheet. dd1 W_CLAMP stays off: its extra small transients (306 vs 157) are unexplained.
Still open from s6893: is block 8074A380 live when copyNativeToRAM writes it. Levels 10 and 15 census used only 0x9E00.
Ask owner when a human is next on: fly dd2 and dd4 at the owner recipe. Are terrain drops gone or fewer? Spikes fewer? Look at docs/owner_sheet_s6896_edge_fix_on_off.png and docs/owner_sheet_s6895_wedge_vs_hardware.png: are those what you called a drop? docs/owner_sheet_s6895_steps_vs_hardware.png: have you seen black steps, and at dd1 too? A short screen recording of a drop would settle it. Also re-fly Gerrard V past half way at dd2 and dd4, more than once: does it crash?

# PAUSED until G5 closes
# NEXT: 21:9 flight on 144 Hz at a free XG49V corner, or what enters the 72 ms state if still built-in alone
Old slug: g1e-present-drain
Why: s6891: reports need the XG49V or built-in (both UG27 give none, even uncovered) and only a partly visible window. Externals left at ~22:15, so 21:9 flight on 144 Hz has no data. Built-in off reads 39 ms, acq 0.03; s6889's 72 ms ring had acq 14.93.
FIRST, no game run: build tools/g1e_display_state.swift and tools/g1e_display_free.swift (xcrun swiftc -O, DEVELOPER_DIR set; binaries also in scratch/s6891). Runner template with 45 s report gate and display census: scratch/s6891/arms60.zsh (kills m6_god_common.sh before the game, or it relaunches). Set P to a free corner: the window only needs part of itself uncovered. Never use a UG27.
If the XG49V is online: arms 21:9 dd4 no SCREEN_JOB off, gate, stall (ST string in scratch/s6891/arms.zsh), 240 s, then 4:3 off. H-60only (10-12 ms, no level) / H-wide-level (a level holds at 21:9). Score: bash scratch/s6891/score.sh pattern, g1e_present_latency.py --last 120 --hz 144. Control: 200 ms stalls lift to 24-39 ms and return.
If built-in alone: find what enters the 72 ms state. Ungated arms, same recipe: window centred full size vs free strip; fully visible vs mostly covered; stall lever arm (ROGUESQ_PRESENT_TEST_STALL 200 ms) to see whether a slip can push o1 from acq 0.03 to ~15. H-slip (stalls enter it) / H-window (placement or cover selects it) / H-display (needs a display not now attached; then wait for it). Read acq_ms p50 on ungated rings. Add the stall control: s6891's set had none.
Default stays off until the owner chooses. DRAIN not in OWNER-OPT-INS.
Also open: the 3% vs 12.5% off-pattern share between the two 144 Hz gate rings. Input-to-photon not measured. wg vs woff rate 54.6 vs 58.7 needs a matched-cover repeat before it means anything.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: are the two UG27 panels powered on and how are they connected; did you undock around 20:48 and 22:15 on 2026-11-04; which screen do you play on at what refresh rate; is 60 fps on the 144 Hz display visibly uneven, and does 120 Hz (if offered) look better; does PRESENT_INFLIGHT=2 feel better; does 21:9 flight feel smoother after s6885 (ROGUESQ_WIDE_EARLY=0 compares); SCREEN_JOB default; add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited); decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6883_spancell.png, docs/owner_sheet_s6882_219_dd4.png, docs/owner_sheet_s6881_wide_dd4.png, docs/owner_sheet_s6880_219_depth.png, docs/owner_sheet_s6879_wide_depth.png, docs/owner_sheet_s6874_dd_edge.png, docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png, docs/owner_sheet_s6872_optin_samepose.png.
Open from s6884: decodeVI now runs on the worker up to one tail after the VI. FAST vs PROBES not split. Best sx gap: 4:3 box 1106 px is +0.82%, not closed.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous, 21:9 lvl5/lvl10 at 300 s. lvl10 cloud clock only on an owner report.
