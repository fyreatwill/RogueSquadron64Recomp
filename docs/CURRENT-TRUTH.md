# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7873 (2026-11-23).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; item-1 classes DG-EO in "(s7491 migration)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)"; s7533 Next-steps items 1,12,15-21 (classes FD-FZ) in "(s7534 maintenance)"; s7535-s7576 headline + items 17-21 + pre-s7300 superseded in "(s7581 maintenance)"; s7702-s7790 headline + Next-steps items 1-36 in "(s7792 maintenance)"; s7579-s7616 headline + items 19-46 in "(s7622 maintenance)"; s7647-s7659 headline + items 21-35 in "(s7662 maintenance)"; s7617-s7702 headline + item 20 (G6) in "(s7703 maintenance)"; s7702-s7743 headline + items 22-32 + s7312-s7418 superseded in "(s7747 maintenance)"; s7802-s7815 headline + items 12-13 (closed classes, G3 det threads s7793-s7841) in "(s7848 maintenance)". Grep there for any sNNNN.

## Headline

**Every engineering goal on the ladder is closed or awaiting the owner's look** (s7792). The full s7790 headline (s7702-s7790
bullets: regen/census engineering, G5h, G6a/b/c, owner settings, host audits, G3, draw distance, fog, freezes, Retina, host
hazards, presentation, window/aspect, boot freeze, spill fixes, G1e, wide fixes, opt-ins) is archived verbatim in
PROJECT-OVERVIEW "(s7792 maintenance)". Standing facts an agent needs:
- **Owner: docs/OWNER-REVIEW-QUEUE.md (s7762) is the one-sitting list** (20 items, command + sheets each). Paths/settings in it and in
  OWNER-OPT-INS are gated by `python3 tools/s7762_owner_doc_check.py --controls`; every queue command is checked by
  `python3 tools/s7763_owner_cmd_check.py --control` (11/11 MATCH), in-flight toggles by `zsh tools/s7764_inflight_toggles.zsh`
  (7/7), controls dump/controls.json by `python3 tools/s7765_controls_dump_check.py` (12/12). Only the F6 panel's interactive use is untested by us.
- **Owner decisions pending (defaults unchanged until the owner says):** QOS_ALL=1, RETINA=1, M5_B40_VALUE, S7524_V2P=1, SP_LATE,
  RENDER_TO_RAM=0, DD_FOG_ALT=1,3,1 look, STANDINS=1 look (G6c), rumble/controls feel (G6a/G6b), launch presets `--preset tv|ultrawide|window`, VI_STAMP=1 (determinism only, s7838 soak clean), ROGUESQ_RETAIL_SNAP=1 (s7840: timeSnapshotFiller pin el 811160 / vd 1; pinned port = retail CPO1 camera rest pitch on lvl2/3/4 and the lvl4 reticle to the pixel; soak s7839_snappin_L1 PASS; retail-accuracy candidate default, pairs with VI_STAMP=1).
- **Sweep:** `python3 tools/s7651_gate_sweep.py` (--jobs 2, iron rule 0) ~216 gates, 0 RED, 0 HOLLOW; stop_gate blocks RED. The live
  RecompiledFuncs tree IS the regen replay: `tools/s7719_regen_gate.py --strict` byte-compares it, so ANY hand edit under
  ../N64Recomp/RecompiledFuncs turns the sweep RED (put it in a fixup/apply script). Ucode: `tools/s7741_ucode_regen_gate.py --controls`;
  after a fixup_factor5_ucode.py edit `zsh tools/ucode_regen.sh snapshot`. After a regen `python3 tools/s7734_compiled_reader_census.py`.
- **s7788-s7791 vendored fixer pruning CLOSED:** dead-emitter census 0 dead; 257 never-run blocks deleted (s7790), shadowed-block prune
  1 block (s7791); `--strict` 0 differ, census HIT 326. **s7781-s7787 hook classes CLOSED** (s5660 unaligned-store hook value/address fix,
  load-hook hole, 4 pc-literal emitters).
- **Retained captures are zstd'd (*.zst):** tools reading scratch/ must use tools/rs64_zopen.py (zopen/resolve/materialize;
  argv paths self-resolve to .zst, s7805). Class closed with guards: sweep rows S7802_RETAINED, S7803_RETAINED, S7804_LINT
  (waiver `# zst-ok: <reason>`), S7805_CITED. Detail s7802-s7805 in PROJECT-OVERVIEW "(s7848 maintenance)".
- **Latency (s7766/s7767):** FPS60 58.3 ms, retail 75-86, FPS60+VI_LOCK=1 53.7 ms; window mode does not change it (FULLSCREEN=2 exists).
- **s7848:** the s7804 zst lint now scopes tools cited in CURRENT-TRUTH AND PROJECT-OVERVIEW (maintenance moves citations); 4 blind
  readers fixed. Any new CURRENT-TRUTH-scoped gate must read both docs.
- **Crash reports:** `python3 tools/crash_reports.py --since <date>`; a NEW report outranks all other work (s7664).
- **s7806-s7813 non-retail-by-default siblings CLOSED** (detail PROJECT-OVERVIEW "(s7848 maintenance)"): patches toolchain stamp
  (s7806; rebuild PatchesLib after patches.elf relinks, s7807), gcc C-patch bodies (S7808_FIND, S7809_PATCH_CLASS: a NEW C patch is
  RED until rowed), host overrides (S7810_HOST_OVR, zmemcpy sign-extension fixed), host callees (s7813), include resolution (s7814),
  elementwise VU vs cxd4+CEN64 (S7815_VU; oracle now loads the VU-fixed cxd4, s7816). New census tools must use the weak-aware
  header regex `^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC` and pass `tools/s7420_parser_census.py` (s7811).
- **Hazards:** never LAUNCH the game under lldb (s7616: it tried to delete the ROM); attach to a normally started pid
  (preflight tools/lldb_attach_check.sh). New build dirs need a COPY of build/saves. Title plume si_addr=0x58 CLOSED (0/76 boots s7660;
  s7725 RT64 texture-descriptor over-release fixed, NSZombie 0).
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
- **s7872 "el=0 hits a special 0-divisor path in timeSnapshotFiller; the cinematic needs el in (0, 811160)"** (superseded s7873).
  Believable because el=0 moved island A far off instead of onto retail. Reading 0x8000BE28-BF38 shows no el branch: the value is
  el/rate + VIperiod*max(vd,1) and RETAIL_SNAP pins vd=1, so el=0 stored 1 VI vs retail's 2 VI. Retail-valued arms leave island A unchanged.
- **s7857 "0x31=14 port-side 1-2 ULP transient t892-899"** (superseded s7858). Believable because retail r2 == r1 and r2 differed
  from the port in the same words, so it looked port-side. Both retail runs were scored against the SAME misindexed pin file: the
  port was fed dt 0x3D088887 at tick 891 where retail ran it at 892 (store watch: same PCs, f10 = [sp+0x1DC] dt arg 87 vs 88).
- s7828 "the port's flight pitch delta is port-side (H-cpu-pose): the port feeds or computes something differently": believable
  because retail's pose was timing-invariant while the port was 42/42 pitched in its one schedule. s7829 showed the same port binary
  matches retail (0/42) when the autopilot presses land ~36 game frames later: the pitch belongs to one press schedule, not to
  port math or a port input (idle stick 0 on all 8043 reads).
- s7827/s7825 "sub-pixel flight-pose/logo residuals are H-input-time (time-integrated state depends on frame/dt history)": believable
  because static-authored scenes were exact and only time-integrated scenes differed. s7828 changed ONLY retail's emulated CPU timing
  (26% fewer frames) and the steady flight pose stayed within one quantum, while the port differs by 3-6 quanta: the pose is
  timing-independent in retail, so the port delta is port-side. (The s7825 logo verdict was not re-tested.)
- s7826 "reticle +0.5 px = a screen-space constant on the reticle only (HUD anchor chain suspect)": believable because the texrect
  path matched to <0.5 px and only that PRIM missed. s7827 found the projected sky mesh shifted too, with a pitch-shaped x/y
  pattern: a camera pose delta of ~0.1 deg, not a reticle/HUD transform.
- s7816 "animated oracle frames differ cross-run because of wall-clock press/dump timing" was only half the cause: with presses
  and dumps VI-locked, runs still diverged from VI ~2115 because mupen64plus-core randomizes PI/SI interrupt timing with a
  time-seeded rand() (s7817). Believable because wall-clock jitter was a real, visible source and the first fix to try.
- s7752 "residual (a), 31-33 replaced commands per task, is <=1 LSB sub-visible precision": believable because the render diff was
  tiny and both RSPs looked healthy, but s7815 showed it is cxd4's VCH (vt=0x8000) and VCR (signs differ) defects: with those two
  fixed, cxd4 is byte-identical to our stream on both retained tasks.
- s7783/s7781 "the port places DL chunks inside the framebuffer pair (H-overlap / H-shared-slot, port-only)" and s5661 "unaligned
  stores are not the rail writer": believable because the hook fired with a passing plant control and the oracle disagreed, but
  the s5660 hook used the stored value as the address at every swl/swr/sdl/sdr site (s7784). Any [swatch]/s6843 hit from an
  unaligned-store pc before s7784 names the value, not the destination.
- s6268/s6868 "no syms-toml placeholder is a real function / the leftovers are shape-only": believable because s6868 audited the
  generated tree and s6268 read objdump, but N64Recomp never emits the libultra exception block and objdump prints it as data.
  Overturned s7770 (ELF byte census, tools/s7770_placeholder_census.py): func_8002BB34 had 14 jal sites and is send_mesg (named).
- s7748/s7690 "L12: 85/92 stand-in items are never added": believable because [s7690-par] reads tries=120 adds=0 per item; it prints once at the first 120 tries, so it is a window, not lifetime (s7749: 79 of 85 added later).
- s7746 "L12 stand-ins are added but NOT visible (H-gain refuted on L12, H-not-visible)": believable because the ground-only
  scorer and its paint control both passed. Overturned s7748: the same on-window flicker (131 vs 146 per triplet) against a quiet
  control (36, not 126) gives 4.1x, and the on-frames show extra pylons by eye; s7746's forced-off window carried camera-motion flicker.
- s7587 "the 2026-11-18-014353 RT64 Present SIGTRAP is an OBJC_DEBUG_MISSING_POOLS instrument artifact": believable because only
  the debug arm crashed; superseded by s7725 (the env alone never traps; the push flushes a freed +0 texture descriptor that plume
  over-released; fixed).
- **s7645/s7646 "gfx tasks read display-list bytes that PI DMAs refill mid-task at dd>1 (L4 4912/120 s); H-slot-recycle" (superseded
  s7647).** Believable: controls fired, dd1 arm read 0, and the issuer/ROM offsets were coherent. But both sides were keyed `& 0x7FFFFF`
  while the RSP addresses 32 MB and dd>1 data lives above 8 MB: true-key overlap 0, alias-only overlap 4881 in the same run.
- **s7552 "pre-mission out-of-rect colour change is real content (a darkening fade)" (superseded s7553).** Believable: samples
  0x294B->0x2109 failed RT64's requant test F(pre,d). But F only models upward dither from pre; the source is the retained float.
  s7553 shadow: pre == RT64's own last writeback for 100% of those px, post within ±1, dark/bright balanced, outside every draw.
- **s4711 "retail never runs reapplyAudioConfig/reapplyDisplayMode at boot/attract" (superseded s7476).** Believable because the oracle
  ran 120 s with 0 hits; but it ran with dummy video, which never leaves the 320 boot phase. With Rice + Start presses retail calls
  reapplyDisplayMode on every scene (t=2.1/6.7/17.3/38.4 s). The count=1 re-init was the port's s4889 patch clobbering $a1.
Recent only; older entries in the PROJECT-OVERVIEW maintenance archives (s7307, s6994, s6900, s6870, s6759).
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
- Frame-exact presses: `ROGUESQ_AUTOPILOT_CLOCK=vi` keys autopilot to ultramodern's VI count (port twin of oracle `--clock vi`, s7820).
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
- Title plume si_addr=0x58 CLOSED s7660 (0/76 boots); reopen only if `[plume-null-color-attachment]` prints.
- Public forks (owner, 2026-11-18): loop.sh runs `tools/agent/publish_forks.sh` between iterations; it pushes `autonomy` to
  fyreatwill/RogueSquadron64Recomp (fast-forward only) and mirrors N64Recomp tool source + decomp tracked files to their `rs64`
  forks. Never commit ROM-derived data (*.z64, ucode/RDRAM dumps, RecompiledFuncs) or files > 50 MB, and never rewrite history,
  or publishing stops (`scratch/agent/PUBLISH-BLOCKED.md`). `tools/build-from-scratch.sh` is the public build; keep it working.
  **Re-verified s7806** from clean clones of the 3 public forks (632 s, CMAKE_BUILD_PARALLEL_LEVEL=4): RecompiledFuncs, build/factor5_ucode,
  patches.elf/.bin/.map and RecompiledPatches/patches.c byte-identical to the live tree; both binaries boot past attract (s7806 boot2.zsh).
  Re-run it in ../rs64-cleanbuild-s7806 (reuses the clones; `git -C <repo> pull` first) after any build-system, regen or patches/ change.
- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 streams. Positive control for every null; two
  independent lines before a conclusion enters this file.

## Next steps (single monotonic backlog)

Spec: ITERATION.md item 3c (no backlog-exhausted block). Renumbered s7792 into one sequence (s7848: 11b -> 12); the s7790 numbering (1-36) is
archived verbatim in PROJECT-OVERVIEW "(s7792 maintenance)". Ladder item 4 REVISIT has no open target (rename sweep CLOSED s7770,
M4 boundary CLOSED s5354, retail-entry boundary CLOSED s4845).
1. **G5e fog: owner look.** ROGUESQ_DD_FOG_ALT=1,3,1 qualified at 16:9 and 21:9 (headline). Only if the owner asks for
   more haze at 21:9: sweep ke 2 / 2.5 with `tools/s7306_fog_219.zsh l1k2:1:1,2,1`.
2. **21:9 dd>1 left-edge sliver FIXED (s7310, ROGUESQ_DD_FARMAX default 32767, 0 = old), qualified s7312: owner look.**
   Far above ~36-40k units makes the F5 clip pin sky-dome edge panels to fb x=0 (two lines: RDP W decode + presented
   left-column count, 12 same-pose arms). **Mechanism now two-source (s7751):** the independent cxd4 RSP, fed the same
   captured gfx task (ROGUESQ_S7751_SNAP + tools/s7751_cxd4_task/replay), emits the same 3 pinned tris bit-identically
   (2/2 FARMAX=0 tasks), and 0 at the default (control arm): the pin is the F5 ucode's own result, not our LLE. Sheets docs/owner_sheet_s7310_farmax.jpg,
   s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
3. **Owner decisions on defaults:** M5_B40_VALUE (s7558/s7564: default 0 is alive only via the s4889+s7476 compensations; =1 is retail and equally clean 6/6), RETINA=1, QOS_ALL=1, S7524_V2P=1 (s7526), SP_LATE=1 (s7537), DD_FOG_ALT, dd8 bundle, RENDER_TO_RAM=0 (s7385). Never flip without the owner.
   QOS_ALL evidence: s7277-s7281 (load freezes removed) + s7382 (the threads it raises are exactly the hot ones, DEFAULT otherwise).
4. **G5i hangar re-entry (s6995), G5a Gerrard V crash (s6893; s6998 writeback audit clean), G5b terrain drops
   (FWDWIN far-loss fix, tools/g5b_fwdwin_seamless.py), G5d logo (s6903), G5f knife lines (s6906; sheets
   s7005/s7006), G5g hangar lens (s6907), G5h cutscene background (s6908-s6919; re-held post-G6c s7698-s7700 incl. movies playlist): owner flight / look.**
5. **L15 21:9: owner re-flight after s6992 PTRMASK.**
6. **G1d close-out: owner judgement** (scratch/s6731/sheet_menus_owner.png); owner scope: why L7/L16/L17
   autopilot holds cycle the backdrop menu.
7. **Near-wall NEARLIFT, G3 21:9 holes (s7132-s7140), L4 cutscene SKYFILL_BOT (s7166): owner look.**
8. **Owner judgement / parked:** FPS60 feel, G3c sheets, native hangar geometry, rare dd4/dd8 gfx SIGBUS
   (single-source). Reopen on an owner report or side-effect failure.
9. **(PARKED by owner) G1(d) objective qualification.** PORTING-STATE s6640-s6687 first.
10. **RENDER_TO_RAM=0 CLOSED s7389: ready for the owner (OWNER-OPT-INS), default stays on.** Saves ~2.5 ms/gfx task in
    mission (s7385); abort-cut stale-upload stripe fixed (s7387, ROGUESQ_R2R_CPUUP=1 old); soaks L1/L4/L12 300 s pass (s7389);
    fb-cpu-reader census CLOSED s7391 (0 guest loads from a live colour image on 6 levels; build_fbld, ROGUESQ_S7389_FBLD=1).
    Not covered: RSP/RDP DMA reads (RT64 fb-as-texture owns those).
11. **G6 (owner 2026-11-18): G6a rumble, G6b controls, G6c stand-ins: all LANDED, close on the owner's hands/look** (headline).
    Full step history s7617-s7691 (stand-in steps 2-4, H-culled/H-far, draw proof, handoff polish) verbatim in PROJECT-OVERVIEW
    "(s7703 maintenance)".
12. **G3 retail flight det sweep (s7832-s7853).** Pair = port (VI_STAMP=1 + RETAIL_SNAP=1) vs retail CPO1 oracle (FTZ per
   FCR31.FS, s7841): render tris, HUD census, 460-w ramdump. lvl2/3/4 pinned = retail (s7840); lvl5 render exact (s7841); lvl5
   1-ulp camera fork CLOSED s7843 as oracle timing (chase dt = running min of the 1/60-snapped dt; 0x3D088887 only for raw dt
   low nibble 0, mupen CPO jitter; tools/s7843_dt_snap_replay.py, apply_s7842_chasehex.py, scratch/s7842/chase_cmp.py).
   **0x31=5..9 (s7844-s7853)** detail (seed pin + dt replay recipe, rumble/3D-sound timing class, 0x31=8 audio-clock) migrated
   verbatim to PROJECT-OVERVIEW "(s7862 migration)"; one-line verdicts in `tools/s7862_det_sweep_table.py`.
   **0x31=10 (s7854): H-exact.** Bespin, 2672 ticks, seed 36b554eb, 1 dt pin, no song switch, hp static. p1 rand/callers equal all
   2580 ticks (2 pinned runs). The 0x80043918 [ramdump] PC is in buildVisibleTerrainGridAroundCamera, so it runs 1x on no-terrain
   levels (vacuous record). s7849_det_pair.sh REC=1 (default) now dumps the 460-w record at tick marker 0x800FA730 on both sides,
   scored by tools/s7854_tick_rec_cmp.py: 0 diffs in 2580/2580 ticks; p2 forks tick 3; --control 100 is caught.
   **0x31=11 (s7855): H-exact.** 1539 ticks, seed 05e6d779, 2 dt pins, 12 hp hits, 9 song switches. p1: rand/callers, hp, all
   song switch ticks, rumble 16=16 and the 460-w record (1539/1539 ticks) all equal; p2 forks t0/t16, record t599; control ok.
   **0x31=12 (s7856): H-exact.** 5765 retail ticks (5674 compared), seed 90ef4fcb, 42 dt pins, death t5304 + respawn t5490, 11 song
   switches, rumble 5=5, record 0 diffs / 5673 ticks; p2 forks t0, control ok. Scorer tools/s7856_det_verdict.py (exit 0 exact /
   1 fork / 2 no-verdict); serial driver tools/s7856_det_sweep.sh OUTROOT v... (stops at first FORK).
   **0x31=13 (s7857): H-exact, residual timing-class.** 3903 ticks, seed 8d3c57d9, 73 pins: rand/hp/9 song switches/record nonpose
   all equal; only TIMING words 135/149 (3D-sound flags) from t1898 and one rumble pulse-length swap (6/5 vs 5/6). Verdict lines
   now end `residual=none|timing-class(...)` (s7855/s7856 none).
   **0x31=14 (s7857, corrected s7858): FORK = H-audio-clock only.** Song 01 ends t1396 retail / t1395 port (336/643 vs 334/640
   VI/buffers), rand forks t1413; record nonpose exact through t1395 with corrected pins (s7858 p4, control flip caught t100).
   The s7857 "port-side 1-2 ULP transient t892-899" was a HARNESS artifact (superseded below): one r1 `[hit]` line at tick 886 had a
   `[vi-poll]` printf spliced in, tools/s7849_det_pins.py dropped it and indexed dt by list position, so 118/160 pins after t886
   landed one tick early. Fixed (rejoin splices, key by record-row ordinal, exit 2 on a missing/duplicate tick); test
   tools/test_s7858_det_pins_splice.py (sweep row S7858_PINS; old parser fails it). Audit of every det-pair r1 log s7849-s7857:
   only s7857/v14 affected, all other verdicts stand. Port store watch now stamps `tick=` (ROGUESQ_STORE_WATCH_PTS) and
   tools/s7858_store_seq_cmp.py diffs per-tick store sequences vs an oracle `--watch-write --hit-vi-window --hit-cap` log.
   **0x31=15 (s7859): H-exact**, residual timing-class (w149 from t943). 1892 retail ticks, seed f58510db, 4 pins, hp hits
   t694-701 equal, songs t823/t1410 equal; port ends t1833 (305 s), so retail's t1848 death is past the compared window.
   **0x31=16 without the bonus unlock = DUPLICATE of 15** (retail seed, ticks, hp, songs identical; the game clamp at
   0x8006EE7C only caps >16, so the fallback comes from the locked bonus bit). With +0x39=0x60 (scratch/s7859/base_bonus.eep):
   retail = the self-starting race (6626-6930 ticks, seed ebdad279, 787 dt pins; dt-pin cap raised 512 -> 8192 in
   apply_s7844_dt_at.py + s7849_det_pins.py). Verdict FORK t395: retail crashes into the ground at t395 (hp 80->0, retry t458),
   port only at t786, and the port stops ticking after t849. The cause is the harness, not the port (H-input, single-source):
   retail's PP Start presses land at tick 0 and t458/t698 (the MISSION FAILED screen), but the port's AP fires 7-9 land
   pre-race and mid-run. det_pair's hangar-mission press schedule is invalid for the race.
   **s7860: bonus 16 (race) H-exact, H-input CLOSED.** s7849_det_pair.sh now takes PP_OVR/AP_OVR (unset = old schedules).
   Race recipe: PP_OVR=19.5,31.5,43.5:start; AP_OVR=6,11,11.5:w1024,19.5,31.5,43.5,67.5:start (the port needs that 67.5 s
   Start: without it the port waits on AVAILABLE CRAFT with 0 ticks). Port = retail on all 458 ticks (rand, hp 80->0 crash
   t395-403, 460-w record, rumble 5/5); every press is pre-race on both sides. Controls: p2 forks t0, flip caught t100.
   Data: scratch/s7860/v16s/score.txt. **The main-mission sweep 0x31=0..15 is COMPLETE**
   (8 and 14 = H-audio-clock FORK; 7 residual closed s7851; the rest H-exact or timing-class).
   **s7861: bonus 17 (Death Star trench) = H-audio-clock FORK:** p1 = retail t0-t1123 (rand, hp, 460-w record, rumble), seed fork
   t1124 = song-3 end (retail t1124 / port t1123, 643 vs 640 AI buffers); agrees with s6772. Recipe: PP_OVR=19.5:start,
   27.5:dright,31.5:start,43.5:start,55.5:start, AP_OVR=6,11,11.5:w1024,19.5,31.5,39.5:right,43.5,67.5,79.5:start, BASE_EEP=
   scratch/s7859/base_bonus.eep, 0x31=16. **Retail's SELECT LEVEL window is between its 4th and 5th Starts (PP 19.5-31.5; the
   5th = commit), the port's between AP 31.5 and 43.5** (cursor 0x800CDAC1 traced at 0x800C6674, s7861/probe). s7856_det_verdict.py
   now prints fork=audio-clock|unclassified (test_s7856_det_verdict.py, sweep row S7861_VERDICT).
   **s7862: bonus 18 (Hoth) H-exact, the det SWEEP 0..18 IS COMPLETE.** 6444 retail ticks, seed 43308409, 17 dt pins: rand/callers,
   hp (t586 150->130), rumble 2=2, 460-w record 0 diffs on 6291 ticks, no song switch (agrees with s6773); p2 forks t0, flip t100.
   Recipe = bonus 17's + PP 29:dright + 67.5:start (Hoth needs a 3rd retail Start after the commit; without it retail sat 305 s
   pre-flight, 0 ticks, scratch/s7862/v18_short) + AP 41:right; cursor probe C1 0x10->0x11->0x12 (s7862/probe). **Verdict table:
   `python3 tools/s7862_det_sweep_table.py`** (sweep row S7862_TABLE; re-scores the 10 retained score.txt rows, 10 hand rows cite
   their session; --control plants a mismatch): 17 H-exact, 3 FORK all audio-clock (0x31=8, 14, bonus 17). In every FORK the
   PORT song ends 1 tick early (3/3 same sign): b17 song 01 640/640 buffers equal, song 02 1869 vs 1872, song 03 640 vs 643.
   **s7863: the 3 FORKs are timing class, not a port audio-rate defect (g3-audio-clock-sign CLOSED).** (a) every AI buffer is
   a1=0x300 (immediate in the delay slot of both osAiSetNextBuffer jals 0x8008EE08/0x8008EE84), so H-buflen is dead by code;
   (b) `python3 tools/s7863_song_end_threshold.py --control` (sweep row S7863_SONGN): in all 10 song windows (3 forks + retail
   r1/r2) one song-end buffer count N fits both arms (b17 song 03 N=639..641, m9 N=640, m15 N=640..641), planted -1% rate
   caught in every window. Whole-run buffers/VI retail 1.9146 vs port 1.9139, per-VI cum drift -4..+2 with no trend (H-rate
   refuted). The port delivers 0-3 AI buffers per VI (host SDL-drain paced, events.cpp s4450 DRAIN=2048) vs retail's steady
   1-2, so the port crosses N one VI early (b17: +2 local lead at dVI 334). The 3/3 sign is one cue (~640 buffers, 167-168
   ticks) whose N sits on retail's tick edge in all three missions, not three independent samples.
   **s7864: ROGUESQ_AI_VI_CLOCK opt-in (determinism harness only, default off; events.cpp s7864).** =1 posts AI-done from the VI
   thread at rate/(192*60) per VI with a fractional accumulator (drain/HZ threads off); =2 uses the oracle's measured rate
   (48681812/2207/192/60 = 1.914746/VI, s7854 r1); _BPV / _SEED override rate and phase. Positive control
   (`python3 tools/s7864_ai_per_vi_hist.py --control`, sweep row S7864_AIHIST): port buffers/VI histogram {0:382,1:656,2:1252,3:1122}
   -> {1:299,2:3102} (retail {1:297,2:3175}); same-run drain arm keeps 0..3. **b17 still forks at t1124 in all 3 arms (=1, =2,
   =2+BPV 1.914588+SEED 0.28)**: song-3 song-relative count diff r-p stays -1 on 96-136 of 168 ticks; the seed moved the
   port's residual 0.294 -> 0.055 but retail's own rate wanders (1.914588 to t1123, 1.914722 whole run), so no constant clock
   holds retail's phase. Cause (mupen source, rs64-oracle ai_controller.c get_dma_duration/do_dma): each AI-done fires
   LEN*floor(cpu_counts_per_sec/(4*fs)) cycles after its DMA STARTS, and a DMA starts only when queued (gap when the FIFO ran
   empty), so the oracle's AI phase depends on guest queue latency. Remaining det lever: model DMA start/end events
   (NEXT.md g3-ai-dma-model). Single-source for the mupen reading (code only, not yet measured).
   **s7865: H-dma selected, H-const refuted (offline, `python3 tools/s7865_ai_dma_rate.py`, sweep row S7865_AIDMA).** mupen's
   DMA time is D = 0x300*floor(cps/(4*fs)) = 768*551 = 423168 cycles (fs 22047, AI_DACRATE 2207, VI delay 811092), so its
   GAP-FREE rate is 1.916714 buf/VI; retail measures 1.914459 -> the FIFO sits empty 0.118% of the time. A constant clock
   cannot be retail at any rate (the port's =1 rate 1.913802 is exactly the no-floor value). Single-source (one oracle run
   family; s7861/s7864 logs are the same deterministic run).
   **s7867: det sweep CLOSED as timing class (H-unmodelable selected).** ROGUESQ_AI_VI_CLOCK=3 (events.cpp "AI DMA" thread,
   stamp in audio.cpp queue_audio_buffer) = mupen ai_controller.c verbatim: 2-entry FIFO, AI_INT at DMA end, e = max(q, e_prev)
   + bytes*551/811092 VI. The game's AI loop (0x8008EE10) primes 1 buffer and queues 1 per type-1 message, so the FIFO is 1 deep
   in retail too: each buffer's gap = guest IRQ->osAiSetNextBuffer latency, retail 0.000615 VI (~10 us, from 1.914459 vs
   gap-free 1.916714), port 0.0197 VI (~330 us, host thread wake). b17 v17c: 1.8425 buf/VI, FORK t436 (worse than =1/=2 t1124).
   Retail's AI phase is set by guest instruction timing; a host-timed recomp cannot reproduce it, and a constant latency is the
   constant clock already refuted (s7864 v17c). Det sweep verdict stands as s7863: 17 exact, 3 audio-clock timing forks.
   **s7868: per-frame RENDER oracle on det-exact ticks: b17 render = retail, 1120/1120 frames.** `RBIN=1 zsh
   tools/s7849_det_pair.sh` keeps retail + p1 + p2 RDP streams; `python3 tools/s7868_det_frame_cmp.py RETAIL.bin P1.bin --plant
   --neg P2.bin` pairs frames by unique-signature offset vote and compares every frame's full multiset (tri edge coefficients +
   PRIM, texrect geometry + PRIM = HUD). b17 (scratch/s7868/v17, same det verdict: p1 = retail t0-t1123, fork t1124): 1120
   consecutive exact frames, 0 non-exact inside the exact span, ending at the fork; plant (1 tri YH+1) caught; unpinned p2 matches
   only the 101-frame boot logo. Two lines: det state record + independent RDP stream. Retained s7844 (0x31=5) pair: its whole exact span is
   PRE-flight (phase 6, intro cinematic + text screen; s7870 superseded the "tri-count = enemy-hit fork" reading: that diff is
   ~1190 frames before tick 0); p4 had no seed pin, so its flight is 0% exact. s7868 also fixed a torn (vi_n, vi_t_ns) read in the =3 DMA model (now under
   s7867::mtx) and classified the AI DMA thread in s7382/s7383/s7538/s7599.
   **s7869: 0x31=12 (longest exact mission, death t5304 + respawn t5490) render = retail for ALL 5662 flight frames.**
   `RBIN=1 zsh tools/s7849_det_pair.sh 12` (det H-exact 5765 ticks, residual none). s7868 cmp: retail 9272 / port 9704 frames,
   offset -524 (6173 votes), exact span port[3388:9704] = E431 N143 E5742; flight phase (port phase 7 = retail 512-wide,
   port 4042+) is 100% exact; plant caught, p2 neg PASS. The 143-frame island (port 3819-3961) is in the pre-flight 640-wide
   phase 6, BEFORE mission tick 0 (no seed/dt pin there), and `tools/s7869_island_probe.py` shows it state-driven: p1 and p2
   both diverge on the same retail frames 3295-3437 with DIFFERENT tri values (0/143 frames identical), both re-converge after
   (p2 E80 to the end of phase 6). A port render defect on equal input would give identical wrong tris in both arms. Two
   missions now render-exact on det-exact ticks (b17 1120, m12 5662). Pre-flight islands = unpinned window, not render.
   **s7870: 0x31=5 (mission 6) flight render = retail, 2383/2383 frames (death + respawn incl.). G3 det render line CLOSED: 3
   missions.** `RBIN=1 zsh tools/s7849_det_pair.sh 5` (H-exact whole run, p2 forks t0). s7868 cmp now prints phase tables, HUD
   frames per phase, places islands by phase, and scopes --neg to the final (flight) phase (old whole-run bar failed a correct
   p2 that matched the deterministic pre-flight cinematic). Islands: text screen p1/p2 differ (state); cinematic opening p1 ==
   p2 but offset = 0.51 x per-frame speed (scratch/s7870/phase_a.py): half-frame animation-time phase, timing class.
   **s7871: 0x31=10 (Bespin, mission 11) flight render = retail, 2519/2519 frames: 4 missions render-exact on det-exact
   ticks (b17 1120, m12 5662, m6 2383, m11 2519).** Det p1 H-exact 2525 ticks (seed/calls/rec/pose/timing None), p2 forks t0;
   plant caught, phase-7 neg PASS. Pre-flight phase 6 islands: A port[3395:3554] = the SAME 64 PRIM-FF opening-cinematic
   tris as m6 island A (identical values, p1 == p2), i.e. the s7870 half-frame timing phase recurs per mission; B
   port[6067:7121] (1054 frames, up to 869/873 tris) p1/p2 wrong by different values on 813/1054 -> state (unpinned window).
   **s7872: island A (cinematic half-frame) is NOT dt:** retail dt row 2899 = port fr 3428 - 529 (same offset as the RDP
   alignment) and both get dt 1,2,2.. from the cinematic's first frame (`tools/s7872_frame_clock.py`, retail CPO1 trace of
   0x8000BBE8 + 0x8000BE28). H-count (stall parity) refuted. Retail timeSnapshotFiller el is phase-dependent (0 on most pre-flight
   frames incl. the cinematic, 1 VI in a hangar stretch / post-load frames / flight); RETAIL_SNAP pins 811160 everywhere.
   Lever `ROGUESQ_S7872_SNAP_WIN=lo:hi:el` (VI window, after the pin): el=0 at VI 5560-6300 MOVES island A (p1 values differ
   from the p2 control on 164/168 frames) but far off (offsets -489..244), not onto retail; whole-run el=0 forks boot/menus.
   **s7873: H-snap REFUTED at retail values.** timeSnapshotFiller stores el/rate + VIperiod*(vd<2?1:vd) (no el=0 special
   case; RETAIL_SNAP also pins vd=1, so s7872's el=0 arm stored 1 VI = half retail). Retail store at 0x8000BF38 (`tools/
   s7873_snap_value.py`, oracle scratch/s7873/rvd): cinematic = 0.03333 (el 0, vd 2), post-load frame 0.01667; port pin 0.03397.
   Arms A (0.03333 from VI 5584) and B (A + 0.01667 on the post-load frame) both give island A unchanged (regression 0.510 x
   speed - 0.016, = pin reference), with post-load dt 1 VI (A) vs 2 VI (B): neither the stored value nor the post-load dt
   carries the half frame. **s7874: H-phase (raw clock) and H-audio REFUTED; slug PARKED (budget rule 8).** `python3 tools/s7874_clock_census.py`
   (control PASS): game code has 0 inline Count reads (only 2 mfc0 Compare in a data gap), 0 osGetCount callers, 14 osGetTime
   sites; on the render path only timeSnapshotFiller consumes raw time (0x8011A914 since-last-frame -> profiler only). Det pair
   p1 ROGUESQ_AI_VI_CLOCK=3 (mupen AI-DMA clock; boot timeline moved, off -532 vs -535 = lever control) vs p2 default: island A
   identical in both (0.510 x speed - 0.016, 6244/6244). Island A is pre-flight timing class, open: H-index (frame-counter offset)
   / H-retail-rdp (capture lag). Retail bin: scratch/s7872/v10/r1 (hard-linked s7873/s7874).
   **s7875: 0x31=2 (mission 3) flight render = retail, 3804/3804 det-tick frames: 5 missions render-exact** (b17, m12, m6, m11,
   m3). `env RBIN=1 zsh tools/s7849_det_pair.sh 2`: p1 H-exact 3807 ticks (seed/calls/rec/pose None; timing word 149 from t3102),
   p2 forks t0; plant caught, phase-7 neg PASS. rc 1 is NOT a flight defect: retail flight frames 3408-7212 = 3804 for 3807 ticks
   (1 frame/tick), then a 10-frame tri-less blank on both sides (retail 7212, port 7739) ends the mission ticks; the 1953
   post-blank phase-7 frames are an end-of-mission screen (212 tris PRIM 0A0000FF, texrects 128->470) with identical
   counts/texrects and ~2-5% of tris off by 1/4-1 px (animation phase, outside the det window; scratch/s7875/*.py).
   **s7868 scorer caveat: "phase 7" runs past the last mission tick; bound flight by the post-flight blank.** Island A
   (cinematic half-frame) did NOT appear in m3 (phase 6 exact port 3391-3752); pre-tick-0 island 3752-3935 = state (p1/p2
   differ on 183/183).
   s7865 gate note: s7723_retained_controls is allow-listed RED (6 retained s7392-s7399 run.log.zst deleted 2026-11-23
   08:25 by an unidentified scratch wipe); gate_trace.py now records importlib-loaded modules via their .pyc source.
13. **Closed audit classes / censuses / gates (old items 1-36, s7808-s7815 siblings): ALL CLOSED, 0 open.** Full text + per-item
   tool lists verbatim in PROJECT-OVERVIEW "(s7848 maintenance)" (and "(s7792 maintenance)"). They stay live through
   `python3 tools/s7651_gate_sweep.py` (--jobs 2) and `python3 tools/s7719_regen_gate.py --strict`.
14. **Closed G3 threads (verbatim in PROJECT-OVERVIEW "(s7848 maintenance)"):** post-G6c fidelity (s7793-s7800: L1/L10/L12 16:9,
   L1/L4 21:9, dd2 H-equal, handoffs H-clean; STANDINS 300 s holds 19/19 s7802); oracle det mode `--det` default (s7817-s7819);
   lvl1 det pair title->flight no port render defect (s7820-s7831); lvl2/lvl3 pitch = dt/snapshot path, not render (s7832-s7836);
   VI_STAMP=1 determinism opt-in (s7837, soak PASS s7838); lvl4 rest-pitch fork = timeSnapshotFiller el=0 on a fast host
   (s7838-s7839 -> ROGUESQ_RETAIL_SNAP=1, s7840 two lines lvl2/3/4); s7841 oracle FIX: arm64 mupen never emulated FCR31.FS
   (tools/oracle/patches/arm64-fcr31-fs-ftz.patch, RS64_ORACLE_FTZ=0 = old): retail captures before s7841 carry denormals,
   so any port-vs-oracle diff in a decaying float is suspect there. Active continuation = item 12.

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7417, s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7748-7848; search bounded windows only.
