# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7928 (2026-11-24).
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
- **s7927 "the port SKIPS retail's flight-entry MusyX wait (gate 0x800A0F50 == 0 at flight entry)"** (superseded s7928). Believable:
  retail made 8 waits, the port 6, and every retail wait came from musyxNoopStub's gated jal. But nobody matched the waits by
  caller: retail's flight-entry wait is runVideoFrameTick from mainGameLoop@0x8003E360, and the port's 6th wait (+62 s) is that same
  call with the gate at 1. The missing ones are the B40 boot wait and one route-dependent menu transition.
- **s7915 "whole-run p1_rand traces differ in all 6 arms (md5)"** (superseded s7916). Believable: the six files' md5s all differ. But
  C1's (site,value) stream is a strict prefix of D1's (C1 stopped 42 VI sooner, VI stamps off by 1): the element-exact pair shares its rand stream.
- **s7911 "m6 island B is deterministic game state (state other than rand values)"** (superseded s7912). Believable: the lag re-locks at
  532 and full rand replay changed nothing. But two same-config port runs differ on the element as much as port vs retail: it is
  run-to-run nondeterminism in one particle element, not a reproducible state difference.
- **s7905 "island B absent on the rebuilt binary; leading reading a host-timing race"** (superseded s7906). Believable: 3/3 exact
  right after a rebuild. But loop soaks on the same binary give 708 twice at different loads; class = det_cmp offset gap 28 vs 29.
- **s7904 "island B = flame-block arena placement/timing (H-sched vs H-alloc-seq)"** (superseded s7905). Believable: port RAM held
  retail's correct blocks at other addresses. But the residual vanishes 3/3 on today's rebuilt binary (same recipe/pins),
  and the addresses are shared bump-arena slots, so "other address" was never a per-object fact.
- **s7903 "island B residual = rand-replay ordinal keying, one burst frame per instance with opposite signs"** (superseded s7904).
  Believable because the port's flame bytes hash-matched retail's adjacent-frame blocks. But both two-site skews fail (one is a
  no-op on the residual) and retail's correct current blocks exist in the port's RAM at other arena addresses: placement/timing.
- **s7892 "RETAIL_SNAP=3 is m11-only: on m6 the crawl clock lead is 0 but island A stays"** (superseded s7894). Believable because
  two instruments agreed. They were two runs: the crawl dump (el 0 at fire 6, delta 0) and the render arm m6s3c (el 781250 at fire 6,
  so =3 never took effect there). =3 stores real el; with the crawl frame forced to retail's 1 VI, m6 island A disappears.
- **s7873 "the post-load dt (1 vs 2 VI) does not carry island A's half frame"** (superseded s7891). Believable because a
  retail-valued post-load window left island A unchanged. That window (VI 5584:5587) was placed from computeFrameDeltaTime's
  post-load frame and never checked the crawl dt site. The s7891 crawl-site dump shows the crawl's post-load frame IS the half frame (SNAP=3 removes it).
- **s7879 "the same Start schedule (19.5..91.5) runs on both sides"** (superseded s7880). Believable because PP and AP carry the
  same times; but PP is placed from a different anchor and the oracle adds a fixed 16 s press, so the port is 1 press short.
- **s7840 "0x31=3 (mission 4) pinned port = retail, H-exact"** (superseded s7877). Believable because every tick of that run matched;
  it was a 170 s run that ended before the t2111 death. At 305 s the respawn forks on the death-song end (audio-clock class).
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
- Frame-exact presses: `ROGUESQ_AUTOPILOT_CLOCK=vi` keys autopilot to ultramodern's VI count (port twin of oracle `--clock vi`, s7820). `f<N>:key` = N fullsyncs after the previous fire (s7907). Its latch s_last_fs has a FW-census row (s7908); any new host scalar latch needs one too, or s7530 reads RED.
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
(s7897: any new static pointer in src/ needs an s7613 HP census row, class base/host/gated/..., or the exit gate goes RED.)
0a. **G5c freeze gap: CLOSED on measurement (s7919-s7921); owner judges feel.** In-flight bar met on every owner-recipe ring
   s7694-s7919 (s7920 `tools/s7920_hold_class.py`: the s7806 L4 holds were a mission restart). The one IN-SCENE pre-flight hold
   (t=43.4 s, 9DE900/A62B80, 275-295 ms) is the menu -> hangar entry and is RETAIL (s7921, two lines): retail oracle
   (`--vi-holds 4 --hit-vi`, field-normalised) holds the same transition 17 VIs around the same waitForMusyXAudioTaskDone spin
   (0x80091EC4 -> 0x80091F44, 8-9 VIs; every retail transition wait sits in a 15-19 VI hold), then 123 more VIs on the hangar
   load; port host sample on that hold = game thread in musyxNoopStub -> waitForMusyXAudioTaskDone ~103 ms. Port <= retail at
   every transition. Oracle trap: interlaced fields alternate the origin by one scanline (512: 0x656400/0x656800), so raw-origin
   hold counts read "no holds"; `--vi-holds` handles it. The 17 s "hold" at t=11 s is the single-buffered animating title.
   s7922 whole-route table (`tools/s7922_transition_table.py <ring> <oracle.log>`, planted PORT-LONGER/EQUAL controls, anchored at
   the hangar-entry hit): 6/6 port transitions EQUAL or PORT-SHORTER vs retail on BOTH owner-recipe rings (s7919, s7921): boot
   15-18 vs 238 VIs, ->title 17-18 vs 18, title->menu 0 vs 0, hangar 16.5-17.7 vs 140, ->briefing 17 vs 124, ->mission 23.5 vs 212.
   Pre-flight route is retail-paced; owner-queue row 20. s7925: pairing now two-source: present-ring `M` rows (port MusyX wait,
   src/rsp/s7324_rcp_spill.cpp rs64_s7925_wait_mark) pair 6/6 with the hold ordinals on 2 runs (`--waits`, shift-1 mutation 0/6;
   sweep row S7925_WAITPAIR); port waits 133-150 ms = retail's 8-9 VI spin.
   s7923: `tools/agent/ring_stalls.py` max_vihold_ms (soak summary field) now excludes animating holds (>2 s, gen advancing on
   >=90% of rows) into a new `max_animhold_ms`; `--selftest` planted controls. Re-scored owner rings: 17302/17318 -> 392/391 ms,
   so the field now reads real freezes. Verdict/summary lines before s7923 carry the raw ~17300 (title). vi_stalls30s unchanged.
   s7924: the loop verdict line now ends `freeze_arms=<n> freeze_na=<m>` (tools/agent/soak_verdict_fields.sh): arms whose
   max_vihold_ms or max_gap_ms >= FREEZE_MS (1000) - the G5c 1-5 s freeze that vi_stalls30s (>=30 s) cannot see. Controls in
   tools/agent/test_soak_verdict_fields.sh (planted 1.5 s frozen ring -> 1, 17 s animating -> 0, no-anim-rule mutation -> 1).
   12/12 recent owner-recipe rings re-scored -> freeze_arms=0 (max vihold 374-408 ms); fold any freeze_arms>0 as a G5c datum.
   s7926-s7928: datum CLOSED = port TAKES retail's flight-entry wait (s7927 "SKIPPED" superseded). s7928 ROGUESQ_S7928_GATEW=1
   (present ring: G row per store to gate 0x800A0F50, C row per runVideoFrameTick caller site; runVideoFrameTick is the
   per-TRANSITION tick and calls musyxNoopStub first) + retail oracle `--watch-pc 0x80001354,0x80091EC4 --hit-vi` (HLE RSP; cxd4
   stalls the 640 intro): retail 8 calls, 8/8 waits: menu, initScene, menu x4, initScene, mainGameLoop@0x8003E360 (flight entry).
   Port 7 calls: menu (gate 0 = B40 default), initScene, menu x3, initScene, mainGameLoop@0x8003E360 = the port's 6th slow wait.
   So 8 vs 6 = B40 (1) + one fewer menuOverlayInit transition on the autopilot route (1; route, single-source). Gate is left 1
   after flight entry, never 0. `python3 tools/s7928_gate_writers.py <ring> [--oracle <log>]`, sweep row S7928_GATEW. Nothing open.
   s7920 also fixed an ungated diagnostic: PATCH s5885 destroy-ctx did backtrace+symbolisation in normal play (class audit: 1/63 sites).
0. **G3 pre-flight retail match on det pairs: CLOSED (s7891-s7917).** Island A H-index (s7891/s7894); island B harness frame/VI
   class (s7907); +28 frames = one shorter port load stall, retail load-time cost (s7909/s7910); m6 island B particle element =
   f(global rand stream position) = host-paced frame count, timing class, no port value to fix (s7912-s7917; DET_CLOCK=1/2 and
   S7913_CLOCKLOG remain as opt-in instruments). Full text verbatim in PROJECT-OVERVIEW "(s7918 maintenance)".
1. **G5e fog: owner look.** ROGUESQ_DD_FOG_ALT=1,3,1 qualified at 16:9 and 21:9 (headline). Only if the owner asks for
   more haze at 21:9: sweep ke 2 / 2.5 with `tools/s7306_fog_219.zsh l1k2:1:1,2,1`.
2. **21:9 dd>1 left-edge sliver FIXED (s7310, ROGUESQ_DD_FARMAX default 32767, 0 = old), qualified s7312: owner look.**
   Far above ~36-40k units makes the F5 clip pin sky-dome edge panels to fb x=0 (two lines: RDP W decode + presented
   left-column count, 12 same-pose arms). **Mechanism now two-source (s7751):** the independent cxd4 RSP, fed the same
   captured gfx task (ROGUESQ_S7751_SNAP + tools/s7751_cxd4_task/replay), emits the same 3 pinned tris bit-identically
   (2/2 FARMAX=0 tasks), and 0 at the default (control arm): the pin is the F5 ucode's own result, not our LLE. Sheets docs/owner_sheet_s7310_farmax.jpg,
   s7312_farmax_l5_l12.jpg. POSE_FREEZE "<x" = falling crossing (L12 needs it).
3. **Owner decisions on defaults:** M5_B40_VALUE (s7558/s7564: default 0 is alive only via the s4889+s7476 compensations; =1 is retail and equally clean 6/6; s7927: =1 also restores the boot-menu MusyX wait the port skips, s7928), RETINA=1, QOS_ALL=1, S7524_V2P=1 (s7526), SP_LATE=1 (s7537), DD_FOG_ALT, dd8 bundle, RENDER_TO_RAM=0 (s7385). Never flip without the owner.
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
12. **G3 retail flight det sweep (s7832-s7890): CLOSED.** 19/19 missions render-exact on det ticks (m1-m16, b16, b17 pre-fork,
   b18; slug g3-det-render-coverage); one-line verdicts in `tools/s7862_det_sweep_table.py`; recipe tools/s7849_det_pair.sh +
   tools/s7856_det_verdict.py / s7856_det_sweep.sh. Full text verbatim in PROJECT-OVERVIEW "(s7918 maintenance)".
   s7865/s7893 gate note: the "unidentified scratch wipe" is the OWNER's launchd job ~/.local/bin/rs64-scratch-compress.sh
   (6 h: zstd >12 h) -> rs64-scratch-prune.sh (deletes >7 d, >64 KB files not cited by EXACT path, .zst stripped, in a
   tracked file; log ~/Library/Logs/rs64-scratch-prune.log). Dir-only or '.zst' citations do not protect, so it ate the
   s7392-s7399 logs (s7723 RED) and the s7435/s7439/s7442 sample_N.txt (s7433/5/6/7/8 + s7441 RED, all allow-listed,
   unrecoverable). Since s7893 tools/retained_captures.txt (tools/s7893_retained_manifest.py, refreshed by loop.sh every
   iteration, --check / --control) cites all 766 surviving gate inputs by exact path. A new retained capture is safe only
   once it is cited in a gate ARGS row or a tools/s7*.py literal. gate_trace.py records importlib-loaded modules.
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
