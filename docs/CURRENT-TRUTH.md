# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7778 (2026-11-21).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; item-1 classes DG-EO in "(s7491 migration)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)"; s7533 Next-steps items 1,12,15-21 (classes FD-FZ) in "(s7534 maintenance)"; s7535-s7576 headline + items 17-21 + pre-s7300 superseded in "(s7581 maintenance)"; s7579-s7616 headline + items 19-46 in "(s7622 maintenance)"; s7647-s7659 headline + items 21-35 in "(s7662 maintenance)"; s7617-s7702 headline + item 20 (G6) in "(s7703 maintenance)"; s7702-s7743 headline + items 22-32 + s7312-s7418 superseded in "(s7747 maintenance)". Grep there for any sNNNN.

## Headline

**Every engineering goal on the ladder is closed or awaiting the owner's look** (s7779: dangling-global class item 31 closed 7/7; s7780: diag helpers must gate inside their own body, or the class censuses read them as default-on). Nothing is broken at the
owner's recipe as far as any instrument can see; remaining items are owner judgements (list in Next steps).
**Owner: docs/OWNER-REVIEW-QUEUE.md (s7762) is the one-sitting list** (20 items, command + sheets each); every path and setting
name in it and in OWNER-OPT-INS is gated by `python3 tools/s7762_owner_doc_check.py --controls` (in the sweep; rc 0 s7762).
**s7763: every queue command does what its row says** (`python3 tools/s7763_owner_cmd_check.py --control`, launches each of the
11 distinct commands for 12 s, one at a time): 11/11 MATCH on echoed dd/aspect/FPS60/fullscreen/stand-ins plus the row's own switch
echo (NEARLIFT, RETINA swapchain=drawable, QOS_ALL, RENDER_TO_RAM=0, V2P, SP_LATE); env-over-preset control DRAW_DISTANCE=3 echoes 3;
negative controls: the plain tv log scored as tv-with-dd3 flags dd, and scores 0/6 feature echoes.
**s7764: the queue's in-flight toggles work too** (`zsh tools/s7764_inflight_toggles.zsh` -> `tools/s7764_inflight_toggle_check.py`, L1 dd4 21:9
FPS60 autopilot, arms def/off/tog 150 s + B40 pair 70 s, 5/5 alive 0 crash vi_stalls30s=0): 7/7 H-works, each with its own counter as
positive control: RUMBLE=0 vpad_nz 19->0; RUMBLE_SCALE=0.5 vpad hi 24616->12687; W_CLAMP clamped tris 5948 / =0 0 / =tog 0 even 3271 odd;
SKYFILL 5252 / =0 0 / =tog 0 even 2610 odd; DD_FARMAX far cap 32767 / =0 65504; STICK_GATE full-stick counts 85 / =0 127 (new
ROGUESQ_LOG_STICK_GATE=1); M5_B40_VALUE b40-write stores 0x00 / =1 0x01. Swapped-arm negative control fails 6/6 controls.
**s7765: row 2's ROGUESQ_CONTROLS_DUMP=1 / controls.json work at launch** (`python3 tools/s7765_controls_dump_check.py`, 4 launches,
temp files in scratch/s7765, build/controls.json absent and untouched): 12/12 PASS. No file -> `[controls] no ...` and the dump equals
the table parsed independently from the verbatim old code rs64_bind_old_sdl (30 button sources + WASD stick); the dump fed back as a
file loads and re-dumps identically (it IS a ready-made starting file); A->key:Space file changes only A (positive control); a
malformed file is rejected `(not valid JSON)` and dumps the defaults (negative control). Every switch in the queue is now verified;
only the F6 panel's interactive use remains the owner's.

**s7766: input-to-photon latency measured end to end** (`ROGUESQ_S7766_INLAT=1 ROGUESQ_G3C_LOG=1` + present ring ->
`python3 tools/s7766_inlat.py <log> <ring> --ctl`): FPS60 58.3 ms (poll->submit 16.6 + submit->queue 13.6 + queue->photon 28.0),
retail 75-86 ms, FPS60+VI_LOCK=1 53.7 ms; the stick step always shows in the very next gfx task (0 port-added frames, two paths
agree, fake-step ctl 0-1/19). DRAWABLES=2 is not a latency lever (wait moves upstream, p90 75 ms). Largest port-only leg = present->photon.
**s7767: the window mode does not change it.** FPS60+VI_LOCK=1, same run: borderless fullscreen 53.8 ms (queue->photon 23.1), windowed
53.3 (23.1), SDL exclusive fullscreen (new `ROGUESQ_FULLSCREEN=2`) 53.8 (23.0). H-compositor refuted: the ~23 ms leg is vsync phase +
swap, not a CoreAnimation composite pass. This also replicates s7766's VI_LOCK=1 53.7 ms (second run, so two sources).

- **s7702-s7743 regen / census / env-reader engineering: ALL CLOSED, 0 open defects** (every bullet verbatim in PROJECT-OVERVIEW
  "(s7747 maintenance)"). Standing facts from it: the live RecompiledFuncs tree IS the s7739 regen replay, and
  `tools/s7719_regen_gate.py --strict` (in the sweep) byte-compares live vs a fresh replay, so ANY hand edit to
  ../N64Recomp/RecompiledFuncs turns the sweep RED (put it in a fixup/apply script). Ucode: `tools/s7741_ucode_regen_gate.py --controls`;
  after any fixup_factor5_ucode.py edit `zsh tools/ucode_regen.sh snapshot`; the 9 factor5_ucode_ovl*_recompiled.c are splice inputs
  (keep byte-true, s7743). Env readers: launch strips empty ROGUESQ_* (s7730), maps on/off words to 1/0 (s7731), unsets invalid
  ROGUESQ_ASPECT (s7732); after a regen `python3 tools/s7734_compiled_reader_census.py` (rc 0). s7725 plume +0 texture-descriptor
  over-release (RT64 Present SIGTRAP) fixed, NSZombie 0 on boot/flight/hangar route (s7726/s7727). 21:9 fb read-back harmless (s7702-s7706).
  Sweep: `python3 tools/s7651_gate_sweep.py` (--jobs 2) ~216 gates, 0 RED, 0 HOLLOW; s7753 adds an end-to-end ucode RDP-OUTPUT gate (item 26; 21 snaps since s7761 incl. L10 21:9 stand-ins flight, hangar re-entry after abort, PAUSE/ABORT/MISSION FAILED overlays SELECT LEVEL and LEVEL DESCRIPTION, hangar H-state item 27, 6 pairs).
- **G5h cutscene pool floor (s6908) re-held post-G6c (s7696-s7701):** mission intros L1/L4/L5 and the AT THE MOVIES playlist (outro
  proxy) at 16:9 dd2/dd4 and 21:9 dd2 (kept nodes floor vs old cap e.g. 16:9 dd2 1350/831, 21:9 dd2 1605/858); visible where the old
  cap leaves flat ground holes (sheets docs/owner_sheet_s7700_movies_dd2.jpg, s7701_movies_219_dd2.jpg, scratch/s7699/L5d2_sheet.png).
  Stand-ins never run inside intro cutscenes (H-absent, 3/3 levels). At 21:9 FB_DUMP needs ROGUESQ_ALLOW_WILD_W=1 (tools arm it).
- **Post-G6c re-holds (s7692-s7695): clean.** 300 s STANDINS=1 dd4 owner recipe L1/L4/L5/L10/L12/L15 6/6; G5c 900 s freeze gate L4/L12
  (0 gaps >= 250 ms after t=95 s, SIGSTOP control caught); G2b crawl audio fix 2 vs ctl 1037; G5d logo share unchanged.
- **s7744-s7748 G6c coverage L10/L12: stand-ins add AND are visible on both (s7748).** `STANDINS_DUMP=a<adds>:<gap>:<n>` add-anchored windows; score with tools/s7746_ground_flicker.py (sky masked). L10 ground 2334 vs forced-off ctl 375 (6.2x, reproduced s7745/s7748). L12 at the 62 s add peak: 146 vs ctl 36 (4.1x, ctl PASS) + by eye 3-4 extra pylons in the haze on the on-frames only (docs/owner_sheet_s7748_l12_standins.jpg). The s7746 L12 null (131 vs 126) was a noisy forced-off window (camera-motion flicker), not absence: its on-window equals s7748's. H-drop/H-clip/H-size all refuted: L12 adds reach psn ret + dl34; depth 37-124 view units vs effective far ff*4 ~31000 world (~121 view, 1 view unit = 256 world); `[standins-px]` (STANDINS_LOG=1) projected radius median 19 px on L12 (sub 0036 25 px) vs 4.6 px on L10. s7749 closed the coverage question: "85/92 never added" was the [s7690-par] first-120-try window; the `[s7749-life]` lifetime table (tools/s7749_life_tally.py) shows 93/131 L12 stand-ins add over 200 s (79 of the 85 later in the same run), 24 never grid-linked (script-spawned, skip by design), 7 condition-gated, 7 off-screen-culled; v_far=0 everywhere; activation control 27 edges / 0 without spawn (H-ours refuted).
- **G6c stand-ins (ROGUESQ_STANDINS=1, opt-in, dd>1 only): DONE, owner's look.** Design docs/G6C-STANDINS-PLAN.md; code
  src/main/rs64_standins.cpp + tools/apply_s7623_standins.py and follow-ups (RS64_REPLAY). Visible early at true depth on 2 levels,
  19/19 levels 300 s clean (s7629/s7630), sheet docs/owner_sheet_s7691_standins_on_off.jpg. Default-on sub-fixes inside STANDINS (=0 old):
  S7625 far (STANDINS_FAR=dd), S7672_HOLD (no blink at spawn), S7677_GEN, S7679_NEAR=15, S7681_SHIELD, S7684_RSKEY, S7685-S7687_POSSUB,
  S7690_PARITY (frame mode). Ghost thread closed as H-gate (s7676); level changes safe (s7678). Rerun tools/g6c_sub_handler_map.py after
  a stand-in table edit and scratch/s7672/run.zsh after a stand-in code edit.
- **G6a rumble (s7617/s7638/s7671, default ON, ROGUESQ_RUMBLE=0 old, _SCALE 0..2) and G6b controls (s7618-s7620, s7666-s7670; table
  src/main/rs64_bindings.h == old map, controls.json, F6 panel): LANDED, owner's hands.** Rumble abort cannot stick (the game stops the
  motor at PAUSE entry). F6 panel survives mission load, fullscreen toggle and live resize (S7668_ASPECT). After an input-path edit
  rerun `ROGUESQ_BIND_PANEL_TEST=1` scratch/s7620/run.zsh + tools/test_bindings.cpp.
- **Owner launch settings s7663 (`--preset tv|ultrawide|window`, build/settings.txt; env > file > preset; s7667 relative
  ROGUESQ_CONTROLS resolves beside the file): owner to try.** Crash reports gate s7664 (tools/crash_reports.py; NEW outranks all work).
- **s7660/s7661:** title plume si_addr=0x58 CLOSED (0/76 boots); lldb attach works in loop sessions (preflight tools/lldb_attach_check.sh;
  never LAUNCH the game under lldb, s7616).
- **s7647-s7659 (census-gate sweep + classes TS-4/MK8): ALL CLOSED, 0 behaviour defects** (archive "(s7662 maintenance)"). Standing
  check: `python3 tools/s7651_gate_sweep.py` (--jobs 2; cold ~455-530 s, warm ~15 s) -> 135 GREEN (s7716 adds its census), 5 REPORT, 0 RED; stop_gate blocks RED.
  Key reviews by text anchor, never line number. NEEDS-INPUT gates use retained inputs under scratch/s7215, s7316/ram, s7573/retained.
  All s7617-s7702 bullets verbatim in PROJECT-OVERVIEW "(s7703 maintenance)".
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
- **G5c freezes CLOSED (s7272-s7285; re-held s7694 on the post-G6c binary, STANDINS=1 L4/L12 900 s):** 0 flight image holds >= 250 ms on quiet host, windowed, fullscreen, 900 s
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
- s6268/s6868 "no syms-toml placeholder is a real function / the leftovers are shape-only": believable because s6868 audited the
  generated tree and s6268 read objdump, but N64Recomp never emits the libultra exception block and objdump prints it as data.
  Overturned s7770 (ELF byte census, tools/s7770_placeholder_census.py): func_8002BB34 had 14 jal sites and is send_mesg (named).
- s7748/s7690 "L12: 85/92 stand-in items are never added": believable because [s7690-par] reads tries=120 adds=0 per item; it prints once at the first 120 tries, so it is a window, not lifetime (s7749: 79 of 85 added later).
- s7746 "L12 stand-ins are added but NOT visible (H-gain refuted on L12, H-not-visible)": believable because the ground-only
  scorer and its paint control both passed. Overturned s7748: the same on-window flicker (131 vs 146 per triplet) against a quiet
  control (36, not 126) gives 4.1x, and the on-frames show extra pylons by eye; s7746's forced-off window carried camera-motion flicker.
- s7587 "the 2026-11-18-014353 RT64 Present SIGTRAP is an OBJC_DEBUG_MISSING_POOLS instrument artifact": believable because only
  the debug arm crashed; superseded by s7725 (the env alone never traps; the push flushes a freed +0 texture descriptor that plume
  over-released; fixed).
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
   left-column count, 12 same-pose arms). **Mechanism now two-source (s7751):** the independent cxd4 RSP, fed the same
   captured gfx task (ROGUESQ_S7751_SNAP + tools/s7751_cxd4_task/replay), emits the same 3 pinned tris bit-identically
   (2/2 FARMAX=0 tasks), and 0 at the default (control arm): the pin is the F5 ucode's own result, not our LLE. Sheets docs/owner_sheet_s7310_farmax.jpg,
   s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
4. **Owner decisions on defaults:** M5_B40_VALUE (s7558/s7564: default 0 is alive only via the s4889+s7476 compensations; =1 is retail and equally clean 6/6), RETINA=1, QOS_ALL=1, S7524_V2P=1 (s7526), SP_LATE=1 (s7537), DD_FOG_ALT, dd8 bundle, RENDER_TO_RAM=0 (s7385). Never flip without the owner.
   QOS_ALL evidence: s7277-s7281 (load freezes removed) + s7382 (the threads it raises are exactly the hot ones, DEFAULT otherwise).
5. **G5i hangar re-entry (s6995), G5a Gerrard V crash (s6893; s6998 writeback audit clean), G5b terrain drops
   (FWDWIN far-loss fix, tools/g5b_fwdwin_seamless.py), G5d logo (s6903), G5f knife lines (s6906; sheets
   s7005/s7006), G5g hangar lens (s6907), G5h cutscene background (s6908-s6919; re-held post-G6c s7698-s7700 incl. movies playlist): owner flight / look.**
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
    after a regen run tools/s7610_ov_census.py --controls + tools/scan_selfbranch.py + the s7407-s7419 emission tools with --controls (rc 0); after a ucode regen tools/s7741_ucode_regen_gate.py --controls (strict, s7741) + tools/s7742_fixup_idem_gate.py --controls (s7742: fixup idempotent on main/_b/boot, fresh-regen _b+boot, overlays refused)
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
18. **After-regen UB gates (all CLOSED, rc 0 expected; rerun s7693 on the post-G6c tree: all rc 0, BLIND=0, FOLDED=0):** tools/s7575_ir_calls.sh + `tools/s7575_break_census.py --controls --ir D`
    (BLIND=0); `python3 tools/s7576_trunc_census.py --controls` (FOLDED=0); after a ucode regen or rsp*.hpp edit
    `tools/s7577_ubsan_sites.py <tu> --check` per ucode TU (UNCLASSIFIED 0) + `tools/s7577_ucode_ub_census.py scratch/s7577`;
    tools/s7580_lui_identity.py (0 object diffs). UBSan builds: `env SAN=<checks> B=<dir> zsh tools/build_ubsanc.sh`, scorer
    tools/s7579_bounds_report.py, plants ROGUESQ_S7578_PLANT=1-6,u (SANREC for non-recoverable checks). s7578 null/wrapv, s7579 bounds, s7580 shift/align, s7582
    pointer-overflow, s7583 div0/fcast/bool/builtin/vla/nonnull/unreachable CLOSED: every C-applicable UBSan check has run.
19. **Rerun-after-change censuses s7579-s7616 (all CLOSED, 26/26 rc 0 s7693; RG --witness takes >=2 of s7103/s7108/s7110 logs; per-class trigger text verbatim in PROJECT-OVERVIEW
    "(s7622 maintenance)").** Each `python3 tools/s76NN_<cls>_census.py --controls` must exit 0 after an edit in its scope:
    RQ/DQ s7616/s7615 (lib/rt64 RDRAM reads, new threads; a worker-thread RDRAM reader needs a command-time copy or a gate),
    HM/HP s7614/s7613 (--ast; statics), RG/SN/MK s7612/s7611/s7609 (--witness; regen, statics), OV s7610 (regen, overlays.cpp),
    TK s7608, UW s7607 (throw/catch, blocking calls), HC s7606 (threads.cpp/recomp.cpp), FR/RA/RX s7605/s7604/s7603 (host code
    touching guest regs/FPRs), TP s7602 (TO_PTR views), BS s7601, GX s7600, GR s7599, AZ s7598 (allocations, createTexture),
    XC s7597 (throw/json parse), FS/SV/SG s7596/s7595/s7594, EX/TH s7593/s7592, MR s7591 (lib/ edits). OW/OW-2/LK/HR
    s7585-s7589 tools as named in the archive. Renaming sweep closed (s6868). ROGUESQ_MTL_WAITPOOL default on.
20. **G6 (owner 2026-11-18): G6a rumble, G6b controls, G6c stand-ins: all LANDED, close on the owner's hands/look** (headline).
    Full step history s7617-s7691 (stand-in steps 2-4, H-culled/H-far, draw proof, handoff polish) verbatim in PROJECT-OVERVIEW
    "(s7703 maintenance)".
21. **Classes RP, HD, HB, ST, AT, CF, TS, TS-2, TS-3, TS-4, MK8 + walker fusion + spike cost + closed-gate drift (s7631-s7659):
    ALL CLOSED** (full text, numbers, controls, tools verbatim in PROJECT-OVERVIEW "(s7662 maintenance)"). Defaults that stay
    (=0 / old restores): ROGUESQ_S7634_FUSE=1 (walker fusion), S7639_ST, S7640_AT, S7641_CF, S7643_PI (release/acquire s4211 ring),
    S7632_SNAP; opt-ins/diag: S7636_FASTSPIKE (default 0), S7632_STATS, S7644_RSPDMA(_CTL), S7647_MASK8. Rerun triggers:
    tools/s7639_st_census.py after any SDL call edit or new thread; tools/s7640_at_census.py / s7641_cf_census.py after AppKit or
    framework-callback edits; TSan builds tools/s7642_tsan_rt64_build.sh, s7643_tsan_host_build.sh (lightweightsemaphore tsan
    annotations are TSan-only); the gate sweep after any src/ or lib/ change. A new G above 0x80180000 reads unclassified (RED): re-dump.
22. **s7663-s7718 owner-setting, crash-report, sweep and agent-gate items: ALL CLOSED** (old items 22-32 verbatim in
    PROJECT-OVERVIEW "(s7747 maintenance)"). Rerun triggers kept: rs64_settings.cpp edit -> tools/test_settings.cpp +
    scratch/s7663/run.zsh; any new src/ or lib/ instrument file -> the gate sweep before committing; `python3 tools/crash_reports.py`
    (rc 1 = NEW outranks all work); tools/agent/run_tests.sh after tools/agent edits (stop_gate runs it); SKIP_WILD_W change ->
    tools/s7705_fbread_flight.zsh + tools/test_s7705_join.sh. If CONTRACT-CARRY.md heads your prompt, fix it before NEXT.md.
23. **G6c coverage CLOSED on L1/L10/L12 (s7749 L12, s7750 L10+L1): no gap.** Lifetime table (tools/s7749_life_tally.py,
    200 s dd4 holds): L10 280 items ADDED 192 / CULL-OFF 81 / COND 3 / UNLINKED-NEVER 3 / DEAD 1; L1 47 items ADDED 43 /
    CULL-OFF 1 / UNLINKED-NEVER 3. CULL-FAR=0 and CULL-NOVT=0 on all three levels (activation control edges 64/32, nospawn 0).
    The s7748 L10 "273/273 never added" read was the same 120-try window artifact as L12. Reopen only on an owner report.
24. **s7310 FARMAX mechanism: CLOSED two-source (s7751)** — cxd4 replay of the captured task reproduces the pinned dome
    tris exactly; H-ucode selected, H-rspemu refuted.
25. **cxd4-vs-port RDP residual: CLOSED (s7752).** Offline replay of OUR ucode on the snap (tools/s7752_port_task/harness,
    needs ROGUESQ_UCODE_CAP=1048576 = live dd>1 cap, else a truncated prefix) == live stream byte-for-byte 3/3 (H-snapshot
    refuted); with ROGUESQ_G5B_TG_FIX=0 it is length-exact with cxd4 and the ~18 port-only tris + reordered 846-cmd block are
    gone (H-fixup: s6896 TriGen clamp). Last 31-33 cmds/task: degenerate-edge slopes (0xFE33 high half, yh==ym) and
    near-saturated tex/Z coefficients, rendered <=1 LSB on ~2.7% of px (tools/s7752_render_diff.py, --ctl passes): sub-visible.
    **G5b TriGen fix now two-source:** the retail ucode output (cxd4 == TG_FIX=0) draws giant terrain wedges over ~3/4 of the
    L1 21:9 dd8 frame (340k px >=8 LSB, scratch/s7752/img_f0_4054_tg0.png). Rerun after a ucode fixup edit: build.sh + harness.
26. **RDP-output regression gate: LANDED (s7753), widened s7754, in the sweep.** `tools/s7753_rdp_output_gate.py --controls` replays
    8 retained snaps through the live factor5_ucode_lean.cpp.o (harness auto-rebuilt when older) at each snap's live policy (dd1
    CAP=65536 TG_FIX=0, dd>1 CAP=1048576 TG_FIX=1) and requires == live RDP tail byte-for-byte: 2 L1 21:9 dd8 flight (scratch/s7751)
    + 6 from s7754 (scratch/s7754/retained: attract, SELECT GAME, L4 intro cutscene and flight at dd1 4:3, L4 cutscene and flight at
    16:9 dd2 FPS60). GREEN 8/8. **s7757: 13 snaps** - + 5 at the owner's 21:9 recipe (ASPECT=21:9 dd4 FPS60 STANDINS=1, stand-ins
    active: scratch/s7754/retained/w219_s{250,1000,2250,2750,4000}: attract, SELECT GAME, L4 cutscene, 2x L4 flight with TriGen hits,
    tg0 = our TG_FIX=0 length). 22/24 route tasks of that run exact from begin AND end image; the 2 misses are the hangar (H-state). GREEN 13/13. Ctls: tg0 (only the dd8 snaps have TriGen hits; 0 hits in every s7754 frame), CAP=<capc> strict
    prefix cap_fires=1, 1-byte flip. **s7758: 15 snaps** - + 2 L10 flight at the same 21:9 recipe in seconds adding 3085/5705
    stand-ins (w219L10_s10200 largest tail 348824 B, w219L10_s10800 add peak; 0 TriGen hits). L10 route: 24/24 flight tasks
    (s8400-s13000, 16 in stand-in-adding seconds) and 22/24 earlier tasks (16 of them the long Chapter III crawl) exact from begin AND
    end image; misses = hangar only. Stand-in region 0x81700000+ is CPU-only, so stand-ins never make a task H-state. GREEN 15/15.
    **s7759: 17 snaps** - + 2 SELECT YOUR CRAFT scrolls in the hangar RE-ENTRY after a mission abort (s6995 route on the owner save,
    21:9 dd4 FPS60 STANDINS=1; w219re_s15500 mid-scroll, w219re_s17000 settled): 20/20 re-entry craft-select tasks (aim camera on)
    exact from begin AND end image; the forced route never reaches this screen. GREEN 17/17.
    **s7760: 20 snaps** - + 3 in-mission overlays on the same owner route (w219ov_s11040 PAUSE menu, s11400 ABORT confirm, s12060
    MISSION FAILED medal; screens attributed by window sheet AND autopilot-fire/dump log order): 24/24 overlay tasks exact from begin
    AND end image (pause/abort re-render the full flight scene, 1.22 MB). GREEN 20/20.
    **s7761: 21 snaps** - + w219sel_s1620, the one begin-exact SELECT LEVEL holo task (normal boot, owner save, left@25 s). Owner
    route now covered end-to-end incl. SELECT LEVEL and LEVEL DESCRIPTION (C-up on AVAILABLE CRAFT; H-state, item 27). GREEN 21/21.
    RDP-output coverage is COMPLETE: do not schedule more coverage units.
    Pitfall: on L10 the crawl runs to ~VI 8500, so EVERY=250:24 without a <from> captures no flight (check snap vi vs the sheet).
    A RED after a ucode fixup edit = emitted stream changed: intended -> re-capture
    (`tools/s7753_capture_snaps.zsh`, `tools/s7754_capture_route.zsh` with ROGUESQ_S7751_EVERY=<N>:<max>:<from>) and say so.
27. **Hangar gfx tasks are NOT snapshot-replayable (s7754 H-state, measured):** in all 10 AVAILABLE CRAFT tasks (dd1 + 16:9 dd2)
    the begin-image replay and the end-image replay (`_end.bin`) give different streams and live sits between them; 14/14 other
    tasks are exact from both images. The influential RAM is the craft model's display list (0x720000-0x753000): the game CPU
    rewrites its 0x04/0x02 vertex-pointer words (0x8072xxxx -> 0x80739xxx) while the gfx thread's task reads that DL. Only
    shade/texture coefficients differ, never stream length. Evidence pair: scratch/s7754/retained/hangar_hstate/k900_s1250{,_end}.bin.
    **CLOSED s7755: not visible** (`tools/s7755_hstate_visibility.py <snap> [--cap --tg]`, flip + shade+16 controls). dd1 s1250 and
    20 H-state pairs at 16:9 dd2 FPS60: live == end-image render to <=1 LSB (5-bit) on all of them (no torn/half-patched picture);
    begin-vs-live <=3 LSB on <=313 px (craft shading) on alternate tasks. Retail-race vs port-timing is moot. Retained dd2 pair
    scratch/s7754/retained/hangar_hstate_dd2/k900_s1500{,_end}.bin.
    **Gated s7756:** `tools/s7756_hstate_gate.py --controls` (in the sweep, NEEDS-INPUT when the pairs are absent) requires
    live-vs-end ge2LSB == 0 on both retained pairs + s7755 flip/shade ctls; ctl CAP=2048 must read >=2 LSB (22589 / 44539 px).
    GREEN 2/2; planted cap=2048 policy -> RED 2/2, planted missing pair -> NEEDS-INPUT rc 4.
    **s7757: 3 pairs** (+ 21:9 dd4 FPS60 STANDINS hangar_hstate_219/k900_s1500): live-end ge2LSB 0 (631 px <=1 LSB), begin-live 336 px
    >=2 LSB (info only; same shape as 16:9's 313). GREEN 3/3, CAP=2048 ctl 44768 px. RDP-output coverage of the owner recipes is done.
    **s7759: 4 pairs** (+ hangar_hstate_219re/k900_s12750 = RE-ENTRY AVAILABLE CRAFT after abort, 21:9): the 3 re-entry H-state tasks
    (VI 12750-13250) render live-end ge2LSB 0 (1137/711/340 px <=1 LSB), same H-state shape as first entry. GREEN 4/4, CAP=2048 ctl 37385 px.
    **s7761: 5 pairs** (+ hangar_hstate_219sel/k900_s1800 = SELECT LEVEL holo, 21:9 normal boot): SELECT LEVEL is H-state too (6/7
    tasks begin != end; influential RAM region not bisected - begin/end images differ in ~320k words incl. fbs), and all 7 render live-end ge2LSB 0 (0-10153 px <=1 LSB),
    s7755 flip + shade+16 ctls PASS on each. **+ hangar_hstate_219ld/k900_s2400 = LEVEL DESCRIPTION** (C-up at 31 s): 14/14 tasks H-state,
    6/6 checked live-end ge2LSB 0 (618-17930 px <=1 LSB); begin-live up to 183 px >=2 LSB (info only, s7755 says VISIBLE on begin,
    same shape as the s7757 first-entry 336 px). GREEN 6/6, CAP=2048 ctl 21288 px.

30. **Placeholder census (s7770): rename sweep CLOSED on evidence.** `python3 tools/s7770_placeholder_census.py --controls` (ELF bytes,
    not objdump/generated tree): placeholders=2 called=0 (func_80018ED4 UNREF cache loop, func_80092F10 TAIL); func_8002BB34 was
    libultra send_mesg (14 jal sites), named s7770. stop_gate.sh blocks a NEXT.md naming the rename sweep while called=0
    (tools/agent/test_rename_census_gate.sh). **jal/j-to-interior class CLOSED s7771** (`python3 tools/s7771_jal_target_census.py
    --gate --controls`, raw ELF words per section, in the gate sweep): 15295 jal words, 14632 start, 188 .text->overlay start
    (lookup by loaded overlay), 474 from data sites (OUTSIDE/data_gap_/__OSGlobalIntMask). Code-site mid-function rows: 3, all
    dead or known: 0x800B58B8 playerAwingInitPreamble jal +0x30 into initNpcHealthMotionAndDetail and 0x8005EE64
    steerOrientationTowardTargetPreamble j steer+4 (3-word stubs after a `jr ra`, 0 jal/j/word/lui-pair refs, entry skips the
    target's prologue = H-data), 0x80092F8C = s7081 jump-table tail. 0 live H-interior. Gate RED on any new row (mutation ctl).
    **Overlay-aliased jal lookup class CLOSED s7772** (`python3 tools/s7772_ovl_lookup_audit.py --controls --gate`, in the sweep):
    188/188 .text->overlay start_ovl sites generated as LOOKUP_FUNC, 64 targets each a start in exactly ONE overlay, librecomp
    func_map = loaded sections only (s7528 evicts), so a wrong-overlay call aborts loudly; 0 lookup failures in 43 logged runs
    (280 overlay loads). **Sibling fn-pointer class CLOSED s7773** (`python3 tools/s7773_ovl_fnptr_audit.py --controls --gate`,
    in the sweep): 393 raw words / lui+addiu|ori pairs equal to an overlay function start; 359 overlay-local; 8 cross-overlay
    are own-overlay data addresses or jump-table targets coinciding with another overlay's start (own=data/interior); 26 resident
    = .text NPC spawners setupNpcUpdateFunctions/spawnDatStructureNpcByType (called by loadDatFile/updateActiveGridCellState and
    mission code) passing mission handlers to spawnNpcOfType; 0 targets a start in >1 overlay, so a stale slot handler can only
    abort loudly (jalr = LOOKUP_FUNC). Runtime: `python3 tools/s7773_ovl_swap_witness.py` 99 logs, 154 overlay swaps (incl.
    mission>menu 2), 0 "Failed to find function" (--plant ctl counts 1). Heap-held pointers: same loud-only argument.
    (s7775: the s7774 scan was rewritten to keep lockset/BS/OV census gates green: loaded_sections read before s7m, words via s7_ramw.) **Stale NPC-slot question CLOSED s7774 = H-cleared** (`zsh tools/s7774_slot_run.zsh <name>` = ROGUESQ_S7774_SLOTS=1 on the
    owner route_long abort->hangar, + tools/s7774_slot_scan.py): slot table *0x80130BB0 (2048x8 B, obj+0 = handler) scanned before
    and after every overlay-window DMA + every >=5 s tick. Ctl: in flight 29-36 live overlay handlers, all in func_map. At the
    mission(idx2)->menu(idx3) swap live=0 (last tick <=5 s before: 752 live/34 ovl): the game empties the table before the swap;
    0 post-swap unmapped, 0 "Failed to find function". Single run. **Dangling-table side finding CLOSED s7776 = H-unused:** in the
    menu (idx3) phase after the menu frees its NPC heap (~t=15-75 s) the pointer stays 0x80202120 while its block is reused (1578
    non-RAM entries); ROGUESQ_S7776_TBLWATCH=1 (s7484 load-watch bitmap marks the word 0x80130BB0, so all 59 generated lw sites
    report; 43 fired) counted 0 table-pointer reads in that window and dangling_hits=0 (read-time rescan), with the frame-counter
    watch ctl +8131 reads in the same window and 14.8M clean reads elsewhere. The next read of any kind is initNpcSlotList's
    re-init (t=77.9 cinematic table, t=83.8 mission table). Score: `python3 tools/s7776_tblwatch_score.py <log>` (--selftest
    3/3). Retail-shaped (pointer never cleared, never used): no guard needed. Single run.
31. **Dangling resident-global class (s7777-s7779): CLOSED 7/7, 0 defects.** `ROGUESQ_S7777_DANGLE=1 ROGUESQ_STORE_DIAG=1` ->
    `python3 tools/s7777_dangle_score.py <log>` (detail PORTING-STATE s7777). Members: heap head ALLOC-META, 0x80148514 NOT-PTR,
    0x8014A894 COMPARE-ONLY, 0x80136FCC READ-NO-DEREF (0 stale derefs, two ways), 0x80130BB0 unused (s7776), and the FRAME member
    (VI swap slots 0x80128E98/9C, frameStartReset 0x8011A8C0/C4) = FB pointer, H-retail (s7779, two sources): rs_malloc flag 4 ->
    ensureHeapInitialized builds a frame-scoped scratch arena (head 0x8010FEFC) over the FB that acquireFreeBufferSlot returns as
    FREE, and clearFrameReadyFlag drops it each frame. `ROGUESQ_S7779_ARENA=1 ROGUESQ_S7779_PLANT=300` ->
    `python3 tools/s7779_arena_score.py <log>` (rc 0 H-clean): 10 epochs of 10-70 ms per route_long run, never on a busy slot. Host
    writes into a live arena come only from its own loaders (zmemcpy 646, PI 4). rt64_writeback has 0 hits there and 15.8k ctl
    writes into the same span outside epochs. The plant is counted, 2/2 runs identical.
29. **FPS60 L12 half-rate phases: CLOSED s7769 as an unreproduced transient (not owner-reported).** s7749 L12 ring 60->30-43
    gen/s from t=75 s did not recur in 4/4 L12 arms (s7768 la/lb + soak s7768_fps60_rate_L12 r1/r2: 60 tasks/s, lim=1, send_dl
    ~10.5 ms, 0 slow windows). Two instruments agree: tools/s7768_fps60_rate.py (G3C_LOG+G1B; BUSY ctl 16/16 H-cost) and
    `python3 tools/s7769_ring_genrate.py <ring> [win] [from] [slow]` (present ring gen changes only; ctls s7749 u124 24/25 slow,
    s7768 lc BUSY 15 slow). Scan of all 32 FPS60 flight rings on disk (s7744-s7768): sustained slow only s7749 u124 (+ BUSY ctl);
    s7744/s7745 one isolated 42 gen/s window each. Reopen only on a recurrence or owner report; first run both tools on its log.
28. **Input latency (s7766): measured, H-1frame.** Tool tools/s7766_inlat.py (needs ROGUESQ_S7766_INLAT=1, ROGUESQ_G3C_LOG=1,
    ROGUESQ_PRESENT_RING; heading detector + --ctl fake steps). s7767: borderless, windowed and exclusive fullscreen all give
    queue->photon 23 ms at VI_LOCK=1, so the compositor lever is closed. Rerun after any present-path or input-path change.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7417, s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7617-7747; search bounded windows only.
