# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7378 (2026-11-14).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7369 text of this file (every audit class s7315-s7369 in full) is archived verbatim in
PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7370 maintenance)"; the full s7306 text (every headline paragraph s7192-s7229 with
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
- Slow builds (TSan/ASan): `ROGUESQ_AUTOPILOT_CLOCK=frames ROGUESQ_AUTOPILOT_FPS=58` (FPS60) keys autopilot to fullsyncs,
  but front-end screens are VI-timed, so the route still diverges at TSan speed; gate with `<s>:w<width>` events (s7371).
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

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7370 into one sequence 1-17 (the s7369
numbering 1-28 with sub-items 27b-27zi is in the s7370 archive).

1. **ACTIVE (NEXT.md, HYPOTHESIS-ID rt64-resize-destroy-vs-present): class AU2, the workload thread's resize/fb-config
   teardown (threadConfigurationUpdate: renderFramebufferManager/targetManager destroyAll + fbManager.destroyAllTileCopies under
   managerMutex only, inside configurationMutex) vs the present thread using colour targets under workloadMutex (s7377).**
   Fires on every swap-chain resize (fullscreen toggle, ASPECT=auto window moves). Lock-order table + a resize stress arm under TSan.
   **AU CLOSED s7378** (`tools/s7378_shared_res_census.py --check` rc 0, 20 fields, 192 accesses; hand verdicts
   tools/s7378_shared_res_reviewed.tsv): 13 GUARDED (all config fields under configurationMutex, incl. targetRate/resolutionScale:
   threadConfigurationUpdate holds it for its whole body), 1 CONFINED, 6 fixed: swapChainRate (port get_display_framerate read
   unlocked = the s7354-s7377 TSan BENIGN row), viOriginalRate, interpolatedFramesIndex -> std::atomic; the per-present
   interpolatedFrames counter reset and the present's two count reads, and the interpolatedColorTargets grow, now under
   interpolatedMutex (ROGUESQ_S7378_SHLOCK=0 = old). Control: `--rev HEAD` (upstream) flags the unlocked rows. Smoke both arms crash 0,
   14 resets, 10800 presents each; TSan rc 0, CTL 3011, swapChainRate group gone (was x1 in s7375/s7376/s7377 runs), 0 SharedQueueResources rows.
   **AT CLOSED s7377** (`tools/s7377_present_lock_table.py --check`): present-thread colour-target get + GPU pass now under
   workloadMutex, colorImageAddressVector snapshotted under managerMutex (ROGUESQ_S7377_EARLYLOCK=0 = old).
   **AS2 CLOSED s7376**: port present-thread inserts into targetManager/fbManager now under workloadMutex (ROGUESQ_S7376_PQLOCK=0 = old).
   **AS CLOSED s7375** (tools/s7375_nolock_threads.py + s7375_nolock_reviewed.tsv, `--check`): the 98 s7366 NOLOCK containers,
   walker + hand verdicts CONFINED 37 / CALLER-LOCKED 16 / NOT-SHARED 15 / HANDOFF 9 / INIT-ONLY 6 / GUEST-SERIAL 6 / CFG-DEAD 5
   (RT64 texture-replacement-pack state, inspector-only: upstream race if a pack were loaded) / FIXED 1: the depth-hist diag
   (ROGUESQ_FLOOR_DEPTH_DIR, rt64_framebuffer_renderer.cpp) reached from both FramebufferRenderer instances (State on the gfx
   thread, WorkloadQueue on the RT64 render thread) now locks g_depthMu, gate at static init. Smoke clean, diag control 12544
   events; TSan arm 0 reports in that file, CTL fires (hangar-only coverage; two-thread reach single-source, static).
   **AR CLOSED s7374** (tools/s7374_lazy_static_census.py + s7374_lazy_static_reviewed.tsv, `--check`): 236 lazy-init statics,
   27 COMPANION/PTR rows thread-reviewed (SINGLE 8, GUEST-SERIAL 11, NOT-LAZY 7), 1 real multi-thread site FIXED: rs64_s7012_cap
   (guest + gfx_thread under S7026_SUB / G1E_TRING) now a magic static (could read the cap tables as zeros or v[3] out of range);
   172 SIMPLE rows are idempotent single-word values, not converted. TSan arm with the gfx caller armed: 0 reports on it, CTL fires.
   **AQ CLOSED s7373** (tools/s7373_aq_gate_table.py). Re-cut rows on the tree the coverage build used (tool exits 3 on stale rows).
2. **G5e fog: owner look.** ROGUESQ_DD_FOG_ALT=1,3,1 qualified at 16:9 and 21:9 (headline). Only if the owner asks for
   more haze at 21:9: sweep ke 2 / 2.5 with `tools/s7306_fog_219.zsh l1k2:1:1,2,1`.
3. **21:9 dd>1 left-edge sliver FIXED (s7310, ROGUESQ_DD_FARMAX default 32767, 0 = old), qualified s7312: owner look.**
   Far above ~36-40k units makes the F5 clip pin sky-dome edge panels to fb x=0 (two lines: RDP W decode + presented
   left-column count, 12 same-pose arms; mechanism single-source). Sheets docs/owner_sheet_s7310_farmax.jpg,
   s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
4. **Owner decisions on defaults:** RETINA=1, QOS_ALL=1, DD_FOG_ALT, dd8 bundle. Never flip without the owner.
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
11. **Rerun-after-change censuses (all CLOSED, 0 defects):** after a regen: tools/scan_selfbranch.py +
    tools/s7081_selfbranch_test, tools/s708[2-7]_* lowering, host-shim s7088/s7089; after a fixup edit:
    tools/s7090_fixup_statement_census.py (exit 1 = defect); after RSPRecomp/ucode fixups: tools/ucode_regen.sh
    `verify`, tools/s7093_su_census.py --controls; after rsp_vu*.hpp / DMEM: tools/s7092_vu_mem_test; after rsp DMA:
    tools/s7094_dma_test + s7094_dma_census.py; after dpc_bridge submit/defer/wrap: ROGUESQ_S7095_DPC /
    S7096_FWD=ctl / S7097_EDIT=ctl (missing/dup/order/unattributed must stay 0); after an rs64_s7239 edit:
    tools/s7241_merge_test/run.sh; tools/s7243_resume_test.zsh; loop: tools/agent/test_soak_idle_gate.sh.
    After any host-code edit: every class census in item 14 with `--controls` (exit 1 = survivor or failed control).
12. **Closed, reopen only on an owner report:** transition stalls (s7065/s7285), host self-time (s7066-s7070),
    misnomer rename (s7080; tools/apply_symbol_renames.py), G1e residual (s6996), G5c freezes (s7285), GPU
    contention (s7283), WIDEWIN thread (s7271), Retina (s7224), window/aspect G1f (s7228).
13. **Harness discipline (CLOSED s7313-s7314, s7332):** iteration tools take the pid from tools/rs64_game_pid.zsh;
    loop.sh SIGKILLs any game alive around each soak recipe and names it in SOAK-RESULTS (a kill line = that run's
    frame times are contaminated). Soak recipes take the analyser's own rc (`${pipestatus[1]}`), never a grep's.
14. **Idiom-class audits s7315-s7366: ALL CLOSED** (full text, numbers and controls: s7370 archive). Census tool per class:
    - guest-side: retail RAM bound s7315 (tools/s7315_retail_bound_census.py, single-source); DATA-word bound s7316
      (s7316_data_bound_census.py); spill holders / class B compares / C diffs s7317-s7320 (ROGUESQ_S7317_ALLOCMAP=1,
      s7317_spill_holders.py, apply_s7318_bcmp_probe.py); D 24-bit truncation s7321 (s7317_field_compare_census.py,
      s7321_trunc_report.py); E KSEG re-tag s7322; F addr-derived index s7323 (s7323_addr_index_census.py); G RCP-visible
      spill refs s7324 -> FIXED s7327 (s7324_rcp_report.py); audio heap-gap reads s7325 (artefact); audio freed-block
      access s7330 (s7330_task_free_report.py); scene-reset dangling writers s7331 (s7331_reset_writer_report.py);
      flags&4 carve s7332-s7334 (s7333_carve_report.py); fb-layout bound consumers s7335; host arena layout s7336
      (s7336_host_arena_table.py); R stale 8 MB bounds s7337; M 8 MB masks s7338; N 16 MB masks s7339 (latent);
      O KSEG0 16 MB bounds s7340; P top-byte tests s7341; L zero-extended bases s7361 (apply_s7361_sext_bases.py);
      AM raw rdram+X s7362 (s7362_rdramraw_census.py). Tools are tools/s73NN_*_census.py.
    - host C/C++: S addr-indexed tables s7342 (single-source); T fixed buffers s7343; U wrap-prone bounds s7344;
      V mul overflow s7345 (single-source); W signed len s7346; X float->int s7347; Y div/mod s7348; Z shift s7349;
      AA overlapping memcpy s7350; AB cast loads s7351; AC signed overflow s7352; AD bool/enum s7353; AE data races s7354
      (TSan, tools/build_tsan.sh; COV=1 coverage arm s7372); AQ lockset s7366/s7373; AR lazy-init statics s7374; AS NOLOCK containers s7375, AS2 lockless files s7376 (AT present-thread maps open); AF signal safety s7355; AG unchecked alloc s7356;
      AH I/O lengths s7357; AI env parses s7358; AJ string copies s7359 (src/main/rs64_apf.h); AK guest string reads
      s7360; AN fixed arrays s7363, AO heap buffers s7364, AP container invalidation s7365 (each: census + independent
      reviews + ASan + gate); AQ cross-thread containers s7366 (static lockset census) + runtime half s7372/s7373 (COV=1 arm,
    tools/s7372_aq_runtime_cross.py, tools/s7373_aq_gate_table.py): CLOSED.
15. **Default-on fixes from the audits and TSan thread (=0 / old value restores the previous behaviour):**
    ROGUESQ_SPILL_RESET + 8 MB spill arena 0x81000000 (s7326, SPILL_MB=4 old); RSP_DMA25 (s7327); S7334_CLASS5;
    S7335_CLAMP; S7336; S7337; S7339; ALTSTACK (s7355); S7358_ENVCHECK; S7364_WLRESET; CF0_DUPDROP (s7367, guest
    video-ack deadlock = the s6993 boot freeze mechanism under starvation; host-load soaks 5/5 clean in both arms);
    DLPOOLX_ARM_REBUILD (s7368, pool grows armed at the game's own pool init, not a frame-count proxy);
    build_tsan ucode exemption (s7369, ROGUESQ_TSAN_UCODE=ON old). Detail per session in PORTING-STATE.
16. **Next audit candidates (when 1 closes):** any new arena or pointer layout re-runs items 11/14 with --controls; a
    census whose rows are cached across sessions must re-cut them on the measured tree (s7373 stale-row lesson).
17. **When 1-16 offer nothing an agent can do:** take the next open ITERATION.md 3c rung (G5 renaming sweep,
    item 4) or a new idiom-class audit; do not write a backlog-exhausted block.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7307-7370; search bounded windows only.
