# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 6836 (2026-11-03).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md` (latest archive: "Migrated from CURRENT-TRUTH (s6759 maintenance)").

## Headline

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
- **G3 front-end CLOSED (s6784).** Title START/OPTIONS menu (1171/1193 menu frames exact, residual = fade/pulse phase),
  OPTIONS top level (240/240) and post-erase SELECT GAME (median 7/870 = emblem tri count + pulse) match retail at the RDP
  stream, cross-screen controls 0 exact. Menu worker overlap (s6782 residual) is H-disjoint: the song-load worker exists
  only in screen 10 = passcode (MAESTRO) Concert Hall, which never sends or polls image jobs, and the passcode exit blocks on
  its own image completion first (tools/menu_worker_reach.py, static + runtime null on 3 routes with a same-run positive
  control; single-source for screen 10 itself, not driven).
- **G3 ENTER NAME + native 4:3 hangar match retail at RDP level (s6785).** ENTER NAME 235/236 exact (odd frame = retail
  transition), control 0/236. Hangar (SELECT LEVEL, 512 wide): frame-pair matcher never goes exact (median 209/1260)
  because ~1100 tris share one PRIM that flickers per frame and the hologram picture + lower band are wobbling texrect
  grids; new tools/g3_rdp_phase.py (distribution compare): 153 texrects/frame both, static set 53/53 identical (prompt line
  25/25 rects), tri q05..q95 [1093..1136] vs [1094..1138], mean ratio 1.003 over ~800 frames each; hologram grid visible in
  ~20% of frames in both. Control (retail hangar vs port ENTER NAME) separates on every term.
- **G3 AT THE MOVIES swept (s6792).** 81/81 shots H-match vs retail per shot; the default spike cull deleted retail's
  legit 640-wide cinematic tris (port zeroed 24806, retail emits 26869 past the bound); cull now skips 321..640-wide images,
  notch 59/60 -> 0/797 frames, scanner positive control 20792 flagged / 0 culled. scratch/s6792/notch_fix_sheet.png.
- **s6794 cinematic sky seam line FIXED (port-only RT64 raster defect).** RT64 decodeTriangles rebuilt each RDP tri as
  (H(yh), H(yl), (xl,ym)), so the minor L/M edges leaned off their real position by rounding (sky: L x=318.000 vs rebuilt
  318.036); with RT64's +0.5 px halfPixelOffset pixel 318 samples at x=318.0 and fell outside both shared-edge tris -> clear
  colour. A half-period texture shift left the line in place (refutes wrong texel). Fix: exact polygon H(yh) H(yl) L(yl) L(ym)
  M(ym) M(yh) emitted as a fan when an edge misses by >1/256 px (ROGUESQ_EXACT_EDGES, default on, =0 old, =tog A/B). Same-run
  off 0.58 / on 0.00; playlist line shots 40/939 -> 2/902 (content); lvl1 flight 120 s clean, no new lines. Retail RDP streams
  are identical to ours (s6793), so retail-match is unaffected; ROGUESQ_RESMULT selects Manual (s6793).
- **G3 SHOWROOM fully driven (s6787).** AT THE MOVIES does nothing on a lvl1 save in retail or port (cursor on it, A
  fired, 133 texrects unchanged). Passcode DIRECTOR (pair script PASS2=DIRECTOR) enables it: the cutscenes play back to back
  at VI width 640 (+3.0 s port / +3.4 s retail after the press). Cinematic RDP match: 1184 aligned frames, tri-count median |d| 1,
  521 full-signature exact, wrong-lag control cost 417 vs 23, title cards on the same frames. Concert Hall track changes:
  same title order in both arms (3 tracks), no song-worker request per change in either arm. Dump caps: RS64_RDP_BIN_PORT_MAX_MB
  (port), RMAX_MB/PMAX_MB/RBW=all (pair script).
- **G3 screen 10 = OPTIONS > SHOWROOM matches retail (s6786).** Passcode MAESTRO (tools/g3_passcode_sched.py) adds the
  SHOWROOM row; SHOWROOM (ships fly past the Death Star; CONCERT HALL / AT THE MOVIES / BACK) and the CONCERT HALL song
  player: texrect static sets identical (80/80 + 1595 animated positions, 99/99), controls disjoint. The tri gap is the
  game's RNG: ship idx = rand%18 then +1/+2 per 1023-tick flyby, pose = rand&0x7FF; menus call rand every frame so the seed
  differs per arm. Indices from each arm's seeds (tools/g3_showroom_models.py) predict the shared ship (model 10: tile and
  texture sets equal 908/908, control 0). Song worker runtime H-disjoint in both arms (one request + completion after image
  job 4, no image mark after). Port song worker completes in the send tick, retail 9 ticks later (benign, one job).
  Runner tools/g3_showroom_pair.sh (GAP=16 needed). Front-end CLOSED except SHOWROOM > AT THE MOVIES.
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
- **G3 in-mission menus (s6778, m17):** pause menu H-match (d 6.8-8.3 vs medians 45-48, mismatch controls 44/100);
  debrief text/emblem match (emblem sway same range both arms); backdrop photo differs only after a sim split
  (single-source). **Oracle fix:** `--fb-dump` used to copy RDRAM on the VI-poll thread while the emulator drew: 37/42 dumps
  saw VI_ORIGIN change mid-copy and debrief dumps lost text. Every earlier "torn retail dump" outlier is that race, not
  retail. Now the copy runs in dbg_vi: 0/42 swaps, 0/7 incomplete vs racy 2/7 in the same run.
- **G3 mission 3 (s6777, canyon, pinned):** sim identical t0-t1775 (23112 rand calls, 35041 NPC rows, 0 disallowed
  words); split t1776 = song-1 end on the audio clock (retail 167 ticks/637 buffers, port 166/638). Render pre-split
  d 3.90-6.36 vs medians 44-64; vi 9693 = torn retail dump in the song-1 cutscene (HUD off in both arms). 0 cap, 0 crash.
  **Per-mission G3 sim+render sweep 1-19 COMPLETE.**
- **G3 mission 19 (s6773, Battle of Hoth, bonus, snowspeeder):** sim identical over the whole retail trace (6077 rand
  calls / 4742 ticks; 34420 NPC rows to t2999 with 0 point/obj diffs, 0 disallowed words); song handle never changes,
  so no split (as m11). Render best d 4.4-5.7, worst = torn retail dumps / camera phase. 0 cap, 0 crash. Reach: two
  d-pad RIGHT on SELECT LEVEL (port `23:w512,25:right,25.7:right`, retail `41:dright,42.5:dright`) + craft Start.
  **Per-mission G3 sim sweep 3-19 CLOSED** (1-2 render match s6744-s6748; m3 pinned render s6777).
- **G3 mission 18 (s6772, Death Star trench run, bonus, X-wing):** sim identical t0-t1097 (16980 rand calls, 31908 NPC
  rows, 0 point diffs, 0 disallowed words), split t1098 = song-3 end (retail t1098 vs port t1115: audio-clock split as
  m10-16); flip control flagged. Render pre-split d 3.47-6.07, outliers torn retail dumps / phase. 0 cap, 0 crash.
  Reach: the game clamps the saved current mission (+0x31) to 16 (0x8006EE7C/0x8006EEB4), so bonus 18/19 need d-pad
  RIGHT on the SELECT LEVEL screen (port `23:w512,25:right`, retail `41:dright`) plus a craft-select Start (port 42 s,
  retail 64 s); recipe in the run.sh header. Offline needs G3_SNAP_TICKS=800FA730.
- **G3 mission 17 (s6771, Beggar's Canyon race, bonus):** sim identical to retail over the whole race, 458
  runInMissionFrame ticks (3972 rand calls, 3664 NPC rows, 0 point/obj diffs, event mask/song identical, no disallowed
  snap/glob word); 1-bit flip control flagged. The race ticks 0x800FA730 like every mission. Recipe: tools/g3_mission/run.sh
  with PRESS to 51 s / AP to 31 s (no press after the level pick: the race starts by itself, the unsteered T-16 hits the
  ground ~12 s in, MISSION FAILED), POKE=<dt pin>,800FA730:0:80003470:1:1 (new one-shot 5th field, both arms: rngSeed=1 on
  race tick 0), G3_MIN_TICK=0 G3_SNAP_TICKS=800FA730 offline. Render: in-race pairs d 4.9-9.5; outliers = crash wipe phase,
  fast-motion capture phase, one torn retail dump. HUD-off t417-453 = crash in both arms. 0 cap fires, 0 crash lines.
  Unlock (s6770/s6772): save byte +0x39=0x60 sets bonus bits 0x00100000/200000/400000 (indices 16/17/18; run.sh adds it).
- **G3 mission 16 (s6769, ocean/Calamari towers, +0x31=15):** sim identical 2038 ticks (70442 rand calls, 32319 NPC
  rows, 0 point diffs before t2040, 0 disallowed words); songs 1/2/3 start on the same ticks in both arms (game events;
  retail drops frames to 3.25-3.44 VI/tick there, port 2.00), split t2039 = song-3 end on the audio clock (retail 166
  ticks/336 VI/641 buffers, port 167/334/640). Render: pre-split dumps d 3.96-13.2; vi 15145 = torn retail dump; d 10-13
  = capture phase (port draws the same spray plume 0.3 s later). Port HUD-off t1864-2039 = player death camera (song 3);
  retail dump inside is HUD-off and matches at d 3.96. 0 cap fires, 0 crash lines. Control: scratch/s6769/flip_ctl.py
  (s6768's script can land on an uncompared 8006c018 row) flips one rand value and it is flagged.
- **G3 mission 15 (s6768, canyon/bunkers, X-wing, +0x31=14, no unlock flag on the save route):** sim identical 1377
  ticks (23845 rand calls, 37807 NPC rows, 0 point/obj diffs, tick_mem first diff = the split); split t1378 = song-1 end
  on the audio clock (retail 153 ticks/334 VI/638 buffers, port 167/334/640). Render: pre-split dumps d 5.0-8.5; vi 7930
  and 9730 = torn retail dumps. Port HUD-off t1082-1379 = overhead in-mission cutscene; both retail dumps inside are
  HUD-off. 0 cap fires, 0 crash lines. Control: a 1-bit rand flip is flagged.
- **G3 mission 14 (s6767, lava planet, Y-wing, +0x31=13):** sim identical 2875 ticks (32988 rand calls, 43243 NPC rows,
  0 point/obj diffs, tick_mem first diff = the split); split t2875 = song-1 end on the audio clock (retail 124 ticks/334
  VI/639 buffers, port 167/334/640). Render: pre-split dumps d 1.8-4.2; vi 7480 = torn retail dump (no ship/HUD drawn
  yet). Port HUD-off t2628-2865 = in-mission cutscene; the one retail dump inside (t2753) is HUD-off too. 0 cap fires,
  0 crash lines. Control: a 1-bit rand flip is flagged.
- **G3 mission 13 (s6766):** sim identical for the whole 4417-tick retail trace (60110 rand calls, 104266 NPC rows, 0
  point/obj/tick_mem diffs); songs 1/2 switch on the same ticks in both arms (game events), no split. Render: in-trace
  dumps d 4.6-5.6 (8.0 once), three torn retail dumps d 15-24. Port HUD-off t4308-4415 = letterboxed in-mission
  cutscene from the song-3 switch t4305. Control: a 1-bit rand flip is flagged. 0 cap fires, 0 crash lines.
- **G3 mission 12 (s6765, Escape from Fest, +0x31=11, no unlock flag):** sim identical 1006 ticks (3978 rand calls,
  0 NPC point/obj diffs, 0 tick_mem diffs, only allowed pacing words); split t1007 = song-1 end on the audio clock
  (retail 165 ticks/334 VI/640 buffers, port 167/334/637); after it the same rand values run 2 ticks late. Render:
  pre-split dumps d 5.6-9.3 (9.3 = bolt phase only). Port HUD-off t1168+ = its own post-split death camera, then
  game-over debrief. 0 cap fires, 0 crash lines.
- **G3 mission 11 (s6764, Bespin, Y-wing):** sim identical for the whole retail trace, 3410 ticks (25226 rand calls,
  78 NPCs, 0 point/obj diffs, 0 tick_mem diffs, no song switch in either arm, so no split). Render: 15 retail dumps
  d 4.9-7.1, one torn retail dump (vi 12965, d 9.8); HUD on 14/14 retail dumps and 345/345 port captures. 0 cap fires, 0 crash lines.
- **G3 mission 10 (s6763):** sim identical 1410 ticks (16812 rand calls, 24 NPCs, 0 obj diffs); split t1411 = song-1 end
  on the audio clock (retail 129 ticks/332 VI/634 buffers, port 167/334/640). Render: pre-split dumps d 3.1-6.8, two
  torn retail dumps (angrylion mid-raster) d 15/22; HUD-off t1270-1401 in both arms. 0 cap fires, 0 crash lines.
  Oracle stdout splices `[vi-poll]` inside xtrace tokens: g3_frame_snap/tick_mem/song_windows/ai_clock now cut the
  token at `[` (dropping the row shifted the tick join by one and faked NPC diffs from t372).
- **G3 sim determinism with dt pinned (s6753-s6763).** Missions 3-10: rand stream, NPC state, event mask and song
  handle identical to retail (lvl5 20635 rand calls / 1972 ticks). Unpinned desyncs = pacing (retail drops frames,
  2.115 VI/tick; port 2.000). Late splits on lvl4/lvl7/lvl8 = song end on the audio clock (equal AI-buffer counts; lvl8 s6760: retail dropped
  frames to 2.43 VI/tick in the song, so the same 331-VI/634-buffer song spans 136 retail ticks vs 167 port ticks).
  Pin: oracle RS64_XTRACE_POKE / port ROGUESQ_XTRACE_POKE=800FA730:29:30:3d088889 (needs RAND_TRACE). Mission
  select on a signed save: tools/g3_eep_patch.py (+0x31). Tools: g3_rand_ticks, g3_ai_clock, g3_frame_snap,
  g3_tick_mem, g3_vi_edges. Allowed render-pacing diffs: snap words 2-6/9, glob 7/8 (0x8011A89C-A3), 18, 20-31.
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

## Superseded conclusions — do not act on these
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

- s6735 "the load-frame right-edge vertical line is a stale presenter column from the full-width hangar present" (believable: it sat outside the horizontal line's extent and survived the follow-mode fix). s6736: it is source column cw-1 holding the game's clear colour, also visible in briefing/flight. The pre-load screen is the briefing fly-over, not the hangar.
- s6729 "H-rt64-target: identical commands + identical TMEM, RT64's render target drops the draw" (SUPERSEDED s6730).
  Believable because the dpc_bridge rect2 log showed identical texrects on undrawn/drawn swaps; but that log runs before
  the s6158 region shift rewrites the stream. RT64's own RDP entry log ([rtrdp]) showed the rects arriving at x 896/960.
  Lesson: a bridge-side command log is not RT64's input while any RDP-rewrite hook runs after it.

- s6574/s6576 "dd8 lvl1/5 hold clean" as a usable dd8 (s6701: every dd8 frame from the hangar on drew inside a centre box,
  perspNorm 1 from the scaled far). Believable because holds were crash-free and fb checks sampled early or terrain-fraction only.
- s6458 "G3c(c) turning shake closed as retail 30 Hz judder" and s6455 "camera jerk identical in all arms" (s6696: every run
  since s6372 ran at ~17 game fps with bunched presents from our own per-vector-load getenv). Believable because the jerk
  was arm-independent: the overhead was in every arm, retail included.

- s6692/s6693 "21:9 floor tear is lost in RT64 depth handling at w=1024" (s6694: the game's scissor lrx w*4 wraps to 0 in the 12-bit field, so the depth-clear fill is clipped empty before RT64 bookkeeping). Believable because RDP triangle input matched and only RT64 touched the depth rows.

- s6631 "21:9 level-select tear closed: heap 8010FEFC stops at the depth image" (s6691: the s6631
  passing frame is visibly torn; heapslot on/off both torn). Believable because the s6631 scorer
  (edge columns at x=16/w-17, dy180) flipped from fail to pass with the cap; it never measured the
  floor rows themselves, and nobody looked at the frame.

- Older superseded entries (s6292-s6673) are archived verbatim in PROJECT-OVERVIEW (s6759 maintenance).


## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Current pinned dd4 lvl1 run: `zsh scratch/agent/s6549_run.sh <dd> <poolx>`.
- dd4 was enabled without `ROGUESQ_DD_UNSAFE` in s6582; higher exploratory
  settings use DD_UNSAFE (clamp 8). Confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. Wide soaks need
  `MISSION_WIDTH=796|1024` + `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`.
- Pose control: `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_PIN_POSITION=1`; dump
  ordinal is not a phase key, join dumps to `[vi]`/origin
  (`tools/g1c_fbdump_join.py`).
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

- Retail defaults remain unchanged. Opt-ins include draw distance, aspect,
  FPS60, spike culling, and audio control. Do not make an opt-in default from
  a single-source result.
- `ROGUESQ_DRAW_DISTANCE`: dd2 qualified lvl1/5/10; dd3/dd4/dd6 300 s holds
  clean lvl1/5/10 under DD_UNSAFE; dd8 lvl1/5 clean. Crash-free holds do not
  mean "renders correctly" (s6468: dd>=4 ground missing before the bypass).
  No mitigation is acceptable without naming the writer and establishing value
  legitimacy; dd>1 fixes live in `tools/apply_s6*.py` and fixup scripts.
- Wide rendering uses runtime RAM-top handling and a larger reported memory
  arm; default remains 4:3/retail. Native hangar artifacts remain parked.
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
- **Owner 2026-11-02 playtest:** terrain drops out for single frames, intermittently but
  consistently; still frequent with only FPS60 + DD4 (ASYNC/NODRAIN refuted as sole cause) ->
  ITERATION G3e, take now. Owner tried a PS4 remap + Starship-style stick shaping (6ed036b97)
  and asked for it reverted: get_n64_input is back to the pre-6ed036b97 mapping. Do not
  change controls without an owner request.
  Third run: no dropouts with no draw-distance arg -> dropouts are a draw-distance (dd>1) defect.
  Owner also heard choppy audio on the Chapter II text crawl -> ITERATION G2b (after G3e).
  Owner also saw a fish-eye-lens look in the hangar, only while scrolling between ships (gone
  1-2 s after the camera settles) -> ITERATION G3f (after G2b).
  **s6788 G3e mechanism named + fixed (lvl1, FPS60, per-VI census + terrain trace, same build):** the s6540 per-swap
  span-bypass cap (120 cells) made dd>1 terrain BISTABLE. The retail span test rejects ~1500 in-window cells in 86% of
  dd4 swaps (pose-dependent); with only 120 rescued, terrain flipped between full dd4 and LESS than retail (lvl1 dd4
  median tris 816 vs dd1 1083; kept-cell count vs tris corr 0.86; 47 in-flight drop edges / 180 s, dd3 90, dd2 0, dd1 0;
  0 ucode-cap fires on drop frames). Uncapped accept: drops 47 -> 4-6, median 1407-1431, but 431 synthetic ucode-cap
  fires per run, so the dd>1 bundle now also sets ROGUESQ_UCODE_CAP=1048576 (fires 0). New dd>1 defaults in
  rs64_g1c_apply_dd_policy: ROGUESQ_BYPASS_MAXCELLS=-1, ROGUESQ_UCODE_CAP=1048576 (explicit env wins). Default-path
  run: dd4 6 dips / dd3 0 in flight; game fps lvl1 dd4 45.9, dd3 48.2 (dd1 59.9; s6810: logging-on figures, clean dd4 = 59.3) - the old dd4 "56-60 fps" was partly
  bought by drawing less than retail. RESIDUAL (NEXT): dd4 dips every ~481 VI (= the autopilot 8 s a/sl/a/sr cycle):
  kept cells decay ~2200 -> ~850 over 4-5 frames, then jump back, window constant. lvl5/lvl10 soaks queued (s6788_g3e_*).
  **s6789 residual NAMED + FIXED (sentinel collision, two lines):** (1) per-call reject reasons: on dip calls the 0x80042D64
  "both span bytes == 0x80" skip jumps 61 -> 957 cells/call (pool-cap, z/x skip, no-node all 0); (2) scanConvertTriangleToSpanTable
  clamps each frustum height to ROM floats [-128.0, 127.0] (0x8003A4E8-F4; ROM read verified against the runtime-logged 0.2/-0.2
  thresholds at 0x8003A4D0) and stores it with sb, so a saturated-low height IS the 0x80 "untouched" sentinel. dd4 pyramid
  corners sit at y ~ +-86 grid units (4x dd1), so pose changes push whole swaths past -128. Fix tools/apply_s6789_spansent.py:
  at dd>1 the low clamp is -127.0 (dd<=1 bit-identical; ROGUESQ_SPANSENT_FIX=0 opts out, ROGUESQ_SPANSENT_TOG=N same-run A/B).
  Same-run A/B lvl1 FPS60 dd4: fix-off blocks 10 kept-dips / 4 census drops, fix-on 0 / 0 (median spaneq 133 -> 0). Clean arms:
  dd4 0 and dd3 0 in-flight drops (pre-fix dd4 6, every ~481 VI); dd1 control has no in-flight dips (H-retail refuted for the
  periodic dip). Cost (logging-on arms; clean dd4 = 59.3 fps, s6810): dd4 game fps 44.6 -> 42.8 (visible terrain now actually drawn). Remaining census "drops" are the mission
  intro cuts (VI ~3560/4057, tri=0, also in dd1). Prior s6788 lvl5/lvl10 dd4 soaks (pre-fix) showed 17/12 drops, many tri=0
  cut frames; post-fix soaks s6789_spansent_lvl5/10_dd4 folded s6790.
  **G3e CLOSED s6790.** Post-fix FPS60 dd4 300 s holds, 0 crash / 0 VI stall: lvl5 in-flight terrain drops (tx>0) 12 -> 0;
  lvl10 0 -> 0. Remaining census hits in both levels are (i) the tri=164/100 front-end frames (ci 644800/6A2400, same VI
  pre- and post-fix) and (ii) 3-VI tri=0 triplets at timeline-fixed VIs, present pre-fix, post-fix and in the dd1 lvl1 run
  (dd-independent cuts, not terrain). dd3/dd4 may be recommended again in OWNER-OPT-INS.
  **G2b NAMED + FIXED s6790 (choppy Chapter II crawl audio):** the crawl switches the AI rate to 32006 Hz (play uses 22047).
  The s5672 host-paced AI event fires when the SDL queue drains to <= 2048 BYTES: 23 ms of headroom at 22047 Hz but 16 ms
  at 32006 Hz against the 1024-frame device period, so the queue ran dry every ~96 ms (~10.7 underruns/s for the whole
  ~95 s crawl). H-fps60 REFUTED (FPS60 on 1033 / off 1023 empty-queue events over the 32 kHz span); H-underrun SELECTED.
  Fix (ultramodern events.cpp, exported): threshold scales with the live AI rate above 22047 Hz (32006 Hz -> 2972 B);
  <=22047 Hz bit-identical; ROGUESQ_AI_DRAIN_FIXED=1 restores the old threshold. Same build, same crawl, FPS60:
  fix 0 empty-queue events / 96 s, control 1023 / 95 s. Instrument ROGUESQ_AI_TRACE=<file> (per AI buffer: wall s,
  queue bytes, samples, VI width/origin; PCM to <file>.pcm), analyzer tools/g2b_ai_scan.py. Single-instrument (SDL queue
  depth); the owner's listen is the second line. Also seen, not chased: ~315 ms AI gaps with an empty queue at every
  scene transition (boot, hangar entry, mission load, game over) in every arm.
  Recipe: owner save + ROGUESQ_FORCE_SAVE_MISSION=5 ROGUESQ_FORCE_UNLOCK=5 (index 5 = THE JADE MOON, Chapter II start),
  Start 6..41 s -> crawl at 43-60 s (scratch/s6790/crawl_arms.zsh).
  **G3f CLOSED s6791 (H-retail): hangar fish-eye = retail SELECT YOUR CRAFT camera move.** Camera 0x800CD670: fovy 45,
  aspect 1.882 (about 76 deg horizontal) on every call, FPS60 on and off, rotation orthonormal. Each ship scroll slides the camera 13 units sideways
  in ~0.5 s while its yaw lags ~3 s (overshoot 1-1.6 on rightward moves). Same endpoints and shape in retail (oracle
  swc1 store trace of cam+0x2C..0x5C, tools/g3f_retail_pan.sh + g3f_retail_cam.py; fovy word not animated). FPS60 only samples
  the same delta-time curve at 60 Hz. Instrument ROGUESQ_G3F_CAM=<file> (setupCameraMatrices, the only guPerspective site).
  Offer the owner an opt-in hangar FOV knob if wanted; default stays retail.

Owner 2026-10-31: spike cull default ON; G1(d) objectives PARKED; G1f CLOSED s6717; G3d shake closed s6697.
Spec: ITERATION.md item 3c. No backlog-exhausted block.

1. **G3 transition AI gap CLOSED s6807 (NAMED + FIXED).** The port's 19-VI guest AI feed gaps at every scene transition
   (= G2b's ~315 ms empty queue) were src/main/main.cpp set_frequency closing/reopening the CoreAudio device (~150 ms,
   blocks the guest caller) on each same-rate osAiSetFrequency, twice per audio re-init. Retail oracle traced from boot
   (tools/g3_ai_gap_pair.sh): max gap 2 VI through boot/title/level select/load/flight, 1.912 buf/VI. Fix: same rate +
   open device = no-op (ROGUESQ_AI_REOPEN_ALWAYS=1 restores). Same build: gaps 7 -> 0, 1.866 -> 1.912 buf/VI.
   s6808: title residual (4-6 VI @737/973, real underruns) = game thread pri 10 / OSId 7 pri 5 building text glyph meshes
   70-90 ms with no OS call; ultramodern never preempts between OS calls, pri-122 audio starved. FIXED: rs64_preempt_point
   (tools/fixup_preempt_point.py, =0 off) -> max gap 2 VI = retail. Instrument ROGUESQ_VI_WALL + tools/g3_title_gap.py.
   s6809 audit CLOSED: hangar-entry/mission-load gaps (VI ~1958/~2507) = game thread spinning on anyAudioSlotActive
   (drainAudioAndFinalizeSpeechBuffer, gracefulMenuShutdown drain loops); preempt point added there -> lvl3 boot->flight
   0 post-boot empty-queue events (control PREEMPT_POINT=0: 3). Soak s6809_preempt2_lvl1_fps60 queued.
   s6810: soak s6809_preempt2_lvl1_fps60 clean (303 s, 0 stalls; AI qzero=1 only at boot, 0 after). lvl3 flight was
   already matched s6777 (every mission 1-19 is).
   s6811 G3 LARGE FIREBALL = H-match: lvl9 unsteered crash (same tick both arms) -> star flash, translucent dome, burst,
   embers identical in tick order (pairs d 2.96 vs ctl 8.0; dome frame 2.96 vs 23.3; hot-pixel colour equal). Retail wall
   duration 2x port = 4 vs 2 VI/tick. Dense port capture now exists: g3_port_capture.sh BURST=t0,t1 (winctl burst, ~16 fps);
   recipe tools/g3_mission/fireball_pair.sh, scorer tools/g3_fireball_score.py.
   s6812 lvl14 CUTSCENE VEHICLE DESTRUCTION = H-match (t2737-2750, EEP=scratch/s6767/lvl14.eep): tick-keyed pairs (new
   tools/g3_tick_pair_score.py, pairs by sim tick via snap.txt) median d 1.21 vs ctl 3.98 over 141 pairs; hot-pixel
   count/colour per tick equal (flash 8973|6169 px, same RGB).
   s6813 same destruction at ROGUESQ_FPS60=1 with dt pinned 1/60 (owner's setting, deterministic) = H-match in GAME seconds:
   flash peak -> dome end 0.27 s (retail 0.27-0.30; a per-frame effect would be ~0.14), phase colours within ~13/255
   (scratch/s6813/fps60_sheet.png). Refutes H-anim60/H-blend60. g3_tick_pair_score.py --port-rand/--ratio keys a port on its
   own ticks.
   s6814 the lvl14 HUD-off sequence is the PASSIVE PLAYER'S DEATH (flag 0x100 in 0x8010CA1C set by spawnNpcDestructionDebris
   on the hp-0 tick, 7/7 runs). FPS60 dies later (seeds: 30 Hz 87/81/52 s, FPS60 102/>138/86/96 s) because it takes ~half
   the 50-hp hits per game s (0.107-0.140 vs 0.029-0.069, no overlap); per-hit damage, hp regen (1.945/s) and mission
   timers are dt-exact. Tool tools/g3_death_time.py.
   s6815 (offline, 7 seeded runs, tools/g3_fps60_hit_attrib.py): the s6814 "NPC formation spawns 0.7x" is NOT a spawn
   timer. spawnNpcFormationWithRandomOrientation is misnamed - a particle-pool allocator (free list 0x80130BD0, 108-byte
   entries) whose bursts follow explosion events (npcPowerGeneratorHandleDestruction 7-rand cluster) 85-100%; no fixed
   spawn times. Every player hp hit (33/33) is preceded within 0.1 s by an impact effect (randomlyScaledEffectNpcHandler
   0x800606F4 onset); impacts near/at the player per game s are NOT lower at FPS60 (0.82-1.47 vs 1.03-1.14) but the share
   that cost hp halves: 30 Hz 20/187 (10.7%) vs FPS60 22/416 (5.3%). Refutes H-spawn-timer / H-fire-rate; the deficit is
   hit probability per shot (H-lead: enemy target lead uses a per-tick velocity; H-collision; H-splash). Side datum:
   npcWingmanBehaviorByMode 0x800D860C and initActorMotionParams 0x800F28F4 fire every 20 TICKS (0.667 s at 30 Hz, 0.333
   s at FPS60, seed-independent) - a frame-locked cadence. Boot freeze soak s6814_bootfreeze_ab: 10/10 boots clean (5
   preempt on, 5 off), the a30_s2 freeze did not recur (1 in 11 boots).
   s6816 (instrument: tools/fixup_rand_trace.py s6816 rows; g3_bolt_attrib.py, g3_guided_attrib.py; 3+3 seeds, deterministic
   - deaths reproduce s6814): every hp drop 16 s -> death is a 50-hp HOMING MISSILE (guidedEffectNpcHandler -> playerYwingUpdate
   msg -> tickCinematicObjectStateMachine 0x800B1468), 30 Hz 0.114-0.167/s vs FPS60 0.043-0.058/s; bolts never hit there. Turrets
   fire pairs every 3.05 game s (dt-exact) only within ~52 u of the player. The chain starts at a terrain scrape at 15.4 s:
   updatePlayerCraftPhysics 0x800B29F8 takes 20 hp per CONTACT TICK (0x800FEF10 returns 1, no cooldown): 2 contacts at 30 Hz vs
   7 at FPS60 in all seeds, different exit velocity (+z 0.2 u/s) -> FPS60 path ~9 u further +z by 40 s -> fewer turrets in
   range -> fewer missiles. Supersedes s6815's "hit probability per shot" framing.
   s6817 FIXED (main term): 0x800FEF10 is the collision resolver (5 passes/tick); each contact pass rotates the craft by
   K*dt (120/180 deg/s) - a deflection quantum, halved at FPS60. +0xD8..0xE0 are heading/pitch/roll in DEGREES. Fix
   tools/fixup_fps60_scrape.py: case multiplies use max(dt,1/30) under ROGUESQ_FPS60 (=ROGUESQ_FPS60_SCRAPE=0 restores; retail
   untouched). Seed 1 same build: contacts 30Hz 2 / fix 4 / off 7; exit pitch exact; hit50/s 0.107 / 0.094 / 0.057; death
   81.3 / 90.6 / none. s6818 seeds 2/3 CONFIRM (two lines, all 3 seeds): contacts 4 every seed (30 Hz 2, off 7);
   hit50/s(t>16) fix 0.094/0.129/0.059 (mean 0.094) vs 30 Hz 0.107/0.100/0.140 (0.116) vs off 0.057/0.029/0.037 (0.041);
   death fix 90.6/39.3/84.3 vs 30 Hz 81.3/86.2/51.8. Idiom audit (tools/g3_dt_quantum_audit.py --slice, 38 callers / 79
   sites of rotate helpers 0x8001CC3C/0x8001CD6C): K*dt quanta ONLY in 0x800FEF10 (7/7 = positive control); the two
   other dt-arg sites are continuous (npcDeformingMeshUpdate rate*dt spin; updateNpcOrientationFromMotion angle+offset).
   Rotate-helper class CLOSED. 0x800FEF10's callers are updatePlayerCraftPhysics AND updateSplineCraftTransform, so the
   fix also restores the 30 Hz quantum for NPC spline craft. RESIDUAL (tools/g3_scrape_damage.py): scrape hp 30 Hz 40
   (2x20) / fix 80 (4x20: 15.417, 15.6, 15.617, 15.65) / off 140 (7x20) - 20 hp per contact TICK, ticks 1-3 apart.
   s6819 FIXED (residual): the contact branch 0x800B2918..0x800B29F8 has NO re-hit gate (two flag tests only:
   0x80130B4C&0x800000, player +0x184&0x78; consecutive FPS60 ticks 15.600/15.617 both charged) -> H-no-gate; the 20 hp
   (rodata 0x800A5734) is a per-tick quantum. tools/fixup_fps60_scrape.py now scales it by dt*30 under FPS60
   (ROGUESQ_FPS60_SCRAPE_DMG=0 restores). Seed 1 one build: scrape hp a30 40 / fix 40 (4x10) / nodmg 80 (= s6817 exactly,
   death 90.62 both); fix death 93.8 (30 Hz 81.3), hit50/s 0.103 (0.107). Seeds 2/3 queued (s6819_scrapedmg_*).
   Remaining FPS60 difference is path: the extra heading case at 15.6 s (60 Hz surface sampling), pos@40 s z 94.6 vs 77.2. s6820 soaks
   s2/s3: scrape hp 40/40 -> s6819 CONFIRMED all 3 seeds.
   s6820 FIXED: s6815's "20-tick AI cadence" is NPC despawn/re-create churn. 24 NPC handlers despawn an NPC after its range
   test (0x80047D40/0x80047DAC) fails for 21 TICKS (per-NPC counter, slti 0x15); the grid scan re-creates it next frame, so
   edge-of-range NPCs churn every 0.67 s at 30 Hz but 0.33 s at FPS60. tools/fixup_fps60_despawn.py: threshold
   round(21/(30*dt)) in [21,42] under FPS60, dt captured at 0x800FA90C (ROGUESQ_FPS60_DESPAWN=0 restores). Same build lvl14
   s1: TIE re-create 40 VI (30 Hz) / 41 (fix) / 20 (off), creates/s 2.81 / 3.51 / 7.05. Class closed (24/24). s6821: seeds 2/3 CONFIRM (41 vs 20 VI).
   s6821 FIXED (rest of the tick-timer class): tools/g3_tick_counter_audit.py (154 load/+-1/store/test sites; finds all 24
   despawn compares = control) -> 15 hand-read mission timers stepped by game time under FPS60 (tools/fixup_fps60_ticks.py,
   rs64_tick_step = 1/30 s boundaries crossed this tick; ROGUESQ_FPS60_TICKS=0 restores) + ROGUESQ_TICK_TRACE=<file> on all
   109 sites (tools/g3_tick_timer_durations.py). lvl14 s1 one build: advanceNpcOnCurvedPath countdown 0.233 s a30 / 0.100 off
   / 0.200 fix; multiEventTemplateNpcHandler lifetime 0.200 / 0.100 / 0.200. The other 13 whitelisted sites (turret +0x88,
   TIE attachment effect, textured effect, emitter, train car x2, throttle, type-4 effect, TIE orientation, cinematic stage,
   mission transition) did not run on lvl14: static fix only, runtime-unverified. Next: exercise them on other levels.
   s6822 per-level census (FPS60, lvl2-19 bar 14, 150 s): exercised 80044938 (cutscene <5 count-up, all flight levels),
   8007030C (lvl5/8/9/15), 800DAB64 (lvl13/15), 800E1E28 (lvl9/13), 800E32CC (lvl13). lvl13 one build a30/off/fix: 800DAB64,
   800E32CC, 800E1E28 decrement once per EVENT (ex/gs 0.54/0.54, ~1.02 s per step both rates), so the fix doubled them
   (0.73 ex/gs, 3.8 s) -> REMOVED from FIX (UNFIX revert; re-run 0.54 ex/gs, 3.05 s = a30, 8006C024 still 0.250 vs off 0.100).
   80044938 kept (reaches 5 at 0.167 / 0.117 / 0.150 s). rs64_tick_step is 1 outside a mission tick (0x800FADE4 end hook);
   all observed out-of-tick reads were pre-first-tick with step 1, so that change is defensive (second mission load), untested.
   Never hit on any level: 7 sites (turret 800C96B8, 8007CD50, 800806AC, 800B5350, 800BC778, 800F8708, 800FB4F8) - their
   static per-tick reading was wrong for 3/5 exercised sites, so they are SUSPECT. lvl6/11/16/17 never reached flight in
   150 s (still in the intro cinematic: start presses at 6-50 s did not skip it) - recipe gap.
   s6823: static re-read of the 7: 800C96B8 (turret +0x88) and 800806AC (emitter +0xB4) decrement only when a dt float
   interval timer expires -> UNFIX (FIX now 10). Other 5 per-call behind state/button gates -> kept (single-source).
   Presses to 121 s (scratch/s6823/census.sh) get lvl6/11 into flight; 800F8708 ran 8x on lvl11 FPS60 only (a30 arm took
   another path) - unclassified at runtime. Never hit yet: 8007CD50, 800B5350/800BC778 (need +0x1E button held), 800FB4F8.
   s6824 FIXED (FPS60 C-down): config +0x1E = 0x0004 = C-DOWN; the game's button word 0x80130B88 carries it for ONE tick
   per press, so 800B5350 / 800BC778 (+0x15C 0..2 cycle) run once per PRESS (lvl2 a30 2/2, FPS60 2/2) = H-event, and the
   s6821 step (0 on alternate FPS60 ticks) swallowed presses: lvl2 FPS60 16 C-down presses, fix arm 0/13 advanced, UNFIX
   arm 13/13 (0,1,2,...) = a30 (tools/g3_press_cycle.py; tick trace now logs held word + config per tick). FIX now 8.
   Left unexercised: 8007CD50, 800FB4F8, 800F8708 (lvl11 FPS60 only).
   s6825 FIXED + CLASS CLOSED: 8007CD50 (textured effect +0xA0, decrement right after the effect spawn 0x800989D8) runs once
   per emission EVENT every ~3.05 game s per emitter at both rates (lvl17 400 s: a30 92 ticks apart, decrement every
   execution; FPS60 182 ticks apart, about half the decrements dropped by the step) -> UNFIX, FIX now 7. Control 8006C024
   1.9x ex/game-s in the same arms. 800F8708 / 800FB4F8 never ran on lvl14 (LIVES_CAP=1, no death in 240 s), 16, 17 (both
   rates): kept, static-only single-source. lvl16/17 need ~400 s runs (240 s ended ~27 game s into the intro).
   s6826 FLOAT QUANTA (H-some, small): tools/g3_float_quanta_audit.py (597 lwc1-op-swc1 sites) + fixup_fps60_float_trace.py
   (253 per-tick non-dt sites into ROGUESQ_TICK_TRACE) + g3_float_quanta_rates.py (median per-tick |d| f60/a30: 0.5 dt-scaled,
   1.0 quantum; controls updateNpcEventTimer 0.50, int counters 1.00). lvl14: most static STEP rows are dt-scaled upstream (0.5).
   FIXED: guided-motion accel (steerOrientationTowardTarget +0x5C += 0.4, speed += accel) and drop term
   (levelOrientationToReferenceAxis +0x5C) were per tick: accel slope a30 12 / FPS60 24 per game s -> tools/fixup_fps60_float_quanta.py
   k=dt*30 under FPS60 (ROGUESQ_FPS60_FQUANTA=0 restores): fix 12.0 / off 24.0, same-run controls held. Speed-increment part
   single-source (speed sits at clamp).
   s6827 FIXED (same script, same switch): minimalRandomNpcHandler particle scale +0x20/+0x24 *= 1.1 per tick (GROWTH, not
   damping; alpha +0x44 -= 512*dt) -> pow(1.1, dt*30); computeRandomizedOrientationFrame (executeActorType1Effect wobble)
   phases +0x8C/+0xA4 -> step*dt*30. One build lvl14 fix/off: dR (lrR for the scale) 0.50 fix / 1.00 off on all 4, controls
   0.50 (dt) / 1.00 (int) in both; lvl2 a30 vs fix: 0.49-0.51 on all 4, no other site dR>=0.8 with ex x2. Classified benign:
   timeSnapshotFiller 0x8012A8F4 (sample count of a running average). Guided-motion fix still single-level.
   **s6828 MISSION FLOAT-QUANTA CLASS CLOSED.** updatePlayerVehicleByControlMode (0x8004D2B0) integrates speed/position with its
   a1 step dt. Caller trace (ROGUESQ_TICK_TRACE, pc = call site, v = a1) across 5 arms: the 3 destroyEffectObjectTypeNpcSlots
   callers (0x8004F990/FA54/FB24, ~98% of calls) pass the real tick dt (a1/tick dt 1.000 at a30 and FPS60, lvl14 + lvl2) ->
   0x8004D7CC is dt-scaled; its lvl14 dR 1.41-2.59 is direction/path mixing (lvl2 0.50 = control 0x800EFE3C 0.50). The other 2
   callers (releaseEffectObjectNpcSlots 0x8004EF38, ...Variant 0x8004F160) pass a CONSTANT 1/30 (rodata 0x8003A9AC/B0):
   per-tick at FPS60 (off arm lvl14: 3 calls, a1/tick dt 2.000) -> FIXED a1 = 1/30*k in fixup_fps60_float_quanta.py (same
   switch). That fix is static-only: 0 calls in both fix arms (rare path).
   **s6829 HANGAR TILT FIXED.** hangarVehicleDisplayNpcHandler +0x8/+0xC are ship TILT ANGLES (fed to 0x800193E8 with +0x10),
   not a spin velocity as s6828 read it: per call += stick*c, clamp, decay toward 0 by a constant. The handler's a2 (s3)
   points at its frame dt (+0x14 -= *s3): runtime 1/30 in 474/474 a30 calls, 1/60 in 1066/1068 FPS60 calls (H-dt-exists).
   Fix: the 6 add/decay sites scaled by (*s3)*30 in fixup_fps60_float_quanta.py (same switch). Same build, owner save,
   SELECT YOUR CRAFT, stick right 2 s (scratch/s6829/arms.sh, tilt.py): rise-to-90% / settle a30 0.167/0.600 s, FPS60 off
   0.083/0.300 s, FPS60 fix 0.183/0.633 s; plateau 0.0237 / 0.0237 / 0.0244 rad (half-decay sampling, 0.04 deg). +0xC path
   (stick y) static-only.
   **s6830 G1e FPS60 RATE CLASS CLOSED.** s6829 front-end dR~1 rows were mostly analyzer artifacts (no --sites: floats
   read as ints; zero deltas dropped): 80044938 already FIX (net +30/game-s in a30/fix), npcWakeUpdate 80077180/88 dR 0.50,
   guMtxCatF 8002E5A4 = 1.5e-5 rounding, 800B2804 heading += +0x14C (the same addend as +0xD0, which reads 0.51), counters
   0x8011A894 / 0x8013889C = frame-ID stamps (s6256/s6257), 80006FE0/8009C0EC/8009CB00 equal net rate. One real quantum:
   updateSplineCraftTransform (0x800B0A88, the lvl14 player-death sequence, game t 81-121 s) speed +0x140 +-= 2.0/tick
   (clamp +-180; position += speed*dt) and scale +0xE8 *= 1.01/tick -> FIXED k=dt*30 / pow in fixup_fps60_float_quanta.py
   (same switch). Pre-fix: a30 60 u/s^2 (4 runs) vs FPS60 120 (4 runs). Same build lvl14 420 s (tools/g1e_spline_ramp.py):
   fix 60.0 / 0.299 = a30, FQUANTA=0 120.0 / 0.597; control updateNpcEventTimer 0.50. 240 s runs never reach the death.
   **s6831 int |K|>1 step class CLOSED.** tools/g1e_int_step_audit.py 41 sites: 40 not time (heap/DL/pixel strides, JFIF/
   inflate, RSP text, pause-menu layout cursor, audio offsets, tickTextureAnimSlots carry of a dt accumulator). One fix:
   advanceNpcOnCurvedPath +0x1E speed ramp +0x20/tick (clamp 0xFF) -> step x rs64_tick_step() (tools/fixup_fps60_int_step.py,
   ROGUESQ_FPS60_INTSTEP=0 restores). Same build lvl14 (tools/g1e_int_step_rates.py): ramp a30 0.267 s (n=7), off 0.133
   (n=5), fix 0.233-0.258 (n=2). All three G1e FPS60 rate classes (float, +-1 timers, int steps) are closed.
   s6832: soak s6831_intstep_fix_lvl14 (400 s, 0 crash) fix arm up n=7 med 0.250 / down n=8 med 0.250 (min 0.250,
   max 0.267) vs a30 0.267, off 0.133 -> H-fixed (within one 60 Hz tick; H-phase-bias refuted). Owner table of every
   FPS60 fix + its =0 switch: docs/FPS60-FIXES.md (linked from OWNER-OPT-INS). **Owner: judge FPS60 feel.** Queued
   s6832_fps60bundle_lvl1/lvl10_dd4 (300 s FPS60+dd4 holds with all fixes; last such holds predate s6817).
   s6833: bundle holds CLEAN (lvl1/lvl10 FPS60+dd4 300 s, alive, 0 crash, 0 VI stall; 42/55 drawn fps = FPS60 live).
   Static read of the last two kept timer sites: 800FB4F8 is the LIVES byte 0x80130B10[slot] decremented once per
   respawn in tickMissionTransitionAndTeardown (an event; a step of 0 would skip a life loss) -> UNFIX (TICKS FIX now 6);
   800F8708 = 20-consecutive-call state debounce in a dt-aware handler -> kept. Static-only; witness soak queued
   (s6833_lives_fps60_lvl14: lives log via LIVES_CAP=9 + tick trace).
   s6834 witness folded: lvl14 FPS60 400 s, lives 3 -> 2 -> 1 (two deaths) with 0 executions of 800FB4F8 while the
   same trace logged 20.0M records / 16820 ticks (hook present in funcs_42.c, binary rebuilt after it) -> normal hp-0
   deaths decrement lives in requestMissionTransitionMode 0x800FB190; the 0x380000 respawn routine is a different
   (unexercised) death kind. UNFIX stands (it restores retail code); not chased further.
   s6834 boot-freeze hunter: tools/boot_freeze_hunt.sh (N retail boots; fs= stalled 12 s -> two `sample` call trees 5 s
   apart, per-thread guest frames via tools/sample_game_threads.py; boot1 sampled healthy = control; HUNT_SELFTEST=1
   SIGSTOP = freeze-path control, both pass). Queued s6834_bootfreeze_hunt_a/b (22 boots) for the s6814 1-in-11 freeze.
   s6835: hunts a/b 22/22 clean (freeze now 1 in 43 boots). a30_s2 log: last guest output = partitionFramebufferMemory(640,480)
   at fs~40 (fb array switches partitions there); the only blocking code before swapBufferWithViMode is advanceVideoFrame's
   drain loop 0x80018264 (waits until no slot 0x80128EAA is 3/4; the retrace thread 0x8011CD28 moves 4->5 / 3->4 every VI
   under mutex 0x80128D10). Audio flowed -> game thread blocked in an OS call. Hypotheses H-lost-mutex / H-lost-vi /
   H-lost-post. New passive [stall-dump] (default on, fires only on a >=600-VI fullsync stall; =0 off, _VI=<n>, _TEST=<vi>)
   prints slot states + the three queues' waiting threads; controls pass. Hunts s6835_bootfreeze_hunt_c/d queued.
   s6836: hunts c/d 22/22 clean -> freeze 1 in 65 boots; thread PASSIVE ([stall-dump] default on, no more hunts).
   s6836 G3f owner offer LANDED: ROGUESQ_HANGAR_FOV=<deg> narrows SELECT YOUR CRAFT cam 0x800CD670 only (apply_s6836_hangarfov;
   0x800CDC80 = SELECT LEVEL, excluded, crops at 30). Same build: fovy 30 on 1486/1486 craft-cam calls, other cams 45, camera
   path identical; 38 suggested (30 crops wingtips). OWNER-OPT-INS row; sheet scratch/s6836/sheet_craft_fov.png.
2. **G1d close-out awaiting owner judgement** (scratch/s6731/sheet_menus_owner.png; recipe scratch/s6731/menus.sh
   <tag> <aspect|none> "ROGUESQ_LIVES_CAP=1 <env>"). Mission-start dark frame with edge lines = RT64/present path,
   horizontal line fixed s6735, vertical line = source column cw-1 clear colour (s6736).
3. **Owner judgement / parked.** G3c sheets; native hangar geometry and rare dd4/dd8 gfx SIGBUS parked
   (single-source). Reopen on an owner report or a side-effect failure, not repeat holds.
4. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first. NEVER send hull damage
   on level 8 (counter3==1 fails the mission).

## Evidence index

- s6759 maintenance archive (verbatim headline s6689-s6758, superseded s6292-s6673): PROJECT-OVERVIEW.
- [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts: [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); per-level images:
  [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md`; latest 20261103-021659 (s6831_intstep_fix_lvl14, consumed s6832: clean, ramp H-fixed). s6781_menufifo_lvl1_dd1 (20261101-220157) consumed s6782: clean; none new through s6786.
- Recent chronology: PORTING-STATE sessions 6738-6760; search bounded windows only.
