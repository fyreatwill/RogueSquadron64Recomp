# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. History: s295-330
   ran 5 passes (668→459 lines by s330); s346 ran a 6th (670→~470 lines) migrating the closed s297-337
   M5 gate-reversal arc to PROJECT-OVERVIEW §9. Full per-session detail in git log. 35 KB remains a
   stretch target, not a hard floor -- the "Current truth" env-var/timeline prose and the Regeneration
   section's Standing warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: design doc + steps 1-3 DONE (s298/300/301). Step 4 (`setDisplayMode`
   VI=320 hang, `reapplyDisplayMode` gate) is CLOSED and fix-validated — title-reach confirmed 3/3 as
   of s343 (item -199). Step 5 (crash-family #3/#4 rate comparison) is OPEN, `HYPOTHESIS-ID
   m5-audio-destub-step5-crashrate-comparison`, still diffuse-not-concentrated as of s351 (item -207):
   across 14 soaks (8 `m5step5v3_rate_*` + 6 verify), `drainMeshReleaseQueue` is the single most-hit
   function but at 3 different sub-mechanisms in one tail-scan idiom (`+600` unlocalized, `+960`
   read-guarded s350, `+1580` write-guarded s351), the rest scattering across 5+ other symbols. s351
   guarded the write-through-v1 sibling site the s350 verify soak's FIRST attempt reproduced (with the
   s350 read guard confirmed firing in the same run) — `m5-audio-destub-drainmesh-breadcrumb` CLOSED
   with a 2nd landed fix; new thread `m5-audio-destub-drainmesh-writeguard-verify` to consume
   `s351_drainmeshwriteguard_verify1/2` next session. `m5-audio-destub-contentguard-verify` thread
   CLOSED s350: 0/4 repeat of `processSceneNode+1424` since item -204's guard landed. 1 more iteration
   on the parent step-5 hypothesis before the 3-strike budget rule forces a pivot check.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md.
Sanctioned tooling work unit, counts as ADVANCED whenever picked up: backport function-scoped matching (the BREADCRUMB10+ slice idiom) to the ~100 file-scoped-only guard patches in fixup_game_funcs.py, per the 2026-08-04 analysis in that file's header comment.

## Current truth (established by session 295; unchanged, reviewed through s332)

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
oldest). Current top is -207 (s351); the next new item takes -208 and is inserted at the top.

-207. **(s351) s350's `drainMeshReleaseQueue` read guard fired correctly on its own FIRST verify soak
    but the crash happened anyway 2 lines downstream, at the exact write-through-v1 sibling site the
    s350 comment had already flagged as unguarded — guarded it too, landing a 2nd fix.** Drained
    `s350_drainmeshguard_verify1/2.sh` (both already run+moved to `soak_queue/done/` by the loop between
    iterations). `verify1`: CRASH, `pc-symbol=drainMeshReleaseQueue+1580`, `last-guest-pc=0x800081c4`,
    AND `guard_fire_n=1` (`bad_v1=0x00010001`) in the same run — the read guard at `0x800081AC` fired
    (positive control satisfied), correctly bailed the read (`ctx->r2=0`), but did not repair `ctx->r3`
    (v1) itself, and the function unconditionally writes through that same corrupted pointer 2 lines
    later (`0x800081C4`: `MEM_W(0X0, ctx->r3) = ctx->r2`) regardless of loop-exit reason — precisely the
    gap the s350 fixup comment named but left unguarded pending a confirmed hit. `verify2`: CRASH at a
    4th distinct symbol (`static_5_800AAD9C+5140`, `guard_fire_n=0`) — further diffuse-storm evidence,
    not informative for this guard. This is the discriminating result iteration 3 of
    `m5-audio-destub-drainmesh-breadcrumb` needed: not scatter, a precise source-provable sibling bug at
    a site already named as the next candidate. Guarded both compiler-duplicated occurrences of the
    `0x800081C4` write (`fixup_game_funcs.py`, one indent-agnostic regex) with the same range-check-
    and-bail shape, on invalid `v1` skipping the write entirely (no-op). New diagnostic tag
    `[drain-mesh-write-guard]`, reuses the already-armed `ROGUESQ_LOG_DRAIN_MESH_TAIL_GUARD` env var —
    no wiring change needed. Deliberately left the sibling `0x800081C8` write unguarded (its address
    operand is `ctx->r2`, the freelist-head global, not the corrupted v1 — different idiom, no confirmed
    crash there). Full regen + rebuild clean (`patched x2`). Queued
    `s351_drainmeshwriteguard_verify1/2.sh`. Net across 14 soaks: `drainMeshReleaseQueue` still the
    single most-hit function, now at 3 confirmed sub-mechanisms in one dense tail-scan idiom (2
    guarded), the rest still scattered — parent step-5 hypothesis (item -203) stays diffuse-not-
    concentrated, unchanged. `lib/` not touched — confirmed via `git status`/`git ls-files` this session
    that the whole `~/Documents/Tools/N64Recomp` tool repo (where `fixup_game_funcs.py` lives,
    untracked) sits outside `RogueSquadron64Recomp`'s `lib/`/submodule-patches system entirely. Full
    detail: `PORTING-STATE` Session 351. `HYPOTHESIS-ID m5-audio-destub-drainmesh-breadcrumb` CLOSED
    (landed fix); new thread `m5-audio-destub-drainmesh-writeguard-verify`.

-206. **(s350) Drained both s349 queues, refuted the `+600` single-exact-repeat framing, found a 2nd
    precise `drainMeshReleaseQueue` crash site via BREADCRUMB15, guarded it, closed the
    `contentguard-verify` thread.** Ran `s349_drainmeshbreadcrumb_verify1/2.sh` (queued s349, drained
    inline this session — `zsh`, not `bash`, is the allowlisted interpreter for `soak_queue/*.sh`):
    NEITHER reproduced `drainMeshReleaseQueue+600` — verify1 crashed at `reserveAndEmitDLEntry+10212`,
    verify2 at `heapFreeListInsert+72` (both symbol-distance-confirmed genuine via a new
    `scratch/agent/check_symtab3.py`, not misattribution). This is the discriminating result: item
    -205's "2/2 exact repeat" did NOT survive 2 more attempts (0/2), refuting "single fixed-PC bug at
    `+600`". Meanwhile the loop had already drained `s348_contentguard_verify2/3.sh` (item -205's other
    open thread) between iterations: `verify2` crashed at `drainMeshReleaseQueue+960` — a THIRD hit in
    this function, at a DIFFERENT offset than `+600` — with `last-guest-pc=0x800081ac` now PRECISE
    (BREADCRUMB15 was already live for this build). Source-read (`funcs_3.c:1746-1758`) identified the
    exact crash: a tail-scan loop `v1 = *v1; v0 = *v1` (guest `0x800081A8`/`0x800081AC`) walking a
    linked list with NO validity check on `v1` before either dereference — a second, distinct unguarded
    site in the same "dense unguarded linked-list" function item -205 already characterized. Added a
    range-check-and-bail guard at `0x800081AC` (`fixup_game_funcs.py`, same s190/s348 shape: env-gated
    `[drain-mesh-tail-guard]` diagnostic, `ROGUESQ_LOG_DRAIN_MESH_TAIL_GUARD` — now armed by default in
    `run_s327waitpump.sh` — bails to `ctx->r2=0`, i.e. treats an invalid `v1` as natural list-end rather
    than crashing). Full regen + rebuild clean (`patched x1` for the guard, `x149` for BREADCRUMB15).
    Queued `s350_drainmeshguard_verify1/2.sh`. Net tally across this cluster: 3/12 recent crashes land
    somewhere in `drainMeshReleaseQueue` (now at 2 confirmed distinct offsets, one guarded), the
    remainder scattered across 5+ other symbols — still the diffuse-not-concentrated shape from item
    -203, not a single fixable bug. Also closed `HYPOTHESIS-ID m5-audio-destub-contentguard-verify`:
    `verify2`/`verify3` gave 0/2 more `processSceneNode+1424` repeats (0/4 total since item -204's
    guard), and `verify2`'s `guard_fire_sample` (`n=0,1,2`, `bad_content=0x0` every time) confirms the
    guard executes normally (positive control satisfied) even though it never observed a bad value in
    these runs — treat item -204's guard as validated-by-non-recurrence, not proven-by-interception.
    `verify3` crashed at a host libc symbol (`__pthread_kill+8`, likely an `abort()`/allocator-detected
    corruption path) — different class, not informative for the guard question. `lib/` not touched.
    Full detail: `PORTING-STATE` Session 350.

-205. **(s349) Found a NEW exact-repeat crash, `drainMeshReleaseQueue+600` (2/2, deterministic file-
    offset match across different ASLR bases) — confirmed real via symbol-table distance (not
    nearest-symbol ambiguity), added BREADCRUMB15 to localize the exact guest PC on the next hit.**
    Drained `m5step5v3_rate_7` (CRASH) and `_rate_8` (CRASH); neither hit `processSceneNode+1424`
    (0/2 repeat post-item -204's guard, weak-but-consistent, not yet "confirmed"), but both hit
    `drainMeshReleaseQueue+600` — same file offset (`0x3fbcc4`) both times despite different bases.
    `nm -n` distance check (`scratch/agent/check_symtab2.py`): `drainMeshReleaseQueue` to next symbol
    `enqueueMeshForDeferredRelease` is 3672 bytes (`0xe58`) — `+600` is genuinely inside this
    function's own body, ruling out misattribution. `last-guest-pc` (`0x8000B650`) was a red herring:
    it's `beginFrameDLChunk`'s own return instruction (BREADCRUMB3's target) — stale, because all 10
    prior `BREADCRUMB*` passes share ONE `g_rs64_last_guest_pc` global and `drainMeshReleaseQueue`
    itself was never instrumented. Added `BREADCRUMB15` (same blanket per-instruction-comment pattern
    as BREADCRUMB3/10-14) to `fixup_game_funcs.py`, targeting `drainMeshReleaseQueue`'s body in
    `funcs_3.c` (dense, entirely unguarded linked-list free/coalesce routine, `funcs_3.c:1669+`). Full
    regen + rebuild clean (`patched x149`). Queued `s349_drainmeshbreadcrumb_verify1/2.sh`. Content-
    guard verify soaks (`s348_contentguard_verify2/3.sh`) had NOT yet been drained by the loop this
    session — that check stays open. `HYPOTHESIS-ID m5-audio-destub-contentguard-verify` stays open;
    new parallel thread `m5-audio-destub-drainmesh-breadcrumb`. `lib/` not touched. Full detail:
    `PORTING-STATE` Session 349.

-204. **(s348) processSceneNode's repeat crash (2/6, exact host+guest PC match) was an unguarded
    "content pointer" one field removed from the already-guarded node pointer — GUARDED, not just
    catalogued.** Drained `m5step5v3_rate_5` (CLEAN) and `_rate_6` (CRASH, `pc-symbol=processSceneNode+1424`,
    `last-guest-pc=0x80014FDC` — byte-identical to `rate_3`'s crash, item -203). This crossed NEXT.md's
    declared "2+ hits" escalation threshold, the first symbol in the whole v3 batch to do so. Source-read
    `funcs_4.c` at the guest PC: the crash is `MEM_W(ctx->r16, 0X30)` where `ctx->r16` was loaded from
    `MEM_W(ctx->r17, 0X8)` — a field of the scene-node pointer that s190's existing entry guard (which
    validates `ctx->r17` itself) never checks. Found a second load site of the same field on the
    sibling-loop continuation path (guest `0x800153F8`) feeding the same downstream derefs. Added two
    `fixup_game_funcs.py` guards (same shape as s190's, bail to the function's own `L_80015528` exit,
    env-gated under `ROGUESQ_LOG_SCENE_NODE_CONTENT_GUARD`), full regen + rebuild clean. Hit and fixed a
    real pipeline-ordering trap while landing this: the first attempt placed the patch BEFORE the
    BREADCRUMB4 pass whose output its anchor depended on, so it silently matched 0 times — moved it to
    run after BREADCRUMB4, confirmed `patched x1` both sites and guard text present in output. One
    inline validation soak crashed on an unrelated, first-ever-seen boot-time death
    (`musyxSynthFrame+4652`, before title, not informative for this guard). Queued
    `s348_contentguard_verify2/3.sh` + re-queued `m5step5v3_rate_7/8.sh` for the loop to drain.
    **Not yet confirmed empirically** — no soak has shown the guard firing or the crash's absence yet;
    that's the immediate next-session check. `HYPOTHESIS-ID m5-audio-destub-step5-crashrate-comparison`
    closes with a landed fix (not another inconclusive tally); new thread
    `m5-audio-destub-contentguard-verify`. `lib/` not touched (both edited files are outside the
    submodule-patches system — see PORTING-STATE Session 348 for why). Full detail: `PORTING-STATE`
    Session 348.

-203. **(s347) M5 step 5 crash-rate comparison, first real batch (n=4): 3/4 runs crashed but at
    THREE DIFFERENT symbols — refutes "allocOrEvictMaterialNode is a new concentrated family #5",
    supports "post-title window has a high (~75%) but diffuse crash rate, with family #3/#4
    specifically absent."** Drained `m5step5v3_rate_3` (CRASH, `pc-symbol=processSceneNode+1424`,
    `runlog_bytes=68.6MB`) and `_rate_4` (CRASH, `pc-symbol=trackResourceListWithMappingTables+1192`,
    `runlog_bytes=55.9MB`) — both in the normal band, s345's fix holds. Neither matches item -202's
    `allocOrEvictMaterialNode+944` (0/3 repeat since rate_1) — that stays a single, still-uncatalogued
    data point, does not meet the bar for a guard. `processSceneNode` is itself a KNOWN
    misattribution-prone multi-offset crash site (PORTING-STATE s151/152 documented `+6668`/`+7640`
    crashes there before; `+1424` is a 3rd offset, likely the same nearest-symbol-ambiguity family, not
    a new bug). `trackResourceListWithMappingTables+1192` has no prior crash citation anywhere in
    `docs/`/`PORTING-STATE.md` (only a 2024-era unrelated duplicate-symbol-name mention) — genuinely
    new, but a singleton like `allocOrEvictMaterialNode`, so not (yet) a family either. Net across the
    4-run v3 batch: 0/4 hit family #3 (`waitForAnyAudioSlot`) or family #4 (post-cutscene stall)
    specifically — the two named families this comparison was designed to rate — while 3/4 crashed on
    something else entirely, each a different symbol. This splits the competing hypotheses: it refutes
    "de-stubbing concentrated risk into one new bug" and is consistent with "de-stubbing didn't reduce
    the post-title crash rate, just diffused it away from #3/#4 into whatever ~20+-family background
    noise was already there." n=4 is still small (confirmed by design: each crash a *different* symbol
    means no single-family rate is estimable yet). Queued `m5step5v3_rate_5..8.sh` (same template) to
    extend the sample before drawing a firmer conclusion. `HYPOTHESIS-ID
    m5-audio-destub-step5-crashrate-comparison` — 2nd iteration of the actual experiment (methodology
    fixed s345, maintenance s346), 1 more iteration before the 3-strike budget rule triggers a pivot
    check. `lib/` not touched. Full detail: `PORTING-STATE` Session 347.

-202. **(s346) MAINTENANCE pass + 2 folded-in soak verdicts: s345's log-blowup fix CONFIRMED working,
    and one of the 2 real data points hit an uncatalogued crash — `allocOrEvictMaterialNode+944`,
    single data point, not yet evidence (superseded by item -203: still 1/4 as of s347, no repeat).**
    Compacted CURRENT-TRUTH 670→470 lines (Step 0 triggered at
    60,543 bytes). `m5step5v3_rate_1` (rc=1) and `_rate_2` (rc=0) landed via the soak queue:
    `runlog_bytes` back to the normal 57-62 MB band (positive control for the `${VAR:-1}` fix passed).
    `rate_2` clean (full 240s hold, benign `pairs=0` plateau); `rate_1` crashed ~10-12s into the hold
    at `last-guest-pc=0x80010b7c`/`pc-symbol=allocOrEvictMaterialNode+944` — grepped `docs/` and
    `PORTING-STATE.md`, zero prior hits, no match to any already-catalogued post-title signature.
    Queued `m5step5v3_rate_3/4.sh` (not run — maintenance iteration). Full detail: `PORTING-STATE`
    Session 346.

-201. **(s345) The `m5step5v2_rate_1/2` soaks' `rc=137` was a recipe artifact, not crash-family
    #3/#4 signal — fix confirmed working by item -202.** Both hit the loop's 600s hard-cap despite
    their own launcher logs showing the driven scenario completed cleanly at ~301s wall. Root cause:
    `run.log` ballooned to 8.2-8.7 GB (vs. 76-233 MB normal) because
    `ROGUESQ_LOG_RS_FREE_WALK`/`_MALLOC_WALK` log once PER LIST NODE walked (unlike every other
    `ROGUESQ_LOG_*` var) — the SAME family Session 209/210 already root-caused for an unrelated bug
    hunt, so it's state/timing-dependent, not a fixed cost; root mechanism (why THIS run) stays open.
    **Fix landed**: `run_s327waitpump.sh`'s 4 heap-walker log vars now default-overridable
    (`${VAR:-1}`) so a recipe can opt out without forking the driver. Cancelled the 2 unrun
    `m5step5v2_rate_3/4` recipes; queued corrected `m5step5v3_rate_1/2.sh` (4 vars opted to 0, logs
    `runlog_bytes`/`rs_free_walk_lines`). Deleted the two 8+ GB run.logs after extracting the
    discriminating samples. `HYPOTHESIS-ID m5-audio-destub-step5-crashrate-comparison` — pure
    recipe-methodology repair this session, 0 data points toward the rate question. Full detail:
    `PORTING-STATE` Session 345.

-200. **(s344) M5 audio de-stubbing: neither queued confirmation soak reproduces the
    `tickWrappingTimerAccumulatorList` div-by-zero from item -199 — parked, not guarded.** `confirm1`
    is genuinely clean: `CRASH: 0` for the full 307s including the hold window, and (despite a
    `[keys]`-log-file recipe bug misreporting `keys_lines=0`) actually drove the full schedule and
    reached title at 45.5s. `confirm2` hit an unrelated, already-catalogued
    `emitAllocatedDLCommand`/`submitSceneNodeRender` SIGBUS (`last-guest-pc=0x80008928`), NOT the
    target div-by-zero — confirmed by symtab walk + source grep. Net: title-reach now confirmed 3/3
    (strengthening item -199); the div-by-zero itself is 1/3 total — doesn't meet the bar for a guard,
    doesn't read as a clean flake either. `HYPOTHESIS-ID m5-audio-destub-tickwrap-divzero-craftselect`
    PARKED (recurs if a future soak reproduces `last-guest-pc=0x80054744` specifically). Reopened
    M5-AUDIO-PLAN step 5 (crash-family #3/#4 rate comparison) with 4 methodology-corrected recipes
    (`m5step5v2_rate_1..4.sh`, `HOLD_S=240`) that fix the `[keys]`-log-file bug and print
    `last-guest-pc`/`pc-symbol` on every crash (generalized in Method Traps below). Full detail:
    `PORTING-STATE` Session 344.

-199. **(s343) M5 audio de-stubbing: reverted `reapplyDisplayMode`'s gate to force-zero, title-reach
    restored — but a NEW crash surfaced one stage later, in the SELECT YOUR CRAFT stabilization
    window, never reachable before.** Regen'd with the fixup regex narrowed to `0x8008EC88`-only
    (`setDisplayMode`'s `0x8008EB40` stays reversed). One soak: title reached at 45.5s (matches the
    44.6-46.2s baseline), full `[keys]` schedule fired. Then, during the 12s post-title stabilization
    window, the process died: signal 6 (abort), `last-guest-pc=0x80054744` inside
    `tickWrappingTimerAccumulatorList` (`BREADCRUMB9`'s function) — a compiler-inserted `break 7`
    div-by-zero trap, a DIFFERENT signature from `BREADCRUMB9`'s previously-catalogued `0x80000004`
    near-null-pointer crash. Byte-identical gate config to s328's clean baseline (0/2 crashes) — either
    a nondeterministic race s328 didn't hit, or ~15 intervening sessions exposed it. Single-source;
    confirmation soaks queued (folded in by item -200). `HYPOTHESIS-ID
    m5-audio-destub-reapplydisplaymode-title-block` CLOSED (title-reach restored); new thread
    `m5-audio-destub-tickwrap-divzero-craftselect`. `lib/` not touched. Full detail: `PORTING-STATE`
    Session 343.

-198. **(s342) M5 audio de-stubbing: `reapplyDisplayMode`'s gate reversal deterministically blocks
    the game from EVER reaching the title screen (0/5 relevant soaks) — supersedes item -197's plan,
    weakens item -196's promotion (see Overturned Conclusions).** The 2 `m5step5_rate_1/2` soaks and
    s340/s341's own soaks all showed the same signature: 0 `[keys]` presses, the game never leaves the
    pre-title screen — despite s340's write-up describing a full driven hold (mechanically impossible:
    `run_mission_keys.sh`'s wait-for-VI=1024 gate self-times-out first). Isolated to
    `reapplyDisplayMode` specifically: baseline and `setDisplayMode`-alone both reach title normally;
    every soak with `reapplyDisplayMode`'s gate reversed has NEVER reached title, 0/5 across 3
    sessions. **Recommendation** (executed s343, item -199): revert `reapplyDisplayMode`'s gate to
    force-zero, keep `setDisplayMode`'s reversal. `HYPOTHESIS-ID
    m5-audio-destub-step5-crashrate-comparison` CLOSED (superseded); new thread
    `m5-audio-destub-reapplydisplaymode-title-block`. Full detail: `PORTING-STATE` Session 342.

-197. **(s341) M5 audio de-stubbing step 5: queued a 6-run soak batch to measure crash-family #3/#4
    rates — superseded by item -198's finding that the underlying gate config never reaches title at
    all.** Wrote 6 self-contained recipes (`m5step5_rate_1..6.sh`, `HOLD_S=300`) against the
    then-current both-gates-reversed build; no soak run this session. Full detail: `PORTING-STATE`
    Session 341.

-196. **(s340) M5 audio de-stubbing: promoted BOTH `setDisplayMode`'s and `reapplyDisplayMode`'s
    gate-byte reversals to the PERMANENT shipped default — the promotion's original validation basis
    was later found invalid (s342, see Overturned Conclusions), but the promotion itself was never
    reverted and is still the current gate state as of s345.** 2 soaks were believed to validate
    combining both reversals; s342 found neither soak had actually left the pre-title screen. Edited
    `fixup_game_funcs.py`'s gate regex (N64Recomp repo, untracked) to permanently match neither
    audio-gate address. `M5-AUDIO-PLAN.md` step 4 marked DONE, pointing at step 5 (crash-family #3/#4
    rate comparison, still open as of item -201). Full detail: `PORTING-STATE` Session 340.

-195. **(s339) M5 audio de-stubbing: source-proves `submitGfxFrame` structurally cannot produce a
    `FramebufferPair`, and that `cinematicLoopBody`'s self-loop calls the real `SET_COLOR_IMAGE`
    producer (`runVideoFrameTick`) exactly ONCE — not per-iteration — resolving the s329-s338 VI=640
    `pairs=0` chase (item -160..-194 below) in 1 iteration, no new soak.** `submitGfxFrame`'s full
    callee set has no `setupCameraMatrices`/`emitFrameRdpInitDl`/`runVideoFrameTick`/
    `advanceVideoFrame` — only buffer-arbiter/SP-task-producer bookkeeping. Confirmed at runtime:
    `[static6-800a9abc-entry]` fires exactly once for a ~600s soak, matching s333's raw
    "`runVideoFrameTick` stops after exactly 2 calls" (1 from `mainGameLoop` + 1 here = 2).
    Conclusion: nothing is actually stalled — the self-loop runs correctly the whole time; it just
    never re-emits `SET_COLOR_IMAGE` after its one-time pre-loop RDP-state setup, so
    `[vi-fs-decision]`'s `pairs` counter faithfully reads 0 for the rest of the scene (very likely not
    a bug — a locked-camera cutscene reusing one RDP-state prologue is ordinary). Full detail:
    `PORTING-STATE` Session 339.

-160..-194. **(s297-337) M5 audio de-stubbing: the full gate-byte-reversal and VI=640-stall
    measurement-chasing arc, 41 sessions of instrumentation each superseded by the next, closed by
    item -195's source proof.** Chased a "missing call count" through 2 diagnostic-cap bugs to a
    false 14-call gap (closed s325: the gap was the bug itself), found and fixed the `setDisplayMode`
    VI=320 hang (a spin loop starved of `musyxSynthFrame` pumps, s326/327, confirmed 3/3 s328), then
    chased `reapplyDisplayMode`'s VI=640 stall through 5 reachability probes to `cinematicLoopBody`'s
    internal self-loop, resolved by item -195. Along the way: `initMusyXEngine`'s gate found to be
    dead code, never called (s306, see Overturned Conclusions). Full paragraph migrated to
    `docs/PROJECT-OVERVIEW.md` §9 (s346 maintenance pass); full raw detail: `PORTING-STATE` Sessions
    297-337.

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

- **(s339→s340→s342)** "The VI=640 `pairs=0` plateau is a benign, locked-camera mission cutscene" (s339)
  and "s340's 2/2 clean soaks validate promoting both audio gate reversals together" (s340) — s342
  found both soaks (and s341's 2 follow-ups) never left the pre-title attribution/logo screen: 0
  `[keys]` lines in all 4 raw logs, and `run_mission_keys.sh`'s wait-for-VI=1024 gate mechanically
  cannot reach its `SCHEDULE`/`HOLD_S` logic without first seeing VI=1024, which never happened.
  Believable: the soaks genuinely were crash-free for the full 600s with audio/DMA/voice counters
  visibly live throughout (a real same-run positive control) — it just never occurred to check whether
  the `[keys]` schedule had actually fired. The underlying `pairs=0` mechanism (item -195's source
  trace) is not overturned, only its context: it onsets pre-title, not mid-mission-cutscene, and is
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
