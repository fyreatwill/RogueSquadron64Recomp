# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7464 (2026-11-16).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)". Grep there for any sNNNN.

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
Recent only; older entries in the PROJECT-OVERVIEW maintenance archives (s7307, s6994, s6900, s6870, s6759).
- s7418 "32 live cache ops". Believable: RecompiledFuncs census with a passing liveness control. s7419: its liveness keyed on objdump
  names, so 147 renamed functions were `nofn`; one live CDE (clearMemory16ByteBlocks 0x8000041C, boot) was skipped -> 33, still safe.
- "0 live cache ops" (s7405 class BO). Believable because the census ran with a control that passed (Status/Count/Compare rows),
  but that control never exercised `cache`: mips64-elf-objdump prints cache as .word, so the row could not fire. s7418 on
  RecompiledFuncs: 32 live (CDE 0x0D + HWB-D 0x19 only), no-op-safe. Class BO's FR/RM/FS conclusions stand.
- "FCSR.FS vs host FZ: known and left, ROGUESQ_FTZ stays opt-in" (s6013/s7087). Believable because the s6012 lvl1 holds
  were clean in both arms; but no instrument ever asked whether denormals occur. s7405 FPSR witness: they do (game thread, in
  flight), so FTZ is now default on (=0 old).
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
- Title plume parked; reopen only on new evidence.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams. Positive control for every null; two
  independent lines before a conclusion enters this file.

## Next steps (single monotonic backlog)

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7417 into one sequence 1-20 (the s7416
numbering 1-27, with class sub-items AQ-BP under item 1, is in the s7417 archive).

1. **Classes CC-DH s7420-s7451: ALL CLOSED** (full text, numbers, controls, tool flags: PROJECT-OVERVIEW "(s7452 maintenance)").
   m6 stall-measure series (DN-DR) CLOSED s7463. DS CLOSED s7465. DT CLOSED s7466 (soak PASS). DV CLOSED s7466. Next: see NEXT.md. One line each:
   - **DV s7466 remaining clang-analyzer crash families (UAF/double-free unix.Malloc+cplusplus.NewDelete, MismatchedDeallocator,
     DivideZero, BitwiseShift, StdCLibraryFunctions, Stream, BlockInCriticalSection), CLOSED:** tools/s7466_analyzer_rest_census.py
     --controls (planted lines 3-8 PASS) rc 0 over 150 TUs: 0 UAF/double-free/mismatch; 6 sites = 2 fixed (main.cpp s4243 PCM
     double getenv, s7106_rsptri fopen(e) null-safe), 4 reviewed (events.cpp:1924 static-const hz FP, rt64 dumpRDRAM DEAD no
     caller, main.cpp:8132 one-shot fgets under mutex, s7064 env-gated FP). Unscored counts: DeadStores 263, NullPassedToNonnull 2.
   - **DT s7465 host null-pointer derefs (analyzer core.NullDereference/CallAndMessage/NullArg), CLOSED (s7465_dt_guard_flight soak PASS s7466: L4+L12 dd4 alive, 0 crash/stall, fillrect_null=0 both arms):**
     tools/s7465_nullderef_census.py --controls (s7463 TU scope + runner, null-family regex; planted control lines 3/4/5 PASS) rc 0,
     11 sites: 1 GUARDED (rt64_framebuffer_renderer.cpp FillRect read chosenTarget->width when the fbStorage has neither colour nor
     depth target; writer RenderFramebufferManager::get() with both keys empty; the null-colour case is reached in this port, the
     both-null case never observed -> skip + `[s7465] fillrect-null-target` log, census no longer flags it), 1 KNOWN-parked (plume
     createFramebuffer null colour attachment = s5377 title plume), 2 INTENTIONAL (crash-reporter controls), 7 FP with the invariant
     written in tools/s7465_nullderef_reviewed.tsv (Tier2 flag re-read, env-gated getenv derefs, draw-without-pipeline contract).
     Regression soak s7465_dt_guard_flight queued (L4+L12 dd4 HOLD=150, fillrect_null count expected 0).
   - **DU s7464 quiet-arms spec split, CLOSED:** g1e_owner_quiet_arms.zsh splits ARMS on whitespace, so s7463_padhash_flight's
     "4:cnt:A=1 B=2" ran 4 arms (two named "" with dd=<env assignment>); the 2nd "" arm overwrote log_.txt, cnt data lost, CONTROL FAIL
     on a phantom arm. Now every spec is validated first (dd numeric, arm [A-Za-z0-9_]+, unique; else exit 3, never re-queued);
     tools/agent/test_quiet_arms_spec.sh 8/8 (the s7463 spec is the negative case); s7243 resume test still passes. Scan of 1317 done
     recipes: s7463 was the only g1e victim. Incidental in-flight datum (surviving "" arm = PADCOUNT=ctl, L1): drawcallkey
     distinct_raw 2277124 vs distinct_fixed 2266 over 2.36M calls -> the planted control fires in flight too. Re-queued s7464_padhash_flight.
   - **DS s7463 host uninitialized reads + missing returns, CLOSED s7465:** tools/s7463_uninit_census.py --controls
     (150 in-scope TUs from compile_commands: src/, ultramodern, librecomp, rt64 common/gbi/hle/render/rhi/preset, plume_metal; line A
     clang -Wsometimes/-Wconditional-uninitialized/-Wreturn-type/-Wdangling, line B clang static analyzer; planted control flagged by both)
     rc 0: 5 compiler sites FP-by-construction (rsp.hpp byte-loop loads, CTC2 total switch; tools/s7463_uninit_reviewed.tsv), 1 analyzer site
     REAL: XXH3 over ReinterpretHashData's 4 uninit tail padding bytes (rt64_state.cpp:1891). Class sweep of every raw-bytes struct hash
     (tools/s7463_hash_layouts.py, record layouts from clang): 7 structs, 3 padded = ReinterpretHashData 36-39, FramebufferTile 6-7
     (fb tile-copy cache key), DrawCallKey 84-87 (every draw call, preset cachedKeyMap never cleared). All 3 now hash through
     rs64_s7463_hash (padding zeroed on a copy; ROGUESQ_S7463_PADFIX=0 old). Runtime (title+attract, same build, ROGUESQ_S7463_PADCOUNT=1):
     padding nonzero on 100% of calls (dck 524288, fbtile 8192) but distinct_raw == distinct_fixed (651/651, 18/18) -> H-const (stable
     garbage, no split keys yet; latent, depends on stack contents); ctl (=ctl plants varying padding) raw 511270 vs fixed 651, fixdiff 0.
     Flight (s7464_padhash_flight, L4 cnt / L1 ctl dd4 150 s, CONTROL PASS): drawcallkey cnt 9.18M calls, padnz 100%, distinct_raw
     2922 == fixed 2922 -> H-const in flight too; ctl raw 4.0M vs fixed 2307; reinterpret + fbtile 0 calls in flight (H-unreached).
     CLOSED s7465: fix is latent-only (no cache fragmentation observed), stays default on. Latent, no callers: DrawCallKey::operator==
     returns memcmp() (true when DIFFERENT). Analyzer also lists null-deref/dead-store findings (not this class; candidate class DT).
   - **DR s7462 H-void (m6), CLOSED s7463:** s7462_m6_void_holds_ctl CONTROL PASS (P void_holds=1, C 0). void attempts (notitle/nohangar/nomission/died_in_verify) were retried with stalls unscored, so a
     pre-gate held frame (s6993 boot-freeze shape) vanished behind a later good attempt. fail() now scores each void log with
     vilog_stalls.py (keys line gains fs_holds=/max_fs_hold_vi=), every summary carries void_holds=<sum>, soak_verdict_fields counts
     void_holds>0 as a stall arm; M6_VOID_BLIND=1 old (mutation). tools/s7462_m6_void_holds_test.zsh 11/11 (planted + real s61 held log,
     advancing + real s7450 void log, sum, mutation, verdict). Census of the 15 surviving fail_att logs: 0 holds (11 scored, 4 no fs=).
     Real-game control queued: soak_queue/s7462_m6_void_holds_ctl.sh (P plant 10,150 MAXATT=1 -> void_holds>=1; C clean -> 0).
   - **Stall-measure series DN/DO/DP/DQ CLOSED s7462:** s7461_m6_verify_window_ctl CONTROL PASS (mission t=71, stall t=156,
     vi_stalls30s=1 fs_holds=1 max_fs_hold_vi=2368, alive_at_end=1).
   - **DQ s7461 H-window (m6):** s7460_plant_hold_ctl folded: g1e arm PASS (vi_stalls30s=1 max_vihold_ms=39916); m6 arm CONTROL
     FAIL only on vi_stalls30s=0 while offline fs_holds=1 max_fs_hold_vi=2368 (~39.5 s). Cause is none of the s7460 hypotheses: the
     m6 live poller started only AFTER the 130 s mission-verify sleep (gate t=72 s -> polling from ~202 s), and the plant ran
     120-160 s, inside it. Any hold in mission t 0-130 s was unscored live (offline fs_holds still saw it). Fix: m6_god_common.sh
     polls vtick through the verify window (M6_VERIFY_BLIND=1 = old sleep, mutation). tools/s7461_m6_verify_window_test.zsh 3/3
     (held -> stall, advancing -> 0, mutation -> 0). Real-game re-control queued: soak_queue/s7461_m6_verify_window_ctl.sh.
   - **DP s7460:** ROGUESQ_PLANT_HOLD=<s>[,<dur>] (main.cpp rs64_diag_plant_hold_tick, beside PLANT_EXIT; default dur 40) blocks the
     guest thread once inside osViSwapBuffer_recomp while host VI keeps ticking: the in-game held-frame positive control. Fired in
     both arms of s7460_plant_hold_ctl (begin/end lines); both scorers (m6 fs_holds, g1e ring) flagged it.
   - **DO s7459 H-blind (m6):** m6_god_common.sh (g1_level_coverage_common: 25 of the last ~60 recipes; s7263/s7272/s7277 cat its summary)
     scored vi_stalls30s by [vi] row COUNT, but rows print every 64 VIs whatever the game does: a held frame with VI ticking read 0.
     Now the newest row's fs= (M6_STALL_LINES=1 old) + summary fs_holds/max_fs_hold_vi (tools/agent/vilog_stalls.py, fs unchanged
     >=1800 VIs); verdict counts fs_holds>0 as a stall; dead arm vi_stalls30s=na. Census 321 logs: 221 clean (max hold 1216 VIs ~20 s,
     loads), 90 no fs, 10 flagged = s61_death_repro run4 (fs=2199 held 3776 VIs) + 9 s43xx boots stuck fs=0. Test
     tools/s7459_m6_stall_test.zsh incl. 2 mutation controls + real-log control. s7458 SIGSTOP soak: CONTROL PASS (ok 0, stp 1 @35 s).
     Remaining stall_na: none in live launchers (boot_freeze_hunt frozen=, g1e ring, m6 fs).
   - **DN s7458 H-blind:** g1e arms now score vi_stalls30s from their present ring (tools/agent/ring_stalls.py): present gap >= 30 s, OR
     presents flowing with the VI origin unchanged >= 30 s, OR a silent ring tail before a live arm's SIGKILL. Gaps alone are blind: the
     s6993 L4 boot freeze held one origin 235 s with a max present gap of 77 ms (it agrees with that session's log, fs stuck at 273).
     The census of 374 historical rings found that 1 episode and nothing else (365 at 0, 8 empty; normal max hold 17.4 s). Fake-ring tests:
     s7453_harness_death_test.zsh 33/33, including 2 mutation controls. Real-game SIGSTOP control queued (s7458_ring_stall_ctl).
   - **DM s7457 H-few:** 5 live launchers put no per-arm tag= line in the soak log (g1e_owner_quiet_arms 64 recipes, boot_freeze_hunt 11,
     s7277 6, s7263 5, s7272 1; 72/103 logs arms=0). All now emit one; verdict: frozen=1 = stall arm, trailing stall_na=<k> (arms with no
     stall measure; g1e arms are stall_na=1). tools/s7453_harness_death_test.zsh 25/25 incl. 2 mutation controls.
   - **DL s7456 H-few:** rc vs per-arm summaries over 30 summarised soaks: 2 misreads (s7449 false fail, s7452 planted dead arm read
     as rc=0). loop.sh verdict line now appends tools/agent/soak_verdict_fields.sh fields. fatal_patterns `abort` word-bounded (s7331_abort
     tag lines scored fatal=2) + `Abort trap`; fatal_scan selftest 20/20, test_soak_idle_gate.sh 20/20, both with mutation controls.
   - **DK s7455 H-none in data:** summary pass checks were prefix matches (`grep -q 'inits=1'` s7448/s7449, `*exitrc=1*` s7450-s7452
     passes exitrc=134); 0/11740 historical checks over 2348 m6 summaries flipped. New recipes score with
     `sh tools/agent/summary_field.sh $D/summary <key> eq|le|ge|is <v>` (exact key, selftest tools/agent/test_summary_field.sh 21/21).
   - **DJ s7454 H-none:** inits= was always per-process (each attempt rewrites run.log), so inits>1 = same-process mission restart;
     m6 summaries now add launches=$att mission_restarts=<call#>=2 count> (restart-control in harness; tools/s7454_restart_test.zsh
     6/6 incl. real s7449 L4=1/L10=0, mutation control caught). 0 live templates gate on inits=1 (2 one-shot done recipes only).
   - **DI s7453 H-few:** 4 of 6 live launchers passed a dead game: boot_freeze_hunt.sh (silent EXITED -> now bad=1 exitrc=),
     g1e_owner_quiet_arms.zsh (alive=0 exit 0 -> done line fatal=, exit 1), s7272/s7263 (old CRASH grep -> fatal_patterns.txt,
     s7263 rc=1). 47 fail()/retry copies are dead (newest ref <= s5921). Test tools/s7453_harness_death_test.zsh 13/13.
     s7452 tee fix run-verified (s7452_fatal_harness rc=0). s7449 L4 rc=1 = same-process mission re-init (inits=2, endMissionCleanup), not a crash.
   - DH s7451 H-none (Debug build): all 13 live exit/abort sites print a fatal_patterns line; NDEBUG pair hardened (selftest 19/19).
     m6_god_common.sh died_in_verify is now terminal (DIED_RETRY=1 = old): post-gate deaths used to be retried as void attempts.
   - **s7452 harness fix:** since s7450 (d354bfbdf) m6_god_common.sh:94 had `# comment | tee $OUT/summary`, so NO passing run wrote
     a summary; s7449/s7450/s7451 control-arm "failures" (arm C summary missing) were this, not the game. Re-queued s7452_fatal_harness.
   - DG s7450 H-few: shared tools/agent/fatal_patterns.txt + fatal_scan.sh feed m6_god_common.sh (+exitrc), g1e_level_fps.py,
     g1_objective_response_run.py; ROGUESQ_PLANT_EXIT=<s> KIND=switch|quick|silent plant.
   - DF s7449 H-few: rs64_diag_keep checks formatted "%s" text (ROGUESQ_PLANT_FAIL plant). DE s7448: diag_keep passes
     [initMission]-class prefixes. DD s7447: include/rs64_diag_route.h force-included (RS64_DIAG_ROUTE, default ON), qualified L4/L7/L12.
   - DC s7446 spill bump line; DB s7445 burst latch (apply_s7445); DA s7444 periodic print latch; CZ s7443 hooks 0.022 ms/f;
     CY s7442 probe-gate census; CX s7441 rs64 census + rs64SkipDraw latch; CW s7440 image-word op test at call site;
     CV s7439 decodeTriangles shade work gated (G1E_TRIM=0 old). All diagnostic-only, no guest store changed.
   - CU-CP s7433-s7438 cost censuses by /usr/bin/sample: H-known/H-free/H-tail, no change needed.
   - CO s7432 generated-C fprintf routed via include/rsp_dpc_macros.h; CN s7431 per-frame stderr writer fixed (39.5 MB/260 s cut);
     CM s7430 rs64_s6892.log rotation; CL s7429 save finalize window fixed (S7429_NO_QUIT_FLUSH=1 old; not runtime-verified).
   - CK s7428 env wins over config files, RT64 config persist gated like the save; CJ s7427 env policy order; CI s7426 env defaults;
     CH s7425 build-option drift fixed (BYTE_WATCH off qualified L1/L5/L10); CG s7424 no stale objects; CF s7423 live vs regen;
     CE s7422 windowed idempotence; CD s7421 regen drift; CC s7420 weak-aware RECOMP_FUNC regex.
2. **G5e fog: owner look.** ROGUESQ_DD_FOG_ALT=1,3,1 qualified at 16:9 and 21:9 (headline). Only if the owner asks for
   more haze at 21:9: sweep ke 2 / 2.5 with `tools/s7306_fog_219.zsh l1k2:1:1,2,1`.
3. **21:9 dd>1 left-edge sliver FIXED (s7310, ROGUESQ_DD_FARMAX default 32767, 0 = old), qualified s7312: owner look.**
   Far above ~36-40k units makes the F5 clip pin sky-dome edge panels to fb x=0 (two lines: RDP W decode + presented
   left-column count, 12 same-pose arms; mechanism single-source). Sheets docs/owner_sheet_s7310_farmax.jpg,
   s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
4. **Owner decisions on defaults:** RETINA=1, QOS_ALL=1, DD_FOG_ALT, dd8 bundle, RENDER_TO_RAM=0 (s7385). Never flip without the owner.
   QOS_ALL evidence: s7277-s7281 (load freezes removed) + s7382 (the threads it raises are exactly the hot ones, DEFAULT otherwise).
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
11. **RENDER_TO_RAM=0 CLOSED s7389: ready for the owner (OWNER-OPT-INS), default stays on.** Saves ~2.5 ms/gfx task in
    mission (s7385); abort-cut stale-upload stripe fixed (s7387, ROGUESQ_R2R_CPUUP=1 old); soaks L1/L4/L12 300 s pass (s7389);
    fb-cpu-reader census CLOSED s7391 (0 guest loads from a live colour image on 6 levels; build_fbld, ROGUESQ_S7389_FBLD=1).
    Not covered: RSP/RDP DMA reads (RT64 fb-as-texture owns those).
12. **Rerun-after-change censuses (all CLOSED, 0 defects):** after a regen: tools/scan_selfbranch.py +
    tools/s7081_selfbranch_test, tools/s708[2-7]_* lowering, host-shim s7088/s7089; after a fixup edit:
    tools/s7090_fixup_statement_census.py (exit 1 = defect); after RSPRecomp/ucode fixups: tools/ucode_regen.sh
    `verify`, tools/s7093_su_census.py --controls; after rsp_vu*.hpp / DMEM: tools/s7092_vu_mem_test; after rsp DMA:
    tools/s7094_dma_test + s7094_dma_census.py; after dpc_bridge submit/defer/wrap: ROGUESQ_S7095_DPC /
    S7096_FWD=ctl / S7097_EDIT=ctl (missing/dup/order/unattributed must stay 0); after an rs64_s7239 edit:
    tools/s7241_merge_test/run.sh; tools/s7243_resume_test.zsh; loop: tools/agent/test_soak_idle_gate.sh.
    After any host-code edit: every class census in item 15 with `--controls` (exit 1 = survivor or failed control).
    After a regen replay: tools/s7421_regen_drift.py <live> <regen> <compare.json> --control (exit 1 = LOST/REORDER not in
    tools/s7421_regen_accept.tsv); after a host/rt64 edit: tools/s7463_uninit_census.py --controls (rc 0) + tools/s7463_hash_layouts.py
    (any new padded struct hashed by raw bytes must go through rs64_s7463_hash); after an apply-script edit: tools/s7421_idem_test.py + tools/s7422_idem_class_test.py.
13. **Closed, reopen only on an owner report:** transition stalls (s7065/s7285), host self-time (s7066-s7070),
    misnomer rename (s7080; tools/apply_symbol_renames.py), G1e residual (s6996), G5c freezes (s7285), GPU
    contention (s7283), WIDEWIN thread (s7271), Retina (s7224), window/aspect G1f (s7228).
14. **Harness discipline (CLOSED s7313-s7314, s7332):** iteration tools take the pid from tools/rs64_game_pid.zsh;
    loop.sh SIGKILLs any game alive around each soak recipe and names it in SOAK-RESULTS (a kill line = that run's
    frame times are contaminated). Soak recipes take the analyser's own rc (`${pipestatus[1]}`), never a grep's.
15. **Idiom-class audits s7315-s7366: ALL CLOSED** (full text, numbers and controls: s7370 archive). Census tool per class:
    - guest-side: retail RAM bound s7315 (tools/s7315_retail_bound_census.py, single-source); DATA-word bound s7316
      (s7316_data_bound_census.py); spill holders / class B compares / C diffs s7317-s7320 (ROGUESQ_S7317_ALLOCMAP=1,
      s7317_spill_holders.py, apply_s7318_bcmp_probe.py); D 24-bit truncation s7321 (s7317_field_compare_census.py,
      s7321_trunc_report.py); E KSEG re-tag s7322; F addr-derived index s7323 (s7323_addr_index_census.py); G RCP-visible
      spill refs s7324 -> FIXED s7327 (s7324_rcp_report.py); audio heap-gap reads s7325 (artefact); audio freed-block
      access s7330 (s7330_task_free_report.py); scene-reset dangling writers s7331 (s7331_reset_writer_report.py);
      flags&4 carve s7332-s7334 (s7333_carve_report.py); fb-layout bound consumers s7335; host arena layout s7336
      (s7336_host_arena_table.py); R stale 8 MB bounds s7337; M 8 MB masks s7338; N 16 MB masks s7339 (latent);
      O KSEG0 16 MB bounds s7340; P top-byte tests s7341; L zero-extended bases s7361 (apply_s7361_sext_bases.py);
      AM raw rdram+X s7362 (s7362_rdramraw_census.py); **BA guest thread stack headroom s7391** (build_spwm:
      include/spwm/recomp.h checks all 68k generated $sp adjusts, tools/build_spwm.sh + s7391_spwm_run.zsh +
      s7391_spwm_report.py, ROGUESQ_S7391_SPWM=1 [+_CTL=1]): 27 threads on the s7386 route all inside their stacks, deepest
      mainBootstrapWorker 6848/8192 B, 1 KB audio stack uses 120 B; line B (service-worker stack snapshot, exact bounds from
      the registerServiceWorker descriptor) dirties 16-44 B above the $sp min, canaries intact, planted control seen ->
      H-fits. Soak s7391_spwm_levels (L4/L7/L12) queued. Tools are tools/s73NN_*_census.py.
    - host C/C++: S addr-indexed tables s7342 (single-source); T fixed buffers s7343; U wrap-prone bounds s7344;
      V mul overflow s7345 (single-source); W signed len s7346; X float->int s7347; Y div/mod s7348; Z shift s7349;
      AA overlapping memcpy s7350; AB cast loads s7351; AC signed overflow s7352; AD bool/enum s7353; AE data races s7354
      (TSan, tools/build_tsan.sh; COV=1 coverage arm s7372); AQ lockset s7366/s7373; AR lazy-init statics s7374; AS NOLOCK containers s7375, AS2 lockless files s7376 (AT present-thread maps open); AF signal safety s7355; AG unchecked alloc s7356;
      AH I/O lengths s7357; AI env parses s7358; AJ string copies s7359 (src/main/rs64_apf.h); AK guest string reads
      s7360; AN fixed arrays s7363, AO heap buffers s7364, AP container invalidation s7365 (each: census + independent
      reviews + ASan + gate); AQ cross-thread containers s7366 (static lockset census) + runtime half s7372/s7373 (COV=1 arm,
    tools/s7372_aq_runtime_cross.py, tools/s7373_aq_gate_table.py): CLOSED.
16. **Classes AQ-BZ s7373-s7416: ALL CLOSED** (full text, numbers, controls, tool flags: s7417 archive). One line each:
    - TSan/lockset follow-ups: AQ s7373 gate table; AR s7374 lazy statics (1 site fixed); AS s7375 NOLOCK containers, AS2 s7376
      present inserts locked (S7376_PQLOCK); AT s7377 present colour-target under lock (S7377_EARLYLOCK); AU s7378 shared res
      (S7378_SHLOCK); AV s7380 condvars H-shutdown; AW s7381 spins -> barrier CV (S7381_BARRIER_CV); AX s7382 thread QoS H-gap
      (QOS_ALL evidence); AY s7383 fb addr+width packed atomic (S7383_FBPACK); AZ s7384 0 default-path races (S7384_LDGFX opt-in).
    - Guest stack BA s7391 (build_spwm): 27 threads inside their stacks, deepest 6848/8192 B -> H-fits.
    - libultra/OS contracts: BB s7392 mesg drops benign; BC s7393 queue re-create H-none; BD s7394 heap-mutex re-seed window
      (S7394_HOLDFIX); BE s7395 event wiring H-none; BF s7396 upstream thread_queue_remove walk (S7396_TQFIX); BG s7397 upstream
      osSetTimer re-arm (S7397_TIMERFIX); BH s7398 osPiStartDma OSIoMesg (S7398_IOFIX); BI s7399 event payloads H-none; BJ s7400
      output contract 2 latent (S7400_CONTFIX); BK s7401 args 1 latent (S7401_FLAGFIX); BL s7402 clock divergence
      (S7402_CLOCKFIX); BM s7403 boot globals == retail 8 MB cold boot; BN s7404 direct RCP/cart access H-none; BO s7405 FCSR.FS
      (ROGUESQ_FTZ default on); BP s7406 FP corners after FTZ H-none.
    - Recompiler emission semantics (each tool rc 0 = still H-equal; re-run after any ROM/asm/generator change): BQ s7407 libm
      replacements (s7407_libm_census.py); BR s7408 FP->int (s7408_cvt_contract.py); BS s7409 FR/odd-FPR views; BT s7410
      callee-saved across FR=1 asm; BU s7411 unaligned ld/st; BV s7412 integer 64-bit GPR; BW s7413 aligned ld/st; BX s7414
      FP compare + bc1x (unordered-cond generator table wrong on NaN, 0 game sites); BY s7415 FP arith + moves (0 FMA); BZ s7416
      control flow + delay slots; CA s7418 opcode residue (s7418_opcode_residue.py: 0 live gap, cvt int/FP->FP exact, live cache
      = CDE/HWB-D no-op-safe). LATENT from BZ: jr/jalr emit the slot BEFORE reading rS (2 sites, dead data_gap_80024A0C).
    - **CB s7419 objdump decode blind spot: CLOSED H-clean.** The ELF is flagged `o32, mips1`, so plain `objdump -d` left every
      MIPS II/III op undecoded (ldc1 1386, sdc1 1255, trunc 1094 as `c1`, 8 branch-likely forms 2445 [s7392 parse patched 4],
      sqrt.s 94, cache 33, 64-bit ~140, eret), dumped size-0 OBJECT labels inside FUNCs as bytes (texPackTlutAtAllocSlot's 66
      instrs; __osException's rcp/prenmi/... sub-handlers, then mis-named LIVE functions) and skipped zero runs. Canonical
      listing tools/s7419_canon_dis.py (strip those 10 labels on a temp copy, `-d -z -m mips:4300 -M cp0-names=r3000`), now the
      auto-built default of s7392 parse (warns on any other listing), s7407, s7418. tools/s7419_dis_agree.py: 243,426 SAME (operands
      equal) + 42,275 alias spellings vs rabbitizer, 0 survivors outside data_gap/ucode/REVIEWED; control = plain listing flagged
      (6,799 survivors). Census re-runs: s7392-s7402 + s7407 byte-identical; s7403/s7404 rows move to IGNORED (__osException,
      s7403 now honours ignored_funcs); s7405 gains only cache (43 LIVE rows = s7418's set + 1 unrecompiled data word) + IGNORED
      eret/cop0. s7418 had tagged 147 renamed functions `nofn`; with the vote name join (s7419_dis_agree.name_map) it stays
      H-equal rc 0, live cache = 33 (18 CDE + 15 HWB-D; +clearMemory16ByteBlocks CDE then full 16 B sd/sd = no-op-safe).
17. **Default-on fixes from the audits and TSan thread (=0 / old value restores the previous behaviour):**
    ROGUESQ_SPILL_RESET + 8 MB spill arena 0x81000000 (s7326, SPILL_MB=4 old); RSP_DMA25 (s7327); S7334_CLASS5;
    S7335_CLAMP; S7336; S7337; S7339; ALTSTACK (s7355); S7358_ENVCHECK; S7364_WLRESET; CF0_DUPDROP (s7367, guest
    video-ack deadlock = the s6993 boot freeze mechanism under starvation; host-load soaks 5/5 clean in both arms);
    DLPOOLX_ARM_REBUILD (s7368, pool grows armed at the game's own pool init, not a frame-count proxy);
    build_tsan ucode exemption (s7369, ROGUESQ_TSAN_UCODE=ON old). Detail per session in PORTING-STATE. s7394-s7405 add (each =0 old): S7394_HOLDFIX, S7396_TQFIX, S7397_TIMERFIX,
    S7398_IOFIX, S7400_CONTFIX, S7401_FLAGFIX, S7402_CLOCKFIX, FTZ; s7376-s7383 add S7376_PQLOCK, S7377_EARLYLOCK,
    S7378_SHLOCK, S7381_BARRIER_CV, S7383_FBPACK.
18. **Runtime soak folds for the AQ-BZ classes all PASSED** (SOAK-RESULTS s7392-s7416: L4/L7/L12 or L5/L10/L15, 0 crash, 0 VI
    stall, controls PASS). No class soak is outstanding.
19. **Rerun the emission tools after any regen:** tools/s7407-s7416 + s7418 + s7419_dis_agree.py --controls (rc 0 expected) alongside item 12.
20. **When 1-19 offer nothing an agent can do:** take the next open ITERATION.md 3c rung (G5 renaming sweep,
    item 4) or a new idiom-class audit; do not write a backlog-exhausted block.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7417, s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7417-7452; search bounded windows only.
