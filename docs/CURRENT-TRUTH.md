# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Twenty-two passes
   so far (s295-330 x5, s346, s355, s364, s371, s380, s391, s398, s409, s429, s438, s444, s451, s461,
   s469, s479, s486, s492, s504) kept the file oscillating around the cap as new session detail
   accrues — full per-pass migration targets in git log; PROJECT-OVERVIEW §16-§22 hold the most recent
   seven arcs. 35 KB remains a stretch target, not a hard floor -- the "Current truth" env-var/timeline
   prose and the Regeneration section's Standing warnings stay intact deliberately; both are used every
   iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (full arc: PROJECT-OVERVIEW
   §10-§12). Next M5 work needs a genuinely new lead (**last checked s514 — zero new leads (grepped
   s506-s513's soak logs for any `musyx`/`audio-slot`/`audio-voice` signature, none found), cadence
   reset to s514, due again once 3+ sessions have passed, i.e. s517+**).
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. Every bucket
   surfaced by the s465/s477 frequency scans has a disposition (items -298..-309, PROJECT-OVERVIEW
   §18-§19). Items -312..-316 (s481-490, the `DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`/
   `AUDIO_SLOT_ACTIVE_GUARD`/`DL_ALLOC_PROPAGATION_GUARD` sibling-site-gap lineage) are all fully
   CLOSED — PROJECT-OVERVIEW §20-§21. **Item -317 (that lineage's step 3, a ~150-location blanket
   sweep) status as of s514: 17 of ~150 leads fixed, 16 fully CLOSED 2/2
   (`RENDER_LIT_MESH_R5_GUARD` and `RENDER_LIT_MESH_R6_GUARD` both closed this session — R5's retried
   2nd confirm and R6's 2nd confirm both landed clean, valid `hangarbay-entry` positive control on
   each, crash on an unrelated already-catalogued signature in each case), 1 (`RENDER_LIT_MESH_R7_GUARD`,
   fixed s514) 1st-live-verify-clean-on-the-guard with a 2nd confirm queued** (see item -317 below for
   the current tier and next pick; full campaign detail: PROJECT-OVERVIEW §22). Item -318
   (`appendRdpStateDl+144`) is FULLY CLOSED 2/2 (`APPEND_RDP_STATE_DL_ENTRY_GUARD`, fixed s505, 2nd
   confirm clean s507 after a s506 retry). Item -319 (`beginFrameDLChunk+40536`) still has only 2
   independent occurrences (s503, s505); none of this session's confirm/live-verify soaks crashed on
   it either, so it stays below the 3rd-occurrence threshold — s506's fresh tracer scan found a
   ready-made list of candidate guard sites inside `beginFrameDLChunk` itself if/when that thread
   opens (see item -317 below). Item -320 (`loadCutsceneAssetsByIndex+1860`/`last-guest-pc=0x800aafb8`)
   is still a single-occurrence breadcrumb from R2H's own 2nd confirm — watch for recurrence, not yet
   a dedicated thread. Item -321 (`menuOverlayInit+3648`/`last-guest-pc=0x800ab1c4`, filed s510) is
   still a single-occurrence breadcrumb, host-symbol-offset-identical to the historically-CLOSED item
   -266/-267 chain but with a different `last-guest-pc` — flagged as a *possible* recurrence, not
   concluded (see item -321 below), watch for a 2nd occurrence with a matching `last-guest-pc` before
   escalating. Item -322 (`heapFreeListDequeue`/`last-guest-pc=0x8000d92c`, filed s512) still has only
   2 independent occurrences (s457, s512); no soak this session crashed on it. **Item -323 (NEW,
   s514)**: `RENDER_LIT_MESH_R7_GUARD`'s 1st live-verify crashed on a previously uncatalogued
   signature, `pc-symbol=beginFrameDLChunk+27456`/`last-guest-pc=0x8000ae40` — inside the SAME
   function item -319 tracks but at a DIFFERENT `last-guest-pc` than item -319's own `0x8000b0d0`, so
   NOT the same crash; single occurrence, watch for a 2nd before opening a dedicated thread (see item
   -323 below).

-312..-317. **(s481-503) The `DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`/`AUDIO_SLOT_ACTIVE_GUARD`
    "grep-verified unique site" lineage — six items, all fully CLOSED except -317 step 3** (open scope
    and methodology lesson: see item -317 below). Full derivation: `docs/PROJECT-OVERVIEW.md` §20-§22.

## Current truth (established by session 295; unchanged, reviewed through s486)

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

Menu state machine (s48, extended through s75; hold/crash triage s76-s114): title —start→ SELECT
GAME —start→ war room / SELECT LEVEL —start→ **AVAILABLE CRAFT** (war-room craft holograms; `a` does
**not** show a level description card, s61–s69). With process alive 65s+ post-`a` (s72/s73): black
~5s → capital-ship flash → stable **SELECT YOUR CRAFT** (hangar pad + full X-wing; `a` no-ops, s74;
camera orbits). A single Start leaves the menu — **OVERTURNED s150 (see Overturned conclusions)**:
same craft-select scene under a corrupting camera move, not a new environment; what actually leaves
SELECT YOUR CRAFT is reopened as unanswered. VI stays on the 0x6AB400/0x656400 pair throughout —
**origin cannot identify these menu scenes**, only phases (the round level-select war room and
SELECT LEVEL share 0x6AB400; a separate outdoor scene at 0x690400 does too for its phase). ~20 crash
classes closed getting through this chase (mechanisms/tags: `docs/PROJECT-OVERVIEW.md` §3/§7/§9).

Remaining visual defects, all parked as M4 except where noted: outdoor 512 zero-shade masked not
fixed (`baseFixed = −32768` root cause unknown, s19/s20); S=0 triangles in the 640 attribution phase,
uninvestigated (s18); `[dpc-behind]` ring-wrap drops with `DPC_WRAP` off (not a black-screen cause,
s11). Hangar floor multi-hue band, hangar dimness, and the post-leave black/SIGBUS chain are all
FIXED (M1 closed s48; `SHADE_WRAP` s25; ImemOverrun s69 + depth-writeback SIGBUS s72) — mechanisms in
`docs/PROJECT-OVERVIEW.md` §3.

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep. 0
`UnhandledJumpTarget`, 0 `[defer-drop]`, 0 `[dmem-race]`, 0 asserts. `[missing-func]` in the undriven
outdoor-512 stretch: s49's original 3 addresses **FIXED and closed s399** (item -6); s399 also found
~801-803 further phantom overlay-range functions in `main_overlay.txt`; s400+s402+s403+s405+s406+s407+
s408+s410+s411+s412+s413+s415+s416+s417+s419+s420 have fixed 727 of the corrected 778-candidate count
(71 remain per a fresh regen post-s420, 58 actionable, 9 permanently excluded as known-bad, 4
known-skip, item -249). s411
resolved the long-standing `[missing-func] 0x800FB9E4` baseline (was `endMissionCleanup`, a
phantom-overlay victim of this same family) — every clean live-verify from here should show 0
`[missing-func]` lines, not 1. Post-`a` process now soaks well past 65s without death.

## Goal stack — work strictly top-down

A milestone is done only when its definition-of-done is met **and documented here**. The
autonomous loop (`tools/agent/loop.sh`, contract in `tools/agent/ITERATION.md`) always draws its
work unit from the top open milestone, so this ladder is what keeps it from idling.

**M1 — hangar band root cause and fix: DONE (s48).** Mechanism and fix recipe:
`docs/PROJECT-OVERVIEW.md` §3 ("Fixing the hangar band"). Full detail: PORTING-STATE s45–s48.

**M2 — post-clip-fix regression sweep: DONE (s49).** New stability baseline: 1138 tasks,
fanjal=9448, 0 cull-census-identity violations (scales with capture window, not a fixed constant).
Stability 0 except 3 gracefully-stubbed `[missing-func]` addresses in the undriven outdoor stretch,
never soaked before — parked as M4 (identified s53, fixed s54, runtime check outstanding — see
step 2 below). Full detail: PORTING-STATE s49.

**M3 — first gameplay: OPENED (s50), still open.** AVAILABLE CRAFT and SELECT YOUR CRAFT are both
reachable and stable; ~20 crash classes closed s50-s294 (mechanisms: `docs/PROJECT-OVERVIEW.md` §3
arc + §9 closed lineages; per-class catalog: §7). "Single Start leaves SELECT YOUR CRAFT into
hangar-flight" (s75) was **OVERTURNED s150** — same craft-select scene under a corrupting camera
move; what a leave-key actually leads to is unresolved. **s423 first-look DoD attempt** stalled at
SELECT GAME for 134s (documented indefinite-wait behavior) before advancing to the war-room screen,
which then crashed ~1.3s later — the crash that opened the still-active item -261→-267 chain (item -262
onward, see Next steps). *Done when:* 60s of in-mission rendering, craft visibly responds to synthetic
input, stability counters 0, phase timeline covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it. The 3 `[missing-func]` addresses, the `main_overlay.txt` phantom-overlay-function
family, and its `0x800290d4` clustering are all **DONE/CLOSED** (items -6/-249/-259).

**M5 — audio de-stubbing: DONE and fully CLOSED (s297-376).** No outstanding thread; next M5 work
needs a genuinely new lead. Full arc: `docs/PROJECT-OVERVIEW.md` §9-§12.

## Next steps, in order of expected value (s295)

Numbering convention (fixed s295): items are numbered highest-magnitude-negative (top,
newest/highest priority) counting up to -1 (bottom, oldest); never renumbered when compacted into
a range pointer. Highest allocated so far: -323. The next NEW item takes -324.

-323. **(s514, NEW) `beginFrameDLChunk+27456`/`last-guest-pc=0x8000ae40` crash — single occurrence,
    watch for a 2nd before opening a dedicated thread.** Surfaced by `RENDER_LIT_MESH_R7_GUARD`'s 1st
    live-verify (funcs_4.c:15620/`0x80014140`, `renderLitMeshFaceGroup`, item -317 step 3's 17th fix),
    0 fires on that guard itself, `hangarbay-entry n=2600` positive control, 4 benign init-time
    n=0/`ra=0x00000000`-class co-fires (`generic-cache-guard`, `dl-list-append-rwrite-guard`,
    `dl-list-reset-rnode-guard`, `sibling-ptr-write-guard`). Crashed at 110.7s. Grepped
    `PORTING-STATE.md` + both `docs/*.md`: no prior hits on this exact `pc-symbol`/`last-guest-pc`
    pair. **Same function as item -319's own crash (`beginFrameDLChunk`) but a DIFFERENT
    `last-guest-pc`** (`0x8000ae40` vs item -319's `0x8000b0d0`) — per Iron Rule 4 / the s422
    overturned-conclusion precedent (one shared function/offset can span multiple real crash sites),
    treat as a distinct signature, not a 3rd occurrence of item -319. Not yet source-traced.

-322. **(s457 first seen; 2nd occurrence s512) `heapFreeListDequeue+NNNN`/`last-guest-pc=0x8000d92c`
    crash — TWO independent occurrences now, watch for a 3rd before opening a dedicated thread.**
    First surfaced s457 (`stepSongPitchBendLanes` live-verify, `pc-symbol=heapFreeListDequeue+32596`,
    frame-3 return address `submitSceneNodeRender+45220`, full backtrace `heapFreeListDequeue <-
    submitSceneNodeRender <- processSceneNode <- traverseSceneGraphRecursive <- setupCameraMatrices <-
    runHangarSelectionFrame <- runHangarMenuFromOverlay <- menuOverlayInit <- mainGameLoop`,
    `hangarbay-entry n=2600`) — at the time filed only as a same-subtree observation next to a
    DIFFERENT-signature s456 crash (`submitSceneNodeRender+29928`/`last-guest-pc=0x80010874`), not
    given its own item number. 2nd occurrence: `RENDER_LIT_MESH_R4_GUARD`'s 2nd confirm soak (s512
    fold-in, 0 fires on that guard itself, `hangarbay-entry n=31` positive control) —
    `pc-symbol=heapFreeListDequeue+40432 (local-symtab)`, **`last-guest-pc=0x8000d92c` byte-identical**
    to the s457 sighting (the `pc-symbol` offset differs, 32596 vs 40432, but that's expected: guard
    insertions upstream shift code layout between sessions, same as every other guard's offset drift
    in this campaign — `last-guest-pc` is the more reliable identity signal since it's a fixed guest
    instruction address). Post-s480, so per item -311 the `(local-symtab)` tag means the symbolizer
    found a real covering entry, not necessarily proof the fault is genuinely inside
    `heapFreeListDequeue` itself (a real function can still sit in an unexported-symbol gap the local
    table doesn't cover) — the s457 full backtrace is the stronger evidence here, and it does show a
    genuine `heapFreeListDequeue` frame. Not yet source-traced.

-321. **(s510, NEW) `menuOverlayInit+3648`/`last-guest-pc=0x800ab1c4` crash — single occurrence,
    host-symbol-offset-identical to the historically-CLOSED item -266/-267 chain but with a DIFFERENT
    `last-guest-pc`, flagged as a possible-but-unconfirmed recurrence.** Surfaced by
    `EMIT_FRAME_RDP_INIT_DL_R2J_GUARD`'s 2nd confirm soak (s510 fold-in, 0 fires on that guard itself,
    `hangarbay-entry n=31` positive control, one benign `hangarmenu-a0-guard` co-fire). The item
    -266/-267 chain (`PROJECT-OVERVIEW.md` §16) was CLOSED s432-433 as a side effect of fixing
    `getAvailablePlayerCraftFlagsConsiderUnlocks`, and every one of its original occurrences carried
    `last-guest-pc=0x800547bc` (or other values, never `0x800ab1c4`); `last-guest-pc` is a
    last-executed-guest-instruction breadcrumb, not the fault site, so a host pc-symbol+offset match
    with a differing breadcrumb is genuinely ambiguous — it could be a real recurrence via a different
    guest code path, or (per the s422 `0x800290d4` overturned-conclusion precedent, where one shared
    breadcrumb value turned out to span five different real crash functions) a coincidental re-hit of
    a shared host-code sink unrelated to the old bug. Per Iron Rule 4 and the s344 crash-signature-
    blindness method trap, do NOT conclude "item -266/-267 reopened" from this single ambiguous data
    point — watch for a 2nd occurrence with a matching `last-guest-pc` before escalating. Not yet
    source-traced.

-320. **(s508, NEW) `loadCutsceneAssetsByIndex+1860`/`last-guest-pc=0x800aafb8` crash — single
    occurrence, watch for a 2nd before opening a dedicated thread.** Surfaced by
    `EMIT_FRAME_RDP_INIT_DL_R2H_GUARD`'s 2nd confirm soak (s508 fold-in, 0 fires on that guard itself,
    `hangarbay-entry n=2700` positive control, one benign all-zero `compose-npc-orient-guard9` co-fire).
    Call chain: `menuOverlayInit` → `runHangarMenuFromOverlay` → `runHangarSelectionFrame` →
    `loadCutsceneAssetsByIndex`. Grepped `PORTING-STATE.md` + both `docs/*.md`: no prior hits on this
    exact `pc-symbol`/`last-guest-pc` pair — does not match the async Metal-shader-compiler-thread
    cluster (items -10/-9, `last-guest-pc≈0x800ab0e0`-`0x800aae00`ish) despite the nearby address, since
    this crash carries a real, function-attributed `pc-symbol` (not a dyld-shared-cache nonsense
    offset) and a distinct call stack through `loadCutsceneAssetsByIndex`. Not yet source-traced.

-319. **(s503, NEW; 2nd occurrence s505) `beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0` crash —
    TWO independent occurrences now, watch for a 3rd before opening a dedicated thread.** First
    surfaced by `EMIT_FRAME_RDP_INIT_DL_R2C_GUARD`'s 2nd confirm soak (s503, 0 fires on that guard
    itself). 2nd occurrence: item -318's `APPEND_RDP_STATE_DL_ENTRY_GUARD` 1st live-verify (s505, 0
    fires on that guard either) — byte-identical `pc-symbol` AND `last-guest-pc` to the s503 sighting,
    both unrelated to the guard under test in their respective runs. Does not match any prior
    catalogued family (grepped `PORTING-STATE.md` + both `docs/*.md`, no hits beyond its own two
    entries). Per item -318's own precedent, a 3rd independent occurrence of this exact signature
    would meet the threshold this campaign has been using to escalate a passive breadcrumb to a
    dedicated M3 session.

-318. **(s501-507) `appendRdpStateDl+144` crash — FIXED and FULLY CLOSED, 2/2
    (`APPEND_RDP_STATE_DL_ENTRY_GUARD`).** 1st live-verify (s505) clean. s506's first queued
    2nd-confirm attempt was INCONCLUSIVE (crashed at only 20.0s/8 frames on an unrelated
    already-catalogued crash, `pc-symbol=rebuildActiveDisplayObjectList+540`, the long-tracked
    shared-heap-corruption walker family, PORTING-STATE Sessions 164-219+, with **zero guard-fire lines
    of any kind, including zero `hangarbay-entry` positive-control fires** — per Iron Rule 1 didn't
    count) and was retried. The retry (folded in s507) is CLEAN: 0 `append-rdp-state-dl-entry-guard`
    fires, `hangarbay-entry` n up to 2700 (positive control), ran the full 300s scheduled duration with
    **no crash at all** (122 frames captured). 2/2 confirms, CLOSED. All three original occurrences
    (s498, s501, s503) shared
    `pc-symbol=appendRdpStateDl+144`, `last-guest-pc=0x800109b8`. s505 source-traced the mechanism
    (independently corroborated by a second Explore-agent pass reaching the same conclusion): all 6
    call sites of `appendRdpStateDl` (`funcs_4.c`, including `submitSceneNodeRender`'s `jal` at
    `0x800109B4`, whose delay slot at `0x800109B8` is what `last-guest-pc` actually names — the call
    site, not the fault site, per the s501 methodological note preserved below) reload the `-0x23A8`
    sibling global (`0x8011DC58`) with **no range check**, then pass the raw result as `$a0`/`ctx->r4`
    into the call. Inside `appendRdpStateDl` (`funcs_3.c` `0x8000DE70`), that argument becomes a
    display-list-append write cursor (aliased `ctx->r3`/`ctx->r11`) dereferenced **unconditionally from
    the function's first instruction** (`0x8000DE7C`, +12 bytes) through dozens of further sites, with
    zero null/range check anywhere in the function on any alias — a cross-function propagation gap of
    the same shape as item -316's `DL_ALLOC_PROPAGATION_GUARD` (an unguarded reload passed onward
    instead of dereferenced in-place), but via a call argument rather than a second in-function deref,
    and NOT covered by the existing 119-site `SIBLING_PTR_WRITE_GUARD` audit (item -296/-306), which
    only covers same-function `MEM_W(...) = val` writes through this same global, not "reload → pass as
    call arg → callee writes." Fix: guard once at function entry (`ctx->r4` range-checked
    `0x80000000`-`0x80800000`, early `return` — skip the whole body — if invalid), covering all 6 call
    sites from one patch point; `appendRdpStateDl` is void with RDRAM-only side effects, so skipping the
    body on an invalid cursor is safe by the same precedent as every other item -317/-318-family guard.
    **1st live-verify (s505)**: 0 `append-rdp-state-dl-entry-guard` fires (null result), 0 regressions
    on any sibling guard (3 benign init-time `n=0`/`ra=0x00000000` co-fires, the established
    non-corruption signature), `hangarbay-entry n=31` (positive control). Crashed at ~105s on
    `beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0` — **a 2nd occurrence of item -319's exact
    signature** (see below), unrelated to this guard. 2nd confirm CLOSED clean s507 (see item -318
    disposition above).
    **Register-correlation caution (preserved, still applies)**: s503's occurrence additionally carried
    `x0`=`x9`=`0x0000000300000000` in its mcontext dump, initially read as a correlation to the separate
    `initVec4TripletFromArgs+68` family (items -302/-306) — this is a **false lead**, already resolved
    by the s216-218→s219 overturned-conclusion entry (`0x0000000300000000` in `x0`/`x8` is the
    process's constant RDRAM host base pointer, present by construction in every `MEM_W`-involved fault,
    not written corruption); s502/s503's own 2nd-confirm folds added two more sightings in two MORE
    different registers (`x8`, `x11`), reinforcing "common incidental constant," not "one propagating
    corrupted value." Full derivation: `PORTING-STATE.md` Sessions 501, 503, 505.

-317. **(s490-514) Step 3 of the `-312..-316` lineage: a ~150-location blanket sweep of the same
    derived-pointer reload idiom across `funcs_3.c`/`funcs_4.c`, tool-audited then fixed
    incrementally, 17 of ~150 leads fixed so far, 16 FULLY CLOSED 2/2, 1 1st-live-verify-clean
    (2nd confirm queued — R7, s514).**
    Steps 1 (`heapFreeListDequeue`) and 2 (`buildOrientedFaceGeometry`) are separately FULLY CLOSED
    2/2 (item -316 area). Step 3's tracer (`scratch/agent/s494_item317_step3_tracer.py`, a forward
    taint-propagation dataflow analysis) found ~448 raw reload sites deduping to ~150 distinct
    candidate guard placements across 30 functions; an 8-site audit sample confirmed 8/8
    TRUE_POSITIVE. Fixed and 2/2-confirmed clean, s495-s514: `NODE_LIST_HEAD_SIBLING_R4_GUARD` (35
    sites), `RENDER_LIT_MESH_R2_GUARD` (48 sites), `EMIT_FRAME_RDP_INIT_DL_R2_GUARD` through
    `...R2J_GUARD` (ten guards, 40 shared sites each, all in `emitFrameRdpInitDl`),
    `RENDER_LIT_MESH_R3_GUARD` (`funcs_4.c:17346`/`0x800148E8`, 40 shared sites, `renderLitMeshFaceGroup`
    — a SECOND site in that function, not covered by R2's own fix), `RENDER_LIT_MESH_R4_GUARD`
    (`funcs_4.c:16049`/`0x800142FC`, 38 shared sites, `renderLitMeshFaceGroup` — a THIRD site, 2nd
    confirm closed clean s512 fold-in, crashed on item -322's `heapFreeListDequeue` signature,
    unrelated), `RENDER_LIT_MESH_R5_GUARD` (`funcs_4.c:17784`/`0x80014A8C`, 46 shared sites, a FOURTH
    site), and `RENDER_LIT_MESH_R6_GUARD` (`funcs_4.c:16575`/`0x80014558`, 38 shared sites, a FIFTH
    site). **R5's retried 2nd confirm and R6's 2nd confirm both folded in clean this session (s514)**:
    R5 retry — 0 `render-lit-mesh-r5-guard` fires, `hangarbay-entry n=2600` positive control (the
    s513 first attempt's missing-positive-control problem did not recur), crashed at 110.7s on
    `pc-symbol=rebuildActiveDisplayObjectList+540`/`last-guest-pc=0x800ab060` — byte-identical to an
    already-catalogued shared-heap-corruption-walker family occurrence (`PORTING-STATE.md:41991`),
    unrelated to this guard, CLOSED 2/2. R6 confirm — 0 `render-lit-mesh-r6-guard` fires,
    `hangarbay-entry n=2600` positive control, crashed at 118.4s on a nonsense dyld-shared-cache
    `pc-symbol` with `last-guest-pc=0x800ab0e0`, byte-identical to the already-catalogued async
    Metal-shader-compiler-thread SIGSEGV cluster (items -10/-9), unrelated to this guard, CLOSED 2/2.
    Item -317 step 3 is now **16/16 fully closed guards** (up from 14/14). s514 fixed a SEVENTH,
    distinct write site in the same `renderLitMeshFaceGroup`, `RENDER_LIT_MESH_R7_GUARD`
    (`funcs_4.c:15620`/`0x80014140`, 32 shared sites) — **1st live-verify clean on the guard itself**:
    0 `render-lit-mesh-r7-guard` fires, `hangarbay-entry n=2600` positive control, 4 benign init-time
    n=0/`ra=0x00000000`-class co-fires, crashed at 110.7s on a NEW, previously uncatalogued signature
    (`pc-symbol=beginFrameDLChunk+27456`/`last-guest-pc=0x8000ae40`, filed as **item -323**, single
    occurrence) — unrelated to this guard, 2nd confirm queued:
    `scratch/agent/soak_queue/s514_render_lit_mesh_r7_confirm.sh`. All 17 fixes share one shape: a
    null check (`ctx->r2 == 0`) gates the null arm safely, but the non-null fallthrough has no
    `0x80000000`-`0x80800000` range check before dereferencing; downstream control flow reassigns the
    register from the table again before any further use, so skip-the-write-on-invalid is a safe fix.
    Five crash threads surfaced as a side effect of earlier live-verifies (not chased in-band): item
    -318 (`appendRdpStateDl+144`, FULLY CLOSED 2/2 s507), item -319 (`beginFrameDLChunk+40536`, still
    only 2 independent occurrences), item -320 (`loadCutsceneAssetsByIndex+1860`, still a single
    occurrence), item -321 (`menuOverlayInit+3648`, filed s510, single occurrence,
    possible-but-unconfirmed item -266/-267 recurrence), item -322 (`heapFreeListDequeue`/
    `last-guest-pc=0x8000d92c`, filed s512, 2 occurrences, s457 + s512), and item -323
    (`beginFrameDLChunk+27456`/`last-guest-pc=0x8000ae40`, filed s514, single occurrence, same
    function as item -319 but a different `last-guest-pc`) — see above/below. **~128 other distinct
    locations remain unaudited/unfixed** (s514's fix was a seventh site inside an already-partially-
    covered function, not a new function, so the ~150-location estimate is essentially unchanged).
    **Next-ranked tier (from the s513 post-R6-regen scan — now stale by one guard insertion, MUST
    re-scan before picking)**: `funcs_3.c:16582`/`funcs_3.c:14280`/`funcs_3.c:15157` (36 sites each,
    all `beginFrameDLChunk`), `funcs_4.c:4880` (34 sites, `submitSceneNodeRender`),
    `funcs_3.c:14763`/`funcs_3.c:16107` (32 sites each, `beginFrameDLChunk`). Re-run both scripts
    fresh before picking (`s494_item317_step3_tracer.py --scan` + `scratch/agent/s506_dedupe.py`) —
    line numbers drift after every guard insertion; do not reuse recorded numbers once stale. Prefer a
    `renderLitMeshFaceGroup` or `submitSceneNodeRender` site over a `beginFrameDLChunk` site unless
    deliberately pursuing item -319's or -323's own investigation (fixing inside `beginFrameDLChunk`
    before either hits a 3rd-occurrence threshold pre-empts that thread's own dedicated
    investigation). **New signal (s506, not yet acted on)**: the tracer scan also flags a cluster of
    candidate sites (counts 28-36) inside `beginFrameDLChunk` itself — the exact function items -319
    and -323 both crash in; if either hits its 3rd occurrence, re-run the tracer scan and use that
    cluster as a ready-made starting point (recorded line numbers have already drifted repeatedly, do
    not reuse them). Full derivation: `docs/PROJECT-OVERVIEW.md` §21-§22, `PORTING-STATE.md` Sessions
    490-514.

-316. **(s488 scan → s489 FIXED → s490 2nd confirm clean) `DL_ALLOC_PROPAGATION_GUARD` — FULLY CLOSED,
    2/2.** A scope gap in the existing s436 `CACHE_HEAD_A1_GUARD` (`emitAllocatedDLCommand`,
    `funcs_3.c`): validated one deref but not two propagating writes right after it feeding a
    `-0x5BB4` write-cursor global reloaded unguarded at 19 sites; fixed by extending the check. Its own
    2nd confirm surfaced item -317 above. Full derivation: `docs/PROJECT-OVERVIEW.md` §21,
    `PORTING-STATE.md` Sessions 488-490.

-311. **(s480) Crash-symbolizer tooling fix — DONE, positive-control validated.** The item -310
    `dladdr`-nearest-exported-symbol blind spot is closed: `src/main/main.cpp` now builds a sorted
    local+exported symbol table (`nm -n` on the running binary, parsed once at startup outside any
    signal context) and the `[CRASH][pc-symbol]` line does a nearest-preceding-address binary search
    against it FIRST, falling back to `dladdr` only if the table's empty or has no covering entry
    (`(local-symtab)` vs `(dladdr-fallback)` tag in the log). Confirmed `nm -n` does print real names
    for internal-linkage (`t`-type) symbols (not stripped/anonymous) — this was the scope-check that
    picked this design over dSYM/`atos` (no dSYM is generated by this build at all). Validated with a
    deliberate env-gated crash inside `do_lwl` (a `static inline` helper from `recomp.h`, present as
    one of the exact functions populating item -310's 40KB gap): correctly symbolized as
    `sym=do_lwl+60 (local-symtab)`, not misattributed to `heapFreeListDequeue` or any other exported
    neighbor. Every future crash-signature triage session benefits from this, not just the one family
    that surfaced it. Full derivation: `PORTING-STATE.md` Session 480.

-310. **(s478) `heapFreeListDequeue+NNNN` crash family — INVESTIGATED AND CLOSED, a crash-symbolizer
    artifact (`dladdr` nearest-exported-symbol misattribution over a 40 KB unexported-code gap after
    `heapFreeListDequeue`), not a real recurring bug.** Guest-address arithmetic against the
    confirmed base ruled out both available `last-guest-pc` data points (off by 18-30 KB). No guard
    written (no single site to guard). **Do NOT re-file future occurrences as "same family, filed not
    chased"** — each is very likely an unrelated crash colliding with this blind spot. **The
    symbolizer blind spot itself is now FIXED, see item -311** — any NEW occurrence from here on will
    carry a `(local-symtab)`-tagged `pc-symbol` line naming the real function, so treat a future
    `heapFreeListDequeue`-attributed crash as genuinely that function, not this artifact, unless the
    log predates s480. Full derivation: `docs/PROJECT-OVERVIEW.md` §19.

-305..-309. **(s472-477) Five more single-bucket audits from the s465 frequency-scan lineage — four
    CLASSIFIED AND DEFERRED (not guard candidates), one (-306) a real fix.** -305
    (`hi16=0x8011,off=0x63d4`, `0x801163D4`, 170 sites, scan's largest bucket): compare-only
    bounds-check idiom (27-site sample, 26/27 confirmed). -306: resolved -296's flagged `-0x23a8` gap
    (141 sites) into a real `SIBLING_PTR_WRITE_GUARD` fix (1 new site, 120th, `setupCameraMatrices`,
    missed by s459's taint-tracking), CLOSED, 2nd confirm (s474) clean. -307
    (`hi16=0x8011,off=-0x35e0`, `0x8010CA20`, 23 sites/9 files): compare-only integer-flag idiom (12
    writes confirm non-pointer). -308 (`hi16=0x8013,off=0xb50`, `0x8012F4B0`, 24 sites/12 files):
    compare-only bitfield test, never dereferenced. -309 (`lui`+`sw` scan, 546 buckets/1471 sites, top
    3 checked): every large bucket a fixed-address global store, no stale-pointer risk — closes the
    `lui`+`sw` angle alongside `lui`+`lw` (s476). No code change except -306's. Full derivation:
    `docs/PROJECT-OVERVIEW.md` §19.

-298..-304. **(s463-472) Seven more M3 idiom-class audit buckets from the s465 frequency scan, six CLOSED, one DEFERRED — every CLOSED item's soak result matches item -287's established true-negative baseline.** -298 `DL_LIST_RESET_GUARD` (re-scoped ~111 non-canonical `-0x5824` sites, global `0x8011A7DC`) CLOSED s464, 84/84. -299 `DL_BUFFER_POOL_GUARD` (`0x801163FC`) CLOSED s466, 84/84, 2nd confirm s467. -300 `NODE_LIST_HEAD_GUARD`/`_WRITE_GUARD` (`0x8011A4B8`) CLOSED s467, 20 read + 10 write sites (two distinct downstream shapes), 2nd confirm s468. -301 `TEXDATA_TABLE_GUARD` (`hi16=0x8013,off=-0x70F8`, `funcs_6.c`) CLOSED s468, 31/31 (substitutes `0x80000000u`, not 0, since index arithmetic follows), 2nd confirm s469. -302 (`hi16=0x8013,off=0x7CE4`, 45 sites/9 files) DEFERRED s468: small INTEGER INDEX, 17 distinct downstream shapes, no single guard placement covers all sites without speculation. -303 `TEXDATA_PTR_ARRAY_GUARD` (`hi16=0x8013,off=-0x7104`, `funcs_6.c`) CLOSED s470, 29/29, 2nd confirm s471. -304 `MATERIAL_ARRAY_PTR_GUARD` (`0x8012($reg)`→`-0x5BBC`, 30 sites/4 files) CLOSED s471, 30/30, 2nd confirm s472. Full derivation: `docs/PROJECT-OVERVIEW.md` §18-§19.

-291..-297. **(s454-462) Three M3 idiom-class audits found via an s454 concurrent-process collision,
    all CLOSED**: -291 `DL_LIST_APPEND_GUARD` (57 sites), -292 `SONGTEMPO_TABLE_GUARD` (43/43 sites,
    `funcs_25.c`), -296 `SIBLING_PTR_WRITE_GUARD` (119 sites; **AMENDED s473/item -306: 1 real site
    silently dropped by a taint-tracking gap, found+fixed+confirmed**). Full detail:
    `docs/PROJECT-OVERVIEW.md` §17.

-261..-290 (and -263). **(s424-453) The duplicate-symbol-name-collision arc — ALL CLOSED.** A
    duplicate-symbol collision truncated `initCraftSelectScreen`; the fix cascaded into 3 more guarded
    crashes (-261..-267), a full duplicate-symbol catalogue closure (18/18) plus a 107-site
    `GENERIC_CACHE_GUARD` sweep, item -263's misattribution chase resolving to a third free-list
    sibling bug (`FREELIST_NEXT_GUARD`, -277, 105 sites), and the `static5-rename-orphan-sweep`
    (94 sites across 6 pre-s427 guard families). Full session-by-session detail:
    `docs/PROJECT-OVERVIEW.md` §16, `PORTING-STATE` Sessions 424-453.

-259. **(s422) `0x800290d4` "six independent triggers" — INVESTIGATED AND CLOSED, not a bug**:
    `inflate_fast`'s own clean return, misread as a shared corruption sink. `PORTING-STATE` 422.

-231..-249. **(s377-421) Three more CLOSED arcs: fixup function-scope backport (176 patches, 168
    converted), M3 `-0x25A4`/"Lookup" idiom resumption, and the 784-function `main_overlay.txt`
    phantom-overlay relocation.** Full detail: `docs/PROJECT-OVERVIEW.md` §13-§15,
    `PORTING-STATE` Sessions 377-421.

-230..-14 (excluding -20, kept below). **Eleven closed investigation lineages, s99-s376 — all CLOSED,
    no outstanding action.** M5 audio de-stubbing (items -160..-230, s297-376, §9-§12) plus ten earlier
    whack-a-mole guard-gap chases (`composeNpcOrientationMatrix`, `renderUnlitMeshFaces`, `heapWalker`,
    `heapFreeListDequeue`, `-0x25A4` family, breadcrumbs B2-B14, audio-array-corruption race,
    `submitDmaRequestBatch` indirect-caller, CALayer/campose SIGSEGV, regen-pipeline-idempotency root
    cause, §9). One-paragraph-per-lineage summaries:
    `docs/PROJECT-OVERVIEW.md` §9-§12; full raw detail: `PORTING-STATE` Sessions 99-376.

-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic).** Root cause: `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c` file that already exists on disk, so any patch whose regex anchor survives its own insertion stacks a duplicate on the next `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every regen is mandatory but **not sufficient by itself** -- residual intermittency's root cause is still unknown. **Standing rule**: audit the patch report for anything other than the expected `xN` count after every `fixup_game_funcs.py` run. Full detail: `PORTING-STATE` Sessions 120, 121, 126.

-11. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89), RECURRED s424, ROOT-CAUSED AND GUARDED s425.** s424 hit it as a sibling of item -261's guarded `startPlayerSlotAnimationChannelLooping` crash; s425 root-caused and guarded it (wild `$a0` arg, same never-initialized-slot root state) — see item -261 for the full trace.
-10/-9. **M3 — Metal-shader-compiler SIGSEGV reproducibility** (s83 spline1: SIGSEGV inside `Metal.framework`'s `MTLCompilerFSCache`, no source on our side; still one data point). **Confirm the s83 spline div0 guard actually engages**: 0/5 fires so far (still 0 after s88/s89/s90); real fix by code inspection (genuine 0/0 IEEE division) but no same-run positive control yet.
-8. **M3 — characterize `frameStartReset` SIGBUS.** 3 occurrences (s85, s108, s156 — the 3rd, `+532`, at a call chain byte-identical to `composeNpcOrientationMatrix`'s own, raising a shared-dispatcher hypothesis); no located faulting instruction in any of the 3.
-7. **M3 — HOLD_S=60 craft stick (M3 DoD body)** once earlier items clear: `PROBE_MODE=start_only HOLD_S=60` marks 10/25/40, document the phase timeline. Gate already keeps black off; residual S1 `fs` freeze (~3769-3872 plateau) may still stall animation.
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

- **(s400-421→s422)** "`0x800290d4`, six independent triggers, one shared downstream corruption
  sink — the strongest available root-cause lead" — `last-guest-pc=0x800290d4` is `inflate_fast`'s own
  clean return, reported by a sparse breadcrumb present in only 8/50 `RecompiledFuncs/funcs_*.c` files;
  `atos`-based exact symbolication of 5 of the 6 crash logs found five different real crash functions,
  not one. Believable for 21 sessions because the shared numeric value looked like a shared fault
  address, and nobody had yet resolved `last-guest-pc` past the breadcrumb's own coarse granularity to
  the actual host instruction. `m4_known_bad.txt`'s parking decision is unaffected (still correct);
  only the "worth a dedicated session" framing is overturned. PORTING-STATE 422.

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its conclusions are among the oldest in the file, not the newest.

- **(s54→s399)** "The M4 missing-func fix is applied and build-verified, only the runtime check is
  outstanding" — s54's fix (adding 3 names to `mission_overlay.txt`) was dead on arrival: the same 3
  names already existed at the same addresses in `main_overlay.txt`, which `make_elf.py` parses
  first and dedupes by name (first-file-wins), and which then get silently dropped as phantom
  functions (range-checked against `.text`, not the overlay window). s54's "build succeeded"
  observation was real but didn't prove what it was believed to prove — nobody checked `strings
  build/roguesquadron.elf` or grepped the recompiler's own output for the 3 names, which would have
  shown they were absent. Believable for 345 sessions because build success is consistent with both
  "fixed" and "silently still broken." Root-caused and actually fixed s399; also surfaced a much
  larger version of the same bug class (~801-803 more addresses, item -248). PORTING-STATE 399.
- **(s348/350→s352)** "`[scene-node-content-guard]` firing is evidence of the same corruption class as
  the other step-5 guards" — s352's raw-log re-read found it fires at the SAME node address
  (`0x80183ECC`) with the SAME zeroed content, thousands of times per run harmlessly across 3 sessions
  — a steady-state signature, not corruption; the n=0-vs-n=1957+ firing-shape distinction just hadn't
  been checked against the other guards until s352 compared them side by side. Guard stays in place;
  only its evidentiary weight for the corruption hunt is overturned. PORTING-STATE 348, 350, 352.
- **(s339→s340→s342)** "The VI=640 `pairs=0` plateau is a benign, locked-camera mission cutscene" and
  "s340's 2/2 clean soaks validate promoting both audio gate reversals" — s342 found those soaks never
  left the pre-title attribution/logo screen (0 `[keys]` lines in all 4 raw logs): crash-free with
  audio/DMA counters visibly live looked like a real positive control, but nobody checked the `[keys]`
  schedule had fired. The `pairs=0` mechanism itself (PROJECT-OVERVIEW §10) stands; only its context
  (pre-title, not mid-cutscene) is corrected. PORTING-STATE 339, 340, 342.
- **(s107/108→s316→s318)** Two linked overturns in the gate1/2/3 tick-producer chase: "the 3
  near-identical countdown/period gates fire `tickAllActiveSongs`/`tickAudioSequencerFrame`" was never
  positive-controlled (s316: none ever takes "call") — itself overturned by s318's fresher `ctx->r2`
  read (a stale-register race in the diagnostic, not the branch): gate1 calls 19/40, gate2 4/4.
  PORTING-STATE 316, 318.
- **(s222→s223)** "no soak reaches mesh-heavy content" — a 4-soak sample-size artifact; a re-run
  reached space-combat content before freezing. The freeze itself is real, still reproduces (now a
  flat fill, not a torn polygon). PORTING-STATE 223.
- **(s216-218→s219)** "shared corrupt literal `0x0000000300000000` at x0/x8, WRITTEN somewhere" — that
  register is the process's constant RDRAM host base pointer, present by construction in every
  `MEM_W` fault, not written corruption; the wild operand is the *other* register (byte-identical at 3
  sightings, all the same `renderUnlitMeshFaces` bug, vs. an unrelated 4th `heapWalker` bug).
  PORTING-STATE 219.
- **(s75/76→s150)** "single Start from SELECT YOUR CRAFT leaves into a distinct hangar-flight scene" —
  dense capture + an independent prior run + a code-level check (crash backtraces stay entirely in
  hangar-menu code) show it's the same craft-select scene under a corrupting camera move. Reopens
  "what leaves SELECT YOUR CRAFT" as unanswered. PORTING-STATE 150.
- **(s2-31→various, ~15 claims, grouped)** Build/pixel-getting era: Z-buffers misread as colour
  buffers, texrect output called invisible, RDP "emitting nothing" (real bug: a ring high-water mark),
  `DPC_WRAP`/fbpair-cap misdiagnosed for missing FULL_SYNC, floor-band/fog/S=0-triangle/stale-TMEM
  misattributions (real causes: M1 s44-49, §4.1), 1024-phase black screen (present-starvation, not
  zero-shade). Each overturned within 1-2 sessions of first being believed. PORTING-STATE 2-31.
- **(s62-69, grouped)** "RSP task submission stays healthy through the freeze" — a 1-in-32 throttled
  sample missed the crashing tail; unsampled showed 100% `ImemOverrun`. "Self-restarting the IMEM
  perspective-divide branch un-freezes tasks" — instrument fired 0 times; real site was
  `CLIP_1FBC`→`L_1650`. PORTING-STATE 62-69.
- **(s12-48, grouped)** "0x6AB400 is the main-menu hangar" (believable: partial render looked coherent
  36 sessions); briefing-room/SELECT-LEVEL origin+timing claims; hangar dimness misattributed to a
  magnitude-erasing shade census (real cause: M1 s44-49). All overturned s47/s48; real causes in
  "Current truth" above. PORTING-STATE 12-48.
- **(s70-82, ~9 claims, grouped)** The post-`a` SIGBUS/black-screen self-correction chain — UAF
  theories, present-stall theories — all resolved by the s84 UAF fix and s82 sane-width gate.
  PORTING-STATE 70-82.
- **(s87→s88)** "8th crash class is self-recursion in `advancePlayerAnimationPhase`" — different,
  unreached call site; constant stack depth across 3296 calls, no recursion. PORTING-STATE 88.
- **(s302→s306)** "reversing `initMusyXEngine`'s gate-byte site validated safely (0/2 family #1
  recurrence)" — a positive-controlled entry counter found `initMusyXEngine` is never called at all;
  the clean result reflects dead code, not a validated gate=1 state. Gate=1 still never exercised by
  any soak. PORTING-STATE 306.
- **(s307→s309→s313→s315)** A chain of "audio-tick stop points converge" claims, each overturned by a
  closer same-run measurement: shared-upstream-resource theory refuted by source-read; "3
  tick-producers + RSP `M_AUDTASK` all stop together at #19/20" refined by a widened print-cap soak to
  2 real stop points, not 1 or 3 (`M_AUDTASK`'s 20/20 was its own unwidened diagnostic bug). Similar
  small round numbers read as simultaneous unless line numbers are diffed. PORTING-STATE 309, 313, 315.
- **(M5-AUDIO-PLAN.md §4→s371)** "The host audio bridge is already fully implemented and functional" —
  a source read found `queue_samples`'s sample-count parameter was passed straight through as
  `SDL_QueueAudio`'s byte length with no `*sizeof(int16_t)` conversion, silently dropping the back half
  of every PCM buffer. Believable: the wiring compiles/links/calls cleanly, so eyeballing the call graph
  reads as functional — the defect is a unit mismatch one level down. Fixed s371 (`src/main/main.cpp`;
  PROJECT-OVERVIEW §12). PORTING-STATE 371.

### Dead ends — labelled as such in the log, do not retry

- **(s2b-s4, grouped)** `RDP_ADDRESS_MASK`→0x7FFFFF (aliased legit extended-RDRAM handles onto low
  memory); `dma_rdram_to_dmem` chunk-replay hack (legit trig reads after a swap); widened DMA shadow
  0x37658 (legit dynamic data); blanket ucode shadow `shadow2` (2 legit rewrites); `ROGUESQ_RING_RESYNC`
  (no effect); `dmem[0x153]=0xFF` forced reload (made failures worse).
- Bulk `main_overlay.txt` symbol moves (s9): splits the enclosing function (§4.5), SIGBUS — use
  `tools/overlay_symbol_probe.py <0xADDR>` first, one batch at a time. Present-side snap-down/
  `findMostRecentContaining` (s9, neither fired); `ROGUESQ_VIEW_RDRAM=1` (s9, window never appears,
  broken in this fork); `ROGUESQ_WRAP_DEDUP=1` (s10, ~33000 fewer submissions, same assert still hits);
  `ROGUESQ_FORCE_PAL15=1` (s14, clears floor band, corrupts ceiling banners sharing pal=15).
- **(s85→s91)** "`do_rom_read` corrupted `physical_addr` is nondeterministic garbage" — the exact same
  DMA call recurred byte-for-byte 3 times across 3 sessions; reclassified deterministic, reproducible.

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
