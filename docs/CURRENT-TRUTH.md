# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7334 (2026-11-14).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7306 text of this file (every headline paragraph s7192-s7229 with
all numbers, the WIDEWIN / dd8 / fog chronology s7262-s7306, the G5c freeze thread s7272-s7285) is archived
verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7307 maintenance)"; older text in "(s7187
maintenance)" and "(s6994 maintenance)". Grep there for any sNNNN.

## Headline

**Every engineering goal on the ladder is closed or awaiting the owner's look.** Nothing is broken at the
owner's recipe as far as any instrument can see; remaining items are owner judgements (list in Next steps).

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
  data in a spill block (dd>=6 hangar route) fetched the 0x80xxxxxx alias. 25-bit mask in rsp.hpp, ROGUESQ_RSP_DMA25=0 old (item 21).
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
Recent only; older entries in the PROJECT-OVERVIEW maintenance archives (s7307, s6994, s6900, s6870, s6759).
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
- s7286/s7288 "the terrain window binds from dd4; dd4->dd6 adds 1.8% cells". Believable: [s7233] in= sat at ~3550
  dd4..dd8. s7291: in= counts only the retail-equivalent 64x64 window (constant by construction); total cells grow +24%.
- s7283 "off-window gaps >=250 ms are the GPU saturator draining after SIGKILL". Believable: they followed lit holds
  near +381 s. s7284: that hold is the SIGSTOP control; the gaps are black fb-relocation transitions.
- s7247/s7259/s7262 "the WIDEWIN auto stack removes no visible ground". Believable: holes/seams scorers clean. They never
  scored the side edge; s7264 showed R=48 erased the side gain (fixed by R=88, s7266).
- s7230 "dd6 at 21:9 adds ~6.6 ms per task (H-dd)" and s7014-s7017 "WIDEWIN costs little at 21:9 dd4". Believable: the arms
  seemed to differ only in radius; s7231 2x2: WIDEWIN +4.5 ms, radius +0.7 ms. s7230 also ran on battery (x1.4, s7251).
- s7054/s7063 "L4 21:9 dd6 58.7-59.5 fps". Believable: whole-flight averages; s7230 heavy window flat 30 (battery);
  AC s7257: 60.0/s at 14.06 ms.
- s7227/s7228 "in-flight flat-30 under FPS60 is the game's own rate". Believable: rigid 33.3 ms swaps, free present path.
  s7229: the harness ran the diagnostic ucode path; owner path holds 60/s.
- s7180 "swaps 4700-5028 are LEVEL DESCRIPTION" / s7181 "Elite Rogues 0.047". s7183: it is Elite Rogues; residual =
  weave-reference combing while it scrolls.
- s7122 "4:3 picture off-centre". s7123: SCK pads the capture; in window points it is centred.
- s7120 "flight camera jumps 2-16 u". s7121: the join mixed cam objects; per-cam 0 such steps.
- s7113 "H-raymiss: collision surface ~0.2 u off the drawn mesh". s7114: common-mode rebuild bias; drawn == collision exactly.
- s7098 "near-wall flashes only with FPS60". s7108/s7109: same rate at 30 fps and full retail.
- s7102 "near-wall zig-zag is push vs clamp (H-fight)"; s7100 "FPS60 episodes 4.1x" (s7101: 1.6x, p=0.185).
- s7059 "transition stalls are audio-slot polling". s7064: waits are ~14% of the gap; remainder OS-silent.
- s7032 "the wall face occludes the craft at poses 0-4". s7033: eye above ~99% of culled cells.
- s7009-s7013 "WIDEWIN costs ~10-25 fps": harness LOG_PHASE probe path. Any harness timing since s6713 without
  G1E_FAST=1 PROBES=0 is suspect.
- s6990 "60.0 fps on all 19 levels at 16:9": FORCE_UNLOCK=1 clamps the cursor to level 1. Check `cur` / cursorMask.
- s6788-s6791 "G3e drops CLOSED" (reopened as G5b); s6895 "dd1 has no knife lines" (s6906: dd1 has the thickest).
- PORTING-STATE line 1862 "Fog contributes nothing" (s6904): true only of the early pre-flight scene.
- g3_aspect_crop scores s6879-s6881 scored pillarbox bars; "pinned pose" s6445-s6583 is attitude-only;
  "300 s hold" FPS60/dd>1 s6774-s6862 counted from boot (use inits= and flight_s=).

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
- Soak verdicts: `scratch/agent/SOAK-RESULTS.md`; read `alive_at_end` / `crashlines`, never rc. Recipes that
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
- Title plume parked; reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams. Positive control for every null; two
  independent lines before a conclusion enters this file.

## Next steps (single monotonic backlog)

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7307 into one sequence (the s7306 numbering
is in the s7307 archive). Active unit: NEXT.md.

1. **G5e fog: owner look.** ROGUESQ_DD_FOG_ALT=1,3,1 qualified at 16:9 and 21:9 (headline). Only if the owner
   asks for more haze at 21:9: sweep ke 2 / 2.5 with `tools/s7306_fog_219.zsh l1k2:1:1,2,1`.
2. **21:9 dd>1 left-edge sliver FIXED (s7310), qualified s7312, owner look pending.** s7312: FARMAX=0 pins the dome edge tris to x=0 on L1,
   L5 and L12 alike, the 32767 default never does (stream decode, same-pose L1/L5); s7311 soak 300 s L1/L5/L12 clean, 60/s, no frame-time cost.
   Sheets docs/owner_sheet_s7310_farmax.jpg + docs/owner_sheet_s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
   The s7312 "window showed another scene" datum was a harness artefact (s7313: a leftover game was alive and `pgrep|head -1` captured its window; tools/rs64_game_pid.zsh guard). Cause of the sliver: the dd-scaled projection far. With far above
   ~36-40k units (L1: far 8070.8 x4.5 clean, x5.0 pinned; dd6 auto and dd8 both above) the F5 clip emits the sky-dome edge panels pinned to
   fb x=0 with texture W 0/-0.0015 (vertical streaks); at far <= x4.5 the same panels arrive as normal guard-band tris (minx -230..-260, W sane).
   Two lines: RDP-stream W decode and presented near-white left-column count (608 vs 0) agree in all 12 same-pose arms. Not perspNorm, not the
   s6418 far clip (NOFARCLIP same), not aspect. H-geom (single-source mechanism reading): our opt-in far pushes dome w past the ucode's working
   range; retail never builds that far. Fix: **ROGUESQ_DD_FARMAX default 32767** (tools/apply_s7310_farmax.py, after apply_s6031_far; 0 = old;
   only bites when the far scale is active and never lowers below the game far, so dd1 is untouched). dd8 21:9 and 16:9 with the cap: sliver 0,
   stream identical to far x4; repeat arm pixel-identical; other diffs vs far x8 are only sky-dome periphery and clouds, horizon/terrain unchanged.
   dd8 horizon look DONE s7308 (sheet docs/owner_sheet_s7308_dd8_horizon.jpg).
3. **Owner decisions on defaults:** RETINA=1, QOS_ALL=1, DD_FOG_ALT, dd8 bundle. Never flip without the owner.
4. **G5i hangar re-entry (s6995), G5a Gerrard V crash (s6893; s6998 writeback audit clean), G5b terrain drops
   (FWDWIN far-loss fix, tools/g5b_fwdwin_seamless.py), G5d logo (s6903), G5f knife lines (s6906; sheets
   s7005/s7006), G5g hangar lens (s6907), G5h cutscene background (s6908-s6919): owner flight / look.**
5. **L15 21:9: owner re-flight after s6992 PTRMASK.**
6. **G1d close-out: owner judgement** (scratch/s6731/sheet_menus_owner.png); owner scope: why L7/L16/L17
   autopilot holds cycle the backdrop menu.
7. **Near-wall NEARLIFT, G3 21:9 holes (s7132-s7140), L4 cutscene SKYFILL_BOT (s7166): owner look.**
8. **Owner judgement / parked:** FPS60 feel, G3c sheets, native hangar geometry, rare dd4/dd8 gfx SIGBUS
   (single-source). Reopen on an owner report or side-effect failure.
9. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first.
10. **Rerun-after-change censuses (all CLOSED, 0 defects):** after a regen: tools/scan_selfbranch.py +
    tools/s7081_selfbranch_test, tools/s708[2-7]_* lowering, host-shim s7088/s7089; after a fixup edit:
    tools/s7090_fixup_statement_census.py (exit 1 = defect); after RSPRecomp/ucode fixups: tools/ucode_regen.sh
    `verify`, tools/s7093_su_census.py --controls; after rsp_vu*.hpp / DMEM: tools/s7092_vu_mem_test; after rsp DMA:
    tools/s7094_dma_test + s7094_dma_census.py; after dpc_bridge submit/defer/wrap: ROGUESQ_S7095_DPC /
    S7096_FWD=ctl / S7097_EDIT=ctl (missing/dup/order/unattributed must stay 0); after an rs64_s7239 edit:
    tools/s7241_merge_test/run.sh; tools/s7243_resume_test.zsh; loop: tools/agent/test_soak_idle_gate.sh.
11. **Closed, reopen only on an owner report:** transition stalls (s7065/s7285), host self-time (s7066-s7070),
    misnomer rename (s7080; tools/apply_symbol_renames.py), G1e residual (s6996), G5c freezes (s7285), GPU
    contention (s7283), WIDEWIN thread (s7271), Retina (s7224), window/aspect G1f (s7228).
12. **Harness one-game discipline: CLOSED (s7313-s7314).** Iteration tools take the pid from tools/rs64_game_pid.zsh (exactly one
    game or nothing; test tools/s7313_pid_test/run.zsh). loop.sh SIGKILLs any game alive at soak-phase start, before and after each
    recipe, and names the pids in SOAK-RESULTS ("leftover"/"foreign game killed"/"outlived"); test tools/agent/test_soak_idle_gate.sh.
    A SOAK-RESULTS kill line = some arm failed to reap its game: treat that run's frame-time numbers as contaminated.
13. **Retail RAM-size/upper-bound idiom class: CLOSED (s7315, static, single-source).** tools/s7315_retail_bound_census.py: 86 sites,
    0 unclassified; only size dependence is 4 MB vs more (framebuffer top, expansion flag 0x80130B63). Table in docs/HEAP-ADDR-AUDIT.md.
    Re-run after a regen (exit 1 = new unclassified site).
14. **Retail DATA-word bound class: CLOSED (s7316, H-clean).** tools/s7316_data_bound_census.py --ram: 303 sites, 41 globals, 4
    pointer-valued (DL pool limit/chunk, heap head), none ever holds a spill pointer; spill-injected dump flags 169 (control).
    Table in docs/HEAP-ADDR-AUDIT.md. Open edge: struct-field bounds (G via register base), see 15.
15. **Spill-pointer holders + class-B compares + class-C differences: CLOSED (s7317-s7320, 0 cross; class D s7321, item 16).** ROGUESQ_S7317_ALLOCMAP=1 +
    ROGUESQ_RDRAM_DUMP_BYTES=20971520; tools/s7317_spill_holders.py. dd8 21:9 L4: 22-120 live spill blocks, 42 owner types
    (scratch/s7317/d8_owner_table.txt). Top-byte shift class (32) spill-equal. Class B (182 slt/sltu): runtime ROGUESQ_S7318_BCMP
    (tools/apply_s7318_bcmp_probe.py, report tools/s7318_bcmp_report.py) 119/182 executed, 0 cross, ctl 3968/3968; 63 static
    (tools/s7319_bcmp_static_class.py). Class C (155 subu, tools/s7320_bdiff_sites.txt): tools/apply_s7320_bdiff_probe.py into the same
    classifier (idx 256+), report tools/s7320_bdiff_report.py: 98 executed, 0 cross, ctl 1398/1398; 57 static
    (tools/s7320_bdiff_static_class.py: 43 scalar, 14 same). Tables: docs/HEAP-ADDR-AUDIT.md.
16. **24-bit truncation class D: CLOSED (s7321, 0 H-alias).** Census class D (tools/s7317_field_compare_census.py) found 26 sites.
    Runtime probe tools/apply_s7321_trunc_probe.py (idx 512+), report tools/s7321_trunc_report.py: dd8 21:9 L4, 19/26 executed, 66M calls,
    0 spill sources, ctl 9313/9313 at 800173C0; L1/L12 soak (s7321_trunc_levels, folded s7322) same 19/26, 154M, 0 cross, ctl 25832/25832.
    The other 7 were classed statically (docs/HEAP-ADDR-AUDIT.md). Latent alias shape: commitMeshDrawBatchRefs rebuilds
    `(ref & 0xFFFFFF) | 0x80000000` and stores through it; its referents are DL-pool heap only. Re-check if the DL pool moves to spill.
17. **KSEG re-tag class E: CLOSED (s7322, static + evaluated, 0 H-alias).** Census class E: 404 sites, 0 unclassified (exit 1 on any):
    387 float->unsigned idiom (instruction-pattern check 387/387), 8 jump tables, 4 full-word sources (bit 24 kept by evaluation), 1
    paired with class D (runtime-clean), 4 read by hand (relocateSndPointer = s6993 mask site, 0xBD DL command). Table in
    docs/HEAP-ADDR-AUDIT.md.
18. **Address-derived table index class F: CLOSED (s7323, static + evaluated, 0 pointer sources).** tools/s7323_addr_index_census.py
    (`--top` adds k 23..31; selftest 6/6; exit 1 on unclassified): srl/sra 8..22 -> memory base 61 sites, 8..31 81 sites. Each site runs
    every heap and spill pointer through its index expression: 36 scalar sources, 20 bounded-safe masks, 5 spill-equal top-byte indexes,
    20 flagged (11 unbounded, 1 OVERFLOW, 4 ALIAS, 4 range-checked) all read by hand as data: ADPCM header, 23-bit pan fraction, JPEG 16.16,
    material flag fields, HOB record length, float->int, opcode decoder. Classes A-F close the spill-pointer-as-value edge (single-source
    static for E/F; linear scan misses indexes crossing branch joins or calls).
19. **RCP-visible spill references class G: REOPENED + FIXED s7327 (s7324 H-cpu-only held on the forced-level route only, see 21).** ROGUESQ_S7324_RCPREF=ctl + ROGUESQ_S7317_ALLOCMAP=1
    (src/rsp/s7324_rcp_spill.cpp; hooks: s7094 DMA census, rs64_dpc_record_submit), report tools/s7324_rcp_report.py (exit 1 on a
    hit). dd8 21:9 L4 205 s flight x3 runs, 0 crash: ~462M RSP DMAs + 40M RDP SETTIMG/ZIMG/CIMG, **0 direct spill addresses, 0 RDP
    aliases**; ctl 198/198 classes the live lowest spill block as direct and alias. Alias-only DMA hits (24-bit address inside a live
    spill block's 16 MB-lower image, no live heap block) are all raw tag 0x80 or static: gfx ucode_data 0x80038D00, state-setup
    sub-DL 0x80037658, audio ucode_data 0x800A4E00 (named retail statics), plus 40k audio sample reads in heap GAPS (no live rs_malloc
    block, tag 0x80): instrument artefact, closed s7325 (item 20). Spill audit family A-G done.
20. **Audio "heap-gap" reads: CLOSED (s7325, instrument artefact, retail path named).** The retail scene-change bulk free never calls
    rs_free: coalesceFreeHeapBlocks (0x800022F8, misnamed) frees every persistent-heap block (head 0x8010FF18) whose header tag lacks
    0x80; waitForPrevFrameDone (0x8000A86C) -> 0x80001880 zeroes head 0x8010FEFC and buildHeapFreeList rebuilds the temp / overlay-BSS
    arenas. The s7317 map kept 531 stale entries nested in live guest blocks, shadowing them; every distinct "gap" address was inside a
    guest ALLOCATED block (independent heap walk), dd1 4:3 identical. tools/apply_s7325_heaprebuild.py (buildHeapFreeList hook +
    coalesce wrapper -> rs64_s7325_heapsync, ALLOCMAP-only) re-syncs: stale 531 -> 1, gap reads 10.5k -> 46, class G re-run clean.
    Any future ALLOCMAP/HEAPLOG consumer gets the corrected map; report tools/s7325_gap_report.py.
21. **Spill scene-reset leak: FIXED + qualified (s7326-s7327).** Soak s7326_spill_levels: forced L4 + L15 dd8 21:9 300 s, 0 crash, 0 arena
    full. Owner hangar route (scratch/s7326/run.zsh, 650 s each, s7327): dd4 16:9 (owner recipe) spills nothing big (peak 0xC560, 0
    releases: fix inert there), dd6 21:9 WIDEWIN spills 2x 0x19DF70 per mission load (peak 0x33BEE0, released at the reset), dd8 16:9
    spills the 0x2DFF00 level buffers (peak 0x688B50: the old 4 MB arena would fill even with the release). All 0 crash / 0 arena full;
    ctl seen == resets in every arm. **Class G re-run on the dd8 16:9 route FAILED s7324's H-cpu-only:** 47-75k gfx RSP DMA reads at
    raw 0x81xxxxxx (len 0x20, stride 0x19) inside the spill 0x2DFF00 blocks (owner initGridLayerFromLevelData < loadLevelAssets <
    initMission); the RSP DMA masked DRAM_ADDR to 0xFFFFF8 so they read the 0x80xxxxxx alias: wrong bytes in 49152/49152 compared reads
    (ROGUESQ_RSP_DMA25_CTL=1). Fix default on: 25-bit mask 0x1FFFFF8 + 32 MB bound in librecomp rsp.hpp (rs64_s7327_mask,
    ROGUESQ_RSP_DMA25=0 old); direct_other=0 in every run (no non-spill DMA carries bit 24). Visible: YES (s7328 dd8 16:9, s7329 dd6 21:9).
    s7329: the dd6 21:9 0x19DF70 blocks are the s6893 tile-variant pool (942 x 72 x 25; dd8's 0x2DFF00 = 942 x 128 x 25), gfx-read:
    forced to spill, 192k bit-24 reads all differ via the 24-bit alias (neg control: sampled non-spill reads 0 differ), old mask
    garbles near terrain 26.2% px, fix pixel-identical to no spill (docs/owner_sheet_s7329_dd6_dma25.jpg). Thread CLOSED.
    Pose any spill question with ROGUESQ_SPILL_FORCE=<size> (forced-route sizes differ: L1 dd6 21:9 pool 0x1CC000; read the
    "[s7328] big req" lines). RCPREF does not see SPILL_FORCE blocks (control fails, hits land in direct_other).
22. **Audio reads/writes into freed blocks: CLOSED (s7330, named, 0 live overlap).** The s7325 "song-channel arrays" are the synth's
    double-buffered audio command lists (task data_ptr = the freed 0x1E30 block). Class 1 (boot): the first coalesceFreeHeapBlocks
    (after menuOverlayInit) releases the untagged initN64RspMixer buffers; the synth keeps building 4-7 tasks into them (+15..+114 ms,
    every hit task submitted AFTER the free: H-next-task), the ucode writes 0x198 B of voice state back into the freed 0x298 block.
    Same in dd8 21:9 and retail-settings arms. Class 2: one task in flight across the rs_free inside waitForMusyXAudioTaskDone (countdown
    is decremented at build time, not SP completion). No live block overlapped in either run. Retail code shape; oracle cannot reach the
    transition (single-source for retail). ROGUESQ_S7324_RCPREF=ctl + ALLOCMAP -> build/rs64_s7330.log, tools/s7330_task_free_report.py.
    Follow-up audit (NEXT.md): every block the scene reset frees that still changes before reallocation.
23. **Scene-reset dangling writers: CLOSED (s7331, H-audio-only).** ROGUESQ_S7331_RESETW=1 + ALLOCMAP + RCPREF=ctl
    (src/rsp/s7331_reset_writer.cpp; report tools/s7331_reset_writer_report.py, `--s7330 <log>` orders stale DMAs). Every block a reset
    drops is re-compared per 64 B for 2 s with RSP/PI/CPU attribution and the guest heap walk at first change. Forced L4, dd8 21:9 x4 +
    retail settings: the only writes into guest-FREE memory are the boot initN64RspMixer buffers (item 22); 0 stale-owner audio DMAs
    after reallocation (last stale DMA 0.075-6.5 ms BEFORE the realloc). Other "post-free" writes (loadDatFile 12-B blocks 0x809B6010)
    are inside a guest-allocated flags&4 carve block = the per-scene framebuffer / temp pool (parseImageFile, rt64_writeback).
    Abort route too (s7332): the s7331_abort_resetw soak's rc=0 was grep's, and its 3 "NEW" rows were the gfx RDP FIFO in the carve
    (a line-start guest-walk artefact). With the walk on the first changed byte: 3 reruns, rc 0, other owners 0, stale 0.
24. **flags&4 carve block: CLOSED (s7332-s7334).** coalesceFreeHeapBlocks (0x800022F8, misnamed: the scene heap reset) writes the
    per-scene fl=6 carve header (pc 80002510/18/5C, 800023AC/D8) holding framebuffers, temp arena and gfx RDP FIFO, and re-terminates the
    persistent arena with fl=8 sz=0 at hi-0x10 (pc 800024A4/A8/B0, s7334 store watch), hi = the fb-layout bound from 0x80000DD4 (caller
    0x80001430) or global 0x801163E4. Above the sentinel = the scene's fb / FIFO tail (rt64_writeback writes it), never heap (H-top; H-stale
    and H-trim refuted). Host map: carve registration (ROGUESQ_S7332_CARVE), walk-down + guest-header keep (ROGUESQ_S7333_KEEP), class 5
    "guest non-heap tail" in rs64_s7325_gap with guest=1 (ROGUESQ_S7334_CLASS5=0 old). Abort route s7334: in-carve FIFO host-live 19/19,
    above-heap FIFO class 5 6/6, `tools/s7333_carve_report.py <log> --class5` rc 0. Point store watch: ROGUESQ_STORE_WATCH_PTS=<p>,...
25. **Soak recipes take the analyser's own rc** (`${pipestatus[1]}`), never a downstream grep's (s7332).
26. **fb-layout bound consumers: CLOSED (s7335).** `tools/s7335_fb_bound_census.py` (68 sites, 0 unclassified, control PASS): every
    guest reader of 0x801163E4/63D8..63F8 derives from partitionFramebufferMemory (top = 0x80000000|osMemSize, 4 MB mode 0x80400000);
    the coalesce-stored hi 0x8010FF08..14 is write-only; walkers stop at the sentinel. Guest H-clean (docs/HEAP-ADDR-AUDIT.md class H).
    Host H-overlap FIXED: the DLPOOLX arena [0x81000000-MB, 0x81000000) starts exactly at the OSMEM-12 guest top, so DLPOOLX_MB 5..8
    or OSMEM_MB 13..16 overlapped the guest heap/fb tail (arm o8: chunks at 0x80800000, latent, 131 s no crash). rs64_s7335_dlpool_cap
    clamps it to the guest top (`[s7335]` line, ROGUESQ_S7335_CLAMP=0 old); default unchanged (L1 dd8 21:9 def/c8/o8, 0 crash each).
27. **Next unit (NEXT.md): host arena layout census** - every host-owned guest-address range (spill, DLPOOLX, BIGARENA, s6127, RT64
    writeback, ...) vs the guest layout and each other, per env combo; one static table + a startup `[s7336] layout` line.
28. **When 1-27 offer nothing an agent can do:** take the next open ITERATION.md 3c rung (G5 renaming sweep,
    item 4) or a new idiom-class audit; do not write a backlog-exhausted block.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7187-7307; search bounded windows only.
