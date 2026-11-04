# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 6866 (2026-11-03).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md` (latest archive: "Migrated from CURRENT-TRUTH (s6847 maintenance)").

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

## Superseded conclusions — do not act on these

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
  collision (s6789); dd>1 defaults now BYPASS_MAXCELLS=-1 + UCODE_CAP=1048576; post-fix lvl5/lvl10 FPS60 dd4 300 s, 0 drops.
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
   **FIXED s6860: lvl10 HUD unanchored at wide aspect.** Ring + left icons stayed in the centred 512 px; only the frame sheet showed it. ORIGIN: s6161 reticle
   exemption (vp 0x80138D20 elem < 0x80300000) caught the heap HUD table, which sits at 0x8028FDxx on lvl10 (0x805623xx lvl1); reticle is static 0x8010CA58/88.
   Bound now 0x80110000 (tools/apply_s6860_hudelem.py, ROGUESQ_G1D_HUD_ELEMTOP=1 = old). Same build: ring 647 -> 903, icons 313 -> 57, equal to lvl1;
   sheet docs/owner_sheet_s6860_lvl10_hud_ab.png. Post-fix lvl10 + lvl1 (+ lvl16 route). Counters do not cover HUD placement: score frames (scratch/s6860/ring.py).
   **FIXED s6861: flight HUD jumped to the centred 512 px while the pause menu opened and closed, all levels at wide aspect.** The s6860 "lvl16 paused window" is the
   real pause menu (harness START), not a race intro. ORIGIN: our s6721 gate treated pause byte HUD+0x258 as a flag; it is a state (initOrUpdatePauseScreenDim: 1 opening,
   3 open, 2 closing). Text links only at 3 (0x800C3A88), HUD draws through 1 and 2 (~20-55 swaps each). Gate now state 3 only (ROGUESQ_G1D_PAUSE_GATE_MASK, default 8,
   14 = old); dim follows any non-zero. Disc in 1/2: backdrop tiles and logo tris are also z-off in the box, so only textures selected in flight shift. Same build mask 14
   vs 8; lvl16 21:9 + 16:9, lvl1 pause + abort clean. Residual: a pause before any flight frame leaves the disc centred (harness only). docs/owner_sheet_s6861_pause_hud_ab.png.
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
3. **G1d close-out awaiting owner judgement** (scratch/s6731/sheet_menus_owner.png; recipe scratch/s6731/menus.sh
   <tag> <aspect|none> "ROGUESQ_LIVES_CAP=1 <env>"). Mission-start dark frame with edge lines = RT64/present path,
   horizontal line fixed s6735, vertical line = source column cw-1 clear colour (s6736).
4. **Owner judgement / parked.** G3c sheets; native hangar geometry and rare dd4/dd8 gfx SIGBUS parked
   (single-source). Reopen on an owner report or a side-effect failure, not repeat holds.
5. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first. NEVER send hull damage
   on level 8 (counter3==1 fails the mission).

## Evidence index

- s6847 maintenance archive (per-mission G3 bullets, closed s6788-s6846 next steps): PROJECT-OVERVIEW.
- s6759 maintenance archive (verbatim headline s6689-s6758, superseded s6292-s6673): PROJECT-OVERVIEW.
- [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts: [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); per-level images:
  [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md`; latest 20261103-104942 (s6852_zgate_lvl9, consumed s6853). None queued.
- Recent chronology: PORTING-STATE sessions 6788-6846; search bounded windows only.
