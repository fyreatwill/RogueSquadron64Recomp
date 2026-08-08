# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Twenty-three passes
   so far (per-pass targets in git log; PROJECT-OVERVIEW §16-§23 hold the most recent arcs) kept the
   file oscillating around the cap as new session detail accrues. 35 KB remains a stretch target, not a
   hard floor -- the "Current truth" env-var/timeline prose and the Regeneration section's Standing
   warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (full arc: PROJECT-OVERVIEW
   §10-§12). Next M5 work needs a genuinely new lead (**last checked s520 — zero new leads
   (`[audio-wait-pump-stall]`, the existing s327/item -184-185 pump-bound diagnostic, fired but is
   already-catalogued steady-state noise, seen in 138 other soak logs), cadence reset to s520, due
   again once 3+ sessions have passed, i.e. s523+**).
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. Every bucket
   surfaced by the s465/s477 frequency scans has a disposition (items -298..-309, PROJECT-OVERVIEW
   §18-§19). Items -312..-319 (s481-520, the `DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`/
   `AUDIO_SLOT_ACTIVE_GUARD`/`DL_ALLOC_PROPAGATION_GUARD`/`APPEND_RDP_STATE_DL_ENTRY_GUARD`/
   `SIBLING_PTR_WRITE_GUARD`-gap sibling-site-gap lineage) are all fully CLOSED except -317 step 3 —
   PROJECT-OVERVIEW §20-§23. **Item -317 step 3 (a ~150-location blanket sweep) status as of s520: 19
   of ~150 leads fixed, all 19 FULLY CLOSED 2/2** (`RENDER_LIT_MESH_R8_GUARD`'s 2nd confirm, s519's
   queued soak, came back clean on re-read: `hangarbay-entry n=2600` positive control, 0 own-guard
   fires, crashed only on the unrelated already-catalogued Metal-framework cluster) — see item -317
   below for the next tier to pick; full campaign detail: PROJECT-OVERVIEW §22-§23. **Item -322
   (`heapFreeListDequeue`/`last-guest-pc=0x8000d92c`) is FIXED and FULLY CLOSED 2/2** (s517/s518,
   `HEAPLISTDEQ_ATTR_WRITE_GUARD`). **Item -321 (`menuOverlayInit`-area/`last-guest-pc=0x800ab1c4`) was
   source-traced s518 and its 2-occurrence escalation is REFUTED** (documented tooling gap, not a crash
   lead — see item -321 below). **Item -319 (`beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0`) was
   source-traced and FIXED s520** — a real gap in the s459 `SIBLING_PTR_WRITE_GUARD` sweep, sandwiched
   between two already-guarded sibling sites in the same function; 1st live-verify clean, 2nd confirm
   queued (see item -319 below). M3's top-ranked work unit reverts to item -317 step 3's own blanket
   sweep, now that item -319 is resolved. Items -320/-323 are unchanged single-occurrence breadcrumbs
   (see below).

-312..-318. **(s481-507) The `DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`/`AUDIO_SLOT_ACTIVE_GUARD`/
    `APPEND_RDP_STATE_DL_ENTRY_GUARD` "grep-verified unique site" lineage — seven items, all fully
    CLOSED except -317 step 3** (open scope and methodology lesson: see item -317 below). Full
    derivation: `docs/PROJECT-OVERVIEW.md` §20-§23.

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

-323. **(s514, single occurrence) `beginFrameDLChunk+27456`/`last-guest-pc=0x8000ae40` crash.**
    Surfaced by `RENDER_LIT_MESH_R7_GUARD`'s 1st live-verify, 0 fires on that guard, real positive
    control. Same function as item -319 but a DIFFERENT `last-guest-pc` (`0x8000ae40` vs `0x8000b0d0`)
    — per the s422 precedent, a distinct signature, not a 3rd -319 occurrence. No 2nd occurrence yet.

-322. **(s457/s512/s515 → s517 FIXED, `HEAPLISTDEQ_ATTR_WRITE_GUARD` → s518 FULLY CLOSED 2/2.**
    Source-traced `funcs_3.c:22715` `heapFreeListDequeue` (spans `0x8000CFD4`-`0x8000D9D0`, one
    continuous control-flow region, confirmed by inspection — the `last-guest-pc=0x8000d92c` shared by
    all 3 prior occurrences pins to `MEM_W(0X0, ctx->r2) = ctx->r3;` at `0x8000D92C`, where `ctx->r2`
    is reloaded unguarded from stack slot `0x3C($sp)` (filled far upstream at `0x8000D4DC` from a
    fixed-global-array-base + `index<<2` computation, no `0x80000000`-`0x80800000` range check before
    the write-through). Downstream immediately reassigns the register to an unrelated flag-test
    result, so skip-the-write-on-invalid is safe, same precedent as the whole item -317-lineage.
    **Side note**: the `pc-symbol`'s `+NNNN` offset (32596/40432/etc.) is a NATIVE code offset from
    `nm`, not a guest-address delta — confirmed by reading `src/main/main.cpp`'s crash handler — so it
    should never be used to estimate a guest offset within the function; only `last-guest-pc` is
    reliable for that. 1st live-verify (s517, manual, foreground): 0 `heaplistdeq-attr-write-guard`
    fires, 1 benign `hangarmenu-a0-guard` co-fire (item -265, already-catalogued), `hangarbay-entry
    n=34` positive control. Crashed at 121.2s on `pc-symbol=coalesceFreeHeapBlocks+4424`/
    `last-guest-pc=0x8000247c` — the already-catalogued background-noise heap-walker family
    (documented since s354-366), unrelated to this guard. 2nd confirm (s518,
    `s517_heaplistdeq_attr_write_confirm`, run by the loop): ran the FULL 347s scheduled duration with
    **zero crashes of any kind** and 0 `heaplistdeq-attr-write-guard` fires, `hangarbay-entry n=2700`
    positive control — cleaner than the 1st verify (no unrelated background-noise crash even). CLOSED
    2/2. Full detail: `docs/PROJECT-OVERVIEW.md` §23, `PORTING-STATE.md` Sessions 457, 512, 515, 517,
    518.

-321. **(s510/s515, 2 occurrences → s518 source-traced, escalation REFUTED — closed as a documented
    tooling gap, not a crash lead.** s510 (`pc-symbol=menuOverlayInit+3648`) and s515
    (`pc-symbol=unregisterServiceWorker+536 (local-symtab)`) shared `last-guest-pc=0x800ab1c4`, which
    looked like matching corroboration despite the pc-symbol mismatch. Source-trace (s518): guest
    address `0x800AB1C4` is `runHangarSelectionFrame`'s own `addiu $sp,$sp,0x30` return-epilogue
    instruction (`N64Recomp/RecompiledFuncs/funcs_28.c:6019` — confirmed by reading the recompiled
    source; verified this address is also independently claimed by two OTHER overlay functions,
    `composeEffectObjectTransformMatrix` and `spawnCutsceneDebrisField`, since all three overlays load
    at the same fixed base `0x800A5130` — `menuOverlayInit`'s own `hangarbay-entry` positive controls
    rule those two out). It is pure register arithmetic, not a memory access — it cannot fault. The
    `g_rs64_last_guest_pc` breadcrumb tracker only exists inside a curated allowlist of instrumented
    functions (`BREADCRUMB1`-`18` in `fixup_game_funcs.py`); `runHangarSelectionFrame`'s last write is
    its own return, and its callers one level up (`runHangarMenuFromOverlay`, `funcs_35.c:450`;
    `menuOverlayInit`, `funcs_34.c:5260`) have **zero** breadcrumb writes in their bodies (grep-verified
    s518) — so the global freezes at `0x800AB1C4` regardless of where execution actually goes next.
    This is the exact `BREADCRUMB17`→`18` "chase the freeze one level up" pattern already documented
    for item -263 (PROJECT-OVERVIEW §s435-439), now recurring a 3rd time. **Conclusion**: s510 and s515
    are most likely two DIFFERENT real crashes that both happen to have just unwound out of
    `runHangarSelectionFrame` — the matching `last-guest-pc` is not meaningful corroboration. Downgraded
    from escalated-and-queued to a documented instrumentation gap. **If a similar breadcrumb-freeze
    pattern recurs and needs localizing**, add `BREADCRUMB19` to `runHangarMenuFromOverlay` modeled
    directly on `BREADCRUMB17`/`18` (same per-instruction-comment regex patch) — not currently queued
    as work, since neither underlying crash has its own 2nd occurrence.

-320. **(s508, single occurrence) `loadCutsceneAssetsByIndex+1860`/`last-guest-pc=0x800aafb8` crash.**
    Surfaced by `EMIT_FRAME_RDP_INIT_DL_R2H_GUARD`'s 2nd confirm (0 fires, real positive control). Call
    chain: `menuOverlayInit` → `runHangarMenuFromOverlay` → `runHangarSelectionFrame` →
    `loadCutsceneAssetsByIndex`. Distinct from the async Metal-shader-compiler cluster (items -10/-9)
    despite a nearby address — real function-attributed `pc-symbol`. No 2nd occurrence yet.

-319. **(s503/s505/s519 → s520 SOURCE-TRACED AND FIXED, `SIBLING_PTR_WRITE_GUARD` site=0x8000B0D0
    (121st site in that family) → 1st live-verify CLEAN, 2nd confirm queued.**
    `beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0`, `funcs_3.c:15017`. First surfaced by
    `EMIT_FRAME_RDP_INIT_DL_R2C_GUARD`'s 2nd confirm; 2nd occurrence was item -318's own 1st
    live-verify; 3rd occurrence (s519) was `RENDER_LIT_MESH_R8_GUARD`'s own 1st live-verify — all three
    shared byte-identical `pc-symbol` AND `last-guest-pc`. Source-trace (s520): the write at `0x8000B0D0`
    (`MEM_W(0X4, ctx->r3) = ctx->r4;`) is a genuine unguarded pointer write-through sitting directly
    BETWEEN two already-guarded sibling sites through the exact same `ctx->r3` (the `-0x23A8`
    fixed-global-scalar pointer, guest address `0x8011DC58`) — `0x8000B0BC` (guarded since s459) and
    `0x8000B0EC` (guarded since s459), in the same function. `ctx->r3` is neither reassigned nor
    rechecked between the `0x8000B0BC` guard and this write; it IS reloaded from the identical
    `-0x23A8` global again immediately after (`0x8000B0D4`/`0x8000B0D8`), and that next use is already
    guarded at `0x8000B0EC` — skip-on-invalid is safe, same shape as every other `SIBLING_PTR_WRITE_GUARD`
    site. A genuine gap in the original s459 sweep (`0x8000B0BC` and `0x8000B0EC` were caught,
    `0x8000B0D0` sandwiched between them was missed), NOT covered by the s494 item-317-step-3 tracer
    (that tracer is hard-scoped to a different, self-referential `+0x63B0` reload idiom). Fixed by adding
    the site to `fixup_game_funcs.py`'s existing `_SIBLING_PTR_WRITE_SITES` table (same guard shape,
    `ROGUESQ_LOG_SIBLING_PTR_WRITE_GUARD=1`), taking the family from 120 to 121 sites. 1st live-verify
    (s520, manual, foreground, 2 attempts — 1st discarded, crashed at 20.3s on the Metal-framework
    shader-compiler cluster before reaching the hangar, too weak a positive control per Iron Rule 1):
    CLEAN — 0 `sibling-ptr-write-guard` fires (any site, including the new `site=0x8000B0D0`), 0 fires on
    all other ~55 armed sibling guard families (no regression), 3 benign pre-existing `s284-guard`
    co-fires, `hangarbay-entry n=2600` positive control (strong). Crashed at 113.9s on the SAME
    already-catalogued Metal-framework shader-compiler-thread cluster as items -10/-9
    (`last-guest-pc=0x800ab048`) — unrelated to this guard and unrelated to item -319's own original
    signature, filed not chased. 2nd independent confirm queued:
    `scratch/agent/soak_queue/s520_sibling_ptr_b0d0_confirm.sh`. Note: `beginFrameDLChunk` is also item
    -317 step 3's own largest reload-site cluster (36/32/30-count tiers, deliberately skipped so far to
    avoid pre-empting this thread) — those tiers are a DIFFERENT reload idiom (the self-referential
    `+0x63B0` shape) from this fix's `-0x23A8` sibling-global shape, so this fix does NOT subsume them;
    they remain open leads for step 3's continuation.

-318. **(s501-507) `appendRdpStateDl+144` crash — FIXED and FULLY CLOSED 2/2
    (`APPEND_RDP_STATE_DL_ENTRY_GUARD`).** All 6 call sites reload a sibling global with no range check
    and pass it as a write-cursor argument the callee dereferences unconditionally from its first
    instruction — outside the existing 119-site `SIBLING_PTR_WRITE_GUARD` audit's scope. Fixed by
    range-checking at function entry and skipping the (void, RDRAM-only) body if invalid. 1st
    live-verify (s505) clean; 2nd confirm's first attempt (s506) INCONCLUSIVE (no positive control,
    Iron Rule 1), retry (s507) ran the full 300s clean — CLOSED 2/2. Mechanism and session detail:
    `docs/PROJECT-OVERVIEW.md` §23.

-317. **(s490-519) Step 3 of the `-312..-316` lineage: a ~150-location blanket sweep of the same
    derived-pointer reload idiom across `funcs_3.c`/`funcs_4.c` — 19 of ~150 leads fixed, all 19 FULLY
    CLOSED 2/2.** Steps 1 (`heapFreeListDequeue`) and 2 (`buildOrientedFaceGeometry`) are separately
    FULLY CLOSED 2/2. Step 3's tracer (`scratch/agent/s494_item317_step3_tracer.py`, a forward
    taint-propagation dataflow analysis) found ~448 raw reload sites deduping to ~150 candidate guard
    placements across 30 functions. All 19 fixes share one shape: a null check gates one arm safely, the
    non-null fallthrough has no `0x80000000`-`0x80800000` range check before a write-through deref,
    downstream control flow reloads the register from a table again — skip on invalid is safe.
    `renderLitMeshFaceGroup` now carries 7 fixes (R2-R8, s519 added the doubly-linked free-list-cache
    prepend site at `funcs_4.c:15166`/`0x80013F0C`); its 19th fix, `RENDER_LIT_MESH_R8_GUARD`, CLOSED 2/2
    s520 on re-read of the s519-queued 2nd confirm: `hangarbay-entry n=2600` positive control, 0 own-guard
    fires (no regression), crashed only on the unrelated already-catalogued Metal-framework
    shader-compiler cluster (items -10/-9). **~126 locations remain unaudited — this is the top-ranked
    M3 work unit again**, now that item -319 (which had temporarily outranked it) is resolved (see item
    -319 above). Next-ranked tier (from the s519 scan — RE-RUN fresh before picking, line numbers drift
    per insertion): `funcs_3.c:16582`/`14280`/`15157` (36 sites each, `beginFrameDLChunk`),
    `funcs_3.c:14763`/`16107` (32 sites, `beginFrameDLChunk`), `funcs_3.c:11625`/`12895`/`15641` (30
    sites, mixed `emitColorFillRect`/`beginFrameDLChunk`), `funcs_4.c:4457`/`3299` (`submitSceneNodeRender`,
    30/28 sites). Note: item -319's s520 fix was a DIFFERENT reload idiom (`-0x23A8` sibling-global
    shape, `SIBLING_PTR_WRITE_GUARD` family) from this tracer's self-referential `+0x63B0` shape — it
    does not subsume any of these tiers. Full guard table and gotchas: `docs/PROJECT-OVERVIEW.md`
    §22-§23, `PORTING-STATE.md` Sessions 490-520.

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

- **(s400-421->s422)** "`0x800290d4`, six independent triggers, one shared downstream corruption sink -- the strongest available root-cause lead" -- `last-guest-pc=0x800290d4` is `inflate_fast`'s own clean return, reported by a sparse breadcrumb present in only 8/50 `RecompiledFuncs/funcs_*.c` files; `atos`-based exact symbolication of 5 of the 6 crash logs found five different real crash functions, not one. Believable for 21 sessions because the shared numeric value looked like a shared fault address, and nobody had yet resolved `last-guest-pc` past the breadcrumb's own coarse granularity to the actual host instruction. `m4_known_bad.txt`'s parking decision is unaffected (still correct); only the "worth a dedicated session" framing is overturned. PORTING-STATE 422.

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its conclusions are among the oldest in the file, not the newest.

- **(s54->s399)** "The M4 missing-func fix is applied and build-verified, only the runtime check is outstanding" -- s54's fix (adding 3 names to `mission_overlay.txt`) was dead on arrival: the same 3 names already existed at the same addresses in `main_overlay.txt`, which `make_elf.py` parses first and dedupes by name (first-file-wins), and which then get silently dropped as phantom functions (range-checked against `.text`, not the overlay window). Believable for 345 sessions because build success is consistent with both "fixed" and "silently still broken." Root-caused and actually fixed s399; also surfaced a much larger version of the same bug class (~801-803 more addresses, item -248). PORTING-STATE 399.
- **(s348/350->s352)** "`[scene-node-content-guard]` firing is evidence of the same corruption class as the other step-5 guards" -- s352's raw-log re-read found it fires at the SAME node address (`0x80183ECC`) with the SAME zeroed content, thousands of times per run harmlessly -- a steady-state signature, not corruption; the n=0-vs-n=1957+ firing-shape distinction just hadn't been checked against the other guards until s352 compared them side by side. Guard stays in place; only its evidentiary weight for the corruption hunt is overturned. PORTING-STATE 348, 350, 352.
- **(s339->s340->s342)** "The VI=640 `pairs=0` plateau is a benign, locked-camera mission cutscene" and "s340's 2/2 clean soaks validate promoting both audio gate reversals" -- s342 found those soaks never left the pre-title attribution/logo screen (0 `[keys]` lines in all 4 raw logs): crash-free with audio/DMA counters visibly live looked like a real positive control, but nobody checked the `[keys]` schedule had fired. The `pairs=0` mechanism itself (PROJECT-OVERVIEW §10) stands; only its context (pre-title, not mid-cutscene) is corrected. PORTING-STATE 339, 340, 342.
- **(s107/108->s316->s318)** Two linked overturns in the gate1/2/3 tick-producer chase: "the 3 near-identical countdown/period gates fire `tickAllActiveSongs`/`tickAudioSequencerFrame`" was never positive-controlled (s316: none ever takes "call") -- itself overturned by s318's fresher `ctx->r2` read (a stale-register race in the diagnostic, not the branch): gate1 calls 19/40, gate2 4/4. PORTING-STATE 316, 318.
- **(s222->s223)** "no soak reaches mesh-heavy content" -- a 4-soak sample-size artifact; a re-run reached space-combat content before freezing. The freeze itself is real, still reproduces (now a flat fill, not a torn polygon). PORTING-STATE 223.
- **(s216-218->s219)** "shared corrupt literal `0x0000000300000000` at x0/x8, WRITTEN somewhere" -- that register is the process's constant RDRAM host base pointer, present by construction in every `MEM_W` fault, not written corruption; the wild operand is the *other* register (byte-identical at 3 sightings, all the same `renderUnlitMeshFaces` bug, vs. an unrelated 4th `heapWalker` bug). PORTING-STATE 219.
- **(s75/76->s150)** "single Start from SELECT YOUR CRAFT leaves into a distinct hangar-flight scene" -- dense capture + an independent prior run + a code-level check (crash backtraces stay entirely in hangar-menu code) show it's the same craft-select scene under a corrupting camera move. Reopens "what leaves SELECT YOUR CRAFT" as unanswered. PORTING-STATE 150.
- **(s2-31, s62-69, s12-48, s70-82 -- grouped, ~35 claims total, the earliest build/pixel-getting and menu-triage era)** Z-buffers misread as colour buffers, texrect output called invisible, RDP "emitting nothing" (real bug: a ring high-water mark), `DPC_WRAP`/fbpair-cap misdiagnosed for missing FULL_SYNC, floor-band/fog/S=0-triangle/stale-TMEM misattributions (real causes: M1 s44-49, section 4.1), 1024-phase black screen (present-starvation, not zero-shade); "RSP task submission stays healthy through the freeze" (a 1-in-32 throttled sample missed the crashing tail; unsampled showed 100% `ImemOverrun`); "self-restarting the IMEM perspective-divide branch un-freezes tasks" (instrument fired 0 times, real site was `CLIP_1FBC`->`L_1650`); "0x6AB400 is the main-menu hangar" (believable: partial render looked coherent 36 sessions) plus briefing-room/SELECT-LEVEL origin+timing claims and hangar-dimness-as-shade-census (real cause: M1 s44-49, see "Current truth" above); the post-`a` SIGBUS/black-screen self-correction chain (UAF and present-stall theories, resolved by the s84 UAF fix and s82 sane-width gate). Each overturned within 1-2 sessions of first being believed. PORTING-STATE 2-31, 62-69, 12-48, 70-82.
- **(s87->s88)** "8th crash class is self-recursion in `advancePlayerAnimationPhase`" -- different, unreached call site; constant stack depth across 3296 calls, no recursion. PORTING-STATE 88.
- **(s302->s306)** "reversing `initMusyXEngine`'s gate-byte site validated safely (0/2 family #1 recurrence)" -- a positive-controlled entry counter found `initMusyXEngine` is never called at all; the clean result reflects dead code, not a validated gate=1 state. Gate=1 still never exercised by any soak. PORTING-STATE 306.
- **(s307->s309->s313->s315)** A chain of "audio-tick stop points converge" claims, each overturned by a closer same-run measurement: shared-upstream-resource theory refuted by source-read; "3 tick-producers + RSP `M_AUDTASK` all stop together at #19/20" refined by a widened print-cap soak to 2 real stop points, not 1 or 3 (`M_AUDTASK`'s 20/20 was its own unwidened diagnostic bug). Similar small round numbers read as simultaneous unless line numbers are diffed. PORTING-STATE 309, 313, 315.
- **(M5-AUDIO-PLAN.md §4->s371)** "The host audio bridge is already fully implemented and functional" -- a source read found `queue_samples`'s sample-count parameter was passed straight through as `SDL_QueueAudio`'s byte length with no `*sizeof(int16_t)` conversion, silently dropping the back half of every PCM buffer. Believable: the wiring compiles/links/calls cleanly, so eyeballing the call graph reads as functional -- the defect is a unit mismatch one level down. Fixed s371 (`src/main/main.cpp`; PROJECT-OVERVIEW §12). PORTING-STATE 371.

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
