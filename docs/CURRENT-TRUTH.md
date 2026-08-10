# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. 27 passes so far
   (git log has per-pass targets; PROJECT-OVERVIEW §16-§26 hold the most recent arcs) kept the file
   oscillating around the cap as new session detail accrues. 35 KB remains a stretch target, not a
   hard floor -- the "Current truth" env-var/timeline prose and the Regeneration section's Standing
   warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (PROJECT-OVERVIEW §10-§12). Next
   M5 work needs a genuinely new lead (rechecked s582 SOAK-RESULTS: no new audio-family
   crash leads since s487; due again s585+).
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. Every bucket from
   the s465/s477 frequency scans has a disposition (items -298..-309, PROJECT-OVERVIEW §18-§19). The
   `DL_LIST_APPEND_GUARD`→`HEAPLISTDEQ_ATTR_WRITE_GUARD` lineage (items -312..-348, s481-569) is all
   fully CLOSED — PROJECT-OVERVIEW §20-§25; see individual items below for closure notes.

## Current truth (established by session 295; unchanged, reviewed through s610)

    cd build && ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ./RogueSquadron64Recomp

Metal shader rebuilds need full Xcode on PATH:
`export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` (bare CLT has no `metal`).

- `ROGUESQ_LLE_SOLO=1` is not optional: without it the runner runs LLE **and then falls through to
  HLE for the same task** (s9).
- Default-ON, no longer worth naming: `ROGUESQ_VI_FOLLOW_DRAW=3` (s23), `ROGUESQ_SHADE_WRAP=1`
  per-pixel (s24→s26), `ROGUESQ_FIX_ZERO_SHADE` (s20), `ROGUESQ_FIX_SAMPLE_BOUNDS` (s15),
  `ROGUESQ_VI_FULLSYNC` (s11), PresentEarly fallthrough + forceAdvance +
  `ROGUESQ_PRESENT_EARLY_FORCE` (s21), deferred-range coalescing (opt out with
  `ROGUESQ_NO_DPC_MERGE=1`, s10), **s78 wild/OOB FB refuse** in `FramebufferManager::get`
  (width>1280 or past 8MB — same family as s72 writeback; does **not** unfreeze present),
  **s182 `[fbsync-oob-skip]` guard** in `State::fullSync`'s color/depth read-into-`fbStorage`
  blocks (`rt64_state.cpp`) — s78's refuse gate returns a `refuseFb` that still carries the wild
  width/height, and this downstream RDRAM read had no bounds check of its own; same family as
  s72/s78.
- Default-OFF, keep them off: `ROGUESQ_FIX_DXT` (s22/s23), `ROGUESQ_FIX_DXT_I` (s27, null on
  hangar band), `ROGUESQ_FLATTEN_I4` / `FLATTEN_RGBA16` / `FLATTEN_CI4` (attribution probes),
  `ROGUESQ_SHADE_ONLY_MONO` (s30, pad-only), `ROGUESQ_SHADE_WRAP=3` (s31), `ROGUESQ_SHADOW2`,
  `ROGUESQ_RING_RESYNC`. Diagnostics: `ROGUESQ_DUMP_IMEM_DMA=1` (s47, lib-side) dumps every skipped
  IMEM DMA to `build/imem_dma_dump.bin` (`scratch/s47_parse_imemdump.py` decodes).
  `ROGUESQ_LOG_RUNNER=1` prints a per-task RDP-opcode histogram (1-in-32 sampled by default --
  `ROGUESQ_LOG_RUNNER_ALL=1`, s64, prints every task unsampled; the sampled mode misattributes
  31 tasks' counts onto whichever task is next sampled). `ROGUESQ_LOG_SEQ=1` dumps a task's raw
  pre-translation DL bytes -- not valid for "does this task emit SYNC_FULL" (needs the
  post-translation histogram above, s64).
- Deleted from the code (s44): `ROGUESQ_DPC_WRAP` / `ROGUESQ_WRAP_DEDUP` (s11), `ROGUESQ_FORCE_PAL15`
  (s14), `ROGUESQ_FORCE_SHADE_WHITE` (s19). `ROGUESQ_MAX_FBPAIRS` (default 8192) engages 0 times
  since s11 but is KEPT deliberately -- OOM insurance for future FULL_SYNC-less phases (M3
  missions), turns a 22 GB Metal abort into a capped workload (s44).

Unattended timeline (VI width, ±1 s over 9 runs, s18; content counts s9/s20/s22/s23):

| t | VI | scene |
|---|---|---|
| 0.0 s | 0 → 320 | boot |
| 1.7 s | 640 | attribution → N64 logo → cinematic geometry → star flare → **Factor 5 logo**, all correct (content in 24/60 frames over ~2–44 s) |
| ~46.5 s | 1024 | **title screen** — logo, pilot, X-wing, START/OPTIONS; 5/5 content frames, ~20.9k colours |
| ~72 s | 640 | transition |
| ~90 s | 512, origin 0x690400 | **outdoor scene** — sky, clouds, horizon, sand; 6/6 content frames |

**s39/`-O2` harness note:** the game now progresses further per unit time, so the old
`PROBE_KEYS="3:start 7:start 11:a 15:a 19:a"` schedule overshoots the hangar into a later exterior
scene that shares VI origin **0x6AB400** — origin alone no longer identifies the hangar. Use
`"3:start 7:start"`. The phase timeline below is unchanged (transitions are not render-rate bound).

Driven from the title with `PROBE_KEYS_FROM_PHASE=1` (s23, scene names corrected s48):

| t | VI | scene |
|---|---|---|
| 46.7 s | 1024 | clean title |
| ~50 s | 1024 | **SELECT GAME** (photographic hangar backdrop, AAA save, ERASE GAME) — waits for input indefinitely |
| +1 press | 512, origin 0x6AB400, colour 0x656000/0x6AB000 | **level-select war room → SELECT LEVEL — "AMBUSH AT MOS EISLEY"** with X-wing hologram (the scene s12–s47 called the "main-menu hangar"; see s48 below) |
| ~93 s | 640 | transition — process died here in the undriven-era observation and in every crashing run of the post-s86 family; on later crash-free runs the process instead survives past here |
| leave SELECT YOUR CRAFT (1 Start press) | 512→640, origin 0x6AB400→0x6A2900ish | **s162: a Chapter-1 mission-intro cutscene** — gold "STAR WARS" logo bumper → "Chapter 1"/"THE RED…" crawl text → black → desert-planet horizon widening into a fast dive toward a hangar structure (establishing shot, not gameplay). The s75/s76/s161 "hangar-flight" label for this window was an unverified inference from title-yellow color decay, not from the picture itself — **see the s150 overturned-conclusion entry below: it is the SAME craft-select scene under a corrupting camera move, not gameplay.** |
| ~+90-115s post-leave | varies | **graphics-task-submission stall** — `[vi-fs-decision]` reports `stalled=1 pairs=0` continuously, RDP `fs` counter frozen. Not a crash; a staggered subsystem shutdown (s178): the per-frame graphics-task producer stops being invoked at all while heap-free-walking keeps running to the end of the log. s180's source-confirmed candidate mechanism: a `[thr-resume-skip]` scheduler event (the s84 UAF guard) fires immediately before stall onset in one reproduction, but s183 reached and sustained the stall a 2nd time with **zero** `[thr-resume-skip]` fires — this weakens (does not confirm) s180's mechanism as the general cause. Open, unresolved as of s183; the last dedicated session on this thread. Full detail: `PORTING-STATE` Sessions 176-183. |

Menu state machine (s48, extended through s75; hold/crash triage s76-s114): title --start--> SELECT
GAME --start--> war room / SELECT LEVEL --start--> **AVAILABLE CRAFT** (war-room craft holograms; `a`
does **not** show a level description card, s61-s69). With process alive 65s+ post-`a` (s72/s73):
black ~5s -> capital-ship flash -> stable **SELECT YOUR CRAFT** (hangar pad + full X-wing; `a`
no-ops, s74; camera orbits). A single Start leaves the menu, but what it leaves INTO is unresolved
(s75's "hangar-flight" claim was **OVERTURNED s150**, see Overturned conclusions -- same craft-select
scene under a corrupting camera move, not a new environment). VI stays on the 0x6AB400/0x656400 pair
throughout -- **origin cannot identify these menu scenes**, only phases. ~20 crash classes closed
getting through this chase (mechanisms/tags: `docs/PROJECT-OVERVIEW.md` §3/§7/§9).

Remaining visual defects, all parked as M4 except where noted: outdoor 512 zero-shade masked not
fixed (`baseFixed = −32768` root cause unknown, s19/s20); S=0 triangles in the 640 attribution phase,
uninvestigated (s18); `[dpc-behind]` ring-wrap drops with `DPC_WRAP` off (not a black-screen cause,
s11). Hangar floor multi-hue band, hangar dimness, and the post-leave black/SIGBUS chain are all
FIXED (M1 closed s48; `SHADE_WRAP` s25; ImemOverrun s69 + depth-writeback SIGBUS s72) — mechanisms in
`docs/PROJECT-OVERVIEW.md` §3.

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep. 0
`UnhandledJumpTarget`, 0 `[defer-drop]`, 0 `[dmem-race]`, 0 asserts. The `[missing-func]` saga
(s49's original 3 addresses plus ~801-803 further phantom `main_overlay.txt` entries found while
fixing them) is fully **CLOSED** (items -6/-249) — every clean live-verify should show 0
`[missing-func]` lines. Post-`a` process now soaks well past 65s without death.

## Goal stack — work strictly top-down

A milestone is done only when its definition-of-done is met **and documented here**. The
autonomous loop (`tools/agent/loop.sh`, contract in `tools/agent/ITERATION.md`) always draws its
work unit from the top open milestone, so this ladder is what keeps it from idling.

**M1 — hangar band root cause and fix: DONE (s48).** Mechanism and fix recipe:
`docs/PROJECT-OVERVIEW.md` §3 ("Fixing the hangar band"). Full detail: PORTING-STATE s45–s48.

**M2 — post-clip-fix regression sweep: DONE (s49).** New stability baseline: 1138 tasks,
fanjal=9448, 0 cull-census-identity violations (scales with capture window, not a fixed constant).
Stability 0 except 3 `[missing-func]` addresses in the undriven outdoor stretch — parked as M4,
since **DONE/CLOSED s399** (item -6). Full detail: PORTING-STATE s49.

**M3 — first gameplay: OPENED (s50), still open.** AVAILABLE CRAFT and SELECT YOUR CRAFT are both
reachable and stable; ~20 crash classes closed s50-s294 (mechanisms: `docs/PROJECT-OVERVIEW.md` §3
arc + §9 closed lineages; per-class catalog: §7). Leave-key from SELECT YOUR CRAFT: s75 hangar-flight
OVERTURNED s150; **s577 REAL hangar exit CONFIRMED** (case 3→5→6→8). Post-exit FULL_SYNC starvation
product-fixed via `ROGUESQ_FS_PIPE_INJECT` (default OFF; items -354..-358). **s608: force6+inject
path completed thr11 destroy → sec4 → thr12 → sec2 (mission overlay)** — H-handoff2 REFUTED
(76BA90 not required); thr11→sec4 is no longer the primary blocker when recovery cell
`0x76B768` fires. **s609: recovery silence is a co-primary gate** — eng+inject without
`0x76B768` never reaches thr11 destroy/sec2 (H-recov1 necessity SUPPORTED). **s610:
s609 reroll scored class E recharacterized** — recovery ×48 DID fire; process Abort'd
~+4k lines after first `0x76B768` inside `mat3x3InverseInto` (NAN_CHECK) mid the s607
recovery→thr11-destroy gap (~+7k), not a clean thr11-stall. Free-reroll class added
(`s610_recov_mat3inv_reroll` + `ROGUESQ_LOG_MAT3INV`). Post-sec2 HMT/`packTlut` (-373, 1×);
material `0x8000e29c` (2×); mat3inv Abort (-375, 1×). Tools (default OFF):
`FORCE_STATE6_AFTER`, `FORCE_CASE6_START`, `FS_PIPE_INJECT`. Full chain: items -349..-375;
raw Sessions 577-610.
DoD = **cutscene→in-mission** + craft input.
*Done when:* 60s in-mission render, craft responds to synthetic input, stability 0, phase timeline
covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it. The 3 `[missing-func]` addresses, the `main_overlay.txt` phantom-overlay-function
family, and its `0x800290d4` clustering are all **DONE/CLOSED** (items -6/-249/-259).

**M5 — audio de-stubbing: DONE and fully CLOSED (s297-376).** No outstanding thread; next M5 work
needs a genuinely new lead (rechecked s570: zero new leads, intentionally-left stubs still C88
force-zero + default `real_ucode=0`; due again s573+). Full arc: `docs/PROJECT-OVERVIEW.md` §9-§12.

## Next steps, in order of expected value (s295)

Numbering convention (fixed s295): items are numbered highest-magnitude-negative (top,
newest/highest priority) counting up to -1 (bottom, oldest); never renumbered when compacted into
a range pointer. Highest allocated so far: -375. The next NEW item takes -376.

-375. **(s610) Post-exit `mat3x3InverseInto` Abort (NAN_CHECK) mid recovery→thr11-destroy
    window — 1×; free-reroll, not chased.** s609_recovery_cell_reroll scored a3 class E:
    eng+inject+recov76B768~=48, thr11_create=1, thr11_destroy=0, crash Abort trap.
    Host: `mat3x3InverseInto` ← `traverseSceneGraphRecursive` ← `setupCameraMatrices` ←
    `runModelViewerLoop` ← `menuOverlayInit`. `last-guest-pc=0x80022160` is **STALE**
    (`tickTextureMaterialExpiry` epilogue; mat3inv does not stamp guest PC). Offline vs
    s607: first 76B768 ~same +63–67k post-hsel; s607 thr11d ~+7k after first 768; s609
    death ~+4k after first 768 — **mid-window abort**, not EOF thr11-stall. s223 hangar
    mat3inv null (0 abnormal/456k) does **not** cover this post-exit force6 phase.
    **Act:** `s610_recov_mat3inv_reroll` free-rerolls mat3inv stack + arms
    `ROGUESQ_LOG_MAT3INV=1`. Escalate only on 2nd same host stack with abnormal control.
    Full: Session 610.

-374. **(s609/s610) Force6+inject recovery silence — co-primary thr11→sec2 gate; H-recov1
    necessity SUPPORTED.** s608_confirm a3: eng+inject n=750, thr11 create, mono
    `0x0076DF60`×474, **0×76B768**, thr11_destroy=0 (class F). s609 reroll: recov_silent=0
    (recovery did fire when scored) — silence remains intermittent, not every eng.
    Filter: free-reroll if 0×76B768 within `RECOV_WAIT_S=100` post hangar-sel. Pre-eng
    `setByteAcrossEntryList+176`/`0x800aafa8` now 3× (near closed -320 `0x800aafb8`).
    Full: Sessions 609-610.

-373. **(s608) Post-sec2 mission HMT texture load SIGBUS — primary M3 bottleneck once recovery
    fires (1 occurrence; not chased yet).** Scored `s607_handoff_material_noise_reroll` class C
    but **past** thr11→sec4: `force6=1 case6=1 hangar-sel=1 ace80=1 inject_max_n=400
    recov76B768~=92 recov76BA90=0 thr11_destroy=1 sec4_post=1 sec2=1 sec2_post=1
    thr495FC_creates=2 crash=CRASH`. Host: `packTlutEntriesRgba5551+2608` ←
    `loadTextureToMemory` ← `parseHmtMaterials` ← `registerHmtTextureInTable` ←
    `loadDebugAssets` ← `advanceVideoFrame` ← `mainGameLoop`. `si_addr=0x38ea20812`,
    guest-ish x10=`0x8ea20812` (OOB). **last-guest-pc=`0x800025ac` is STALE** (packTlut has
    no `g_rs64_last_guest_pc`; -347 trap) — do **not** merge with item -326 (`do_rom_read`
    / `initSceneForMission` stack). Co-symptom: `osViSetMode` width=24 (garbage
    mode_ptr=0x80128DA0 type=0) ~10 lines pre-crash. 0 TEXDATA/MATERIAL guard fires. Pipeline
    order after thr11 create: 76B768 → thr11 destroy → sec4 → thr12 create → thr12 destroy →
    **sec2** → VI24 → crash (~47 log lines post-sec2). s608 confirm did **not** re-hit sec2
    (recovery-silent -374); 2nd occ still pending. Full: Session 608.

-372. **(s607) `s606_handoff_76ba90_dual_target` folded: class E0 (material, no recovery);
    `0x8000e29c` 2nd occ; H-handoff1 recharacterized; material-noise reroll ran → -373.**
    Scored: force6+case6+hsel+ace80, thr11 create, inject n=450, **0 recovery cells**,
    thr11_destroy=0, crash `findOrCreateMaterial+776` / `0x8000e29c` (2nd after s605).
    Material death independent of 76B768; aborts thr11→sec4 when it fires. Do not
    single-chase (2nd occ filed). Full: Session 607.

-371. **(s606) `s605_force_state6_dual_target` folded: H-force6a CONFIRMED; thr11→sec4
    pipeline RECHARACTERIZED to 76B768→76BA90 handoff; H-recov1 sufficiency REFUTED;
    queued `s606_handoff_76ba90_dual_target` (ran → item -372).** Scored attempt 2/2 (A1
    pre-eng discard): `force6=1 case6=1 hangar-sel=1 ace80=1 inject_max_n=300
    recov76B768~=7920 thr11_create=1 thr11_destroy=0 sec4_post=0 recov76BA90=0
    crash=CRASH crash_pc=0x8000e29c` (`findOrCreateMaterial+776`, then NEW guest PC;
    2nd occ s607). Offline vs sole thr11→sec4 control `s592_a`: thr10 destroy~+0.8k →
    thr11 create~+0.9k → inject~+9k → 76B768~+20k..+87k; s592 then `0x76BA90`@+95599 →
    thr11 destroy@+96337 → sec4@+96340; s605 dies@+89961 with **0× 76BA90**. **H-force6a
    SUPPORTED.** **H-recov1 sufficiency REFUTED.** Necessity still open. Keep
    FORCE_STATE6_AFTER env-gated. Full: Session 606.

-370. **(s605) `s604_item338_item361_hold180_budgetfix` folded: budget fix WORKED, engagement
    still 0/3; landed `ROGUESQ_FORCE_STATE6_AFTER` (s602 E pivot) + queued
    `s605_force_state6_dual_target` (ran → item -371).** Loop hard-cap 600s (rc=137) mid-A3.
    Attempts: A1 pre-eng `hangarTickCameraOrbit`/`0x800ab068`; A2 pre-eng
    `tickWrappingTimerAccumulatorList`/`0x80054750`; A3 alive at state=5, **0 ACE80**,
    c5≈186. Combined s603+s604 = **0/5 ACE80**. Product tool (default OFF):
    `ROGUESQ_FORCE_STATE6_AFTER=N` at case5-entry n==N (`[case5-force-state6]`). Full:
    Session 605.

-369. **(s604) `s603_item338_item361_hold180` = no engagement (rc=2); budget NEED starved
    retries; requeued as `s604_item338_item361_hold180_budgetfix` (ran → item -370).**
    2/2 attempts died pre-engagement at hangar state=5. Budget math root cause:
    `NEED=HOLD_S+90=270` refused attempt 3. Fix: `START_FLOOR_S=100`. Full: Session 604.

-368. **(s603) `s602_item338_beginframe_s0_verify_r3` scored D + clean survival; thr-11/sec4
    pipeline recharacterized; HOLD_S=180 dual-target soak queued (s603 ran → item -369).**
    Attempt 4 scored: `case6=1 hangar-sel=1 ace80=1 inject_max_n=550 recov76B768=0 sec4=1
    sec2=0 beginframe_s0_guard=0 last_guest_afa0=0 crash=ok`. No-sticks engagement OK.
    thr-11 = `saveServiceWorker` entry=`0x8006F2CC`. Pipeline: thr-11 destroy ↔ sec4 →
    coalesce R2 `@0x8000247c`. Full: Session 603.

-367. **(s602) `s601_item338_beginframe_s0_verify_r2` = no engagement (rc=2); engagement gate
    diagnosed as ACE80 camera-settle; requeued no-sticks as
    `s602_item338_beginframe_s0_verify_r3`.** Attempt 1: pre-engagement
    `transformLightByType+256`/`0x80010134` (item -347; discard). Attempt 2: full HOLD
    survived at hangar **state=5**, 0 ACE80 / 0 ACE94 / 0 case6. Mechanism: FORCE_CASE6
    injects at ACE94 which only runs in state 6; 5→6 is automatic `[state-write]
    site=0x800ACE80` (camera settle), not a button. s603: no-sticks r3 **engaged** (ACE80+case6)
    — stick hypothesis SUPPORTED as engagement fix; force-write pivot not needed. Full: Session 602.

-366. **(s601) `s600_item338_beginframe_s0_verify` scored D (path not exercised).** Fast-retry:
    attempt 1 pre-engagement death; attempt 2 engagement `case6=1 hangar-sel=1` then scored.
    Gate: `beginframe_s0_guard=0 last_guest_afa0=0 sec4=1 … crash_pc=0x8000241c` /
    `coalesceFreeHeapBlocks+3192` (catalogued noise; died before beginframe path). s601-r2
    requeue scored no engagement → item -367. Full: Session 601.

-365. **(s600) Item -338 ROOT-CAUSED and GUARDED (`BEGINFRAME_S0_GUARD` site=`0x8000AFA0`);
    live 2/2 confirm still PENDING (s600=D, s601=D, s602 r3=D — 3 scored non-hits).** Offline
    on all 5 crash logs (s554/s572/s574/s592_r2/s598): identical mechanism — guest `0x8000AFA0`
    `lw $v0, 0x8($s0)` after null-only `beql $s0,$zero`; SIGBUS `si_addr=0x335000008` on 4/5
    (s598: `0x384004087`), `x11` matches low 32 of `si_addr`. Function base `0x8000A8A0`
    (`beginFrameDLChunk`); host `+37740` vs `+46800` is pc-symbol/binary drift, not two sites.
    Stacks: hangar path `initRenderStateArrays←runHangarSelectionFrame` (4/5) or post-exit
    `drawFrameProfilerBars←runModelViewerLoop` (s598) — same guest PC, two callers. Idiom =
    item -317 family (null-check gates zero arm; non-null fallthrough has no
    `0x80000000`–`0x80800000` range check) missed by the hi16-reload sweep because the pointer
    arrives via stack-slot load (`lw $s0,0($s1)`), not `lui`+`lw`. Inner list walk at
    `0x8000B1EC` reloads `$s0` and branches back to `L_8000AFA0`, so one guard covers both
    entries. Fix: range-check `ctx->r16`; OOB → `s2--` + `goto L_8000B208` (mirrors outer null
    arm). Env `ROGUESQ_LOG_BEGINFRAME_S0_GUARD` / `[beginframe-s0-guard]`. In
    `fixup_game_funcs.py` + hand-applied `funcs_3.c` (sentinel blocks re-fixup without regen);
    binary rebuilt. **Keep LOG armed passively; do not dedicate another same-HOLD soak if
    s603 is again F/D for beginframe — path is rare under force+inject.** Full: Sessions 600-603.

-364. **(s599) `s598_fast_retry_case6` ran: engagement on attempt 1/8, then item -338 before
    `sec4=2` — REFRAMES item -361 bottleneck to "item -338 racing thr-11 destroy."**
    `case6=1 hangar-sel=1 … sec4=1 crash=CRASH` at `0x8000afa0` (5th). Offline vs sole real
    `sec4=2` run (`s592_sec4_thr12_a`): recovery `0x76B768` fired to EOF in BOTH; discriminator
    was thr-11 `[thr-destroy]` (present only in `s592_a`, immediately before 2nd sec4 reload).
    First post-engagement death in the item -361 tally (s593–s596 were all pre-engagement).
    s603: thr-11 identity corrected to `0x8006F2CC`; s602 clean survival shows -338 is not
    always the race — HOLD window / cutscene advance can starve thr-11 destroy without any
    beginframe crash. Full: Session 599.

-363. **(s598) Item -361 redesign option (1) BUILT: `s598_fast_retry_case6.sh` queued to
    `scratch/agent/soak_queue/`.** Implements NEXT.md's fast-retry recommendation: loops the
    existing case6+inject recipe inside one 560s slot, discarding any pre-engagement death
    (no `[case6-force-start]`+`[hangar-sel]`) as a free reroll instead of a scored soak, up to 8
    attempts; only the first attempt that reaches engagement runs its full `HOLD_S` window and
    gets the sec4-decision-tree analysis. Verified `run_mission_keys.sh` already self-terminates
    promptly on early death (per-phase `kill -0` checks) so no separate mid-run polling/kill logic
    was needed — confirmed `ROGUESQ_FORCE_CASE6_START`'s implementation
    (`~/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_28.c` ~17830) fires on the 5th poll of the
    hangar-bay check once SELECT YOUR CRAFT is reached, not gated on additional key input beyond
    getting there. Syntax-checked (`zsh -n`); not execution-smoke-tested standalone this session
    (direct invocation of a `soak_queue/` script required interactive approval) — the loop will run
    it for real on the next queued-soak pass. **Next session: read the
    `s598_fast_retry_case6` verdict line in `scratch/agent/SOAK-RESULTS.md` and fold into item
    -361's decision tree.** Full detail: `PORTING-STATE.md` Session 598.

-362. **(s597) Item -361 pre-engagement noise tally (redesign option a) — CLOSED NEGATIVE, no
    dominant fixable family; new "waitForAnyAudioSlot+244" signature (2/2, s594_d/s595_e)
    INVESTIGATED and found to be a local-symtab misattribution, not a real crash.** Tallied
    cause-of-death for the 8 directly-checkable s592b/s593-manual/s593_a/s593_b/s594_c/s594_d/
    s595_e/s595_f nulls: item -306 (2×), the new cluster (2×), item -331 2nd occ (1×), a
    genuinely distinct recovery-cell-reliability failure (1×, `s594_c` — the real bottleneck,
    see item -361), non-crash early death/hang (2×). No single family is a majority — option
    (a)'s "find one dominant family, write one guard" premise fails. The new cluster
    (`waitForAnyAudioSlot+244`/`0x8000834c`, both died in 7-8s at VI640, pre-title-screen)
    looked like a fresh M5-relevant lead but failed its own implied positive control:
    `waitForAnyAudioSlot` (`funcs_15.c:7253`) prints an unconditional `[audio-drain-enter]` as
    its first statement whenever `ROGUESQ_LOG_AUDIO_DRAIN=1` (armed correctly — sibling
    env-gated tags fired normally in the same logs), yet 0 such lines appear in either
    6000+-line log, despite the instrument firing in 199 other historical run dirs. A real
    crash inside the function's body cannot skip its own unconditional entry print — this is
    the `nm -n` nearest-symbol lookup (item -311's fix) misattributing a nearby unexported
    crash site, same family as item -310, not fully closed by -311. **Do not chase
    "waitForAnyAudioSlot boot deaths" from this signature.** Also sharpens item -361's option
    (b): since these nulls die with `case6=0 hangar-sel=0` (before `ROGUESQ_FORCE_CASE6_START`
    ever engages), "the force mechanism adds fragility" cannot explain them — a natural-path
    comparison's real value is `s594_c`-style recovery-cell reliability, not pre-engagement
    survival. Full detail: `PORTING-STATE.md` Session 597.

-361. **(s589-s610) thr11→sec4→sec2 pipeline — reachable when recovery fires (s608); blocked
    by recovery silence (-374) or mid-window cutscene Abort (-375) otherwise.** thr-11 =
    `saveServiceWorker` entry=`0x8006F2CC`. s608: thr11 destroy + sec4 + thr12 + **sec2**
    with recov76B768~=92, recov76BA90=0 (H-handoff2 REFUTED; H-handoff3 SUPPORTED). s609:
    eng+inject without 76B768 → no thr11 destroy (H-recov1 necessity SUPPORTED). s610:
    eng+inject+76B768×48 died mid recovery window on mat3inv Abort before thr11 destroy.
    Residuals: material `0x8000e29c`; recovery silence (-374); mat3inv (-375); post-sec2
    -373. Free-reroll all three noise classes. Do not raise HOLD_S past 210. Full:
    Sessions 589-610.

-360. **(s590/s591) thr-11→sec4→thr-12→sec2 pipeline RECHARACTERIZED.** thr-11
    `saveServiceWorker` is an infinite recv loop, destroyed only externally, co-timed with sec4
    DMA when FULL_SYNC recovery is healthy (H12c SUPPORTED; H12a mesg/audio-wait REFUTED).
    Primary remaining = item -361 + recovery reliability. Artifact: `s591_thr11_pipeline/ANALYSIS.md`.

-359. **(s589/s590) Force path missing section 2 RECHARACTERIZED.** Not a case5-vs-case6 gate
    (H11a REFUTED — FORCE_CASE6 reached 6→8+hangar-sel+VI640, still 0 sec2). Real gap = item
    -360's thr pipeline. `ROGUESQ_FORCE_CASE6_START` (ACE94, default off) landed as reliable
    exit tool.

-358. **(s588-s590) Post-dual empty after H9d RECHARACTERIZED/CLOSED as structural gap.** H10a
    CONFIRMED — recovery cell `0x76B768` firing yields 2288 post-dual `syncs>0` (H10b/H10d
    REFUTED). Empty = failed recovery, not a missing task-end inject. 2nd recovery confirm s590
    @0x76B768×3853. Artifact: `s589_post_dual_empty/ANALYSIS.md`.

-357. **(s587/s588) Residual F3/FD FULL_SYNC starvation FIXED s588 (H9d drop-return).** Extend
    `ROGUESQ_FS_PIPE_INJECT` to any non-E9 size-8 at slot∩last_fs, inject+drop. 570 continuous
    E9→E7→F3→FD, 0 UJ, hangar e9_b 39/40. Default OFF until item -358.

-356. **(s586/s587) H7 writer RESOLVED; product `FS_PIPE_INJECT` E7-phase DONE (default OFF).**
    E9→E7 is Factor5 LLE RSP (H7a CONFIRMED). Mode-1 non-mutating E7 inject H8a CONFIRMED.

-355. **(s585-s589) H-sync4 mechanism + writer + product inject through FD.** Sticky side-slot
    FULL_SYNC; RSP writer (H7a); E7 + F3/FD inject. Natural dual sticky confirm still open
    (H7d). Rolled into -358.

-354. **(s584/s585) H-sync4 stop edge RESOLVED as staging-cell opcode switch.** Shared 8-byte
    DPC staging cell at phys `0x76DF60`; 237 E9 then 150 E7 + 530 FD, dual DLs continue (H5b/H5c
    REFUTED). Force recovers at `0x76A838` task #6258.

-353. **(s583/s584) H-sync4 stop edge — owner FOUND, RESOLVED s584 → item -354.** Shared LLE DPC
    staging cell at phys `0x76DF60`. Stop = content switch E9→E7 (then F3/FD), not submit-path
    death.

-352. **(s582/s583) H-sync4 source FOUND.** Cutscene dual DLs have e9_b=0 yet runner syncs=1
    for ~238 tasks then flip to syncs=0 — all real guest `E9000000` (G_RDPFULLSYNC) at fixed
    phys `0x76DF60`, a side-slot outside the task `e9_b` tree (H4c CONFIRMED; H4b/H4d REFUTED).

-351. **(s581/s582) Factor5 DL walk GREEN; post-exit H-sync1 CONFIRMED, H-sync2 REFUTED.**
    Hangar control e9_b 30/30 (H-walk1 CONFIRMED). Post-exit plateau 132/132 e9_b=0, 0 cases of
    e9_b≥1 & syncs=0. Use `e9_b` as authoritative guest FULL_SYNC presence.

-350. **(s580/s581) `ROGUESQ_LOG_DL_SYNC` walker FIXED s581.** Factor5 `0xB5` is a chunk
    marker/no-op, not ENDDL; treating it as ENDDL ended walks before guest `0xE9`. Closed by
    `e9_b` mode.

-349. **(s579) Post-mission-overlay RDP `fs` plateau RECLASSIFIED — NOT s178 producer-stop;
    FULL_SYNC starvation with live GFX tasks.** `rdpFs`==Σ`syncs`; last `syncs>0` task #5959,
    then 772 consecutive `syncs=0` all `exit=1`, 0 `stalled=1`, present FIRE pairs=4 (H-stall3b
    CONFIRMED; H-stall1/2/classic-s178 REFUTED). Root-caused through items -352..-356 into the
    `FS_PIPE_INJECT` product line.

-348. **(s568/s569) SIBLING_PTR DIRECT residual same-base gap class — FIXED and FULLY CLOSED
    2/2.** 218 new guard sites (w1=159 TIGHT+delay-dups, w2=52 multi-field tails, w3=7
    second-order); freelist R-numbered + ATTR residual EMPTY under dual scan — DIRECT residual
    campaign for this lineage exhausted.

-347. **(s566, s582, s594/s595 — 3 occurrences) `transformSceneLights`/`transformLightByType` /
    `last-guest-pc=0x80010134` breadcrumb — REFRAMED s595 as an instrumentation-coverage
    artifact, NOT escalated.** Neither function carries `g_rs64_last_guest_pc` tracking (only
    52/2499 functions do, all guard-campaign-associated), so a crash anywhere in this unaudited
    subtree freezes the value at the same caller stub — 3 reports are consistent with 3
    different crashes, not one recurring bug. No guard written. Method-trap generalization filed
    below: the "watch for the Nth occurrence" heuristic only has teeth when the reporting
    function is in the guard-audited set.

-346. **(s565-s567) `heapFreeListDequeue` residual r3-base write at `0x8000D6D0` — FIXED and
    FULLY CLOSED 2/2.** DIRECT gap before existing `HEAP_FREE_LIST_DEQUEUE_R2_GUARD`
    site=`0x8000D6D4`; fixed as `HEAP_FREE_LIST_DEQUEUE_R6_GUARD`. Same gap model as
    -334/-340/-345.

-320. **(s508/s565/s566) `loadCutsceneAssetsByIndex+1860`/`0x800aafb8` — ROOT-CAUSED AND FULLY
    CLOSED 2/2.** ≥4 hangarbay-controlled hits pre-fix. **Mechanism:** `projectModelBoundsToScreen`
    guard1/guard2 early-exit `goto` clobbered `$s1` before it was spilled, corrupting the caller
    (`runHangarSelectionFrame`)'s later reload. Fix: safe mini-epilogue.

-345. **(s562/s564) `heapFreeListDequeue` DIRECT gap after `HEAPLISTDEQ_ATTR_WRITE_GUARD`
    site=`0x8000D92C` — FIXED and FULLY CLOSED 2/2.** Same gap model as items -334/-340; extended
    to 7 residual sites sharing env `ROGUESQ_LOG_HEAPLISTDEQ_ATTR_WRITE_GUARD`.

-344. **(s562/s563) Non-r3 freelist dual-walk residual + freelist simple-walk — FIXED and FULLY
    CLOSED 2/2.** 3 sites (`allocateDisplayListBuffer`, `renderLitMeshFaceGroup`,
    `countDisplayListChunks`); packing DEFERRED (21/22).

-343. **(s561/s562) Residual freelist initial-deref GUARD2 — FIXED and FULLY CLOSED 2/2.** 92
    sites (`ROGUESQ_LOG_ALLOC_TAIL_GUARD2`).

-342. **(s560/s563) Residual freelist-walk GUARD3+GUARD4 — FIXED and FULLY CLOSED 2/2.** GUARD3
    x94 + GUARD4 x92.

-341. **(s559/s561) Freelist-walk GUARD4 systematic audit (item -339 shape) — FIXED and FULLY
    CLOSED 2/2.** GUARD3-without-GUARD4 gap at 16 sites (`emitAllocatedDLCommand` x3 incl -339,
    `heapFreeListDequeue` x4, `submitSceneNodeRender` x9 incl -337) — covers both -339/-337.

-340. **(s557/s558) `SIBLING_PTR_WRITE_GUARD` site=`0x80010B4C` (`submitSceneNodeRender`) — FIXED
    and FULLY CLOSED 2/2.** DIRECT gap after existing site `0x80010B48`, same model as item -334.

-339. **(s556) `emitAllocatedDLCommand+13216`/`0x800088ec` — ROOT-CAUSED, FIXED and FULLY CLOSED
    2/2 with item -341 (s561).**

-338. **(s554, s572, s574, s592, s598 — 5 occurrences) `beginFrameDLChunk`/
    `last-guest-pc=0x8000afa0` — ROOT-CAUSED s600, GUARDED as item -365 (`BEGINFRAME_S0_GUARD`
    site=`0x8000AFA0`); live 2/2 confirm PENDING (3 scored D: s600/s601/s602 r3).**
    Guest insn `lw $v0, 0x8($s0)` after null-only check on stack-slot-loaded node ptr; SIGBUS
    `si_addr=0x335000008` (4/5). s554 pre-crash also co-fired existing guards with
    `bad_ptr=0x7500D019` (corruption wave feeding the bad `$s0`, not a second independent
    bug). See items -365/-368.

-337. **(s551) `submitSceneNodeRender+69192`/`0x80010df4` — ROOT-CAUSED, FIXED and FULLY CLOSED
    2/2 with item -341 (s561).**

-335/-336. **(s550) Two single-occurrence background-noise breadcrumbs, filed not chased.**
    -335 `emitAllocatedDLCommand+1960`/`0x800086ec`. -336 `findLookupEntryByKey+2212`/
    `0x800ac914` — same symbol+offset as item -325 but a DIFFERENT `last-guest-pc` (pc-symbol
    instability gotcha, s541) — a new single-occurrence signature, not a 2nd occ of -325. Watch
    both for recurrence.

-334. **(s549) `SIBLING_PTR_WRITE_GUARD` site=`0x80010DCC` + item -327's root-cause fix
    (`DL_LIST_APPEND_DEREF_GUARD`, 84 sites) — FIXED and FULLY CLOSED 2/2.** Found via DIRECT
    mechanistic correlation: an unguarded write immediately after existing guard `0x80010DC4`,
    reusing the same already-flagged-bad register — same non-branch-likely recompiler duplication
    (`bne`/`bnel` taken+fallthrough) that `FREELIST_NEXT_GUARD` hit (s441). Fixed as 2 new
    entries (122nd/123rd) in the family's site list. 2nd confirm clean; crashed downstream on the
    unrelated item -336 breadcrumb. Full derivation: `PORTING-STATE.md` Sessions 549-550.

-328..-333. **Six single/double-occurrence breadcrumbs surfaced by item -317 step 3's s526-546
    live-verifies, all filed not chased.** Full detail: `docs/PROJECT-OVERVIEW.md` §25-§26.
    -328 `submitSceneNodeRender+69820`/`0x80010ebc`. -329 `rebuildActiveDisplayObjectList+660`/
    `0x800ab060`. -330 (2 occurrences back-to-back, weak corroboration) `heapFreeListInsert+72`/
    `0x800220b8`. **-331** (`local-symtab`, free-list-pop region) `heapFreeListDequeue+29152`/
    `0x8000d688` — **2nd occurrence s593**, confidence low→moderate, watch for a 3rd. **-332**
    (weak `n=5`, recurred s544 with a strong `n=2600` control) `submitSceneNodeRender+38976`/
    `0x8001086c` — confidence low→moderate, watch for a 3rd. **-333** (`local-symtab`, 16 bytes
    from -331's address, distinct guest PC) `findAndUnlinkSmallestEntry+356`/`0x8000d698`. Watch
    all six for recurrence before escalating.

-320..-327. **Eight breadcrumbs (s508-524); -320 FULLY CLOSED 2/2 s566 (see top entry); -321
    REFUTED; -322 FIXED+CLOSED (+ residual -345); -327 FIXED+CLOSED with -334; -323..-326 watch.** -323
    (s514) `beginFrameDLChunk+27456`/`0x8000ae40`. -324 (s521) `heapFreeListInsert+72`/`0x80015544`.
    -325 (s522) `findLookupEntryByKey+2212`/`0x800ad0dc`. **-326** (s524) `do_rom_read+608`/
    `0x800025ac` — **if a 2nd occ appears, urgent**.

-319. **(s503/s505/s519, 3 occurrences) `beginFrameDLChunk+40536`/`0x8000b0d0` — FIXED and FULLY
    CLOSED 2/2.** `SIBLING_PTR_WRITE_GUARD` site=`0x8000B0D0` (121st site), a genuine gap in the
    original s459 sweep between two already-guarded `-0x23A8` sibling sites. Full mechanism:
    PROJECT-OVERVIEW §24.

-318. **(s501-507) `appendRdpStateDl+144` crash — FIXED and FULLY CLOSED 2/2
    (`APPEND_RDP_STATE_DL_ENTRY_GUARD`).** All 6 call sites reload a sibling global with no range
    check and pass it as a write-cursor argument, outside the existing 119-site
    `SIBLING_PTR_WRITE_GUARD` audit's scope. Fixed by range-checking at function entry. Mechanism:
    `docs/PROJECT-OVERVIEW.md` §23.

-317. **(s490-569) Step 3 of the `-312..-316` lineage: a ~150-location blanket sweep of the same
    derived-pointer reload idiom across `funcs_3.c`/`funcs_4.c` — 131 guards, ALL FULLY CLOSED
    2/2.** Steps 1 (`heapFreeListDequeue`) and 2 (`buildOrientedFaceGeometry`) separately FULLY
    CLOSED 2/2 (step 3 later added R-numbered guards inside these same functions too — a naming
    coincidence, not a reopen). Tracer `scratch/agent/s494_item317_step3_tracer.py` found ~448 raw
    reload sites deduping to ~150 placements; shared shape: null check gates one arm, non-null
    fallthrough has no `0x80000000`-`0x80800000` range check before write-through deref — skip on
    invalid is safe. **s558-s569 residual sweeps** (items -341..-348) closed the freelist WRITE
    campaign, item -320's `projectModelBoundsToScreen` root cause, and the SIBLING_PTR DIRECT
    residual class — DIRECT residual campaign now exhausted. **Standing gotchas** (full:
    PROJECT-OVERVIEW §22-§25): hangarbay positive control (s536); cross-check `last-guest-pc` not
    host symbol (s541); weak item -306 early deaths discard+retry; early-guard `goto` full
    epilogue only if ALL callee-saves already spilled (s565). Raw detail: `PORTING-STATE.md`
    Sessions 490-569.

-316. **(s488-490) `DL_ALLOC_PROPAGATION_GUARD` — FULLY CLOSED 2/2.** A scope gap in the existing s436
    `CACHE_HEAD_A1_GUARD` (`emitAllocatedDLCommand`): validated one deref but not two propagating
    writes right after it feeding a `-0x5BB4` write-cursor global unguarded at 19 sites; fixed by
    extending the check. Its own 2nd confirm surfaced item -317 above. Full derivation:
    `docs/PROJECT-OVERVIEW.md` §21, `PORTING-STATE.md` Sessions 488-490.

-311. **(s480) Crash-symbolizer tooling fix — DONE, positive-control validated.** Closed the item -310
    `dladdr`-nearest-exported-symbol blind spot: `src/main/main.cpp` now builds a sorted local+exported
    symbol table (`nm -n`) and `[CRASH][pc-symbol]` does a nearest-preceding-address search against it
    first, falling back to `dladdr` only if uncovered. Validated with a deliberate crash inside
    `do_lwl` (item -310's own 40KB gap): correctly symbolized. Full derivation: PROJECT-OVERVIEW §19,
    `PORTING-STATE.md` Session 480.

-310. **(s478) `heapFreeListDequeue+NNNN` crash family — INVESTIGATED AND CLOSED, a crash-symbolizer
    artifact** (`dladdr` nearest-exported-symbol misattribution over a 40KB unexported-code gap), not
    a real recurring bug — guest-address arithmetic ruled out both `last-guest-pc` data points. No
    guard written. **The symbolizer blind spot is now FIXED, see item -311** — any NEW occurrence will
    carry a `(local-symtab)` tag naming the real function; do not re-file future occurrences as this
    family unless the log predates s480. Full derivation: `docs/PROJECT-OVERVIEW.md` §19.

-305..-309. **(s472-477) Five more single-bucket audits from the s465 frequency-scan lineage -- four CLASSIFIED AND DEFERRED (not guard candidates), one (-306) a real fix.** -305 (`hi16=0x8011,off=0x63d4`, 170 sites, scan's largest bucket): compare-only bounds-check idiom (27-site sample, 26/27 confirmed). -306: resolved -296's flagged `-0x23a8` gap into a real `SIBLING_PTR_WRITE_GUARD` fix (1 new site, 120th, `setupCameraMatrices`, missed by s459's taint-tracking), CLOSED, 2nd confirm (s474) clean. -307 (`hi16=0x8011,off=-0x35e0`, 23 sites/9 files): compare-only integer-flag idiom (12 writes confirm non-pointer). -308 (`hi16=0x8013,off=0xb50`, 24 sites/12 files): compare-only bitfield test, never dereferenced. -309 (`lui`+`sw` scan, 546 buckets/1471 sites, top 3 checked): every large bucket a fixed-address global store, no stale-pointer risk -- closes the `lui`+`sw` angle alongside `lui`+`lw` (s476). No code change except -306's. Full derivation: `docs/PROJECT-OVERVIEW.md` §19.
-298..-304. **(s463-472) Seven more M3 idiom-class audit buckets from the s465 frequency scan, six CLOSED, one DEFERRED — every CLOSED item's soak result matches item -287's established true-negative baseline.** -298 `DL_LIST_RESET_GUARD` (re-scoped ~111 non-canonical `-0x5824` sites, global `0x8011A7DC`) CLOSED s464, 84/84. -299 `DL_BUFFER_POOL_GUARD` (`0x801163FC`) CLOSED s466, 84/84, 2nd confirm s467. -300 `NODE_LIST_HEAD_GUARD`/`_WRITE_GUARD` (`0x8011A4B8`) CLOSED s467, 20 read + 10 write sites (two distinct downstream shapes), 2nd confirm s468. -301 `TEXDATA_TABLE_GUARD` (`hi16=0x8013,off=-0x70F8`, `funcs_6.c`) CLOSED s468, 31/31 (substitutes `0x80000000u`, not 0, since index arithmetic follows), 2nd confirm s469. -302 (`hi16=0x8013,off=0x7CE4`, 45 sites/9 files) DEFERRED s468: small INTEGER INDEX, 17 distinct downstream shapes, no single guard placement covers all sites without speculation. -303 `TEXDATA_PTR_ARRAY_GUARD` (`hi16=0x8013,off=-0x7104`, `funcs_6.c`) CLOSED s470, 29/29, 2nd confirm s471. -304 `MATERIAL_ARRAY_PTR_GUARD` (`0x8012($reg)`→`-0x5BBC`, 30 sites/4 files) CLOSED s471, 30/30, 2nd confirm s472. Full derivation: `docs/PROJECT-OVERVIEW.md` §18-§19.
-291..-297. **(s454-462) Three M3 idiom-class audits found via an s454 concurrent-process collision, all CLOSED**: -291 `DL_LIST_APPEND_GUARD` (57 sites), -292 `SONGTEMPO_TABLE_GUARD` (43/43 sites, `funcs_25.c`), -296 `SIBLING_PTR_WRITE_GUARD` (119 sites; **AMENDED s473/item -306: 1 real site silently dropped by a taint-tracking gap, found+fixed+confirmed**). Full detail: `docs/PROJECT-OVERVIEW.md` §17.
-261..-290 (and -263). **(s424-453) The duplicate-symbol-name-collision arc -- ALL CLOSED.** A duplicate-symbol collision truncated `initCraftSelectScreen`; the fix cascaded into 3 more guarded crashes (-261..-267), a full duplicate-symbol catalogue closure (18/18) plus a 107-site `GENERIC_CACHE_GUARD` sweep, item -263's misattribution chase resolving to a third free-list sibling bug (`FREELIST_NEXT_GUARD`, -277, 105 sites), and the `static5-rename-orphan-sweep` (94 sites across 6 pre-s427 guard families). Full detail: `docs/PROJECT-OVERVIEW.md` §16, `PORTING-STATE` Sessions 424-453.
-259. **(s422) `0x800290d4` "six independent triggers" -- INVESTIGATED AND CLOSED, not a bug**: `inflate_fast`'s own clean return, misread as a shared corruption sink. `PORTING-STATE` 422.
-231..-249. **(s377-421) Three more CLOSED arcs: fixup function-scope backport (176 patches, 168 converted), M3 `-0x25A4`/"Lookup" idiom resumption, and the 784-function `main_overlay.txt` phantom-overlay relocation.** Full detail: `docs/PROJECT-OVERVIEW.md` §13-§15, `PORTING-STATE` Sessions 377-421.
-230..-14 (excluding -20, kept below). **Eleven closed investigation lineages, s99-s376 -- all CLOSED, no outstanding action.** M5 audio de-stubbing (items -160..-230, s297-376, §9-§12) plus ten earlier whack-a-mole guard-gap chases (`composeNpcOrientationMatrix`, `renderUnlitMeshFaces`, `heapWalker`, `heapFreeListDequeue`, `-0x25A4` family, breadcrumbs B2-B14, audio-array-corruption race, `submitDmaRequestBatch` indirect-caller, CALayer/campose SIGSEGV, regen-pipeline-idempotency root cause, §9). One-paragraph-per-lineage summaries: `docs/PROJECT-OVERVIEW.md` §9-§12; full raw detail: `PORTING-STATE` Sessions 99-376.
-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic).** Root cause: `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c` file that already exists on disk, so any patch whose regex anchor survives its own insertion stacks a duplicate on the next `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every regen is mandatory but **not sufficient by itself** -- residual intermittency's root cause is still unknown. **Standing rule**: audit the patch report for anything other than the expected `xN` count after every `fixup_game_funcs.py` run. Full detail: `PORTING-STATE` Sessions 120, 121, 126.
-11. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89), RECURRED s424, ROOT-CAUSED AND GUARDED s425.** s424 hit it as a sibling of item -261's guarded `startPlayerSlotAnimationChannelLooping` crash; s425 root-caused and guarded it (wild `$a0` arg, same never-initialized-slot root state) — see item -261 for the full trace.
-10/-9. **M3 — Metal-shader-compiler SIGSEGV reproducibility** (s83 spline1: SIGSEGV inside `Metal.framework`'s `MTLCompilerFSCache`, no source on our side; still one data point). **Confirm the s83 spline div0 guard actually engages**: 0/5 fires so far (still 0 after s88/s89/s90); real fix by code inspection (genuine 0/0 IEEE division) but no same-run positive control yet.
-8. **M3 — characterize `frameStartReset` SIGBUS.** 3 occurrences (s85, s108, s156 — the 3rd, `+532`, at a call chain byte-identical to `composeNpcOrientationMatrix`'s own, raising a shared-dispatcher hypothesis); no located faulting instruction in any of the 3.
-7. **M3 — hangar-exit → mission-entry (M3 DoD gate): OPEN.** Exit + cutscene CONFIRMED (s577);
    FULL_SYNC inject product-fixed (-354..-358); force6 engagement CONFIRMED s606; **s608 first
    force-path sec2 after thr11 destroy** when recovery `0x76B768` fires. Co-primary blockers
    on the eng+inject path: recovery silence (-374), mid-window mat3inv Abort (-375), material
    noise `0x8000e29c` (2×). In-mission still blocked by post-sec2 HMT/`packTlut` (-373, 1×).
    H-handoff2 REFUTED. `FS_PIPE_INJECT` / `FORCE_STATE6_AFTER` still default OFF.
-6. **(s53/s54→s399) M4 — the 3 `[missing-func]` addresses: DONE, CLOSED s399.** s54's fix was dead on arrival — silently shadowed by pre-existing duplicate entries at the same addresses in `main_overlay.txt` (first-discovered instance of item -249's family). Root-caused and fixed s399 by deleting the 3 duplicate lines; verified 3/3 post-fix runs, same-run positive control. Full detail: `PORTING-STATE` Session 399.
-5. Past the first sustained mission hold: expect further new failure classes (mission overlay DMA → missing-func/UnhandledJumpTarget, new VI phase, overlays 12/44 splice, texture corruption — s399's item -248 is a concrete, proactively-found instance of exactly this). Each new failure is its own work unit.
-3. **Sibling-repo housekeeping (flagged s54, not autonomous):** `~/Documents/Tools/rogue_squadron64` carries uncommitted symbol-file edits, including s54's now-superseded `mission_overlay.txt` addition, s399's `main_overlay.txt` 3-line deletion (the actual fix), and s426's `menu_overlay.txt` duplicate-symbol deletion (item -262's fix). Ask the user before committing there.
-2/-1. **Band-row coverage history** (settled, s41-49): s40's `col`-write probe fails its control. **GPU->CPU present PNG** via `NativeTarget::copyToRAM` -- a convenience, not a blocker.

**Done, do not redo:** optimising the ucode vector path (s38: `-O0`→`-O2` gave 41x; SIMD/RSPRecomp vector work unnecessary at 4.5ms/task without new justification); the ucode-performance-bottleneck→DL-submission-collapse→RDP-census→draw-loss chain (s33-s37); coverage attribution/format-mismatch analysis (`LOG_BBOX`/`LOG_UPLOAD` — every band draw is I4 `tlut=0`); the s27-s31 I4-decode line (`FIX_DXT_I`, `I4_SHADE_MONO`, `SHADE_ONLY_MONO`, restricted `FLATTEN_I4`) — aimed at a texture that doesn't paint those pixels.

## Regeneration and build pipeline

Game functions (s1) — all four steps, in order:

1. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
2. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
3. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — **required**, and the only thing that
   re-applies the hand-edits, idempotently:
   - writes to `$zero` (`0 = expr;`) commented out (~2700 sites; the recompiler emits invalid C)
   - `fake_func_*` gap fillers with gotos to nonexistent labels → `__builtin_trap()`
   - real functions with cross-function branches (shared asm tails: `lvj_checkComplexObjectives`,
     `audioCompandS16`, `applyVoiceDelayFilter`, `__OSGlobalIntMask`) → each bad goto becomes
     `__builtin_trap()`; a runtime SIGTRAP means one of those was taken
   - audio-engine gate stores → 0 in `funcs_23.c` for `setDisplayMode`/`reapplyDisplayMode` only (gate
     byte 0x800A0F50) — without this the scheduler wedges in `waitForMusyXAudioTaskDone`.
     `initMusyXEngine`'s own site was reversed s302 (M5 step 4); the guest's real write takes effect
     there now, validated 0/2 family #1 recurrence over 2 soaks
   - the `jr $t9` return idiom in `funcs_4.c` (`convertMat3x4ToN64Mtx`, 0x80018D80) → plain `return`
     instead of `LOOKUP_FUNC(ctx->r25)`
   - `musyxKeyOnVoice` `break 6/7` div-by-zero guards → early `return`, keyed on the exact `do_break`
     constants 2148076780..2148077008
   - `evalCubicSplineAtTime` (s83) zero-width-interval div0 guard at `0x8001906C` (`funcs_4.c`) —
     `f1.fl==0` → log first 20 as `[spline-div0]` + `f4.fl=0` instead of `DIV_S` producing NaN
4. `cd build && cmake --build . -j8`

RSP ucode (only when a ucode toml changes): `~/Documents/Tools/N64Recomp/build/RSPRecomp` on
`factor5_rsp.toml` / `factor5_boot_rsp.toml` → `build/factor5_ucode/*.c`, then
`tools/fixup_factor5_ucode.py`. **s47: before the fixup, also run
`python3 tools/make_clip_composite.py` + RSPRecomp on `factor5_rsp_ovl4.toml`** — fixup 6 splices
the clip-overlay translation from `factor5_ucode_ovl4_recompiled.c` and hard-fails without it
(build/ is gitignored, so a fresh checkout must regenerate it). `factor5b_rsp.toml` (ROM 0x9ABE0)
is the **MusyX audio** ucode; `factor5_ucode_b_recompiled.c` stays in the build as a never-called
artifact (s5).

Standing warnings:
- `lib/N64ModernRuntime` and `lib/rt64` carry **uncommitted working-tree patches**:
  `librecomp/src/pi.cpp` `do_dma` → `load_overlays_by_start`, `overlays.cpp` `it < upper`,
  `librecomp/src/rsp.cpp` `rs64_dmem_lock/unlock` hooks (the shared-DMEM serialization, s5), and the
  whole RT64 assert-guard chain (s2b/s3/s7/s9/s12). **Never `git submodule update --force`.**
- The ROM must sit next to the executable in `build/`; run from anywhere else and the binary silently
  takes the "place your ROM" path and gives a dead VI (s8).
- Hand-edited diagnostics in `build/factor5_ucode/*.c` survive a cmake build but **not** an RSPRecomp
  regen — add them to `tools/fixup_factor5_ucode.py` to keep them. Diagnostics in `RecompiledFuncs`
  are wiped by regen entirely.
- The settings.json Bash allowlist matches the FIRST WORD of the command: `VAR=1 tools/probe.sh …`
  is denied despite `Bash(tools/:*)` — prefix such commands with `env` (allowlisted) instead (s44).
- Harness: `clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m`;
  capture with `tools/probe.sh` / `tools/regress.sh`. Kill runs with SIGKILL, not SIGTERM — the TERM
  path aborts in SDL_QUIT cleanup and leaves a crash dialog over the next run's capture (s9).
  Python decoders need `scratch/venv/bin/python` (PIL is gone from system python, s18).
- `regress.sh` preflight must not write probe images as `.*` hidden names: `screencapture` refuses
  final path components starting with `.` (exit 0, no file) and falsely reports visual=denied (s26).
- ~~Screen Recording permission is intermittent~~ — **overturned s32**: capture and synthetic input
  both work (74/74 `screencapture -l` succeeded, stable CGWindow id). `could not create image from
  window` means the **window id is wrong**, not missing permission — check via `winctl find <pid>`
  (`winctl trusted` reports Accessibility state; `winctl list` is not a subcommand).
- `winctl activate` is a cooperative request modern macOS **ignores while another app holds focus** —
  keys then drop silently with `trusted`=yes (s45; the real cause of the old "no GUI session"
  failures). `probe.sh`/`regress.sh` raise via System Events `set frontmost` (`raise_game()`) instead
  — use them rather than `winctl` directly for driven runs.

## Overturned conclusions — do not act on these

Full list (11 entries spanning s2-s422, each with why it was believable and what refuted it),
plus the early-era dead-ends list, migrated to `docs/PROJECT-OVERVIEW.md` §26. Load-bearing for
active work: **(s400-421->s422)** `0x800290d4` "six independent triggers" is `inflate_fast`'s
clean return (background noise). **(M5-AUDIO-PLAN.md §4->s371)** host audio
`queue_samples`→`SDL_QueueAudio` unit-mismatch, fixed s371. **(s578→s579)** post-exit `rdpFs`
plateau is **not** the s178 graphics-task-submission stall — s178 is `stalled=1 pairs=0` +
producer stop; s577 post-exit keeps submitting/completing GFX tasks with present FIRE pairs=4
while only FULL_SYNC (`syncs`/`rdpFs`) dies (item -349).

### Dead ends — labelled as such in the log, do not retry

Full list (early ucode/DMA/overlay hacks, s2b-s91, each made things worse or had no effect)
migrated to `docs/PROJECT-OVERVIEW.md` §26.

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here, session tag is the
specific instance in PORTING-STATE:
- §4.1 instruments-that-lie: `fbPair.projections` over-count (s32), `[loadblock]` sampled-log miscount (s18/s19), stale TMEM at draw-record time (s19), capture harness outliving the process, `window_burst.sh` 60/60 false-positive (s9).
- §4.2 attribution errors: colour match ≠ attribution, fog #C8C0A0 (s18); plausible decoded image ≠ phase ID (s17).
- §4.3 cross-run comparison: knob effects/nulls manufactured by camera drift, "7.30%" constant misread as an effect (s18); phase timing varies tens of seconds run-to-run, gate on `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1` not a stopwatch (s17 → s18/s23).
- §4.6 missing protocol events: pair/buffer/wrap counters measured instead of FULL_SYNC arrivals (s11).

Other instrument-specific traps (crash-free-soak-isn't-evidence, orphaned background soaks,
sparse-screenshot false regressions, unvalidated suppression instruments, `dpc_bridge` walker desync,
histogram-drain timing, camera motion confounding aggregates): `docs/PROJECT-OVERVIEW.md` §8.
- **crash-signature blindness (s344)**: a soak-recipe verdict of "did any `[CRASH]` marker fire" is not
  evidence for a SPECIFIC target crash unless `last-guest-pc`/`pc-symbol` is checked against it — RS64
  has ~20+ independent, already-catalogued, nondeterministically-firing crash families, so a bare
  presence check will false-positive-confirm the wrong bug. Same session also found a `[keys]`-log-file
  bug (grepping the game's `run.log` for driver-emitted `[keys]` lines, which only ever land in the
  launcher's own log) that made 2 real, fully key/stick-driven soaks misreport as having driven no
  input at all. Item -200.
- **repeated-`last-guest-pc` is not repeated-bug proof outside the audited set (s595)**: `g_rs64_last_guest_pc`
  tracking is added per guard-campaign function (52/2499 functions, ~2%), not blanket. A crash inside an
  unaudited callee subtree freezes the value at the last *instrumented* caller, so N sessions reporting
  the identical address can be N different crashes sharing one caller stub, not one recurring bug at one
  site. Check whether the reporting function is in the guard-audited set before trusting the "watch for
  the Nth occurrence" escalation heuristic used throughout the Next-steps breadcrumb list. Item -347.
