# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7582 (2026-11-17).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; item-1 classes DG-EO in "(s7491 migration)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)"; s7533 Next-steps items 1,12,15-21 (classes FD-FZ) in "(s7534 maintenance)"; s7535-s7576 headline + items 17-21 + pre-s7300 superseded in "(s7581 maintenance)". Grep there for any sNNNN.

## Headline

**Every engineering goal on the ladder is closed or awaiting the owner's look.** Nothing is broken at the
owner's recipe as far as any instrument can see; remaining items are owner judgements (list in Next steps).

- **NEW s7582 (pointer-overflow UB CLOSED, H-clean):** `env SAN=pointer-overflow,nonnull-attribute,signed-integer-overflow
  B=build_ubsanp zsh tools/build_ubsanc.sh`: all 51 RecompiledFuncs objects carry ___ubsan_handle_pointer_overflow. L1 dd4, L4 dd2,
  L12 dd4 150 s (owner recipe) + L1 dd1 60 s: 0 reports, 0 crash/stall; plant ROGUESQ_S7578_PLANT=5 (char* at UINTPTR_MAX-3 + 16)
  fired (scorer kind ptrovf). So the MEM_* `rdram + (addr - 0xFFFFFFFF80000000)` add never wraps a host pointer in play (no guest
  KUSEG/zero-extended address reaches a load/store). nonnull-attribute: 0 reports but NO plant yet (single-source, uncontrolled).
- **s7580 (shift/alignment UB CLOSED; class LU fixed):** `env SAN=shift,alignment,signed-integer-overflow B=build_ubsans zsh
  tools/build_ubsanc.sh`. Pre-fix: 7,136 executed sites, ALL the N64Recomp LUI emit `S32(0X8011 << 16)` (signed shift into the sign
  bit, C17 6.5.7p4 UB; 24,698 literals) + 2 patch residuals (s7009 spannarrow `int64 neg << 7`, s4192 wait-spin `u16 << 16` in int)
  + 1 static hand-LUI. tools/fixup_lui_unsigned.py (LAST pass of fixup_game_funcs_vendored.py) rewrites all 24,703 to unsigned /
  multiply; tools/s7580_lui_identity.py: 51 TUs at real -O2, 0 object diffs (plant 34 diffs) = machine-code neutral. Post-fix L1 dd4,
  L4 dd2, L12 dd4 150 s: 0 reports, 0 crash/stall; plants PLANT=3 (shift) and =4 (misaligned u32) fired. Alignment: 0 reports ever.
- **s7579 (fixup-C host array-bounds class CLOSED, H-clean; gen-c-bounds-audit closed):** `env SAN=array-bounds,signed-integer-overflow
  B=build_ubsanb zsh tools/build_ubsanc.sh` = 879 bounds checks in RecompiledFuncs (ucode TUs 0: no fixed-array indexing). L1 dd1/dd4,
  L4 dd2, L12 dd4 150 s: 0 reports, 0 crash/stall; plant ROGUESQ_S7578_PLANT=2 (int[4] idx 4) fired. Scorer tools/s7579_bounds_report.py
  (rc 0). Scope: only directly-indexed fixed arrays are checked, not pointer-indexed buffers. **s7578:** game-C null/wrapv UB CLOSED
  (52 TUs, signed-overflow UBSan 0 reports, plant fired; new build dirs need a COPY of build/saves). **s7577:** ucode 759/759 bounded.
- **s7535-s7576 (classes GA-GR, regen health 19b, compensation chains 19c/19d, S6892, GUARD-6, do_break, float->int): ALL CLOSED.**
  Full text verbatim in PROJECT-OVERVIEW "(s7581 maintenance)". Landed defaults: RS64_DIV32/DIVU32 (s7575), RS64_TRUNC_W_S/D (s7576),
  tools/rs64_anchor.py regen fix (s7558), regen_replay "ok" (s7560). Opt-in fixes: ROGUESQ_SP_LATE=1 (GA s7535-s7537),
  ROGUESQ_RDP_NODRAIN=3 (GB s7540; OWNER-OPT-INS row). Owner decisions from them: M5_B40_VALUE (s7558/s7564), SP_LATE. Censuses
  docs/COMPENSATION-CHAINS.md (122 rows, 0 UNKNOWN) and docs/DEFAULT-ON-LEVERS.md (s7557). No default flipped.
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
- **s7552 "pre-mission out-of-rect colour change is real content (a darkening fade)" (superseded s7553).** Believable: samples
  0x294B->0x2109 failed RT64's requant test F(pre,d). But F only models upward dither from pre; the source is the retained float.
  s7553 shadow: pre == RT64's own last writeback for 100% of those px, post within ±1, dark/bright balanced, outside every draw.
- **s4711 "retail never runs reapplyAudioConfig/reapplyDisplayMode at boot/attract" (superseded s7476).** Believable because the oracle
  ran 120 s with 0 hits; but it ran with dummy video, which never leaves the 320 boot phase. With Rice + Start presses retail calls
  reapplyDisplayMode on every scene (t=2.1/6.7/17.3/38.4 s). The count=1 re-init was the port's s4889 patch clobbering $a1.
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
- Pre-s7300 superseded entries (s6445-s7288, 27 lines) moved verbatim to PROJECT-OVERVIEW "(s7581 maintenance)"; grep there.
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

Spec: ITERATION.md item 3c. No backlog-exhausted block. Renumbered s7534 into one sequence 1-18 (the s7533 numbering 1-22 is archived
verbatim in PROJECT-OVERVIEW "(s7534 maintenance)").

1. **Audit classes CC-FZ s7420-s7533: ALL CLOSED** (full text, numbers, controls, tool flags: PROJECT-OVERVIEW
   "(s7452 maintenance)" for CC-DH, "(s7488)/(s7491 migration)" for DG-EO, "(s7534 maintenance)" for the rest incl.
   FD-FZ). Last fold: s7533_fz_levels score 0 (L1 dd8 21:9, L7/L10/L12 dd4, 4/4 alive) -> FZ CLOSED 6 levels.
2. **G5e fog: owner look.** ROGUESQ_DD_FOG_ALT=1,3,1 qualified at 16:9 and 21:9 (headline). Only if the owner asks for
   more haze at 21:9: sweep ke 2 / 2.5 with `tools/s7306_fog_219.zsh l1k2:1:1,2,1`.
3. **21:9 dd>1 left-edge sliver FIXED (s7310, ROGUESQ_DD_FARMAX default 32767, 0 = old), qualified s7312: owner look.**
   Far above ~36-40k units makes the F5 clip pin sky-dome edge panels to fb x=0 (two lines: RDP W decode + presented
   left-column count, 12 same-pose arms; mechanism single-source). Sheets docs/owner_sheet_s7310_farmax.jpg,
   s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
4. **Owner decisions on defaults:** M5_B40_VALUE (s7558/s7564: default 0 is alive only via the s4889+s7476 compensations; =1 is retail and equally clean 6/6), RETINA=1, QOS_ALL=1, S7524_V2P=1 (s7526), SP_LATE=1 (s7537), DD_FOG_ALT, dd8 bundle, RENDER_TO_RAM=0 (s7385). Never flip without the owner.
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
12. **Rerun-after-change censuses (all CLOSED, 0 defects; tool list verbatim in PROJECT-OVERVIEW "(s7534 maintenance)"):**
    after a regen run tools/scan_selfbranch.py + the s7407-s7419 emission tools with --controls (rc 0); after a ucode regen tools/ucode_regen.sh verify
    + tools/s7507_rsp_ctrl_flow.py + s7508_rsp_scalar_gaps.py + s7509_rsp_vec_operands.py; after a librecomp/ultramodern
    replacement change tools/s7527_host_replace_audit.py --controls; after any new host writer into guest RAM tools/s7542_gc_census.py; after a src/main static/hook change tools/s7548_gh_census.py; after a fixup/apply script edit tools/s7549_gi_census.py --controls; after an RT64 fullSync/framebuffer-manager edit tools/s7550_gj_census.py --controls; after a librecomp/ultramodern getter or a new os*_recomp import tools/s7555_go_census.py --controls; after a scheduler/replacement or injected-yield change tools/s7543_gd_census.py --controls and tools/s7546_gf_census.py --controls; after a new host-retained guest pointer (osSetEventMesg-style registration) tools/s7547_gg_census.py --controls; after a class-touched function change, its class scorer.
13. **Closed, reopen only on an owner report:** transition stalls (s7065/s7285), host self-time (s7066-s7070),
    misnomer rename (s7080; tools/apply_symbol_renames.py), G1e residual (s6996), G5c freezes (s7285), GPU
    contention (s7283), WIDEWIN thread (s7271), Retina (s7224), window/aspect G1f (s7228).
14. **Harness discipline (CLOSED s7313-s7314, s7332):** iteration tools take the pid from tools/rs64_game_pid.zsh;
    loop.sh SIGKILLs any game alive around each soak recipe and names it in SOAK-RESULTS (a kill line = that run's
    frame times are contaminated). Soak recipes take the analyser's own rc (`${pipestatus[1]}`), never a grep's.
15. **Idiom-class audits s7315-s7416 (AQ-BZ) and their runtime soak folds: ALL CLOSED/PASSED** (archives: s7370, s7417,
    s7534 maintenance). No class soak is outstanding.
16. **Default-on fixes from the audits (=0 / old value restores the previous behaviour):** full list verbatim in
    PROJECT-OVERVIEW "(s7534 maintenance)" (SPILL_RESET, RSP_DMA25, S7334-S7364, CF0_DUPDROP, DLPOOLX_ARM_REBUILD, S7376-S7405
    locks/fixes, FTZ, STICK_GATE s7513, S7528_EVICT, the s7533 FPS60 clamp byte CAS).
17. **Classes GA-GR + 19b/19c/19d + S6892/GUARD-6 + do_break/float->int (s7535-s7576): ALL CLOSED** (verbatim in
    PROJECT-OVERVIEW "(s7581 maintenance)"). Open only: queued AC repeat scratch/agent/soak_queue/s7536_splate_cost.sh (fold with
    `python3 tools/s7537_ring_cost.py scratch/s7536_splate_cost <arms> --from 72`; if AC L12 dd4 late < early - 0.5 in a 3v3 ABBA, try
    delivering SP done at the LLE's last input fetch). Regen trees: tools/regen_front.sh D/pristine; cp -R D/pristine D/replay;
    tools/regen_replay.sh D/replay; tools/regen_verify.sh D/replay D/verify.
18. **After-regen UB gates (all CLOSED, rc 0 expected):** tools/s7575_ir_calls.sh + `tools/s7575_break_census.py --controls --ir D`
    (BLIND=0); `python3 tools/s7576_trunc_census.py --controls` (FOLDED=0); after a ucode regen or rsp*.hpp edit
    `tools/s7577_ubsan_sites.py <tu> --check` per ucode TU (UNCLASSIFIED 0) + `tools/s7577_ucode_ub_census.py scratch/s7577`;
    tools/s7580_lui_identity.py (0 object diffs). UBSan builds: `env SAN=<checks> B=<dir> zsh tools/build_ubsanc.sh`, scorer
    tools/s7579_bounds_report.py, plants ROGUESQ_S7578_PLANT=1-5. s7578 null/wrapv, s7579 bounds, s7580 shift/align, s7582 pointer-overflow CLOSED.
19. **NEXT (s7583): gen-c-residual-ub-audit** (NEXT.md): last UBSan group over the game C in ONE build (integer-divide-by-zero,
    float-cast-overflow, bool, builtin, unreachable, return, vla-bound, nonnull-attribute) with a plant per kind, L1/L4/L12.
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
