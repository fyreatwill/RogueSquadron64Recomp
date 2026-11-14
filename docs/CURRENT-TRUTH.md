# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7303 (2026-11-13).
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
hold ~60 fps in flight with 0 crashes at 21:9 (s7063; the L4 heavy-window flat 30 of s7230/s7231 was battery plus WIDEWIN cost; on AC the auto WIDEWIN stack holds 60 at dd4/dd6 on L1/L4/L5/L12, Next 1, CLOSED s7262) and 16:9 (s7043). Cap 12288 is an opt-in (+0.25 ms
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
- s7286/s7288 "the terrain window binds from dd4; dd4->dd6 +25% area adds 1.8% cells". Believable: tools/s7286_dd_window_cells.py
  "cells/call" ([s7233] in=) sat at ~3550 for dd4..dd8. s7291: in= counts only cells inside the retail-equivalent 64x64 window,
  so it is constant by construction; counting the wide-only histogram, total cells grow 5528 dd4 -> 6878 dd6 (+24%).
- s7283 "the off-window gaps >=250 ms (l12cb0 379 ms, l12cb1 274 ms) are the GPU saturator's in-flight buffers draining after its SIGKILL". Believable: both followed lit holds near +381 s at the end of an on window. s7284: the +381 s lit hold is the SIGSTOP control; the gaps themselves are black (luma 0) fb-relocation transitions 11-53 s after the edge.
- s7247/s7259/s7262 "the WIDEWIN auto stack removes no visible ground" (and OWNER-OPT-INS "WIDEWIN is free with its automatic settings"). Believable: holes/seams/flip scorers found no lost ground inside the picture. They never scored the side edge, which is the only thing WIDEWIN adds: s7264 same-run toggles show the side gain present with STACK=0 (L/R -4.4/-5.0) and gone with the stack (-0.7/+0.4).
- s7230 "the dd6 radius at 21:9 adds ~6.6 ms per gfx task over dd4 (H-dd)" and s7014-s7017 "WIDEWIN costs little or none at 21:9 dd4". Believable: s7230's dd4 21:9 arm (13.94 ms) differed from the dd6 line only, it seemed, in the radius; in fact it also lacked ROGUESQ_DD_WIDEWIN, and s7014-s7017 measured whole-flight/other windows. s7231 2x2 in the L4 t=77-97 window: WIDEWIN +4.5 ms at dd4 (flat 30/s), radius +0.7 ms without WIDEWIN.
- s7054/s7063 "Gerrard V (L4) at 21:9 dd6 runs 58.7-59.5 fps / all 19 levels ~60 at 21:9". Believable: whole-flight averages on the then route. s7230 (owner path, direct harness, two instruments): L4 t=77-97 flat 30/s for 21 s at 20.5 ms per gfx task, 109/239 s <55/s; dd4 21:9 holds 60 there. s7251: s7230 itself ran on battery (Low Power Mode, x1.36-1.43 CPU/task vs AC s7248 off; x0.97-1.01 vs battery s7231 n4), so this is also a battery-host verdict; AC measured s7257: dd6r 60.0/s, 14.06 ms (n4 bridge 9.81 vs battery 13.97 = x1.42), control dd6rd flat 30 21.81 ms.
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

0. **s7303 G5e fog END sweep (dd8 16:9, same-run FOG_ALT toggle, xor8 sheets, 0 crashes, patch control PASS in all 12 bands):
   haze grows monotonically as ke drops, no knee. Texture removed far/near/side: L1 ke4.5 0.6(null)/0.9(null)/1.1; L1 ke3 1.3(null)/2.4/2.7;
   L1 ke2 1.5/4.6/3.7; L4 ke3 1.5/6.5/4.0 (%; s7302 ctl 0.3,0.8 = 7/38/22). By eye (docs/owner_sheet_s7303_{l1k3,l4k3,l1k2}_fog_tog.jpg):
   ke3 melts the far horizon into the sky/orange haze and near terrain keeps its detail; the L1 plateau stays dark CLOSE to the camera
   (retail draws it there too, distance fog cannot remove it without hazing near land). ke3 at dd8 = dd4's default fog end (0.8x4=3.2).
   Opt-in for the owner: ROGUESQ_DD_FOG_ALT=1,3,1 (OWNER-OPT-INS). Default unchanged (owner decides). s7302: the band is the off-map
   plateau and it takes fog; s7301: the dd8 ring beyond 88 cells is invisible (default R128 left). Next: 300 s hold + frame ms of the opt-in (NEXT.md).**
0. **s7299: dd8 px8 auto QUALIFIED at 21:9 (s7298 soak, ctl flat-30 158 s PASS): L1/L5/L9/L10/L12 300 s, 0 crash, 60/s,
   beyond-route 3/8/0/1/0 s (L5's 8 s are 36-47/s single seconds at t<=76, route), heaviest20 10.6-12.1 ms (headroom 3.2-6.1).
   total_emit L1 11134 L5 11837; L9 6189 (CAPLEVEL 9:8192 binds, wide 2509); L12 RLEVEL 12:48 wins (3839 vs ctl R128 12420 ->
   flat 30); L10 cloud level, no [s7233] terrain lines (same as 16:9). dd8 now qualified at 16:9 and 21:9; OWNER-OPT-INS updated.
   Next: horizon-in-view dd6-vs-dd8 look sheet, then the game far cutoff 0x8009DEB4.**
0. **s7297: dd8 px8+R128 auto extended to 21:9 (FB_WIDTH<=796 gate dropped in main.cpp [s7293]).** s7296 soak (L4 21:9 dd8,
   1 run/arm, ctl flat 30 + px8 depth 128 PASS): total_emit ref(px5,R88) 7466 / px8 7909 / px8+R128 11818, win77-97 12.98 /
   13.54 / 13.65 ms, all 60.0/s -> H-219-ok. In-session verify (scratch/s7297_verify.sh): auto [s7293] fbw=1024, 11620 cells/call
   depth 128, 60.0/s 13.73 ms vs PX8_AUTO=0 7313, 12.94 ms. Queued s7298_219_dd8_levels (300 s L1/L5/L9/L10/L12 21:9 + ctl).
   **s7295: dd8 px8 auto QUALIFIED at 16:9 (s7294 soak, ctl flat-30 PASS): L1/L5/L10/L12 300 s, 0 crash, 60/s, beyond-route
   <=4 s, L12 RLEVEL 12:48 still wins.** Look sheet docs/owner_sheet_s7295_dd6_dd8.jpg (L1 dd1/6/8, L4 dd6/8, SHOTS t=100-140,
   tools/s7295_dd_look_sheet.py): that route window banks under cliffs, horizon mostly off-frame; only L4 shot 6 separates dd6
   (11% sky band) from dd8 (1%) - single-source. A horizon-in-view camera (pose lock / later route second) is needed for a real
   dd6-vs-dd8 look. Then the game far cutoff 0x8009DEB4.
   s7293 G1c dd8 bundle LANDED: H-R selected (2 runs: s7292 explicit + s7293 auto, ctl depths PASS).** L4 16:9 dd8 total emitted
   cells/call ref(px5,R88) 6902 / px8(R88) 7316 / px8+R128 11322 (s7292) / auto 11406 (s7293), window 128x128 vs ref 80, win77-97
   11.83-12.06 ms all 60.0/s. main.cpp [s7293]: dd>=8 + WIDEWIN + FB_WIDTH<=796 -> POOLX_MAX=8, WIDEWIN_R=128 (explicit env wins,
   ROGUESQ_DD_PX8_AUTO=0 off; width gate removed s7297).
   **s7291 G1c: total emitted terrain cells per stream call (tools/s7291_wide_cells.py = [s7233] retail in + wide-only histogram -
   R skip) L4 16:9: dd2 1893 -> dd4 5528 -> dd6 6878 -> dd8 6809 (px clamp 5 = same cap as dd6); dd6 POOLX_MAX=8 7453 (+8%, window
   128x96, wide 3875 -> 5457 but WIDEWIN_R=88 skips 528 -> 1578), win77-97 11.20 vs 11.24 ms, 0 crash. OFFMAPCULL=-1 leaves the
   tally identical (the cull acts downstream of it; +1.4 ms) (s7290, 1 run/arm, ctl: px8 depth 96 PASS).** Binding distance limit
   at dd>=6 is our own WIDEWIN_R=88, then the px clamp. Queued s7292_r_px (dd8: ref / px8 / px8+R128, cells + ms + sheet).
   **s7287 L12 16:9 dd6 dip: H-R88 selected (2 runs: s7286 + s7287, control STACK=0+DUTY flat 30 120 s PASS).** win77-97 r88 49.1/s
   15.53 ms flat 30 t=77-84 vs r48 60.0/s 10.95 ms vs dd4(R88) 59.3/s 15.43 ms, equal cells/call (3521/3509/3538). Fix: new
   ROGUESQ_DD_WIDEWIN_RLEVEL=<lvl>:<R>[,...] (upstream_compat.cpp rs64_s7233_win, gCurrentLevel latch s7056_last), auto 12:48 at dd>=6
   (main.cpp [s7258]); verified same session auto 60.0/s 10.94 ms, 0 flat vs RLEVEL=none 49.3/s flat t=77-84, [s7287] level=12
   widewin_r=48/88. **s7288: L1/L9/L13 16:9 dd6 R=88 all 60/s, 0 beyond-route s (ctl PASS) -> H-L12-only, CLOSED.** dd5 L12 unmeasured.
   **s7288 window bind (site-17 trace, tools/s7289_window_bind.py, ctl WIDEWIN=0 pins 64x64 PASS):** dd>=4 window = 128 side x
   cap/128 deep (cap 2048 x ceil(dd), px clamp 5: 128x64 dd4, 128x80 dd5+). (Its "+1.8% cells" reading is SUPERSEDED s7291.)
   Loop fix s7287: soak recipes now run under their shebang shell (zsh recipes ran under bash; the syntax error's rc=2 was filed as
   a human VOID) and a `-n` syntax failure is filed rc=SYNTAX (tools/agent/test_soak_idle_gate.sh 15/15).

1. **CLOSED s7262: WIDEWIN heavy-window cost at 21:9 (s7231-s7262; full thread migrated to PROJECT-OVERVIEW "s7262").**
   Cause: WIDEWIN far side cells are far denser than their pixels (H-tiny, s7232). Fix: the auto stack R=48 + 2x2 merge 0.4 + E16
   (tools/apply_s7233_widewin_r.py, apply_s7239_widewin_merge.py, main.cpp [s7258]) applies at any dd>1 with ROGUESQ_DD_WIDEWIN=1
   (ROGUESQ_DD_WIDEWIN_STACK=0 off; explicit values win). Measured auto vs off, heavy window, AC, same-run controls PASS: L4 dd4 9.77 vs
   13.91 ms (s7261), L4 dd6 9.99 vs 13.40 (s7259), L12 dd6 8.94 vs 12.02 p50 (s7260). **s7262 levels fold (s7261_dd4_stack_levels):**
   dd4 21:9 auto on L1/L5/L12 all print [s7258] dd4, merged 4.47M/4.79M/1.04M unm 0, win77-97 60.0/s at 8.91/5.17/11.81 ms, beyond-route
   <55/s 0/1/0 s (L5's single s at t=75, 39/s, sits just after the route transients), alive, 0 crash; control L12 STACK=0+DUTY 30/s flat
   (172 beyond-route s) PASS -> H-general. Image: dd4 L4 clean two runs (s7247), dd6 L4 clean (s7259), L12 dd4 clean (s7262: holes control PASS 143/148,
   flip +0.0022 +- 0.0041, seams on-off -11.2 vs A/A -15.7 px, tog ph0 merged 0 / ph1 0.49M; single run). **16:9 TV (s7263 fold of
   s7262_169_widewin, L4 dd4, AC, control w0d+DUTY 33.9/s 112 beyond-route s PASS):** win77-97 n (no WW) 9.23 ms 60/s, w (auto stack) 9.15 ms
   merged 3.25M, w0 (STACK=0) 12.25 ms 4 frames >=17 ms; beyond-route 3/0/3 s; 0 crash -> H-cost (stack needed at 16:9 too, free with it; single run).
   **s7264: the auto stack ERASES WIDEWIN's side-edge gain** (L4 dd4, same-run WIDEWIN=tog parity, g5e_edge_score hard80% off->on L/C/R,
   capture 52-63 frames/s): 21:9 stack on 23.2->22.5 / 29.7->28.7 / 20.7->21.1 (no gain); 21:9 STACK=0 17.5->13.1 / 29.1->29.3 / 17.6->12.6
   (gain re-fires, = s7009); 16:9 stack on 21.5->24.1 / 31.1->30.6 / 19.1->18.7 (no gain). So "stack is free" = the stack removes the cells
   that WIDEWIN adds, visible gain included (single run per arm). **s7265 (fold of s7264_stack_edge, control c219 STACK=0 L/R -6.4/-8.0 PASS,
   51-56 capture frames/s, 0 crash): R=48 is the eater (H-R)**: 21:9 R=0 (merge+E16 kept) L/R hard80 21.9->15.8 / 21.1->14.7 (gain kept);
   16:9 STACK=0 21.4->17.6 / 21.0->15.9 (H-gain16: WIDEWIN does widen the 16:9 sides). Second line: the [s7233] wide_by_d8 histograms
   (tools/s7265_ww_r_predict.py, L4 21:9, L4 16:9, L12 21:9 runs) put the wide-only cells at 32-96 cells from the eye, so R=48 skips
   92-95% of them (predicted = measured skip/call); R=72 keeps ~65%, R=88 ~98%. Open: does R=72/88 (+merge) keep 60/s and the side gain?
   **s7266 fold -> auto R 48 -> 88 (main.cpp [s7258]).** s7265_ww_r_cost (L4 21:9 dd4 AC, control w0d STACK=0+DUTY flat30 21 s, 122
   beyond-route s PASS): win77-97 r0 12.42 / r72 11.58 / r88 12.03 ms, all 60/s, 0 flat runs, beyond-route 4/4/4 s; r88 measured skip 2%,
   r72 35%. s7265_ww_r_edge (control c219 STACK=0 L/R hard80 -8.0/-8.8 PASS, 52-56 cap fps, 0 crash): r72 -5.1/-7.2, r88 -7.6/-9.6 (gain
   kept). So merge+E16 carries the cost cut; R only ate the gain. Single run per arm. Open: dd6 at R=88 (s7257's late dips were removed
   with R=48): queued s7266_dd6_r88 (a88 / a48 / offd control).
   **s7267 fold of s7266_dd6_r88 (L4 21:9 dd6 AC, control offd STACK=0+DUTY flat30 t=77 21 s, 121 beyond-route s PASS) -> H-keep6:**
   a88 (auto R=88) win77-97 60.0/s 12.30 ms headroom 4.27, p95 13.89 max 16.15, 0 flat runs, beyond-route 4 s, 7 frames >=17 ms,
   measured skip 12%; a48 9.67 ms headroom 6.96, 0 flat, beyond-route 3 s, 0 frames >=17 ms, skip 96%; merged 4.62M/2.59M unm 0;
   0 crash. dd6 keeps 60 at R=88 (single run per arm). Queued s7267_169_r88_cost (16:9 a88/a48/w0d) + s7267_r88_edge_sheet (16:9 s88,
   21:9 w88, c219 control; new SHEET=1 in tools/s7263_widewin_edge_arms.zsh -> tools/s7267_tog_sheet.py off|on frame-pair sheets).
   Capture hygiene: s7263_169_edge (rc=0) and its first re-run were void, 133-142 frames/180 s, Chrome frontmost; the s7009 arm lacked the
   s7259 frontmost keeper. tools/s7263_widewin_edge_arms.zsh now keeps the game in front and fails (rc=3) under 10 captured frames/s.
   **s7268 fold (L4 dd4 AC):** s7267_169_r88_cost control w0d (STACK=0+DUTY) 33.7/s 108 beyond-route s PASS: 16:9 a88 win77-97 60.0/s
   10.92 ms (max 12.53, 0 f>=17 ms, 0 flat, beyond-route 3 s, skip 5%, merged 6.04M) vs a48 9.11 ms (skip 96%) -> 16:9 R=88 cost OK.
   s7267_r88_edge_sheet control c219 L/R -6.3/-9.6 PASS: s88 16:9 R=88 -0.2/-2.1 (vs s7264 16:9 STACK=0 -3.8/-5.1, cross-run), w88 21:9
   -7.7/-3.6 (s7265 R=88 -7.6/-9.6: the right side swung 6 between runs). Single-run 16:9 'no gain' not trusted; sheets show no cracks/
   missing ground but neighbouring seconds differ in camera. New tools/s7268_edge_delta.py (L/C/R deltas + control verdict).
   Queued s7268_169_split: 16:9 s0 STACK=0 / m88 MERGE=0 / s88b repeat + c219 control (H-merge16 vs H-noise vs H-real16).
   **CLOSED s7269 (fold of s7268_169_split, L4 dd4 AC, capture 52-58/s, 0 crash; control c219 21:9 STACK=0 L/R -6.9/-11.9 PASS):**
   16:9 s0 STACK=0 L/R -0.8/+0.9 (side gain -0.1), m88 MERGE=0 -1.1/-1.2 (2.3), s88b R=88 -0.4/-4.8 (5.2). The 16:9 reference itself
   shows no gain this run (s7264: 8.9), so 16:9 side gains across 5 runs/arms span -0.1..8.9 with no STACK=0 > R=88 ordering -> H-noise:
   at 16:9 WIDEWIN's side gain is small and below run noise on this route; R=88 is not shown to cost any of it. Keep auto R=88 at
   both aspects (16:9 cost 10.92 ms 60/s, s7268). Likely why (unmeasured): the 16:9 off-edge is already lower (s0 off L/R 17/16 vs
   21:9 23/25), the 64-cell window covers most of the 16:9 frustum. tools/s7268_edge_delta.py now takes ref_arm:min_gain (MEASURABLE).
   Unit tests: tools/s7241_merge_test/run.sh (after any rs64_s7239 edit), tools/s7243_resume_test.zsh. Arms: tools/g1e_owner_quiet_arms.zsh.
   Not shown: real Low Power Mode on the clock probe (only the DUTY stand-in). Boot freeze stays passive: hunter
   `env HUNT_OWNER=1 HUNT_CONTROL=1 zsh tools/boot_freeze_hunt.sh <out> N 34 12`.
   **s7270: the stack is invisible in cutscenes at 21:9 dd4** (AT THE MOVIES, same-run tog3 ph0 off / ph1 auto stack / ph2 control; new
   ROGUESQ_DD_WIDEWIN_R_TOG=3 _R3 and _MERGE_TOG=3 _MERGE3): off->stack edges p99 1.26 max 1.54 vs mid-second control p99 1.45 max 2.85; control
   (R1 + merge + ungated off-map cull R0) fires 3.36-3.78 (green-field shot). Top edges viewed = ship motion/fades. Merge acts (3.4M merged), R barely
   (wide-only cells rare in cutscene views). A R=1-only control does NOT fire (t3 run VOID as null).
   **CLOSED s7271: same at 16:9 dd4 (owner TV) -> H-clean169.** Soak s7270_169_cutscenes was VOID: its autopilot gate 13:w1024 waits for a VI
   width EQUAL to 1024, the 16:9 menu phase commits 1592, so the schedule stalled and the game looped attract for 960 s (top edges = logo/fades).
   Recipe fixed (13:w1592; route then leaves the menus at 216.8 s = 21:9's 217.0). Re-run s169b in-session: 0 crash, 50886 frames, movies
   216.8-955 s; off->stack p99 1.60 max 2.72 vs mid-second control p99 1.49 max 1.98; control (ocull 1469/f in ph2 only) 2->0 4.91 / 1->2 3.24 =
   green-field ground band. Top 4 off->stack edges viewed: shot cut, camera move, fade, explosion; no ground loss. Sheet
   docs/owner_sheet_s7271_widewin_stack_cutscenes_169.jpg. Gate audit: no other 16:9 recipe carries w1024. Thread widewin-stack-cutscenes closed.
2. **G5i hangar re-entry: fixed s6995, owner look.** Route scratch/s6995/arm.zsh; tools/g5i_pan_metric.py.
3. **G5a Gerrard V (LEVEL=4) crash: fixed s6893, owner re-flight** past half way, repeated (s6998 writeback audit clean).
4. **G5b terrain drops: owner flight.** FWDWIN far-loss fix holds L1/L4/L5/L7 (tools/g5b_fwdwin_seamless.py).
   LEVEL=10 is cloud (no terrain grid): never use it for terrain measures.
5. **G5c freezes (s6902), G5d logo (s6903): owner flight / boot.**
   s7272: no frozen image in flight on the WIDEWIN auto-stack path, 16:9 L4 dd4 same-run tog3 (off / stack / R88): 0 holds >= 120 ms in
   flight in any phase; the 6 holds 250-442 ms are all cutscene transitions; SIGSTOP 1 s control caught 3/3. Tool tools/s7272_image_hold.py
   (time between differing frames, sees repeats and gaps), arm tools/s7272_g5c_hold_arm.zsh. **s7273 21:9: same (H-none219)**: in-session
   KEEP=1 run, control 3/3, 2 holds 275/372 ms both black transition frames (sheet docs/owner_sheet_s7273_g5c_widewin_holds_219.jpg,
   new tools/s7273_hold_sheet.py), 0 flight holds; the s7272_219_hold soak's 8 holds are unclassified (raw deleted). Thread closed.
   **s7274 FULLSCREEN=1 (owner recipe, [g1f] fullscreen=1 drawable 3024x1898) on L1/L4/L5/L12: 0 flight holds >= 250 ms, control 12/12,
   every hold = black mission-restart transition (sheets docs/owner_sheet_s7274_g5c_fullscreen_L*.jpg) -> H-none-fs.** Arm now takes
   LEVEL= FS=1 PLAIN=1 DUR=. **s7275 close criterion MET (H-none-long): PLAIN owner env (FPS60 dd4 16:9 FULLSCREEN, no WIDEWIN/MELT),
   900 s, L4 + L12: 0 flight holds >= 250 ms, control 6/6; L4's 7 holds = black death/restart transitions (sheets
   docs/owner_sheet_s7275_g5c_plain900_L{4,12}.jpg). G5c engineering CLOSED on a quiet host.** **s7276 busy host (H-robust): PLAIN FS L12 600 s with 15 `yes` spinners (= hw.ncpu, load avg 30) and with 5 (= P-cores, load ~10): control 3/3 each, 0 flight holds >= 250 ms; the one hold (271 ms, 15-spinner arm) is a letterboxed HUD-less cinematic shot, viewed (docs/owner_sheet_s7276_g5c_busyhost_{all,p}_L12.jpg; tools/s7276_busy_host_arm.zsh). (s7276 reading SUPERSEDED by s7277.)** **s7277 within-run toggle, game's own present clock (tools/s7277_toggle_load_arm.zsh + s7277_toggle_score.py): 15 CPU spinners on drop the game 60 -> 49.4 fps with 5 frame gaps 250-567 ms (off windows 60.0, 1); the same toggle with ROGUESQ_QOS_ALL=1 holds 59.5 fps, 0 gaps >= 250 ms (capture image-hold scorer agrees: 7 holds -> 0; control 3/3 every arm). A saturating GPU neighbour (tools/s7277_gpu_busy.swift) makes a steady 16.6 fps, no long gaps. -> H-cpu-slow: background CPU load is a real freeze source and QOS_ALL fixes it. **s7278 L4 (Gerrard V) replicate, same toggle: no QoS 52.0 fps on-load, 3 real image freezes 357-700 ms (lit held frames); QOS_ALL=1 59.6 fps, 0 real freezes (every hold = black death/restart frame); control 3/3 each -> H-qos-general (two lines: present ring + image holds; one run per arm per level).** Awaiting the owner: make QOS_ALL=1 the default? **s7279 split (L4, same toggle): GUEST_QOS alone 55.0 fps on-load, gaps >=100 ms 48 -> 1, 0 lit freezes; GFX_QOS alone 47.7 fps, 38 gaps, 1 lit freeze -> the guest thread carries the freezes, GFX is not the fix, the leftover frame rate needs the RT64 render-side knobs (gpu95 2.6 vs 0.37 with QOS_ALL).** **s7280 (L4, same toggle): GUEST+PRESENT 57.9 fps on-load, 1 gap >=100 ms, 0 lit freezes = everything-but-GFX 58.0 / 0 lit -> smallest set is GUEST_QOS+PRESENT_QOS (H-present); WL/UPLOAD/GFX add nothing measurable. **s7281 L12 replicate: GUEST+PRESENT 57.1 fps on-load, 0 gaps >=250, 0 lit holds; QOS_ALL 59.6, 0/0 (control 3/3 each) -> the pair removes the freezes on 2 levels, QOS_ALL adds ~2 fps under load on both (every gp window below every all window). Split CLOSED.** Owner recommendation stays QOS_ALL=1; default is the owner's call. **s7282 GPU contention (fold of s7281_l12_gpu_{none,qos}, L12 PLAIN FS 16:9, Metal saturator 35.8 ms/cmdbuf toggled 60 s, control 3/3 each): none 16.0 fps on-load / 57.3 off, qos (QOS_ALL, witnesses [guest-qos] ok + s6985-s6988 threads) 16.0 / 57.3, 0 gaps >= 250 both, max 149/120 ms -> H-gpu-share: CPU QoS cannot help GPU contention; the game slows evenly (no freezes), so G5c's close bar holds under GPU load too.** 16 fps = 62.5 ms = ~1.75 saturator buffers per frame (single-source): FIFO-behind-cmdbuf vs fair GPU timeslice is open. Queued dose-response s7282_l12_gpu_i{5000,80000}.sh (GPU_ITER, ~9 / ~143 ms/cb): fps ~flat 16 = timeslice (nothing in-process helps); fps tracks 1/(k*cb) = our ~k dependent submits/frame wait behind each foreign buffer (lever: fewer RT64 submits per frame). **s7283 fold + census: frame time 33.7/62.5/84.0 ms at 9/36/143 ms per foreign buffer (sublinear, slope ~0.33: neither flat timeslice nor FIFO); RT64 issues ~26 MTLCommandBuffer commits per frame (ROGUESQ_MTL_COMMITS=1), opt-in ROGUESQ_MTL_SKIP_EMPTY_WAIT=1 cuts them 31-36% with 0 fps change (12.2 vs 12.0 on-load, control 3/3) -> commit count is not the lever; the GPU's own inter-process policy sets our share. GPU-contention thread CLOSED; off-window gaps >=250 ms in these runs sit at the saturator's on->off edge (single-source; SUPERSEDED s7284).** **s7284 offline edge-gap census (tools/s7284_edge_gaps.py, all 17 s7277-s7283 toggle runs, no game run): 0 lit quiet-host freezes.** Gaps >=250 ms: CTL 52 (every SIGSTOP control 1021-1160 ms appears, 3/run), PRE 119 (route), ON 25 (the known no-QoS CPU-load freezes), off-window 31 = 27 black holds (luma 0-1) + 4 unlit fb relocations; ALL 31 carry FBSWITCH (the fb double-buffer pair relocates, e.g. L4 B51E00/AA3C00 -> A7CA00/A12600 ~2.6 s before the restart black hold; 0/52 controls do, so the flag is not trivially true). Only 1 gap lies <=2 s after an on->off edge (0.34 s, an fb relocation) -> H-edge-drain/H-cpu-edge refuted, H-quiet-freeze refuted; off-window gaps are scene-change transitions. G5c fully closed.
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
16. **Closed, reopen only on an owner report:** transition stalls (s7065; s7285 split all 158 real >=250 ms gaps of 17 rings with
    tools/s7285_gap_split.py: guest-side, presents <=10.6 ms keep flowing, RT64 render not late, one ~139 ms VI-silent MusyX stretch
    per gap; quiet L4 restart gaps 256-414 ms = retail waits + load), host self-time
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
  game window carry `# SOAK_NEEDS_IDLE=<secs>` (loop skips them on a busy/locked host; tools/agent/test_soak_idle_gate.sh). s7254: if nothing ran and only gated recipes wait, the loop polls up to SOAK_IDLE_WAIT=1800 s (every 30 s) for idle before starting the next iteration.
  An edited loop.sh now takes effect BEFORE the soak phase that follows the editing iteration (s7235 re-exec + RS64_LOOP_SOAKS_FIRST).
- Recent chronology: PORTING-STATE sessions 7047-7187; search bounded windows only.
