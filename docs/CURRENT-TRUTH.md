# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7448 (2026-11-15).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)";
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

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7417 into one sequence 1-20 (the s7416
numbering 1-27, with class sub-items AQ-BP under item 1, is in the s7417 archive).

1. **Class DF CLOSED s7449 (quiet-crash-passthrough). Next: class DG (HYPOTHESIS-ID harness-fatal-exit-coverage)**, see
   NEXT.md: m6_god_common.sh crashlines greps only 'CRASH\|SIGSEGV\|abort', so non-signal fatal exits (librecomp
   switch_error "Switch-case out of bounds" / do_break "Encountered break" via printf+exit, quick_exit "Exiting with exit
   status", message_box "Failed to allocate memory!") score crashlines=0. Soak s7449_argck_levels (L4/L10 QUIET) queued.
   DF (s7449) CLOSED H-few, one change: rs64_diag_keep words + (fmt has "%s") the FORMATTED text is checked. Members found
   by audit: ultramodern message_box "%s\n" + our callback "[Error] %s\n", quick_exit "Exiting with exit status", librecomp
   "Failed to find function at", "RSP ucode %u exited unexpectedly", [s7357-io] "... failed", [s6892] "%s\n" walker-guard
   repairs (G5a breadcrumb). Non-members: the macOS SIGSEGV/SIGBUS/SIGABRT handler (every line "[CRASH]..." + raw
   backtrace_symbols_fd), assert (libc raw), switch_error/do_break (printf = stdout, unrouted). Positive control
   ROGUESQ_PLANT_FAIL=15 (7 planted lines then SIGSEGV), scratch/s7449: default 7/7 planted, 37 [CRASH] + 12 bt frames;
   QUIET ARGCHECK=0 (s7448 filter) 1/7, 37 + 12; QUIET new 7/7, 37 + 12; boot log 5937 -> 6346 B. ARGCHECK=0 = old.
   s7448_quiet_levels fold: L7/L12 QUIET 135 s flight, 0 crash, 0 stall (DE second line).
   DE (s7448) CLOSED H-few, one change: src/main/main.cpp rs64_diag_keep also passes format prefixes [initMission],
   [autopilot], [vi] update_screen, [f5-phase5-target-store], [godmode], [g1b], [stall- (the tags the live harnesses
   m6_god_common.sh / g1_level_coverage_common.zsh, s7230/s7257/s7229 scorers, boot_freeze_hunt.sh gate on; [fbhash and
   [autopilot] fire were already raw). ROGUESQ_DIAG_QUIET_HARNESS=0 = old. 150 s owner recipe lvl1 (s7431 tool), QUIET:
   keep arm [initMission] 1 / [autopilot] armed 1 / [vi] update_screen 143, 501 KB; HARNESS=0 control 0 / 0 / 0, 484 KB;
   fbhash 8826 / 8834 both. g1_level_coverage_common.zsh L4 under QUIET: mission_t 72 s, flight 136 s, 0 VI stall, 0 crash,
   run.log 595 KB (s7447 default same recipe: 164.8 MB, mission_t 73 s). QUIET is now usable in every harness.
   s7447_route_levels fold: L4/L7/L12 137-138 s flight, 0 crash, 0 stall (DD build qualifies on 3 levels).
   DD (s7447) CLOSED H-hidden, one change: include/rs64_diag_route.h force-included (CMake option RS64_DIAG_ROUTE, default ON)
   into src/main + src/rsp (not factor5_ucode*) and the rt64 / librecomp / ultramodern C++ TUs, so every direct fprintf /
   std::fprintf goes through rs64_diag_fprintf; `(fprintf)(...)` keeps a site raw ([diag-quiet], [fbhash, [autopilot] fire).
   150 s owner recipe lvl1 (scratch/s7447): QUIET flight residual 18.8 KB/10s (12 periodic bypass tags) -> 163 B/10s, control
   [fbhash 8830 -> 8833; default arm 8.770 -> 8.772 MB, same tags, flight_from 68.4 s both; 0 crash all four runs.
   DC (s7446) CLOSED H-hidden, one change: src/main/upstream_compat.cpp rs64_s6569_spill per-request bump line
   "[spill] req=.. -> .." latched on ROGUESQ_SPILL_LOG=1 (G1E_TRIM=0 = old); arena-full breadcrumb and the 1-in-256
   reuse/free summaries stay unconditional; placement stays in the s6893 ring / S7317_ALLOCMAP. scratch/s7446, 150 s owner
   recipe lvl1 flight (tools/s7431_stderr_volume.sh): default [spill] req 0 (reuse 1, free 4 kept), consumer arm 752 (= s7445
   752), fbhash control PASS both (8803 / 8825), 0 crash both. No [spill] per-request consumer in tools/ (only retired soaks).
   DB (s7445) CLOSED H-hidden, one change: tools/apply_s7445_burst_latch.py (in the fixup apply list before s7069) latches
   [s4234-ENTRY] (funcs_24.c, ROGUESQ_S4234_ENTRY=1; rs64_s4234_g still counts), [newbtn] (funcs_19.c, ROGUESQ_NEWBTN_LOG=1)
   and the s1976-s1982 [drain-tick/slots/cross/cursor/path/base/hdr] dump block (funcs_30.c, ROGUESQ_DRAIN_DUMP=1);
   G1E_TRIM=0 restores all. Diagnostic only, no guest store changed. scratch/s7445, 150 s owner recipe lvl1 flight: default
   0 / 0 / 2 lines (2 = the one-shot drain-inloop-gate + drain-exit), consumer arm 2101 / 796 / 432 (= s7444's 2101 / 791 /
   ~450, PASS), fbhash control PASS both, 0 crash both. H-stall REFUTED (two runs): the ~200 ms fbhash gaps at t=6.2 s and
   44.8 s are there with the bursts latched (204 / 203 ms vs 206 / 203 ms in s7444), so they are scene loads.
   DA (s7444) CLOSED H-hidden, one latch: 14 periodic `(n & MASK) == 0|1` print sites read by hand. GATED (env/latch before
   the counter): s6955-bc (G1E_BATCH_CHECK), s6933-wm, s6945-coal, s6934-tbl (G1E_TRIM tbl check), s6936-walk, s4272-latetot /
   s4280-tot / s4284-tot (G1E_CDIAG), s4638-tally (LOG_S4299), s7318 (S7318_BCMP), s6911 (DD_VARCLAMP_LOG), g3d toggle,
   s4779-ctl (LOG_S4457), ustore/vstore (s7443). UNGATED-DIAG: [s6956-cdiag] (dpc_bridge.cpp rs64_dpc_defer_end_impl, every
   1024 commits, 8 lines / 150 s, the only DA tag in the s7443 default stderr). Now latched on ROGUESQ_G1E_CDIAG (any value) /
   G1E_TRIM=0. scratch/s7444, 150 s owner recipe lvl1 flight: default 0 lines, consumer G1E_CDIAG=1 8 (PASS), fbhash control
   PASS, 0 crash both.
   CZ (s7443) CLOSED H-trivial + one latch: the four hooks left by s7441_rs64_census sum 0.022 ms/f self. rs64_s6287
   (ppcount, 5 sites funcs_3.c) GATED-INSIDE (cached ROGUESQ_PPLOG); rs64_s6285_en (11 sites) NEEDED (dlpool grow gate,
   static latch); rs64_s6963_pre (funcs_10.c clampGridCellLookup) NEEDED (cell-index memo; S.calls++ only); rs64_s5660_ustore
   (4+ swl/swr sites) was UNGATED-DIAG: atomic counters + [ustore-all] every 2^18 calls (42 lines / run) with no env. Now
   latched on ROGUESQ_VSRC_STORES / ROGUESQ_LOG_USTORE (g1d_blk pc + s6843 STORE_WATCH stay unconditional), G1E_TRIM=0 old.
   scratch/s7443, 150 s owner recipe lvl1 flight each: default [ustore-all] 0, consumer LOG_USTORE=1 24 (PASS), 0 crash both.
   Trap: any ROGUESQ_LOG_* env turns on [storediag] (reason=ROGUESQ_LOG_USTORE): consumer stderr 9.8 -> 109 MB.
   CY (s7442) CLOSED H-hidden: tools/s7442_probe_gate_census.py (every rsNNNN helper the apply_s*.py patches inserted, call
   sites from guest functions, GATED / GATED-INSIDE / UNGATED + sample ms/f via --samples) on scratch/s7441: 12/40/9; the 9
   read by hand are renamed-body wrappers or latched (regex misses) except rs5908_call (apply_s5908_callers.py, every
   findSegmentObjectSphereHit call, printed [s5908] every 1024 calls: 2127 lines / 529 KB per run). Now latched on
   ROGUESQ_LOG_HITS / G1E_TRIM=0; script re-insert bug fixed. scratch/s7442: control PASS, [s5908] 0, stderr 16.45 -> 15.92 MB,
   0 crash; consumer control LOG_HITS=1 [s5908] 983.
   CX (s7441) CLOSED H-hidden, three changes. Census tool tools/s7441_rs64_census.py (every rs64*-named frame, all threads,
   self/incl ms/f, defining file) on scratch/s7440: NO rs64 frame >= 0.003 ms/f in render/framebuffer_renderer, hle/state,
   framebuffer*, present_queue, rdp_tmem, workload_queue (H-small for the named files). Found elsewhere: (1) the s5835 sphere
   probe (tools/apply_s5835_sphere_probe.py, intersectSegmentWithObjectSphere, every guest sphere test) ran at the owner
   recipe and printed [s5901] per bolt position up to 60000 lines; call site now latched on ROGUESQ_LOG_HITS / TELE_BOLT (its only
   guest write) / G1E_TRIM=0. Guest inclusive 0.096 -> 0.005 ms/f (intersect) and 0.098 -> 0.007 (findSegmentObjectSphereHit),
   fprintf samples under it 224 -> 0; second line: same-recipe stderr 36.9 MB (s7439, [s5901] 60000) -> 16.4 MB ([s5901] 0).
   (2) rs64_e9prov_frame_pop/resume (dpc_bridge.cpp, per DL return) did map find + 2 erases ungated; now return unless
   ROGUESQ_LOG_E9_PROVENANCE (dlwalk event kept). (3) rs64SkipDraw -> load-time latch + slow path. Capture scratch/s7441 control
   +0.0352 vs 0.030 PASS, guest probe verdict H-free 0.074 (control 0.63), 0 crash. Consumer control (LOG_HITS=1 +
   LOG_E9_PROVENANCE=1, 150 s): [s5901] 21212, [s5841] 146, [sph39] 158, [e9-prov] push=pop=resume=160 mis 0, 0 crash.
   Left in owner-recipe stderr (16.4 MB / 4 min, file sink, no cap): [s2020-svc] 2.1 MB, [vi-mode-table], [dpc-fwd],
   [osViSetMode], [s3290-stall] ~1.8 MB each: routed via rs64_diag_fprintf, closed s7431/s7432 (terminal cap, 0.3% core).
   CW (s7440) CLOSED H-small, one change: rs64_note_image_word was an out-of-line call per RDP command that returned unless op
   FF/FE; the op test is now at the rt64_interpreter.cpp call site (same ring; consumer = the default-on [ost-wb] wild-width
   freelist log in rt64_state.cpp, so the ring stays). rs64_floor_rect call (rt64_rdp.cpp, per rect) now skips its argument
   building unless ROGUESQ_LOG_FLOOR (or G1E_TRIM=0). rs64LogLoad (6 samples) and rs64SkipDraw (27) are already env-gated at
   entry, < 0.015 ms/f each. /usr/bin/sample top-of-stack, owner recipe lvl1, scratch/s7440 (control +0.0355 vs 0.030 PASS):
   note_image_word 35 -> 0 samples vs scratch/s7439; 0 crash. CV consumer control PASS (same session, LOG_SHADE_RAW/FLOOR/
   FLOOR_MESH=1): shade-raw 4751 lines with ord>=1, tri-source-join 4751, [floor*] 55745 incl. census rect counts > 0,
   [s4531-img] control 1 (ring still fed after the call-site gate).
   CV (s7439) LANDED H-gated: rt64_gbi_rdp.cpp decodeTriangles now computes shadeTask/shadeOrdinal/submit serial only when
   ROGUESQ_LOG_SHADE_RAW / FIX_ZERO_SHADE / LOG_FLOOR_MESH / SHADE_DIAG=1 is armed, and builds the floor_note/cover/texel/untex
   argument blocks only under ROGUESQ_LOG_FLOOR / LOG_FLOOR_MESH (every callee already returned at once without them).
   ROGUESQ_G1E_TRIM=0 restores the old always-run path. Measured by /usr/bin/sample, owner recipe lvl1 flight (scratch/s7439,
   control +0.0384 vs 0.030 PASS) vs s7435: decodeTriangles self 0.373 -> 0.176 ms/f, inclusive 0.726 -> 0.468, every rs64_floor_*
   / mutex / __hash_table / getter row gone from --under; Gfx thread 8.71 -> 8.00 ms/f (cross-run, single-source for the total).
   0 crash over the ~233 s run. Other hot loops (drawTris, loadBlock, loadTLUT, fullSync, pairTiles) carry <= 0.02 ms/f of rs64
   hooks (H-spread refuted). Logged ord/task read 0 in FIX_ZERO_SHADE lines unless SHADE_DIAG=1 (only behaviour change, log-only).
   CU (s7438) CLOSED H-closed (RT64 self terms all have prior closures; full text PORTING-STATE s7438).
   CT (s7437) CLOSED H-known: tools/s7437_tmem_hash.py on scratch/s7435 (control +0.0345 vs 0.030 PASS): TMEMHasher::hash
   0.0292 core = 0.49 ms/frame (body/CI4 scan 0.38, XXH3 0.11), 100% from TextureManager::uploadTexture on the Gfx thread; other
   XXH users 0.11 (FramebufferManager::checkRAM 0.05). Second capture scratch/s7433: 0.50 + 0.13. Redundancy already measured:
   s6942 TMEM-generation memo 0 hits in 2.29M flight calls (H-redundant refuted, ROGUESQ_G1E_TMEMMEMO opt-in), s6960 exact
   provenance cache (ROGUESQ_G1E_PROVCACHE) 0 wrong in 10.9M hits but costs more than it saves; s6942 NEON CI4 scan default on.
   No build: the planned step-2 counter would have re-measured s6942. No change landed.
   CS (s7436) CLOSED H-free: tools/s7436_alloc_cost.py on scratch/s7435 (8 x 12 s windows, owner recipe lvl1 flight; control
   DIAG_BUSY_GUEST_US=500 +0.0345 core vs 0.030, PASS): every allocator sample (libsystem_malloc frames, operator new/delete)
   together 0.0122 of one core = 0.20 ms/frame spread over all threads; RT64 Idle 0.0031 / RT64 Workload 0.0030 / Gfx 0.0028,
   guest threads <= 0.0002; 0 lock-wait samples under malloc (H-lock refuted). Largest owned caller RT64::TextureMap::use
   (Workload+Gfx 0.0035 core) then plume executeCommandLists 0.0022, all < 0.01. Second line: scratch/s7433 sample_{4,8}
   (--second-line, its control passed in s7433) alloc 0.0127, same callers. No change landed.
   CR (s7435) CLOSED H-tail: tools/s7435_spin_cost.py over one tools/s7433_probe_cost.sh owner-recipe run (lvl1 flight, 8 x 12 s
   /usr/bin/sample windows, control DIAG_BUSY_GUEST_US=500 toggled 30 s: +0.0345 core vs 0.030 expected, PASS). All host spins
   together 0.049 of one core: VI deadline tail spin (events.cpp:850, deliberate s6456/s6967, VI_NOSPIN / VI_RT_SPIN_US exist)
   0.0325, moodycamel LightweightSemaphore partial spin (maxSpins 10000, mostly the idle guest thread's wait_for_resumed) 0.0088,
   other clock polls 0.0062, yields 0.0012. Second lines: s7433 capture 0.031/0.011, s7381 counters 3.0%. wait_one_frame
   (vi.cpp:47) has no caller. No change landed (nothing >= 0.01 core outside the deliberate VI tail).
   CQ (s7434) CLOSED H-known: tools/s7434_gfx_glue.py on scratch/s7433/sample_{4,8}.txt (owner recipe dd4 16:9 FPS60, lvl1
   flight, busy-off windows) charges each running Gfx Thread sample to its innermost owned frame: 8.97 ms/frame = F5 ucode 3.85
   (43%, matches s7014's 41%) + RT64 3.21 (36%) + our glue 1.92 (21%). Our glue = rsp_dpc_submit_impl self 1.07 (per-DPC_END-bump
   bridge: hot PCs sit right after the s_fwd/g_task_rdp ldadd counters, = s7028/s7029's split, closed H-call; BUMPFAST=2 stays
   opt-in) + record_submit walkers 0.42 (= s7018's 0.23-0.45, closed) + submit_rdp_range 0.08. H-copy REFUTED: memmove/memcpy
   0.50 ms/frame in total, largest owned caller rsp_dpc_submit_impl's vector insert 0.163. defer_end is 1.99 inclusive, of which
   0.085 ours (the rest RT64 processDisplayLists). Two lines (sampling profiler here, mach-timer splits s7018/s7028), so no
   owned term >= 0.5 ms/frame is left that is not already split and closed. Largest RT64 terms: TMEMHasher::hash + XXH3
   0.57, rs64LoadBlockRuns (our lib/rt64 patch) 0.32, decodeTriangles 0.28, processRDPLists 0.27 ms/frame.
   CP (s7433) CLOSED H-free, measured by /usr/bin/sample (external profiler): tools/s7433_probe_cost.{sh,py} (owner recipe via
   tools/s7431_stderr_volume.sh, 8 x 12 s windows, control ROGUESQ_DIAG_BUSY_GUEST_US=500 toggled 30 s in-run: +0.68/+0.63 ms
   per frame vs 0.50 expected, PASS both runs). Guest threads run 2.5 ms/frame; probe helpers (own frames + library calls
   beneath, wrappers not charged for wrapped game code) 0.144 ms/frame, mostly the CO fprintf and s6963_tick. FIX: s6963_tick
   read mach_absolute_time on every clampGridCellLookup for a tick that does nothing with no toggle/log; now skipped
   (ROGUESQ_S7433_TICK_ALWAYS=1 = old): 43 -> 5 samples, 0.108 ms/frame after, 0 crash, 60 tasks/s. Gfx-thread probes
   0.054 ms/frame. Traps: osViSwapBuffer self 9% is the runner's planted [fbhash] (FB_HASH=1); wait_for_resumed self 7% is the
   moodycamel semaphore spin. The default-on diagnostic-cost family (CM-CP) is closed.
   s7428 F9 arms C/D retired after 5/5 VOID (no injected key reaches the game): the F9 persist gate is code-reading only.
   CO (s7432) CLOSED H-free: include/rsp_dpc_macros.h now routes every generated-C fprintf (50 objects, 0 direct) through
   rs64_diag_fprintf (main.cpp), as do [dpc-fwd]/[osViSetMode]/[vi-mode-table]/[lle task]; ROGUESQ_DIAG_QUIET=1 drops them at
   source (crash formats pass), opt-in, default 0. Same-run 2x2 (quiet 15 s x busy 30 s, owner recipe lvl1 flight, FAST=1
   PROBES=0, tools/s7432_diag_quiet_ab.py): control 1 ms busy per gfx task = +0.934 ms/task ucode (PASS); quiet = +0.086 ms
   (noise, sign differs between the two pairs), tasks/s 60.6 vs 60.6. Direct cost: 0.71 ms/s on gfx-task threads (388
   calls/s, 31 KB/s, ~0.012 ms per task) + 2.2 ms/s elsewhere (1507 calls/s, 165 KB/s) = 0.3% of one core. Guest 1 ms busy
   per swap moved tasks/s by -0.1 (headroom >= 1 ms/frame). The s7431 writer cap is enough.
   CN (s7431) CLOSED H-perframe FOUND + FIXED (writer-side): tools/s7431_stderr_volume.{sh,py} (copied folder, owner recipe
   FPS60 dd4 16:9 + forced lvl1 autopilot, no logging env, per-line arrival timestamps; planted per-frame control
   ROGUESQ_FB_HASH=1). Old binary 260 s: 39.5 MB, flight 1.71 MB/10 s, 37 tags print in every flight window ([s5855] 800 KB/10s
   at 5 KB/line, [vi-mode-table]/[osViSetMode] 60 lines/s, [dpc-fwd], [s2020-svc], [s3290-stall], [lle ...); burst
   [s4234-ENTRY] 165 KB in 1 s at boot. Fix: per-tag token bucket in the s6979 async-stderr WRITER thread (game threads pay
   nothing): 200-token burst, 0.2 tokens/s, a line costs 1+bytes/512; CRASH/abort/FATAL/SIG/ERROR/assert lines always pass; a
   "[stderr-cap] dropped" summary every 30 s. ROGUESQ_STDERR_CAP unset = on iff the original stderr is a terminal (owner's
   Terminal launch; harness pipes/files keep every line their gates parse), =1 force, =0 off; _BURST/_RATE tunable. Arms, new
   binary: C (file, CAP=1) 1.33 MB/260 s, flight 11.5 KB/10 s (149x less), control [fbhash held to 2 lines/window; N (file,
   unset) cap=0, 2.1 MB/10 s = unchanged; T (pty via script(1), unset) cap=1, 11.5 KB/10 s; crash control
   ROGUESQ_TEST_CRASH_AT=25 under CAP=1 printed the whole [CRASH] block.
   CM (s7430) CLOSED H-bounded after two fixes: rs64_s6892.log rotated to .1 above 256 KiB at start (ROGUESQ_S7430_NO_ROTATE=1
   = old); boot ucode dump opt-in ROGUESQ_DUMP_UCODE_BIN=1 (tools/s7430_file_growth.{py,sh}). rs64_s6893_rdram.bin (20 MB,
   once per run on the first real s6892 repair) left: bounded, a one-off G5c stall candidate.
   CL (s7429) WINDOW FOUND + FIXED: librecomp finalize_output_file_with_backup copied temp -> final with copy_file, which
   truncates final first; a quit/crash/kill inside the copy left a short or 0-byte final save, and the loader opened it (it
   exists) instead of the whole .bak, then zero-filled = profile wiped. tools/s7429_save_quit/harness.cpp (real files.cpp,
   fork + SIGKILL at 50-3000 us during continuous saves): old finalize 236-259/2000 bad loads (all 0-byte), new 0/4000, same
   binary toggled by ROGUESQ_S7429_OLD_FINALIZE=1. Fix: fsync the temp, rename it over final (atomic); read_save_file now
   loads the whole .bak when final is short ([s7429-io] line; runtime arm R1 in a copied folder fired, control R1c with no
   .bak zero-fills). Second gap (code reading only, single-source): SDL_QUIT -> quick_exit never joined the saving thread,
   which writes only after a 10 ms gap with no new writes, so a quit inside that window dropped the newest save; main.cpp now
   calls ultramodern::flush_save_file() first (writes only if the write_gen counter is ahead; keeps the NO_SAVE_WRITE gate;
   ROGUESQ_S7429_NO_QUIT_FLUSH=1 = old). NOT runtime-verified: no injected quit reached the game (s7428 key VOID), and a
   40 s forced boot wrote no save, so the rename path is verified by the harness only. tools/s7429_save_quit.sh (exit 0
   H-durable). Owner save untouched (mtime 2026-11-08).
   CK (s7428) CLOSED H-env-wins after one fix: tools/s7428_config_precedence.py (110 open sites in src/, librecomp,
   ultramodern, rt64 hle; 0 unreviewed fixed-path reads; control PASS: planted file-before-env read, ungated persist write,
   RT64 config on, ungated save write all flagged; HEAD~ main.cpp flags persist-gated). Config files the game reads: RT64
   user config NEVER (rt64_render_context.cpp useConfigurationFile=false, detectDataPath=false: every RT64 setting comes from
   ROGUESQ_* env), audio_device.txt (exe dir; ROGUESQ_AUDIO_DEVICE wins, runtime arms A/B in a copied folder confirm), save,
   stored ROM, mods/ (empty). DEFECT fixed: the F9 audio-route cycle persisted audio_device.txt even under
   ROGUESQ_NO_SAVE_WRITE, so a probe run could change the owner's next default; now gated like the save. F9 arms C/D
   (tools/s7428_audio_route_arms.sh, injected-Return void check) VOID in-session (no injected key reached the game, Return
   included) -> queued scratch/agent/soak_queue/s7428_audio_route_arms.sh (SOAK_NEEDS_IDLE=300).
   CJ (s7427) CLOSED H-ordered after one fix: tools/s7427_env_policy_order.py --control (planted pre-policy static latch /
   step-order inversion / unguarded overwrite all flagged) + runtime trace ROGUESQ_S7427_ENVTRACE=1 (rs64_env_cache.cpp, phase
   pre/in policy; ROGUESQ_S7427_PLANT=1 control seen). 36 policy vars, 5 steps, 8 overwrites (sanitiser 4 / guarded 1 / ASPECT
   normalisation 3), 0 inter-step read-before-set. Pre-policy readers at runtime: g_rs64_s7030, S7239Init/S7246Init (re-armed
   by rs64_s7258_merge_reinit), events.cpp GFX_QOS (reads QOS_ALL itself), and the DEFECT rs64_g5b_tg_fix (dpc_bridge.cpp,
   static init read the RAW DRAW_DISTANCE: "4x"/"inf" ran retail dd1 with the dd>1 TriGen fix armed). Fixed:
   rs64_s7427_tg_fix_reinit() after the policy (ROGUESQ_S7427_REINIT=0 = old); arms 4x -> 1->0, 4x+REINIT=0 -> stays 1,
   dd4 -> unchanged. Owner recipe unaffected (valid values).
   CI (s7426) CLOSED H-consistent after one fix: tools/s7426_env_defaults.py --control PASS (planted flipped default / presence /
   file-scope policy latch all flagged); 3,789 sites, 703 lambdas compiled+evaluated, 86 documented vars, reviewed rows in
   tools/s7426_env_accept.tsv. Defect fixed: ROGUESQ_DD_UNSAFE was a presence test (=0 unlocked dd 8); now a value test in
   apply_s6036_dd.py + live funcs_9.c, two-arm verified (=0 -> multiplier 4, =1 -> 8). OWNER-OPT-INS header corrected. 154
   undocumented default-ON vars = internal fix kill-switches/caps (inventory, not drift).
   CH (s7425) qualified at runtime: s7425_nobw_levels L1/L5/L10 alive, 0 crash.
   CH (s7425) DRIFT FOUND + FIXED: tools/s7425_build_options.py --control (planted -O0 -DRS64_BYTE_WATCH librecomp entry and
   planted cache SP_WATCH=ON both flagged). 16 options/cache vars all at default (MIPS_*/N64RECOMP_EXE = host paths); hot targets
   (RecompiledFuncs 52, PatchesLib, game 24, librecomp 27, ultramodern 15, rt64 211, plume 3) all -O2; gfx ucode keeps
   -inline-threshold=4000; 0 sanitizer flags/symbols; 454 objects newer than flags.make. One finding: -DRS64_BYTE_WATCH (s5690
   bool-store watch, no remaining consumer) on all 52 RecompiledFuncs TUs = inlined static load+test on every guest byte access,
   +2.5% __text (funcs_9). Now option ROGUESQ_BYTE_WATCH default OFF; rebuilt: rs64_bwatch 118 -> 0 symbols, game __text
   -575,888 B (1.8%), tool VERDICT H-intended rc 0. Identity when ROGUESQ_BOOLSTORE_WATCH unset (single-source reading of
   recomp.h); runtime qualification soak queued: scratch/agent/soak_queue/s7425_nobw_levels.sh (L1/L5/L10 owner recipe, 120 s).
   Cold -O0 libs linked by design: LiveRecomp/N64Recomp/rabbitizer/fmt/miniz/nfd/re-spirv/zstd (zstd -DDEBUGLEVEL=1 is zstd's
   own Debug default). tools s7413-s7418 compile forms with -DRS64_BYTE_WATCH "as CMakeLists sets it": drop it when rerun.
   CG (s7424) CLOSED H-fresh: tools/s7424_stale_objects.py --control --make-n PASS: 415 linked objects (24 + 15 archives) newer
   than source and every .d dep, archives byte-match their .o, RecompiledFuncs from the live tree, glob == compiled set, 0 orphans,
   2504/2504 RECOMP_FUNC symbols in the .o. make -n residue = spirv-cross relink (a 12:41 reconfigure rewrote only its
   build.make/link.txt) -> 56-shader chain; current spirv_cross_msl regenerates all 56 .metal byte-identical, so no-op in content.
   CF (s7423) CLOSED H-diag: tools/s7423_live_stale.py live vs fresh regen, every function text-level, --control PASS (known funcs_9
   lines listed DIAG, planted store BEHAVIOUR, planted print DIAG): 124 regen-only statements = DIAG 25 / FILE-DIAG 5 / ORDER-DIAG 10
   / GUEST 4 + REGEN-FUNC 1 (the s6871 sizing set) / 3 reviewed ORDER rows (tools/s7423_live_stale_accept.tsv: diag swap, goto-less
   labels, dead post-return copy). 0 behaviour patches missing from the shipped build. Live funcs_9 [streamdump] bounds print 0 until
   the next regen (diag only).
   CE (s7422) CLOSED H-once: of 13 windowed-idempotence scripts, 8 are called twice (inline fixer + RS64_REPLAY); 0 doubled in
   the real chain (fresh replay /tmp/s7422/R byte-identical to s7421 R2), but 7 of 8 double once a later block lands at their anchor
   (tools/s7422_idem_class_test.py control) -> whole-function tag checks; s5829 safe by anchor shape; s5693/s5697/s6303/s6311/
   fixup_preempt_point called once (SAFE). Residue explained: s5856 regen>live = same decl line labelled s5904 in live (label only);
   s6497 regen>live = live lost the two funcs_9 lines above (regen correct).
   CD (s7421) CLOSED H-mirrored: tools/s7421_regen_drift.py --control rc 0 (plant LOST / plant-diag ENVDIAG PASS) over a fresh
   replay (2664/114/18/3, = s7420; 2671/107/18/3 after the idempotence fix): all 47 new diffs + 3 new one-sided = funcs_13 store-diag handler rs64_s5798_st reorder
   (diag, inlined into 45 callers) + 6 stale ROGUESQ_TICK_TRACE hooks; 0 LOST; baseline residue in tools/s7421_regen_accept.tsv.
   PATCH-tag census agrees (live-only tags = documented opt-in list). Found and fixed: s5787/s5790/s5791/s5809 HUDBIT logs
   double-applied in a regen (windowed idempotence; diag only). docs/REGEN-VERIFY.md "s7421".
   CC (s7420) CLOSED H-clean. Use the weak-aware regex `^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC` in new parsers.
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
    tools/s7421_regen_accept.tsv); after an apply-script edit: tools/s7421_idem_test.py + tools/s7422_idem_class_test.py.
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
- Recent chronology: PORTING-STATE sessions 7370-7417; search bounded windows only.
