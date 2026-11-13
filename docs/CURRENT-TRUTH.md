# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7248 (2026-11-12).
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
hold ~60 fps in flight with 0 crashes at 21:9 (s7063; EXCEPT L4 heavy window t=77-97: flat 30/s, 20.5 ms task, s7230; s7231: the cost is WIDEWIN, not the dd6 radius, see Next 1; s7249: s7230/s7231 ran ON BATTERY at 10%->2%, CPU/task x1.40, on AC WW holds 60) and 16:9 (s7043). Cap 12288 is an opt-in (+0.25 ms
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
  s7218 endurance (FULLSCREEN + ASPECT=auto, LEVEL=4, 420 s, RETINA=1 vs 0): on screen both 59.5 presents/s, 0 gaps >250 ms,
  0 crashes, 1 swap chain each; RETINA gpu p95 0.68 vs 0.43 ms. a1's one 1048 ms gap at 354 s = Claude.app auto-update relaunch
  covered the fullscreen Space (pmset; P at=0 from then on): host event. Scorer now prints `hidden` (P at=0) rows; harness logs front-app changes.
  s7219 replicate, 600 s on screen throughout (1 front row, 0 hidden): 59.7/s, 0 gaps >250, gpu p95 0.75 (0.77 past 354 s), max 2.76 ms,
  0 crashes, 1 swap chain. **RETINA endurance complete (H-free, two runs); default = owner's call.**
  s7220 front end (s7215 L17 long route, auto FULLSCREEN, a1 vs a0): viewport 3016x1898 = 2 x 1509x949, same route (mode sequence),
  in-phase shot pairs bbox <=1 px at 4x, diff <=3.2; 0 gaps >250, gpu p95 0.78 vs 0.44 (H-ok; H-scale/H-cost refuted).
  tools/s7220_shot_pair.py; sheet docs/owner_sheet_s7220_retina_frontend/. **RETINA flight + front end CLOSED.**
  s7221 fullscreen display removal at RETINA=1: re-enter on the 2x built-in builds a 3024x1898 chain (r0 1512x949), 30/s on screen
  in ~2 s, backing-res sharpness kept (hf 1.178 vs 0.856, ctl 0.792). **RETINA hot-plug CLOSED.**
  s7222 display ADDED while fullscreen on the built-in: no resize, no swap chain change, 30/s steady (both RETINA arms). Removing a
  display the window is NOT on used to cycle fullscreen (resize + ~3 s at 13-19/s); s7222 gates the cycle to removals of the
  window's own display (bounds match; ROGUESQ_HOTPLUG_ANY=1 = old). Gated: 0 resizes, min 29/s; own-display removal still re-enters.
  s7223 ASPECT=21:9 WINDOWED (1360x594 pt window, LEVEL=4 owner recipe, r1 vs r0): r1 swap chain 2720x1188 (r0 1360x594), full 21:9
  view + edge HUD in the window both arms (bbox 0..1), hf 0.914 vs 0.735 (r1 higher 17/19 pairs; ctl down/up2 r1 0.522, r0 0.532),
  0 gaps >250, min 27 vs 29/s in a shared 30/s dip. H-ok. **RETINA windowed CLOSED.** Sheet docs/owner_sheet_s7223_retina_window_21x9.png.
  s7224 LIVE changes mid-flight (fs toggle x4 + SDL resize to 1000x430, r1 vs r0): every change = ONE swap chain step to 2x (r1) /
  1x (r0) the new point size, recover <=2 s, 0 gaps >250, Q==P (30/s stretches are game output); window-crop hf r1>r0 in 6/6
  phases, ctl passes. H-ok. **RETINA CLOSED in every scenario; default = owner.** Sheet docs/owner_sheet_s7224_retina_live_resize.png.
- **s7225 ASPECT=auto + live window resize = bars, not follow (H-bars; H-follow/H-stretch refuted).** auto (fb 692) and the 16:9
  control keep the boot width; RT64 pillar/letterboxes at 1000x430, 900x675, 1200x675 with lit aspect within ~1% of fb/448
  (tools/s7225_resize_aspect_score.py, ctl PASS). FB_WIDTH lives in function statics + boot-time heap/HUD policy, so live follow is
  not a bounded change. **G1f closed: auto follows the display at boot.** Sheet docs/owner_sheet_s7225_auto_live_resize.png.
- **s7226 auto on a SECOND display fixed (H-window + H-main):** the opt-in window always opened on display 0 (main), and a window placed on
  a secondary still took display 0's aspect + notch band (16:9 virtual: FB 712, BARS 16/18). One target display now drives auto, notch,
  fit and placement: ROGUESQ_WIN_DISPLAY=<n>|mouse (or the ROGUESQ_WINDOW_POS point's display; ROGUESQ_G1F_POSDISP=0 = old); default 0.
  Fix arm FB 796, FILL 17/18 (tools/s7226_display_fill_score.py, ctl PASS); 21:9 virtual -> 1024. Sheet docs/owner_sheet_s7226_auto_second_display.png.
- **s7227 F11 x2 + removal of the target display (WIN_DISPLAY=1): H-ok.** Toggle stays on the secondary (windowed 1920x1018, refill
  FILL 21/22); removal lands visible fullscreen on the built-in, letterboxed, 0 gaps >250 ms; s7222 gate reads still_present=0 right.
  HOTPLUG=0 also recovered here (contradicts s7202 hidden-Space, sequence differs). Its post-removal "flat 30/s" is NOT a display
  effect (s7228): the GAME swap rate (W/Q rows) fell to a rigid 33.3 ms, acquire 0.03 ms, VI clock is a fixed 60 Hz timer.
  Sheet docs/owner_sheet_s7227_secondary_toggle_removal.png.
- **s7228 WINDOWED removal of the target display: H-ok, flat-30 = H-content.** Both arms (default, HOTPLUG=0; same code path when
  windowed) land visible windowed on the built-in, 1512x863 layer, 30-60/s after removal (tools/s7228_present_rate_score.py, scorer
  reproduces s7227 old FLAT30 / fix MIXED). The old windowed arm ran a 62-s flat-30 stretch from t=127, 41 s BEFORE the removal, and a
  21-s one at t=76 recurs in all 4 s7227/s7228 arms: in-flight flat-30 runs up to ~60 s happen with no display event (single-route,
  diagnostic-logging harness). Sheet docs/owner_sheet_s7228_windowed_removal.png.
- **s7229 those in-flight flat-30 runs are the HARNESS (H-log/diag selected, owner unaffected).** m6_god_common.sh LOG_PHASE turns on
  G1E_PROBES (diag ucode path): L4 t=77-97 gfx task 21.95 ms -> rigid 30/s for 21 s. Same route with OWNER_TIMING=1 (12.95 ms) or a direct
  owner launch (12.76 ms): 60/s, 0 flat runs (tools/s7229_flat30_cost.py). The coverage harness now defaults OWNER_TIMING=1 for any arm
  with PRESENT_RING/G1B. Owner-path margin in that window: 12.8 of 16.7 ms, the thinnest measured at dd4.
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
- **s7213 present box shape fixed, default on (lib/rt64, ROGUESQ_PRESENT_SHAPEFIX=0 = old):** at a VI mode switch the first present of a
  target drawn under the old VI used that target's rs x/y ratio on the new VI, so the box took the old shape. At 21:9 this was LIT: the first
  frame of the mission intro and of the hangar re-entry showed squashed into a 1360x260 band (fb 1024x336, rs 5.143,3.0; tools/s7213_box_scan.py,
  control PASS; RDP 224 KB). Now the viewport shape comes from the present VI + aspect config when the ratios differ >3% (sampling unchanged;
  RDRAM uploads excluded). Same binary: fix=0 squashed band back, fix=1 full window; 4:3 and 16:9 census 1 correction each, no box frame.
  Owner sheet docs/owner_sheet_s7213_shape.png. s7214 fullscreen (1512x949): ASPECT=auto is rewritten to Manual 712:448 in main.cpp before
  RT64 init (it never uses Expand); ROGUESQ_ASPECT=expand is the only Expand user. Both: exactly 1 mismatch per run, the boot 4:3 vi-follow-draw
  target (auto rs 2.25,3 -> 2.973; expand 3.137 -> 4.145 = the rs ordinary 512x444 frames carry), 0 false fires on ordinary frames, all other
  viewports full. fix=0 arm logs the 4:3 pillar (vp 185..1324) but it falls in the dark title-still fade-in: no box frame in pixels (x8 gain sheet,
  scan control PASS). s7215 long route at 21:9 (s7210 mode sequence incl. 3 interlaced 0x80128D50 visits, MISSION FAILED, ER x2):
  16 corrections, all <=874 log lines after an osViSetMode/vi-mode-table line, 0 non-full viewports bar the 320x224 boot logo;
  box scan 51 narrow = fades/wipes only (control PASS x2). tools/s7215_shape_census.py (exit 1 = correction off a mode switch).
  **mode-switch-pillarbox thread CLOSED.**
- **s7216 21:9 long-route front end == angrylion (H-match, CLOSED):** GAME OVER/results, oval wipe, Elite Rogues, SELECT GAME / LEVEL,
  AVAILABLE CRAFT, hangar at the owner recipe 21:9: centre frac 0.019 / 0.000 / 0.009 / 0.035 / 0.018, 0 swaps >0.05 bar 22 ER scroll swaps
  that are a weave-reference pairing artefact (next frame = current field at the floor; H-field refuted). dx 0, dy flat (H-shift refuted).
  Undrawn fb side columns of the 4:3-band screens present black (reference shows stale RDRAM); hangar undrawn wedges show the buffer's prior
  content like hardware. The 21:9 "dark ring" (19% of lit px) was the row misfit below; interiors equal (s7182 edge class).
  Sheet docs/owner_sheet_s7216_219_frontend.png. TRAP: RT64 presents rows 0-443 of 448-row and 0-335 of 339-row screens; score with
  tools/s7122_fidelity.py FID_ALROWS=444 / 336 and check scratch/s7216/yprof.py (dy per band) first.
- **s7217 LEVEL DESCRIPTION at 21:9 and 16:9 == angrylion (H-match, CLOSED):** owner recipe, s7184 route; LDESC centre frac 0.044 / 0.036
  (AVAIL 0.034 / 0.029, 4:3 0.038), 0 swaps >0.05, dx 0 dy flat, text box k=1.000 (RECT_ASPECT right), 0 glyph-interior loss, controls PASS.
  Crawl / pause / MISSION FAILED were already scored at 21:9 (s7146 / s7150 / s7153). **G3 fidelity matrix complete** at every aspect arm.
  Sheet docs/owner_sheet_s7217_ldesc_wide.png.
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
- s7230 "the dd6 radius at 21:9 adds ~6.6 ms per gfx task over dd4 (H-dd)" and s7014-s7017 "WIDEWIN costs little or none at 21:9 dd4". Believable: s7230's dd4 21:9 arm (13.94 ms) differed from the dd6 line only, it seemed, in the radius; in fact it also lacked ROGUESQ_DD_WIDEWIN, and s7014-s7017 measured whole-flight/other windows. s7231 2x2 in the L4 t=77-97 window: WIDEWIN +4.5 ms at dd4 (flat 30/s), radius +0.7 ms without WIDEWIN.
- s7054/s7063 "Gerrard V (L4) at 21:9 dd6 runs 58.7-59.5 fps / all 19 levels ~60 at 21:9". Believable: whole-flight averages on the then route. s7230 (owner path, direct harness, two instruments): L4 t=77-97 flat 30/s for 21 s at 20.5 ms per gfx task, 109/239 s <55/s; dd4 21:9 holds 60 there.
- s7227/s7228 "in-flight flat-30 under FPS60 is the game's own frame rate (H-content)". Believable: rigid 33.3 ms game swaps with a free present path and a 60 Hz VI timer, no display event. s7229: the harness ran the diagnostic ucode path (LOG_PHASE -> G1E_PROBES, 21.95 ms task); the owner path holds 60/s there (12.8 ms).
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

1. **(next, NEXT.md) WIDEWIN cost at 21:9 (s7231 2x2, L4 t=77-97, owner path, one run per cell, 0 crashes, cursorMask 0x10).**
   gfx task ms / fps: dd4 13.96/60, dd6 14.62/58.6 (both WIDEWIN off), dd4+WIDEWIN 18.47/30 (flat 20 s), dd6+WIDEWIN 20.73/30 (flat 21 s)
   -> H-widewin selected (+4.5 ms at dd4, +6.1 at dd6), the radius adds only +0.7 / +2.3 (single run per arm; two instruments: [g1b]
   sd_wall and the G1E_TL rsp split agree, tog ph0 20.27 vs a6 20.73). Same-run tog3 in the dd6+WW line: K 0.6->0.45 rsp -1.04 ms
   (shift control -0.15), cap 10240->8192 -0.34 (shift control -0.47 = noise) although streamed cells/f fall 8300->6100: the cap
   and the streamed window cell count are NOT the cost (H-cap, H-cells refuted). Cost tracks RDP triangles: pooled fit 1.80 ms per
   1000 tri/task (R2 0.60, shuffle 0.00); WIDEWIN adds ~2.0-2.4k tri/task in the window, and the window sits +1.3..+3.7 ms above the
   line (extra per-triangle work the count misses, largest with WIDEWIN). OWNER-OPT-INS corrected: steady 60 at 21:9 = WIDEWIN off.
   s7232 (new [g1cf] tin/tout/tzero/kpx/bin fields, tools/s7232_tri_onscreen.py, classifier control 0.96-0.99): WW's +2557 tri/task in the
   window are 0 off-screen (ucode already rejects them; H-offscreen refuted), 42% zero-height (no pixel) and 58% visible but adding only +42 kpx
   (+2%) -> H-tiny (single-source): far WW cells are far denser than their pixels, past retail's coarsest LOD (s7011). Next: WW-only far
   thinning. s7233: knob ROGUESQ_DD_WIDEWIN_R=<cells> (+_R_TOG=1) skips non-empty cells outside the retail-equivalent 64x64 window
   farther than R from the eye (tools/apply_s7233_widewin_r.py, scorer tools/s7233_widewin_r.py, [g1cf] wr=, [s7233] tallies); built.
   **s7237 measured R=40/56** (L4 21:9 dd4+WW+MELT, same-run tog, CONTROL PASS both: ph1 skip 1820/1503 per placement, ph0 0; s7236 flush
   verified, 60 [s7233] blocks/log). Window t=77-97: r40 dsd -3.19 ms, dkpx -8.6%; r56 -1.94 ms, +3.8%. Flight t=60-230: r40 -1.61 ms,
   -3.3%; r56 -1.62 ms, +0.8%. Skipping cells cannot add pixels, so r56's +3.8% marks the tog kpx noise floor (~4% window, ~1% flight).
   Both lines agree that the cost moves with R (H-near refuted). r40 buys about 3 ms at a real kpx loss, while r56 buys about 1.7 ms with no measurable loss. About 40-50% of the cut is
   zero-height tris (dtzero -830..-1030 window). WW-only cells peak at d8 56-72. Neither arm meets the dsd <= -3 ms at < 0.5% bar, which leans H-thin
   (single run per R). **s7238: per-cell H-thin refuted** (code-read: retail level 2 = the 4 corner verts = one quad per cell; r40/r56 remove
   1.1-1.3 tri per skipped cell), so the only thinning past R is a 2x2 cell-merge mesh; scorer now prints tri/cell, ms/ktri and `s7238 BAR`.
   **s7239: the 2x2 merge is designed** (docs/WIDEWIN-MERGE-PLAN.md, static, not built). The flat lod-2 TRI_GEN carries its own spacing (w9 low =
   elem+0x22<<2) and the emit list is the node dist2 chain, so the plan is to rewrite 1 command and drop 3, with no ucode change.
   **s7240: merge BUILT, unmeasured** (owner active all session, so neither soak could run). Knob ROGUESQ_DD_WIDEWIN_MERGE=<frac> (+_MERGE_TOG=1), tools/apply_s7239_widewin_merge.py
   (H1 L_8004323C elem->dist2 hash, H2 0x800113DC pairing, H3 0x80011884 capture, H4 0x800119A8 drop, H5 L_800119BC anchor rewrite) + rs64_s7239_* in
   upstream_compat.cpp; [g1cf] gains wm=<phase>, one [s7239] line per phase every 2 s; scorer `tools/s7233_widewin_r.py --merge` (control: ph1 merged>0,
   drop==3*merged, unm=0; ph0 anc=0, cand>0). Off by default (g_rs64_s7239_on=0, all hooks no-op). Soak s7240_widewin_merge queued (MERGE 0.4/0.55/0.7). **s7241: host unit test tools/s7241_merge_test/run.sh** (live block, synthetic RDRAM, emulated writer + TriGen02 decode): 17/17 pass incl. reorder, negatives, overflow, TOG ph0, checker control; UB `<<4` on negative -> `*16` fixed. Rerun it after any rs64_s7239 edit. **s7242: H-stale closed in code**: H1 dist2 hash slots carry a per-build-pass generation (H1 after an H2 bumps it); an older entry is a miss counted as `stale=` in [s7239] (scorer prints it), never a merge input. Test 19/19, negative control (gen check off) fails the stale case.
   **s7244: merge MEASURED** (L4 21:9 dd4+WW+MELT, same-run tog, owner idle; 9 arms over 3 soaks, CONTROL PASS on every merge arm: drop==3*merged, unm=0, stale=0).
   Gate bug found and fixed: H1 node+8 reaches 7116 while farcut 0x8009DEB4 = 117.4 (different units), so the s7240 gate frac^2*farcut passed ~all
   cells (near 216..7627 of ~2M; three arms = three reps of merge-all: win dsd -2.44..-2.75 ms, kpx +-0.4%). Now thr = frac^2 * pass-max node+8
   ([s7239] thr=, unit test 22/22, negative control fails 5 checks). Fixed gate shows dose-response, m40/m55/m70: merged 1.73M/1.21M/0.61M,
   win dsd -2.31/-1.75/-0.79 ms (about 0.9 ms per ktri), win kpx within +-1%. m30: win -1.89, flight -3.04 ms. **m40+R56 combined: win dsd -4.46 ms,
   kpx -0.1%; flight -3.58 ms, kpx -6.6%.** The null arm m99 (merges nothing) reads flight kpx +4.7%, win +1.7%, so the tog kpx floor is ~+-5% in
   flight and the s7238 flight |dkpx|<=1% half of the bar CANNOT be resolved with tog kpx (single-source; the s7237 1% estimate was too low).
   The window time half is met by m40+R56 only.
   **s7245: the merge CRACKS (H-crack, two runs; H-clean refuted, keep it out of OWNER-OPT-INS).** New tools/s7245_merge_cracks.py counts bright 1-px
   seams in the side thirds per in-flight frame by tog phase, same-run control (+80 seams injected) PASS 112/112 both runs. Seam px/frame off -> on:
   m40+R56 24.5 -> 55.0 (A/A -6.4), m40 alone 24.4 -> 47.4 (A/A +8.3). Zoom (docs/owner_sheet_s7245_merge_cracks_zoom.png): haze shows through slivers
   along cell edges on mid-distance hillsides and along the L4 shoreline. The merge boundary sits at ~0.4 of the window radius, in clear view, so the plan's
   'haze hides the T-junction' was wrong. R sweep folded (s7237_widewin_r2): r48 win -4.12 ms, r64 -1.20, r72 -1.56; kpx +-7% unordered = noise.
   **s7246: flatness gate BUILT and measured (H-flat-works for cracks, partial for time).** ROGUESQ_DD_WIDEWIN_MERGE_E=<emitted units> (default 0 =
   exact planar; abs y = 16*(ybase+h)) rejects a block whose 4 merged-edge midpoints deviate from the end average by > E (the T-junction gap);
   _MERGE_C (default E) does the same for the centre vs both diagonals (TriGen02 picks the split by depth). [s7239] gains E= C= flatrej= ctrrej= shmis=
   dh=<8-bin edge-dev histogram>; unit test 29/29 (7 new flat cases incl. random-terrain negative control). L4 candidates: 70-76% are exactly planar,
   80% within 32, so H-flat-empty refuted. Image (4 capture arms, owner idle, synthetic control PASS on all): at full capture geometry E=16 side seams
   23.1 -> 20.1 px/frame (no excess), ungated control in the same session 26.4 -> 38.2, side Q3 28 -> 52 (real-crack control, weaker than s7245).
   E=0/E=64 arms got a narrower crop (content_w 631/895), so they are not comparable (e64 also had owner input). Timing (same-run tog, 1 run/arm,
   CONTROL PASS x3): window dsd e16 -1.28 ms (kpx -6.8%, within window tog noise), e0 -1.14, ungated -2.30 (repeats s7244's -2.31); flight e16
   -1.13 ms kpx -1.1%. So the gate keeps ~75% of merges but only ~55% of the saving, because the rejected blocks are the hilly, visible ones. Below the
   -1.5 ms bar (single run). Owner sheet docs/owner_sheet_s7246_merge_e16.png. **s7247: H-stack selected (two runs, CONTROL PASS on all 6 timing arms).**
   Window dsd: r48 -3.72/-2.83 ms, E16+R48 -3.63/-3.88, E16 -1.33/-1.35 (partial overlap: singles sum ~-4.6). Flight: r48 -1.04/-1.82, stack
   -3.22/-2.03, E16 -1.40/-3.38. Image (2 capture arms, owner idle, content_w 1191 both): seams r48 -2.4, stack -1.8 px/frame (synthetic control
   PASS); holes by new tools/s7247_tog_pop.py (TEX = grain fraction G=3 in the side band, flip test + phase means; control = most textured 200x40
   window flattened, PASS 130/136, 132/138): r48 +0.0029+-0.0052, stack +0.0013+-0.0056 = no visible terrain removed (sensitivity ~1/3 of a 200x40
   patch). OWNER-OPT-INS line added (experimental; s7248 fixed-on numbers added); sheet docs/owner_sheet_s7247_widewin_stack.png. Next (NEXT.md): fixed-on
   (no tog) fps in the window: WW off / WW / WW+stack.
   **s7248: fixed-on (no tog), one run per arm, owner idle, 0 crashes, knobs engaged (stack: [s7233] skip ~4006/placement, [s7239] merged 51.9k
   unm=0 stale=0).** Window t=77-97 gfx task ms / fps: off 10.06/60, ww 13.16/60, stack 9.59/60; flight p50 8.62/9.56/6.30, max>=17ms s 0/18/0.
   stack - ww = -3.57 ms, which matches the tog -3.63/-3.88: the fixed-on and tog lines agree (two lines), and stack <= WW-off. Positive control FAILED:
   ww did NOT reproduce s7231's flat 30 because the host ran ~4 ms/task faster (off 10.06 vs s7231 n4 13.92, sd_cpu 8.70 vs 12.25 at t=80, same code:
   no perf-relevant diff since s7231). So 'stack holds 60 on a slow host' is inferred (stack <= off, and off held 60 in s7231), not measured. 2nd runs voided
   by owner input at offb t=120 and re-queued (soak s7248_fixed_fps_b, RESUME keeps run 1).
   **s7249: the slow host was BATTERY POWER (two lines).** (1) pmset log: BatteryHealth warning cap 10% at 14:40 and 2% at 15:09, 'Low Power Sleep'
   at 1% at 15:22, wake on AC attach 19:08; s7231 ran 14:30-14:52, s7248 22:41 on AC. (2) [g1b] sd_cpu ratio s7231/s7248 is a constant 1.37-1.44
   in every window (light 1 ms tasks and heavy 12 ms tasks alike; matched n4/off and a4/ww), wall-cpu almost equal, load1 similar (3-4) and qos
   0x15 both: a clock signature, not contention (H-load refuted, H-thermal not needed). So the WIDEWIN flat 30 is a battery-host result; on AC
   ww holds 60 (headroom 3.48 ms, 18 s with a >=17 ms task) and stack holds 60 with 7.06 ms. Timing arms on battery are now refused:
   tools/g1e_owner_quiet_arms.zsh logs pwr= on start/done and exits 2 on battery unless ALLOW_BATT=1.
 (tools/g1e_owner_quiet_arms.zsh, test tools/s7243_resume_test.zsh 7/7): after a void, only the unfinished arms re-run. Both queued recipes use it.
   The bracket arms R=48/64/72 are queued as soak s7237_widewin_r2 (idle-gated). r72 was voided by owner input in s7237. Tools: tools/s7231_cost_decomp.py (needs ROGUESQ_G1CF=1;
   dsize is 0 on the owner path), s7230_headroom.py, s7229_flat30_cost.py, g5e_cost_by_parity.py --phases 3.
   Boot freeze stays passive; hunter `env HUNT_OWNER=1 HUNT_CONTROL=1 zsh tools/boot_freeze_hunt.sh <out> N 34 12`.
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
tools/angrylion_replay/build16.sh (16 MB core for dd>1). TRAPs: set FID_ALROWS=444/336 (RT64 shows rows 0-443 / 0-335, s7216); score only the flight window (--t1 before
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
- Queued-soak verdicts: `scratch/agent/SOAK-RESULTS.md` (s7235_widewin_r run by s7237 itself: r40+r56 scored, r72 void; s7237_widewin_r2 queued). Recipes that drive the
  game window carry `# SOAK_NEEDS_IDLE=<secs>` (loop skips them on a busy/locked host; tools/agent/test_soak_idle_gate.sh).
  An edited loop.sh now takes effect BEFORE the soak phase that follows the editing iteration (s7235 re-exec + RS64_LOOP_SOAKS_FIRST).
- Recent chronology: PORTING-STATE sessions 7047-7187; search bounded windows only.
