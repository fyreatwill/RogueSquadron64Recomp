# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Nine passes so far
   (s295-330 x5, s346, s355, s364, s371) kept the file oscillating around the cap as new session detail
   accrues; this is the tenth (s380), migrating the closed s371/s373-376 M5 Step 6/C88-investigation
   arc to PROJECT-OVERVIEW §12. Full per-pass detail in git log. 35 KB remains a stretch target, not a
   hard floor -- the "Current truth" env-var/timeline prose and the Regeneration section's Standing
   warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: design doc + steps 1-5 DONE and fully CLOSED (full arc: PROJECT-OVERVIEW
   §10, §11). Step 6 (PCM sanity-check) is ANSWERED: real PCM is 100% silent, root-caused to the same
   C88 force-zero patch that keeps title-reach working; a genuine host-bridge byte-count bug found en
   route is fixed (`queue_samples`, see Overturned Conclusions). The follow-on investigation into WHY
   reversing that gate hangs pre-title, and what drives the VI 640→1024 transition under it, ran to
   completion and closed by elimination, not by a fix — full arc: PROJECT-OVERVIEW §12. **No M5 audio
   thread remains open as of s376** — next M5 work needs a genuinely new lead. Current work unit is the
   sanctioned tooling item below instead (NEXT.md).
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md.

Sanctioned tooling work unit: backport function-scoped matching (the BREADCRUMB10+ slice idiom) to the
file-scoped-only guard patches in `fixup_game_funcs.py`, per the 2026-08-04 analysis in that file's header
comment. **CLOSED OUT as of s386.** Real count 176 (an AST scan, not a grep guess). **168/176 converted
across 9 batches (s377-379, s381-386)**, all verified byte-identical fixup-report output before/after, all
built and soaked clean. The remaining **8 sites are confirmed permanent exclusions by design**, not
backlog — none fit the function-scope idiom, for reasons specific to each (listed below). This task will
not resurface as a recurring work unit; only the two follow-up items named below remain live. Process
notes accumulated across the run: (s379/s381) run verification (regen+diff) AND the soak in the
orchestrating session, not a delegated subagent — both cross-repo regen commands and launching the
compiled binary hit sandbox permission/approval gates a subagent cannot satisfy non-interactively;
delegate ONLY the conversion-editing step. (s382) once remaining sites stop being one big single-file
cluster, delegate the "which target function does this site belong to" identification pass to a read-only
Explore/general-purpose agent; but for small counts (≤4 sites, as in the closing batch), doing the
identification directly in the orchestrating session is faster and just as safe. Launching the compiled
binary needs a tiny `zsh script.sh` wrapper that `cd`s into `build/` then `exec`s the binary — an inline
`env VAR=1 /abs/path/to/binary` runs with the wrong cwd and silently degrades to a ROM-less false-clean
soak. (s384) the byte-identical regen-diff check is not a formality — it caught a real scope
mis-attribution once (`musyxSynthFrame`'s `[synth-rearm-ptr]` diagnostic actually belongs to
`initN64RspMixer`). (s385) standing exclusion lists given to an identification agent must be by
address/anchor, not just function name, or the agent can't recognize an excluded site named only in prose.
(s386) triage lists drift as line numbers shift between batches — a re-scan can undercount how many sites
are genuinely untriaged; this session's fresh identification found 4 untriaged singleton sites where
s385's list said 3 (`loadCraftShadowTextures` had been missed), so always re-derive the candidate list from
a fresh `scan_filescoped.py` + line-content read rather than trusting a prior session's named list at face
value.

**Final state of the 8 sites originally called permanently-excluded**: (1) the whole-file `$zero`-write
comment-out sweep (~2700 sites, by design — every occurrence needs the same blanket transform); (2) the
`0x8008EC88` `reapplyDisplayMode` audio-gate hand patch (deliberately volatile/experimental, file-scoped
on purpose); (3-4) the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair (deliberately dual-target);
(5) the `_s284_deref_guard_sites` multi-function guard loop (deliberately multi-function); (6) the
`runHangarMenuFromOverlay`/`hasKasanMoorDefected` bare-label collision (FIXED s387 — this was a real bug,
not by-design, so it's out of the exclusion set); (7) `tickAudioSequencerFrame`'s exit diagnostic (match
text spans past this function's own body into the next function's signature, can't be body-scoped without
breaking it — genuinely permanent); (8) `musyxSynthFrame`'s `synth-rearm-ptr` diagnostic, now FIXED s388 —
converted to function-scope on its real owner `initN64RspMixer` (see below). **Both follow-up items from
s387 are now resolved; the backport thread has no remaining live work.**

(s387) `runHangarMenuFromOverlay`/`hasKasanMoorDefected` collision: fixed. Added `p.name == "funcs_43.c"`
to the `L_800C68AC:` bare-label patch so it only fires in `runHangarMenuFromOverlay`'s real home file,
not `hasKasanMoorDefected`'s (a different overlay function that happened to reuse the same local-label
text). Byte-identical regen-diff confirmed exactly one file changed (`funcs_29.c` lost the spurious
match, `funcs_43.c` unaffected); build+soak clean (0 crash markers, full VI phase timeline).

(s388) `musyxSynthFrame`/`initN64RspMixer` `synth-rearm-ptr` ownership question: resolved. Confirmed
directly against the generated `funcs_24.c` (`grep -n` for both `RECOMP_FUNC` signatures and the
`0x800919D4` anchor): `initN64RspMixer` starts at the line immediately before the anchor with no
intervening function boundary, and `musyxSynthFrame`'s own body ends well before it — the anchor is
unambiguously inside `initN64RspMixer`, confirming s384's finding. Converted the patch from file-scope
(`p.name == "funcs_24.c"`) to function-scope on `initN64RspMixer` (both functions already live in the
same file, so this is a defensive/correctness improvement against a hypothetical future duplicate anchor
elsewhere in the file, not a behavior change). Byte-identical regen-diff confirmed: 374-line fixup report
identical, full 45-file `RecompiledFuncs/` tree SHA-256 identical before/after — the site is unambiguous
(sole occurrence of the anchor text in the file) so tightening its scope changes nothing about the
generated code. Build clean; soak clean (0 crash markers over 15,750 log lines, healthy VI/present
progression as positive control — `present-1024`/`w=512` markers firing continuously, VI update counter
reached #6528+ over 110s).

## Current truth (established by session 295; unchanged, reviewed through s372)

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
oldest). Current top is -240 (s390); the next new item takes -241 and is inserted at the top.

-240. **(s390) M3 idiom-class audit: `hangarInitialize` "chunk 2" of the `-0x25A4` hangar-list-pointer
    family, 11 sites guarded.** The s389 soak population was fully mined; queued 3 fresh unbiased soaks
    (`scratch/agent/soak_queue/s390_freshpop1/2/3.sh`) for a future cycle and, per NEXT.md's fallback,
    delegated an Explore-agent sweep of every numbered guard family in `fixup_game_funcs.py`. Found the
    `HANGARLIST_GUARD`/s283-285 `-0x25A4($s1/s4/s5)` global-pointer family is **self-documented as
    incomplete**: s284's own comment says `hangarInitialize` (funcs_27.c, 103 of 172 raw hits, a single
    13,770-line function) was deliberately parked as its own multi-session item; s285 patched only a first
    "chunk" (lines 119818-124175, `S285_H1_BAIL`) and no chunk 2 was ever written — 65 sites remained
    completely unguarded, lines 124175-133587. Scoped this session to the next two bounded internal
    sub-blocks (chunk 2a: lines 124202-125013; chunk 2b: 125014-125822), each ending at its own natural
    `return;`/epilogue — reused both existing epilogue labels (`L_800AB1A4`, `L_800AB618`) directly, no new
    labels needed. Delegated classification (2 Explore-agent passes) found 11 NEEDS-GUARD sites + 1
    confirmed-SAFE (pointer only passed as a call arg, never dereferenced); hand-verified the trickiest
    sites myself directly against the generated source before writing the patch (all matched, no
    corrections). Verified: byte-identical-except-intended-diff regen protocol (only `funcs_27.c` touched,
    diff was exactly the 11 guard-block insertions); build clean; 3 soaks, none crashed inside or
    downstream of the new guards or shared a guest-address family with the `-0x25A4` idiom (one hit the
    exact already-closed heapWalker-GUARD5 background-noise address, `0x8000834c`; the other two hit
    addresses outside `hangarInitialize` entirely, not previously catalogued but structurally unrelated).
    0 guard fires across all 3 runs (proactive/defensive fix, matching every prior guard in this family).
    ~54 raw `-0x25A4` hits remain in `hangarInitialize` past line 125822 (a future chunk 3+). Full detail:
    `PORTING-STATE` Session 390; next work unit: NEXT.md — continue the SAME class (chunk 3, not a new
    candidate), since it's self-evidently unfinished and the sibling-audit-sweep cost is already paid.

-239. **(s389) M3 idiom-class audit: "Lookup" struct-family unguarded table-base-pointer dereference, 4
    sites guarded.** First systematic M3 audit since the backport thread closed. Candidate search (tally
    of `[CRASH][last-guest-pc]` across ~24 recent soaks) surfaced `0x800ad0dc`
    (`pc-symbol=findLookupEntryByKey+1864`) recurring at n=2, independently dismissed twice before
    (s359, s370) as "off-target" noise for other threads. Investigation found the pc-symbol attribution
    itself was WRONG: the address is not in `findLookupEntryByKey` at all (guest range
    `0x800642A0-0x800643C0`) but inside `hangarInitialize`/`static_5_800AB658` (real symbol
    `updateHangarBayScene`), a huge already-heavily-patched function, at a fixed-global store fed by a
    possibly-upstream-corrupted register — not a hash-table dereference, and not safely fixable without
    much deeper root-causing of that function's own patch history. **Same failure mode as the
    long-catalogued `0x8000b650` staleness** (nearest-symbol misattribution), just not previously flagged
    for this address — worth remembering if `findLookupEntryByKey+1864` recurs again. Pivoted within the
    same work unit: `findLookupEntryByKey` and 2 siblings (`removeLookupTableEntry`,
    `getLookupEntryField5`, `relocateLookupEntryToNewKey` — all `funcs_14.c`/`funcs_15.c`) share the
    identical unguarded idiom already fixed for their sibling `setLookupEntryField5ByKey` (s260,
    `SETLOOKUP_TABLE_GUARD`): a table-base pointer loaded from the struct's offset 0, dereferenced via
    `index*8+base` with no range check. `destroyLookupTable` checked and confirmed out of class (only
    passes the pointer to `rs_free`, never dereferences it directly). Guarded all 4 remaining sites
    reusing the exact s260 KSEG0-range+hi-word check, bail semantics matched to each function's own
    control flow (plain `return`/`ctx->r2=0; return`/`goto` to the real epilogue for the one function with
    a stack frame). Verified: byte-identical-except-intended-diff regen protocol (only `funcs_14.c`/
    `funcs_15.c` touched, diff was exactly the 4 guard-block insertions); build clean; 3 soaks (2 died to
    already-catalogued unrelated crash families — `coalesceFreeHeapBlocks+4424` and the
    `waitForAnyAudioSlot` boot-crash class — 1 fully clean, 304s hold, full `0→320→640→1024→512→640` VI
    timeline). 0 guard fires across all 3 runs (proactive/defensive fix, not a response to reproducing
    corruption — the sibling function's own guard had already proven this idiom dangerous once). Full
    detail: `PORTING-STATE` Session 389; next work unit: NEXT.md — pick a fresh idiom-class candidate the
    same way (the current soak_results population is now fully mined for this cycle).

-238. **(s386) batch 9/N: final 4 sites converted (168/176 total), backport CLOSED OUT.** Target:
    `loadCraftShadowTextures` (funcs_16.c, table-index guard), `mat3x3InverseInto` (funcs_5.c, det/inverse
    diagnostic), `tickTextureMaterialExpiry` (funcs_6.c, MATEXPIRY_GUARD node-walk pointer guard),
    `coalesceFreeHeapBlocks` (funcs_0.c, next-block-header read guard). Fresh `scan_filescoped.py` re-scan
    found these were the true remaining untriaged set — s385's list said only 3 untriaged sites
    (`mat3x3InverseInto`, `tickTextureMaterialExpiry`, `coalesceFreeHeapBlocks`), but a 4th
    (`loadCraftShadowTextures`) had been missed; the "9 confirmed intentional exclusions" count in s385's
    NEXT.md was also off by one (actually 8). All 4 sites' anchors verified to sit cleanly inside their
    named function's own body span (checked against `RECOMP_FUNC` boundaries in the generated
    `RecompiledFuncs/*.c`, no cross-function spillover) before delegating the conversion edit to a
    subagent; all 4 converted without needing to fall back to file-scoped. Byte-identical regen-diff
    verified clean (fixup-report and full `RecompiledFuncs/` tree both diff empty before/after). Build
    clean. Soak clean: 0 crash markers over 17,355 log lines across 120s, VI reached the full
    0→320→512→640→1024 phase timeline. Post-batch re-scan confirms exactly **8 file-scoped sites remain,
    all matching the previously-identified permanent-exclusion list** — the backport is done; see the
    Sanctioned tooling paragraph above for the final site-by-site breakdown and the two live follow-up
    items. Full detail: `PORTING-STATE` Session 386; next work unit: pick up one of the two follow-up
    items, or move to M3 idiom-class audits per the standing strategic-priority order (M5 has no open
    thread as of s376).

-237. **(s385) batch 8/N: 16 more converted (164/176 total), no regression this batch.** Target: 17
    sites across 15 functions in 8 files (funcs_1/4/14/15/23/24/26.c — `convertMat3x4ToN64Mtx`,
    `submitDmaRequestBatch`, `piDmaWorker`, `setupSongRenderBuffers`, `buildSongDecodeBufferRing`,
    `musyxMixActiveVoices`, `isAudioSlotActive`, `tickAndReap3DAudioVoices`, `factor5MutexAcquire`,
    `factor5MutexRelease`, `setupCameraMatrices`, `traverseSceneGraphRecursive`, `activateAnimationKeyframe`,
    `setLookupEntryField5ByKey`, `initMusyXEngine`, `resetMusyXEngineState`), identified by a delegated
    read-only Explore agent from the fresh 28-site scan; 1 of the 17 (`tickAudioSequencerFrame`'s exit
    diagnostic) was correctly declined by the conversion subagent because its match text spans into the next
    function's signature line and can't be body-scoped without breaking it — left file-scoped, matching this
    backport's standing rule. Byte-identical regen-diff verified clean this time (unlike s384, no regression
    found). Build clean; soak clean (0 crash markers over 10,757 log lines, VI reached the full
    0→320→640→1024 timeline at 45.5s, matching batch 7's 45.6s closely, held at 1024 for ~1500 further frames
    before SIGKILL). **New process finding**: the Explore agent's recommended batch included the volatile
    `0x8008EC88` `reapplyDisplayMode` audio-gate hand patch — a standing exclusion, but the agent wasn't given
    it by address, only by function name for other exclusions, so it didn't recognize this one; caught by the
    orchestrating session reading the patch's own comment before delegating conversion. Lesson: give
    standing-exclusion lists to identification agents by address/anchor, not just function name. **12
    remain**, most now understood to be intentional design exclusions rather than untouched backlog. Full
    detail: `PORTING-STATE` Session 385; next work unit: NEXT.md (batch 9, or close-out review).

-236. **(s384) batch 7/N: 17 more converted (148/176 total), plus verification caught a real
    regression.** Target: 9 functions across 8 files (`musyxSynthFrame`, `initFactor5Mutex`,
    `update3DAudioFrame`, `tickAllActiveSongs`, `viRetraceHandlerThread`, `waitForPostSwapAck`,
    `updateAnimatedTextureStreaming`, `static_5_800B4048`, `selectPostCrawlCraft`), identified by a
    delegated read-only Explore agent from the fresh 45-site scan. The byte-identical regen-diff check
    (not a formality this time) found one real drop: `musyxSynthFrame`'s `[synth-rearm-ptr]` diagnostic
    went from 1 match to 0, because its `0x800919D4` anchor actually lives inside `initN64RspMixer` (the
    next function over), not `musyxSynthFrame` as an old s101-era design comment assumed — scoping to the
    wrong function silently dropped the patch. Reverted that one site to file-scoped (its original,
    proven-correct form), converted 17 (not 18) sites this batch. Re-verified byte-identical after the
    fix; build clean; soak clean (0 crash markers, VI reached the full 0→320→640→1024 timeline at 45.6s,
    matching batch 6 almost exactly). **28 remain.** The `runHangarMenuFromOverlay`/`hasKasanMoorDefected`
    collision resurfaced at this iteration's fresh line numbers, still parked. Full detail: `PORTING-STATE`
    Session 384; next work unit: NEXT.md (batch 8).

-235. **(s383) batch 6/N: 21 more converted (131/176 total).** Target cluster: 4 functions in
    `funcs_4.c` (`processSceneNode` ×10, `renderUnlitMeshFaces` ×7, `drawSubtitleText` ×2,
    `evalCubicSplineAtTime` ×2), identified by a delegated read-only Explore agent from the fresh 66-site
    scan. Byte-identical regen-diff verified (375-line report and full tree both zero-diff); build clean;
    soak clean (0 crash markers, VI reached the full 0→320→640→1024 timeline in 45.6s). **New finding**: a
    genuine latent multi-file collision at the `runHangarMenuFromOverlay` site (~line 8299) — its bare
    label anchor also matches an unrelated function (`hasKasanMoorDefected`) in a different overlay file,
    so today's file-scoped patch silently double-targets; parked untouched, needs a dedicated `p.name`-
    filtering fix, not a function-scope conversion. Also confirmed the `initFactor5Mutex`-adjacent region
    is 6+ distinct functions despite line/file adjacency (correcting a prior session's proximity-based
    mis-scan). **45 remain**. Full detail: `PORTING-STATE` Session 383; next work unit: NEXT.md (batch 7).

-234. **(s381) batch 4/N: 21 more converted (89/176 total).** Target cluster: the musyx/audio-heap
    instrumentation block in `funcs_23.c` (`musyxInitVoiceFromSample`, voice-slot-ptr init,
    `tickAudioChannel`, `serviceVoicePoolFrame`, `tickAudioSeq`, `tickAllAudioChannels`, 3 `musyxGate`
    counters, `musyxRawgate`, audio-drain call/iters, `streamNodeInit`, `voiceAttackEntry`,
    `voiceActiveGate`, `songArrayAlloc`, song-count-write-early, shutdown-audio-free, rs-malloc
    asset-alloc). Byte-identical regen-diff verified (375-line report and full tree both zero-diff);
    build clean; ~130s soak clean (0 crash markers, VI traversed the FULL 0→320→512→640→1024 timeline).
    **New process finding**: unlike batches 1-3, the delegated subagent could not complete VERIFICATION
    either this time (not just the soak) — every cross-repo regen command (`make_elf.py`, even a bare
    `rm -f RecompiledFuncs/funcs_*.c`) hit a hard sandbox permission denial distinct from s379's
    binary-launch gate. Orchestrating session took over verification+build+soak directly. **Standing
    rule updated**: delegate ONLY the conversion-editing step to a subagent; run regen-diff
    verification, build, and soak all in the orchestrating session. **87 remain**, no single
    obviously-largest cluster left (scattered 1-5-site sub-clusters) — batch 5 re-scans cold. Full
    detail: `PORTING-STATE` Session 381; next work unit: NEXT.md (batch 5).

-233. **(s379) batch 3/N: 24 more converted
    (68/176 total), entire `funcs_3.c` drain-mesh/heap-walker cluster now fully converted.**
    Delegated convert+verify+build to a subagent. Verification method, established batch 1 and reused
    unchanged every batch since: regen `RecompiledFuncs/` fresh twice (pre-batch backup script vs.
    converted script), diff both the patch report and the output tree — byte-identical/zero-diff means
    no latent cross-function anchor collision, the one failure mode worth stopping for. Converted:
    `beginFrameDLChunk` (1), `emitAllocatedDLCommand` (2), `heapWalker` (4), `heapFreeListDequeue` (2),
    `drainMeshReleaseQueue` (15). Build clean. **Soak process note**: the subagent could not launch the
    compiled binary itself — every attempt hit the harness's interactive-approval gate from its
    non-interactive sandbox, a clean blocked-before-start state. The orchestrating session ran the
    soak directly instead: ~110s, 0 crash markers, VI traversed the FULL 0→320→512→640→1024 timeline.
    **Standing rule for batch 4+: run the soak step in the orchestrating session, not a delegated
    subagent.** Excluded site-classes (`0x8008EC88` audio gate; `waitForMusyXAudioTaskDone`/
    `shutdownAudioEngine` pair) confirmed untouched. **108 remain**, no single obviously-largest
    cluster left — re-scan cold and pick whatever groups cleanly. Full detail: `PORTING-STATE`
    Session 379; next work unit: NEXT.md (batch 4).

-232. **(s378) batch 2/N: 21 more converted (44/176 total).** Same delegated methodology and
    byte-identical-regen-diff verification as batch 3 above. Converted across 8 functions:
    `reserveAndEmitDLEntry` (2), `activateAnimationKeyframe`, `composeNpcOrientationMatrix`/
    `static_5_800AB1C8` (9), `projectModelBoundsToScreen` (3), `updateHangarBayScene`/
    `static_5_800AB658` (3), `musyxSynthFrame`, `acquireSampleStreamBlock`, `fillSampleStreamRange`.
    Build clean; ~100s soak clean, VI progressed the FULL 0→320→640→1024→640→512 timeline (evidence
    batch 1's stuck-at-320 soak was ordinary run-to-run timing variance, not a regression — Method
    traps §4.3). Excluded site-classes confirmed untouched via diff. **132 remain**; next batch's
    clear target was the `funcs_3.c` drain-mesh/heap-walker cluster (drawn down by batch 3 above).
    Full detail: `PORTING-STATE` Session 378.

-231. **(s377) batch 1/N: 23 of 176 file-scoped patches converted** (real count from an AST scan of
    `re.subn(..., text, ...)` call sites, not a grep guess — vs. the docstring's prior "~150"
    estimate). Converted to the BREADCRUMB10-15 function-scoped idiom: `musyxSynthFrame`,
    `runVideoFrameTick`, `reapplyDisplayMode`, `mainGameLoop`, `menuOverlayInit`,
    `cutsceneDispatchSlotsByFlag`, two `static_N_0xADDR` functions, `musyxKeyOnVoice` (8),
    `evalCubicSplineAtTime`, `advancePlayerAnimationPhase`, `updateAnimatedTextureStreaming`, two more
    `static_N` diagnostics, `reserveAndEmitDLEntry` (3). Established the byte-identical-regen-diff
    verification method reused every batch since; build clean, ~70s soak clean (0 crash markers; VI
    stayed at 320, later batches showed this was ordinary timing variance, not a regression — Method
    traps §4.3). Two site-classes deliberately left file-scoped: the volatile `0x8008EC88` audio-gate
    hand patch, and the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair (shared regex is
    intentionally dual-target, not a mis-scoped single anchor). Full detail: `PORTING-STATE`
    Session 377.

-226..-230. **(s371, s373-376) M5 Step 6 (PCM sanity-check) and the C88-reversed pre-title-hang/
    VI-trigger investigation — all CLOSED.** s371 answered Step 6: real PCM is 100% silent even under
    genuine RSP-dispatched real ucode (13,832 logged `[pcm-sanity]` calls, 0 non-zero — a
    positive-controlled result), and found+fixed a real host-bridge bug en route (`queue_samples`
    silently dropped half of every buffer's bytes — see Overturned Conclusions). s373 root-caused WHY:
    `reapplyDisplayMode` unconditionally re-zeros the audio-tick gate every video frame and never
    durably re-enables it, because its own re-enable site is the same `0x8008EC88` address
    `fixup_game_funcs.py` force-zeros to keep title-reach working — so voice population never gets a
    window to run; the ucode mixing exact zeros is correct behavior on empty input, not a mixing bug.
    s374 found a plausible single-token-mutex-deadlock candidate for why reversing that gate hangs
    pre-title; s375's build+soak REFUTED it cleanly (9131/9131 balanced mutex acquire/release, never
    blocks) — `HYPOTHESIS-ID m5-audio-destub-c88-pretitle-hang` CLOSED: there is no hang, C88-reversed
    just never re-triggers the VI 640→1024 transition. s376's source-only pass discriminated three
    candidate trigger mechanisms (reset-branch divergence, shared-mutable-state collision, real
    completion-condition wait) and REFUTED all three cleanly — `HYPOTHESIS-ID
    m5-audio-vi640to1024-trigger-site` CLOSED by elimination, not solved (the remaining diffuse
    frame-timing fallback wasn't worth a build cycle, since real audio stays silent regardless per
    s373). **No M5 audio thread remains open as of s376** — next M5 work needs a genuinely new lead.
    Full detail: `docs/PROJECT-OVERVIEW.md` §12; raw detail `PORTING-STATE` Sessions 371, 373-376.

-225..-210. **(s354-370) M5 Step 5 guard-hunting arc — Thread A (`coalesceFreeHeapBlocks`), Thread B
    (`drainMeshReleaseQueue` linked-list corruption), and a heapWalker background-noise site (GUARD5)
    all CLOSED.** Full blow-by-blow (every guard site, fire count, and soak-tooling lesson): `docs/
    PROJECT-OVERVIEW.md` §11; raw detail `PORTING-STATE` Sessions 354-370. One-paragraph summary:
    Thread A (`m5-audio-destub-coalesce-heap-guard-verify`) opened s354 on an independent
    `coalesceFreeHeapBlocks+3452` repeat; s358 found the guard's own bail target re-entered the loop
    instead of exiting it, fixed; closed s366 with 6/6 non-recurrence soaks post-fix. Thread B
    (`m5-audio-destub-linkedlist-corruption-source`) opened on s352's `bad_v1=0x00010001` lead
    (byte-identical across 2 sessions, ~1-in-4-billion coincidence odds) and found THREE distinct
    unguarded pointer families across `drainMeshReleaseQueue`'s five structurally identical tail-scan
    loops (tail-cursor read+write pairs s354-361; head-pointer read+clear-write pairs s363; a third
    "previous tail" family s365), plus a s366 full-function audit confirming coverage exhaustive;
    closed s368 with `s367`'s verify pair both crashing OUTSIDE the function after it completed and
    returned normally, every guard family positive-controlled (fired) in the same runs. A heapWalker
    background-noise crash surfaced by those soaks (`heapWalker+1696`, `last-guest-pc=0x8000834c` —
    coincidentally `drainMeshReleaseQueue`'s own return checkpoint, not a link between the bugs)
    reached n=4 by s368, crossing the catalog's 3rd-hit confirmation trigger; s368-369 binary-analysis
    (hand-extending `s193_disasm.py`, `otool`/`nm`/`objdump`/`dwarfdump` still sandbox-blocked) mapped
    it to guest address `0x80007A3C` + 4 unrolled siblings, the same unvalidated-pointer idiom already
    guarded 4x elsewhere in `heapWalker` — guarded as GUARD5, closed s370 with 2/2 non-recurrence (one
    full clean 302s hold recovered from raw logs after an 8.7 GB `run.log` defeated the soak wrapper's
    own timeout — new lesson: an `rc=137`/empty-wrapper-log verdict is not automatically
    uninformative, check the raw launcher/run.log before discarding). **Net as of s370: no M5 Step 5
    or escalated-background-noise threads remain open** — next M5 work was Step 6, since closed
    (item -226..-230).

-209..-195. **Sixteen sessions (s339-353), M5 gate-promotion/step-5-crash-rate/drainMeshReleaseQueue
    tail-scan arcs — all CLOSED/superseded.** VI=640 `pairs=0` stall resolved as an ordinary one-time
    RDP-state prologue, not a stall (s339). Both audio gates were briefly promoted to default (s340, on
    a since-overturned validation basis — Overturned Conclusions), then `reapplyDisplayMode`'s reversal
    alone was found to deterministically block title-reach (0/5, s342) and reverted, restoring
    title-reach (3/3, s344) but surfacing a `tickWrappingTimerAccumulatorList` div-by-zero PARKED at 1/3
    recurrence (`m5-audio-destub-tickwrap-divzero-craftselect`, reopens on
    `last-guest-pc=0x80054744`). **Current gate state, unchanged since s343**: fixup regex force-zeros
    ONLY `reapplyDisplayMode` (`0x8008EC88`); `setDisplayMode` (`0x8008EB40`) stays reversed. A
    crash-rate-comparison methodology arc (s341-352) found the post-title crash rate diffuse across
    symbols until a re-analysis showed the TIMING was bimodal and a corrupted pointer
    (`bad_v1=0x00010001`) reproduced byte-identically across 2 sessions — became Thread B's origin lead
    (item -225..-210). `drainMeshReleaseQueue` tail-scan cluster (s348-353): 3 crash sites GUARDED; the
    `[scene-node-content-guard]` from this is now known steady-state-benign, not corruption evidence
    (Overturned Conclusions). Full detail: PROJECT-OVERVIEW §10; raw: `PORTING-STATE` Sessions 339-353.

-160..-194. **(s297-337) M5 audio de-stubbing: the full gate-byte-reversal/VI=640-stall arc, 41
    sessions of instrumentation each superseded by the next, closed by item -209..-195's (s339) source
    proof.** Chased a false "missing call count" (closed s325: the gap was the diagnostic-cap bug
    itself), fixed the `setDisplayMode` VI=320 hang (s326-328), then resolved `reapplyDisplayMode`'s
    VI=640 stall via `cinematicLoopBody`'s internal self-loop (s339). `initMusyXEngine`'s gate found
    dead code, never called (s306, Overturned Conclusions). Full detail: PROJECT-OVERVIEW §9; raw:
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
  the step-5 corruption-source hunt. PORTING-STATE 348, 350, 352; CURRENT-TRUTH item -209..-195.
- **(s339→s340→s342)** "The VI=640 `pairs=0` plateau is a benign, locked-camera mission cutscene" (s339)
  and "s340's 2/2 clean soaks validate promoting both audio gate reversals together" (s340) — s342
  found both soaks (and s341's 2 follow-ups) never left the pre-title attribution/logo screen (0
  `[keys]` lines in all 4 raw logs). Believable: the soaks genuinely were crash-free with audio/DMA
  counters visibly live (a real positive control) — nobody checked whether the `[keys]` schedule had
  actually fired. The underlying `pairs=0` mechanism (PROJECT-OVERVIEW §10) is not overturned, only its
  context: pre-title, not mid-cutscene, specific to `reapplyDisplayMode`'s gate. PORTING-STATE 339, 340, 342.
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
  the same point, one shared upstream resource" (s307) — source-read found separate code paths (s309).
  "The 3 tick-producers and RSP `M_AUDTASK` all stop together at call #19/20" (s307/310/311) — a
  widened print-cap soak found `update3DAudioFrame` fires 40/40 (the real hard-stop boundary), the
  tick-producers stop 3 calls earlier at 37/37, and only `M_AUDTASK` genuinely stopped at 20/20 (s313) —
  which then turned out to be its own unwidened flat-cap diagnostic bug; widening found it also fires
  40/40 (s315). Net: 2 real stop points (37/37, 40/40), not 1 or 3. Believable each time: similar small
  round numbers read as simultaneous unless line numbers are diffed. PORTING-STATE 309, 313, 315.
- **(M5-AUDIO-PLAN.md §4→s371)** "The host bridge (`queue_samples`/`SDL_QueueAudio` wiring) is already
  fully implemented and functional" — a source read found `queue_samples`'s parameter is a sample count
  but was passed straight through as `SDL_QueueAudio`'s byte length with no `*sizeof(int16_t)`
  conversion, silently dropping the back half of every PCM buffer since this bridge was written.
  Believable: the wiring compiles/links/calls cleanly end-to-end, so eyeballing the call graph reads as
  "functional" — the defect is a unit mismatch one level down, only visible by checking actual values.
  Fixed s371 (`src/main/main.cpp`; mechanism detail: PROJECT-OVERVIEW §12). PORTING-STATE 371.

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
