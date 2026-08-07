# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Seventeen passes
   so far (s295-330 x5, s346, s355, s364, s371, s380, s391, s398, s409, s429, s438, s444, s451, s461)
   kept the file oscillating around the cap as new session detail accrues — full per-pass migration
   targets in git log; PROJECT-OVERVIEW §16-§17 hold the most recent two arcs. 35 KB remains a
   stretch target, not a hard floor -- the "Current truth" env-var/timeline prose and the
   Regeneration section's Standing warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (full arc: PROJECT-OVERVIEW
   §10-§12). Next M5 work needs a genuinely new lead.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. Closed arcs so
   far, oldest to newest: the original `-0x25A4` family (s283-396); the s426-429 duplicate-symbol-name
   thread (18/18 pairs) and its s438-445 BREADCRUMB18/free-list-guard follow-on (items -261..-280,
   -263); that follow-on's own s445-451 fallout, the `static5-rename-orphan-sweep` (items -282..-290
   — s449 confirmed the whole guard idiom class is correct hardening, not a live crash source); item
   -291 (`DL_LIST_APPEND_GUARD`, 57→84 sites, s454/456, extended s463); item -296
   (`SIBLING_PTR_WRITE_GUARD`, 119 sites, s459); item -292 (`SONGTEMPO_TABLE_GUARD`, 43/43 sites
   across 6 reader functions, s454-462); item -298 (`DL_LIST_RESET_GUARD`, 84/84 sites — 70
   blanket-regex s463 + 14 per-site-literal-anchor s464, CLOSED s464); item -299
   (`DL_BUFFER_POOL_GUARD`, global `0x801163FC`, 84/84 sites, `funcs_3.c`x46/`funcs_4.c`x38,
   CLOSED s466, 2nd independent confirm soak s467); and item -300 (`NODE_LIST_HEAD_GUARD`/
   `NODE_LIST_HEAD_WRITE_GUARD`, global `0x8011A4B8`, 20 read-guard + 10 write-guard sites,
   `funcs_3.c`/`funcs_4.c`, CLOSED s467 — the first bucket in this scan-driven sub-arc to turn out
   to be TWO distinct downstream shapes rather than one, caught by reading full per-site context
   instead of a short sample window). **No next candidate identified yet — s465's scan surfaced
   several other unexamined buckets (see item -300 below), the next session should classify the
   top-ranked one.**

Sanctioned tooling work unit (backport function-scoped matching to the file-scoped-only guard patches
in `fixup_game_funcs.py`): **CLOSED OUT as of s386/s388, no live work remains** — see item -231..-238
below and `docs/PROJECT-OVERVIEW.md` §13. M4's largest item (-249) and its `0x800290d4` follow-on
(-259) are both CLOSED — see those items below for status.

## Current truth (established by session 295; unchanged, reviewed through s462)

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
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't consume
it; the 3 `[missing-func]` addresses (**DONE s399**, item -6 below); the `main_overlay.txt`
phantom-overlay-function family (**CLOSED s421**, item -249 below) and its apparent `0x800290d4`
clustering (**CLOSED s422**, not a shared bug, item -259 below).

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.

## Next steps, in order of expected value (s295)

Numbering convention (fixed s295, was previously three colliding sequences): items are
numbered highest-magnitude-negative (top, newest/highest priority) counting up to -1 (bottom,
oldest). Highest number allocated so far is -300 (this item); items are never renumbered when
compacted into a range pointer. The next NEW item takes -301.

-300. **(s467) M3 idiom-class audit: `NODE_LIST_HEAD_GUARD` (read) / `NODE_LIST_HEAD_WRITE_GUARD`
    (write), global `0x8011A4B8` (`hi16=0x8012,offset=-0x5B48`), `funcs_3.c`/`funcs_4.c`
    linked-list-insert-at-head code (10 near-identical functions). CLOSED s467, 20/20 read-guard +
    10/10 write-guard sites.** Item -299's own next-candidate pointer; s465's scan ranked this the
    most concentrated remaining bucket. Classified with `scratch_s467_classify_5b48.py` (N64Recomp
    repo, untracked): all 20 raw sites share a byte-identical reload (`ctx->rL = MEM_W(ctx->rL,
    -0X5B48)`) immediately followed by a deref-read (`ctx->rD = MEM_W(ctx->rL, 0X0)`) — same
    read-off-the-raw-reload crash risk as `DL_BUFFER_POOL_GUARD` if `rL` is wild. **Unlike item
    -299, full per-site context (not a short sample window — the exact trap that cost s465/s466 a
    session) showed this bucket is TWO distinct downstream shapes, not one:** 10 "first-of-pair"
    sites where `rD` gates a `bnel`-delay-slot conditional write (`if (ctx->rD != 0) { MEM_W(0X4,
    ctx->rD) = ctx->rPayload; goto L; } goto skip; <dup, dead>; skip:` — the same idiom
    `FREELIST_NEXT_GUARD`, s441, already fixed for a sibling global) needing only the read guard
    (forcing `rD=0` on invalid `rL` makes the `if` false, safely skipping both write copies); and
    10 "second-of-pair" sites (the SAME 10 functions reloading the SAME global again a few lines
    later) where the reload register itself, never reassigned, is later used DIRECTLY as a SECOND
    unconditional write address (`MEM_W(0X0, ctx->rL) = ctx->rPayload`, usually the delay slot of
    the function's own `jr $ra`) — the SAME write-through-reload risk `DL_LIST_RESET_GUARD` (item
    -298) established for a different global, needing its own separate write guard. 9/10 of the
    second shape are byte-identical and regex-anchor cleanly; the 10th (`funcs_3.c` `0x80008080`/
    `0x80008090`) has a pre-existing `s436 CACHE_HEAD_A1_GUARD` block spliced in between by an
    earlier unrelated patch, breaking regex adjacency — handled by its own per-site literal anchor,
    same discipline as `DL_LIST_RESET_GUARD`'s 14-site remainder. Both regexes match-count-verified
    with a standalone test script (`scratch_s467_test_regex.py`, N64Recomp repo, untracked) against
    the actual on-disk text before being written into `fixup_game_funcs.py`. Clean regen+build
    (20/20 `NODE_LIST_HEAD_GUARD` + 10/10 `NODE_LIST_HEAD_WRITE_GUARD`, no regression in
    `DL_LIST_APPEND_GUARD`(84)/`DL_LIST_RESET_GUARD`(84)/`DL_BUFFER_POOL_GUARD`(84)/`SIBLING_PTR_
    WRITE_GUARD`(119)); `strings` on the binary confirms 20 `node-list-head-guard` + 10
    `node-list-head-write-guard` format strings. Live-verify: **0 `[CRASH]` across the ENTIRE 300s
    schedule** (all 10 scheduled key presses fired — the first soak in several sessions to run the
    full schedule clean rather than hitting an unrelated background-noise crash partway through), 0
    fires on both new guards (matches item -287's established true-negative baseline), 0 fires on
    every sibling guard (no regression), `hangarbay-entry` n=33 (positive control). Confirmation
    soak queued: `scratch/agent/soak_queue/s467_nodelisthead_confirm.sh`.
    **Next candidate, not yet examined** (from s465's scan, ranked by concentration): the more
    scattered buckets `hi16=0x8013,offset=0x7CE4` (45 sites, 9 files), `hi16=0x8013,offset=-0x70F8`
    (31, `funcs_6.c` only), `hi16=0x8012,offset=-0x5BBC` (30, 4 files), `hi16=0x8013,offset=-0x7104`
    (29, `funcs_6.c` only), `hi16=0x8011,offset=-0x35E0` (23, 9 files), `hi16=0x8013,offset=0xB50`
    (21, 11 files). None are as tightly concentrated in the `funcs_3.c`/`funcs_4.c` lineage core as
    items -299/-300 were, so budget extra time for shape classification before assuming a single
    guard pattern applies.

-299. **(s465-467) M3 idiom-class audit: `DL_BUFFER_POOL_GUARD`, global `0x801163FC`
    (89 bytes past the `0x801163B0` free-list-cache-head global), `funcs_3.c`/`funcs_4.c`
    DL-buffer-pool code (`allocateDisplayListBuffer`/`emitAllocatedDLCommand` and siblings).
    CLOSED s466, 84/84 sites, 2nd independent confirm soak s467.** Found s465 by a fresh
    codebase-wide frequency scan of every `lui $reg,0x80XX; lw $reg,OFFSET($reg)` global-reload
    idiom (not just previously-known offsets) across all 50 `RecompiledFuncs/funcs_*.c` files
    (`scratch_s465_scan.py`, N64Recomp repo, untracked; caught a case-sensitivity bug in its own
    exclude-list normalizer along the way). 87 raw reload sites (`funcs_3.c`x46, `funcs_4.c`x38,
    `funcs_6.c`x3); a shape pass (`scratch_s465_classify_63fc.py`) split off 3 `funcs_6.c`
    `COMPARE_ONLY` sites (benign, out of scope) from 84 `funcs_3.c`/`funcs_4.c` sites sharing a
    lazy-init idiom: `ctx->rL = MEM_W(ctx->rL, 0X63FC); ctx->rD = MEM_W(ctx->rL, 0X0); if
    (ctx->rD != 0) goto Lalready; MEM_W(0X0, ctx->rL) = ctx->rNew; goto Ldone;` (read
    `global->field0`; if non-null skip the write). Both the read and write deref the unvalidated
    reload — same structural risk as `DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`. s466 ran the
    shape-uniformity audit s465 left open (a CONDITIONAL BRANCH sits between the read and write,
    with a compiler-arbitrary delay-slot instruction only sampled at 5 sites):
    `scratch_s466_shapecheck_63fc.py` (N64Recomp repo, untracked) dumped and normalized the full
    reload-through-write block for all 84 sites and found 100% (84/84) adjacency between the
    reload and the READ deref and 100% (84/84) reach a same-register write within 40 lines — the 7
    "distinct" normalized shapes it found are entirely explained by the harmless delay-slot
    instruction (`nop` at 73 sites, various `addu $reg,$reg,$zero` register combos at 11),
    confirming the write is only ever reachable through the read's result. That let the fix guard
    the READ alone: validate `ctx->rL` right after the reload; if invalid, skip the read and force
    `ctx->rD` to a nonzero sentinel (1) so control takes the "already initialized" branch (which
    contains the write too) — NOT "substitute 0", which would route into the write branch and
    still deref the invalid `ctx->rL` as a write address. `DL_BUFFER_POOL_GUARD` landed in
    `fixup_game_funcs.py` (regex anchored to just the 3-instruction lui/reload/read-deref prefix,
    leaving the branch/delay-slot/write untouched). Clean regen+build (84/84 sites: `funcs_3.c`x46
    + `funcs_4.c`x38, no regression in sibling guard counts), `strings` on the binary confirms 84
    `dl-buffer-pool-guard` format strings. Live-verify: 0 `[CRASH]` from the guard itself, 0
    `dl-buffer-pool-guard` fires (matches item -287's established true-negative baseline),
    `hangarbay-entry` n=32 (positive control, content reached), 0 fires on every sibling guard (no
    regression). Crashed later in the same run on `coalesceFreeHeapBlocks+4424`/
    `last-guest-pc=0x8000247c` — the SAME already-catalogued heap-walker background-noise family
    seen at s464's confirm soak (documented since s354-366), unrelated to this guard, filed not
    chased. **Confirmation soak run s467**: `s466_dlbufferpool_confirm` (rc=3, 170s) — full
    `run.log` check (not just the probe.sh summary line) found 0 fires across all 4 sibling guards,
    `hangarbay-entry` n=34 (reachable), crashed at 121.6s on the SAME `coalesceFreeHeapBlocks+4424`
    family again — a 2nd independent confirmation of the true-negative result, unrelated to any
    guard tested.

-298. **(s463-464) M3 idiom-class audit: `DL_LIST_RESET_GUARD`, re-scoped the ~111 non-canonical
    `-0x5824` population (same global as item -291, `0x8011A7DC`) flagged at s454/456. CLOSED s464,
    84/84 sites.** item -291's original scan was regex-scoped too narrowly and silently missed a
    breadcrumb-dialect variant of its OWN canonical shape. Programmatic re-classification
    (`scratch_s463_classify_5824.py`/`scratch_s463_verify_reset.py`, N64Recomp repo, untracked)
    found the 111 split three ways: 27 were actually-canonical (missed because their function has
    full per-instruction `g_rs64_last_guest_pc` tracing, a breadcrumb dialect that puts the
    breadcrumb between each instruction's own comment and its ctx-> line, a slot item -291's regex
    never tolerated) — folded into `DL_LIST_APPEND_GUARD` itself s463 by widening its regex with
    matching inside-instruction breadcrumb slots, now 84/84 canonical sites total. 70 are a
    genuinely different, byte-identical shape — landed s463 as `DL_LIST_RESET_GUARD`: the reloaded
    global is used DIRECTLY as a write address (`MEM_W(0X0, ctx->rload) = ctx->rnode;`, no
    intervening deref at all, structurally the same risk as `SIBLING_PTR_WRITE_GUARD`/item -296) —
    one blanket regex substitution (rload backreferenced end-to-end, verified programmatically not
    sampled). The remaining 14 (5 `funcs_3.c`, 9 `funcs_4.c`) had 1-4 lines of unrelated intervening
    code between the reload and the write pair (confirmed by direct source read that none of it
    touches the reload register, `$v0`/`ctx->r2` uniformly across all 14) — landed s464 via
    `SIBLING_PTR_WRITE_GUARD`'s own per-site-literal-anchor method (`_DL_LIST_RESET_EXTRA_SITES` in
    `fixup_game_funcs.py`, each anchor confirmed tree-wide-unique by a standalone script,
    `scratch_s464_verify_dllistreset14.py`, before patching), reusing `DL_LIST_RESET_GUARD`'s own
    env var (`ROGUESQ_LOG_DL_LIST_RESET_GUARD`) and stderr tag (`[dl-list-reset-guard]`) so both
    mechanisms count as one instrument. Same "skip the write" remediation precedent throughout.
    Manual live-verify: s463's soak ran the full 300s schedule with 0 fires on any of the 4 sibling
    guards; s464's soak ran ~126s before crashing on `coalesceFreeHeapBlocks+4424`
    (`last-guest-pc=0x8000247c`) — the SAME already-catalogued, already-closed heap-walker
    background-noise family documented since Session 366, unrelated to any guard tested, filed not
    chased — with 0 fires on `dl-list-reset-guard`/`dl-list-append-guard`/`sibling-ptr-write-guard`
    and `hangarbay-entry` reaching n=2700 (reachability confirmed). Both null results match this
    whole guard-idiom class's established true-negative baseline (item -287). Confirmation soaks, both
    now run: `s463_dllistguards_confirm` crashed at 19.4s on `loadCutsceneAssetsByIndex+1860`
    (`last-guest-pc=0x800aafb8`) — a single-occurrence new offset inside a function already known to
    have multiple unguarded holes found piecemeal (`+668` fixed s254 as `HANGARLIST_GUARD`, `+948`
    fixed s283), filed not chased per the no-reactive-single-crash-chase rule; `s464_dllistreset14_confirm`
    crashed at 116.4s on `last-guest-pc=0x80065e94`, symbolized here as `initVec4TripletFromArgs+68` —
    the SAME already-catalogued `NAN_CHECK`/misattributed-symbol family documented since ~s327
    (recurs under many different `pc-symbol` labels at this exact guest PC — `trackResourceListWithMappingTables`,
    `slotDispatcherIter`, others — a known symbolication-collision artifact, not a new bug), filed not
    chased. Neither confirm soak's crash relates to any of the 4 sibling guards tested. **CLOSED: the
    whole re-scoped `-0x5824` non-canonical population (111 sites) is fully accounted for** (27
    canonical + 70 blanket-regex + 14 per-site). Next candidate: item -299 (s465), see above.

-291..-297. **(s454-462) Three M3 idiom-class audits found via an s454 concurrent-process
    collision, all now CLOSED.** Item -291 (`DL_LIST_APPEND_GUARD`, `-0x5824($reg)` → global
    `0x8011A7DC`, 57 sites, `funcs_3.c`/`funcs_4.c`) found s454, CLOSED s456: 57/57 sites
    built/verified/soaked, 0 crash, 0 fires across a full 300s schedule (`hangarbay-entry`
    n=3000); its queued confirm soak later crashed on an unrelated already-catalogued signature.
    Item -296 (`SIBLING_PTR_WRITE_GUARD`, `-0x23A8($reg)` → sibling global `0x8011DC58`, 119
    sites, same two files) found AND CLOSED same session s459 (the rule-8 mandatory pivot off item
    -292, after 3 straight iterations without closing it): 119/119 sites, 0 `[CRASH]`, 0 fires
    across a full schedule; 10 of its 119 sites sit in `submitSceneNodeRender`, now a
    discriminating instrument for that function's still-open wait-for-recurrence breadcrumb (2
    independent single-occurrence crashes, different `last-guest-pc` each time, not confirmed as
    one bug) — 0 fires there so far. Item -292 (`SONGTEMPO_TABLE_GUARD`, 43 sites across 6 reader
    functions, `funcs_25.c`) advanced from 4/43 to 43/43 across s454/s457/s458/s460/s462 and
    CLOSED s462 — see its own entry below. Full session-by-session detail (per-site bail
    derivations, scan methodology, every soak result): `docs/PROJECT-OVERVIEW.md` §17.

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
    `docs/PROJECT-OVERVIEW.md` §17. Next idiom-class-audit candidate, not yet started: ~111
    non-canonical `-0x5824` sites (same global as the closed item -291, non-adjacent load/deref
    pair).

-290. **(s453) `S392_H3A`/`S393_H3B` (50 sites, items -282..-289's own tracked remainder):
    INVESTIGATED AND CLOSED, no code change — all 50 sites already covered by earlier guard
    sweeps, not a partial-coverage case.** Closes the `funcs_40.c`/`funcs_27.c`-gated orphan-sweep
    inventory except `BREADCRUMB7` (diagnostic, lowest priority). Full detail: PROJECT-OVERVIEW §16,
    `PORTING-STATE.md` Session 453.

-282..-289. **(s445-451) `static5-rename-orphan-sweep`: the s427 duplicate-symbol fix (item
    -261..-267) split a ~13,770-line anonymous merged blob back into ~15 real functions
    (`hangarInitialize` never existed as a real function post-s427), orphaning every pre-s427
    guard/patch hardcoded to the old `static_N_0xADDR` names or file locations. Root-caused and
    fixed across 6 sessions: `GETDATITEM_GUARD` (6 sites), `HANGARLIST_GUARD` family (4 sites),
    the combined s284/s285 deref-guard list (30 sites), `S390_H2A`/`S390_H2B` (11 sites),
    `G1`-`G32` + a sibling `A`-`E` family (34 sites), and 9 further doubly-orphaned
    `composeNpcOrientationMatrix` sites — 94 sites total, same method every time (standalone
    Python scan confirms tree-wide anchor uniqueness before ungating, `SystemExit`-on->1-match
    hard guard added). s449 closed the arc's central open question with a positive control:
    unconditional REACHED counters showed the sibling `HANGARLIST_GUARD` family reached 245000+
    times with 0 trips — a true negative, not dead code, so this whole guard idiom class
    (`-0x25A4`/table-deref/free-list-cache-head) is confirmed correct hardening unlikely to ever
    fire under normal play, not a live crash source. Incidentally: found+fixed a `tools/probe.sh`
    false-negative bug (silently reported crashed soaks as clean, s447) and opened one new,
    unrelated single-occurrence crash class (`NAN_CHECK` assert in `transformVec3ByMat34`, item
    -281, filed not chased). **Closes the `funcs_40.c`-gated orphan inventory except
    `S392_H3A`/`S393_H3B`** (50 sites, known `GENERIC_CACHE_GUARD`-redundancy wrinkle on
    `L_800ADB2C` — check before patching) **and `BREADCRUMB7`** (diagnostic, lowest priority).
    `S392_H3A`/`S393_H3B` is `scratch/agent/NEXT.md`'s current top work unit. Full detail:
    `docs/PROJECT-OVERVIEW.md` §16 (s445-451); raw: `PORTING-STATE` Sessions 445-451.

-274..-280 (and -263). **(s438-445) BREADCRUMB18/free-list-guard arc, all resolved or parked.**
    Item -263 (s426, recurred s433/436/437/440) RECLASSIFIED PARKED s441: none of its 5 occurrences
    ever showed a fault inside `updateHangarBayScene`'s own body; adding full breadcrumb coverage
    there (BREADCRUMB18, item -275, ~6805 lines/2643 writes, motivated by a 4th recurrence at s438,
    item -274) let s441 prove the real mechanism was a THIRD free-list-cache-head sibling bug
    (`FREELIST_NEXT_GUARD`, item -277: the HEAD pointer is validated before deref but the "next"
    pointer read back from it is not; 105 sites fixed) misattributed to item -263 by superficial
    signature match alone — an entry counter (item -276) supplied the same-run positive control
    that made the misattribution provable. Falsifying condition unchanged: a NEW occurrence where
    BREADCRUMB18 reports a real address inside `updateHangarBayScene`'s own body. The
    `FREELIST_NEXT_GUARD` fix surfaced a new, unrelated single-occurrence crash class (item -278:
    SIGSEGV in the thread-scheduler/semaphore runtime, no game-code frames); s442 found its confirm
    soak's apparent "failure" was a soak-script off-by-one path bug, not a crash (item -279); s443's
    `[wait-resumed-dead-ctx]` UAF diagnostic instrument (item -280) PARKED s445 after 2 clean
    confirm soaks and ~10 soaks total without item -278 recurring. Full detail:
    `docs/PROJECT-OVERVIEW.md` §16 (s438-445); raw: `PORTING-STATE` Sessions 438-445.

-268..-273. **(s432-437) Duplicate-symbol catalogue closed (18/18); the `0x801163B0` free-list-
    cache-head-deref idiom swept at scale (107 sites, `GENERIC_CACHE_GUARD`, plus a 7-site `$a1`
    sibling, `CACHE_HEAD_A1_GUARD`); item -263 progressively localized through two rounds of
    breadcrumb-coverage misattribution (BREADCRUMB16, BREADCRUMB17).** Full detail:
    `docs/PROJECT-OVERVIEW.md` §16, `PORTING-STATE` Sessions 432-437.

-261..-267. **(s424-431) The `startPlayerSlotAnimationChannelLooping`-family crash chain: 3
    siblings guarded, then SUPERSEDED by the real root cause — a duplicate-symbol-name collision
    truncating `initCraftSelectScreen`'s body to 1 instruction — whose fix un-truncated code that
    had never run before and triggered a cascade of 3 further crashes, one per newly-live
    function.** Isolated the last (item -267, a stray write in `mallocCraftSelectionData`) to a
    47-callee search space; **s433 update: did NOT recur** after a sibling duplicate-symbol fix,
    plausibly because the sibling's garbage state (not `mallocCraftSelectionData` itself) was the
    real corruption source (single-run, not independently confirmed). Full detail:
    `docs/PROJECT-OVERVIEW.md` §16, `PORTING-STATE` Sessions 424-431.

-259. **(s422) `0x800290d4` "six independent triggers" lead — INVESTIGATED AND CLOSED, not a bug.**
    `0x800290d4` is `inflate_fast`'s own clean return, reported by a sparse breadcrumb (8/50 files);
    `atos` symbolication of 5/6 crash logs found FIVE DIFFERENT real crash functions, each independently
    tripping an already-catalogued family, not one shared mechanism. All six stay parked, correct and
    safe. Full detail: `PORTING-STATE` Session 422.

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
