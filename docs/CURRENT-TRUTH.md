# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. 28 passes so far
   (git log has per-pass targets; PROJECT-OVERVIEW §16-§27 hold the most recent arcs) kept the file
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

## Current truth (established by session 295; unchanged, reviewed through s621)

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
| ~+90-115s post-leave | varies | **graphics-task-submission stall** — `[vi-fs-decision]` reports `stalled=1 pairs=0` continuously, RDP `fs` counter frozen. Not a crash; a staggered subsystem shutdown (s178). Open, unresolved as of s183 (last dedicated session). Full detail: `PORTING-STATE` Sessions 176-183. Note s579: post-exit `rdpFs` plateau with live GFX is a *different* class (FULL_SYNC starvation, item -349) — do not merge. |

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

**M1 — hangar band root cause and fix: DONE (s48).** Mechanism: `docs/PROJECT-OVERVIEW.md` §3.

**M2 — post-clip-fix regression sweep: DONE (s49).** Stability baseline: 1138 tasks, fanjal=9448,
0 cull-census-identity violations. The 3 `[missing-func]` addresses **DONE/CLOSED s399** (item -6).

**M3 — first gameplay: OPENED (s50), still open.** AVAILABLE CRAFT and SELECT YOUR CRAFT reachable
and stable; ~20 crash classes closed s50-s294. Leave-key "hangar-flight" OVERTURNED s150; **s577
REAL hangar exit CONFIRMED** (case 3→5→6→8). Post-exit FULL_SYNC starvation product-fixed via
`ROGUESQ_FS_PIPE_INJECT` (default OFF; items -354..-358). Pipeline status as of **s621**:
- thr11 (`saveServiceWorker` `0x8006F2CC`) → sec4 → thr12 (`hudDisplayUpdateWorker` via
  `loadLevelTextureCache`) → sec2 (mission overlay) is reachable when recovery cell `0x76B768`
  fires (s608; H-handoff2 / 76BA90 REFUTED). **s619: thr11d_new LIVE** when recovery fires →
  sec4_post=1; class-D craft-shadow soft-skip LIVE (cshadow_a≥1); thr12 blocked by null
  `rs_malloc(0x136C)` in thr12 parent (**-385**, guard landed s620; **live-verify still
  PENDING** — s621 recovery-active never re-entered class-D).
- Co-gates: recovery silence (-374; s621 freeroll fix: any eng+hsel `recov768=0` freerolls),
  mid-window mat3inv Abort (-375, free-reroll), post-hsel `isPlayerShipActive` ret=1 / ship
  store (-376/-377), class-D craft-shadow (**-378**), FORCE_STATE6 KSEG0 base OOB (**-381
  CLOSED s617**), scene-graph (**-382**), readAccount (**-383**), freelist null-base (**-384**),
  null-malloc thr12 parent (**-385**, guard landed; M1 PENDING), **sinfApprox NAN_CHECK Abort
  on recovery-active thr11-live path (**-386**, 1× freeroll, s621)**, trackResourceList
  freeroll noise pre-recovery (not escalated).
- **thr11d scoring trap (s618):** post-hsel destroy of the *old* thr11 is not thr11d. Real
  metric = destroy of an id created post-hsel with entry `0x8006F2CC` (`thr11d_new`).
- **Soak freeroll trap (s620→s621):** freeroll that requires `EARLY_REASON=recovery_silent`
  misses mid-HOLD crashes (EARLY empty) and wrongly scores them. Fix: freeroll any
  eng+hsel with `recov768=0` (H-freeroll1 CONFIRMED s621b).
- Tools (default OFF): `FORCE_STATE6_AFTER`, `FORCE_CASE6_START`, `FS_PIPE_INJECT`.
- Post-sec2 residual: HMT/`packTlut` SIGBUS (-373, 1×). Material `0x8000e29c` (2×, free-reroll).
- Full durable arc: **`docs/PROJECT-OVERVIEW.md` §27**; items -349..-386; Sessions 577-621.
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
a range pointer. Highest allocated so far: -386. The next NEW item takes -387.

### Active M3 pipeline (s577–s621) — open residuals only

-386. **(s621) recovery-active thr11-live `sinfApprox` NAN_CHECK Abort — 1× freeroll.**
    Host: `sinfApprox` (funcs_5.c:6460 `assert(f10==f10)`) ←
    `buildPositionAndCallTransformHelper` ← `runModelViewerLoop` ← `menuOverlayInit`.
    Known freeroll family (s214/s215); thr11c_post=1 thr11d_new=0 (blocks thr11d/class-D).
    Free-reroll 1st; escalate only on 2nd same host stack with thr11 live. Full: Session 621.

-385. **(s620→s621) `loadLevelTextureCache` null `rs_malloc(0x136C)` fill SIGBUS — primary
    residual after class-D entry (guard landed; live-verify still PENDING).** s619 scored a2:
    thr11d_new=1 sec4_post=1 cshadow_a=3 ltex=1 thr12=0; crash `loadLevelTextureCache+2576`
    si_addr=`0x380001054`. Guard: `[level-tex-malloc-guard]` @ `0x80048248` → `L_8004840C`
    (in binary; strings present). s620 soak was recovery_silent (freeroll-bug scored). s621
    recovery-active hit sinfApprox (-386) before thr11d/class-D — **ltexmg never observed**.
    Soft-skip skips `registerServiceWorker` so thr12 stays 0 until malloc succeeds. Why
    malloc null is open (H-ltexOOM) after M1. Full: Sessions 620-621.

-384. **(s619→s621) Post thr11d_new+sec4 `buildMaterialFreeList` null-base SIGBUS — 1×;
    H-matfree1 SUPPORTED (0 on s619 scored freeroll).** s618 only hit. Host
    `buildMaterialFreeList+260` ← `advanceVideoFrame` ← `initSceneForMission`. Do not
    merge with -385 (different stack) or -373 (stale pc). Escalate only on 2nd same host
    stack. Full: Sessions 618-621.

-383. **(s618→s620) Post-force `readAccountForSelectionScreen` SIGBUS — stays 1× free-reroll;
    0 on s618/s619 scored (H-readacct1 SUPPORTED).** local-symtab often mislabels as
    `rebuildActiveDisplayObjectList+540` — nm: `readAccountForSelectionScreen+604`
    (guest `0x800B85B4`). Escalate only on 2nd same host stack. Full: Sessions 618-620.

-382. **(s617→s620) Post-force `traverseSceneGraphRecursive` SIGBUS — H-sg1 SUPPORTED (0 on
    scored; freeroll noise including s619 a1). Stays 1× freeroll policy on scored path;
    do not escalate without 2nd on recovery-active scored.** Full: Sessions 617-620.

-381. **(s616→s617) FORCE_STATE6 KSEG0 `uint32` base OOB — FIXED and LIVE-VERIFIED.**
    S32-extended `gpr base = S32(0x800D << 16)` in case5 force-state6 + case3-start.
    s616 soak: `case5_n0_state=5` (matches hangar-state), `ctrl_good=5 ctrl_bad=0`,
    `force6=1 force_old5=1 force_skip=0`, hangar 5→6→8 after force. H-kseg3 + H-force6c
    CONFIRMED. **CLOSED.** Full: Sessions 616-617.

-380. **(s615) Fold `s614_class_d_force_gate` + `s615_class_d_recov_active` — both
    unscored recovery_silent; force_skip was OOB base (closed by -381).** Natural ACE80
    still engages without force-write. Full: Sessions 615-617.

-379. **(s614) FORCE_STATE6 state==5 gate — still correct policy; s613 hang recharacterized
    by -381 as OOB write (hangar never left 5), not a successful 3→6 clobber.** Gate
    logs `[case5-force-state6-skip]`. Keep gate after S32 base fix. Recipe
    `ENGAGE_WAIT_S=90`. Full: Sessions 614-616.

-378. **(s613→s620) class-D craft-shadow soft-skip LIVE on scored (cshadow_a=3 s619);
    thr12 still blocked by -385 null-malloc in parent.** thr12 parent =
    `loadLevelTextureCache`. Guards: `[craft-shadow-asset-guard]`/
    `[craft-shadow-walk-guard]` @ `0x8006B764`/`0x8006B780` + `[level-tex-cache]` +
    `[level-tex-malloc-guard]` @ `0x80048248` (-385). walk-guard not entered (asset-guard
    soft-skips all three crafts). Full: Sessions 613-620.

-377. **(s612) gPlayerShip writer instrument live.** Only two stores to `0x800CC85C`:
    non-null `updateTextOverlayLookupEntry` @ `0x800B40D0` (when current null; copies
    `0x800CC864`); zero `destroyPlayerShipRecord` @ `0x800B42A8`. Tags `[ship-store]` /
    `[ship-zero]` / `[ship-store-skip]`. H-ship1b not fully causal-proven (no E_store_no_thr11d).
    Full: Session 612.

-376. **(s611) thr11-destroy co-gate: post-hsel `isPlayerShipActive` ret=1 — H-ship1
    SUPPORTED.** Controls s592_a+s607 have post-hsel ret=1 before destroy; s610 class E stall
    had 0 post-hsel ret=1 with thr11 live. Full: Sessions 611-612.

-375. **(s610) Post-exit `mat3x3InverseInto` Abort (NAN_CHECK) mid recovery→thr11 window —
    1×; free-reroll WORKED.** Host: `setupCameraMatrices`←`runModelViewerLoop`. Escalate only
    on 2nd same host stack with abnormal. Full: Sessions 610-611.

-374. **(s609) Force6+inject recovery silence — co-primary thr11→sec2 gate; H-recov1 necessity
    SUPPORTED.** Intermittent 0×76B768 after eng+inject (class F). Free-reroll if silent
    within `RECOV_WAIT_S=100` post hangar-sel. Full: Sessions 609-610.

-373. **(s608) Post-sec2 mission HMT texture load SIGBUS — primary M3 bottleneck once recovery
    fires (1×; not chased).** Host: `packTlutEntriesRgba5551`←`loadTextureToMemory`←
    `parseHmtMaterials`←…←`mainGameLoop`. `si_addr=0x38ea20812`. **last-guest-pc=`0x800025ac`
    is STALE** — do not merge with -326. Co-symptom: `osViSetMode` width=24. 2nd occ pending.
    Full: Session 608.

-361. **(s589-s621) thr11→sec4→sec2 pipeline — thr11d_new LIVE when recovery fires
    (s619); class-D soft-skip LIVE (s619); blocked on thr12 parent by null rs_malloc
    (-385, guard landed, M1 PENDING), or pre-thr11d by recovery silence (-374; freeroll
    fixed s621), mat3inv (-375), sinfApprox NAN Abort (-386, 1×), ship re-activation
    (-376/-377), freelist 1× (-384), scene-graph (-382), readAccount (-383), FORCE_STATE6
    gate (-379; OOB base -381 CLOSED), or post-sec2 packTlut (-373). thr-11=
    `saveServiceWorker` `0x8006F2CC`; thr-12=`hudDisplayUpdateWorker` via
    `loadLevelTextureCache`. Do not raise HOLD_S past 210. Full arc: PROJECT-OVERVIEW
    §27; Sessions 589-621.**

### Closed product lineage (FULL_SYNC inject + thr pipeline setup) — do not re-open

-372..-349. **(s579-s607) Post-exit FULL_SYNC starvation → `FS_PIPE_INJECT` product line + thr11
    handoff recharacterization — ALL CLOSED as setup for -361.** Summary: post-exit plateau
    reclassified as FULL_SYNC starvation not s178 producer-stop (-349); guest E9 at phys
    `0x76DF60` side-slot (-352..-354); E7/F3/FD inject product (-355..-357); recovery cell
    `0x76B768` yields post-dual syncs (H10a, -358); FORCE_CASE6 / FORCE_STATE6 tools (-359/-370);
    thr-11 destroy co-timed with sec4 under healthy recovery (H12c, -360); beginframe `0x8000AFA0`
    guarded as `BEGINFRAME_S0_GUARD` (-365/-338; live 2/2 still PENDING, rare under force+inject);
    engagement = ACE80 camera-settle state 5→6 (-367). Durable write-up: PROJECT-OVERVIEW §27.
    Individual session detail: PORTING-STATE 579-607.

### Closed idiom-class / guard campaigns (s424–s569) — range pointers only

-348..-334. **(s549-s569) Freelist / SIBLING_PTR residual WRITE campaign — ALL FULLY CLOSED 2/2.**
    Includes -348 DIRECT residual (218 sites), -346/-345 freelist R6/ATTR, -344 packing DEFER,
    -343..-341 GUARD2-4, -340/-334 SIBLING gaps, -339/-337 emitAllocated/submitSceneNode (via
    -341). PROJECT-OVERVIEW §25-§26.

-338 / -365. **`beginFrameDLChunk` `0x8000afa0` — ROOT-CAUSED s600, GUARDED (`BEGINFRAME_S0_GUARD`);
    live 2/2 PENDING (3 scored D).** Keep LOG armed passively; do not dedicate another same-HOLD
    soak solely for beginframe. See -361 note on thr-11 race.

-335/-336 / -328..-333 / -323..-326. **Breadcrumbs filed not chased** (watch for 3rd occ before
    escalating). Notable: **-331** `heapFreeListDequeue+29152`/`0x8000d688` (2×); **-332**
    `submitSceneNodeRender+38976`/`0x8001086c` (2× weak); **-326** `do_rom_read+608`/`0x800025ac`
    (**urgent if 2nd** — do not confuse with -373's stale pc). Full: PROJECT-OVERVIEW §25-§26.

-347. **(s566/s582/s594/s595) `transformLightByType`/`0x80010134` — REFRAMED as instrumentation-
    coverage artifact, NOT escalated.** 52/2499 funcs carry `g_rs64_last_guest_pc`; unaudited
    subtree freezes caller stub. Method trap: N identical addresses ≠ N same bugs outside
    audited set.

-320. **(s508/s565/s566) `loadCutsceneAssetsByIndex+1860`/`0x800aafb8` — FULLY CLOSED 2/2.**
    `projectModelBoundsToScreen` early-exit clobbered `$s1`.

-327 / -319 / -318. **CLOSED 2/2:** DL_LIST_APPEND_DEREF (84 sites, with -334), SIBLING gap
    `0x8000B0D0`, APPEND_RDP_STATE_DL_ENTRY. PROJECT-OVERVIEW §23-§24.

-317..-311. **(s480-s569) Step-3 blanket sweep + symbolizer fix — ALL CLOSED.** ~131 range-check
    guards on derived-pointer reload idiom; `nm -n` local-symtab crash symbolizer (-311) fixed
    -310 `dladdr` artifact. Standing gotchas: hangarbay positive control; cross-check
    `last-guest-pc` not host symbol; early-guard `goto` needs full epilogue if callee-saves
    unspilled. PROJECT-OVERVIEW §19-§25; PORTING-STATE 480-569.

-310..-291. **(s454-s480) s465 frequency-scan buckets + DL_LIST/SIBLING first wave — CLOSED
    (or DEFERRED non-guard).** -305/-307/-308/-309 classify-only; -306 real SIBLING fix;
    -302 DEFERRED (integer index, multi-shape); -298..-304 / -291..-297 closed. PROJECT-OVERVIEW
    §17-§19.

-261..-290 (and -263). **(s424-453) Duplicate-symbol-name-collision arc — ALL CLOSED.**
    PROJECT-OVERVIEW §16; PORTING-STATE 424-453.

-259. **(s422) `0x800290d4` "six independent triggers" — CLOSED, not a bug** (`inflate_fast`
    clean return). PORTING-STATE 422.

-231..-249. **(s377-421) Fixup function-scope backport + M3 `-0x25A4` resumption + 784-function
    `main_overlay.txt` phantom relocation — ALL CLOSED.** PROJECT-OVERVIEW §13-§15.

-230..-14 (excluding -20). **Eleven closed investigation lineages, s99-s376 — all CLOSED.**
    M5 audio de-stubbing (-160..-230, §9-§12) plus ten earlier guard-gap chases. PROJECT-OVERVIEW
    §9-§12; PORTING-STATE 99-376.

### Standing / open non-pipeline items

-20. **Regen-pipeline reliability bug (s120, intermittent).** `N64Recomp` skips rewriting existing
    `funcs_*.c`; delete all before every regen is mandatory but residual intermittency unknown.
    **Standing rule**: audit patch report for unexpected counts after every `fixup_game_funcs.py`.
    PORTING-STATE 120/121/126.

-11. **`advancePlayerAnimationPhase` SIGBUS: PARKED s89, RECURRED s424, GUARDED s425** (see -261).

-10/-9. **Metal-shader-compiler SIGSEGV** (s83, one data point). **s83 spline div0 guard**: 0/5
    fires; real fix by inspection, no same-run positive control yet.

-8. **`frameStartReset` SIGBUS** — 3 occurrences (s85/s108/s156); no located faulting insn.

-7. **M3 hangar-exit → mission-entry (DoD gate): OPEN.** Exit+cutscene CONFIRMED s577;
    FULL_SYNC inject product-fixed; force6 engagement CONFIRMED s606 and **live-writes real
    hangar state s617** (-381 CLOSED); s608 first force-path sec2 after thr11d when recovery
    fires; **s619 thr11d_new + class-D LIVE** then dies in -385 null-malloc (guard s620;
    M1 live-verify PENDING s621). Active residuals: -386..-373 / -361 / -379. Tools still
    default OFF.

-6. **(s53→s399) M4 `[missing-func]` addresses: DONE, CLOSED s399.** PORTING-STATE 399.

-5. Past first sustained mission hold: expect new failure classes (mission overlay DMA,
    missing-func/UJ, new VI phase, overlays 12/44, texture corruption). Each is its own unit.

-3. **Sibling-repo housekeeping (not autonomous):** `~/Documents/Tools/rogue_squadron64`
    carries uncommitted symbol-file edits. Ask user before committing there.

-2/-1. **Band-row coverage history** (settled s41-49). **GPU->CPU present PNG** via
    `NativeTarget::copyToRAM` — convenience, not a blocker.

**Done, do not redo:** optimising the ucode vector path (s38: `-O0`→`-O2` gave 41x); the
ucode-performance→DL-submission-collapse→RDP-census→draw-loss chain (s33-s37); coverage
attribution/format-mismatch (`LOG_BBOX`/`LOG_UPLOAD`); the s27-s31 I4-decode line.

## Regeneration and build pipeline

Game functions (s1) — all four steps, in order:

1. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
2. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
3. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — **required**, re-applies hand-edits
   idempotently: `$zero` writes commented (~2700); `fake_func_*` → `__builtin_trap()`; cross-
   function branch traps; audio-engine gate stores → 0 in `funcs_23.c` for
   `setDisplayMode`/`reapplyDisplayMode` only (`initMusyXEngine` site reversed s302); `jr $t9`
   in `convertMat3x4ToN64Mtx` → plain `return`; `musyxKeyOnVoice` break 6/7 → early return;
   `evalCubicSplineAtTime` div0 guard (`[spline-div0]`).
4. `cd build && cmake --build . -j8`

RSP ucode (only when a ucode toml changes): `~/Documents/Tools/N64Recomp/build/RSPRecomp` on
`factor5_rsp.toml` / `factor5_boot_rsp.toml` → `build/factor5_ucode/*.c`, then
`tools/fixup_factor5_ucode.py`. **s47: before the fixup, also run
`python3 tools/make_clip_composite.py` + RSPRecomp on `factor5_rsp_ovl4.toml`**. `factor5b_rsp.toml`
is the **MusyX audio** ucode; stays in the build as a never-called artifact (s5).

Standing warnings:
- `lib/N64ModernRuntime` and `lib/rt64` carry **uncommitted working-tree patches** — never
  `git submodule update --force`. Mirror via `submodule-patches/export.sh`.
- ROM must sit next to the executable in `build/`; otherwise silent "place your ROM" dead VI (s8).
- Hand-edited diagnostics in `build/factor5_ucode/*.c` / `RecompiledFuncs` die on regen — put them
  in fixup scripts.
- settings.json Bash allowlist matches FIRST WORD: prefix env assignments with `env` (s44).
- Harness: `clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m`;
  capture with `tools/probe.sh` / `tools/regress.sh`. Kill with SIGKILL, not SIGTERM (s9).
  Python decoders: `scratch/venv/bin/python` (s18).
- `regress.sh` must not write probe images as `.*` hidden names (s26).
- ~~Screen Recording permission intermittent~~ — overturned s32: wrong window id, not permission.
- `winctl activate` ignored while another app holds focus — use `probe.sh`/`regress.sh`
  `raise_game()` (System Events `set frontmost`) instead (s45).

## Overturned conclusions — do not act on these

Full list (11+ entries spanning s2-s422, each with why it was believable and what refuted it),
plus the early-era dead-ends list: `docs/PROJECT-OVERVIEW.md` §26. Load-bearing for active work:
- **(s400-421→s422)** `0x800290d4` "six independent triggers" is `inflate_fast`'s clean return.
- **(M5-AUDIO-PLAN.md §4→s371)** host audio `queue_samples`→`SDL_QueueAudio` unit-mismatch, fixed s371.
- **(s578→s579)** post-exit `rdpFs` plateau is **not** the s178 graphics-task-submission stall —
  s178 is `stalled=1 pairs=0` + producer stop; s577 post-exit keeps submitting GFX with present
  FIRE pairs=4 while only FULL_SYNC dies (item -349).

### Dead ends — labelled as such in the log, do not retry

Full list (early ucode/DMA/overlay hacks, s2b-s91) migrated to `docs/PROJECT-OVERVIEW.md` §26.

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here:
- §4.1 instruments-that-lie; §4.2 attribution errors; §4.3 cross-run comparison on animating
  scenes (gate on `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1`); §4.6 missing protocol events.
- Other instrument traps: PROJECT-OVERVIEW §8.
- **crash-signature blindness (s344)**: soak "any `[CRASH]`" is not evidence for a SPECIFIC target
  unless `last-guest-pc`/`pc-symbol` matches — ~20+ independent crash families. Also: grepping
  game `run.log` for driver `[keys]` is wrong (launcher log only). Item -200.
- **repeated-`last-guest-pc` is not repeated-bug proof outside the audited set (s595)**: only
  ~52/2499 functions track `g_rs64_last_guest_pc`. N identical addresses can be N different
  crashes sharing one instrumented caller. Check audited set before "Nth occurrence" escalation.
  Item -347.
