# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 6793 (2026-11-02).
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
  120-cell bypass cap, which drew less terrain than retail most of the time; re-measure on the s6788 bundle.
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
  run: dd4 6 dips / dd3 0 in flight; game fps lvl1 dd4 45.9, dd3 48.2 (dd1 59.9) - the old dd4 "56-60 fps" was partly
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
  periodic dip). Cost: dd4 game fps 44.6 -> 42.8 (visible terrain now actually drawn). Remaining census "drops" are the mission
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

1. **G3 cinematic sweep follow-ups (NEXT: g3-cinematic-sweep).** s6792 all 81 AT THE MOVIES shots pair with retail;
   s6794 sky seam fixed (exact-edge fan). s6795 TRI shots 48/64 CLOSED = frame weighting (tools/g3_cine_tri.py).
   s6796 CLOSED (H-same): the exact-edge fan does not touch source column cw-1. Same-run ROGUESQ_EXACT_EDGES=tog,
   EDGE_CONTENT=0, lvl1 4:3: sky edge column off 26/44 (59%, pos ctl vs s6736 ~69%) vs on 31/47 (66%), identical
   right-edge blue profile, 0 new columns; [g1d-reach] still max_tri_x1 = cw-1.00. The EDGE_CONTENT crop stays correct
   with EXACT_EDGES on. NEXT = s6794 "not checked": hangar/menus seams + fan tri/frame-time overhead under EXACT_EDGES=tog.
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
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md`; latest 20261101-202615 (s6775 arms, consumed s6776: clean; none new at s6781). s6781_menufifo_lvl1_dd1 (20261101-220157) consumed s6782: clean; none new through s6786.
- Recent chronology: PORTING-STATE sessions 6738-6760; search bounded windows only.
