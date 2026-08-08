# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Twenty passes so
   far (s295-330 x5, s346, s355, s364, s371, s380, s391, s398, s409, s429, s438, s444, s451, s461,
   s469, s479, s486) kept the file oscillating around the cap as new session detail accrues — full
   per-pass migration targets in git log; PROJECT-OVERVIEW §16-§20 hold the most recent five arcs. 35
   KB remains a stretch target, not a hard floor -- the "Current truth" env-var/timeline prose and
   the Regeneration section's Standing warnings stay intact deliberately; both are used every
   iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (full arc: PROJECT-OVERVIEW
   §10-§12). Next M5 work needs a genuinely new lead (**last checked s488: re-read M5-AUDIO-PLAN.md +
   scanned every s481-487 session entry in PORTING-STATE.md — the s481-487 arc's guards all target
   pointer-aliasing bugs in already-known MusyX voice functions, not stub/gate/trap surfaces; no new
   lead found, cadence reset**; due for a fresh check once
   3+ sessions have passed since then).
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. Every bucket
   surfaced by the s465/s477 frequency scans has a disposition (items -298..-309, PROJECT-OVERVIEW
   §18-§19). The s480 crash-symbolizer fix (item -311, local-symtab lookup replacing `dladdr`'s
   exported-symbol-only blind spot) resolved two more breadcrumbs it was built to help with: s481
   found `loadCutsceneAssetsByIndex+1860` was itself a misattribution, but the reproduction handed
   back a real, root-caused guard gap in `DL_LIST_APPEND_GUARD` (item -312) that s482 found recurred
   at up to 78/84 sites (generalized, item -313); applying that same "is the address-uniqueness claim
   actually shape-uniqueness?" skepticism to another old closed patch then found `AUDIO_SLOT_ACTIVE_GUARD`
   recurring across 20 more MusyX voice-function sites (item -314, s483), whose own confirm soak
   surfaced a THIRD sibling scope gap in `DL_LIST_RESET_GUARD` (item -315, s484) that s485 also
   generalized (73/84 sites). s486: item -315's 2nd confirm came back clean. **s487: item -314's own
   deferred 6-site remainder (the 2 mid-loop `musyxMixActiveVoices`/`musyxSynthFrame` site anchors)
   fixed with a loop-scoped `goto`-based guard shape — item -314 is now fully covered, 20/20, both
   independent confirms clean (2nd came back with ZERO crashes over the full run, the cleanest
   possible outcome). All four items (-312/-313/-314/-315) are fully CLOSED, 2/2 confirms each; full
   narrative migrated to PROJECT-OVERVIEW §20.** No untried
   high-expected-value instruction-pattern scan and no un-investigated high-recurrence breadcrumb
   remain queued — next M3 session should run a fresh from-scratch idiom scan per the s465/s477
   precedent, or check the M5 lead cadence. **s488 ran both**: the idiom scan's >=20-site tier came
   back structurally dry (every large bucket already covered), closing the large-bucket lui+lw/lui+sw
   idiom-audit method for now — see item -316. The M5 lead-check came back with nothing new (see item
   2 above) — cadence reset to s488. **s489 resolved item -316's sub-20 `-0x5BB4` candidate into a
   real fix**: a downstream trace found the actual gap one function upstream of the 19 read sites, in
   an existing `CACHE_HEAD_A1_GUARD` site that validated one deref but not two propagating writes
   right after it — same shape as -312..-315, fixed the same way (extend the check), 1st confirm
   clean (0 fires, unrelated already-catalogued crash). **s490: item -316's own 2nd confirm handed
   back a 5th instance of the lineage (item -317, `HEAP_DEQUEUE_DERIVED_PTR_GUARD`) — with a
   methodology lesson, not just another fix: the first fix attempt validated the wrong register
   (path-dependent at a shared control-flow label) and false-positived 660,261 times in one soak
   before being caught by the same live-verify discipline that's supposed to catch exactly this;
   corrected to validate the actually-dereferenced register directly, re-verified clean (0 fires),
   2nd confirm queued.** No fresh idiom-scan candidate remains queued — next M3 session needs either
   a new frequency-scan angle (both `lui`+`lw` and `lui`+`sw` are now structurally dry at the >=20-site
   tier), a control-flow-aware blanket sweep of item -317's own 183-site sibling population
   (DEFERRED this session, see item -317), or a wait for a new breadcrumb.

-312..-315. **(s481-487) `DL_LIST_APPEND_GUARD` and `DL_LIST_RESET_GUARD`'s own "grep-verified
    unique site" scope claims both turn out to be wrong, plus `AUDIO_SLOT_ACTIVE_GUARD`'s own
    20-site sibling gap — all FOUR items now fully CLOSED or fully covered.** Item -312: a
    `loadCutsceneAssetsByIndex+1860` breadcrumb reproduced as `submitSceneNodeRender+63868` under the
    s480 symbolizer fix, revealing a real `DL_LIST_APPEND_GUARD` unguarded-`rwrite` gap at one site;
    fixed, then SUPERSEDED. Item -313: a structural re-audit found that same aliasing shape recurs at
    78/84 `DL_LIST_APPEND_GUARD` sites (confirmed via 2nd direct source read); generalized into a
    blanket `rwrite`-validating patch, CLOSED. Item -314: applying the same "address-unique ≠
    shape-unique" skepticism to `AUDIO_SLOT_ACTIVE_GUARD` found 20 more unguarded loads of its global
    across 15 MusyX voice functions; s484 fixed 14/20 via 10 site-anchored early-return guards
    (`AUDIO_VOICE_BASEPTR_ENTRY_GUARD`), deliberately leaving the 6 mid-loop
    `musyxMixActiveVoices`/`musyxSynthFrame` sites unguarded pending a loop-scoped design. **s487
    closed that remainder**: `musyxMixActiveVoices`'s loop-head reload (transitively covering its 2
    other same-iteration reloads) gets a `goto`-to-per-iteration-increment guard (skips only that
    voice, continues the loop); `musyxSynthFrame`'s single reload gets a `goto`-past-the-array-walk
    guard (skips only that countdown pass, preserves later unrelated work in the same call) —
    `AUDIO_VOICE_BASEPTR_LOOP_GUARD`, 2 site anchors, all 20/20 item -314 sites now covered. 1st
    live-verify (`s487_audio_voice_baseptr_loop_manual`) clean: 0 fires on the new guard or any of 13
    sibling guard families, `hangarbay-entry` reached n=2600 (positive control), crash at 113.1s
    byte-identical to the already-catalogued `tickWrappingTimerAccumulatorList`/`memcpy_recomp+288`
    family (`last-guest-pc=0x80054780`, same address seen at s462's confirm) — unrelated, filed not
    chased. **2nd independent confirm (`s487_audio_voice_baseptr_loop_confirm`, rc=0) came back the
    cleanest possible outcome: ZERO `[CRASH]` events over the full run, 0 fires on
    `audio-voice-baseptr-loop-guard` or `audio-voice-baseptr-guard` (the s484 entry-guard sibling) or
    any other guard family, `hangarbay-entry` reached n=3000 (positive control, higher than the 1st
    confirm's n=2600). Item -314 is now FULLY CLOSED, 2/2 independent confirms clean.** Item -315:
    item -314's own confirm soak crashed live on a THIRD sibling scope gap, in `DL_LIST_RESET_GUARD`
    (wrong register validated at one `submitSceneNodeRender` site); fixed site-anchored, then a
    static-analysis audit found the same shape at 73/84 sites, generalized into
    `DL_LIST_RESET_RNODE_GUARD`, CLOSED, 2nd confirm (s485) clean. Full derivation and every soak
    verdict: `docs/PROJECT-OVERVIEW.md` §20, `PORTING-STATE.md` Sessions 481-487.

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
a range pointer. Highest allocated so far: -317. The next NEW item takes -318.

-317. **(s490) `HEAP_DEQUEUE_DERIVED_PTR_GUARD` — a 5th instance of the "-312..-316 lineage" shape,
    found while confirming item -316, with a methodology lesson: the FIRST fix attempt was wrong and
    had to be caught and corrected before landing.** Item -316's 2nd confirm soak's raw log showed
    four existing sibling guards (`freelist-next-guard`, `generic-cache-guard`,
    `dl-list-append-rwrite-guard`, `dl-list-reset-rnode-guard`) fire in sequence on the SAME
    corrupted pointer (`0x181B7580`) at four adjacent guest addresses inside `heapFreeListDequeue`
    (`funcs_3.c`), immediately followed by a SIGBUS 24 bytes past the last one. Direct-source trace
    (delegated to a subagent, then independently re-confirmed by hand) found the gap: `ctx->r4` is
    reloaded unguarded from the free-list-cache-head global (`0x801163B0`) at `0x8000D6E4`, then used
    at `0x8000D744` to compute a derived pointer (`ctx->r16 = ADD32(ctx->r4, 0x8)`, i.e. `$s0=$a0+8`)
    that's dereferenced completely unguarded at `0x8000D760` — crash address `0x181B7590` matches the
    corrupted base plus the two chained `+8` offsets exactly. **First fix attempt validated `ctx->r4`
    before the store (matching the -312..-316 precedent of re-checking the propagating value's own
    source register) — WRONG for this site**: `0x8000D760` sits at a label (`L_8000D75C`) that is
    ALSO reached via a second, unrelated control-flow path (an earlier bounds-check early-exit,
    `goto L_8000D75C` at guest `0x8000D67C`) where `ctx->r16` was last set from `ctx->r7` (a plain
    register copy, nothing to do with the free-list reload) — so `ctx->r4` at the shared label has no
    consistent meaning across both paths. Live-verify caught it immediately: the guard fired 660,261
    times in one ~300s soak while all four related sibling guards stayed at 0 — an order-of-magnitude
    departure from every other guard in this entire lineage's history (0-4 fires), which is what
    flagged the false-positive rather than a genuine widespread-corruption result. **Corrected**: validate
    `ctx->r16` itself (the pointer actually dereferenced), not an upstream proxy register — correct on
    both paths regardless of which one set it, matching the convention every other guard in this
    codebase already follows. Rebuilt, re-verified: 0 fires on the corrected guard, `hangarbay-entry`
    n=31 (positive control), 1 unrelated fire on the pre-existing `compose-npc-orient-guard9` sibling
    family, crashed on the already-catalogued `loadCutsceneAssetsByIndex+1860` /
    `last-guest-pc=0x800aafb8` family (same crash s463's own confirm soak hit). 2nd independent confirm
    queued (`s490_heap_dequeue_derived_ptr_confirm.sh`). **Scope note**: the reload idiom
    (`ctx->r4 = MEM_W(ctx->r4, 0X63B0);`) recurs 184 times across `funcs_3.c`/`funcs_4.c`; a
    classification-scan subagent, still running when this session closed, found only 1 of the other
    183 sites has an unguarded ADD32-derived-pointer dereference by its own (unvalidated, sanity-check-
    failing) textual-proximity heuristic — untrustworthy given this session's own shared-label-merge
    discovery, which a naive textual scan structurally cannot detect. A full blanket sweep needs
    control-flow-aware validation (validate the dereferenced register directly, never an upstream
    proxy) and is DEFERRED, not attempted at scale this session. **UPDATE (subagent's report landed
    after this session's commit)**: the classifier finished and, hand-sample-verified against live
    source, found the shipped fix is CORRECT but INCOMPLETE — `ctx->r16` (the same derived pointer
    just guarded at `0x8000D760`) is dereferenced at least 9 MORE times later in the same
    `heapFreeListDequeue` body, all still unguarded (guest addrs approx. `0x8000D794`, `0x8000D7A0`,
    `0x8000D7AC`, `0x8000D7C8`, `0x8000D7E4`, `0x8000D7E8`, `0x8000D7F0`, `0x8000D7F8`, plus a
    second-generation derived pointer `ctx->r5 = ADD32(ctx->r16, 0X10)` that likely propagates the
    same gap further) — the guard stops the FIRST crash on a corrupted pointer but not the rest of the
    same block. It also found ONE more confirmed VULNERABLE site under the strict same-function
    same-register criterion: `funcs_4.c` reload `0x80012E94` -> derived `ctx->r18` at `0x80012EF0` -> an
    8-field unguarded struct-init block starting `0x80012F14`. It explicitly flagged a structural blind
    spot (register-rename / global-round-trip indirection, ~73/88 candidates use this idiom) meaning
    the TRUE count is very likely higher than what direct-register tracing alone can find. Next M3
    session: (1) extend `HEAP_DEQUEUE_DERIVED_PTR_GUARD` to cover the other 9+ `ctx->r16` uses plus the
    `ctx->r5` second-generation pointer in the SAME function before calling this class closed, (2) fix
    the new `funcs_4.c` site, (3) only then consider the wider 183-site sweep, and only with
    control-flow- and register-rename-aware tooling, not a repeat of this session's textual scan. Full
    derivation: `PORTING-STATE.md` Session 490.

-316. **(s488 scan -> s489 FIXED, 2nd confirm s490 clean) DL_ALLOC_PROPAGATION_GUARD, a scope gap in
    the existing s436 `CACHE_HEAD_A1_GUARD` (guard covers one deref, not the propagation) — FULLY
    CLOSED, 2/2.** A downstream-consumer trace (delegated to a subagent) found the real gap wasn't in
    19 unguarded read sites but one function upstream, in `emitAllocatedDLCommand` (`funcs_3.c`): its
    own `CACHE_HEAD_A1_GUARD` site=4 (s436) validates the newly linked node pointer before writing the
    node's `next` field, but two more statements right after the guard block stayed UNCONDITIONAL —
    publishing the same possibly-bad node as the new list head, and propagating its data-area pointer
    into the persistent `-0x5BB4` write-cursor global that all 19 read sites reload unguarded. Fixed by
    extending the check (`DL_ALLOC_PROPAGATION_GUARD`, `fixup_game_funcs.py`) rather than adding 19
    read-site guards. **1st confirm (manual live-verify, s489)**: 0 fires on the new guard, `hangarbay-
    entry` n=31 (positive control), crashed at 113.2s on `pc-symbol=initVec4TripletFromArgs+68`,
    `last-guest-pc=0x800ab068` (already-catalogued s463/s468 family, unrelated). **2nd confirm
    (`s489_dl_alloc_propagation_confirm`, queued, ran s490)**: also 0 fires on `dl-alloc-propagation-
    guard` — item -316 itself is CLOSED, 2/2, no regression. **But this confirm's own run.log handed
    back a genuinely NEW, well-evidenced crash, not a null result — see item -317 below**: four
    unrelated sibling guards (`freelist-next-guard`, `generic-cache-guard`, `dl-list-append-rwrite-
    guard`, `dl-list-reset-rnode-guard`) fired in sequence on the exact same corrupted pointer value
    before a SIGBUS 24 bytes past the last one, inside `heapFreeListDequeue` — the same "guard-covers-
    one-deref-not-the-propagation" shape recurring a 5th time, this time on a DERIVED pointer
    (`$sN = $a0+8`) computed before any of those guards run. Full derivation: `PORTING-STATE.md`
    Sessions 489-490.

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
    all now CLOSED.** -291 `DL_LIST_APPEND_GUARD` (global `0x8011A7DC`, 57 sites, `funcs_3.c`/
    `funcs_4.c`) CLOSED s456, 0 crash/0 fires. -292 `SONGTEMPO_TABLE_GUARD` (`0x29C0($reg)`→global
    `0x801529C0`, MusyX song-sequencer's "current song track" base pointer, `funcs_25.c`) CLOSED
    s462, 43/43 sites across 6 reader functions, same stale-global-reload shape as the closed
    `-0x25A4` family. -296 `SIBLING_PTR_WRITE_GUARD` (sibling global `0x8011DC58`, 119 sites) CLOSED
    s459 (rule-8 mandatory pivot off -292), 0 fires; 10 sites sit in `submitSceneNodeRender`, a
    discriminating instrument for that function's still-open wait-for-recurrence breadcrumb.
    **AMENDED s473 (item -306): a register-taint-tracking gap had silently dropped 1 real site (120th,
    `setupCameraMatrices`) — found, fixed, soak-confirmed.** Full detail: `docs/PROJECT-OVERVIEW.md` §17.

-261..-290 (and -263). **(s424-453) The duplicate-symbol-name-collision arc: the
    `startPlayerSlotAnimationChannelLooping` crash chain, the duplicate-symbol catalogue closure, the
    BREADCRUMB18/free-list-guard arc, and the `static5-rename-orphan-sweep` — ALL CLOSED.** A
    duplicate-symbol-name collision truncated `initCraftSelectScreen`'s body to 1 instruction
    (s424-431); the fix triggered a cascade of 3 further crashes (items -261..-267, all guarded — the
    last did not recur after a sibling duplicate-symbol fix, single-run only). s432-437 closed the
    full duplicate-symbol catalogue (18/18) and swept the `0x801163B0` free-list-cache-head-deref
    idiom at scale (107 sites, `GENERIC_CACHE_GUARD`, plus a 7-site `$a1` sibling
    `CACHE_HEAD_A1_GUARD`); item -263 was progressively localized through two rounds of breadcrumb
    misattribution (BREADCRUMB16/17) before s441 reclassified it PARKED — the real mechanism was a
    THIRD free-list-cache-head sibling bug (`FREELIST_NEXT_GUARD`, item -277, 105 sites) misattributed
    to it by signature match alone (falsifying condition: a NEW occurrence where BREADCRUMB18 reports
    a real address inside `updateHangarBayScene`'s own body). That fix surfaced item -278
    (thread-scheduler SIGSEGV, PARKED s445, ~10 soaks no recurrence) and item -279 (a soak-script
    off-by-one, not a crash). s445-453's `static5-rename-orphan-sweep` then fixed every pre-s427
    guard/patch the -261..-267 fix had orphaned (94 sites: `GETDATITEM_GUARD`, `HANGARLIST_GUARD`
    family, `S390_H2A`/`H2B`, `G1`-`G32`+`A`-`E`, 9 `composeNpcOrientationMatrix` sites; s449
    positive-controlled `HANGARLIST_GUARD` at 245000+ reaches, 0 trips), closing the last tracked
    remainder (`S392_H3A`/`H3B`, item -290) with no code change needed. Incidentally opened item -281
    (`NAN_CHECK` assert in `transformVec3ByMat34`, filed not chased) and fixed a `tools/probe.sh`
    false-negative bug (s447). Full session-by-session detail: `docs/PROJECT-OVERVIEW.md` §16,
    `PORTING-STATE` Sessions 424-453.

-259. **(s422) `0x800290d4` "six independent triggers" lead — INVESTIGATED AND CLOSED, not a bug.**
    `0x800290d4` is `inflate_fast`'s own clean return, reported by a sparse breadcrumb (8/50 files);
    `atos` symbolication of 5/6 crash logs found FIVE DIFFERENT real crash functions, each already
    catalogued, not one shared mechanism. All six stay parked, correct and safe. `PORTING-STATE` 422.

-231..-249. **(s377-421) Three more CLOSED arcs, oldest-first: fixup function-scope backport,
    M3 idiom-class resumption, M4 phantom-overlay relocation.** -231..-238 (s377-386): 176 file-scoped
    guard patches found, 168 converted to function-scope, 8 confirmed permanent design exclusions,
    CLOSED OUT s386 (process lessons: `docs/PROJECT-OVERVIEW.md` §13). -239..-247 (s389-397):
    `hangarInitialize`'s `-0x25A4` hangar-list-pointer family and the "Lookup" struct-family fully
    CLOSED, plus two guard-placement bugs found+fixed and a codebase-wide frequency scan that came
    back negative, closing the pure-idiom-audit discovery method for now until the s463 scan revived
    it (§14). -249 (s400-421): `main_overlay.txt` phantom-overlay-function relocation, 784 functions
    relocated across 21 sessions, 10 genuinely-buggy parked in `m4_known_bad.txt`, 4 more in
    `m4_known_skip.txt`, 0 actionable candidates remain (§15). Raw: `PORTING-STATE` Sessions 377-421.

-230..-14 (excluding -20, kept below). **Eleven closed investigation lineages, s99-s376 — all CLOSED,
    no outstanding action.** M5 audio de-stubbing (items -160..-230, s297-376: gate-byte-reversal/
    VI=640-stall, Step 5 guard-hunting, gate-promotion/crash-rate-comparison, Step 6 PCM-sanity + C88
    pre-title-hang/VI-trigger — §9-§12) plus ten earlier whack-a-mole guard-gap chases
    (`composeNpcOrientationMatrix`, `renderUnlitMeshFaces`, `heapWalker`, `heapFreeListDequeue`,
    `-0x25A4` family, breadcrumbs B2-B14, the audio-array-corruption race fix, the
    `submitDmaRequestBatch` indirect-caller find, the CALayer/campose SIGSEGV hunt, the
    regen-pipeline-idempotency root cause, s99-s337, §9). One-paragraph-per-lineage summaries:
    `docs/PROJECT-OVERVIEW.md` §9-§12; full raw detail: `PORTING-STATE` Sessions 99-376.

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
-6. **(s53/s54→s399) M4 — the 3 `[missing-func]` addresses: DONE, CLOSED s399.** s54's fix was dead on
    arrival — silently shadowed by pre-existing duplicate entries at the same addresses in
    `main_overlay.txt` (first-discovered instance of item -249's family). Root-caused and fixed s399 by
    deleting the 3 duplicate lines; verified 3/3 post-fix runs, same-run positive control. Full detail:
    `PORTING-STATE` Session 399.

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
