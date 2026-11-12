# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7210 (2026-11-12).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7186 text of this file (every s7047-s7186 headline paragraph
with all numbers, the long item-6 dd chronology, closed items 11-42 in full) is archived verbatim in
PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7187 maintenance)"; older text in "(s6994 maintenance)".
Grep there for any sNNNN.

## Headline

**G3 render fidelity is H-equal everywhere scored (s7122-s7188).** RT64 == angrylion to the retail
floor at retail 4:3 (flight L0-L18 s7180, menus/cutscenes s7181-s7185), owner recipe 16:9 (flight L0-L18
s7164, menus s7142-s7156), 21:9 (flight L0-L18 s7173, holes s7132-s7140) and fullscreen 16:9 (s7186:
menus 0.004-0.019 native frac, L6 flight 0.0037) and ASPECT=auto fullscreen (s7188: fb 712, menus 0.004-0.023,
L6 flight 0.0064). The 1 undrawn right column on 339-row menus is retail (s7189). The only large residuals anywhere are the deliberate ROGUESQ_W_SHEET_PX / W_SHEET_POS
guard-band sky-sheet culls (s7125, s7127-s7130).
- In plain words: at every setting checked, the renderer draws the same picture as an accurate N64 model.

Fixes from the G3 series, all default on (=0 restores the old path):
- **FBW_ALIGN (s7188):** non-standard aspects (auto) round FB_WIDTH to a multiple of 4 (713 -> 712): the odd width
  left 2 undrawn right columns on the 339-row menus (game scissor xh 711) and an unaligned 1426 B stride. 796/1024 unchanged.
- **RECT_ASPECT (s7142):** RT64 scaled 2D texrects 1.33x when the scissor matched the VI fb ratio; fixed.
- **HORIZON_XFIX / GATEFIX / SKYFILL (s7133-s7136) + SKYFILL_BOT (s7166):** 21:9/16:9 sky holes; no-op at 4:3.
  L6 zero-height top-fade skirt is retail (s7138).
- **W_SHEET_POS (s7130):** drops all-W-positive hairline wedges from guard-band corners; pixel-checked both arms.
- **G5B_FRAME recorder after the radar-disc shift walker (s7125):** the old ~1000 px "HUD diff" was the recorder.

Engineering closed s7066-s7098 (detail in the s7187 archive): one cached getenv for the image (s7066,
ROGUESQ_ENV_CACHE), dladdr cache (s7067), diag call-site gates (s7068/s7069), Gfx hash/memmove = RT64 fb
tracking (s7070), N64Recomp self-branch miscompile fixed (s7081, tools/fixup_selfbranch.py), lowering /
host-shim / fixup / RSP censuses (s7082-s7095, rerun after any regen), DPC bridge forwards exactly the
hardware RDP stream (s7096) and every in-flight edit is one of our walkers (s7097), big G5b drops are
already in the RDP stream (s7098). Scene-transition stalls are the retail 3072-sample MusyX wait, ~139 ms
(s7065). Near-wall flicker is retail eye-cell near-plane loss (s7109); opt-in NEARLIFT k1.6 removes it (s7118-s7121).

dd6 21:9/16:9 auto bundle (s7037-s7063, detail archived): off-map cull past 0.6 x fog end, KEDGE=0.8,12,
WIDEWIN cap 10240, auto KLEVEL `12:0.5,13:0.5` and CAPLEVEL `9:8192` when FB_WIDTH>796. All 19 levels
hold ~60 fps in flight with 0 crashes at 21:9 (s7063) and 16:9 (s7043). Cap 12288 is an opt-in (+0.25 ms
rsp, +2-5 L4 shoreline rows); cap 9216/8192 and K0.5 globally shave a horizon somewhere (refuted as defaults).

Open or awaiting the owner:
- **s6992 FIXED, default on: L15 21:9 dd4 crash.** The game's 7-site pointer test
  `(p & 0xFF000000) == 0x80000000` rejected the 0x81000000 spill arena. tools/apply_s6993_ptrmask.py,
  ROGUESQ_PTRMASK=0 = retail mask.
- **G1e:** 60 fps in flight on all levels (s6996; use fl_shown). Latency chain closed s6962-s6989:
  defaults VI_RT, STDERR_ASYNC, G1E_CELLIDX; opt-ins VI_LOCK=1, QOS_ALL=1. Owner decides QoS default.
- **Boot freeze (1 in ~65 in s6993; 0/41 in the s6993 env s7190-s7191):** s6993 [stall-dump]: retrace thread 8011CD28 blocked
  on a FULL send to 0x80128CF0, vflag 0, no receiver. s7191 static census: all live CF0 receivers balanced (mode-2 leak dead), so the
  state needs a receiver delayed >=2 VIs before its clear that then waits elsewhere (H-consumer). [stall-dump] now prints
  [stall-wait] (each guest thread's current blocking mq + recompiled caller) and [stall-cf0] (last 48 CF0 events), default on.
  s7192 forced arm ROGUESQ_CF0_DELAY_TEST=600:40|100 builds that exact pre-state on demand (retrace on CF0 fullq, vflag 1) and
  it heals 10/10 (H-stale-heals): the freeze needs tid 3 blocked on a SECOND queue whose producer depends on retrace (cycle).
  s7193: waitForPostSwapAck exits when the retrace thread's postSwapRdpReset clears 0x8011A8C8, so a slow vflag clear produces the
  s6993 state by design; 120 forced retrace holds (ROGUESQ_RETRACE_HOLD_TEST) at every boot phase always park tid 3 back on CF0,
  never on 8011A7E8 or another retrace-fed queue -> H-cycle refuted; the post-clear yield is host std::this_thread::yield (cannot lose
  tid 3). PASSIVE now: [stall-wait]/[stall-cf0] + host sample name the second wait on recurrence. 0 freezes in 73 owner-env boots.
  s7194: separate runtime hazard fixed, default on: external messages to a guard-refused mq are dropped, not requeued forever
  (v1 arm 5/5 FROZEN old path -> 5/5 OK fixed). s7195: BLOCK recv on a refused mq parks instead of spinning (3/3 FROZEN -> 3/3 OK). s7196: busy-poll class CLOSED (docs/COOP-SCHED-POLL-CENSUS.md: no guest-produced
  NOBLOCK poll; both real spins wait on higher-priority producers). Fixed, default on: a PI DMA to an unknown region now posts its
  completion (ROGUESQ_PI_UNK_TEST=400 old 3/3 FROZEN with piDmaWorker IN recv 80111290 -> fix 3/3 OK). 0 freezes in 100 owner-env boots.
  s7197: host completion-delivery class CLOSED (docs/HOST-COMPLETION-CENSUS.md). One HAZARD fixed, default on: the AI drain
  thread never posted once SDL stopped pulling (paused/disconnected output), so guest audio tasks stopped for good (forced
  ROGUESQ_AI_STALL_TEST=15: old 2 audio-task rows after, fix 578, ctl 0 fallback fires). ROGUESQ_AI_STALL_POST_MS=0 = old. Not a freeze.
  s7198: resume after a stall recovers by itself, but the stuck-device backlog replayed as stale audio (+87 ms per paused second;
  20 s pause -> 1.76 s). ROGUESQ_AI_BACKLOG_MS=150 trim, default on (=0 old): 52 ms at resume, normal <1 s, 0 trims in normal play
  (peak queue 36 ms boot/attract; in-mission soak s7198_backlog_L4: 0 trims, peak 36.1 ms over 374 s).
  s7199: output hot-plug fixed, default on (ROGUESQ_AUDIO_HOTPLUG=0 = old). A REAL CoreAudio removal (tools/audio_hotplug_agg.c
  creates/destroys an aggregate output) left the named route dead for good (13 bufs/s, trims every ~3 s). Now the audio
  thread reopens on SDL_AUDIODEVICEREMOVED for our id (ids kept as a bitmask: SDL3/sdl2-compat posts our id then id 0),
  or on a 400 ms drain-stall watchdog (status stays PLAYING after removal), falling back to the system default, and moves
  back when the preferred device is ADDED. Real arm: 0 trims, 115 bufs/s through the removal; pause/ctl arms 0 reopens.
  s7200: default route needs nothing: removing the macOS DEFAULT output, SDL3 migrates the stream itself (hotplug=0 arm
  also 115 bufs/s, 0 trims; one 93-buf second at the switch); the handler stays idle (0 reopens). Audio host thread CLOSED.
  s7201: pad hot-plug fixed, default on (ROGUESQ_PAD_HOTPLUG=0 = old). Removing the open pad left input dead for good even
  with a second pad connected (only an ADDED ever opened a pad). Now the first remaining game controller is adopted on
  REMOVED (or on a silent detach). Forced arm ROGUESQ_PAD_HOTPLUG_TEST=<sec> (two SDL virtual pads, P1 detached): old 24 s
  of btn 0 after removal, fix 24 s of P2's word 0x4000, ctl P1 0x8000 throughout. No latch on the old path either.
  s7202: display hot-plug fixed, default on (ROGUESQ_DISPLAY_HOTPLUG=0 = old). Real display removal (tools/virtual_display.m,
  CGVirtualDisplay): fullscreen old path stayed fullscreen in a hidden Space (0 frames on screen for 18 s), now leaves and
  re-enters fullscreen on the remaining display (30/s on screen within 2 s); windowed move to a 2x panel left RT64 drawing a
  quarter-size image (plume needsResize checked points only), now resizes when the layer drawable is stale. Built-in control
  0 extra resizes. [g1f-win] logs window/Space/layer state after any display event. Next: Retina render scale (below).
- **s7203 Retina render scale: opt-in ROGUESQ_RETINA=1 (owner decides default).** plume ran its swap chain at the window's
  POINT size (PLUME_APPLE_RETINA_ENABLED OFF), so a 2x panel got a half-size image upscaled by CoreAnimation (H-half selected;
  H-resmult-covers refuted: RT64's internal 4x/960 rows still reach the panel through a 764-row swap chain). Runtime switch in
  plume_apple.mm getScaleFactor; [retina] swapchain create row is the witness. Built-in: win 1360x764 -> 2720x1528, fs
  1512x949 -> 3024x1898 (internal WindowIntegerScale 4x -> 7x/8x); half-resolution residual score (scratch/s7203/hf.py)
  0.577 -> 0.779 win, 0.584 -> 0.839 fs; positive control (R1 frames down/up 2x) 0.537 = the R0 level. GPU median
  0.27 -> 0.48 ms win, 0.29 -> 0.57 fs (attract, 30 pres/s), 0 crashes, layout identical. 1x virtual display control:
  1920x1080 and 0.35 ms in both arms. Hot-plug 1x -> 2x with RETINA=1 resizes to 2720x1528.
  s7204 flight cost at the owner recipe (FPS60 dd4 16:9 fullscreen, quiet host, L4 + L6 x2): H-free selected. fl_shown 59.9/60.0/59.5/60.0
  (R1) vs 59.9/59.9/59.8 (R0), GPU median +0.05-0.13 ms (0.41-0.44 vs 0.28-0.36), p95 <= 0.90 ms, 0 gaps > 250 ms, 0 crashes in 6 arms.
  The one 92-gap arm (L6r1) was an 8 s non-flight screen (VI origin B517C8) where the game itself updates at 20/s in both arms;
  the replicate L6r1b skipped it and showed 2 gaps. Scorer tools/s7204_ring_cost.py.
  s7205 flight sharpness (LEVEL=4 owner recipe, 6 timed shots per arm, scratch/s7205/scores.txt): H-sharp selected on fixed HUD crops
  (badge 0.567 -> 0.815, icon 0.542 -> 0.727, radar 0.418 -> 0.778; positive control R1 down/up 2x = 0.539/0.402/0.374, the R0 level)
  and visually (radar ring and ticks crisp). Ground texture 0.653 -> 0.734 (camera pose differs between arms, so scene-confounded).
  Owner sheet docs/owner_sheet_s7205_retina.png. **Awaiting the owner: make RETINA=1 the default?**
- **s7206 interlaced stills fixed, default on (lib/rt64):** the title / backdrop stills are interlaced double-stride VI (width 1592,
  fb 796 cols B51E00, origin B52438). VI::fbAddress() subtracted a 1592-col row -> B517C8, so early present never matched the
  current VI (presented 20/s on VI changes only), or matched a leftover zero-height VI-history entry and presented 60/s through it
  while dropping the real presents (the s7204 R0-only datum; timing, not Retina). ROGUESQ_VI_ILACE_ADDR=0 / ROGUESQ_PE_STALEFIX=0
  restore the old paths. f1: 60/s through the current VI, picture pixel-identical to old (shift-0 diff 0.00), flight 59.3 shown/s both.
  s7207: H-motion selected at 16:9: title / fade / SELECT GAME stills show 58.6 distinct images/s (f0 20.1), the game renders 60/s in
  both arms (ring W), and the steps are 3x finer motion, not field shimmer (tools/s7207_distinct_by_vi.py, s7207_motion.py). 4:3 Elite
  Rogues (also double-stride) now presents through 790000: G3 kit frac equal within the slideshow-phase confound (matched phases
  0.0313/0.0323, 0.0630/0.0650; single-source), no distinct-rate change (~50/s).
- **s7208 4:3 double present fixed, default on (lib/rt64, ROGUESQ_PE_DEDUPE=0 = old):** the s7207 pairs were mostly the 4:3 boot logos
  (and menu transitions), not Elite Rogues itself (30/s, 0 pairs). updateScreen's needStaticPresent fired on every VI through the
  `last-drawn fb == 0x790000` and `static VI > 2` terms while early presents were already showing every workload, so a VI-path present of
  the same image landed ~2.5 ms before each next early present. Those two terms now count only after 8 VIs without an early present,
  like the s6885 width term. Same session, both arms (tools/s7208_present_pairs.py, s7207_distinct_by_vi.py): 4:3 ER route pairs
  1376 -> 4, presents 8314 -> 6165, distinct images 5730 -> 5799 (boot logos 537/1096 -> 536/565 distinct/presents); 16:9 fullscreen
  boot stills unchanged (B51E00 58.7 distinct/s both, pairs 1 both). 0 crashes in 4 runs.
- **s7209 4:3 Elite Rogues field screen CLOSED (H-prog):** RT64 ignores the Set Scissor field bit (scissorMode read only by the
  debugger), so it draws every row: presented == angrylion NOFIELD progressive replay (G picked 121/122 where G != W, offset 0, row-symmetric,
  synthetic-G control 122/122), not the retail weave (which combs on fades/scroll). Design difference, cleaner than retail; no fix.
  Kit: frame_replay NOFIELD=1, tools/s7183_parity.py GDIR=. (16:9: crop replays to the band and run tools/s7210_regfit.py first.)
- **s7210 field-mode census CLOSED (H-more-prog):** over the whole owner-recipe 16:9 route (boot -> menus -> L17 -> MISSION FAILED -> ER x2,
  14912 swaps, 86456 scissors; tools/s7210_field_census.py) only two screens set the Set Scissor field bit, both B51E00/796, band 142-654,
  even field only: the boot title stills (swaps 626-1649) and the Elite Rogues list (twice, 461 swaps each); a second run found ER again
  (456 swaps). At 16:9 ER presents progressive like 4:3: PROG picked 119/121 where it differs from the weave (offset 0, rows symmetric,
  synthetic-G 121/121, bob/weave controls PASS). TRAP: score only after tools/s7210_regfit.py; a rect ~4 native rows off made BOB "win".
  Datum (single-source): the 1360x796 window shows native rows 0-443 of ER; rows 444-447 are near-black.
- **G5 owner items fixed, awaiting the owner's flight/look:** G5a s6893, G5b s6896-s6901, G5c s6902,
  G5d s6903, G5e s6904, G5f s6906, G5g s6907, G5h s6908-s6919, G5i s6995. Final-mission dd>1 heap crash
  fixed by OSMEM_MB=12 at dd>1; DL chunk arena reclaim s6909.
- **Wide/aspect fixes default on:** G1D_SHOWROOM, G1D_340PERSP, G1D_INTROSHAPE / W640 / SCISSOR_TOL,
  notch safe area + VPW_SCALE, WIDE_LOGQUIET, WIDE_UNDRAWN (s6924-s6932).
- **Opt-ins, owner's choice (default off):** VI_SHAPE (owner 2026-11-08: stays opt-in, no further work),
  DD_MELT, DD_SKYZ, DD_CUT_LIVE, HANGAR_FOV, G5G_LENS, NEARLIFT, WIDEWIN cap 12288. Owner ran MELT, SKYZ,
  VI_LOCK, QOS_ALL and reported nothing wrong (2026-11-08).
- Save guard: runner.sh exports ROGUESQ_NO_SAVE_WRITE=1 and snapshots build/saves to
  ~/Documents/RS64-save-backups/auto. Never touch the owner's save (profile "ASS").

## Closed work, summarised

Detail: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s6900 / s6994 / s7187 maintenance)".
- **G3 retail match** (angrylion oracle): boot, attract, hangar, crawl, intro, missions 1-19, front-end
  at RDP level, AT THE MOVIES 81/81 (s6784-s6792); G3 presented-frame fidelity matrix s7122-s7186 (headline).
- **Default-on fixes from that sweep:** UCODE_CAP 65536 (dd>1 1048576), MENU_WORKER_FIFO,
  EXACT_EDGES, exact-ns VI deadline, LLE_FORCE/UNGATED/SOLO, audio_device_mutex.
- **G1e rate:** s6696 getenv, -O2, RSP work s6713-s6775, FPS60 classes s6828-s6831 (docs/FPS60-FIXES.md).
- **G1, G1c, G1d, G1f, G3c, M5, M3, M6, G2, renaming (s6868, misnomers s7072-s7080): closed.** G1(d)
  objectives and G4 crash hunting parked by owner. dd4 is the ceiling that adds terrain at 4:3
  (docs/DRAW-DISTANCE.md); dd6+bundle is the max useful wide step (s7037).
- **Wide + dd span class (s6879-s6885)**, width class (s6848-s6861, docs/G1D-WIDTH-CENSUS.md),
  spill arena (s6858) + heap audit (s6862, docs/HEAP-ADDR-AUDIT.md; missed the s6992 mask class).
- **Regen (s6863-s6881):** replay from pristine compiles/links/boots; live tree NOT regenerated (docs/REGEN-VERIFY.md).
- **Present thread (s6884-s6891, s6931):** SCREEN_JOB, PRESENT_INFLIGHT, PRESENT_DRAIN opt-in/off.

## Superseded conclusions — do not act on these
- s7180 "swaps 4700-5028 of the L17 route are the level-description screen" and s7181 "Elite Rogues 0.047, 21 >0.05". Believable: 512x448 interlaced fb after MISSION FAILED. s7183: it is the Elite Rogues list; the residual is the fb-weave reference combing while it scrolls.
- s7122 "RT64 shows the 4:3 picture off-centre (21/66 px margins)". Believable: rect search on the capture fit well. s7123: SCK pads the right of the capture; in window points the margins are 43/45 (centred).
- s7120 "the flight camera sometimes jumps 2-16 u in one frame (open flight, both arms)" and "the lift arm has more >1.0 u jerks". Believable: t/t+1 pairs of equal size, far from any lift, in all runs. s7121: the join in s7119_hop mixed cam objects 458/A28/930; per-cam the flight cam has 0 such steps and the cut cams' stray tick is never presented.
- s7113 "H-raymiss CONFIRMED: the collision tests a surface up to ~0.2 u off the drawn mesh; H-gap refuted". Believable: two-pose static control agreed to 0.002-0.004 u and lattice snap fitted. But a common-mode error (fitted P00/P11, corner-frame basis) passes a two-pose test; s7114 exact surfaces from the shared bytes show the rebuild biased +0.07..+0.18 p50 (p90 to +0.52) where drawn == collision exactly.
- s7113 "the drawn mesh is displaced from the collision grid (0.042 off lattice)". Believable: same rebuild. s7114: TriGen and the sampler read the identical 25 bytes on the same lattice; the only real divergence is LOD decimation (flags in mesh+0x14), and removing it does not change the loss rate.
- s7098 "the near-wall flashes only appear with the 60 fps mode on". Believable: presented-episode counts leaned FPS60. At stream level the eye-cell near clip occurs at the 30 fps rate (s7108) and at full retail settings at the same rate (s7109, 17.4 vs 15.9 per hug-min).
- s7102 "the near-wall zig-zag is the corner push and the y clamp fighting (H-fight)". Believable: the one episode caught flipped push/all-miss/push at 105/1000 ticks. Over 5 more episodes (s7102 r1/r2) 2 had 0 flips, and in s7103 a fix that re-pushes after the clamp left the episode rate unchanged (5/2714 off vs 5/3738 on).
- s7100 "FPS60 near-wall episodes are 4.1x more frequent per tick (p=0.033)". Believable: 4 same-run splits agreed in direction. Two more runs (s7101 A, C) bring it to 1.6x, p=0.185; the excess is unproven. Also s7100's "push-out tuned for dt 1/30": the s7101 push-out has no dt.
- s7059 "transition stalls are mostly the game thread polling isAudioSlotActive/anyAudioSlotActive". Believable: 209/298 game-thread xctrace
  samples in stalls were audio polling. s7064's slot ring timed the waits directly: 25-66 ms per 200-335 ms gap (~14%); the sampler saw only
  ~30 samples per stall, so the off-sample remainder (game thread OS-silent 133-150 ms) was never attributed.
- s7032 "at poses 0-4 the craft flies below the plateau top, the wall face occludes it". Believable: by eye the dark wall stays in view and R=2
  only trims its top sliver there. s7033 read the clamped edge cells' heights in the game's own units: the eye is above them on ~99% of culled cells,
  so height occlusion does not explain the invisibility at poses 0-4.
Recent only; older entries: PROJECT-OVERVIEW "(s6994 maintenance)", "(s6900 maintenance)", "(s6870)", "(s6759 maintenance)".
- s7009-s7013 "WIDEWIN costs ~10-25 fps / VI cliff at 6144 / owner fps trade" (s7014): every arm ran the harness's LOG_PHASE
  probe path (main ucode TU, FAST off). Believable because the toggle split was same-run and self-consistent; the absolute level
  was the debug path's. Owner path: 59-60 fps at 8192. Any harness timing number since s6713 without G1E_FAST=1 PROBES=0 is suspect.
- s6895 "clamp on raises small transients at dd1, 306 vs 157" (s7003): old area-drop rule; under the current rule on is half of off.
- s6901 "ring 7 empties near diagonals" (s7001): dips are on axis headings, edge stepping at 56 cells; the guess was never measured.
- s6993 "H-level-cost: dense levels 7/16/17 run 56-58.5 fps" (s6996): whole-window shown/s counted menu/restart screens; in flight they hold 59.7-60.
- s6990 "60.0 fps on all 19 levels at 16:9" and s6962 "LEVEL=4 58.5, LEVEL=10 60.0" (s6991):
  FORCE_UNLOCK=1 clamps the cursor to level 1, every arm flew level 1. Check `cur` / cursorMask.
- s6991 "21:9 selects a 2000-slot texture table" (s6992): read after the corruption; it is 2048.
- s6984/s6986 VI-phase framing of lates (s6987): the chain picked the next frame's kick; R->W is the late term.
- s6968 "VI_LOCK alone cuts latency" (s6969): the gain is LOCK + ACQ8.
- "Port 4:3 presentation has retail shape" (s6928): retail spans 640 dots for 512 columns.
- s6918 "cutoff inputs match retail" (s6919): sampled after the game's write, before our overwrite. Sample at the reader.
- s6894 "no gap over 250 ms" via capture gaps (s6902): use tools/g5c_frozen_runs.py or [g1b] sd_wall max.
- s6901/s6810 "dd4 ~59 fps" applied to 16:9 (s6902): that was 4:3.
- s6788-s6791 "G3e drops CLOSED" (owner 2026-11-04, reopened as G5b): detector missed the owner's drops.
- s6895 "dd1 has no knife lines" (s6906): dd1 has the thickest, 29 vs 1 same run.
- s6791 "camera slides while yaw lags" (s6907): those floats are view translation, not position.
- PORTING-STATE line 1862 "Fog contributes nothing" (s6904): true only of the early pre-flight scene.
- g3_aspect_crop scores s6879-s6881 scored pillarbox bars; "pinned pose" s6445-s6583 is attitude-only;
  "300 s hold" FPS60/dd>1 s6774-s6862 counted from boot (use inits= and flight_s=).

## Run recipes and hard config

- Run from `build/` with the ROM beside it; SIGKILL to stop; one game run at a time.
- Disk is ~20 GB free: a 960x540 g5b_capture is ~9 GB/min (s7002 filled the disk at 125 s). Keep captures <= 90 s, delete raws after scoring.
- Pinned dd4 lvl1 run: `zsh scratch/agent/s6549_run.sh <dd> <poolx>`. G5 arm template
  `scratch/s6899/arm.zsh`; scenes `scratch/s6908/arm.zsh` (EARLY_N=13, FL_START past the scene).
  Hangar camera arms: `scratch/s6907/arm.zsh`, log ROGUESQ_G5G_CAM=<file>, score tools/g5g_pan_score.py.
  Per-level owner-recipe fps: tools/g1e_owner_quiet_arms.zsh (sets FORCE_UNLOCK to the level; check `cur`).
- dd4 needs no DD_UNSAFE (s6582); higher uses DD_UNSAFE (clamp 8). Confirm run.log echoes `multiplier N`.
- lvl10/15 need `ROGUESQ_FORCE_PLANET_UNLOCK=0xFF`. L10 flight is cloud with no terrain grid (s7000). Wide soaks need `MISSION_WIDTH=796|1024` +
  `WIDE_ROUTE=1`; ASPECT implies `OSMEM_MB=12`.
- Pose control: `ROGUESQ_POSE_LOCK=1` + `ROGUESQ_POSE_FREEZE=<x,...>:<ms>` (needs RAND_TRACE +
  DEBUG_WRITE; tools/g3_optin_pose_arms.sh, PIN=1 pins dt). Port dt pin:
  `ROGUESQ_XTRACE_POKE=800FA730:29:30:3d088889` (oracle RS64_XTRACE_POKE).
- Timing: any ROGUESQ_LOG_* turns FAST off and PROBES on: set `ROGUESQ_G1E_FAST=1 ROGUESQ_G1E_PROBES=0`.
  Per-frame meter `[g1b]` (sd_wall, tasks/s).
- Present rings (ROGUESQ_PRESENT_RING): check tools/g1e_present_cadence.py first; at=0 throughout
  is not a measurement; the window must be partly visible (ROGUESQ_WINDOW_POS). Late-present
  positive control: load generator scratch/s6982/burst.
- g5b_capture is sRGB at source since s7151 (.cs sidecar). Raws captured before s7151 are Display-P3 untagged: score them with FID_P3=1.
- Freezes: stalls = [g1b] sd_wall max; image freezes = tools/g5c_frozen_runs.py on a g5b_capture
  .raw; `sample <pid> <s> <ms>` costs no build.
- AT THE MOVIES shots by run time (dd1 16:9): 76 887-912, 77 912-924, 78 924-942, 79 942-952 s.
- Frame comparison: window captures are Display-P3, convert to sRGB; port RDRAM fb dumps lack
  RT64 3D frames; score menus by RDP (tools/g3_rdp_frame_match.py, tools/g3_menu_pair.sh).
- Oracle missions: tools/g3_eep_patch.py sets +0x31; use --save-dir, never swap a save over the
  user .eep. Do not re-run mission-3 flight.
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` / `crashlines`, never rc.
- Knob tables: PROJECT-OVERVIEW "G1c draw-distance knob and recipe reference";
  docs/DRAW-DISTANCE.md; owner commands docs/OWNER-OPT-INS.md.

## G1 mission coverage

Playable levels 0..18 (`NUM_LEVELS=0x13`); 19/20 are sentinels. All have route, 300 s holds and
framebuffer presence; level 1 has a retail flight match; objective response (d) parked by owner.
See docs/G1-FRAMEBUFFER-COVERAGE.md and docs/G1-OBJECTIVE-RESPONSE.md. Never send hull damage on
level 8 (counter3==1 fails the mission).

## Durable constraints
- Never end a turn to wait on a run: foreground (timeout <= 600 s) or queue a soak (s6865/s6866).
- Retail defaults stay unless the owner chooses; never make an opt-in default from a single source.
- Crash-free holds do not mean "renders correctly" (s6468). No mitigation without naming the
  writer; dd>1 fixes live in `tools/apply_s6*.py` (registered in RS64_REPLAY only, docs/REGEN-VERIFY.md).
- Any guest pointer the game range-tests must sit where its test accepts it: 0x81000000+ fails
  `(p & 0xFF000000) == 0x80000000` unless ROGUESQ_PTRMASK (s6992). Re-check this for any new arena.
- Never reset, clean, checkout or update submodules; after editing `lib/` run
  `./submodule-patches/export.sh` and commit.
- Controls: get_n64_input is the pre-6ed036b97 mapping; no changes without an owner request.
- Title plume parked; reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams. Positive control for
  every null; two independent lines before a conclusion enters this file.

## Next steps (single monotonic backlog)

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7187 into one sequence; the s7186
numbering (1-43) is in the s7187 archive. Active unit: NEXT.md.

1. **(next, NEXT.md) 16:9 vertical crop check:** s7210 fit says the 1360x796 window shows native rows 0-443 of a 448-row
   screen. Is that every screen at 16:9 windowed/fullscreen (flight HUD bottom rows), retail VI range, or window rounding?
   Retina default: owner (s7205). Boot freeze stays passive (headline).
   Hunter `env HUNT_OWNER=1 HUNT_CONTROL=1 zsh tools/boot_freeze_hunt.sh <out> N 34 12`.
2. **G5i hangar re-entry: fixed s6995, owner look.** Route scratch/s6995/arm.zsh; tools/g5i_pan_metric.py.
3. **G5a Gerrard V (LEVEL=4) crash: fixed s6893, owner re-flight** past half way, repeated (s6998 writeback audit clean).
4. **G5b terrain drops: owner flight.** FWDWIN far-loss fix holds L1/L4/L5/L7 (tools/g5b_fwdwin_seamless.py).
   LEVEL=10 is cloud (no terrain grid): never use it for terrain measures.
5. **G5c freezes (s6902), G5d logo (s6903): owner flight / boot.**
6. **G5e fog (s6904): owner look.** 21:9 far slab: DD_MELT takes it to the dd1 floor (s7007). Residual side
   edge = the 64-column terrain window (s7008); WIDEWIN (N=128 at 0x83000000) widens it, free at 21:9 dd4
   on the owner path (s7014-s7015). dd>=6 cost is per cell (s7019-s7029); the off-map bundle pays for it (headline).
7. **G5f knife lines (s6906): owner look.** Sheets docs/owner_sheet_s7005_g5f.png, s7006 (21:9).
8. **G5g hangar lens (s6907) / G5h cutscene background (s6908-s6919): owner look.** Sheet docs/owner_sheet_s6907_lens_elsewhere.png.
9. **L15 21:9: owner re-flight after s6992 PTRMASK.**
10. **G1d close-out: owner judgement** (scratch/s6731/sheet_menus_owner.png). Also owner scope: why
    L7/L16/L17 autopilot holds cycle the backdrop menu.
11. **Near-wall flicker: retail (s7109); opt-in NEARLIFT k1.6 removes it (s7118-s7121); owner look.**
12. **G3 21:9 holes (s7132-s7140) + L4 cutscene SKYFILL_BOT (s7166): owner look.** Sheets docs/owner_sheet_s713[69]_*, s7140, s7166.
13. **Owner judgement / parked:** FPS60 feel, G3c sheets, QoS default, native hangar geometry, rare
    dd4/dd8 gfx SIGBUS (single-source). Reopen on an owner report or side-effect failure.
14. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first.
15. **Rerun-after-change censuses (all CLOSED, 0 defects):** after a regen: tools/scan_selfbranch.py +
    tools/s7081_selfbranch_test, tools/s708[2-7]_* lowering, host-shim s7088/s7089; after a fixup edit:
    tools/s7090_fixup_statement_census.py (exit 1 = defect); after RSPRecomp/ucode fixups: tools/ucode_regen.sh
    `verify` (s7091), tools/s7093_su_census.py --controls; after rsp_vu*.hpp / DMEM: tools/s7092_vu_mem_test;
    after rsp DMA: tools/s7094_dma_test + s7094_dma_census.py; after dpc_bridge submit/defer/wrap:
    ROGUESQ_S7095_DPC / S7096_FWD=ctl / S7097_EDIT=ctl (missing/dup/order/unattributed must stay 0).
16. **Closed, reopen only on an owner report:** transition stalls (s7065, > ~350 ms hitch), host self-time
    (s7066-s7070), misnomer rename (s7080; tools/apply_symbol_renames.py), G1e residual (s6996).

G3 fidelity scoring kit (s7122-s7186), keep for item 1 and any re-score: arms tools/s7125_arm.zsh,
s7131_arm.zsh, s7141_{arm,post}.zsh, s7146_arm.zsh; post tools/s7152_post.zsh (NOPREFILL *n for 4:3-band
screens at 16:9, *r for 336-row screens, *c combine); scorers tools/s7122_fidelity.py, s7183_native_edge.py,
s7163_rectfit.py, s7182_yfit.py, s7154_{kmd,kgrid}.py, s7143_affine.py, s7184_ldesc_region.py; replay
tools/angrylion_replay/build16.sh (16 MB core for dd>1). TRAPs: score only the flight window (--t1 before
medals); L17 autopilot dies ~126 s (FROM=4700 at 21:9, 3300 at 4:3); 448-row cutscenes need FID_MAINRUN=1;
presented capture can end before the stream (drop clamped pframes); capture bursts mis-pair 2-swap runs
(re-pair +-6); raws before s7151 are Display-P3 (FID_P3=1); RECT_ASPECT=0 under ASPECT=4:3 stretches rects.
LEVEL DESCRIPTION = C-up on AVAILABLE CRAFT; the interlaced 512x448 screen is Elite Rogues.

## Evidence index

- s7187 maintenance archive (whole s7186 CURRENT-TRUTH verbatim) and s6994 archive: PROJECT-OVERVIEW.
- Earlier trims: PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (sNNNN)" (s7134, s7121, s7104, s6982, s6962, ...).
- s6900, s6847, s6759 maintenance archives; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png.
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md` (latest s7128_wsheetpos_p1-p4, folded s7128-s7130).
- Recent chronology: PORTING-STATE sessions 7047-7187; search bounded windows only.
