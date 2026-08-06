# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. History: s295-330
   ran 5 passes (668→459 lines by s330); s346 ran a 6th (670→~470 lines) migrating the closed s297-337
   M5 gate-reversal arc to PROJECT-OVERVIEW §9; s355 ran a 7th migrating the closed s339-353 M5
   gate-promotion/step5-rate/drainMeshReleaseQueue-tail-scan arc to PROJECT-OVERVIEW §10; s364 ran an
   8th (689→~480 lines) folding the closed s354-362 guard-hunting arc into one summary item. Full
   per-session detail in git log. 35 KB remains a stretch target, not a hard floor -- the "Current
   truth" env-var/timeline prose and the Regeneration section's Standing warnings stay intact
   deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: design doc + steps 1-4 DONE — title-reach restored and confirmed 3/3
   (s343-344, full arc: PROJECT-OVERVIEW §10). Step 5 opened two parallel threads:
   `m5-audio-destub-linkedlist-corruption-source` (`drainMeshReleaseQueue`, still ACTIVE — three
   distinct unguarded pointer families found across the same 5 structurally identical loops: tail-scan
   cursor, head pointer, and a "global-tail" write-through, all guarded s350-365; a s366 proactive
   idiom-class audit found no further gap, and s367 drained the s365 verify pair with 1 genuine
   non-recurrence (full clean hold, all guards 0) — 1 of the 2 non-recurrence soaks needed to close,
   a second pair (`s367_..._verify3/4`) now queued; byte-identical poisoned value `bad_v1=0x00010001`
   the strongest lead) and
   `m5-audio-destub-coalesce-heap-guard-verify` (`coalesceFreeHeapBlocks`, guarded s354, bail-target
   bug fixed s358, **CLOSED s366** — 6/6 non-recurrence soaks post-fix including one clean full-hold).
   Detail: Next-steps items -222..-210 (folded); live status/decision trees: NEXT.md.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md.
Sanctioned tooling work unit, counts as ADVANCED whenever picked up: backport function-scoped matching (the BREADCRUMB10+ slice idiom) to the ~100 file-scoped-only guard patches in fixup_game_funcs.py, per the 2026-08-04 analysis in that file's header comment.

## Current truth (established by session 295; unchanged, reviewed through s355)

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
`UnhandledJumpTarget`, 0 `[defer-drop]`, 0 `[dmem-race]`, 0 asserts. `[missing-func]` clean in every
soaked phase to date except s49's undriven outdoor-512 stretch (3 addresses, M4 item -6). Post-`a`
process now soaks well past 65s without death.

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
move; what a leave-key actually leads to is unresolved. *Done when:* 60s of in-mission rendering,
craft visibly responds to synthetic input, stability counters 0, phase timeline covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it; the 3 `[missing-func]` addresses in the undriven outdoor-512 stretch (root-caused and
fixed s53/54, see Next-steps item -6, **runtime confirmation still outstanding**).

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.

## Next steps, in order of expected value (s295)

Numbering convention (fixed s295, was previously three colliding sequences): items are
numbered highest-magnitude-negative (top, newest/highest priority) counting up to -1 (bottom,
oldest). Current top is -222 (s367); the next new item takes -223 and is inserted at the top.

-222. **(s367) Thread B's `s365` pair drained: ONE genuine non-recurrence (full 446s clean hold,
    every guard fire counter 0) plus one uninformative pre-title crash — one non-recurrence data
    point toward the two needed to close the thread.** `verify1`: CLEAN, ran the full 446s hold,
    `title_reached` at 45.2s, and for the first time in this whole arc EVERY guard fire counter was
    0 across the board — coalesce, read/write, loop2-5, head1-5 (+clears), tailptr1-5, ring — nothing
    intercepted anything and the process still held. `verify2`: crashed in under 5s, `title_reached`
    blank (never reached the title screen at all), at `pc-symbol=musyxSynthFrame+4652` — an unrelated
    pre-title audio-boot crash in a different subsystem entirely, not a `drainMeshReleaseQueue`
    recurrence. Its `last-guest-pc=0x8000834c` coincidentally matches the s366
    `heapWalker+1696` background-noise checkpoint value, but source-checked that this is a global
    "last breadcrumb hit" variable that persists across calls — a coincidence of which breadcrumb
    last wrote it before an unrelated early crash, not evidence linking the two. Per the standing
    "crash under ~5s that never reaches title_reached is not a meaningful test" rule, `verify2` does
    not count toward the non-recurrence tally. Net: 1 of the 2 non-recurrence soaks NEXT.md's
    closure bar calls for (static exhaustiveness audit, s366, already done; empirical non-recurrence
    now at 1/2). Queued `s367_drainmeshtailptrguard_verify3/4.sh` for the second data point — same
    recipe, all current guard instruments armed. No code changed. Full detail: `PORTING-STATE`
    Session 367.

-221. **(s366) Thread A (`m5-audio-destub-coalesce-heap-guard-verify`) CLOSED — 6/6 non-recurrence
    soaks post-s358-fix, including one clean full-hold — plus a proactive idiom-class audit found
    `drainMeshReleaseQueue`'s guard coverage exhaustive, plus a new background-noise entry.** Session-
    start check found `s364_coalesceheapbailfix_reverify1/2` had already drained (the stale-NEXT.md
    gotcha, 7th recurrence). Both crashed off-target (`coalesce_guard_fire_n=0` both), same
    `pc-symbol=heapWalker+1696`/`last-guest-pc=0x8000834c` byte-identical in both runs — a brand-new
    symbol (0 prior mentions), cataloged as background noise (n=2, guest code, do not chase until a
    3rd hit) rather than investigated reactively. Source cross-check found `0x8000834c` is
    `drainMeshReleaseQueue`'s OWN final checkpoint (the `nop` right before `return`) — the function
    completed and returned normally in both runs; the crash is genuinely downstream, inside
    `heapWalker`, unrelated to either open M5 thread's guards. **Closed Thread A**: tally is now 6
    soaks post-s358-fix (`s358_verify1/2`, `s362_reverify1/2`, `s364_reverify1/2`), zero
    `coalesceFreeHeapBlocks` hits, meeting the closure bar set at item -219. Separately, ran a
    proactive full-function idiom-class audit of `drainMeshReleaseQueue` (Directive #3's model,
    applied to Thread B's own "is coverage exhaustive?" question while its `s365` verify pair is still
    queued): cross-referenced every table-/list-loaded-pointer dereference against the 3 known
    families × 5 loops (25 explicit guard blocks); found one syntactically-bare read per loop (the
    loop-back "advance cursor" read, e.g. `funcs_3.c:1768` for loop 1) but hand-verified it is
    memory-safe by loop invariant — the pointer is always pre-validated (by the head guard on first
    entry, or by the previous iteration's own tail-scan guard) before this line executes. **No new
    unguarded family found; coverage reads as exhaustive**, pending the still-queued `s365` pair's own
    empirical confirmation. No code changed. Full detail: `PORTING-STATE` Session 366.

-220. **(s365) Thread B's `s363` head-guard pair drained 2/2 byte-identical at a NEW
    `drainMeshReleaseQueue` offset with the s363 head guards positive-controlled for the first
    time — found and guarded a THIRD unguarded pointer family in the same function.** Both
    `s363_drainmeshheadguard_verify1/2` crashed at `pc-symbol=drainMeshReleaseQueue+5564`,
    `last-guest-pc=0x8000821C`, with `head1_guard_fire_n=1`, `head1_clear_guard_fire_n=1`,
    `head2_guard_fire_n=1` (the brand-new s363 head-pointer guards' first-ever fires — genuine
    positive control) AND all 5 tail-cursor guard pairs plus `ring_fire_n=1` also firing in the
    same run — every previously-known unguarded site ran at least once, crash genuinely moved past
    all of them. Source-read (`funcs_3.c:2001-2003`) found `MEM_W(0X4, ctx->r2) = ctx->r3` at the
    crash PC: `ctx->r2` is a "previous tail" pointer loaded once per loop from a fixed global table
    slot and checked only for `!= 0` before this write dereferences it — the same
    checked-non-NULL-but-unvalidated-pointer idiom as the tail-cursor and head-pointer families,
    now on a THIRD register. Found the identical site repeated once per loop, all five unguarded
    (loop1 `0x800081C8`, loop2 `0x8000821C` = crash site, loop3 `0x80008264`, loop4 `0x800082C4`,
    loop5 `0x80008314`); guarded all 5 in one pass (`[drain-mesh-loop{1..5}-tailptr-guard]`, reuses
    `ROGUESQ_LOG_DRAIN_MESH_TAIL_GUARD`). Full regen+rebuild clean, patch report `x1` per site,
    idempotency-confirmed on a 2nd fixup run (0 additional matches). Queued
    `s365_drainmeshtailptrguard_verify1/2.sh`, drains after Thread A's still-pending `s364_...`
    pair. Full detail: `PORTING-STATE` Session 365.

-219. **(s364, MAINTENANCE) 8th compaction pass (689→489 lines, folding the closed s354-362
    guard-hunting arc into item -217..-210) plus Thread A's `s362` reverify pair drained while at it.**
    `reverify1` CLEAN (432s full hold, 0 crashes, every guard fire counter 0); `reverify2` crashed at
    the long-catalogued `fscache_insert_and_retain+1192` (Metal shader-compiler system crash, item -10,
    not guest code), also every guard fire counter 0 — off-target-but-known noise, not new evidence.
    Thread A now has zero target-function crashes across 4 soaks since the s358 bail-target fix (1
    clean full hold, 3 off-target/known-noise) — approaching but not yet at its own closure bar. Re-queued
    `s364_coalesceheapbailfix_reverify1/2.sh` (same template, all current guard counters including the
    s363 head-pointer instruments). No code changed, no `lib/` touch.

-218. **(s363) Thread B's `s361` pair drained: the tail-scan loops' HEAD pointer (not the
    already-guarded tail cursor) carries the SAME read-guard/write-guard idiom, unguarded, once per
    loop.** `verify1` crashed at `drainMeshReleaseQueue+796` (`last-guest-pc=0x8000819C`) with all 10
    existing tail-cursor guards (5 loops × read+write) AND `ring_fire_n=1` already fired in the same
    run — genuinely outside every previously-guarded site. Source-read found an unguarded "priming
    read" through the loop's HEAD pointer (`a0`/`ctx->r4`, checked only for non-NULL) before each of
    the 5 loops, paired with an unconditional clear-write through the same pointer later — 10 new
    unguarded sites (5 read + 5 write), the same read-guard-without-write-guard gap as the
    s350→s350b/s357→s359 gotcha, on a parallel pointer the original idiom-class audit didn't cover (not
    part of the loop-body syntax). Guarded all 10 in one pass (`[drain-mesh-head{1..5}-guard]` /
    `[drain-mesh-head{1..5}-clear-guard]`, reuses `ROGUESQ_LOG_DRAIN_MESH_TAIL_GUARD`). Full
    regen+rebuild clean, patch report `x1` per site, all 10 confirmed single-line in regenerated
    source. Queued `s363_drainmeshheadguard_verify1/2.sh` — brand-new instruments, zero prior fire
    history, so even one fire is a positive control. Full detail: `PORTING-STATE` Session 363.

-217..-210. **(s354-362) M5 Thread A/B guard-hunting arc — folded, superseded by s363's head-pointer
    finding (item -218); Thread A's own question still open.** Thread A
    (`m5-audio-destub-coalesce-heap-guard-verify`): opened s354 on an independent
    `coalesceFreeHeapBlocks+3452` repeat, guarded with a range-check-and-bail; s358 found the guard's
    OWN bail target was wrong (`ctx->r3=0` sent execution to `L_80002358`, the coalesce loop's ENTRY
    label, not an exit — re-entering the loop with the still-wild pointer instead of stopping it),
    fixed to `L_80002444` (the real exit); re-verified 0/4 informative for its own question since (all
    4 crashed off-target), re-queued each time. Thread B
    (`m5-audio-destub-linkedlist-corruption-source`): a progressive idiom-class audit of
    `drainMeshReleaseQueue` found FIVE structurally identical tail-scan loops (not three, as first
    believed) across s354/357/359/360/361, each guarded with a read+write pair after repeatedly hitting
    the same read-guard-without-write-guard gap (s350→s350b, recurred s357→s359 one loop over, s360
    found a 3rd loop, s361's full-function audit found the last two); a ring-buffer breadcrumb (s353)
    intercepted `bad_v1=0x00010001` byte-identical across independent sessions/builds — the strongest
    single lead, 6-7 sightings by s360. s362 resolved the 3-session-recurring "does the soak queue
    drain in order?" question (confirmed: plain alphabetical glob = chronological, no bug — apparent
    skips were queue-depth arithmetic) and flagged two background-noise crash symbols now at n=2 each
    (`trackResourceListWithMappingTables+1192`, `unregisterServiceWorker+536`), both reading as Apple
    system-framework `dladdr` fallbacks — deliberately not escalated per the "no reactive single-crash
    chases" directive (a 3rd independent hit is the escalation trigger). Full detail: `PORTING-STATE`
    Sessions 354-362.

-209..-195 (excluding -208, kept below). **Fifteen sessions (s339-353, excl. s352) covering the M5
    gate-promotion, step-5 crash-rate-comparison, and `drainMeshReleaseQueue` tail-scan-cluster arcs —
    all CLOSED/superseded, folded here.** (1) VI=640 `pairs=0` stall resolution (s339): source-proved
    `submitGfxFrame` cannot produce a `FramebufferPair` and `cinematicLoopBody`'s self-loop calls the
    real `SET_COLOR_IMAGE` producer exactly once — not a stall, an ordinary one-time RDP-state prologue.
    (2) Audio-gate promotion arc (s340-344): promoted both audio gates to permanent default (s340, on a
    since-overturned validation basis — see Overturned Conclusions); found `reapplyDisplayMode`'s
    reversal alone deterministically blocks title-reach, 0/5 (s342); reverted just that gate, restoring
    title-reach (confirmed 3/3 by s344) but surfacing a new `tickWrappingTimerAccumulatorList`
    div-by-zero in the post-title window, PARKED at 1/3 recurrence
    (`m5-audio-destub-tickwrap-divzero-craftselect`, reopens on `last-guest-pc=0x80054744`). Current
    gate state unchanged since s343: fixup regex matches ONLY `reapplyDisplayMode` (`0x8008EC88`,
    force-zeroed); `setDisplayMode` (`0x8008EB40`) stays reversed. (3) Step-5 crash-rate-comparison
    methodology arc (s341, s344-347): fixed 2 methodology bugs (a `[keys]`-log misattribution, an
    unbounded per-node log blowup), then a 4-run batch found the post-title crash rate high (~75%) but
    diffuse across symbols, 0/4 hits on the two named target families — closed s352, superseded by item
    -208's bimodal-timing reframe. (4) `drainMeshReleaseQueue` tail-scan cluster (s348-351, s353): found
    and GUARDED 3 distinct crash sites within one function's dense unguarded linked-list tail-scan idiom
    (`processSceneNode`'s content-pointer field s348; a 2nd read site via BREADCRUMB15 s349-350; a
    write-through-v1 sibling site s351); landed a ring-buffer breadcrumb instrument s353 (0/2
    informative on its own verify pair, folded into item -210). The `[scene-node-content-guard]` guard
    from (4) is now known steady-state-benign, not corruption evidence — see Overturned Conclusions.
    Full detail: `docs/PROJECT-OVERVIEW.md` §10; raw detail `PORTING-STATE` Sessions 339-353 (excl.
    352).

-208. **(s352) Parent step-5 hypothesis's mandated pivot iteration: crash SYMBOL scatter is real, but
    crash TIMING is bimodal (two deterministic VI-transition windows) and one guard value reproduces
    byte-identically across independent sessions — reframes "diffuse storm" toward a narrower target.**
    Drained `s351_drainmeshwriteguard_verify1/2`: `verify1` CRASH at a 4th distinct `drainMeshReleaseQueue`
    offset (`+2864`) with BOTH the s350 read guard AND s351 write guard confirmed firing in the same run
    (positive control twice over — crash simply moved further downstream again); `verify2` CRASH at
    `coalesceFreeHeapBlocks+3452`, a heap-allocator routine entirely outside the function, neither guard
    fired. Taken alone, more scatter. **Went further given NEXT.md pre-committed this as the parent
    hypothesis's last iteration before the 3-strike pivot**: re-analyzed all 16 accumulated step-5 soak
    logs offline (zero new builds/runs, pure re-read of already-captured logs, "capture once analyze
    many"). Found (1) every crash's last-passed `[phase] vi_width` transition falls into exactly one of
    two narrow post-transition windows (~74s: `1024→512`; ~143s: `512→640`) despite hitting 10 distinct
    downstream symbols across the two — timing is NOT diffuse even though symbols are, and CLEAN runs
    passing through both windows unharmed show reaching a window is necessary-not-sufficient; (2) the
    `[drain-mesh-tail-guard]`/`[drain-mesh-write-guard]` diagnostic's intercepted value, `bad_v1=
    0x00010001`, is byte-identical across 2 independent sessions/builds (`s350_verify1`, `s351_verify1`)
    at a one-shot (`n=0`) guard site — ~1-in-4-billion odds of coincidence for random heap garbage,
    strong evidence of a deterministic, reproducible bug (source-read confirms the tail-scan is a plain
    singly-linked-list walk, `funcs_3.c:1734-1766`, consistent with a stale/prematurely-freed list node).
    A 3rd finding, `[scene-node-content-guard]` firing at the identical `node=0x80183ECC` thousands of
    times per run harmlessly across 3 sessions, is the OPPOSITE signature (steady-state, not corruption)
    — demoted from "proves a bug" to "proves a benign always-empty placeholder node," see Overturned
    Conclusions. **`m5-audio-destub-drainmesh-writeguard-verify` (iteration 1) CLOSED, superseded** — no
    more single-site downstream-consumer verify soaks planned. New thread `m5-audio-destub-linkedlist-
    corruption-source`, targeting the `bad_v1=0x00010001` lead: next probe logs every `v1` walked (not
    just the final bad one) for the tail-scan's first N iterations in a fresh run, to see whether the
    poisoned node appears at a consistent list position/consumer call — would localize the corrupting
    write/free without a full memory watch. NOT yet proven that every bucket-2 crash (processSceneNode,
    coalesceFreeHeapBlocks, `drainMeshReleaseQueue`'s 4 offsets) shares this one root cause — could still
    be independent bugs sharing only the same activity-burst trigger window; that's the open
    discriminator. Full detail: `PORTING-STATE` Session 352.

-160..-194. **(s297-337) M5 audio de-stubbing: the full gate-byte-reversal and VI=640-stall
    measurement-chasing arc, 41 sessions of instrumentation each superseded by the next, closed by
    item -209..-195's (s339) source proof.** Chased a "missing call count" through 2 diagnostic-cap bugs
    to a false 14-call gap (closed s325: the gap was the bug itself), found and fixed the `setDisplayMode`
    VI=320 hang (a spin loop starved of `musyxSynthFrame` pumps, s326/327, confirmed 3/3 s328), then
    chased `reapplyDisplayMode`'s VI=640 stall through 5 reachability probes to `cinematicLoopBody`'s
    internal self-loop, resolved s339 (see item -209..-195 and PROJECT-OVERVIEW §10). Along the way:
    `initMusyXEngine`'s gate found to be dead code, never called (s306, see Overturned Conclusions).
    Full paragraph migrated to `docs/PROJECT-OVERVIEW.md` §9 (s346 maintenance pass); full raw detail:
    `PORTING-STATE` Sessions 297-337.

-159..-14 (excluding -20, kept below). **Ten closed investigation lineages (nine from s314, plus
    the s297-337 M5 gate-reversal arc folded in s346), s99-s337 — all CLOSED, no outstanding action.**
    Whack-a-mole guard-gap chases (`composeNpcOrientationMatrix`, `renderUnlitMeshFaces`, `heapWalker`,
    `heapFreeListDequeue`, `-0x25A4` hangar-list-pointer family, breadcrumbs B2-B14), the
    audio-array-corruption race fix (s145/147/148), the `submitDmaRequestBatch` indirect-caller find
    (s101), the CALayer/campose SIGSEGV hunt, the regen-pipeline-idempotency root cause, and the M5
    audio gate/VI=640-stall chase (item -160..-194 above). One-paragraph-per-lineage summaries:
    `docs/PROJECT-OVERVIEW.md` §9; full raw detail: `PORTING-STATE` Sessions 99-337.

-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic).** Root cause:
    `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c` file that already exists on disk, so
    any patch whose regex anchor survives its own insertion stacks a duplicate on the next
    `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every
    regen is mandatory but **not sufficient by itself** -- residual intermittency's root cause is
    still unknown. **Standing rule**: audit the patch report for anything other than the expected `xN`
    count after every `fixup_game_funcs.py` run. Full detail: `PORTING-STATE` Sessions 120, 121, 126.

-11. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89).** 3 consecutive non-recurrences since s88's correctly-targeted instrument, against 8 prior crashing soaks. `ROGUESQ_LOG_ANIM_CB=1` still live if it recurs.

-10. **M3 — Metal-shader-compiler SIGSEGV reproducibility** (s83 spline1: SIGSEGV inside `Metal.framework`'s `MTLCompilerFSCache`, no source on our side). Still one data point.

-9. **M3 — confirm the s83 spline div0 guard actually engages.** 0/5 fires so far (still 0 after s88/s89/s90); real fix by code inspection (genuine 0/0 IEEE division) but no same-run positive control yet.

-8. **M3 — characterize `frameStartReset` SIGBUS.** 3 occurrences (s85, s108, s156 — the 3rd, `+532`, at a call chain byte-identical to `composeNpcOrientationMatrix`'s own, raising a shared-dispatcher hypothesis); no located faulting instruction in any of the 3.

-7. **M3 — HOLD_S=60 craft stick (M3 DoD body)** once earlier items clear: `PROBE_MODE=start_only HOLD_S=60` marks 10/25/40, document the phase timeline. Gate already keeps black off; residual S1 `fs` freeze (~3769-3872 plateau) may still stall animation.

-6. **M4 — confirm the s53 missing-func fix at runtime** (s54 applied + built it; only the game-run check remains). Undriven outdoor-512 stretch; `grep -c "\[missing-func\]"` should go 3→0. Not load-gated (s60/s61). Full detail: PORTING-STATE s53, s54.

-5. Past the first sustained mission hold: expect further new failure classes (mission overlay DMA → missing-func/UnhandledJumpTarget, new VI phase, overlays 12/44 splice, texture corruption). Each new failure is its own work unit.

-3. **Sibling-repo housekeeping (flagged s54, not autonomous):** `~/Documents/Tools/rogue_squadron64` carries uncommitted symbol-file edits including s54's `mission_overlay.txt` fix. Ask the user before committing there.

-2. **Band-row coverage history** (settled, s41-49): s40's `col`-write probe fails its control.

-1. **GPU->CPU present PNG** via `NativeTarget::copyToRAM` -- a convenience, not a blocker.

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

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its conclusions are among the oldest in the file, not the newest.

- **(s348/350→s352)** "`[scene-node-content-guard]` firing is evidence of the same corruption class as
  the other step-5 guards" — s352's raw-log re-read found this guard fires at the SAME node address
  (`0x80183ECC`) with the SAME zeroed content, thousands of times per run, harmlessly, across 3
  independent sessions — a steady-state signature (legitimately-empty/placeholder node revisited every
  frame), not a corruption signature. Believable: it's a real guard catching a real out-of-range read,
  and 0/4 crash-repeat since it landed (item -209..-195 range, s348) looked like validated-by-non-recurrence; the n=0-vs-
  n=1957+ distinction (one-shot-before-crash vs. steady-state-thousands-of-hits) just hadn't been
  checked against the OTHER guards' firing shape until s352 compared them side by side. Does not
  overturn the guard's correctness (it still needs to stay in place), only its evidentiary weight for
  the step-5 corruption-source hunt. PORTING-STATE 348, 350, 352; CURRENT-TRUTH item -208.
- **(s339→s340→s342)** "The VI=640 `pairs=0` plateau is a benign, locked-camera mission cutscene" (s339)
  and "s340's 2/2 clean soaks validate promoting both audio gate reversals together" (s340) — s342
  found both soaks (and s341's 2 follow-ups) never left the pre-title attribution/logo screen: 0
  `[keys]` lines in all 4 raw logs, and `run_mission_keys.sh`'s wait-for-VI=1024 gate mechanically
  cannot reach its `SCHEDULE`/`HOLD_S` logic without first seeing VI=1024, which never happened.
  Believable: the soaks genuinely were crash-free for the full 600s with audio/DMA/voice counters
  visibly live throughout (a real same-run positive control) — it just never occurred to check whether
  the `[keys]` schedule had actually fired. The underlying `pairs=0` mechanism (item -209..-195 range,
  s339's source trace, PROJECT-OVERVIEW §10) is not overturned, only its context: it onsets pre-title,
  not mid-mission-cutscene, and is
  specific to `reapplyDisplayMode`'s gate site, not `setDisplayMode`'s. PORTING-STATE 339, 340, 342.
- **(s107/108→s316→s318)** Two linked overturns in the gate1/2/3 tick-producer mechanism chase: (1)
  "the 3 near-identical countdown/period gates fire `tickAllActiveSongs`/`tickAudioSequencerFrame`" was
  never validated with a positive control across 4 sessions (s108/s311/s312 measured only gate1's raw
  inputs, never its branch outcome) — s316 instrumented all 3 and found NONE ever takes "call,"
  contradicting the functions' own 37-call count. (2) That "never calls" reading was itself overturned
  by s318: the diagnostic re-read the shared countdown fresh (`MEM_W`) instead of the register
  (`ctx->r2`) the real branch decision uses, racing against the true value. Direct measurement of
  `ctx->r2` showed gate1 takes "call" on 19/40 and gate2 on 4/4. Believable both times: the disassembly
  pattern matched exactly, and the read-once-for-branch/re-read-once-for-print pattern is easy to write
  without noticing it reintroduces a race. PORTING-STATE 316, 318.
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
- **(s2-31→various, ~15 claims, grouped)** Build/pixel-getting era, each overturned within 1-2
  sessions: Z-buffers misread as colour buffers; texrect output called invisible; RDP "emitting
  nothing" (real bug: a function-local ring high-water mark); `DPC_WRAP`/fbpair-cap misdiagnosed for
  missing FULL_SYNC (PROJECT-OVERVIEW §4.6); `PRIM_ALPHA_FF` called necessary for text; a
  sampling-artifact black-screen; misattributed texture dumps, floor-band line-mask/palette/dxt
  theories (M1's real cause: s44-49), fog-color attribution, S=0-triangle phase, stale-TMEM-at-draw
  (§4.1), and 1024-phase black screen (present-starvation, not zero-shade). PORTING-STATE 2-31.
- **(s62-69, grouped)** "RSP task submission stays healthy through the freeze" — a 1-in-32 throttled
  sample missed the crashing tail; an unsampled histogram showed 100% `ImemOverrun` exits.
  "Self-restarting the end-of-IMEM perspective-divide branch un-freezes tasks" — instrument fired 0
  times; the real site was `CLIP_1FBC`→`L_1650`. PORTING-STATE 62-69.
- **(s12-48, grouped — real causes already stated in "Current truth" above)** "0x6AB400 is the
  main-menu hangar" (believable: the partial render looked coherent for 36 sessions); stray
  briefing-room/SELECT-LEVEL origin+timing claims; hangar dimness/floor-band misattributed to a
  magnitude-erasing shade census (real cause: M1 s44-49); "no complete clip overlay in ROM" (a stray
  census conflated fall-through hits with real dispatch). All overturned s47/s48. PORTING-STATE 12-48.
- **(s70-82, ~9 claims, grouped)** The post-`a` SIGBUS/black-screen self-correction chain — UAF
  theories, what survives past it, Start-press counting, `fs`/present-stall theories — all resolved by
  the s84 UAF fix and s82 sane-width gate. PORTING-STATE 70-82.
- **(s87→s88)** "8th crash class is self-recursion in `advancePlayerAnimationPhase`" — that call site
  belongs to a different, unreached function; constant stack depth across 3296 calls, no recursion.
  PORTING-STATE 88.
- **(s302→s306)** "reversing `initMusyXEngine`'s gate-byte site validated safely (0/2 family #1
  recurrence)" — a positive-controlled entry counter found `initMusyXEngine` is never called at all;
  the clean result reflects dead code, not a validated gate=1 state. Gate=1 still never exercised by
  any soak. PORTING-STATE 306.
- **(s307→s309→s313→s315)** A chain of "stop points converge" claims in the audio-tick investigation,
  each overturned by a closer same-run measurement: "the RSP-task freeze and audio-tick freeze land at
  the same point (task #39/tick #19), one shared upstream resource" (s307) — `main.cpp` source-read
  found separate code paths, audio ticks stopping 18 tasks/1930 log lines earlier (s309). "The 3
  tick-producers and RSP `M_AUDTASK` all stop together at call #19/20 (a SOFT stop)" (s307/310/311) —
  a widened print-cap soak found `update3DAudioFrame` fires 40/40 (the real hard-stop boundary), the
  tick-producers stop 3 calls earlier at 37/37, and only `M_AUDTASK` genuinely stopped at 20/20 (s313).
  Then "`M_AUDTASK` genuinely stops at 20/20" itself — its diagnostic lived outside the game-code patch
  file and had the identical unwidened flat-cap bug s313 had just fixed elsewhere; widening found it
  also fires 40/40 (s315). Net: 2 real stop points (37/37 and 40/40), not 1 or 3. Believable each time:
  similar small round numbers read as simultaneous unless line numbers are diffed. PORTING-STATE 309,
  313, 315.

### Dead ends — labelled as such in the log, do not retry

- **(s2b-s4, grouped)** `RDP_ADDRESS_MASK`→0x7FFFFF (aliased legitimate extended-RDRAM handles onto
  low memory); a chunk-replay hack in `dma_rdram_to_dmem` (legit trig reads right after a swap);
  widening the DMA shadow to 0x37658 (legit dynamic data); blanket ucode-image shadow `shadow2` (2
  addresses are legitimately rewritten); `ROGUESQ_RING_RESYNC=1` (no measurable change);
  `dmem[0x153]=0xFF` forced segment reload (made failures worse).
- Bulk moves of unmapped symbols out of `main_overlay.txt` (s9): splits the enclosing function
  (PROJECT-OVERVIEW §4.5), producing a SIGBUS. Use `tools/overlay_symbol_probe.py <0xADDR>` first, one
  validated batch at a time.
- Present-side snap-down/`findMostRecentContaining` fallbacks (s9, neither ever fired); `ROGUESQ_VIEW_RDRAM=1` (s9, window never appears, broken in this fork); `ROGUESQ_WRAP_DEDUP=1` (s10, removes ~33000 redundant submissions, same Metal assert still hits); `ROGUESQ_FORCE_PAL15=1` (s14, clears floor band but corrupts ceiling banners sharing pal=15).
- **(s85→s91)** "`do_rom_read` corrupted `physical_addr` is nondeterministic garbage" — the exact same
  DMA call recurred byte-for-byte 3 times across 3 sessions; reclassified deterministic, reproducible.

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here, session tag is the
specific instance in PORTING-STATE:
- §4.1 instruments-that-lie: `fbPair.projections` over-count (s32), `[loadblock]` sampled-log miscount (s18/s19), stale TMEM at draw-record time (s19), capture harness outliving the process, `window_burst.sh` 60/60 false-positive (s9).
- §4.2 attribution errors: colour match ≠ attribution, fog #C8C0A0 (s18); plausible decoded image ≠ phase ID (s17).
- §4.3 cross-run comparison: knob effects/nulls manufactured by camera drift, "7.30%" constant misread as an effect (s18); phase timing varies tens of seconds run-to-run, gate on `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1` not a stopwatch (s17 → s18/s23).
- §4.6 missing protocol events: pair/buffer/wrap counters measured instead of FULL_SYNC arrivals (s11).

Not yet generalized in PROJECT-OVERVIEW: instrument-specific traps (crash-free-soak-isn't-evidence,
orphaned background soaks, sparse-screenshot false regressions, unvalidated suppression instruments,
`dpc_bridge` walker desync, histogram-drain timing, camera motion confounding aggregates) migrated to
`docs/PROJECT-OVERVIEW.md` §8 (s314 maintenance pass).
- **crash-signature blindness (s344)**: a soak-recipe verdict of "did any `[CRASH]` marker fire" is not
  evidence for a SPECIFIC target crash unless `last-guest-pc`/`pc-symbol` is checked against it — RS64
  has ~20+ independent, already-catalogued, nondeterministically-firing crash families, so a bare
  presence check will false-positive-confirm the wrong bug. Same session also found a `[keys]`-log-file
  bug (grepping the game's `run.log` for driver-emitted `[keys]` lines, which only ever land in the
  launcher's own log) that made 2 real, fully key/stick-driven soaks misreport as having driven no
  input at all. Item -200.
