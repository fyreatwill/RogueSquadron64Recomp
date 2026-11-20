# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7679 (2026-11-19).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; item-1 classes DG-EO in "(s7491 migration)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)"; s7533 Next-steps items 1,12,15-21 (classes FD-FZ) in "(s7534 maintenance)"; s7535-s7576 headline + items 17-21 + pre-s7300 superseded in "(s7581 maintenance)"; s7579-s7616 headline + items 19-46 in "(s7622 maintenance)"; s7647-s7659 headline + items 21-35 in "(s7662 maintenance)". Grep there for any sNNNN.

## Headline

**Every engineering goal on the ladder is closed or awaiting the owner's look.** Nothing is broken at the
owner's recipe as far as any instrument can see; remaining items are owner judgements (list in Next steps).

- **NEW s7682: G6c inline-draw audit CLOSED for switch-installed subtypes.** heavyAttachedAudioEmitterNpcHandler is a child of sub 0x37
  (npcWordDevastatorUpdate), which has no stand-in (H-none). tools/g6c_sub_handler_map.py (71 subtypes, positive control npcShieldUpdate):
  every stand-in subtype installed by setupNpcUpdateFunctions reaches addNpcToVisibilityBucket except 0x32 (s7681 hook), rc 0. Default-path
  stand-in subs 0x33/0x36/0x44/0x4F unobserved at runtime (0x4B seen handing off). Rerun the tool after any stand-in table edit.
- **NEW s7681: the s7679 "ghost" shield is drawn by the game; our detector was blind to its draw path (code read + two arms).**
  npcShieldUpdate (sub 0x32, 0x8007AEF8) never calls addNpcToVisibilityBucket: its render case 0x8007B8CC runs the same view test
  via 0x8005940C(view, inst, s3+8, radius) and links itself into the bucket inline. tools/apply_s7681_shield_vt.py (RS64_REPLAY) reports
  that test to the handoff detector, matched to sub 0x32 stand-ins only (ROGUESQ_S7681_SHIELD=0 = old). Attract route s7678: old arm
  held the shield to 14.88 and the near release fired; new arm hands off at depth 38.7 on the shield's first visible draw, 0 releases,
  all 233 other [s7679-life] lines identical, 0 crash. First cut (no sub filter) handed off three sub 0x14 neighbours early via the
  2-unit position fallback (37.4 vs 31.0): caught and fixed in-session. heavyAttachedAudioEmitterNpcHandler uses the same inline path.
- **NEW s7680: the s7679 near release does not fire in flight (same-run control).** Forced L5 dd4 16:9 FPS60 STANDINS HOLD=odd 200 s:
  default NEAR=15 0 [s7679-rel], ghost score 0 GHOST (= s7676); control NEAR=99 4 releases, held frames 2491 -> 92; both alive, 0 stall.
  H-attract-only: the cut only touches the attract shield. Recipe tools/s7680_flight_release.zsh <out> <level>.
- **NEW s7679: a held stand-in drew an object the game never draws; released now (two arms, same deterministic attract route).**
  Per-item life table ([s7679-life], STANDINS_LOG): never-spawned stand-ins sit at depth >= 42.9 on L0/L7 (bridging far objects), and real objects'
  first accepted draws are at depth >= 18.0 (137 first calls). One outlier: L5 attract item 8053EDE0 sub 0x32 (handler-picked model "shield") is
  spawned at depth 38 and then never calls addNpcToVisibilityBucket, so the s7672 hold drew it for 706 frames down to 4.6 units, 1.3 units from a
  real object. Fix ROGUESQ_S7679_NEAR=15 (default inside STANDINS; =0 old, =odd control): a hold whose real object has not drawn is dropped
  below depth 15 (depth-only view-test capture, works without logging). Old arm: scorer NOREF-GHOST rc 1 (held_dmin 4.6); fix arm: 1 release
  (depth 14.88, age 95), RELEASED rc 0, item_hits 13269/16119/11416 and drawn 84/49/97 identical to old, 0 crash both. tools/s7675_ghost_score.py
  now scores open holds at level change (they never reached the 899-frame line) and NOREF subtypes against the all-subtype first-draw minimum
  (--selftest 5 cases PASS). Residual: the shield still shows from depth 38 to 15 (the game gives no earlier signal it hides it).
- **NEW s7678: stand-ins survive REAL level changes (H-leak refuted, two arms, same frames).** No-input attract playlist route
  (tools/s7678_attract_run.zsh, dd4 16:9 FPS60 STANDINS=1, 420 s, deterministic) loads L0->5->7->10: rebuild fires on each, new level's
  handoffs match by item (item_hits L5 16119, L7 11416, wrong 0); planted stale map (ROGUESQ_S7678_STALE=1, control only) on the
  same frames drops item_hits to 0/0. On a level change the H-leak signature is item_hits collapse, not wrong=. 0 crashes both arms.
  Gate cache now sees imports served from __pycache__ (tools/gate_trace.py; import control discriminates: FAIL without the fix).
- **s7677: ghost widening clean (L2/L5 scorer rc 0: L5 AT-PT 2 GATE + 2 UNHELD, 0 GHOST) -> H-gate on L1/L2/L4/L5.** Stand-in
  item map (rs64_bk_ret) is now keyed on the rebuild generation, not the object count (ROGUESQ_S7677_GEN=0 = old). Hangar abort
  route (3 loads L15): dat reloads at the same address so the old key was right (wrong 0); planted same-count reorder
  (ROGUESQ_S7677_PLANT=1) old 84350/84350 wrong matches, fix 0; 3/3 arms alive. Recipe scratch/s7677_run.zsh old|fix (PLANT=p). Gate sweep 133/135 then GR/GX rows for s7675 sites -> all green.
- **s7676: the G6c "ghost" thread is CLOSED as H-gate, no code change.** Walker handlers (AT-PT 0x47 L4, AT-ST 0x1F L1)
  draw only inside the same ~30-51-unit camera depth as every other subtype (first-call depth L4 0x47 41.1-51.1, L1 0x1F 28.3-44.9;
  ordinary subtypes 31.6-49.5 = control); their long first-call delay (med 248-821 frames) is approach time, not a hide. The s7675
  never-drawn item 80547410 came no closer than 62.2 units while held (> 51.1) -> GATE: the stand-in correctly bridges a
  distance-gated draw. 0 GHOST rows on L4/L1 (s7675_ghost soaks, both alive, 0 stall). Scorer positive control
  `tools/s7675_ghost_score.py --selftest` (synthetic GHOST rc 1, GATE rc 0) PASS. Widening soaks s7676_ghost_L2/L5 queued.
- **s7674: held stand-ins never leave an on-screen gap.** Every frame our own view test culls a held stand-in is an off-screen
  exit (box/behind/side) or the game's cached copy of one (it view-tests each object on alternate frames, result bit 0x200 in
  state+8): far 0 and pass-then-refused 0 of 10008 (L4) / 3674 (L1) culled frames; same-run control real objects far-rejected
  1548/528. tools/apply_s7674_bucket_vt.py + tools/s7672_handoff_score.py class line (rc 1 on held far/vtpass). Handoff polish closed.
- **s7672: G6c stand-ins no longer vanish at spawn.** The game spawns an object while its own view test still culls it, so
  the stand-in disappeared for 9-443 frames (L1 8/8, L4 36/37 on-screen handoffs) before the real object popped back. Fix
  ROGUESQ_S7672_HOLD=1 (default inside the STANDINS opt-in; =0 old, =odd same-run control): stand-in held until the real object's
  first accepted addNpcToVisibilityBucket. L4 dd4: held 31 handoffs 0 blink 0 double, control 26/27 blink; 5 arms alive 0 stall.
  Instrument tools/apply_s7672_bucket_handoff.py + tools/s7672_handoff_score.py, recipe scratch/s7672/run.zsh.
- **s7670: F6 panel open across a live window resize (windowed, ASPECT=auto, 1226x796 -> 1512x648 21:9-class -> 1280x720):
  3 arms same build, all alive, 0 crash, 0 stall, level_ok=1. Fix arm P: stale path fired, 0 aspect-mismatched draws; old-path arm O
  (ROGUESQ_S7668_ASPECT=0, positive control): exactly 1 squashed draw per resize (~17 ms, vs ~33 draws after a fullscreen toggle);
  no-panel control C equal. A plain resize republishes the window size within one draw. scratch/s7670/run.zsh + score.py.**
- **s7671: rumble cannot stick when a mission is paused/aborted with an effect LIVE (closes the s7669 gap).** Test lever
  ROGUESQ_S7671_FX_ON_KEY=1 arms the game's port-0 effect slot 0x80110520 (the fields startRumbleEffect writes) on every autopilot
  key, ROGUESQ_S7671_FX_TRAIN_MS=N re-arms every 200 ms for N ms after each START. s7326 hangar route, owner recipe, 2 arms:
  forced effects 24/24 and 198/198 reached the game's osMotorStart (positive control), the plant LONG run caught in both. At the
  PAUSE press the game's own osMotorInit+Stop lands 25-26 ms after the forced effect starts, motor ON (run cut at 116 ms), in both
  arms; with effects held live through the stats screen and hangar load every run ended <=368 ms after its last arm (0 tail >800 ms).
  Correction to s7669: the game's mission-side stop is at PAUSE entry (t=180.03, 34 ms after the press), not at the hangar entry.
  Selects H-game-stops; refutes H-host-stuck and H-game-stuck. Pause does not suspend the SI effect service (lever effects play in
  the pause menu; the game itself starts none there). scratch/s7671/score.py. Rumble abort thread CLOSED.
- **s7668: F6 panel held open across level-select -> mission load -> flight and a fullscreen leave/re-enter (owner recipe dd4
  16:9 FPS60, test lever ROGUESQ_PANEL_TEST_WINDOW=open,close): 0 crash, 0 stall, ~60 draws/s throughout, input gate released on
  close; same-run control without the panel equal. Fixed: ~0.5 s squashed panel after each toggle (stale main-thread window size;
  now draws at fb size when aspects differ, ROGUESQ_S7668_ASPECT=0 = old; control arm still shows the mismatch). scratch/s7668.**
- **NEW s7667: settings file + controls.json combination fixed.** A relative `ROGUESQ_CONTROLS=c.json` line in a settings file
  resolved against the cwd and silently gave default controls (arm B pre-fix mismatches=0 vs absolute-path arm A 395); it now
  resolves beside the settings file (rs64_settings_resolve_value, `~/` = HOME; only ROGUESQ_CONTROLS is path-valued). Post-fix same
  build A/B both 395, control C (no settings) 0; tools/test_settings.cpp 23/23. scratch/s7667/run.zsh.
- **NEW s7664: crash reports are now read.** tools/crash_reports.py classifies every game .ips in ~/Library/Logs/DiagnosticReports
  (PLANT / DIAG / FOLDED / NEW); stop_gate.sh blocks on NEW (RS64_CRASH_REPORTS=0 skips). 22 unread reports 11-13..11-19 all attributed
  to planted controls, pre-fix arms (s7326/s7336/s7355/s7356) or env-gated instruments: **0 crashes from normal play.** An owner crash
  now surfaces at the next stop gate: quote its basename in the session entry, and a real one outranks the work unit (G4 reopens).
- **NEW s7663: owner launch settings (owner to try):** `./RogueSquadron64Recomp --preset tv|ultrawide|window` or lines in
  build/settings.txt (src/main/rs64_settings.cpp; env > file > preset; self re-exec, same pid, so pre-main statics see them; loop
  exports ROGUESQ_SETTINGS=0). 5-arm proof + NOEXEC control (H-setenv-enough refuted: a pre-main static misses setenv-from-main) scratch/s7663, OWNER-OPT-INS row. No default changed.
- **s7660: title-boot plume si_addr=0x58 SIGSEGV: 0/20 on the current build (14 default + 6 owner 16:9), same-run
  [CRASH]-handler control PASS; 76 clean boots since s5377 -> CLOSED as gone (H-gone). s7641 race ruled out by code: the
  null is a render-target texture, never a swap-chain drawable. lldb attach -w was a tooling null in that session only.**
- **s7661: lldb attach WORKS in loop sessions (developer mode off): pid + -w + long name + s7660 control verbatim on the real game
  PASS 3/3; H-tcc/H-wait refuted, s7660 transient. New preflight tools/lldb_attach_check.sh (exit 1 = lldb nulls void; /bin/sleep
  is a platform binary and never a valid control); mk_lldb_hold.py soak wrappers run it and VOID on failure.**
- **s7647-s7659 (census-gate sweep + classes TS-4/MK8): ALL CLOSED, 0 behaviour defects** (verbatim in PROJECT-OVERVIEW
  "(s7662 maintenance)"). Standing check: `python3 tools/s7651_gate_sweep.py` (--jobs 2; traced-read cache, cold ~455-530 s,
  warm ~15 s; per-gate cap RS64_GATE_CAP=600) -> 130 GREEN, 5 REPORT, 0 RED; stop_gate.sh --verify blocks any new RED. Key reviews
  by text anchor, never line number (tools/census_rules.py, tools/census_attr.py, tools/ast_cache.py). NEEDS-INPUT gates s7215/
  s7316/s7573 use retained inputs under scratch/s7215, scratch/s7316/ram, scratch/s7573/retained.
- **NEW s7620: G6b F6 Controls panel LANDED (owner to try).** RT64's F1 inspector has no Metal backend, so the panel has
  its own ImGui context drawn through RT64's public post-VI hook (RT64::SetRenderHooks) with imgui_impl_metal; closed = hook
  returns, nothing encoded. Same run (PANEL_TEST): defaults 0 mismatches, scripted bind A=pad:b 112 (control), capture took
  key:E, Reset 0, panel open 0 (600 polls); json roundtrip ok; Save skipped under NO_SAVE_WRITE. Screenshot scratch/s7620/panel.png.
- **NEW s7617: G6a rumble LANDED, default ON (`ROGUESQ_RUMBLE=0` = old no-pak shape, `ROGUESQ_RUMBLE_SCALE` 0..2); owner to feel it.**
  src/main/main.cpp: port 0 reports a Rumble Pak; set_rumble records motor edges, poll_input (owner of `controller`) turns the
  100 ms on-fraction into s = (0.25 + 0.75*duty)*scale and sends SDL_GameControllerRumble(lo=s, hi=0.6s, 150 ms), refreshed
  every 50 ms, cancelled at duty 0. Proof (scratch/s7617, L4 dd1, same build): virtual test pad (ROGUESQ_RUMBLE_TEST=1, its
  Rumble callback = witness) got 14 calls from the game's own 4 osMotorStart at t=84.6 plus 20 from the 1 s injected train;
  RUMBLE=0+PAK_SHAPE_CTL=1 arm: same 4 Start/7 Stop, 0 pad calls. Saves: dev=1 (EEPROM) throughout. **s7638 closed both open
  items:** the virtual pad's rc=-1 was a test artefact (sdl2-compat reads the SDL2 Rumble callback's int 0 as SDL3 bool
  false; scratch/s7638/vpad_rc.c: cb 0 -> rc -1, cb 1 -> rc 0; cb now returns 1, gc arm sdl_fail 0/19); and a fallback chain
  SDL_GameControllerRumble -> SDL_JoystickRumble -> SDL_Haptic landed (advance on failure, 5 s re-probe after all fail,
  `ROGUESQ_RUMBLE_FORCE_PATH=joy|haptic` = control: joy 18/18 delivered, haptic on the non-haptic vpad -> path=none, 0 delivered).
  Game rumble is sparse (L12 130 s: none; L4: one burst at mission start).
- **s7579-s7616 host-side idiom-class audits: ALL CLOSED** (full text, numbers, controls, tool flags verbatim in
  PROJECT-OVERVIEW "(s7622 maintenance)"). TS-2 s7643 (TSan over host runtime, item 21; archived s7662): 1 hardening (s4211 PI ring), SEM blind spot now annotated. TS s7642 (TSan over all RT64+plume, item 21; archived s7662): H-clean, 0 fixes. CF s7641 (framework-callback threads, item 28): 1 fix (plume Metal drawable index race, TSan). AT s7640 (AppKit thread affinity, item 27): 1 fix (RT64 NFD_Init on Gfx Thread). ST s7639 (SDL thread affinity, item 26): 1 fix (F6 panel draw hook). H-clean, no fix: HB s7633 (bridge default-on diag, item 23; 1 getenv latched), HD s7632 (rt64 default-on diag work, item 22; 2 getenv latched), RP s7631 (lib/rt64 kept RDRAM pointers, item 21), RQ s7616, DQ s7615, HM s7614, HP s7613, RG s7612, SN s7611,
  OV s7610, MK s7609, HC s7606, RX s7603, TP s7602, TH s7592, OW-2 s7588, HR s7589, UI s7584, UBSan s7579-s7583 (every
  C-applicable check run; RS64_DIV32). Bounded/gated/masked: GR s7599, GX s7600, BS s7601 (5 diag composers fixed), AZ s7598
  (ROGUESQ_S7598_MASK=0 = old). Fixes landed, default on, =0 restores old: TK ROGUESQ_S7608_TK, UW s7607 (one fix), FR s7605 /
  RA ROGUESQ_S7604_ALLOC (dead-path), XC ROGUESQ_S7597_MODSCAN, FS ROGUESQ_S7596_RM, SV ROGUESQ_S7595_DIRS, SG ROGUESQ_S7594_SIG,
  EX ROGUESQ_S7593_MAINQUIT / _UQ_EXIT, MR ROGUESQ_S7591_HOSTPORT, HR-2 ROGUESQ_S7590_THRPORT, OW ROGUESQ_MTL_OWN, LK leaks
  ROGUESQ_MTL_WAITPOOL (s7585) + dispatch_data (s7586), LU s7580. **Hazard (s7616): never LAUNCH the game under lldb** (it tried
  to delete the ROM; EPERM saved it); attach to a normally started pid. New build dirs need a COPY of build/saves.
- **s7535-s7576 (classes GA-GR, regen health 19b, compensation chains 19c/19d, S6892, GUARD-6, do_break, float->int): ALL CLOSED.**
  Full text verbatim in PROJECT-OVERVIEW "(s7581 maintenance)". Landed defaults: RS64_DIV32/DIVU32 (s7575), RS64_TRUNC_W_S/D (s7576),
  tools/rs64_anchor.py regen fix (s7558), regen_replay "ok" (s7560). Opt-in fixes: ROGUESQ_SP_LATE=1 (GA s7535-s7537),
  ROGUESQ_RDP_NODRAIN=3 (GB s7540; OWNER-OPT-INS row). Owner decisions from them: M5_B40_VALUE (s7558/s7564), SP_LATE. Censuses
  docs/COMPENSATION-CHAINS.md (122 rows, 0 UNKNOWN) and docs/DEFAULT-ON-LEVERS.md (s7557). No default flipped.
- **G3 render fidelity: H-equal everywhere scored (s7122-s7217).** RT64 == angrylion to the retail floor at
  4:3, 16:9, 21:9, fullscreen 16:9 and ASPECT=auto fullscreen, flight L0-L18, menus, cutscenes, front end,
  LEVEL DESCRIPTION. Only large residuals: the deliberate W_SHEET_PX / W_SHEET_POS guard-band sky-sheet culls.
  Default-on fixes from it (=0 old): FBW_ALIGN (s7188), RECT_ASPECT (s7142), HORIZON_XFIX / GATEFIX / SKYFILL
  (s7133-s7136) + SKYFILL_BOT (s7166), W_SHEET_POS (s7130).
- **Draw distance (G1c) at the owner screens.** dd4 is the 4:3 ceiling (docs/DRAW-DISTANCE.md). Wide:
  dd6 auto bundle (off-map cull past 0.6 x fog end, KEDGE 0.8,12, WIDEWIN cap 10240, auto KLEVEL `12:0.5,13:0.5`,
  CAPLEVEL `9:8192` when FB_WIDTH>796) holds ~60 fps on all 19 levels at 21:9 and 16:9. WIDEWIN auto stack
  (R=88 + 2x2 merge 0.4 + E16, main.cpp [s7258], STACK=0 off) at any dd>1 with ROGUESQ_DD_WIDEWIN=1; merge+E16
  carry the cost cut, R=48 only ate the side gain (s7265-s7266). L12 auto RLEVEL `12:48` at dd>=6 (s7287).
  **dd8 auto px8 + R128 (main.cpp [s7293], ROGUESQ_DD_PX8_AUTO=0 off) QUALIFIED at 16:9 (s7295) and 21:9 (s7299):**
  300 s, 0 crash, 60/s on L1/L5/L9/L10/L12; total emitted cells/call L4 16:9 ref 6902 -> 11406. Far plane capped at
  32767 (ROGUESQ_DD_FARMAX, s7310): above it the sky-dome edge clip pins to x=0 (21:9 left sliver).
- **G5e fog (opt-in ROGUESQ_DD_FOG_ALT=1,3,1, s7302-s7307): QUALIFIED at both owner screens.** ke3 at dd8 =
  dd4's fog end; melts the far horizon into haze, near detail kept (16:9 L1 1.3/2.4/2.7%, L4 1.5/6.5/4.0% texture
  removed far/near/side); weaker at 21:9 (L1 null in all bands, lever ctl 8/27/17% PASS, s7306); untouched on
  L10 (cloud). Holds: 16:9 L1/L5/L10 300 s (s7304) and **21:9 L1/L5 300 s (s7307 fold: 0 crash, 60/s, beyond-route
  3/1 s, ctl flat-30 176 s PASS)**. Cheaper per frame in both: same-soak L1 heaviest20 12.57 -> 9.69 ms (16:9),
  13.53 -> 9.40 ms (21:9). Default unchanged; owner judges the look (docs/OWNER-OPT-INS.md, sheets s7303/s7305/s7306, same-pose dd6/dd8/fog s7308).
- **G5c freezes CLOSED (s7272-s7285):** 0 flight image holds >= 250 ms on quiet host, windowed, fullscreen, 900 s
  L4/L12; every hold is a black death/restart or cutscene transition; off-window gaps are fb-relocation scene
  changes (s7284). Background CPU load IS a real freeze source and ROGUESQ_QOS_ALL=1 removes it (s7277-s7281;
  minimal set GUEST_QOS+PRESENT_QOS); GPU contention slows evenly, no freezes, CPU QoS cannot help (s7282-s7283).
  Transition stalls = retail 3072-sample MusyX wait ~139 ms (s7065, s7285). **Owner: QOS_ALL default?**
- **Retina (s7203-s7224): opt-in ROGUESQ_RETINA=1 CLOSED in every scenario** (flight, front end, windowed 21:9,
  live resize, hot-plug): H-free (GPU +0.05-0.4 ms, 0 gaps), H-sharp (HUD crops 0.42-0.57 -> 0.73-0.82).
  **Owner: RETINA default?** Sheets docs/owner_sheet_s7205_retina.png, s7220, s7223, s7224.
- **Host hazards fixed, default on (=0 old):** guard-refused mq drop (s7194) and park (s7195); PI DMA to unknown
  region posts completion (s7196); AI drain post when SDL stops pulling (s7197, AI_STALL_POST_MS); AI backlog
  trim 150 ms (s7198, AI_BACKLOG_MS); audio output hot-plug (s7199, AUDIO_HOTPLUG; default-route needs nothing
  s7200); pad hot-plug (s7201, PAD_HOTPLUG); display hot-plug (s7202, DISPLAY_HOTPLUG; own-display gate s7222,
  HOTPLUG_ANY=1 old). Censuses CLOSED: docs/COOP-SCHED-POLL-CENSUS.md, docs/HOST-COMPLETION-CENSUS.md.
- **Presentation fixes, default on (lib/rt64):** interlaced still address VI_ILACE_ADDR / PE_STALEFIX (s7206),
  4:3 double present PE_DEDUPE (s7208), present box shape PRESENT_SHAPEFIX (s7213). Elite Rogues field screen
  presents progressive (RT64 ignores the scissor field bit; design difference, s7209/s7210).
- **Window/aspect (G1f) CLOSED:** auto follows the display at boot, live resize gives bars (FB_WIDTH lives in
  statics, s7225); ROGUESQ_WIN_DISPLAY=<n>|mouse drives auto/notch/fit/placement on a secondary (s7226);
  F11 and target-display removal OK (s7227/s7228). In-flight flat-30 in harness runs is the diag ucode path
  (LOG_PHASE -> G1E_PROBES); the coverage harness defaults OWNER_TIMING=1 (s7229).
- **Boot freeze (1 in ~65, s6993) stays PASSIVE:** [stall-dump] prints [stall-wait] + [stall-cf0]; H-cycle refuted
  (s7193); 0 in 100+ owner-env boots since. Hunter `env HUNT_OWNER=1 HUNT_CONTROL=1 zsh tools/boot_freeze_hunt.sh <out> N 34 12`.
- **dd8 21:9 hangar-route mission-load crash FIXED (s7326, default on):** spill blocks never saw the retail scene-change bulk free
  (coalesceFreeHeapBlocks frees every non-0x80 persistent block), so loadLevelAssets' 0x2DFF00 outlived the reset, the 4 MB spill
  arena filled, rs_malloc NULL, SIGBUS in grid-cell terrain code. rs64_s7326_spill_reset releases a1&0x84==0 spill blocks at the reset
  (ROGUESQ_SPILL_RESET=0 old) + 8 MB arena 0x81000000-0x81800000, RAMTOP 24 (ROGUESQ_SPILL_MB=4 old). Same-build arms: release-only
  and arena-only both crash, both together 650 s / 2 mission cycles clean; heap_np_kept=0 at every sync (retail semantics).
- **Spill reads by the RSP FIXED (s7327, default on):** the RSP DMA masked DRAM_ADDR to 24 bits, so gfx ucode reads of terrain grid
  data in a spill block (dd>=6 hangar route) fetched the 0x80xxxxxx alias. 25-bit mask in rsp.hpp, ROGUESQ_RSP_DMA25=0 old (item 17).
  **Visible (s7328):** with the grid buffer forced into spill (new lever ROGUESQ_SPILL_FORCE=min:0x200000) on posed L1 dd8 16:9, the
  old mask draws near terrain as rainbow garbage polygons (37.8% of pixels at one freeze); the fix is pixel-identical to the no-spill
  layout. Sheet docs/owner_sheet_s7328_dma25.jpg.
- **L15 21:9 dd4 crash FIXED (s6992):** 7-site `(p & 0xFF000000) == 0x80000000` test vs the 0x81000000 spill arena;
  tools/apply_s6993_ptrmask.py, ROGUESQ_PTRMASK=0 retail.
- **G1e:** 60 fps in flight on all levels (s6996; use fl_shown). Defaults VI_RT, STDERR_ASYNC, G1E_CELLIDX;
  opt-ins VI_LOCK=1, QOS_ALL=1.
- **Wide/aspect fixes default on:** G1D_SHOWROOM, G1D_340PERSP, G1D_INTROSHAPE / W640 / SCISSOR_TOL, notch safe
  area + VPW_SCALE, WIDE_LOGQUIET, WIDE_UNDRAWN (s6924-s6932).
- **Opt-ins, owner's choice (default off):** VI_SHAPE (owner: stays opt-in), DD_MELT, DD_SKYZ, DD_CUT_LIVE,
  HANGAR_FOV, G5G_LENS, NEARLIFT (near-wall flicker is retail, s7109; k1.6 removes it), WIDEWIN cap 12288,
  RETINA, QOS_ALL, DD_FOG_ALT. Owner ran MELT, SKYZ, VI_LOCK, QOS_ALL and reported nothing wrong (2026-11-08).
- Save guard: runner.sh exports ROGUESQ_NO_SAVE_WRITE=1 and snapshots build/saves to
  ~/Documents/RS64-save-backups/auto. Never touch the owner's save (profile "ASS").

## Closed work, summarised

Detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6900 / s6994 / s7187 / s7262 / s7307)".
- **G3 retail match** (angrylion oracle): boot, attract, hangar, crawl, intro, missions 1-19, front end at RDP
  level, AT THE MOVIES 81/81 (s6784-s6792); presented-frame matrix s7122-s7217.
- **Default-on fixes from that sweep:** UCODE_CAP 65536 (dd>1 1048576), MENU_WORKER_FIFO, EXACT_EDGES, exact-ns
  VI deadline, LLE_FORCE/UNGATED/SOLO, audio_device_mutex.
- **G1e rate:** s6696 getenv, -O2, RSP work s6713-s6775, FPS60 classes s6828-s6831 (docs/FPS60-FIXES.md).
- **G1, G1c, G1d, G1f, G3c, M5, M3, M6, G2, renaming (s6868, misnomers s7072-s7080): closed.** G1(d) objectives
  and G4 crash hunting parked by owner.
- **Engineering s7066-s7098:** cached getenv (ENV_CACHE), dladdr cache, diag call-site gates, N64Recomp
  self-branch miscompile (tools/fixup_selfbranch.py), lowering / host-shim / fixup / RSP censuses, DPC bridge
  forwards exactly the hardware RDP stream (s7096), big G5b drops are already in the RDP stream (s7098).
- **WIDEWIN thread s7231-s7271 CLOSED:** cost (H-tiny far side cells), auto stack, side-edge gain at 21:9 kept at
  R=88, 16:9 side gain below run noise (H-noise s7269), stack invisible in cutscenes at both aspects (s7270/s7271).
- **Wide + dd span class (s6879-s6885)**, width class (docs/G1D-WIDTH-CENSUS.md), spill arena (s6858) + heap audit
  (docs/HEAP-ADDR-AUDIT.md; missed the s6992 mask class).
- **Regen (s6863-s6881):** replay from pristine compiles/links/boots; live tree NOT regenerated (docs/REGEN-VERIFY.md).
- **Present thread (s6884-s6891, s6931):** SCREEN_JOB, PRESENT_INFLIGHT, PRESENT_DRAIN opt-in/off.

## Superseded conclusions — do not act on these
- **s7645/s7646 "gfx tasks read display-list bytes that PI DMAs refill mid-task at dd>1 (L4 4912/120 s); H-slot-recycle" (superseded
  s7647).** Believable: controls fired, dd1 arm read 0, and the issuer/ROM offsets were coherent. But both sides were keyed `& 0x7FFFFF`
  while the RSP addresses 32 MB and dd>1 data lives above 8 MB: true-key overlap 0, alias-only overlap 4881 in the same run.
- **s7552 "pre-mission out-of-rect colour change is real content (a darkening fade)" (superseded s7553).** Believable: samples
  0x294B->0x2109 failed RT64's requant test F(pre,d). But F only models upward dither from pre; the source is the retained float.
  s7553 shadow: pre == RT64's own last writeback for 100% of those px, post within ±1, dark/bright balanced, outside every draw.
- **s4711 "retail never runs reapplyAudioConfig/reapplyDisplayMode at boot/attract" (superseded s7476).** Believable because the oracle
  ran 120 s with 0 hits; but it ran with dummy video, which never leaves the 320 boot phase. With Rice + Start presses retail calls
  reapplyDisplayMode on every scene (t=2.1/6.7/17.3/38.4 s). The count=1 re-init was the port's s4889 patch clobbering $a1.
Recent only; older entries in the PROJECT-OVERVIEW maintenance archives (s7307, s6994, s6900, s6870, s6759).
- s7418 "32 live cache ops". Believable: RecompiledFuncs census with a passing liveness control. s7419: its liveness keyed on objdump
  names, so 147 renamed functions were `nofn`; one live CDE (clearMemory16ByteBlocks 0x8000041C, boot) was skipped -> 33, still safe.
- "0 live cache ops" (s7405 class BO). Believable because the census ran with a control that passed (Status/Count/Compare rows),
  but that control never exercised `cache`: mips64-elf-objdump prints cache as .word, so the row could not fire. s7418 on
  RecompiledFuncs: 32 live (CDE 0x0D + HWB-D 0x19 only), no-op-safe. Class BO's FR/RM/FS conclusions stand.
- "FCSR.FS vs host FZ: known and left, ROGUESQ_FTZ stays opt-in" (s6013/s7087). Believable because the s6012 lvl1 holds
  were clean in both arms; but no instrument ever asked whether denormals occur. s7405 FPSR witness: they do (game thread, in
  flight), so FTZ is now default on (=0 old).
- s7376 "the present thread already takes workloadMutex at line ~676 in the same frame" (used in its deadlock/coverage reasoning).
  Believable: upstream locks it there. s7377 counter: that lock sits on the `!interpolationEnabled` branch, taken on 27/10800 presents;
  the other 99.7% ran lock-free (fixed by ROGUESQ_S7377_EARLYLOCK).
- s7372 "17 AQ rows exercised in mission incl. dpc defer_begin and rs64_s6094_tick; 73 never executed". Believable: coverage
  counts are exact. s7373: the s7366 rows' line numbers predated s7368/s7371 edits (20/97 lines no longer named the container);
  re-cut rows give 19 mission rows (defer_begin and s6094_tick out, both env-gated; get, s6702_release_locked, heapsync in), 71 unexecuted.
- s7193 "boot-freeze second wait unknown, not reproducible by forcing" -> s7367: it is MAIN IN 0x8011A818 (scheduler chain), reached when MAIN (not retrace) is starved; s7193 forced retrace holds, which let MAIN return to CF0.
- s7325 "46 audio reads land in song-channel arrays freed by waitForMusyXAudioTaskDone (via musyxNoopStub) or the scene sync". Believable:
  allocator frames said allocateSongChannelArray. s7330: the blocks are the synth's command-list buffers, and the boot hits come from
  tasks built AFTER the scene bulk free (no wait involved); only 1 in-flight case belongs to the wait path.
- s7324 "class G CLOSED, H-cpu-only: the RCP is never handed a spill address". Believable: 462M DMAs at dd8 21:9 L4, 0 direct, ctl
  198/198. It ran the forced-level route, where loadLevelAssets' 0x2DFF00 sits in the main heap; on the hangar route (s7327, dd8 16:9)
  the reset/reload puts it in spill and the gfx ucode DMAs its grid-layer data at 0x81xxxxxx (fixed: 25-bit DMA mask).
- s7324 "40k audio RSP reads hit heap GAPS / freed blocks (no live rs_malloc block)". Believable: the s7317 map recorded every hooked
  malloc/free. s7325: the retail scene reset frees in bulk without rs_free, the map kept 531 stale entries shadowing live blocks;
  the guest heap walk puts every address inside an allocated block, dd1 identical. Re-synced map: 46 residual reads.
- s7316 "spill live in the dd2 16:9 L1 run; 80-87 heap words held spill pointers". Believable: the words were aligned 0x81xxxxxx in
  heap. s7317 allocation map: all 833 spill blocks are freed in the load window; those words are halfword data and dead stack slots.
- s7312 "the presented window can lag the RDP stream for seconds (first run after a rebuild)". Believable: same pose, same stream,
  two captures 0.7 s apart both wrong. s7313: a voided batch-1 L5 game was still alive and the pose script captured the oldest game
  (`pgrep|head -1`); the repro arm with a one-game guard matched 6/6 (diff 0.01 vs 92.8 control).
- Pre-s7300 superseded entries (s6445-s7288, 27 lines) moved verbatim to PROJECT-OVERVIEW "(s7581 maintenance)"; grep there.
## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Disk ~20 GB free: a 960x540 g5b_capture is ~9 GB/min. Keep captures <= 90 s, delete raws after scoring.
- Arms: tools/g1e_owner_quiet_arms.zsh (per-level owner fps; sets FORCE_UNLOCK, check `cur`); G5 template
  `scratch/s6899/arm.zsh`; scenes `scratch/s6908/arm.zsh`; hangar `scratch/s6907/arm.zsh` + tools/g5g_pan_score.py;
  fog/edge sheets tools/s7306_fog_219.zsh, tools/s7263_widewin_edge_arms.zsh (SHEET=1), tools/s7268_edge_delta.py;
  image holds tools/s7272_g5c_hold_arm.zsh + s7272_image_hold.py; toggle load tools/s7277_toggle_load_arm.zsh.
- dd4 needs no DD_UNSAFE; higher uses DD_UNSAFE (clamp 8). Confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. L10 is cloud with no terrain grid: never use it for terrain
  measures. Wide soaks need `MISSION_WIDTH=796|1024` + `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`. 16:9 autopilot
  gates wait on VI width 1592, not 1024 (s7271).
- Pose control (s7308: PIN=1 repeat arms are pixel-identical at a freeze, so cross-run arm diffs are exact there; score with
  tools/s7308_pose_horizon.py): `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_FREEZE=<x,...>:<ms>` (needs RAND_TRACE + DEBUG_WRITE;
  tools/g3_optin_pose_arms.sh). Port dt pin `ROGUESQ_XTRACE_POKE=800FA730:29:30:3d088889`.
- Timing: any ROGUESQ_LOG_* turns FAST off and PROBES on: set `ROGUESQ_G1E_FAST=1 ROGUESQ_G1E_PROBES=0`, or
  OWNER_TIMING=1 in the harness. Per-frame meter `[g1b]` (sd_wall, tasks/s). Measure on AC power (battery x1.4).
- Present rings (ROGUESQ_PRESENT_RING): tools/g1e_present_cadence.py first; at=0 throughout is not a measurement.
- g5b_capture is sRGB since s7151; raws before s7151 are Display-P3 (FID_P3=1).
- Freezes: stalls = [g1b] sd_wall max; image freezes = tools/g5c_frozen_runs.py / s7272_image_hold.py;
  `sample <pid> <s> <ms>` costs no build.
- AT THE MOVIES shots by run time (dd1 16:9): 76 887-912, 77 912-924, 78 924-942, 79 942-952 s.
- Frame comparison: score menus by RDP (tools/g3_rdp_frame_match.py, tools/g3_menu_pair.sh). G3 kit: arms
  tools/s7125_arm.zsh, s7131_arm.zsh, s7141_{arm,post}.zsh, s7146_arm.zsh, post s7152_post.zsh; scorers
  tools/s7122_fidelity.py (FID_ALROWS=444/336: RT64 shows rows 0-443 / 0-335), s7183_native_edge.py,
  s7210_regfit.py (run first at 16:9); replay tools/angrylion_replay/build16.sh. L17 autopilot dies ~126 s.
- Oracle missions: tools/g3_eep_patch.py sets +0x31; use --save-dir, never swap a save over the user .eep.
- Slow builds (TSan/ASan): `ROGUESQ_AUTOPILOT_CLOCK=frames ROGUESQ_AUTOPILOT_FPS=58` (FPS60) keys autopilot to fullsyncs,
  but front-end screens are VI-timed, so the route still diverges at TSan speed; gate with `<s>:w<width>` events (s7371).
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` / `crashlines`, never rc (since s7456 the loop's line carries `arms= alive=a/k crash_arms= stall_arms= fatal=`; arms=0 = recipe printed no summary). Recipes that
  drive the window carry `# SOAK_NEEDS_IDLE=<secs>`; zsh recipes run under their shebang shell (s7287).
- Knob tables: PROJECT-OVERVIEW "G1c draw-distance knob and recipe reference"; docs/DRAW-DISTANCE.md;
  owner commands docs/OWNER-OPT-INS.md.

## G1 mission coverage

Playable levels 0..18 (`NUM_LEVELS=0x13`); 19/20 are sentinels. All have route, 300 s holds and framebuffer
presence; level 1 has a retail flight match; objective response (d) parked by owner. See
docs/G1-FRAMEBUFFER-COVERAGE.md and docs/G1-OBJECTIVE-RESPONSE.md. Never send hull damage on level 8.

## Durable constraints
- Never end a turn to wait on a run: foreground (timeout <= 600 s) or queue a soak.
- Retail defaults stay unless the owner chooses; never make an opt-in default from a single source.
- Crash-free holds do not mean "renders correctly" (s6468). No mitigation without naming the writer; dd>1 fixes
  live in `tools/apply_s6*.py` (registered in RS64_REPLAY only, docs/REGEN-VERIFY.md).
- The RSP DMA keeps bit 24 (s7327, phys < 32 MB); RDP image addresses and the game's own 24-bit rebuilds (class D) still drop it, so
  textures / colour images / DL-pool refs must stay below 0x81000000.
- Any guest pointer the game range-tests must sit where its test accepts it: 0x81000000+ fails
  `(p & 0xFF000000) == 0x80000000` unless ROGUESQ_PTRMASK (s6992). Re-check for any new arena.
- Never reset, clean, checkout or update submodules; after editing `lib/` run `./submodule-patches/export.sh` and commit.
- Controls: get_n64_input is the pre-6ed036b97 mapping; no changes without an owner request.
- Title plume si_addr=0x58 CLOSED s7660 (0/76 boots); reopen only if `[plume-null-color-attachment]` prints.
- Public forks (owner, 2026-11-18): loop.sh runs `tools/agent/publish_forks.sh` between iterations; it pushes `autonomy` to
  fyreatwill/RogueSquadron64Recomp (fast-forward only) and mirrors N64Recomp tool source + decomp tracked files to their `rs64`
  forks. Never commit ROM-derived data (*.z64, ucode/RDRAM dumps, RecompiledFuncs) or files > 50 MB, and never rewrite history,
  or publishing stops (`scratch/agent/PUBLISH-BLOCKED.md`). `tools/build-from-scratch.sh` is the public build; keep it working.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams. Positive control for every null; two
  independent lines before a conclusion enters this file.

## Next steps (single monotonic backlog)

- **Ladder item 4 REVISIT has no open target (s7638):** the rename sweep is CLOSED (item 19), the M4 accumulator boundary is
  CLOSED (s5354: cxd4 LLE retail shows the same transient 0x8000 lanes in every hangar task, docs/REVISIT-S5354-M4-RETAIL-PCS.md)
  and the external retail-entry boundary is CLOSED route-absent (s4845). Do not schedule a revisit; take an owner item or G-rung.

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7534 into one sequence 1-18, s7622 folded 19-46 into 19 (1-21 now) (the s7533 numbering 1-22 is archived
verbatim in PROJECT-OVERVIEW "(s7534 maintenance)").

1. **Audit classes CC-FZ s7420-s7533: ALL CLOSED** (full text, numbers, controls, tool flags: PROJECT-OVERVIEW
   "(s7452 maintenance)" for CC-DH, "(s7488)/(s7491 migration)" for DG-EO, "(s7534 maintenance)" for the rest incl.
   FD-FZ). Last fold: s7533_fz_levels score 0 (L1 dd8 21:9, L7/L10/L12 dd4, 4/4 alive) -> FZ CLOSED 6 levels.
2. **G5e fog: owner look.** ROGUESQ_DD_FOG_ALT=1,3,1 qualified at 16:9 and 21:9 (headline). Only if the owner asks for
   more haze at 21:9: sweep ke 2 / 2.5 with `tools/s7306_fog_219.zsh l1k2:1:1,2,1`.
3. **21:9 dd>1 left-edge sliver FIXED (s7310, ROGUESQ_DD_FARMAX default 32767, 0 = old), qualified s7312: owner look.**
   Far above ~36-40k units makes the F5 clip pin sky-dome edge panels to fb x=0 (two lines: RDP W decode + presented
   left-column count, 12 same-pose arms; mechanism single-source). Sheets docs/owner_sheet_s7310_farmax.jpg,
   s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
4. **Owner decisions on defaults:** M5_B40_VALUE (s7558/s7564: default 0 is alive only via the s4889+s7476 compensations; =1 is retail and equally clean 6/6), RETINA=1, QOS_ALL=1, S7524_V2P=1 (s7526), SP_LATE=1 (s7537), DD_FOG_ALT, dd8 bundle, RENDER_TO_RAM=0 (s7385). Never flip without the owner.
   QOS_ALL evidence: s7277-s7281 (load freezes removed) + s7382 (the threads it raises are exactly the hot ones, DEFAULT otherwise).
5. **G5i hangar re-entry (s6995), G5a Gerrard V crash (s6893; s6998 writeback audit clean), G5b terrain drops
   (FWDWIN far-loss fix, tools/g5b_fwdwin_seamless.py), G5d logo (s6903), G5f knife lines (s6906; sheets
   s7005/s7006), G5g hangar lens (s6907), G5h cutscene background (s6908-s6919): owner flight / look.**
6. **L15 21:9: owner re-flight after s6992 PTRMASK.**
7. **G1d close-out: owner judgement** (scratch/s6731/sheet_menus_owner.png); owner scope: why L7/L16/L17
   autopilot holds cycle the backdrop menu.
8. **Near-wall NEARLIFT, G3 21:9 holes (s7132-s7140), L4 cutscene SKYFILL_BOT (s7166): owner look.**
9. **Owner judgement / parked:** FPS60 feel, G3c sheets, native hangar geometry, rare dd4/dd8 gfx SIGBUS
   (single-source). Reopen on an owner report or side-effect failure.
10. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first.
11. **RENDER_TO_RAM=0 CLOSED s7389: ready for the owner (OWNER-OPT-INS), default stays on.** Saves ~2.5 ms/gfx task in
    mission (s7385); abort-cut stale-upload stripe fixed (s7387, ROGUESQ_R2R_CPUUP=1 old); soaks L1/L4/L12 300 s pass (s7389);
    fb-cpu-reader census CLOSED s7391 (0 guest loads from a live colour image on 6 levels; build_fbld, ROGUESQ_S7389_FBLD=1).
    Not covered: RSP/RDP DMA reads (RT64 fb-as-texture owns those).
12. **Rerun-after-change censuses (all CLOSED, 0 defects; tool list verbatim in PROJECT-OVERVIEW "(s7534 maintenance)"):**
    after a regen run tools/s7610_ov_census.py --controls + tools/scan_selfbranch.py + the s7407-s7419 emission tools with --controls (rc 0); after a ucode regen tools/ucode_regen.sh verify
    + tools/s7507_rsp_ctrl_flow.py + s7508_rsp_scalar_gaps.py + s7509_rsp_vec_operands.py; after a save/files.cpp edit tools/s7595_sv_census.py --controls + --harness; after a librecomp/ultramodern
    replacement change tools/s7527_host_replace_audit.py --controls; after any new host writer into guest RAM tools/s7542_gc_census.py; after a src/main static/hook change tools/s7548_gh_census.py; after a threads.cpp/recomp.cpp thread-entry edit tools/s7606_hc_census.py --controls; after a new host queue / std::thread / pending-list tools/s7615_dq_census.py --controls; after a fixup/apply script edit tools/s7549_gi_census.py --controls; after an RT64 fullSync/framebuffer-manager edit tools/s7550_gj_census.py --controls; after a librecomp/ultramodern getter or a new os*_recomp import tools/s7555_go_census.py --controls; after a scheduler/replacement or injected-yield change tools/s7543_gd_census.py --controls and tools/s7546_gf_census.py --controls; after a new host-retained guest pointer (osSetEventMesg-style registration) tools/s7547_gg_census.py --controls; after a class-touched function change, its class scorer.
13. **Closed, reopen only on an owner report:** transition stalls (s7065/s7285), host self-time (s7066-s7070),
    misnomer rename (s7080; tools/apply_symbol_renames.py), G1e residual (s6996), G5c freezes (s7285), GPU
    contention (s7283), WIDEWIN thread (s7271), Retina (s7224), window/aspect G1f (s7228).
14. **Harness discipline (CLOSED s7313-s7314, s7332):** iteration tools take the pid from tools/rs64_game_pid.zsh;
    loop.sh SIGKILLs any game alive around each soak recipe and names it in SOAK-RESULTS (a kill line = that run's
    frame times are contaminated). Soak recipes take the analyser's own rc (`${pipestatus[1]}`), never a grep's.
15. **Idiom-class audits s7315-s7416 (AQ-BZ) and their runtime soak folds: ALL CLOSED/PASSED** (archives: s7370, s7417,
    s7534 maintenance). No class soak is outstanding.
16. **Default-on fixes from the audits (=0 / old value restores the previous behaviour):** full list verbatim in
    PROJECT-OVERVIEW "(s7534 maintenance)" (SPILL_RESET, RSP_DMA25, S7334-S7364, CF0_DUPDROP, DLPOOLX_ARM_REBUILD, S7376-S7405
    locks/fixes, FTZ, STICK_GATE s7513, S7528_EVICT, the s7533 FPS60 clamp byte CAS).
17. **Classes GA-GR + 19b/19c/19d + S6892/GUARD-6 + do_break/float->int (s7535-s7576): ALL CLOSED** (verbatim in
    PROJECT-OVERVIEW "(s7581 maintenance)"). SP_LATE AC repeat DONE s7637: L12 dd4 ABBA x2 on AC holds 60.0 gen/s in both settings
    (8/8 alive, scratch/s7637_splate_ac), so it costs nothing on AC; the battery-only CPU-bound case stays unresolved and does not matter to the owner. Regen trees: tools/regen_front.sh D/pristine; cp -R D/pristine D/replay;
    tools/regen_replay.sh D/replay; tools/regen_verify.sh D/replay D/verify.
18. **After-regen UB gates (all CLOSED, rc 0 expected):** tools/s7575_ir_calls.sh + `tools/s7575_break_census.py --controls --ir D`
    (BLIND=0); `python3 tools/s7576_trunc_census.py --controls` (FOLDED=0); after a ucode regen or rsp*.hpp edit
    `tools/s7577_ubsan_sites.py <tu> --check` per ucode TU (UNCLASSIFIED 0) + `tools/s7577_ucode_ub_census.py scratch/s7577`;
    tools/s7580_lui_identity.py (0 object diffs). UBSan builds: `env SAN=<checks> B=<dir> zsh tools/build_ubsanc.sh`, scorer
    tools/s7579_bounds_report.py, plants ROGUESQ_S7578_PLANT=1-6,u (SANREC for non-recoverable checks). s7578 null/wrapv, s7579 bounds, s7580 shift/align, s7582
    pointer-overflow, s7583 div0/fcast/bool/builtin/vla/nonnull/unreachable CLOSED: every C-applicable UBSan check has run.
19. **Rerun-after-change censuses s7579-s7616 (all CLOSED; per-class trigger text verbatim in PROJECT-OVERVIEW
    "(s7622 maintenance)").** Each `python3 tools/s76NN_<cls>_census.py --controls` must exit 0 after an edit in its scope:
    RQ/DQ s7616/s7615 (lib/rt64 RDRAM reads, new threads; a worker-thread RDRAM reader needs a command-time copy or a gate),
    HM/HP s7614/s7613 (--ast; statics), RG/SN/MK s7612/s7611/s7609 (--witness; regen, statics), OV s7610 (regen, overlays.cpp),
    TK s7608, UW s7607 (throw/catch, blocking calls), HC s7606 (threads.cpp/recomp.cpp), FR/RA/RX s7605/s7604/s7603 (host code
    touching guest regs/FPRs), TP s7602 (TO_PTR views), BS s7601, GX s7600, GR s7599, AZ s7598 (allocations, createTexture),
    XC s7597 (throw/json parse), FS/SV/SG s7596/s7595/s7594, EX/TH s7593/s7592, MR s7591 (lib/ edits). OW/OW-2/LK/HR
    s7585-s7589 tools as named in the archive. Renaming sweep closed (s6868). ROGUESQ_MTL_WAITPOOL default on.
20. **G6 (owner 2026-11-18, ahead of everything else): G6a rumble LANDED s7617; G6b controls LANDED s7618-s7620 (table
    src/main/rs64_bindings.h == old map, ROGUESQ_BIND_OLD=1; controls.json beside the exe, rs64_bindings_json.h; F6 panel
    src/main/rs64_controls_panel.cpp + rs64_imgui_metal.mm, ROGUESQ_CONTROLS_PANEL=0 removes it). Both close on the owner's
    hands. Rerun `ROGUESQ_BIND_PANEL_TEST=1` (scratch/s7620/run.zsh) + tools/test_bindings.cpp after any input-path edit. s7666: Save -> controls.json -> reload
    round trip PASS (scratch/s7666/run.zsh: save, load mismatches on N64 A only, default-path guard and corrupt-file controls). s7669/s7671 rumble abort route clean (live effect at pause/abort stopped by the game in 25 ms): rerun scratch/s7669/run.zsh <name> "ROGUESQ_S7671_FX_ON_KEY=1 ROGUESQ_S7671_FX_TRAIN_MS=3000" + scratch/s7671/score.py after a rumble/input edit.
    G6c stand-ins: design docs/G6C-STANDINS-PLAN.md (s7621): H-portable (game-side visibility bucket only, no HLE state),
    all 17 upstream code addresses identical in our syms. Step 2 LANDED s7623: src/main/rs64_standins.cpp +
    tools/apply_s7623_standins.py (RS64_REPLAY), ROGUESQ_STANDINS=1|tog (+_LOG=1), dd>1 only; region 0x81700000..0x81800000
    (spill capped 7 MB; matrices reach the DL pool via a stack copy, so CPU-only). L1: 47 objects, submits > 0 at dd2/dd4,
    0 at dd1, 3/3 arms alive 0 stall (single run, on battery). **Step 3 (s7624): H-culled.** The game's own view test
    (transformVec3ToNpcLocalWithScale 0x8001DC34, inside addNpcToVisibilityBucket, which returns 1 only when linked; the bucket is
    a linked list with no cap, so H-budget-at-bucket is refuted by code read) accepts 0.2% of stand-in submits (L1 93/40018,
    L4 361/151825); only 2/9 (L1) and 10/59 (L4) later spawns were ever accepted before spawning (0.5-4.2 s early). Per-frame
    toggle fb dumps: flicker per triplet toggling <= forced-off control (L1 3879 vs 4351, L4 1807 vs 2207), synthetic control
    PASS. The s7621 "no far_check port needed" was wrong: upstream widens that test's far ($f0 *= dd, 0x8001E078) and its
    +-125 camera box (0x8001DCEC/0x8001DD38, constants 0x8000093C/940) and relies on RT64 HLE far matrices for translations past
    convertMat3x4ToN64Mtx's reach; we have neither. **Step 3b (s7625): H-far selected, fixed at the bucket; the draw path culls next.**
    Exit tally (tools/apply_s7625_viewtest_reason.py; exits sum to calls): in-front stand-ins die at the far exit 0x8001DDA8
    (view+0x28 = 30.8 L1 / 27.8 L4 at dd4 = the retail object far; stand-ins sit at d 40-110), then side; box +-125 rejects
    ~3%. Fix tools/apply_s7625_standins_far.py: far *= ROGUESQ_STANDINS_FAR (default dd; =1 retail, =tog) for OUR call only;
    the box test runs first so no matrix overflow is possible. Same-run tog: pass rate L1 0.41% -> 29.6%, L4 0.47% -> 24.2%,
    far rejects 9021 -> 0 / 27996 -> 27, 4/4 arms alive 0 stall. But fb flicker with far on still shows nothing (L1 4068 vs
    4206 off, L4 1813 vs 2129, control PASS, 294/255 accepted in window 1). **Step 3c (s7626) supersedes "accepted stand-ins
    are not drawn": that window had no stimulus.** Stand-ins never use selectMeshLodAndSubmitForRender (probe droids only), so
    upstream's 0x80058264/0x80058304 hooks do not apply. tools/apply_s7626_sg_probe.py (ROGUESQ_STANDINS_LOG=1, other nodes as
    control): traverseSceneGraphRecursive visits/converts them (L1 81591 in 130 s, cam z 42-121, packed t < 2^31); their meshes
    are prebuilt-DL (flags 0x00100018, same as most real objects) and queue mesh+0x34 at 0x80116400; beginFrameDLChunk reads
    100% of those entries (65390/65390). The dump windows (40-46 s after first submit) held ~0 stand-in draws (L1 0, L4 ~60/s
    for 2 s); they draw at 9-19 s. **Step 3d (s7627): stand-ins DRAW RDP pixels.** L1 dd4 STANDINS=frame, dumps 10/16 s,
    flicker px/triplet window1 vs forced-off window2: P (PULL=3) 1071 vs 107.5, N (true depth) 547 vs 108, real-object control
    C (ROGUESQ_STANDINS_CTL=1, real nodes collapsed on off calls, ours never added) 180891 vs 107.5; synthetic control PASS all
    arms, 3/3 alive 0 stall. **Step 3 proof by eye (s7628): stand-ins are visible early, true depth, on 2 levels.** Same-run
    adjacent-frame pairs (tools/s7628_standins_sheet.py, docs/owner_sheet_s7628_standins_on_off.jpg): L1 dd2 a far bunker in the
    haze; L4 dd4 a row of far city towers (1949 px) the game has not spawned yet. L4 dd2 shows none (flicker 143 vs 155 forced-off
    = inside the game's own spawn radius, expected). Flicker scorer alone is NOT proof: the s7627 N excess (547) and the s7628
    L1 dd4 top pairs are cliff-texture shimmer + laser bolts, not stand-ins (eye check); keep the eye check. Dumps show each call
    one swap late (stand-ins appear in label-0 frames). Spawns preceded by a stand-in: L1 10-11 (2-62 s early), L4 19 (0.2-5 s).
    4/4 arms alive, 0 fatal, 0 VI stall. **Step 4 (s7629): 300 s holds STANDINS=1 dd4 owner recipe, L0-L5 6/6 clean** (alive, 0
    crash, 0 VI stall, gap <=148 ms, stand-ins active per spawn lines); **s7630: L6-L18 also clean -> 19/19** (gap <=162 ms,
    spawns 13-360 per level). Owner row in OWNER-OPT-INS + sheet docs/owner_sheet_s7630_standins_on_off.jpg (cluster crops). **G6c now
    closes on the owner's look; default stays off.** s7672: handoff blink at spawn fixed (ROGUESQ_S7672_HOLD, headline); rerun scratch/s7672/run.zsh after a stand-in edit. s7674: held culls all off-screen (H-offscreen); s7675: that "ghost" is a live AT-PT walker with a delayed first draw; s7676: GATE (distance-gated draw, stand-in bridges it), ghost thread CLOSED; s7677: L2/L5 folded rc 0 (H-gate 4 levels); item map keyed on rebuild generation. Scorer
    now ranks by clustered diff px (`--cluster 16`, 8x8 blocks): bunker 153 / towers 1298 / shimmer 0 / none 0 median, control PASS;
    a window-2 shimmer map was tried and rejected (does not predict window 1). s7680: near release inert in flight (L5 0 vs control 4). s7681: the shield was not a ghost (own inline draw path, detector now sees it; near release kept as backstop). Then the owner sheet decides.
21. **Classes RP, HD, HB, ST, AT, CF, TS, TS-2, TS-3, TS-4, MK8 + walker fusion + spike cost + closed-gate drift (s7631-s7659):
    ALL CLOSED** (full text, numbers, controls, tools verbatim in PROJECT-OVERVIEW "(s7662 maintenance)"). Defaults that stay
    (=0 / old restores): ROGUESQ_S7634_FUSE=1 (walker fusion), S7639_ST, S7640_AT, S7641_CF, S7643_PI (release/acquire s4211 ring),
    S7632_SNAP; opt-ins/diag: S7636_FASTSPIKE (default 0), S7632_STATS, S7644_RSPDMA(_CTL), S7647_MASK8. Rerun triggers:
    tools/s7639_st_census.py after any SDL call edit or new thread; tools/s7640_at_census.py / s7641_cf_census.py after AppKit or
    framework-callback edits; TSan builds tools/s7642_tsan_rt64_build.sh, s7643_tsan_host_build.sh (lightweightsemaphore tsan
    annotations are TSan-only); the gate sweep after any src/ or lib/ change. A new G above 0x80180000 reads unclassified (RED): re-dump.

22. **s7663 launch settings/presets: owner to try.** After any edit to rs64_settings.cpp rerun tools/test_settings.cpp and
    scratch/s7663/run.zsh (5 arms; C must print `[gfx-qos] mode=1` from the file). New owner recipes go in its presets() table.
23. **s7614_hm census: CLOSED s7673.** rs64_settings.cpp `p.vars` = host (static const preset table of string literals; row
    proof-checked, broken-proof control -> DRIFT). Census exits 0, controls 8/8. Add a row for any new static with pointer members. s7673 also re-greened s7611/s7599/s7352/s7535 (rows for s7663/s7671/s7672 code): run the gate sweep after every src/ commit.
24. **Crash-report gate (s7664):** `python3 tools/crash_reports.py` (rc 1 = NEW). Deliberate crash arms: quote the .ips basename
    in the session entry. Test tools/agent/test_crash_reports_gate.sh. DIAG datum RogueSquadron64Recomp-2026-11-17-053804
    (s7523 SLOWRDP consume() SIGSEGV) CLOSED s7665 as H-devbuild: crash 05:38, file first committed 05:59; both committed versions
    pass an ASan/UBSan fuzz (tools/test_s7523_model.sh, 2 controls) and the post-commit arms ran alive. Rerun that test after any
    s7523_slow_rdp.cpp edit.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7417, s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7579-7622; search bounded windows only.
