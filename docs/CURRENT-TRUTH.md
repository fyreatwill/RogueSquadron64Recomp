# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, as of Session 7822 (2026-11-22).
`PORTING-STATE.md` is the chronological ledger; durable and migrated material lives in
`docs/PROJECT-OVERVIEW.md`. The full s7416 text of this file (every audit class AQ-BZ s7373-s7416 with all numbers,
controls and tool flags) is archived verbatim in PROJECT-OVERVIEW "Migrated from CURRENT-TRUTH (s7417 maintenance)"; item-1 classes DG-EO in "(s7491 migration)"; classes CC-DH s7420-s7451 in "(s7452 maintenance)";
s7315-s7369 classes in "(s7370 maintenance)"; the s7306 headline chronology in "(s7307 maintenance)"; older text in
"(s7187 maintenance)" and "(s6994 maintenance)"; s7533 Next-steps items 1,12,15-21 (classes FD-FZ) in "(s7534 maintenance)"; s7535-s7576 headline + items 17-21 + pre-s7300 superseded in "(s7581 maintenance)"; s7702-s7790 headline + Next-steps items 1-36 in "(s7792 maintenance)"; s7579-s7616 headline + items 19-46 in "(s7622 maintenance)"; s7647-s7659 headline + items 21-35 in "(s7662 maintenance)"; s7617-s7702 headline + item 20 (G6) in "(s7703 maintenance)"; s7702-s7743 headline + items 22-32 + s7312-s7418 superseded in "(s7747 maintenance)". Grep there for any sNNNN.

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
  RENDER_TO_RAM=0, DD_FOG_ALT=1,3,1 look, STANDINS=1 look (G6c), rumble/controls feel (G6a/G6b), launch presets `--preset tv|ultrawide|window`.
- **Sweep:** `python3 tools/s7651_gate_sweep.py` (--jobs 2, iron rule 0) ~216 gates, 0 RED, 0 HOLLOW; stop_gate blocks RED. The live
  RecompiledFuncs tree IS the regen replay: `tools/s7719_regen_gate.py --strict` byte-compares it, so ANY hand edit under
  ../N64Recomp/RecompiledFuncs turns the sweep RED (put it in a fixup/apply script). Ucode: `tools/s7741_ucode_regen_gate.py --controls`;
  after a fixup_factor5_ucode.py edit `zsh tools/ucode_regen.sh snapshot`. After a regen `python3 tools/s7734_compiled_reader_census.py`.
- **s7788-s7791 vendored fixer pruning CLOSED:** dead-emitter census 0 dead; 257 never-run blocks deleted (s7790), shadowed-block prune
  1 block (s7791); `--strict` 0 differ, census HIT 326. **s7781-s7787 hook classes CLOSED** (s5660 unaligned-store hook value/address fix,
  load-hook hole, 4 pc-literal emitters).
- **Retained captures are zstd'd (*.zst):** any tool reading scratch/ must go through tools/rs64_zopen.py (zopen/resolve/materialize).
  s7802/s7803 found 5 tools silently blind to .zst inputs (s7753/s7756 gates, s7441 + s7442 sample censuses read windows=0, s7773
  overlay-swap witness saw 99 of 956 logs). s7441 is now a sweep gate (S7803_RETAINED, pre-fix s7439 capture = planted RED);
  s7773 witness over all retained logs: mission>menu swaps 63 (was 2), 0 "Failed to find function". REPORT rows left: s7031, s7210
  (inputs verified gone). **Class closed with a guard (s7804):** tools/s7804_zst_blind_lint.py (sweep row S7804_LINT) reads RED
  when any swept or CURRENT-TRUTH-cited tool without rs64_zopen names a capture literal matching a zst-only retained file
  (planted controls RED/ZOPEN/GREEN, real pre-fix s7763 RED). Its first run found 3 more: s7415 skipped 5 soak logs (205 now, verdict
  unchanged), s7616 `--witness-sample scratch/s7616/sample.txt` and s7763 `--offline` crashed FileNotFoundError (now CLOSED 10/10
  and 12 cmds 0 mismatch). Waiver for a non-input literal: `# zst-ok: <reason>`.
  **Argv-borne paths (s7805):** zopen()/new zbytes() now self-resolve `<path>` -> `<path>.zst`, and
  tools/s7805_cited_cmd_zst_check.py (sweep row S7805_CITED, ~47 s) runs every doc/ledger-cited `tools/X.py ... scratch/...`
  whose arg is zst-only: first run 11 RED (FileNotFoundError), all fixed via zopen/zbytes -> 10 GREEN; leftovers are not format
  defects: sample_callers / g1e_drain_blocks ledger lines omit argv, s7427 `--trace` replay symbolizes with atos against the
  CURRENT binary (now prints STALE-BINARY rc 4 instead of a false TRACE CONTROL FAIL), apply_* not run (mutator).
- **Latency (s7766/s7767):** FPS60 58.3 ms, retail 75-86, FPS60+VI_LOCK=1 53.7 ms; window mode does not change it (FULLSCREEN=2 exists).
- **Crash reports:** `python3 tools/crash_reports.py --since <date>`; a NEW report outranks all other work (s7664).
- **s7806 public-build check:** the owner's binary carried a clang-built patches/heap_guards.o (built 2026-10-17 18:06, before
  /opt/homebrew/bin/mips64-elf-gcc was relinked from the clang wrapper to gcc 14.2 at 18:33); make never rebuilt it, so the public
  build (all gcc) differed (9 vs 14 patch funcs). Behaviour-neutral (heap_guards code is dead: override renamed unused_patch_ s6269; live
  bodies identical after address normalisation; patch .data/.bss/.rodata empty). Fixed: patches/Makefile toolchain stamp
  (.toolchain_id; same cc 0 rebuilds, changed identity 4) + CMake DEPENDS on MIPS_GCC. s7420 census: absent patches tree now DEFER
  (was OPEN, a spurious WARNING in every clean build), control (5), `--require-tree` run by build-from-scratch.sh after the build.
- **s7807/s7808:** findAndUnlinkSmallestEntry (gcc patch body) is never called in play (0 calls lvl1 dd3, L4/L1 dd4). Its shipped
  recompiled body is runtime-qualified OFFLINE instead (s7808, `python3 tools/s7808_find_body_diff.py --controls`, sweep row
  S7808_FIND): == native model == recompiled retail 0x8002221C over 262,876 calls, mutant/plant controls PASS. After any build that
  relinks patches.elf, rebuild PatchesLib (s7807 H-stale: patches.c older).
- **s7809 gcc patch-body class CLOSED:** `python3 tools/s7809_patch_class_diff.py --controls` (sweep row S7809_PATCH_CLASS, ~2 s)
  enumerates every RECOMP_FUNC in RecompiledPatches/patches.c (9): 3 live overrides (isCinematicActive, setRngSeed differential here,
  findAndUnlinkSmallestEntry delegated to S7808_FIND), 6 dead (unused_patch_allocateDisplayListBuffer + 5 heap_guards helpers reachable
  only from it; no reference to unused_patch_* anywhere). Shipped wrapper+body == recompiled retail twin over 20,000 trials each
  (r2, callee-saved regs, watched windows + full 8 MB every 64 trials), 0 mismatch, all branch-coverage counters >0; planted body
  mutants H-differ 2/2, RAM plant 207/207, classifier plants (unrowed patch / dead helper made reachable / unused_ referenced) RED 3/3.
  A NEW C patch turns the sweep RED until it gets a ROWS/DELEGATED entry.
- **s7811:** s7420 parser census re-closed (OPEN 0): new census-scoped tools must use the weak-aware header form
  `^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC`, never `startswith("RECOMP_FUNC")` — run `tools/s7420_parser_census.py` before committing one.
- **s7810 host-override class CLOSED:** `python3 tools/s7810_host_override_diff.py --controls` (sweep row S7810_HOST_OVR, ~2 s): host
  definitions shadowing a RECOMP_FUNC = 1 (zmemcpy; recomp_entrypoint is only declared). Pre-fix H-differ: host faulted on a
  zero-extended KSEG0 pointer (rdram + 4 GB) that retail copies; FIXED (sign-extend canonicalisation, upstream_compat.cpp). Post-fix
  == retail over 20,000 trials, all 9 coverage classes > 0, 0 r2 readers at the 72 call sites; mutant / fix-revert / RAM / census /
  scanner controls PASS. L1 150 s live hold clean. A new host override turns the sweep RED until it gets a row.
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

Spec: ITERATION.md item 3c (no backlog-exhausted block). Renumbered s7792 into one sequence; the s7790 numbering (1-36) is
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
12. **Closed audit classes / censuses / gates (old items 1,12,13,14,15,16,17,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36): ALL CLOSED, 0 open.** Full text verbatim in
   PROJECT-OVERVIEW "(s7792 maintenance)". They stay live through `python3 tools/s7651_gate_sweep.py` (--jobs 2) and
   `python3 tools/s7719_regen_gate.py --strict`. Per old item: title -> its tools (rerun after the matching kind of change):
   - old 1: Audit classes CC-FZ s7420-s7533: ALL CLOSED
   - old 12: Rerun-after-change censuses (all CLOSED, 0 defects; tool list verbatim in PROJECT-OVERVIEW "(s7534 maintenance [tools/s7507_rsp_ctrl_flow.py tools/s7527_host_replace_audit.py tools/s7542_gc_census.py tools/s7543_gd_census.py tools/s7546_gf_census.py tools/s7547_gg_census.py tools/s7548_gh_census.py tools/s7549_gi_census.py tools/s7550_gj_census.py tools/s7555_go_census.py tools/s7595_sv_census.py tools/s7606_hc_census.py tools/s7610_ov_census.py tools/s7615_dq_census.py tools/s7741_ucode_regen_gate.py tools/s7742_fixup_idem_gate.py tools/scan_selfbranch.py]
   - old 13: Closed, reopen only on an owner report: [tools/apply_symbol_renames.py]
   - old 14: Harness discipline (CLOSED s7313-s7314, s7332): [tools/rs64_game_pid.zsh]
   - old 15: Idiom-class audits s7315-s7416 (AQ-BZ) and their runtime soak folds: ALL CLOSED/PASSED
   - old 16: Default-on fixes from the audits (=0 / old value restores the previous behaviour):
   - old 17: Classes GA-GR + 19b/19c/19d + S6892/GUARD-6 + do_break/float->int (s7535-s7576): ALL CLOSED [tools/regen_front.sh tools/regen_replay.sh tools/regen_verify.sh]
   - old 18: After-regen UB gates (all CLOSED, rc 0 expected; rerun s7693 on the post-G6c tree: all rc 0, BLIND=0, FOLDED=0 [tools/build_ubsanc.sh tools/s7575_break_census.py tools/s7575_ir_calls.sh tools/s7576_trunc_census.py tools/s7577_ubsan_sites.py tools/s7577_ucode_ub_census.py tools/s7579_bounds_report.py tools/s7580_lui_identity.py]
   - old 19: Rerun-after-change censuses s7579-s7616 (all CLOSED, 26/26 rc 0 s7693; RG --witness takes >=2 of s7103/s7108/s
   - old 21: Classes RP, HD, HB, ST, AT, CF, TS, TS-2, TS-3, TS-4, MK8 + walker fusion + spike cost + closed-gate drift (s7 [tools/s7639_st_census.py tools/s7640_at_census.py tools/s7642_tsan_rt64_build.sh]
   - old 22: s7663-s7718 owner-setting, crash-report, sweep and agent-gate items: ALL CLOSED [tools/agent tools/agent/run_tests.sh tools/crash_reports.py tools/s7705_fbread_flight.zsh tools/test_s7705_join.sh tools/test_settings.cpp]
   - old 23: G6c coverage CLOSED on L1/L10/L12 (s7749 L12, s7750 L10+L1): no gap. [tools/s7749_life_tally.py]
   - old 24: s7310 FARMAX mechanism: CLOSED two-source (s7751)
   - old 25: cxd4-vs-port RDP residual: CLOSED (s7752); residual (a) = cxd4 VU defects, not precision (s7815). [tools/s7752_port_task/harness tools/s7752_render_diff.py]
   - old 26: RDP-output regression gate: LANDED (s7753), widened s7754, in the sweep. [tools/s7753_capture_snaps.zsh tools/s7753_rdp_output_gate.py tools/s7754_capture_route.zsh]
   - old 27: Hangar gfx tasks are NOT snapshot-replayable (s7754 H-state, measured): [tools/s7755_hstate_visibility.py tools/s7756_hstate_gate.py]
   - old 28: Input latency (s7766): measured, H-1frame. [tools/s7766_inlat.py]
   - old 29: FPS60 L12 half-rate phases: CLOSED s7769 as an unreproduced transient (not owner-reported). [tools/s7768_fps60_rate.py tools/s7769_ring_genrate.py]
   - old 30: Placeholder census (s7770): rename sweep CLOSED on evidence. s7773 witness re-run s7803 over .zst logs: 63 mission>menu swaps, 0 aborts. [tools/agent/test_rename_census_gate.sh tools/s7770_placeholder_census.py tools/s7771_jal_target_census.py tools/s7772_ovl_lookup_audit.py tools/s7773_ovl_fnptr_audit.py tools/s7773_ovl_swap_witness.py tools/s7774_slot_run.zsh tools/s7774_slot_scan.py tools/s7776_tblwatch_score.py]
   - old 31: Dangling resident-global class (s7777-s7779): CLOSED 7/7, 0 defects. [tools/s7777_dangle_score.py tools/s7779_arena_score.py]
   - old 32: FB-arena escape class (s7781): CLOSED s7784, H-clean, 0 defects. [tools/apply_s5660_unaligned_store_census.py tools/s7781_escape_score.py tools/s7781_flag4_census.py tools/s7783_shared_slot_score.py tools/s7784_ustore_base_census.py tools/s7785_store_hook_reg_census.py tools/s7785_ustore_fallout.py]
   - old 33: Load-hook register/coverage class (s7786): CLOSED, 0 mixups, 1 hole fixed. [tools/s7786_load_hook_reg_census.py]
   - old 34: Hook pc-literal class (s7787): CLOSED, 4 emitters fixed. [tools/s7787_hook_pc_census.py]
   - old 35: Dead/partial emitter class (s7788): CLOSED, 0 open. [tools/s7788_dead_emitter_census.py]
   - old 36: Quiet-skip vendored blocks (s7789): CLOSED, 0 open. [tools/s7789_replace_site_census.py tools/s7790_prune_dead_blocks.py]
   - s7808-s7812 non-retail-by-default siblings: gcc C-patch bodies (s7809), host overrides (s7810, zmemcpy fixed), fixup hunks
     (= class GR s7558, still gated), recomp.h helpers (s7812: 60 helpers 0 OPEN; memory-layer differential MEM_*/LD/SD/lwl..sdr/cop1 RM
     0/200,000 vs a big-endian byte model, 3 mutants + 4 controls PASS): ALL CLOSED. [tools/s7809_patch_class_diff.py tools/s7810_host_override_diff.py tools/s7812_recomp_h_census.py]
   - s7813 host-callee class (last sibling) CLOSED: 364 distinct non-RECOMP_FUNC callees (pristine regen_front emission vs live),
     71 EMIT (62 libultra/IDO replacements all live rows of s7400 + BJ/BK/BL/BQ; libm s7415; traps s7416/s7575; cop0 s7405/s7409),
     6 force-header helpers, 230 GR hooks, 32 diag, 14 feature libm, 7 runtime, 110 host mem* sites 0 raw-RDRAM; 0 OPEN, token-walk
     enumeration equal (hollow=no), 9 controls PASS; sweep row S7813_CALLEE. Found: s7812 scanned recomp.h only, but CMake force-includes
     include/rsp_dpc_macros.h (MEM_WU, RS64_DIV32/DIVU32, RS64_TRUNC_W_*, fprintf->rs64_diag_fprintf): all already evidenced (s7086/
     s7575/s7576/s7432). Latent: N64Recomp lowers ceil.w.d as bare S32(ceil()) (the s7576 UB shape; s7576 counted 0 CEIL sites by helper
     name); its only site, ceilDouble 0x80093E60, has 0 calls and 0 address refs (gated: a caller turns ceil OPEN). [tools/s7813_callee_census.py]
   - s7814 include-resolution class CLOSED: the resolved header set of every generated TU (game C, RecompiledPatches, 3 LLE ucode TUs)
     in build/ + build_fbld/spwm/asan, taken from the compiler (.o.d of all TUs == a fresh `-M` of the real make command, 10/10 pairs),
     0 OPEN: every project header is scanned by a census/harness, DECL, or dead-in-TU (ultra64.h). Shadows: include/fbld and
     include/spwm recomp.h (diagnostic builds only) pass through bit-exactly vs upstream (2 M inputs, all wrapped MEM_*/LD/lwl/lwr/ADD32),
     so s7389/s7391 findings transfer to build/. Per-helper map of the LLE ucode C: 70 helpers all evidenced; the gap found was
     VMOV (152 sites) + VSAR (74), never checked against an independent RSP -> new tools/s7814_vmov_vsar: 2,048,000 compares vs cxd4,
     0 diffs, whole vpu state, 3 mutants fire. 6 controls PASS; sweep row S7814_INCLUDE. [tools/s7814_include_census.py tools/s7814_vmov_vsar/]
   - s7815 elementwise VU class CLOSED (ours correct): all 25 live ops + 6 dead, every e, both flavours, vs cxd4 AND CEN64. Stock
     cxd4 has 5 VU defects (VCR merge() fed sn=-1; VCH -(-32768) kept 0x7FFF; VABS ACCL; VMRG keeps VCO; VMADN/VMADL clamp misses
     ACCM==0x7FFF/0x8000); CEN64 == ours on those ops. Patched cxd4 == ours bit-exactly on all ops AND on whole real tasks: the s7752
     "31-33 sub-LSB residual commands" were cxd4's VCH+VCR (ablation), so our LLE is byte-exact vs an independent RSP. CAVEAT: every
     angrylion "retail oracle" run used the STOCK cxd4 dylib (<=1 LSB on those tris). Sweep row S7815_VU. **s7816: the 5 oracle
     scripts now load the VU-fixed cxd4 by default** (tools/oracle/rsp_plugin.sh; `RS64_ORACLE_RSP=stock` = old; build
     tools/oracle/build_cxd4_patched.sh -> ../rs64-oracle-cxd4p). Same-session 3-arm oracle run (stock / rebuilt-unpatched /
     patched, title->hangar, 66 frames): all 9 static frames byte-identical in all 3 arms; animated frames differ as much
     between stock and its own rebuild as vs patched (wall-clock press/dump timing): the oracle cannot resolve a sub-LSB plugin
     effect cross-run. Earlier oracle-based fidelity verdicts stand (H-negligible on static frames; flight effect <=1 LSB, s7815).
     **s7817: the oracle is now deterministic with `--det` (= `--clock vi --det-core`).** Two causes of run-to-run divergence:
     wall-clock presses/dumps (fixed by `--clock vi`: presses + dumps on exact emulated VIs) AND mupen64plus-core
     RandomizeInterrupt=True (PI/SI interrupt jitter from rand() seeded by srand(time(NULL)); `--det-core` turns it off for the run
     and restores the user cfg). VI clock alone: dumps on identical VIs, still diverge from VI ~2115 (p1/p2). Angrylion
     Parallel=False and keyboard-only input each refuted (still diverge; pad words change on identical VIs). With `--det-core`:
     two patched runs 82/82 2 MB dumps byte-identical; stock vs patched cxd4 = 0 visible px on all 66 comparable title->hangar frames,
     111 halfwords differ off-screen (one word/dump ~0x7887xx). So the s7815 VU fix has NO visible effect on this route (two-line:
     s7815 ucode compare + s7817 deterministic A/B). Use `XARGS=--det-core CLOCK=vi` in tools/s7816_oracle_rsp_ab.sh; compare with
     tools/s7817_oracle_det.py. **s7818: `--det` is the DEFAULT** in s7816_oracle_rsp_ab.sh and g3f_retail_pan.sh (rsp_plugin.sh
     ODET; ORACLE_DET=0 = old); controls 82/82 vs d1 and g3f g1==g2. **s7819: g3_{menu,showroom,ai_gap}_pair.sh now --det too**: tools/g3_port_capture.sh SAVE_FROM runs from a private game dir OUTDIR/game (symlinked binary+ROM, own saves/; the save path is cwd-relative, main.cpp register_config_path) and never touches build/saves (sha identical before/after 4 runs; lvl1.eep run shows AAA -> AMBUSH AT MOS EISLEY, owner control ASS -> BEGGAR'S CANYON); two g3_menu_pair runs: retail 31/31 dumps raw-identical, same VIs, 4/4 sampled dumps distinct.
     **s7820 det menu pair, title -> SELECT GAME: no port render defect (H-port refuted).** Menu geometry for g3_oracle_match.py:
     `--w 512 --h 448 --bases 790000 --win 66,1024 --winx 86,1194 --dec shift` (the s6741 h336 crop read d~20 on matched content;
     fitted d 3.8). Title/attract d 3.8-7.5 in all 4 pairs, port r1/r2 equal; painted-block control 2 -> 25 tiles>40. SELECT GAME
     d 18-27 = the backdrop photo only (rand%7 at the press, s6780): retail det picks the same photo every run, port picks a
     different one per run (wall clock, and with the new VI clock too: boot-to-title VI 757 vs 762); a title-onset seed poke makes
     port r1 == r2 to 2 dp but != retail, because retail's title rand loop starts 196 VIs after its width switch (slower image
     loads) and its idx-init runs after the switch, while the port's runs before it (rand traces: 286 vs 479 title calls). RDP
     stream (decisive): texrect layout exact 102/103 frames, geometry-without-PRIM exact 68/103, residual = spinning-emblem tri
     PRIM/count phase (ctl median 586). New: `ROGUESQ_AUTOPILOT_CLOCK=vi` (port presses on VI count), g3_menu_pair `PCLOCK=vi
     AP0= ORX=`, `ROGUESQ_DEBUG_WRITE=...:ARM_S:in` (fire inside a phase; default stays switch-only, legacy 1024:5 control unchanged).
     The off-screen word is NAMED (H-dead): an F5-emitted RDP tri edge (X,DxDy) on an edge spanning 0-0.75 scanlines (58/58 groups),
     RSP-written, 0 CPU loads/stores across its lifetime (VI-windowed watch, same-run control 99k CPU reads). New oracle
     `--hit-vi-window A:B`; oracle self-read trap fixed (fb-dump reads used to fire read watches, see tools/oracle/README.md).
     **s7821 det pair through SELECT GAME (panel) and the hangar: no port render defect.** lvl1.eep route = title -> SELECT GAME
     -> fade -> hangar (no separate SELECT LEVEL). SELECT GAME with the save panel: texrect geometry exact 120/120 (ctl 0/120);
     the fade 97/97. Retail draws the panel ~180 frames after entry: press out later than ~6 s or retail never draws it (s7821 run b).
     Hangar: whole frames never pair (continuous time-based animation sampled at ~16 fps emulated-retail vs ~30 fps port: bob period
     44.7 vs 81.6 frames, both ~2.8 s; retail VI flips ~16/s); element test non-breathing 0.944 both ways, ctl 0.000, 0.25 px plant
     0.000; all misses are scale-animated strips. Tool: `python3 tools/s7821_rdp_screen_segments.py R.bin P.bin [--elements 512:5
     --ctl-phase 4]`; capture scratch/s7821/c/*.bin.zst. Don't use RS64_RDP_BIN_WIDTH when a route crosses widths.
     **s7822 det pair through the 512-wide screen's sub-screens: no port render defect.** The 512 screen is SELECT LEVEL (port window
     w_0050.04.png: "SELECT LEVEL", Mos Eisley description), not AVAILABLE CRAFT as s7821 wrote. Presses C-up / C-up / right
     (scratch/s7822/*.bin.zst). Both arms walk the same states (texrect bands 140 -> 240 -> 140, tri bands 1130/1098/1118 retail vs
     1128/1097/1119 port per window). New `--windows r0:r1,p0:p1,c0:c1` in tools/s7821_rdp_screen_segments.py (explicit windows +
     element test excluding 54-66 x 16.5-22 px scale strips). Description screen: non-strip R-in-P 1.000 (18000), P-in-R 0.9988,
     ctl (other sub-screen) 0.000, +0.25 px plant 0.000. Base and post-right windows: non-strip 0.987 / 0.985, plant 0.000, every
     miss a 66.5-66.75 px scale strip (ctl not discriminating there: same static set). Whole frames still never pair (strip breathing).
     [tools/s7815_vu_gate.py tools/s7815_vu_ops/{run.sh,harness.cpp,patch_cxd4.sh,cen64/}]
13. **Next agent work (owner items above wait on the owner):** G3 post-G6c fidelity. Owner recipe (FPS60 dd4 16:9) + STANDINS=1 on the
   post-s7790 binary == angrylion on TWO levels: L1 s7793 (refit 5.27/0.015, 0 >0.05) and L12 s7794 (131 stand-ins; refit 3.88/0.013,
   0 >0.05, centre 0.008; at or below pre-G6c s7159 on every statistic); same-run painted control PASS both. L12 worst swaps are
   CULL_SPIKE removing a retail wedge (intended). Sheets docs/owner_sheet_s7793_L1_standins_fidelity.png, docs/owner_sheet_s7794_L12_standins_fidelity.png.
   L1 21:9 s7795 (47 stand-ins; refit 1,12,469,217 frac 0.009/0.010/0.011, 0 >0.05, centre 0.005 side 0.013 = s7165 floor; control
   PASS, shift-2 359 >0.05). Sheet docs/owner_sheet_s7795_L1_219_standins_fidelity.png. Three-arm check CLOSED.
   L4 21:9 s7796 (155 stand-ins): flight refit 1,11,469,216 frac 0.006/0.007/0.010, 0 >0.05; letterboxed water cutscene (s7166 trigger
   TRIG_LB=1) 247 lb swaps unpainted max 0, 0 >0.05; same-run SKYFILL_BOT=tog control 20 hole swaps (max 20542 px). Sheets
   docs/owner_sheet_s7796_L4_219_{standins_fidelity,cutscene_standins}.png. s7166 fix holds post-G6c.
   L10 16:9 s7797 (280 stand-ins, the most): frac 0.006/0.008/0.013 (s7158 pre-G6c 0.007/0.011/0.013), 0 >0.05, centre/side 0.003/0.017,
   control PASS, shift-2 329 >0.05; sheet docs/owner_sheet_s7797_L10_standins_fidelity.png. Post-G6c fidelity thread CLOSED (L1/L10/L12 16:9,
   L1/L4 21:9). dd2 (owner's other dd) s7798 L4 16:9 155 stand-ins: frac 0.010/0.013/0.017 (refit 0.011/0.012/0.013), 0 >0.05, control PASS,
   shift-2 44; sheet docs/owner_sheet_s7798_L4_dd2_standins_fidelity.png -> H-equal at dd2. Frame diff cannot see a handoff gap (angrylion
   replays our stream). s7799 handoff at dd2 (scratch/s7672/run.zsh <out> <lvl> odd 2): L4 held 23 / L1 9 handoffs 0 blinks, same-run
   control 16/16, 7/7 blink -> H-clean at dd2; L1 held si_far 179 all with re_far >= si_far (beyond far*dd, real out of range too), scorer
   now fails only on far_viol (si_far > re_far). s7800 dd2: L12 held 5 handoffs 0 blinks (control 1/3 blink, 110 frames); L10 held 0
   counted handoffs (autopilot flew past only 3 spawning objects; the 1 held spawned row has its 462-frame gap fully covered by view
   culls of both stand-in and real object = off-screen, not a blink). Scorer now reports uncounted/uncounted_vis (control fires on L12
   odd=0). dd2 handoff CLOSED H-clean on L4/L1/L12, L10 unmeasurable under the autopilot. **G6c STANDINS=1 300 s holds: 19/19 levels
   pass (s7797-s7802 re-holds on the post-s7790 binary; last five L3/6/7/8/9 s7802, spawns 34-112, 0 crash, vi_stalls30s 0).** G6c now
   waits only on the owner's look (OWNER-REVIEW-QUEUE item 3). s7801: whole gate sweep on the post-s7790 tree, uncached (hit=0): 234 gates, 229 GREEN,
   3 REPORT, 2 NEEDS-INPUT, 0 RED/HOLLOW/NEEDS-ARGS; `s7719_regen_gate.py --strict` H-mirrored, 53 files 0 differ, HIT 326 (= s7791).
   s7726_zombie_census.py now reads *.zst and is a retained gate (s7727 hangar capture, control 364, mutant control rc 3).
   **s7802: the s7753 RDP-output and s7756 hangar H-state gates were BLIND s7780-s7801** (NEEDS-INPUT): their 21 snaps / 6 pairs were
   zstd-compressed 2026-11-21 14:24 and the gates tested only the raw .bin. Fixed via tools/rs64_zopen.py resolve()/materialize();
   now 21/21 + 6/6 GREEN with controls PASS, pinned in the sweep (S7802_RETAINED; partial loss = RED, total absence = NEEDS-INPUT,
   planted in tools/s7802_retained_input_controls.py 6/6). Same class: s7769 control ring, s7454/s7462 real-log cases (silently skipped).
   Rule: any gate reading a retained scratch input must go through rs64_zopen (resolve/zopen/materialize).

## Evidence index

- Maintenance archives (whole CURRENT-TRUTH verbatim): PROJECT-OVERVIEW s7417, s7370, s7307, s7187, s6994; trims s7262,
  s7134, s7121, s7104, s6982, s6962; s6900, s6847, s6759; [Maintenance s6667 retained evidence](PROJECT-OVERVIEW.md#maintenance-s6667-retained-evidence).
- Objective contracts [G1-OBJECTIVE-RESPONSE](G1-OBJECTIVE-RESPONSE.md); images [G1-FRAMEBUFFER-COVERAGE](G1-FRAMEBUFFER-COVERAGE.md).
- Owner commands docs/OWNER-OPT-INS.md; owner sheets docs/owner_sheet_s7*.png/jpg.
- Queued-soak verdicts `scratch/agent/SOAK-RESULTS.md`; loop.sh edits take effect before the next soak phase
  (s7235 re-exec); idle-gated recipes polled up to SOAK_IDLE_WAIT=1800 s (s7254).
- Recent chronology: PORTING-STATE sessions 7617-7747; search bounded windows only.
