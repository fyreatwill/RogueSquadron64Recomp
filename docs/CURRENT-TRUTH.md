# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 6897 (2026-11-05).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md` (latest archive: "Migrated from CURRENT-TRUTH (s6847 maintenance)").

## Headline

- **FIXED s6898: Gerrard V cutscene black block.** It is the letterbox overlay right band: setupMissionTransitionScreenOverlay passes boot width 512 as the window right edge, fill runs 512..W on widened frames. tools/apply_s6898_letterbox.py, ROGUESQ_G1D_LETTERBOX=0 old, =tog. Same build 16:9 dd1 black peak 0.009 vs 0.106. FP_XSCALE, FPDEPTH, SPANBOUND refuted. docs/owner_sheet_s6898_letterbox_fix.png.
- **G5b s6897: Gerrard V cutscene black block follows ROGUESQ_ASPECT.** Block in both 16:9 FPS60 states at dd1, absent in both 4:3 (retail side single-source: oracle never reached the scene). dd>1 only steps its edge and loses the water foreground, unexplained. Not the sheets: it stands in fix-on seconds. Scene is an in-mission cutscene, not post-failure. docs/owner_sheet_s6897_black_block_by_arm.png, tools/g5b_letterbox.cpp (black share invalid at 4:3: pillars).
- **G5b s6896-s6897: dd3/dd4 near-plane sheets FIXED, owner must confirm drops.** Cause: TriGen s16 base + step wraps at 32768 of reach ahead of the eye (base 32256, step 512). Bases are eye-relative (s6897, tools/g5b_tg_camrel.py). ROGUESQ_G5B_TG_FIX default on at dd>1, off at dd1 (=0, =1, =tog). Same run: lvl4 dd4 0 vs 112, lvl1 dd4 0 vs 45, lvl4 dd4 0 vs 225; default dd3 and dd4 0 sheets (s6895: 43-687). Inference, untested: s16 caps reach at ~1.8x dd1, next limit for G1c phase 2. Witness ROGUESQ_G5B_TG, tools/g5b_tg_join.py.
- **G5b s6895: flat-sky frames are RT64 W<=0 wedges, FIXED at dd>1.** ROGUESQ_W_CLAMP default on at dd>1, off at dd1 (=0, =1, =tog); mixed-sign tris over 200 px span dropped at dd>1 (ROGUESQ_W_SHEET_PX). Small transients fell 3-11x at dd2/dd4; not shown to be the owner's spikes. docs/owner_sheet_s6895_wedge_vs_hardware.png.
- **FIXED s6893, awaiting owner re-flight: G5a writer named.** selectGridCellTileVariant (0x80046030) overran its tile variant pool at dd>1 (LEVEL=4 pool 90 entries, natural counts 94 and 97) into the next heap block, the sky object. tools/apply_s6893_tilepool.py scales the pools and clamps the slot; ROGUESQ_TILEPOOL=0 = old. Matched pair, same layout, forced overflow: unbounded = object overwritten + crash; clamp only = count 136, 0 writes. dd4 natural count 97: 0 writes. That this is the owner's crash is inference: G5a stays open until Gerrard V is flown past half way, repeated. Pool size checked on LEVEL=4 only (s6893_census_1-4 queued). Open: RT64 copyNativeToRAM writes the old object address at dd4 16:9; guard never fired, probably a dead block, unverified. PORTING-STATE s6893 has the arm table.
- **Owner playtest 2026-11-04 (16:9, FPS60): G3e's "0 drops" does not match what the owner sees.** dd4 drops better but significant, dd2 fewer, dd1 clean; also seconds-long freezes, Factor 5 logo missing frames, spikes still visible, and a repeatable mission crash (junk pointer 0x26282B2B at actor+0x18, see ITERATION G5a). Fog on extended terrain requested. Save guard: runner.sh exports ROGUESQ_NO_SAVE_WRITE=1 and snapshots build/saves to ~/Documents/RS64-save-backups/auto.

Verbatim s6689-s6758 headline bullets and the s6380-s6673 superseded entries were migrated in s6759 to
PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6759 maintenance)". Summary of what they established:

- **G3 render fidelity vs retail angrylion (tools/g3_oracle_match.py, rs64_oracle).** H-match, each with a same-run
  control: boot cinematic (s6738), attract Tatooine flight (s6739), 4:3 hangar (s6741), opening crawl (s6742),
  mission-intro cinematic (s6743), lvl1 flight+HUD/bolts/impacts (s6744-s6747), lvl2 flight+bolts (s6748).
  Colour rules: window captures are Display-P3 -> convert to sRGB (s6740); use `--dec shift` (v<<3), the v*255/31
  decode fakes a ~2% retail>port gain (s6744). Port RDRAM fb dumps lack RT64 3D frames: use window captures.
- **FIXED s6762: LLE ucode iteration cap truncated dense retail-settings frames.** The synthetic guard
  (`++rs64_iter > cap` at L_1090, tools/fixup_factor5_ucode.py) defaulted to 16384 at dd1/4:3 and cut each task's DL
  tail, so lvl9 ticks 292-458 lost the HUD, engine glows and tower lights that retail draws (dense retail dumps t296-386
  HUD on). Census (ROGUESQ_G3_CENSUS=<file>, per-VI tris/texrects/radar calls): renderRadarMinimap ran every frame, its
  texrects never reached the RDP stream, cap fired 192+ times; cap 65536 arm: 0 fires, HUD+glows drawn. Default is now
  65536 everywhere (=16384 restores). Earlier per-level G3 checks that saw no cap fire are unaffected. s6763: the
  second lvl9 port HUD-off window (t2050-2208) persists with 0 cap fires and retail hides the HUD on 16/16 dumps inside
  it (player death camera): retail behaviour, not a defect.
- **G3 OPTIONS sub-screens + ERASE GAME match retail (s6783, RDP stream).** tools/g3_rdp_frame_match.py (per-frame texrect
  coords+PRIM / tri multiset, retail rdplog vs RS64_RDP_BIN_PORT, cross-screen control 0 matches): BIOGRAPHIES and ERASE
  GAME 120/120 exact, GAME/SOUND SETTINGS 119 and 118/120, PASSCODES and CONTROLLER median diff 0-1 (spinning 3D model
  tri count / one transition tri), ELITE ROGUES geometry 108/120 with the colour residual = phase of the row-initial flash
  (all retail colours present in the port). Selected-row highlight = identical 60-frame pulse B94100FE<->E0AE09FE. Pixel
  IoU gaps on these screens are the slideshow backdrop + pulse phase (1 Hz retail dumps alias); score menus by RDP, not
  pixels. Pair runner tools/g3_menu_pair.sh: retail offset 7.3 s, >=5 s between presses (retail loads 2-5 s slower).
- **G3 ENTER NAME, hangar, SHOWROOM, Concert Hall (s6785-s6787): match retail at RDP level.** Detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6867)".
- **G3 front-end CLOSED (s6784).** Title START/OPTIONS menu (1171/1193 menu frames exact, residual = fade/pulse phase),
  OPTIONS top level (240/240) and post-erase SELECT GAME (median 7/870 = emblem tri count + pulse) match retail at the RDP
  stream, cross-screen controls 0 exact. Menu worker overlap (s6782 residual) is H-disjoint: the song-load worker exists
  only in screen 10 = passcode (MAESTRO) Concert Hall, which never sends or polls image jobs, and the passcode exit blocks on
  its own image completion first (tools/menu_worker_reach.py, static + runtime null on 3 routes with a same-run positive
  control; single-source for screen 10 itself, not driven).
- **G3 AT THE MOVIES swept (s6792).** 81/81 shots H-match vs retail per shot; the default spike cull deleted retail's
  legit 640-wide cinematic tris (port zeroed 24806, retail emits 26869 past the bound); cull now skips 321..640-wide images,
  notch 59/60 -> 0/797 frames, scanner positive control 20792 flagged / 0 culled. scratch/s6792/notch_fix_sheet.png.
- **s6794 cinematic sky seam line FIXED** (RT64 rebuilt tri edges; ROGUESQ_EXACT_EDGES default on, =0 old). Detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6875)".
- **CLOSED s6782: stack-payload send class.** tools/audit_service_msg_stack.py (offline, retail ROM, all segments): 8
  stack-formed sendServiceMessage/osSendMesg sites; 1 live (0x800B380C, fixed s6781), 3 doorbells whose receiver never
  dereferences (0x8000582C, 0x800058FC, 0x800C5880), 3 synchronous (0x80004BE4/D0C/F28 block until the stack object
  returns), 1 dead (shutdownAudioEngine quit byte 0x80091E78: its only caller shutdownMusyXEngine is unreferenced).
  s6781 FIFO soak lvl1 dd1: 304 s clean.
- **FIXED s6781: SELECT GAME inset / left emblem panel vanished at random (4 port states EI/E-/-I/--, retail always EI).**
  ORIGIN: the menu image worker tickFormatMessageWorker (0x800B3650) sends each completion as a pointer to a message on its
  own stack (sp+0x10, id +0x14) and loops; the menu polls one message per frame (0x800B3FD8, id byte +0x17) and fades in
  the slot (array 0x800CF180, stride 0x48) whose request id matches. Retail jobs take ~60 VI so each completion is read
  first (oracle: ids 1,2,3,4); the port's worker finished jobs 1 VI apart and the menu read 2,4,4 (slot 3 stuck in state 0).
  Fix: tools/fixup_menu_worker.py + rs64_menu_worker_sent/recv (host FIFO of pointer+id; the menu's lbu returns the id
  that pointer was sent with). ROGUESQ_MENU_WORKER_FIFO=0 = old. Same build: 3/3 arms EI vs control -I (ids 1 2 4 4).
  Rejected: blocking the worker on a stack timer (worker thread destroyed with its stack, no exit message).
  Front-end otherwise (s6779-s6780): title + level/craft select H-match; SELECT GAME backdrop = rand (retail too: idx=rand%7
  at 0x800B48F8, +(rand&3)+1 at 0x800B5274; title calls rand 1/VI). Title decode: --w 512 --h 448 --bases 790000
  --win 64,1024 --winx 85,1191.
- **G3 per-mission sim+render sweep 1-19 COMPLETE (s6753-s6778).** With dt pinned (oracle RS64_XTRACE_POKE / port
  ROGUESQ_XTRACE_POKE=800FA730:29:30:3d088889, needs RAND_TRACE) every mission's rand stream, NPC state, event mask and song
  handle match retail until the song end on the audio clock (retail drops frames, ~2.1-3.4 VI/tick; port 2.00), and render
  pre-split dumps match (d ~2-9 vs mismatch medians 44-64; outliers = torn retail dumps / capture phase); HUD-off windows =
  death camera / in-mission cutscenes in both arms; 0 cap fires, 0 crash. In-mission pause menu + debrief match (s6778).
  Reach: tools/g3_eep_patch.py (+0x31, clamped to 16 on load); bonus 18/19 need d-pad RIGHT on SELECT LEVEL; m17 race
  needs a one-shot rngSeed poke. Per-mission figures + recipes: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6847
  maintenance)". Oracle `--fb-dump` now copies in dbg_vi (old racy copy = every "torn retail dump").
- **FIXED s6839: oracle leaked --save-dir/--shot-dir into the user mupen64plus.cfg**; now restored at exit. Use
  --save-dir (g3_mission/run.sh), never swap a save over the user .eep. Do not re-run mission-3 flight.
- **FIXED s6755:** VI thread truncated its deadline to whole us and re-emitted ~1.4% of VIs; now exact ns, 59.999/s
  (ROGUESQ_VI_TRUNC_DEADLINE=1 = old). **FIXED s6739:** SDL audio device use-after-free (audio_device_mutex).
  **FIXED s6738:** plain launch ran non-hangar gfx through RT64 HLE; ROGUESQ_LLE_FORCE/UNGATED/SOLO now default ON.
- **G1e frame rate (s6696-s6716).** FIXED s6696: per-vector getenv in rs64_vld_note held the game at ~17 fps since
  s6372 (this also invalidated the s6455/s6458 shake readings). -O2 default (s6700). Fast RSP DMA (s6713), inlined
  vector templates (s6714), gated probes (s6715), opt-in ROGUESQ_RDP_ASYNC=1 (s6705), aligned DMEM fast paths +
  constexpr element-select table (s6774: -6.5% flight ns/cmd same-run, bit-identical by tools/g1e_dmem_equiv.cpp;
  ROGUESQ_G1E_DMEM=0 = old byte loops), gfx ucode TU on the constant `dmem` base instead of the thread-local g_dmem_cur
  (s6775: rsp.hpp RS64_DMEM_BASE, -DRSP=RS64_RSP_GFX against template merging with the audio TU; 1039 -> 38 dependent pointer
  loads; -1.6..-3.4% flight ns/cmd same-run, 7/8 paired windows; ROGUESQ_G1E_DMEMBASE=0 = old arm factor5_ucode_tls).
  Remaining ucode self (s6775 op-bucketed, tools/g1e_op_bucket.py): VMAD*/VMUD* math ~35%, generated .c body ~28%, SDV/SSV
  fast paths ~14%. **CLOSED s6776:** lvl5 FPS60 holds ~60 game fps at dd1-dd4 (tasks/s 60.3/60.3/60.3/60.1, dense
  half 60.5/60.5/59.5/59.3; per-task ucode 1.48-2.45 ms, Gfx thread 9-15% busy; [g1b] tasks 59.4-59.5/s, vi 60.0;
  tools/g1e_dd_table.py). The older "dd2 ~48-50, dd3 ~47, dd4 ~44" (pre-s6713) is superseded. s6788: those dd>1 fps were measured with the
  120-cell bypass cap, which drew less terrain than retail most of the time. **s6810 re-measure (current bundle, no
  recipe logging, s6716 recipe lvl1 FPS60):** dd4 59.3 / dd1 59.5 game fps ([g1b] tasks/s), [g1e-split] 60.3/60.6, dd4
  30.4k calls/task (2.6x s6776) at 5.4 ms ucode, Gfx 33% busy. Same binary + s6788 census/trace logging: dd4 48.8. The
  s6788/s6789 "dd4 45.9 / 42.8 fps" were logging cost, not draw distance (superseded).
- **G1c draw distance CLOSED s6703.** dd4 is the ceiling that adds terrain (lvl1/lvl5); dd8 sane after s6701
  (perspNorm centre-box) and s6702 (spill-arena leak in rs_free). Owner guide docs/DRAW-DISTANCE.md.
- **G1d widescreen + G1f window fit CLOSED (s6688-s6735).** Window opens at the chosen aspect, fullscreen toggle,
  16:9/21:9 menus, pause, game-over, debrief, title, LucasArts intro, mission intro and level select all fixed; most
  writers were our own s6156 HUD anchor / s6158 radar region shift / host scanners. Owner sheet
  scratch/s6731/sheet_menus_owner.png awaits judgement. Commands: docs/OWNER-OPT-INS.md.
- **G3c:** (a) far-edge stair no worse than retail; (b) spike wedges are drawn by hardware too (angrylion, s6454);
  ROGUESQ_CULL_SPIKE DEFAULT ON per owner 2026-10-31 (=0 retail); (c) shake: see G1e fix above.
- **G1:** levels 0..18 have route+300 s holds and framebuffer presence ([G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md));
  (d) objective response PARKED by owner 2026-10-31 ([G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md)).
- Closed: M5 audio de-stubbing, M3 idiom audits, M6 endurance (s6442), G2 audio, G5 renaming. G4 crash hunting parked.

- **FIXED s6879-s6880: wide flight lost far terrain, then 21:9 crashed.** ROGUESQ_G1D_FPDEPTH (default on, =0 old) undoes our s6144 forward-reach loss. That exposed a 21:9 crash: scanConvertTriangleToSpanTable (0x80042820) overran the span tables into the descriptor at dd 1, because the s6049 bound was gated on dd != 1. ROGUESQ_G1D_SPANBOUND (default on, =0 old) covers wide frames; k=1 retail. Same binary: =0 crashes, default holds lvl1 21:9 302 s, lvl5/lvl10 135 s; 4:3 and 16:9 0 px changed vs before the bound. 21:9 look is single-source; sheets docs/owner_sheet_s6879_wide_depth.png, docs/owner_sheet_s6880_219_depth.png.
- **s6881: s6879/s6880 now replay from pristine; wide + dd same-pose frames exist.** Regen stopped on an inline s6879 call that ran before the s6144 text exists; call removed, RS64_REPLAY runs it. Compare 2684/82/17/1 = s6871, s6879/s6880/s6049 text in funcs_9 identical to live. New apply scripts go in RS64_REPLAY only (docs/REGEN-VERIFY.md). No regen binary linked or run. Test-only fix: POSE_LOCK and POSE_FREEZE rejected player pointers above 8 MB, and wide + dd spills the player (0x809A6350), so keys were never zeroed and no freeze fired. 16:9 dd4 vs 4:3 dd4 now at identical pose: mad 11.53/11.54/17.53, ctl 25.95/24.00/66.16. Sheet docs/owner_sheet_s6881_wide_dd4.png.

- **FIXED s6882: wide + dd flight ran at 6-9 game fps at 21:9 dd4 and 11-20 at 16:9 dd4 (non-FPS60 recipe); now 20-31 at both.** ORIGIN: the span fill loops in scanConvertTriangleToSpanTable took x bounds of 0x7F7F, the span fill's own bytes. Inference, row count not logged: edge walkers 0x80041FA4/0x80042118 write the 80-row min/max arrays with no limit, so a deep footprint reads max[i>=80] from 0x80130DB0. Each row then walked ~32k x at three float divides, every store skipped (3.84e9 skips in 130 s). Same pose: frames 0 px changed, 0 skips vs 59777 log lines. ROGUESQ_G1D_SPANNARROW (default on where the s6049/s6880 bound runs, =0 old; retail dd1 4:3 untouched). Replays from pristine. Overrun itself: see s6883.
- **FIXED s6883: span scan overrun at dd > 1 or wide; 21:9 dd4 now 30 fps not 20-22 (recipe, non-FPS60).** ORIGIN: edge walkers of scanConvertTriangleToSpanTable fill the 80-row min/max arrays unbounded (row 264 at 21:9 dd4, 136 at 4:3 dd4, 65 at 21:9 dd1), and y/x outside 0..63 passed the s6049/s6880 byte bound into the wrong row or table (9e8 stores, all 4096 cells non-empty). ROGUESQ_G1D_SPANCELL default 3 where the s6882 gate runs (=0 old; bit 1 edge rows to host arrays, 0 px and no rate change alone; bit 2 cell bound, the active term; 4 control). Same binary, repeat 0 px: lvl1 21:9 tasks p50 21 -> 30, lvl5 21 -> 30, ucode 25.7 -> 18.9; lvl10 unchanged. Pixels: <= 3.2% change, a tie vs dd1 (13.84 vs 13.68). Sim identical per tick on every pair (tickdiv, controls fire), retail 4:3 dd1 0 px. Replays from pristine. lvl10 frames pending soaks s6883_l10z/d. Sheet docs/owner_sheet_s6883_spancell.png.
- **s6884: FPS60 21:9 dd4 cost split (lvl1, pinned, same 1612 ticks, all arms 0 px).** Logging text has no measured cost (r100 = r000 at 29.6 fps; r111 = r011 at 59.7). 30 fps = RT64 inline on the Gfx thread (sd_wall 21.6 ms) plus FAST off/PROBES on, which any ROGUESQ_LOG_* env sets: F alone 30.0, A (ASYNC+NODRAIN) alone 44.1, both 59.7, repeat 58.9. Measurement recipes understate rate through FAST/PROBES, not log volume; set ROGUESQ_G1E_FAST=1 ROGUESQ_G1E_PROBES=0 when timing.
- **s6884: opt-in ROGUESQ_RDP_SCREEN_JOB=1 removes game-rate dips (default off, needs ASYNC+NODRAIN).** ORIGIN: update_screen's drain waits on the Gfx thread for the tail NODRAIN deferred (drain p90 3.84 ms, updateScreen 0.28), and ucode + drain nearing 16.7 ms is what dropped tasks to 41-47/s. The job runs updateScreen FIFO on the RDP worker. Keyed lvl1 21:9 dd4, 2 pairs: tasks min/p10 41/46, 44/50 -> 58/60, 59/60; s below 50 11, 4 -> 0, 0. Pinned 0 px, sim identical 6461 ticks. **Displayed rate NOT shown better:** distinct drawn fbs at present p50 46, 55 off vs 54, 58 on, totals overlap, all below tasks/s (single-source, [present-1024] is a change log, not a counter). Other levels and 4:3 pending soaks s6884_job_*.
- **FIXED s6885: 21:9 flight showed frames out of order and dropped some; 4:3 never did.** ORIGIN: needStaticPresent's `screenFbSize.x >= 1024` (session 21, for the retail 1024-wide phase, which has no early presents) also matches 21:9 flight, VI width 1024. So the normal path pushed a stale-origin present behind every early present, 2 per workload, and the present thread ran whichever was last in the queue. ROGUESQ_WIDE_EARLY default on (=0 old): width counts only after 8 VIs with no early present. Same binary, lvl1 FPS60 + SCREEN_JOB, 70 s of flight, off -> on: dd1 backward steps 17.19 -> 0/s, frames never shown 8.10 -> 0.16/s; dd4 4.79 -> 0, 8.69 -> 1.11. Non-FPS60: 60 presents/s of 30 frames -> 30. Game rate unchanged, 0 crashes, no gap > 250 ms in any whole run (title and menus included). 4:3 fixed-binary arm: 0 backward, gaps match pre-fix. Frame identity is by buffer and time (W rows), not pixels; the look is unjudged, and 16:9 (VI width 768) was not run: excluded by the width test only.
- **s6885: present witness.** ROGUESQ_PRESENT_RING=<file> logs every present, every workload's draw targets, and CoreAnimation's presentedTime (not our runtime). tools/g1e_present_ring.py (rates), tools/g1e_present_order.py (order). Control: 30 fps arm 30.0 on screen, 100% in order. CA dropped 0.00-0.06/s in every arm, and on-screen rate is 59.8-60.0 at FPS60, so frames do reach the screen. Open: present-to-screen latency 57 ms at 60 fps vs 26-36 at 30, see NEXT. s6884 SCREEN_JOB soaks: lvl10 21:9 tasks 60/60/61, 4:3 lvl1 58/60/60, both clean (no off arm on those levels); lvl5 still queued.
- **s6882: 21:9 same-pose scores are valid now (H-fit).** g3_aspect_crop --pin (sx = sy from geometry) plus a crop fix. 21:9 dd4 vs 4:3 dd4: mad 4.74/2.94/2.95, hz_p90 2.42/1.61/0.81, ctl 18.56/15.82/57.88; 16:9 dd4 4.51/2.70/2.95. 21:9 dd1: FPDEPTH on 4.58/2.84/2.45 beats off 6.58/4.18/7.69. Best sx is 1.00% under sy at both widths, unexplained. Sheet docs/owner_sheet_s6882_219_dd4.png.

- **s6886: opt-in ROGUESQ_PRESENT_INFLIGHT=2 cuts display queue latency (default off).** Latency is queue depth on discrete levels. Measured from the present thread taking the frame to CoreAnimation presentedTime (tools/g1e_present_latency.py), lvl1 p50/p99: 4:3 dd1 72.2/72.9 -> 48.1/48.7 (repeat 45.5/48.2), 60/s on screen, game rate unchanged. 21:9 dd4 default moves between levels (57.4/72.3, repeat 42.4/54.4), gate p99 48.4-48.6 in 3 runs, so there it cuts the ceiling, not reliably the median. ROGUESQ_DRAWABLES=2 is weaker (52.8/55.8). INFLIGHT=1 halves the screen rate to 30/s: never use. 16:9 has no order bug (BACK 0.00/s). Not shown: input-to-photon, owner feel. Hidden-window cost fixed and window events covered by s6887.

- **FIXED s6887: PRESENT_INFLIGHT=2 no longer slows the game off screen, and holds through resize and fullscreen (still opt-in).** ORIGIN: our s6886 gate. Off screen, CoreAnimation reports a present only when a later one replaces its drawable (presentedTime 0, ~186 ms late under the gate), so every wait timed out: 16.5 presents/s. The gate now opens on a 0 report or a timeout and closes on the first on-screen report. lvl1, one binary, tools/g1e_present_events.py: hidden 60.0 presents/s, tasks 60/60/60; minimized the same; 1 logged timeout per run. After hide, resize, fullscreen on/off and minimize, gated 4:3 reads 47.9/48.6 vs ungated 66.3/72.6; 312 s of flight, last 105 s 48.0/48.6 at 59.8/s. 21:9 dd4 gated p99 48.1-48.5 throughout. 1-2 s task dips (31-49) on a fullscreen toggle occur gated and ungated. One run per arm. Not run: moving between displays (one display here), window covered by another window, input-to-photon, owner feel.
- **s6888: the ungated present level is a backlog, not a window state (lvl1 4:3 dd1, one binary, no gate; tools/g1e_present_level.py, g1e_present_slips.py, g1e_present_stall_course.py).** Producer and display both run 60/s, so depth holds until something moves it. Up: an on-screen slip (33-38 ms between on-screen times) under the ceiling stepped the level up 43 of 55 times; at the ceiling 0 of 101. Ceiling ~72 ms: 172 s unmoved with no events, nextDrawable blocking 12-15 ms. Down: a present-thread stall, inverse to dose. 17 ms lowered it 6 of 6 (to 47-52, or 64 once); 100-200 ms left it at 65-72 in 8 of 8, because workloads held behind waitForPresentId release 1-3 ms apart, each looks newest, is not skipped, and takes a display slot. Resize does nothing: 6 of 6 reached the swap chain (new Z ring row), level unmoved at the ceiling and from 52. Minimize is a reset with a varying result (72 -> 66, 72, 48). **Fullscreen is the one real window effect:** entry landed at 46-48 in 3 of 3 and had 0 slips in 39 s against 12 in 104 s windowed (~4.5 expected), one run. Slip cause not established; close-spaced presents sat near only 2 of 12 up-steps. 21:9 dd4 does not follow this: slips 0.3/s, level moves both ways, no dose response. Default unchanged. See NEXT.

- **s6889: opt-in ROGUESQ_PRESENT_DRAIN=<ms> beats the gate's median at 4:3 on a 60 Hz display (default off, single run, no repeat).** Over 31 reports, median above ms drops one present (>= 1 s apart). lvl1 dd1 FPS60, last 120 s, p50/p99, never shown/s: off 72.2/72.9, 0.14; INFLIGHT=2 45.8/48.5, 1.53; DRAIN=40 35.3/52.4, 0.12; DRAIN=56 52.5/70.3, 0.19. All ~59.9/s on screen. A flight drop omits a frame with no repeat (51 -> 34 ms, spacing 16.7). Gate keeps the better p99. Defect: limit 40 sits on an early-boot level (med 40.2), giving 18 drops that repeat a frame and lower nothing; 44 untested. tools/g1e_present_drain.py.
- **s6889: LATENCY FIGURES ARE PER DISPLAY. Check tools/g1e_present_cadence.py first.** The host moved to a 144 Hz grid mid run set (3840x1080 144 Hz main + two 1080p 144 Hz + built-in at 21:09; cause unknown). There ungated latency is p50 10-11 ms at ~59/s, median interval 13.9 ms, so the backlog looks 60 Hz specific (single-source, one display). 21:9 dd4 gave NO drain result: 0 drops, control did not fire. Gate + drain arm INVALID (display changed under it). Open: gate never shown 1.53/s vs 0.03-0.20 in s6886 rings, one run, unexplained.
- **s6890: on a 144 Hz display at 4:3 there is no present backlog, and 60 fps lands unevenly (lvl1 dd1 FPS60, last 120 s, one binary; off2 and st are the clean ungated rings).** Ungated latency p50/p99 11.8/21.1 ms (off2), 12.1/21.3 (st) against ~72 on the 60 Hz grid. Control: 200 ms present stalls 3/3 lifted latency to 24-39 ms and it was back at 12-14 by 0.3 s after stall start, so the instrument sees a rise and nothing persists. Spacing: 2 vsyncs (13.9 ms) 52%, 3 (20.8 ms) 37%, 1 and 4 vsyncs 12% (off2); exact 60-on-144 would be 60/40/0. Scorer controls: s6889 60 Hz ring 99.8% one interval, residual 0. Gate: no latency gain here (g2 13.2/19.9). g2's low 1v/4v share (3%) did not repeat in g2b (12.5%), so it is not a gate effect. The off-pattern 1v/4v share is not explained. 21:9: only the s6889 woff ring (59.15/s, 57/39 mix); s6890 got no 21:9 data. Whether this spacing is visible is the owner's call.
- **s6890: a ring with at=0 throughout is NOT a measurement; 7 of 11 arms were lost this way, g2b partly.** 4/4 arms sampled by tools/g1e_window_cover.swift (read-only, every 10 s) read 100% covered by the owner's apps and had no on-screen reports. Single-source: no arm had the witness AND on-screen reports, so uncovered -> reports is not shown. g1e_present_order.py still prints 60 "distinct shown/s" on such a ring. Check at=0 first; cadence --hist now prints INVALID.
- **s6891: on-screen reports depend on the display, not only on cover (boot matrix, 35 s per cell, one run each).** XG49V 144 Hz: 100% covered 0 reports, 67% covered 1133, 0% covered 1132. Built-in: 0% covered 1131 (4:3), 1128 (21:9). Both UG27 at 0% covered: 0 reports at 4:3 and 21:9. So a window only needs to be partly visible, and a ring on a UG27 is never a measurement (cause unknown; panels may be off, ask owner). The game opens BEHIND the owner's windows. New test lever ROGUESQ_WINDOW_POS=x,y; tools/g1e_display_free.swift picks a free corner, tools/g1e_display_state.swift counts displays.
- **s6891: the display set changes under runs; all three externals left at about 22:15 (woff grid 13.9 -> 16.7 ms mid run, built-in alone after).** Still NO 21:9 flight result on 144 Hz. On the built-in, 60 Hz grid, lvl1 4:3 dd1 FPS60, last 120 s, witness 0% covered, p50/p99: off 39.1/41.2; DRAIN=44 38.2/39.9, 40.2/42.8, no drops in that window (whole run 17, none lowering the level; 6, three lowering it, before the window); DRAIN=28 37.1/38.9 at 0.99 drops/s, 119/119 repeats, 59.0/s on screen; INFLIGHT=2 48.1/48.6, 39.5/41.8. Off has no backlog here, so neither drain nor gate helps. Keep DRAIN out of OWNER-OPT-INS. 21:9 dd4 on the built-in, no SCREEN_JOB, one run each, cover not matched: off 38.8/48.0 at 58.7/s, gate 37.7/47.8 at 54.6/s.
- **s6891: acq_ms marks the ungated backlog state.** Ungated acquire wait p50: 14.93 ms on the s6889 72 ms ring, 0.03 on o1 and on 144 Hz off2. Single-source, two ungated states. What puts a run in the 72 ms state is open; s6889's display then is unknown. Gate arms read 6-15 ms too, so read this on ungated rings only.
- **s6891: 1v/4v on 144 Hz are compensating pairs (H-boundary), tools/g1e_present_offgrid.py.** 1v beside >=4v: off2 294/485 (shuffled 48), g2 51/120 (4), g2b 311/540 (54), st 346/550 (63); pair sums 4-5 v. Q deviation off vs on pattern p50: 0.70/0.55, 0.58/0.50, 1.57/0.85, 1.11/0.94 ms, so producer jitter is not the main term. The 3% vs 12.5% share between the two gate rings stays unexplained. g1e_present_order.py now warns on rings without reports.

## Superseded conclusions — do not act on these
- s6896 "terrain bases are fixed map coordinates" and "the map's last + edge quad" (superseded s6897: base centre r ~0 with position, ~0.97 with view terms; believable because quads keep their words across swaps). s6894-s6896 "post-MISSION FAILED scene" and s6895 "sheets painted over black steps" (superseded s6897: in-mission cutscene; block stands with sheets gone).
- s6889 "DRAIN=40 beats the gate's median at 4:3 on a 60 Hz display" and s6889/s6890 "the backlog looks 60 Hz specific" (superseded s6891): believable because the off arm read 72 ms on a 60 Hz grid. A 60 Hz grid alone does not give that: built-in off reads 39 ms with nothing to drain.
- s6890 reading of at=0 as "the window was covered" (narrowed s6891): true on the XG49V, but both UG27 give at=0 uncovered. 100% cover still gives at=0 on the XG49V.
- s6888 NEXT H-cost "each skip is a visible repeat" as a general rule (superseded s6889): in flight a drop omits a frame and spacing stays 16.7 ms; it repeats only when the level cannot go lower. Believable because a skip looks like a missing present to the display.
- s6887 "one display here" (superseded s6889): the host now has four displays, three at 144 Hz. All s6885-s6888 latency figures are 60 Hz grid figures; do not apply them to 144 Hz.
- s6887 lead "a window state, not only queue depth, sets the level" and NEXT H-size/H-phase as framed (superseded s6888): believable because the level followed the fullscreen toggle and minimize in the one run. Resize does nothing; large stalls do not drain, the catch-up burst refills. Only fullscreen's missing slips are a real window effect.
- s6887 NEXT "[metal-resize-entry] fired only on fullscreen", read as resizes not reaching the drawable (superseded s6888): the log sits behind a layer-size compare that SDL's Metal view has already satisfied, and it also missed the first fullscreen entry. Use the Z ring row. s6887's AX resizes have no Z witness, so that part of its "holds through resize" stays unwitnessed.
- s6886 "hidden window slows the game with the gate on; a known cost" (superseded s6887): it was a gate defect, not a cost of the idea. Believable because the game recovered on return and hiding is rare; the wait trusted a handler that off screen fires only on replacement.
- s6885 "present-to-screen 57 ms at 60 fps" (superseded s6886): real figure ~72 ms at 4:3. Believable because it came from CoreAnimation; the start stamp was after the present call, so the nextDrawable wait was left out.
- s6884 "distinct drawn fbs at present p50 46-58, displayed rate not shown better" and NEXT H-line/H-skip/H-gpu as framed (superseded s6885): [present-1024] is a change log and only fires at width >= 1024, so it never had a 4:3 baseline. Believable because it was the only present-side number. Real: on-screen is 60/s, but at 21:9 it was the wrong frames, from a present order bug at every dd, not GPU load (dd1 was worse than dd4).
- s6883 NEXT "H-log: recipe logging may hold wf at 30" and "30 -> 60 bundles logging" (superseded s6884): log text is free at both rates. Believable because ROGUESQ_LOG_* arms were the slow ones; the env name turned FAST off and PROBES on, the text was innocent.
- s6883 "FPS60 + 21:9 dd4 p10/p50 47/60, 14 s below 50" as a stable figure (superseded s6884): repeats gave 49/59 (8 s), 46/59 (11 s), 50/60 (4 s). Believable as one run; the below-50 count swings 3x between runs.
- s6879-s6881 g3_aspect_crop MAD/hz figures (superseded s6882): the crop kept the 4:3 pillarbox bars, because 2 title rows survive --bar 62 and span the width, so black columns were scored as picture (MAD floor ~13, hz_mean 39-69 "unread"). Believable because arm ordering and control separation still looked right, and they still hold. Re-score with the fixed tool, do not quote the old numbers.
- s6881 NEXT "recipe logging may explain hd4 tick rate" (superseded s6882): GRIDLOG on/off gave the same VI steps and log size. The cost was the span loop.
- s6880 "g3_aspect_crop not valid at 21:9" (superseded s6882): the free grid's sy started at 1.50 and 21:9 needs 1.24. --pin fixes it.

- s6880 first reading "n219 k2 worse than o219 at 21:9" (hz_p90 31 vs 7.5, superseded s6880 same session). Believable because the tool had just scored 16:9 well; its 21:9 fit is bad (sx 1.22, sy 1.48) and the frames show the reverse.
- s6876 "in-place rotation writer = buildEffectObjectWorldTransform" as the pitch lead (superseded s6877). Believable because it made 8 of 10 [camcaller] rows; that was call count, it never changes word 5.
- s6875 NEXT "add a third dt to test linearity" as written, and the s6876 draft reading "dead-band settles the pitch" (superseded s6876). Believable because 1/45 looked like a third dt and the dead-band is truly per tick; dt is rounded to 1/60 ticks and the knob fires without moving the pitch.
- s6873 "FPS60 pass count follows tick rate" and "FPS60 k0/k1 not explained by frame age" (superseded s6875). Believable because the dt variants stayed near each limiter's own rate, so dt and rate never crossed, and the frame-age estimate assumed half a tick. Crossed arms: dt decides the path and camera pitch; a whole tick of presentation lag explains the rest.
- **"Pinned pose" on dd arms (s6445-s6583, superseded s6872).** POSE_PIN_POSITION never held position: the unit-range filter skips world-unit words (s6582 x ran 15..113), and even written every poll the ship flies on, because +0x4C is a per-tick copy. Believable because attitude did pin and the flag name said position. Cross-run dd figures from those arms (s6470, s6544, s6547) are attitude-only, not same-pose.
- s6268 "symbol sweep COMPLETE" and s3209/s3210 "0x80106C50 is a real callable" (superseded s6868). s6268 counted the syms toml, not the generated tree, where 30 table renames had never landed. s3209 saw a jal and took it for a caller; that site is decoded data. docs/GENERATED-NAME-CENSUS.md.
- s6004 "lvl10-15 mission_cycles=0, in flight the whole hold" (superseded s6867): mission_cycles only counts 0x690400->0x6AB400 origin changes, so it read 0 while lvl11 restarted twice and lvl14 once. Use inits= from the summary.
- **"300 s hold" on FPS60/dd>1 G1 recipes (s6774-s6862, superseded s6865).** Those runs gated on any origin (MISSION_RE='[0-9A-F]+' or a boot-time
  match), so hold counted from t=6..31 s, not flight. Believable because alive/crash/stall all read clean and mission_t looked like a number.
  Flight actually held (tools/audit_hold_flight.py, from [initMission]): s6788/s6789 lvl5 dd4 231 s, lvl10 dd4 124 s; s6832 lvl1 229 s, lvl10 124 s;
  s6857 lvl9 261 s, lvl17 275 s; s6850-s6852 lvl5 44 s. s6860 load pass: lvl5 reached no [initMission] (its s6860b rerun 148 s), the other 16 retained logs 52-129 s. Clean, but shorter than stated. All retained G1 logs: 117 runs report hold>=280 s, 65 of them flew <280 s.
- **s5547 "regen determinism CLOSED: replay reproduces live" (superseded s6863).** True on 2026-10-19, and believable because later patches were applied live and each session saw its script pass; none re-ran from pristine. The fixer stopped on pristine input no later than s5904. Regen restored s6864: docs/REGEN-VERIFY.md.
- s6161 "vp 0x80138D20 HUD elements are above 0x80300000, so that bound separates them from the reticle": believable because
  the only level checked (lvl1, w796) had the table at 0x8034xxxx. s6860: the table is heap and lands at 0x8028FDxx on lvl10.
- s6844 NEXT "the 21:9 hold rects (ul 0 lr 914.5 s=511) are the game's texrect clipper reacting to the lr.x overflow"
  (H-clip/H-wrap2): believable because the values sit right after the 12-bit wrap. s6845: the game clipper is fine; our
  s6156 HUD anchor shifted the full-screen wipe glyph -256 px once the pause byte dropped, and the clip of that x0
  reproduces the words exactly.
- s6842/s6843 "the abort wipe is not in the captured gfx RDP stream; the stream is x-invariant across the wipe": believable
  because the per-class tri/texrect scans and x-bin counts were flat. s6844: tools/rdp_bin_cmds.py output itself lists
  one black texrect with ul.x sweeping 477.8->0, lr.x 512 (why the earlier reading missed it was not established).
- s6815 "FPS60 halves the share of enemy impacts that cost hp (hit probability per shot: H-lead/H-collision/H-splash)":
  believable because impacts per game s were equal and every hit followed an impact. s6816: the hp hits are homing missiles,
  not bolts; the deficit is fewer turrets in range after a frame-locked terrain scrape at 15.4 s changes the player's path.

- s6813 "the lvl14 in-mission cutscene starts ~20 game-s later at FPS60, mission progresses slower in game time":
  believable because the sequence (HUD off, destruction) looked scripted and only 18 VIs were dropped. s6814: it is the
  passive player's death, later at FPS60 because fewer 50-hp hits land per game second; timers are dt-exact.
- s6788/s6789 "dd4 lvl1 FPS60 runs at 45.9 / 42.8 game fps": believable because the same runs showed the bypass cap had
  been hiding terrain (more terrain = more cost). s6810: those arms carried census + terrain-trace logging; clean dd4 = 59.3.
- **(s6770 -> s6772)** "+0x39 bits 0x00200000 -> 16, 0x00400000 -> 17; +0x31=LEVEL selects bonus missions".
  Bits are 0x00100000/0x00200000/0x00400000 -> 16/17/18, and the game clamps +0x31 to 16 on load, so missions 18/19
  are reached only by moving the cursor. Believable because +0x31 selected missions 1-16 exactly and m17 = cursor 16.
- **(s6770 -> s6771)** "mission 17 never calls runInMissionFrame 0x800FA730; flight at 512 wide ~24 s port / ~39 s
  retail; later Start presses pause the race". The 512-wide screen at those times is the LEVEL SELECT (its hologram ticks
  0x800C6674 and calls rand from 0x800B0xxx); m17b's presses ended before the pick, so neither arm ever raced. Believable
  because the level select and the race share VI width 512 and the rand callers looked mission-like.

- **(s6070/s6403 -> s6762)** "ROGUESQ_UCODE_CAP default 16384 = retail behaviour". Hardware has no iteration cap; retail
  draws the HUD in lvl9 frames the 16384 cap truncated. Believable because no dd1 4:3 frame had been seen to fire it
  (s6070 saw 0 fires at dd0.5; the truncation was only ever reported at dd>1/wide, where 65536 was already default).

- **(s6749/s6752-s6754 -> s6755)** "port runs a flat 2.00 VI per frame" / "port update_screen 61-62/s" and the
  s6754 elapsed-VI figures: the port VI column (rs64_vi_n_g) counts update_screen, and the VI thread re-emitted 1.4%
  of VIs, so port "VI" counts were ~1.4% high before the s6755 deadline fix. Believable because update_screen is
  driven once per VI loop pass, so it looked like a VI count. Relative tick comparisons stand.

- **s6740 "the 255/248 decoder-convention idea is refuted; the 2.5% gain is 512-flight-only"** -> superseded s6744. Believable
  because the cinematic logo/snow frames showed gain ~1.00 with the same decoder; but those are textures (5-bit on both
  sides) or saturated, so they cannot show it. Shaded 3D loses the gain under v<<3 in flight and in the 640 intro.
- s6739 "retail G channel +3.6..+3.9/255 above the port, possible H-shade" (believable: 12/12 pairs, two runs). s6740: the
  port side was raw Display-P3 screencapture values; after P3->sRGB the hue-dependent part vanishes, leaving a uniform
  2.5% gain in the 512 flight only. Lesson: convert tagged captures before any colour comparison.


- s6458 "G3c(c) turning shake closed as retail 30 Hz judder" and s6455 "camera jerk identical in all arms" (s6696: every run
  since s6372 ran at ~17 game fps with bunched presents from our own per-vector-load getenv). Believable because the jerk
  was arm-independent: the overhead was in every arm, retail included.



- Older superseded entries: PROJECT-OVERVIEW (s6759 maintenance; s6574-s6735 in "Migrated from CURRENT-TRUTH (s6870)").


## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Current pinned dd4 lvl1 run: `zsh scratch/agent/s6549_run.sh <dd> <poolx>`.
- dd4 was enabled without `ROGUESQ_DD_UNSAFE` in s6582; higher exploratory
  settings use DD_UNSAFE (clamp 8). Confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Wide soaks need
  `MISSION_WIDTH=796|1024` + `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`.
- Pose control: `ROGUESQ_POSE_LOCK=1` (no input) + `ROGUESQ_POSE_FREEZE=<x,...>:<ms>` (needs RAND_TRACE + DEBUG_WRITE arm;
  `tools/g3_optin_pose_arms.sh`). `ROGUESQ_POSE_PIN_POSITION` does NOT pin (s6872). Dump ordinal is not a phase key.
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` /
  `crashlines`, never rc. A queued repeat soak is not a work unit.
- Per-frame cost meter: `[g1b]` lines in run.log (sd_wall, tasks/s).
- Full dd knob/instrument table: PROJECT-OVERVIEW "G1c draw-distance knob and
  recipe reference"; owner guide `docs/DRAW-DISTANCE.md`.

## G1 mission coverage

Playable levels are 0..18 (`NUM_LEVELS=0x13`); 19/20 are sentinels. Route/hold
coverage and framebuffer presence are distinct from objective response.
Level 1 has a retail flight match. Level 0/1/2/3/4/5 named counter responses are
observed; remaining objective response coverage is partial. No level is promoted
here to fully VERIFIED. See [framebuffer coverage](G1-FRAMEBUFFER-COVERAGE.md)
and [objective contracts, evidence and limits](G1-OBJECTIVE-RESPONSE.md).
Mission wins, aim/steer and mission-to-mission progression remain owner playtest.

## Durable constraints
- Runs longer than a turn: never end the turn to wait, the Stop gate counts it, and a background run can die with the session (s6865 arm B got SDL_QUIT 5 s before the iteration ended). Run in the foreground (Bash timeout up to 600 s) or queue a soak (s6866).

- Retail defaults remain unchanged. Opt-ins include draw distance, aspect,
  FPS60, spike culling, and audio control. Do not make an opt-in default from
  a single-source result.
- `ROGUESQ_DRAW_DISTANCE`: dd2 qualified lvl1/5/10; dd3/dd4/dd6 300 s holds
  clean lvl1/5/10 under DD_UNSAFE; dd8 lvl1/5 clean. Crash-free holds do not
  mean "renders correctly" (s6468: dd>=4 ground missing before the bypass).
  No mitigation is acceptable without naming the writer and establishing value
  legitimacy; dd>1 fixes live in `tools/apply_s6*.py` and fixup scripts.
- Wide rendering uses runtime RAM-top handling and a larger reported memory
  arm; default remains 4:3/retail. Wide-only hangar band (s6602) CLOSED s6840 (absent at 4:3/16:9/21:9, scorer
  tools/g3_band_scan.py with controls); native hangar geometry remains parked.
- The title plume is parked after clean boots. Reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams.
  Ground truth must precede new instrumentation; every null needs a positive
  control and two independent lines of evidence before changing this file.
- Generated diagnostics must survive regeneration through fixup tooling.
  Never reset, clean, checkout, or update submodules. If editing `lib/`, run
  `./submodule-patches/export.sh` and commit the refreshed patches.

(s6675-s6677 level5 updates: see G1-OBJECTIVE-RESPONSE.md, same headings.)

## Parked G1(d) objective notes

s6678-s6687 per-level counter contracts moved to PROJECT-OVERVIEW (parked by owner).

## Next steps (single monotonic backlog)
- **Owner 2026-11-02 playtest (all three reports CLOSED).** Terrain dropouts at dd>1 (G3e), choppy Chapter II crawl
  audio (G2b), hangar fish-eye while scrolling ships (G3f). Owner asked for the PS4 remap + stick shaping (6ed036b97)
  reverted: get_n64_input is the pre-6ed036b97 mapping; do not change controls without an owner request.
  **CLOSED s6788-s6791:** G3e dd>1 terrain dropouts = s6540 120-cell span-bypass cap made terrain bistable + a sentinel
  collision (s6789); dd>1 defaults now BYPASS_MAXCELLS=-1 + UCODE_CAP=1048576; post-fix lvl5/lvl10 FPS60 dd4 0 drops over 231/124 s of flight.
  G2b crawl audio = host AI event threshold in bytes, now scaled with AI rate (ultramodern events.cpp). G3f hangar
  fish-eye = retail SELECT YOUR CRAFT camera move (H-retail); opt-in ROGUESQ_HANGAR_FOV landed s6836-s6838. Detail:
  PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6847 maintenance)".

Owner 2026-10-31: spike cull default ON; G1(d) objectives PARKED; G1f CLOSED s6717; G3d shake closed s6697.
Spec: ITERATION.md item 3c. No backlog-exhausted block.

1. **Closed s6807-s6846 (detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6847 maintenance)").** Transition AI
   gaps (s6807 same-rate set_frequency no-op; s6808-s6809 rs64_preempt_point -> max gap 2 VI = retail). G1e FPS60 rate
   classes all closed: float quanta (s6828, fixup_fps60_float_quanta.py), hangar tilt (s6829), spline ramp (s6830), int steps
   (s6831, fixup_fps60_int_step.py); owner table docs/FPS60-FIXES.md; bundle holds lvl1/lvl10 FPS60+dd4 clean (s6833);
   LIVES byte 800FB4F8 UNFIX (s6833-s6834). **Owner: judge FPS60 feel.** Boot freeze now 1 in 65 boots, thread PASSIVE
   ([stall-dump] default on, s6836). ROGUESQ_HANGAR_FOV opt-in (s6836-s6838). g3-hangar-artifacts CLOSED H-clean (s6840).
   21:9 mission-abort transition fixed end to end: striped frame (s6841 apply_s6841_ivsclear), wipe lr.x 12-bit wrap (s6844
   rs64_g1d_rect_wrap), bright hold = our s6156 HUD anchor (s6845 apply_s6845_hudwipe), end strip = initHudStruct 1 px
   epsilon (s6846 apply_s6846_wipeeps). Sheets docs/owner_sheet_s684[0-6]_*.png.
2. **g1d-wide-epsilon-audit CLOSED s6849 (static, single-source by method).** s6848 census + s6849 through-memory pass
   (tools/g1d_wcensus.py now also takes `lwc1 W` sources; docs/G1D-WIDTH-CENSUS.md): HUD node x/scale -> drawSubtitleText
   -> int16 -> drawTextGlyphRect (audited), overlay rect W-1 at 0x8011A90E -> clamp -> 10-bit pack 1023 fits, walker
   sprites -> rect clipper. 0 new flippers; class flippers = s6694, s6844, s6846, s6848.
   **s6850 runtime sweep lvl0-18 at 21:9:** all alive, 0 stalls/crashes (control fired 17/18; lvl5 uncontrolled). New
   class: edge-straddling sprites whose lr.x >= 1024 px wraps the 12-bit field and drops (lvl17 189, lvl6 45, lvl11 41...).
   Fixed by ROGUESQ_G1D_SPRITE_WRAP (default on, clip at the image edge when overhang < 384 px; same-build A/B lvl17,
   rewrites visible in RT64's input bin). **Residual CLOSED s6851:** those rects were valid when walked (ul.x ~760); the
   s6159 radar-region shift (rs64_region_scan, runs after the clip) added 256 px and masked the 12-bit x, wrapping lr.x.
   Shift now saturates (ROGUESQ_G1D_SHIFT_SAT, default on; =0 old); same-build A/B lvl17 WRAP 10 -> 0, controls fired.
   **s6852: the region box also shifted world geometry (H-world selected).** lvl17 21:9 SHIFT=0 bin (tools/g1d_regiontex.py):
   in flight the box held 8876 disc tris (texture 7965C0, z_cmp off, 39..85 cmds before the ring) plus ~49k world tris
   (z_cmp on) and 737640 particle sprites (the s6851 rect class, also drawn at x 110..998), all moved +256. Fix
   ROGUESQ_G1D_REGION_ZGATE (default on, =0 old): shift only z_cmp-off prims after the frame's first z_cmp-on prim (Z clear
   resets); TRI_PAD 32 also catches the one disc tri per frame centred 20-30 px left of the box, which was the grey wedge
   left 256 px from the radar at 21:9 in every flight frame. lvl17 runtime: disc 11840/0 shifted, world 12 shifted vs
   51390 (ZGATE=0); sheet docs/owner_sheet_s6852_regionzgate.png. Residual: one z_cmp-off object drawn after the world
   pass (lvl17, 171 tris/frame for ~600 swaps) is still shifted, as it always was. **16:9 verified s6853 (H-ok):**
   lvl1 16:9 (box 520..630, shift 142, pad 25): disc T43DBF0/T43E3F0 100% shifted in all 8 counter windows, every world
   texture 0 shifted; SHIFT=0 bin has no in-box texrect reaching the gate; frame docs/owner_frame_s6853_169_lvl1.png shows
   disc inside the ring, no wedge left behind. Soaks s6852_zgate lvl5/lvl9 21:9: alive, 0 stalls, ring textures shifted,
   world kept, out WRAP 0. **s6854: that lvl17 residual was the next frame's SKY** (79F7C0..7AD320 family) shifted under a
   stale latch: many lvl17 frames have no Z clear, so "world" carried over. ROGUESQ_G1D_REGION_CFLIP (default on, =0 old)
   also resets on a colour-buffer flip; same-build lvl17 A/B non-disc shifted 12115 -> 8, disc kept 0 both arms; offline
   replay tools/g1d_zoffobj.py agrees and reproduces lvl1 16:9 runtime counts. **s6855 CLOSED:** every in-box texrect is a
   world-anchored marker (lvl17 R78E080; lvl9 R79B270 drawn outside the box in 3933/3950 VIs); radar blips are tris
   (7A3FB0). ROGUESQ_G1D_REGION_TEXRECT (default off, =1 old) never shifts texrects under the gate: lvl9/lvl17 21:9
   runtime non-disc shifted 0, disc/blips 100% shifted, 0 stalls. Region-shift scope done; owner judges the look.
   **s6856 owner sheet** docs/owner_sheet_s6856_region_21x9.png (lvl9 x3 + lvl17 flight, 21:9): disc in ring, no wedge,
   nothing displaced; counters repeat s6855 (non-disc 0 shifted). **s6857 21:9 + FPS60 + dd4 (H-ok):** lvl9/lvl17 300 s
   holds alive, 0 stalls/crash lines; FPS60 live (1.07 swaps/VI vs 0.50 at 30 Hz s6856); disc 56083/20424 shifted, 0 kept;
   non-disc 0 shifted (328210/166197 kept); out WRAP 0; sheet docs/owner_sheet_s6857_region_21x9_fps60_dd4.png.
   **s6858 16:9 bundle + spill-arena fix.** With OSMEM_MB>8 the dd>1 malloc spill arena (fixed 0x80800000-0x80C00000)
   aliased the game heap: 16:9+OSMEM12+dd4 crashed 9/9 at mission load (loadTextureToMemory strncmp on a wild HMT name
   pointer); arm table: only OSMEM>8 & dd>1 crash, FPS60 irrelevant. The dd policy now sets SPILL_HI + RAMTOP_MB=20 when
   OSMEM>8 (21:9 sets OSMEM 12 itself, so its bundle was aliased too, latent). Post-fix lvl1/lvl9 16:9+FPS60+dd4+OSMEM12:
   302/303 s clean, disc 100% shifted, non-disc 0; sheet docs/owner_sheet_s6858_region_16x9_fps60_dd4.png.
   **s6859 21:9 bundle on the new layout (H-ok, lvl9/lvl17 only):** 303/305 s clean, spill 752/3008 blocks all at 0x81, disc
   67636/23184 shifted 0 kept, non-disc 0, out WRAP 0; sheet docs/owner_sheet_s6859_region_21x9_fps60_dd4_spillhi.png. RDRAM
   dump noise on debrief pages = s6723/s6724 pillars (crop fired 8/8 in both layouts; no window capture this run).
   **s6860 load pass lvl0-8, 10-16, 18, env-free owner path:** alive, 0 stalls/crash lines, spill 752 all at 0x81, used 0x9E00/0x400000; control
   (aliased layout) SIGBUS 5/5. 143 s holds, one run each (lvl5 needs 300 s to pass its cinematic).
   **FIXED s6860-s6861:** lvl10 wide HUD anchor (bound 0x80110000) and pause-open HUD jump (ROGUESQ_G1D_PAUSE_GATE_MASK). Detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6872)".
   **g1d-heap-address-tests CLOSED s6862 (H-clean on the owner path; static reading is single-source, HUD table also runtime).** Census tools/audit_heap_addr_tests.py, table docs/HEAP-ADDR-AUDIT.md:
   every behaviour-changing pointer guard follows RS64_RAM_TOP or the 16 MB RSP ceiling; fixed heap bounds left are logging or opt-in harness (the 0x80300000..0x80330000 NPC family, (x>>24)==0x80, FS slot),
   and can read as false zeros on other levels or layouts. HUD table lvl1/5/10/14: moves by level, always above the 0x80110000 bound, reticle static. s4563 stale-head skip is DEAD (setter gone from funcs_0.c);
   the hazard is held by s4786 PAUSE=4. The 9 absent MARKs are strip_diag_layers (7) + fixup_live_replay (2), by design (s6863).
   **replay-patch-presence CLOSED s6864 (H-diag; lvl1 dd1 boot, single run per arm).** Regen from pristine compiles (51/51, control file fails as it should;
   strict flags), links, and boots: lvl1 130 s hold regen vs live, 0 stalls, 0 crash lines. Per-function machine code
   (tools/regen_verify.sh, docs/REGEN-VERIFY.md): 2708 same, 75 differ, 0 missing, and all 75 are layout, env-gated hooks or opt-in logging.
   Pristine refreshed: fresh make_elf + N64Recomp = s5547 input, 0 lines. Regen drops only opt-in diagnostics (list in the doc), so it
   is now safe; the live tree was NOT regenerated. The queued s6864_regen_fps60_dd4_lvl5 rc=1 was the harness, not regen: 5x nomission, 0 crash lines, the 690400 gate never matches at dd4.
   **s4563-dead-code-removal CLOSED s6866 (H-dead; one run per arm).** s4563 removed from live funcs_24.c and the replay list, script deleted, live rebuilt. Regen compare still
   2708 same / 75 differ, same 75 names; funcs_24 before/after: only musyxSynthFrame really differs. Two replays from pristine: 0 lines apart. Post-removal regen lvl5 FPS60+dd4: 306 s of flight, alive, 0 stalls,
   0 crash lines (scratch/agent/m6/g1_lvl5s6865regen). Post-removal live lvl1 dd1: 135 s of flight, same (g1_lvl1s6865liveb). G1 recipes now gate on [initMission] (MISSION_INIT=1, WAITN=60 in g1_level_coverage_common.zsh); the gate fired 4-5 s after it in both arms: H-gate refuted.
   Not re-checked: s6285 armed gate still matches live by construction, on the opt-in dd>1 path.
   **g1-true-flight-hold CLOSED s6867 (H-holds on 4:3 FPS60+dd4; one run per level).** lvl1 305 s, lvl5 306 s, lvl10 302 s of flight, inits 1, 0 stalls, 0 crash lines, no frozen run after [initMission].
   Retail 660 s holds audited offline: gates sat 2-11 s after [initMission] on all 19 levels, so the s6865 gap does not apply; but only lvl3/5/10/12/13/15/18 stayed in one mission, the rest restarted (longest continuous lvl6 267, lvl7 299, lvl11 289, all upper bounds). Table: docs/G1-TRUE-FLIGHT.md.
   Summaries now print inits= and flight_s= (m6_god_common.sh, same-run control flight-control OK); tools/audit_hold_flight.py reads .gz and prints wall_s, tools/audit_hold_segments.py gives continuous stretches. No per-level hold sweep queued: G4 parks repeat holds, and 1/5/10 is the owner's qualification set. FPS60+dd3 and FPS60+dd2 on lvl10 are not held to 300 s (inference from dd4).
   **G5 function names CLOSED s6868.** regen_replay.sh now applies tools/rename_generated_symbols.py; all 139 address-named functions are shape names, compare still 2708/75 with the same names, lvl1 dd1 135 s flight clean (one run). 791 D_ data symbols unnamed.
   **data-decoded-tail-audit CLOSED s6869, generated-size-mismatch CLOSED s6870 (H-elf; one run per level).** make_elf.py sizes each function to the next symbol and never reads the syms toml; tools/regen_front.sh now feeds real sizes through N64Recomp `function_sizes` (tools/func_sizes.txt). 17 junk data_gap_ functions gone from regen. `.word` is NOT a code/data boundary: 3339 of 8152 became do_break, the rest run. docs/DECODED-TAIL-CENSUS.md.
   **elf-size-valid-tails CLOSED s6871 (one run per level).** tools/audit_elf_tails.py classifies every tail >= 0x10 by what lands in it; func_sizes.txt now 11 rows. Pristine 823108 lines, cut step 0/0, compare 2684 / 82 / 17 only live / 1 only regen (the 4 new diffs are the 4 sized functions). Regen lvl1 144 s, lvl5 142 s flight clean, dd1 4:3. Live tree NOT regenerated.
   **Silent N64Recomp miscompile, NOT fixed; selfbranch-mission-null CLOSED s6878 (H-dead on missions 1 and 2, one run per mission plus a mission 1 repeat).** A backward branch out of a function lands on that function's own entry and compiles. 16 real ones, in the voice resampler helpers (one-shot sample end). Retail flight, 420 s: 0 hits in 8009264C..800934A4 and 0 in decodeAdpcmSampleBlock 800934D0..80093D10, while range-form controls fired in the same runs: playSpeechClip 4 (m1) / 19 (m2), allocAndConfigureNewVoice 6 / 21, adjacent 800923E4..8009264C 12.6M / 11.1M. m1 speech timed in flight at 204.4, 241.6, 257.1 s (first tick 203 s); m2 hits were not timed. So speech plays without this block. Static scan also finds no caller. The other 17 missions rest on the static scan and the same voice path; a computed address would escape it. Reopen on any sign that block runs; design in PORTING-STATE s6871. Any new `branching outside` warning on live code needs the same check.
   **g3-optin-frame-diff s6872:** dd4 near field matches dd1 on lvl1 at k0/k1 (one run per arm). Detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6874)".
   **s6873 (lvl1):** pinned dt (g3_optin_pose_arms.sh PIN=1) makes no-input flight bit-identical, floor 0.00 per k; the s6872 fork was dt jitter.
   **FPS60 render CLOSED on lvl1 s6875 (H-near refuted, one level).** FPS60 with dt pinned 1/30 equals 30 Hz frozen one tick later: MAD 0.00/0.00/0.03 at k0-k2, adjacent ticks 5.7-7.7 same run, camera block equal. So the limiter changes nothing drawn; the 30 Hz window just lags its last built frame by one more tick at a freeze. Real rate difference: camera pitch follows dt (tools/g3_cam_pitch_cmp.py), 0.0632 at 1/30, 0.0606 at 1/60 (0.15-0.26 deg), craft attitude equal, so about 2-4 px at 1280x1024. Writer not found. The k2 contact split follows dt too (ufix y -6.799).
   **s6876 lvl5/lvl10 exact match NOT reproduced; neither gap is a limiter draw difference (one run per arm).** lvl1's 0.00 needed POSE_REF. lvl5 (NOREF): ufix vs n1 0.42-0.57, whole view sub-pixel, pitch 0.06330 vs 0.06290 (0.00039 rad ~0.4 px), 0 exact camera rows vs 2568/2570 for n1/n2. lvl10: 7.2-8.4 is cloud-layer phase, same tick count (4489/4490), about half the VIs; n1/n2 0.5. Cloud clock (VI or wall) not measured.
   **dt is rounded (s6876):** runInMissionFrame rounds it to the nearest tick (floatModulo, 0.5 at 0x800A8F94), dt<=0 -> 1/30, cap 0.1 (ROM constants). Tick 1/60 inferred: 1/45 arm equals 1/60 (3798/3799 rows); step ratio 3:2:1 at 1/20, 1/30, 1/60. Only those dt values exist; pitch 0.06233/0.06316/0.06055, not monotonic.
   **Pitch: attitude dead-band REFUTED (s6876). Pitch source NAMED s6877, thread CLOSED on lvl1.** Only updateEffectObjectOrientationQuat +10636 moves word 5 (sum 1.40-2.20 per arm; +41236 and buildEffectObjectWorldTransform 0). Retail sinfApprox (really asin, 0x8001C400) returns pi/2 for x > 0.99999899, so errors under 0.08156 deg read as zero: floor measured 0.0815 in 3 arms, same value from the ROM constant. Pitch steps until inside that zone and stops, so each dt holds a different value (not monotonic); zone 0.163 deg, arm spread 0.1495 deg. u30 repeat 695/695 rows, u30/u60 0. s6875's 0.26 deg upper figure not explained; retail at 1/60 not observed. No fix: retail behaviour, tools/g3_cam_calls.py.
   **FIXED s6874: any ROGUESQ_DRAW_DISTANCE != 1 deleted retail's off-map terrain border.** Retail's footprint window runs past the map (z[32,67) on 64 rows, x[-23,3)); getGridCellValueAt sends those cells to clampGridCellLookup (0x80048948), which repeats the edge cell. The s6037 clamp to tw/th cut them, so the map edge stood against the sky. ROGUESQ_DD_EDGE (default on, =0 old) keeps them; cap and 64x64 limits spend off-map cells first. Same build, k2 whole-frame MAD vs dd1: old 7.43, fixed 0.03. dd4 lvl1 only 135 s so far; lvl5/lvl10 FPS60+dd4 holds queued. Sheet docs/owner_sheet_s6874_dd_edge.png.
3. **G1d close-out awaiting owner judgement** (scratch/s6731/sheet_menus_owner.png; recipe scratch/s6731/menus.sh
   <tag> <aspect|none> "ROGUESQ_LIVES_CAP=1 <env>"). Mission-start dark frame with edge lines = RT64/present path,
   horizontal line fixed s6735, vertical line = source column cw-1 clear colour (s6736).
4. **Owner judgement / parked.** G3c sheets; native hangar geometry and rare dd4/dd8 gfx SIGBUS parked
   (single-source). Reopen on an owner report or a side-effect failure, not repeat holds.
5. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first. NEVER send hull damage
   on level 8 (counter3==1 fails the mission).

**Active s6891:** 21:9 flight on 144 Hz still unmeasured (externals gone); recipe in scratch/agent/NEXT.md. DRAIN stays out of OWNER-OPT-INS; SCREEN_JOB and PRESENT_INFLIGHT defaults stay off until the owner chooses.

## Evidence index

- s6847 maintenance archive (per-mission G3 bullets, closed s6788-s6846 next steps): PROJECT-OVERVIEW.
- s6759 maintenance archive (verbatim headline s6689-s6758, superseded s6292-s6673): PROJECT-OVERVIEW.
- [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts: [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); per-level images:
  [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md`; latest s6865_truehold_lvl10_dd4 (run by hand s6867). None queued.
- Recent chronology: PORTING-STATE sessions 6788-6846; search bounded windows only.
