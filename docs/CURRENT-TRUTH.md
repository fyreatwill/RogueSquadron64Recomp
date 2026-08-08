# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Eighteen passes
   so far (s295-330 x5, s346, s355, s364, s371, s380, s391, s398, s409, s429, s438, s444, s451, s461,
   s469) kept the file oscillating around the cap as new session detail accrues — full per-pass
   migration targets in git log; PROJECT-OVERVIEW §16-§18 hold the most recent three arcs. 35 KB
   remains a stretch target, not a hard floor -- the "Current truth" env-var/timeline prose and the
   Regeneration section's Standing warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (full arc: PROJECT-OVERVIEW
   §10-§12). Next M5 work needs a genuinely new lead.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. **The s465
   codebase-wide frequency scan's candidate list is EXHAUSTED as of s475 (item -308)** — every bucket
   it surfaced has a disposition; see items -298..-308 below and PROJECT-OVERVIEW §18. Next M3 session
   needs either a new discovery pass (re-run the s465 scan methodology against a different instruction
   pattern) or the item -308 tool-bug-#5 backfill audit (re-check every already-CLOSED bucket for
   `lui`->label->`lw` sites silently missed by `scratch_s468_shapecheck_generic.py` — see item -308).

Sanctioned tooling work unit (backport function-scoped matching to file-scoped-only guard patches in
`fixup_game_funcs.py`): **CLOSED OUT s386/s388** — item -231..-238, `docs/PROJECT-OVERVIEW.md` §13.

## Current truth (established by session 295; unchanged, reviewed through s469)

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
a range pointer. Highest allocated so far: -308. The next NEW item takes -309.

-308. **(s475) M3 idiom-class audit: `hi16=0x8013, offset=0xb50` global (`0x8012F4B0`) — CLASSIFIED
    AND DEFERRED, not a guard candidate. Also found tool bug #5, a label-line blind spot.** True site
    count is 24 across 12 files (`funcs_9/12/15/16/17/27/28/29/30/32/33/42.c`), not the 21/11 the
    scan tool initially reported — `scratch_s468_shapecheck_generic.py`'s lookahead loop only
    recognizes disassembly-comment and breadcrumb lines while scanning from a `lui` to its `lw`
    reload; a bare `L_XXXXXXXX:` branch-target label between them (common when the reload address is
    itself a jump target) silently breaks the scan with no site reported and no warning — missed 3
    sites (`funcs_27.c:108435`, `funcs_30.c:14600`, `funcs_32.c:29556`), the last in a file
    (`funcs_32.c`) that didn't appear in the tool's file list at all. Fixed in a standalone checker
    (`scratch_s475_label_gap_check.py`, N64Recomp repo, untracked) that also skips label lines; not
    fixed in the tool itself. All 24 sites (12/12 files) directly read: 100% the identical
    `andi $vN, $vN, MASK` (masks `0x1/0x8/0x10/0x20/0x60` — a packed status/capability bitfield)
    immediately after the reload, consumed only by a conditional branch, never dereferenced — same
    compare-only idiom as items -305/-307. 0 write sites to the global found (`grep MEM_W(0XB50` —
    read-only from recompiled code). No code change, no soak queued (same precedent as -305/-307).
    **Open question, not yet chased**: whether this label-gap bug also undercounts any already-CLOSED
    bucket (items -298/-299/-300/-301/-303/-304/-306) — every spot-checked label-gap site so far has
    been harmless, but no already-closed bucket has been re-checked against this specific bug. Full
    derivation: `PORTING-STATE.md` Session 475.

-307. **(s474) M3 idiom-class audit: `hi16=0x8011, offset=-0x35e0` global (`0x8010CA20`) — CLASSIFIED
    AND DEFERRED, not a guard candidate.** 23 `lw` reload sites across 9 files
    (`funcs_11/16/18/29/30/35/38/40/42.c`), no overlap with any existing guard's global address.
    `scratch_s468_shapecheck_generic.py` flagged 3 sites `ADD32(...)->WRITE_THROUGH hit_deref=True` —
    all 3 confirmed by direct read to be a **newly found tool bug**: the classify loop checks
    register taint via Python substring containment (`"ctx->r2" in args`), which false-matches inside
    `"ctx->r29"` — the near-universal stack-pointer prologue line (`ctx->r29 = ADD32(ctx->r29, N);`)
    immediately following a reload landed in `$v0`/r2 gets misread as touching the tainted register,
    and the next unrelated stack-spill line gets misclassified as a write-through. A from-scratch
    taint scan (`scratch_s474_taint_scan_35e0.py`, N64Recomp repo, untracked, adapted from item -306's
    fixed template) initially found 1 "real" unguarded deref (`triggerStageMusicForNamedDatItem`,
    `funcs_40.c`) — direct read caught a **2nd tool bug in the new scan itself**: taint wasn't cleared
    across a real function call, so `ctx->r2` (the MIPS o32 return-value register) was still marked
    tainted from the pre-call reload when it actually held the callee's own return value post-call.
    Fixed (clear caller-saved regs `r2,r3,r8-r15,r24,r25` after any uncaught real-call line); re-ran:
    0/23 real derefs, 0/23 write-throughs, 0/23 tainted-call-arg escapes. Site count cross-validated
    exact (23/23, file:line match) against the canonical shapecheck list before trusting the result.
    10/23 sites spot-checked directly across 7/9 files — 100% the same "load, compare != 0,
    branch-and-discard" idiom as item -305. 12 write sites to the same global found (`funcs_42.c`
    only, all storing small integer literals/register copies, never pointer-shaped) — independently
    corroborates it's an integer mission-transition-phase flag, not a pointer. No code change (same
    reasoning as item -305: a comparison can't fault on a stale value). No soak queued (no code
    change to verify). Full derivation incl. both tool-bug writeups: `PORTING-STATE.md` Session 474.

-306. **(s473) Resolved item -296's flagged `hi16=0x8012, offset=-0x23a8` gap (141 sites) — found
    and FIXED a real methodology gap in that already-CLOSED item, closing 1 new guard site (120th)
    and classifying the rest.** A from-scratch taint-propagation scan
    (`scratch_s473_taint_scan_23a8.py`, N64Recomp repo, untracked) — validated against the KNOWN
    119-address guard list (exact subset match) before trusting any new finding — found: 119 sites
    already covered by item -296's `SIBLING_PTR_WRITE_GUARD` (matches exactly); **1 genuine unguarded
    write-through-the-reload** (`setupCameraMatrices`, `funcs_4.c`, reload `0x8001770C` -> a
    zero-offset `ADD32` copy survives two branches -> unconditional field write at label
    `L_800177A4`) — the s459 scan that produced the original 119 cleared its register-taint tracking
    on ANY reassignment, including zero-offset copies that preserve it, silently dropping this site;
    **2 false positives** (`renderLitMeshFaceGroup`, `do_lwl` unaligned-load helper calls —
    confirmed by direct read that the tainted register is a discarded merge-seed, not a deref); **10
    sites** where the raw reload is still live in `ctx->r4`/`ctx->r7` at a call to a REAL recompiled
    function (`appendRdpStateDl`/`emitAllocatedDLCommand`/`buildOrientedFaceGeometry`/
    `drawTextGlyphRect`) — crosses the function boundary via the guest ABI calling convention, a
    genuinely novel propagation path no prior bucket in this sub-arc had considered; **flagged, not
    chased** (would need each callee's own body read; plausibly the same safe DL-append-pointer
    idiom used throughout, but unverified); **19 no-use sites**, spot-checked 4/19 (not
    exhaustive — residual risk low but not zero, flagged for anyone revisiting this bucket). Fixed:
    added the confirmed site as `SIBLING_PTR_WRITE_GUARD`'s 120th entry (same mechanism/env flag as
    the other 119). Clean regen/build; `strings`-verified 119->120 with all 10 sibling guard families
    unchanged (no regression). Live-verify: 0 fires on the new site + all 120 + all siblings,
    `hangarbay-entry` n=31 (positive control); crashed at the very end on a NEW signature
    (`setByteAcrossEntryList+176`, bus error, `last-guest-pc=0x800aafa8`, the standard
    RDRAM-host-base-pointer pattern per the s219 overturned-conclusion entry), unrelated to any guard
    tested, filed not chased. 2nd independent confirm soak (`s473_siblingptrwrite120_confirm.sh`) ran
    s474: 0 crash, 0 `sibling-ptr-write-guard` fires (matches the manual live-verify exactly). Item
    -306 fully CLOSED, both confirm passes null on the new guard. Full derivation: `PORTING-STATE.md`
    Session 473.

-305. **(s472) M3 idiom-class audit: `hi16=0x8011, offset=0x63d4` global (`0x801163D4`, 12 bytes
    from item -299's `DL_BUFFER_POOL_GUARD` global) — CLASSIFIED AND DEFERRED, not a guard
    candidate.** The largest bucket in the s465 scan (170 `lw` reload sites, `funcs_6.c`x75/
    `funcs_3.c`x44/`funcs_4.c`x30/`funcs_7.c`x21), 0 `sw` write sites. A stratified 27-site sample
    (all 4 files, spanning every tool-reported chain-depth grouping) read directly showed 26/27 are
    the identical `sltu`/`bne` "current DL pointer < buffer-end limit" bounds-check idiom — the
    reload is COMPARED, never dereferenced or added-to; the 1 outlier is a save/restore (reload held
    live across a call, written back unchanged to the same slot, also no local deref). The
    classification tool's only 2 `hit_deref=True` flags in the whole bucket were confirmed FALSE
    POSITIVES on direct read (the tool anchors its report to the `lui` line, and what it flagged as
    `ADD32->WRITE_THROUGH` was an unrelated stack-pointer prologue adjustment a few lines later, not
    an operation on the reloaded value). Same disposition as item -302: an integer/boolean-valued use
    where guard-at-reload doesn't apply (a comparison can't fault on a stale value, and forcing the
    outcome would silently change game logic rather than harden against a wild pointer). No code
    change. **Tool bug found and documented**: `scratch_s468_shapecheck_generic.py` is
    case-sensitive on its offset argument and returns a silent "total sites: 0" false negative if the
    offset is passed in lowercase (generated code always emits uppercase hex literals) — always pass
    uppercase for future buckets.

-298..-304. **(s463-472) Eight more M3 idiom-class audit buckets from the s465 codebase-wide
    frequency scan, five CLOSED, one DEFERRED.** Item -298 (`DL_LIST_RESET_GUARD`, re-scoped ~111
    non-canonical `-0x5824` sites sharing item -291's global `0x8011A7DC`) CLOSED s464, 84/84 sites
    (27 folded into `DL_LIST_APPEND_GUARD` itself, 70 blanket-regex, 14 per-site literal-anchor).
    Item -299 (`DL_BUFFER_POOL_GUARD`, global `0x801163FC`) CLOSED s466, 84/84 sites
    (`funcs_3.c`x46/`funcs_4.c`x38), 2nd independent confirm soak s467. Item -300
    (`NODE_LIST_HEAD_GUARD`/`NODE_LIST_HEAD_WRITE_GUARD`, global `0x8011A4B8`) CLOSED s467, 20 read
    + 10 write sites (`funcs_3.c`/`funcs_4.c`) — the first bucket in this sub-arc to turn out to be
    two distinct downstream shapes, caught by reading full per-site context rather than a short
    sample window; 2nd independent confirm soak s468. Item -301 (`TEXDATA_TABLE_GUARD`, global at
    `hi16=0x8013,offset=-0x70F8`, `funcs_6.c` only) CLOSED s468, 31/31 sites — a texture-data-slot
    array base pointer with `idx*36` index arithmetic before the deref; substitutes `0x80000000u`
    (valid RDRAM base) rather than 0, since further index arithmetic would make 0 actively unsafe.
    2nd independent confirm soak s469: 0 fires on the new guard and all 6 siblings, `hangarbay-
    entry` n=31 (positive control); crashed on a NEW single-occurrence signature
    (`findOrCreateMaterial+776`/`emitMaterialTexturedDLAlt`, `last-guest-pc=0x80010b7c`, inside
    `submitSceneNodeRender`'s call subtree via `runHangarSelectionFrame`) — `sibling-ptr-write-
    guard` (the instrument covering that function's own open wait-for-recurrence breadcrumb, item
    -296) did NOT fire, so not confirmed as that mechanism; filed, not chased. Item -302
    (`hi16=0x8013,offset=0x7CE4`, 45 sites/9 files) CLASSIFIED AND DEFERRED s468, not closed: the
    reloaded global is a small INTEGER INDEX (not a pointer), 17 distinct downstream shapes, no
    single guard placement covers all sites without speculation. Item -303
    (`TEXDATA_PTR_ARRAY_GUARD`, global at `hi16=0x8013,offset=-0x7104`, `funcs_6.c` only, 12 bytes
    from item -301's global) CLOSED s470, 29/29 sites — the s470 rule-8 mandatory-pivot iteration's
    discriminating probe: classification found two raw-pointer risk shapes (direct use as an
    `rs_free()` argument / write-loop base with no arithmetic, and `idx*4` array-of-pointers access),
    both distinct from item -302's confirmed integer-index shape; substitutes `0x80000000u`, same
    reasoning as item -301. Clean build/live-verify: 0 new-guard fires, 0 fires on all 7 siblings
    (no regression), `hangarbay-entry` n=31 (positive control); crashed on `last-guest-pc=0x80054744`
    inside `tickWrappingTimerAccumulatorList` — the EXACT already-catalogued, already-PARKED
    `m5-audio-destub-tickwrap-divzero-craftselect` compiler div-by-zero-trap signature (first seen
    ~s344, `docs/PROJECT-OVERVIEW.md`), unrelated to any guard tested, filed not chased. 2nd
    independent confirm soak (`s470_texdataptrarray_confirm.sh`) ran s471: 0 fires on the new guard
    and all 7 siblings, `hangarbay-entry` n=31 (matches the manual live-verify exactly); crashed on a
    DIFFERENT signature this time — a host-side Metal.framework SIGSEGV inside
    `fscache_insert_and_retain` (`last-guest-pc=0x800ab0e0`, near but not identical to the s463/s468
    `loadCutsceneAssetsByIndex+1860` crash site) — an async shader-compiler-thread crash unrelated to
    any game-code guard, filed not chased (same family as items -10/-9's Metal-compiler-SIGSEGV
    class). Item -303 fully CLOSED, both confirm passes null on the new guard. Every CLOSED item's
    live-verify/confirm-soak result matches item -287's established true-negative baseline.
    Session-by-session derivation, per-site classification methodology, and every soak result:
    `docs/PROJECT-OVERVIEW.md` §18 (s463-469; s470-471 detail folds in at next maintenance pass).

-304. **(s471) M3 idiom-class audit: `MATERIAL_ARRAY_PTR_GUARD`, `0x8012($reg)`→`-0x5BBC` global,
    30 `lw` reload sites across 4 files (`funcs_3.c`x5/`funcs_4.c`x10/`funcs_6.c`x14/`funcs_7.c`x1).
    CLOSED s471, 30/30 sites, first multi-file bucket in this sub-arc.** Single writer
    `buildAndRegisterDefaultMaterial` (funcs_4.c:27911, stores an `rs_malloc()` result) vs. 30
    reader sites in 4 different functions/files — same uninitialized/stale-global-reload shape as
    every closed bucket in this lineage. `scratch_s468_shapecheck_generic.py 8012 -5BBC` auto-
    classified 24/30 sites as `ADD32→DEREF` (real pointer risk); the remaining 6 `hit_deref=False`
    sites were read directly from source per the s470 lesson (tool false negative, not evidence of
    non-pointer use) and confirmed the same two risk shapes as item -303: `idx*4` array-of-pointers
    access (funcs_3.c:26341/28435) and direct-use-with-no-arithmetic (funcs_4.c:29352 passes the raw
    reload straight into `rs_free()`; funcs_4.c:28004/funcs_6.c:14323/funcs_6.c:14728 use it as a
    write/read-loop base). No item -302-style integer-index shape present — clean single-guard
    bucket despite spanning 4 files. Substitutes `0x80000000u`, same reasoning as items -301/-303.
    Regex verified 30/30 against raw `MEM_W(reg, -0X5BBC)` line counts per file
    (`scratch_s471_test_regex_5bbc.py`); the bucket's one `sw` (write) site excluded by construction.
    Clean build; all 8 pre-existing sibling guards unchanged (84/84/84/119/20/10/31/29); `strings`
    confirms 30 `material-array-ptr-guard` tag occurrences. Live-verify: 0 new-guard fires, 0 fires
    on all 8 siblings, `hangarbay-entry` n=34 (positive control); full 300s/250s-keys schedule
    survived with 0 `[CRASH]` markers at all — unlike most sessions in this sub-arc, this run hit no
    crash of any kind. 2nd independent confirm soak (`s471_materialarrayptr_confirm.sh`) ran s472: 0
    fires on the new guard and all 8 siblings, `hangarbay-entry` n=31 (matches the manual pass
    closely); crashed on a 3rd distinct byte-offset of the already-catalogued `heapFreeListDequeue`
    crash family (`+31924`, `last-guest-pc=0x8000d738`; prior sightings `+19316`/`+32596`), unrelated
    to any guard tested, filed not chased. Item -304 fully CLOSED, both confirm passes null on the
    new guard.

-291..-297. **(s454-462) Three M3 idiom-class audits found via an s454 concurrent-process
    collision, all now CLOSED.** Item -291 (`DL_LIST_APPEND_GUARD`, global `0x8011A7DC`, 57 sites,
    `funcs_3.c`/`funcs_4.c`) CLOSED s456: 0 crash, 0 fires across a full schedule. Item -296
    (`SIBLING_PTR_WRITE_GUARD`, sibling global `0x8011DC58`, 119 sites) CLOSED s459 (rule-8
    mandatory pivot off item -292): 0 `[CRASH]`, 0 fires; 10 of its 119 sites sit in
    `submitSceneNodeRender`, now a discriminating instrument for that function's still-open
    wait-for-recurrence breadcrumb (0 fires there so far, including s469's new crash — see item
    -301/-302 above). **AMENDED s473 (item -306): the s459 scan had a register-taint-tracking gap
    that silently dropped 1 real site (120th, `setupCameraMatrices`) — found, fixed, and
    soak-confirmed; the guard family is otherwise unchanged.** Item -292 (`SONGTEMPO_TABLE_GUARD`, 43 sites/6 reader functions,
    `funcs_25.c`) CLOSED s462 — see its own entry below. Full session-by-session detail:
    `docs/PROJECT-OVERVIEW.md` §17.

-292. **(s455-462) M3 idiom-class audit: `SONGTEMPO_TABLE_GUARD`, `0x29C0($reg)` → global
    `0x801529C0`, the MusyX song-sequencer's "current song track" base pointer, `funcs_25.c`.
    CLOSED s462, 43/43 sites.** Same uninitialized/stale-global-reload shape as the closed
    `-0x25A4` family: only one site (`tickAllActiveSongs`) writes the global; 6 reader functions
    (43 sites) only ever read it with no guarantee of prior initialization. Fixed and
    soak-confirmed across all 6: `updateSongTempoTickRate` (4, s454), `tickScheduledSongEvents`
    (5, s457), `stepSongPitchBendLanes` (5, s457), `stepSongModulationLanes` (5, s458),
    `advanceSongRegion` (12, s460), `stepActiveSongTracks` (12, s462, the largest reader function
    at ~744 lines — confirmed NOT affected by the recompiler's cross-function shared-tail-merge
    quirk despite being flagged the same way). Every soak across the whole arc (s454-462)
    delivered the same null result: 0 guard fires, matching item -287's established baseline for
    this guard-idiom class. Per-site bail method and full session detail:
    `docs/PROJECT-OVERVIEW.md` §17.

-282..-290. **(s445-453) `static5-rename-orphan-sweep`, fully CLOSED.** The s427 duplicate-symbol
    fix (item -261..-267) split a ~13,770-line anonymous merged blob back into ~15 real functions,
    orphaning every pre-s427 guard/patch hardcoded to the old `static_N_0xADDR` names. Root-caused
    and fixed across 6 sessions: `GETDATITEM_GUARD`, `HANGARLIST_GUARD` family, the combined
    s284/s285 deref-guard list, `S390_H2A`/`S390_H2B`, `G1`-`G32`+`A`-`E`, and 9
    `composeNpcOrientationMatrix` sites — 94 sites total. s449 supplied the arc's positive control:
    unconditional REACHED counters showed `HANGARLIST_GUARD` reached 245000+ times with 0 trips —
    confirmed correct hardening, not dead code. s453 investigated the last tracked remainder
    (`S392_H3A`/`S393_H3B`, 50 sites) and found it already fully covered by earlier guard sweeps —
    CLOSED, no code change (item -290). Incidentally opened one new single-occurrence crash class
    (`NAN_CHECK` assert in `transformVec3ByMat34`, item -281, filed not chased) and fixed a
    `tools/probe.sh` false-negative bug (silently reported crashed soaks as clean, s447). Only
    `BREADCRUMB7` (diagnostic, lowest priority) remains untouched. Full detail:
    `docs/PROJECT-OVERVIEW.md` §16 (s445-451); raw: `PORTING-STATE` Sessions 445-453.

-274..-280 (and -263). **(s438-445) BREADCRUMB18/free-list-guard arc, all resolved or parked.**
    Item -263 (5 recurrences) RECLASSIFIED PARKED s441: full breadcrumb coverage (BREADCRUMB18,
    item -275) proved the real mechanism was a THIRD free-list-cache-head sibling bug
    (`FREELIST_NEXT_GUARD`, item -277, 105 sites: HEAD pointer validated but its "next" pointer
    read-back wasn't) misattributed to item -263 by superficial signature match alone. Falsifying
    condition unchanged: a NEW occurrence where BREADCRUMB18 reports a real address inside
    `updateHangarBayScene`'s own body. The fix surfaced a new single-occurrence crash class (item
    -278, thread-scheduler SIGSEGV) that a diagnostic instrument (item -280) PARKED s445 after ~10
    soaks without recurrence; s442 found a queued soak's apparent failure was a soak-script
    off-by-one bug, not a crash (item -279). Full detail: `docs/PROJECT-OVERVIEW.md` §16 (s438-445);
    raw: `PORTING-STATE` Sessions 438-445.

-268..-273. **(s432-437) Duplicate-symbol catalogue closed (18/18); the `0x801163B0` free-list-
    cache-head-deref idiom swept at scale (107 sites, `GENERIC_CACHE_GUARD`, plus a 7-site `$a1`
    sibling, `CACHE_HEAD_A1_GUARD`); item -263 progressively localized through two rounds of
    breadcrumb-coverage misattribution (BREADCRUMB16, BREADCRUMB17).** Full detail:
    `docs/PROJECT-OVERVIEW.md` §16, `PORTING-STATE` Sessions 432-437.

-261..-267. **(s424-431) The `startPlayerSlotAnimationChannelLooping`-family crash chain: 3
    siblings guarded, then SUPERSEDED by the real root cause** — a duplicate-symbol-name collision
    truncating `initCraftSelectScreen`'s body to 1 instruction, whose fix un-truncated code that had
    never run before and triggered a cascade of 3 further crashes. Last one (item -267, a stray
    write in `mallocCraftSelectionData`) **did NOT recur** after a sibling duplicate-symbol fix
    (single-run, not independently confirmed). Full detail: `docs/PROJECT-OVERVIEW.md` §16,
    `PORTING-STATE` Sessions 424-431.

-259. **(s422) `0x800290d4` "six independent triggers" lead — INVESTIGATED AND CLOSED, not a bug.**
    `0x800290d4` is `inflate_fast`'s own clean return, reported by a sparse breadcrumb (8/50 files);
    `atos` symbolication of 5/6 crash logs found FIVE DIFFERENT real crash functions, each already
    catalogued, not one shared mechanism. All six stay parked, correct and safe. `PORTING-STATE` 422.

-249. **(s400-421) M4 item -249: `main_overlay.txt` phantom-overlay-function relocation — CLOSED
    s421, no outstanding action.** 784 functions relocated to their correct overlay across 21 sessions;
    10 genuinely-buggy functions parked in `m4_known_bad.txt`, 4 more in `m4_known_skip.txt`. 0
    actionable candidates remain per s421's fresh regen. Full arc: `docs/PROJECT-OVERVIEW.md` §15; raw:
    `PORTING-STATE` Sessions 400-421.

-6. **(s53/s54→s399) M4 — the 3 `[missing-func]` addresses: DONE, CLOSED s399.** s54's fix was dead on
    arrival — silently shadowed by pre-existing duplicate entries at the same addresses in
    `main_overlay.txt` (first-discovered instance of item -249's family). Root-caused and fixed s399 by
    deleting the 3 duplicate lines; verified 3/3 post-fix runs, same-run positive control. Full detail:
    `PORTING-STATE` Session 399.

-239..-247. **(s389-397) M3 idiom-class audit resumption: `hangarInitialize`'s `-0x25A4`
    hangar-list-pointer family and the "Lookup" struct-family fully CLOSED, plus two independent
    guard-placement bugs found+fixed and a codebase-wide frequency scan for the next comparable idiom
    class — negative result, closing the pure-idiom-audit discovery method for now** (superseded by the
    s426-438 duplicate-symbol/breadcrumb thread, PROJECT-OVERVIEW §16, which reopened live M3 work
    without needing a new discovery tool). Full detail: `docs/PROJECT-OVERVIEW.md` §14; raw:
    `PORTING-STATE` Sessions 389-397.

-231..-238. **(s377-386) Fixup function-scope backport, batches 1-9: 176 file-scoped guard patches
    identified, 168 converted to function-scope, 8 confirmed permanent design exclusions. CLOSED OUT
    s386.** Process lessons (sandbox-permission delegation, scope-misattribution catches, address-not-
    name exclusion): `docs/PROJECT-OVERVIEW.md` §13. Raw: `PORTING-STATE` Sessions 377-386.

-160..-230. **(s297-376) M5 audio de-stubbing arcs — gate-byte-reversal/VI=640-stall, Step 5
    guard-hunting (heapWalker GUARD5), gate-promotion/crash-rate-comparison, Step 6 PCM-sanity +
    C88 pre-title-hang/VI-trigger — ALL CLOSED, no outstanding M5 thread.** Every mechanism, guard
    site, and soak-tooling lesson: `docs/PROJECT-OVERVIEW.md` §9-§12; raw: `PORTING-STATE` Sessions
    297-376.

-159..-14 (excluding -20, kept below). **Ten closed investigation lineages, s99-s337 — all CLOSED, no
    outstanding action.** Whack-a-mole guard-gap chases (`composeNpcOrientationMatrix`,
    `renderUnlitMeshFaces`, `heapWalker`, `heapFreeListDequeue`, `-0x25A4` family, breadcrumbs B2-B14),
    the audio-array-corruption race fix, the `submitDmaRequestBatch` indirect-caller find, the
    CALayer/campose SIGSEGV hunt, the regen-pipeline-idempotency root cause, and the M5 audio gate/
    VI=640-stall chase (item -160..-230 above). One-paragraph-per-lineage summaries:
    `docs/PROJECT-OVERVIEW.md` §9; full raw detail: `PORTING-STATE` Sessions 99-337.

-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic).** Root cause:
    `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c` file that already exists on disk, so
    any patch whose regex anchor survives its own insertion stacks a duplicate on the next
    `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every
    regen is mandatory but **not sufficient by itself** -- residual intermittency's root cause is
    still unknown. **Standing rule**: audit the patch report for anything other than the expected `xN`
    count after every `fixup_game_funcs.py` run. Full detail: `PORTING-STATE` Sessions 120, 121, 126.

-11. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89), RECURRED s424, ROOT-CAUSED AND
    GUARDED s425.** s424 hit it as a sibling of item -261's guarded `startPlayerSlotAnimationChannelLooping`
    crash; s425 root-caused and guarded it (wild `$a0` arg, same never-initialized-slot root state) —
    see item -261 for the full trace.
-10/-9. **M3 — Metal-shader-compiler SIGSEGV reproducibility** (s83 spline1: SIGSEGV inside `Metal.framework`'s `MTLCompilerFSCache`, no source on our side; still one data point). **Confirm the s83 spline div0 guard actually engages**: 0/5 fires so far (still 0 after s88/s89/s90); real fix by code inspection (genuine 0/0 IEEE division) but no same-run positive control yet.
-8. **M3 — characterize `frameStartReset` SIGBUS.** 3 occurrences (s85, s108, s156 — the 3rd, `+532`, at a call chain byte-identical to `composeNpcOrientationMatrix`'s own, raising a shared-dispatcher hypothesis); no located faulting instruction in any of the 3.
-7. **M3 — HOLD_S=60 craft stick (M3 DoD body)** once earlier items clear: `PROBE_MODE=start_only HOLD_S=60` marks 10/25/40, document the phase timeline. Gate already keeps black off; residual S1 `fs` freeze (~3769-3872 plateau) may still stall animation.
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
