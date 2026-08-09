# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Twenty-six passes
   so far (per-pass targets in git log; PROJECT-OVERVIEW §16-§26 hold the most recent arcs) kept the
   file oscillating around the cap as new session detail accrues. 35 KB remains a stretch target, not a
   hard floor -- the "Current truth" env-var/timeline prose and the Regeneration section's Standing
   warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (PROJECT-OVERVIEW §10-§12). Next
   M5 work needs a genuinely new lead (last checked s570, zero new leads, due again s573+).
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. Every bucket from
   the s465/s477 frequency scans has a disposition (items -298..-309, PROJECT-OVERVIEW §18-§19).
   Items -312..-322 (s481-518, the `DL_LIST_APPEND_GUARD`→`HEAPLISTDEQ_ATTR_WRITE_GUARD` lineage) are
   all fully CLOSED — PROJECT-OVERVIEW §20-§25. **Item -317 freelist WRITE campaign CLOSED s564
   (131/131 + residual walk/attr gaps -341..-345).** **Item -320 FULLY CLOSED 2/2 s566**
   (safe mini-epilogue). **Item -346 FULLY CLOSED 2/2 s567** (R6 r3-base gap at `0x8000D6D0`;
   s567 confirm hangarbay n=2700 full 300s rc=0, 0 r6 fires, no 0x8000d6d0 crash).
   **Item -348 FULLY CLOSED 2/2 s569** (SIBLING_PTR DIRECT residual same-base gap class: 218
   sites; freelist R/ATTR residual EMPTY under dual scan — DIRECT residual campaign exhausted).

-312..-318. **(s481-507) The `DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`/`AUDIO_SLOT_ACTIVE_GUARD`/
    `APPEND_RDP_STATE_DL_ENTRY_GUARD` "grep-verified unique site" lineage — seven items, all fully
    CLOSED except -317 step 3** (see item -317 below). Full derivation: `docs/PROJECT-OVERVIEW.md` §20-§23.

## Current truth (established by session 295; unchanged, reviewed through s575)

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
OVERTURNED s150; **s573 H1 CONFIRMED** (no mission overlay); **s575 REFUTED H-exit5** — leave
Start advances hangar case 3→5 same frame; case 5 then polls for a *second* Start the driver never
sends (item -7 H-exit6). Primary DoD gate is hangar-exit →
mission-entry state machine (item -7), not stick input. *Done when:* 60s of in-mission rendering,
craft visibly responds to synthetic input, stability counters 0, phase timeline covers the mission.

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
a range pointer. Highest allocated so far: -348. The next NEW item takes -349.

-348. **(s568/s569) SIBLING_PTR DIRECT residual same-base gap class — FIXED and FULLY CLOSED 2/2
    (s569).** Systematic audit of the `-334/-340/-345/-346` model across all applied freelist/
    sibling guards. Dual offline scan (focus-family seeds + all-PATCH MEM_W seeds): **140 unique
    NEEDS_GUARD**, all **SIBLING_PTR** (102 TIGHT, 92 classic 0X0→0X4); freelist R-numbered + ATTR
    residual **EMPTY**; packing not reopened. Extended `SIBLING_PTR_WRITE_GUARD` by **218 sites**
    (w1=159 TIGHT+delay-dups, w2=52 multi-field tails, w3=7 second-order; float stores at
    `0x80017264`/`0x80017268` packing-adjacent DEFERRED). **1st (s568):** hangarbay n=2900, full
    ~300s rc=0, 0 sibling-ptr-write fires. **2nd (s569 retry after WEAK item-306 discard of queued
    confirm):** hangarbay n=3000, full ~300s rc=0, 0 fires, 0 CRASH — CLEAN. DIRECT residual
    same-base campaign for freelist/sibling write-guard lineage **exhausted**.

-347. **(s566) Single-occurrence breadcrumb, filed not chased**, from item -346's 1st live-verify.
    `transformSceneLights+2456`/`last-guest-pc=0x80010134` (`hangarbay-entry n=2600`). Guest
    `0x80010134` is the *caller* `submitSceneNodeRender` JAL delay-slot `sw $v0,0x10($sp)` before
    `jal transformSceneLights` (same caller-PC-vs-host-offset pattern as item -320). Host fault
    is inside the callee at +2456. Watch for recurrence before source-tracing the callee body.

-346. **(s565/s566/s567) `heapFreeListDequeue` residual r3-base write at `0x8000D6D0` — FIXED
    and FULLY CLOSED 2/2 (s567).** DIRECT gap before existing `HEAP_FREE_LIST_DEQUEUE_R2_GUARD`
    site=`0x8000D6D4`: both delay-slot copies of `sw $v0, 0x0($v1)` (`MEM_W(0X0, ctx->r3)=ctx->r2`)
    were unguarded. Same gap model as -334/-340/-345. Family `HEAP_FREE_LIST_DEQUEUE_R6_GUARD`
    (env `ROGUESQ_LOG_HEAP_FREE_LIST_DEQUEUE_R6_GUARD`). **1st (s566):** hangarbay n=2600, 0 r6
    fires, no 0x8000d6d0 crash; died on item -347. **2nd (s567 retry after WEAK item-306 discard):**
    hangarbay n=2700, full ~300s rc=0, 0 r6 fires, 0 CRASH — CLEAN.

-320. **(s508/s565/s566) `loadCutsceneAssetsByIndex+1860`/`last-guest-pc=0x800aafb8` — ROOT-CAUSED
    AND FULLY CLOSED 2/2 (s566).** ≥4 hangarbay-controlled hits pre-fix. **Mechanism:** guest
    `0x800AAFB8` is the *caller's* JAL delay-slot nop in `runHangarSelectionFrame`. Host `+1860` =
    `L_800A92F0` `lw $v0,-0x25A4($s1)`. `$s1` clobbered by `projectModelBoundsToScreen` guard1/guard2
    early-exit `goto L_80066204` before those regs were spilled. Fix: safe mini-epilogue. **1st
    (s565):** hangarbay n=2600, 0 guard fires, no +1860 crash. **2nd (s566 fold):** hangarbay n=2600,
    full ~300s rc=0, 0 fires, no +1860 crash — CLEAN. Bonus same-run positive engagement on the
    item -346 1st verify: `project-model-bounds-guard2` n=0..179 (fix catches bad args without
    clobbering caller `$s1`).

-345. **(s562/s564) `heapFreeListDequeue` DIRECT gap after item -322 `HEAPLISTDEQ_ATTR_WRITE_GUARD`
    site=`0x8000D92C` — FIXED and FULLY CLOSED 2/2 (s564).** Same-run root cause (s562): guard fired
    `n=0 bad_ptr=0x8` then crash at `last-guest-pc=0x8000d944` (`MEM_W(0X4, r3)` after r3 reloaded
    from the same stack slot `0x3C` that fed the guarded r2 write). Same gap model as items
    -334/-340. Extended family to **7 residual sites** sharing env
    `ROGUESQ_LOG_HEAPLISTDEQ_ATTR_WRITE_GUARD`: `0x8000D944`, `0x8000D94C`, `0x8000D964` (x2 recomp
    delay-slot), `0x8000D978`, `0x8000D980`, `0x8000D994` (bit-0x10 path + L_8000D968 alt). Skip
    safe. **1st (s563):** hangarbay n=2600, 0 fires, no crash at 0x8000D944. **2nd (s564 fold):**
    hangarbay n=2700, 0 fires; crash `coalesceFreeHeapBlocks+3192`/`0x8000241c` (s354-366 noise) —
    CLEAN.

-344. **(s562/s563) Non-r3 freelist dual-walk residual (s560 r3-only gap) + freelist simple-walk —
    FIXED and FULLY CLOSED 2/2 (s563).** Residual freelist-shaped NONE: `allocateDisplayListBuffer`
    `0x80007DA8` r4 + `renderLitMeshFaceGroup` `0x80013EEC` r4 + `countDisplayListChunks` simple-walk
    `0x80007CC8`. GUARD2+3+4 x2 + `FREELIST_SIMPLE_WALK_GUARD` x1. Packing DEFERRED (21/22). **1st:**
    hangarbay n=2600. **2nd (s563 fold):** hangarbay n=2900, 0 fires; crash `coalesceFreeHeapBlocks`
    `0x800023b0` unrelated — CLEAN.

-343. **(s561/s562) Residual freelist initial-deref GUARD2 (post-null-check `lw $v0, 0x0($aN)`) —
    FIXED and FULLY CLOSED 2/2 (s562).** 92 sites (`ROGUESQ_LOG_ALLOC_TAIL_GUARD2`). 1st: hangarbay
    n=2700 full 300s 0 fires. 2nd (s562 fold): hangarbay n=2600, 0 fires, crash on catalogued
    `tickWrappingTimerAccumulatorList` div0 `0x80054744` — CLEAN.

-342. **(s560/s563) Residual freelist-walk GUARD3+GUARD4 (post-findAndUnlink walk-to-tail) — FIXED
    and FULLY CLOSED 2/2 (s563).** GUARD3 x94 + GUARD4 x92. 1st: hangarbay n=2600. 2nd after 3
    consecutive weak item-306 deaths: hangarbay n=2900, full ~300s rc=0, 0 fires — CLEAN.

-341. **(s559/s561) Freelist-walk GUARD4 systematic audit (item -339 shape) — FIXED and FULLY
    CLOSED 2/2 (s561).** GUARD3-without-GUARD4 gap at 16 sites (`emitAllocatedDLCommand` x3
    incl -339, `heapFreeListDequeue` x4, `submitSceneNodeRender` x9 incl -337). Env:
    `ROGUESQ_LOG_EMIT_DL_GUARD4` / `HEAPLISTDEQ_GUARD4` / `SCENE_NODE_LIST_GUARD4`. 1st: hangarbay
    n=2900, full ~300s rc=0, 0 fires. s560 confirm WEAK (item -306); s561 retry CLEAN hangarbay
    n=2900, full ~300s rc=0, 0 fires — **CLOSED 2/2** (covers -339/-337).

-340. **(s557/s558) `SIBLING_PTR_WRITE_GUARD` site=`0x80010B4C` (`submitSceneNodeRender`) — FIXED
    and FULLY CLOSED 2/2 (s558).** DIRECT gap after existing site `0x80010B48`: pre-crash fire
    `bad_ptr=0x18`, crash at `0x80010B4C` = bad_ptr+4 (same model as item -334). New family site
    (reg r3, off 0X4). s558 confirm: hangarbay n=3000, full ~300s no-crash rc=0, 0 fires on residual
    batch-2 tags and 0 sibling-ptr-write fires — intermittent corruption, closed 2/2.

-339. **(s556) `emitAllocatedDLCommand+13216`/`last-guest-pc=0x800088ec` — ROOT-CAUSED AND FIXED
    s559 as part of item -341 freelist-walk GUARD4 (site `0x800088EC`); FULLY CLOSED 2/2 with
    item -341 s561.**

-338. **(s554, s572, s574 — 3 occurrences) `beginFrameDLChunk`/`last-guest-pc=0x8000afa0`
    breadcrumb, filed not chased.** s554 hangarbay: `+37740` at n=2600. **s572 leave-hold:**
    `+46800` at hold-iter ~12. **s574 leave-gates:** `+46800` at hold-iter 1 (same guest PC).
    Confidence **moderate→high**. Still do not open a reactive leave-path chase until hangar
    exit works (item -7); 3rd occ is enough to prioritize after the state-machine gate.

-337. **(s551) `submitSceneNodeRender+69192`/`last-guest-pc=0x80010df4` — ROOT-CAUSED AND FIXED
    s559 as part of item -341 freelist-walk GUARD4 (site `0x80010DF4`); FULLY CLOSED 2/2 with
    item -341 s561.**

-335/-336. **(s550) Two more single-occurrence background-noise breadcrumbs, filed not chased**,
    surfaced by the two s549 confirm soaks folded in this session. **-335**
    `emitAllocatedDLCommand+1960`/`last-guest-pc=0x800086ec` (from
    `s549_five_tied_guards_confirm_retry2`, its 4th and finally-valid attempt, `hangarbay-entry n=31`).
    **-336** `findLookupEntryByKey+2212`/`last-guest-pc=0x800ac914` (from
    `s549_sibling_ptr_write_gap_confirm`, `hangarbay-entry n=31`) — same symbol+offset as item -325's
    `findLookupEntryByKey+2212`/`0x800ad0dc` but a DIFFERENT `last-guest-pc` (the family's own
    `pc-symbol`-instability gotcha, s541/PROJECT-OVERVIEW §25) — not a 2nd occurrence of -325, a new
    single-occurrence signature. Watch both for recurrence before escalating.

-334. **(s549) `SIBLING_PTR_WRITE_GUARD` site=`0x80010DCC` (`submitSceneNodeRender`) and item -327's
    root-cause fix (`DL_LIST_APPEND_DEREF_GUARD`, 84 sites) — FIXED and FULLY CLOSED 2/2 (s550).**
    Found via DIRECT mechanistic correlation (not a blind re-scan): the item -317 step 3 guards-58-61
    2nd confirm crashed at `last-guest-pc=0x80010DCC` while the SAME run's pre-existing
    `sibling-ptr-write-guard site=0x80010DC4` fired (`n=0`, its first-ever fire across the whole
    121-site family) with `bad_ptr=0x48830D10` one instruction earlier — `bad_ptr+4` matches the
    crash's own fault address modulo the RDRAM host-mapping offset. Same shape as item -319's own gap:
    an unguarded write immediately after an existing guard, reusing the SAME already-flagged-bad
    register (`ctx->r5`, the delay-slot instruction after `0x80010DC4`'s `bne`, duplicated x2 by the
    recompiler for taken/fallthrough paths — same non-branch-likely duplication `FREELIST_NEXT_GUARD`
    hit with `bnel`, s441). Fixed as 2 new entries (122nd/123rd) in the family's
    `_SIBLING_PTR_WRITE_SITES` list, sharing the family's existing env var. **Verifying the fix alone
    caught the NEW guard itself firing** (`n=0`, `bad_ptr=0x810C747B`, matching the value the
    pre-existing `0x80010DC4` guard fired with one instruction earlier in the SAME run — a 2nd,
    independent confirmed catch), then the run crashed downstream at item -327's own address instead —
    leading directly to item -327's root-cause fix. **2nd independent confirm (s550 fold-in): clean**
    (`hangarbay-entry n=31`, 0 fires on either `sibling-ptr-write-guard site=0x80010DCC` or
    `dl-list-append-deref-guard` any of 84 sites; crashed at 132.4s on the item -336 breadcrumb above,
    unrelated) — **both FULLY CLOSED 2/2**, the corruption event is intermittent as every guard in this
    campaign has shown. Full derivation: `PORTING-STATE.md` Sessions 549-550.

-328..-333. **Six more single/double-occurrence breadcrumbs surfaced by item -317 step 3's s526-546
    live-verifies, all filed not chased.** Full detail: `docs/PROJECT-OVERVIEW.md` §25-§26.
    -328 (s528) `submitSceneNodeRender+69820`/`0x80010ebc`, distinct from -327's `+67668`/`0x80010e6c`.
    -329 (s529) `rebuildActiveDisplayObjectList+660`/`0x800ab060`, distinct from the item -317 R5
    `+540` breadcrumb. -330 (s536/s537, 2 occurrences back-to-back, weak corroboration per the
    boring-first prior — same binary/script/adjacent wall-clock) `heapFreeListInsert+72`/
    `0x800220b8`, distinct from -324's same-symbol/different-PC breadcrumb. -331 (s537,
    `local-symtab`-tagged, in the free-list-pop region, before every already-guarded address in
    `heapFreeListDequeue`) `heapFreeListDequeue+29152`/`0x8000d688`. **-332** (s539 weak `n=5`,
    recurred s544 with a strong `n=2600` control — confidence upgraded low→moderate, watch for a 3rd
    before source-tracing) `submitSceneNodeRender+38976`/`0x8001086c`. **-333** (s546,
    `local-symtab`-tagged, 16 bytes from -331's address but a distinct guest PC — treat the
    free-list-pop region itself as suspicious if either recurs or a third nearby address appears)
    `findAndUnlinkSmallestEntry+356`/`0x8000d698`. Watch all six for recurrence before escalating.

-320..-327. **Eight breadcrumbs (s508-524); -320 FULLY CLOSED 2/2 s566 (see top entry); -321
    REFUTED; -322 FIXED+CLOSED (+ residual -345); -327 FIXED+CLOSED with -334; -323..-326 watch.** -323
    (s514) `beginFrameDLChunk+27456`/`0x8000ae40`. -324 (s521) `heapFreeListInsert+72`/`0x80015544`.
    -325 (s522) `findLookupEntryByKey+2212`/`0x800ad0dc`. **-326** (s524) `do_rom_read+608`/
    `0x800025ac` — **if a 2nd occ appears, urgent**.

-319. **(s503/s505/s519, 3 occurrences) `beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0` — FIXED
    s520 (`SIBLING_PTR_WRITE_GUARD` site=`0x8000B0D0`, 121st site in that family), FULLY CLOSED 2/2
    s521.** A genuine gap in the original s459 sweep: an unguarded write sandwiched between two
    already-guarded `-0x23A8` sibling sites, not covered by the step-3 tracer (different reload idiom,
    so this fix doesn't subsume its open tiers). Full mechanism: PROJECT-OVERVIEW §24.

-318. **(s501-507) `appendRdpStateDl+144` crash — FIXED and FULLY CLOSED 2/2
    (`APPEND_RDP_STATE_DL_ENTRY_GUARD`).** All 6 call sites reload a sibling global with no range check
    and pass it as a write-cursor argument the callee dereferences unconditionally — outside the
    existing 119-site `SIBLING_PTR_WRITE_GUARD` audit's scope. Fixed by range-checking at function
    entry, skipping the body if invalid. CLOSED 2/2 s507 after an s506 inconclusive retry. Mechanism:
    `docs/PROJECT-OVERVIEW.md` §23.

-317. **(s490-558) Step 3 of the `-312..-316` lineage: a ~150-location blanket sweep of the same
    derived-pointer reload idiom across `funcs_3.c`/`funcs_4.c` — 131 guards fixed, ALL 131 FULLY
    CLOSED 2/2 as of s558.** Steps 1 (`heapFreeListDequeue` as a whole function) and 2
    (`buildOrientedFaceGeometry` as a whole function) are separately FULLY CLOSED 2/2 — note step 3
    has since ALSO landed R-numbered guards inside these same two functions (and `heapFreeListInsert`),
    a naming coincidence, not a re-opening of steps 1/2. Step 3's tracer
    (`scratch/agent/s494_item317_step3_tracer.py`) found ~448 raw reload sites deduping to ~150
    candidate guard placements; every freelist WRITE fix shares one shape (null check gates one arm,
    non-null fallthrough has no `0x80000000`-`0x80800000` range check before write-through deref —
    skip on invalid is safe). Classic r2/0X4: 115/115. Residual free-list-node rN/0X0: 16/16
    (116-131). Full guard table: `docs/PROJECT-OVERVIEW.md` §22-§25.
    **s558–s564:** freelist WRITE campaign CLOSED (details under -341..-345). **s565–s567:** item
    -320 root-caused to `projectModelBoundsToScreen` early-exit s-reg clobber and CLOSED 2/2; item
    -346 residual r3-base write at `0x8000D6D0` FIXED+CLOSED 2/2 (R6). **s568–s569:** SIBLING_PTR
    DIRECT residual same-base class (item -348) 218 sites FIXED+CLOSED 2/2; freelist R/ATTR residual
    EMPTY under dual scan — DIRECT residual campaign exhausted. **Standing gotchas** (full:
    PROJECT-OVERVIEW §22-§25): hangarbay positive control (s536); cross-check `last-guest-pc` not
    host symbol (s541); weak item -306 early deaths discard+retry; early-guard `goto` full epilogue
    only if ALL callee-saves already spilled (s565); breadcrumb occ counts re-tally SOAK-RESULTS
    (s564). Raw detail: `PORTING-STATE.md` Sessions 490-569.

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
-7. **M3 — hangar-exit → mission-entry (M3 DoD gate): OPEN — H1 CONFIRMED s573; s575
    REFUTED H-exit5 (stuck case 3).** Recipe `PROBE_MODE=start_only HOLD_S=20` (single leave
    Start) via `run_mission_keys.sh`. **s574:** leave Start hits case-3 site `0x800AC0F0`;
    misread AC8C0 n=0..4 as "never case 5". **s575 instrumented leave (hangarbay n=900;
    hangar-state + state-write + case5-entry always-on):**
    - Same-frame chain: `a_start=1` @ AC0F0 → `[state-write] site=0x800AC1C4 old=3 new=5` →
      `[hangar-state] state=5` → `[case5-entry] n=0..213` (214 frames in case 5).
    - State path: 0→1 (ABB90) → 3 (ABCD0) → **5 (AC1C4)**; **no revert**.
    - Case 5 button poll AC8C0: n≥200 samples, **0** `a_start=1` (driver sends only one Start).
    - Still **0** `[hangar-sel]`, **0** non-sentinel frame-ret, **0** graceful-menu.
    - **H-exit5 / 5a / 5b REFUTED.** s574 "case 5 never entered" was a rate-limit misread of
      post-leave AC8C0 empty polls. **Primary: H-exit6** — case 5 needs a second Start for
      `isPlayerShipActive`+`hangar-sel` path; single-Start leave never delivers it. **H-exit1**
      (ship-active ret=1 blocks write) now testable once second Start arrives. ship-active early
      samples show `ship=0x8015FD90 ret=1` (from non-case5 callers).
    **Next:** double-Start leave (case3 advance + case5 confirm). Do not chase -338. Stick-hold
    secondary until hangar exits.
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
plus the early-era dead-ends list, migrated to `docs/PROJECT-OVERVIEW.md` §26. The two entries
still load-bearing for active work: **(s400-421->s422)** the `0x800290d4` "six independent
triggers" claim is `inflate_fast`'s own clean return, a sparse shared breadcrumb across unrelated
crash functions, not a real corruption sink — this recurs constantly as background noise across
item -317's soaks (PORTING-STATE 422). **(M5-AUDIO-PLAN.md §4->s371)** the host audio bridge had a
silent `queue_samples`→`SDL_QueueAudio` `*sizeof(int16_t)` unit-mismatch bug dropping half of every
PCM buffer, fixed s371 (`src/main/main.cpp`).

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
