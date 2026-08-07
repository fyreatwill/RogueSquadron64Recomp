# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Thirteen passes so
   far (s295-330 x5, s346, s355, s364, s371, s380, s391, s398, s409) kept the file oscillating around
   the cap as new session detail accrues; s398 migrated the closed s389-397 idiom-audit arc to
   PROJECT-OVERVIEW §14; s409 collapsed the s400-408 M4 item -249 bulk-relocation saga (9 items,
   ~195 lines) into one summary paragraph. Full per-pass detail in git log. 35 KB remains a stretch
   target, not a hard floor -- the "Current truth" env-var/timeline prose and the Regeneration
   section's Standing warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (full arc: PROJECT-OVERVIEW
   §10-§12). Next M5 work needs a genuinely new lead.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. **The `-0x25A4`
   family itself is fully closed (s283-s396)**, and s397's codebase-wide frequency scan for a next
   family found none of comparable magnitude — see item -239..-247. **This method is exhausted for now;
   leaving pure-idiom-audit mode for M3 needs human reconfirmation** (a different discovery tool, or
   falling back to M4/reopening M5).

Sanctioned tooling work unit (backport function-scoped matching to the file-scoped-only guard patches
in `fixup_game_funcs.py`): **CLOSED OUT as of s386/s388, no live work remains** — see item -231..-238
below and `docs/PROJECT-OVERVIEW.md` §13.

**s421: item -249 (M4's largest open item, the `main_overlay.txt` phantom-overlay-function relocation)
CLOSED** — 0 actionable candidates remain, 784 relocated, 14 permanently excluded (10 known-bad + 4
known-skip). **All three directive legs above are now closed or exhausted simultaneously** (M5 closed,
M3 idiom-audit-only exhausted since s397, M4 -249 closed s421) — **this directive needs human
reconfirmation on where to focus next.** **s422 CLOSED the one concrete follow-on lead s421 surfaced**:
the apparent `last-guest-pc=0x800290d4` "six independent triggers, one shared sink" pattern was root-
caused and overturned — `atos` source-line symbolication (a strictly better technique than this
project's prior nearest-symbol attribution, see item -259 below) showed the six known-bad functions
crash in five different real functions with no shared site; `last-guest-pc=0x800290d4` was only ever a
sparse breadcrumb's last checkpoint (`inflate_fast`'s own clean return), not a fault location. No
dedicated root-cause session is indicated there anymore. The only remaining un-acted candidate from
s421's list is M3 DoD resumption (see Goal stack, M3) — still awaiting human reconfirmation before an
autonomous session commits to it as the new standing direction.

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
move; what a leave-key actually leads to is unresolved. *Done when:* 60s of in-mission rendering,
craft visibly responds to synthetic input, stability counters 0, phase timeline covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it; the 3 `[missing-func]` addresses (item -6, **DONE s399**); the `main_overlay.txt`
phantom-overlay-function family (item -249, **CLOSED s421**: 784 relocated across s400-s421, 14
permanently excluded — 10 known-bad, 4 known-skip — 0 actionable remain; full session-by-session
narrative in item -249's Next-steps entry below and `PORTING-STATE` sessions 400-421). Ten known-bad
functions all stay parked (safe, correct) in `main_overlay.txt`/`m4_known_bad.txt` regardless of crash
site; **s422 found their apparent `0x800290d4` x6 clustering was a sparse-instrumentation artifact, not
a shared bug** — `atos` source-line symbolication shows five different real crash functions behind it,
no dedicated root-cause session indicated (item -259 below).

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.

## Next steps, in order of expected value (s295)

Numbering convention (fixed s295, was previously three colliding sequences): items are
numbered highest-magnitude-negative (top, newest/highest priority) counting up to -1 (bottom,
oldest). Current top is -259 (s422, CLOSED); the next new item takes -260.

-259. **(s422) `0x800290d4` "six independent triggers" lead — INVESTIGATED AND CLOSED, not a bug.**
    The s421 close-out flagged this as the strongest concrete lead left after M4 item -249. Root-caused
    from already-captured crash logs: `0x800290d4` is `inflate_fast`'s own clean return (its `jr $ra`
    delay-slot `nop`), and the `g_rs64_last_guest_pc` breadcrumb that reports it is sparse (8 of 50
    `RecompiledFuncs/funcs_*.c` files, piecemeal BREADCRUMB1-14+ passes) — so the shared value only meant
    all six known-bad functions passed through `inflate_fast`'s return at some point, not that they crash
    at or near it. Applying `env atos -o build/RogueSquadron64Recomp -l <base> <pc>` (works via `env`;
    resolves exact DWARF file:line, survives `-O2`, strictly better than this project's prior
    nearest-symbol attribution — a durable technique win) to 5 of the 6 isolate-alone crash logs found
    FIVE DIFFERENT real crash functions (`__osBlockSum`, `loadDatFile`, `menuControllerInput`,
    `freeCutsceneResources`, `allocT16EffectContext`; the 6th resolves to `npcWaterCraftHandleDestruction`
    with a distinct poison-byte signature). Audited `MEM_W`/`MEM_B`/`TO_PTR`, `do_rom_read`,
    `load_overlays_by_start`/`load_overlay` end to end — all correctly perform the guest-KSEG0-tag
    rebase; no shared translation or runtime bug found. **Conclusion: the six known-bad functions each
    independently trip one of this project's own ~20+ already-catalogued nondeterministic corruption
    families, newly exposed by executing for the first time (each pulls in a DAT/overlay decompression on
    its way to a distinct, unrelated crash) — not one fixable shared mechanism.** No action changes (all
    six stay parked in `main_overlay.txt`/`m4_known_bad.txt`, correct and safe); a dedicated
    "`0x800290d4` root-cause session" is no longer indicated. Full detail: `PORTING-STATE` Session 422.

-249. **(s400-421) M4 item -249: `main_overlay.txt` phantom-overlay-function relocation — CLOSED
    s421, no outstanding action.** 784 functions relocated to their correct overlay across 21 sessions;
    10 genuinely-buggy functions found via full sibling-independence bisection and permanently parked
    in `m4_known_bad.txt`, converging on 4 distinct downstream crash sites (`0x800290d4` x6 — the
    strongest root-cause-session candidate on the table, see USER DIRECTIVE — `0x80011088` x2,
    `0x80065e94` x1, `0x8000b650` x1); 4 more names permanently skipped (persistently
    NONE/AMBIGUOUS overlay classification) in `m4_known_skip.txt`. 0 actionable candidates remain per
    s421's fresh regen. Full arc (tooling, batch-size history, every bisection, the sibling-independence
    lesson, the mission/menu sampling-artifact false lead, close-out detail): `docs/PROJECT-OVERVIEW.md`
    §15; raw: `PORTING-STATE` Sessions 400-421.

-6. **(s53/s54→s399) M4 — the 3 `[missing-func]` addresses: DONE, CLOSED s399.** s54's applied fix
    (adding the 3 names to `mission_overlay.txt`) was dead on arrival -- silently shadowed by
    pre-existing duplicate entries at the same addresses in `main_overlay.txt`, which
    `make_elf.py` parses first (name-dedup, first-file-wins) and which then get dropped as phantom
    functions because `main_overlay.txt`-sourced symbols are range-checked against `.text`, not the
    overlay window (same mechanism as item -249 above -- this was the first-discovered instance of
    that family). Root-caused this session via `strings build/roguesquadron.elf` (names absent) and
    a repo-wide grep of N64Recomp's output (names nowhere), which s54 never checked. Fixed by
    deleting the 3 duplicate lines from `main_overlay.txt`; verified 3/3 post-fix runs now (2/2 s399
    live + s399's queued `s399_missingfunc_verify3.sh` PASSED, rc=0, s400 SOAK-RESULTS) -- target
    addresses 0/3 every time, matching phase reached, same-run positive control. Full detail:
    `PORTING-STATE` Session 399.

-239..-247. **(s389-397) M3 idiom-class audit resumption: `hangarInitialize`'s `-0x25A4`
    hangar-list-pointer family fully CLOSED, plus the "Lookup" struct-family (s389), TWO independent
    guard-placement bugs found+fixed, and a codebase-wide frequency scan for the next comparable idiom
    class — negative result, closing the pure-idiom-audit method for now.** s389 guarded the Lookup
    table-base-pointer family (4 sites). s390/s392/s393 chunked `hangarInitialize`'s 103 raw `-0x25A4`
    hits into guarded sub-blocks (chunks 2/3a/3b, 61 sites) after s285's chunk-1-only coverage was found
    self-documented-incomplete. s393 discovered chunk 3a's 29 guards all checked a STALE
    pre-load register instead of the freshly-reloaded pointer (anchors built to start BEFORE the raw
    load, not after) — invisible to soak verification because the fire-count diagnostic was never
    armed; s394 fixed all 29 with a re-extracted, uniqueness-verified anchor set (net-zero-line regen
    diff, soak-confirmed 0 fires with a same-run positive control). s395 found a SECOND, independent
    instance of the same bug class in the much older s285 chunk-1 family (`S285_H1_8` checking a
    65-lines-stale register) — added a correctly-anchored replacement guard (`S395_SWEEP_1`), left the
    broken original in place as harmless dead weight. s396 swept the two remaining files
    (`funcs_40.c`/`funcs_19.c`, 70 raw hits): 0 NEEDS-GUARD, closing the entire family (s283-396) with
    two independent lines of evidence (subagent per-site read + independent grep-count cross-check).
    s397 deleted the leftover `S285_H1_8` dead guard (safe by construction; soak verification
    inconclusive for reasons unrelated to the change) and ran a static base-register-origin classifier
    across the whole codebase for the next `-0x25A4`-scale idiom class: **zero candidates of comparable
    magnitude found** — the two next-highest-frequency displacements are both the mundane
    `lui`-addressed static-global idiom, confirmed by direct source read, not pointer chases. **Net: the
    `-0x25A4` family is fully closed; the frequency-scan discovery method is exhausted; M3
    idiom-audit-only mode needs human input to proceed** (a CFG-aware discovery tool, a return to
    crash-driven discovery, or a fallback to M4/M5 — see USER DIRECTIVE above). The queued soak
    `s397_h1_8removal_verify2` returned `NO_POSITIVE_CONTROL` (hangar scene not reached) — inconclusive,
    doesn't change the safe-by-construction verdict. Full detail: `docs/PROJECT-OVERVIEW.md` §14; raw:
    `PORTING-STATE` Sessions 389-397.

-231..-238. **(s377-386) Fixup function-scope backport, batches 1-9: 176 file-scoped guard patches
    identified (AST scan), 168 converted to function-scope, 8 confirmed permanent design exclusions.
    CLOSED OUT s386.** Per-batch functions, sizes, process lessons (sandbox-permission delegation
    rules, the `musyxSynthFrame`/`initN64RspMixer` scope-misattribution catch, the
    `runHangarMenuFromOverlay`/`hasKasanMoorDefected` collision, address-not-name exclusion lesson):
    `docs/PROJECT-OVERVIEW.md` §13. Exclusion breakdown + s387/s388 follow-ups: Sanctioned tooling
    paragraph above. Raw: `PORTING-STATE` Sessions 377-386.

-160..-230. **(s297-376) M5 audio de-stubbing arcs — gate-byte-reversal/VI=640-stall (41 sessions,
    s297-337), Step 5 guard-hunting (Thread A `coalesceFreeHeapBlocks`, Thread B
    `drainMeshReleaseQueue` linked-list corruption, heapWalker GUARD5, s354-370), gate-promotion/
    crash-rate-comparison (s339-353), and Step 6 PCM-sanity + C88 pre-title-hang/VI-trigger (s371,
    s373-376) — ALL CLOSED, no outstanding M5 thread.** Every mechanism, guard site, and soak-tooling
    lesson: `docs/PROJECT-OVERVIEW.md` §9-§12; raw: `PORTING-STATE` Sessions 297-376.

-159..-14 (excluding -20, kept below). **Ten closed investigation lineages (nine from s314, plus
    the s297-337 M5 gate-reversal arc folded in s346), s99-s337 — all CLOSED, no outstanding action.**
    Whack-a-mole guard-gap chases (`composeNpcOrientationMatrix`, `renderUnlitMeshFaces`, `heapWalker`,
    `heapFreeListDequeue`, `-0x25A4` hangar-list-pointer family, breadcrumbs B2-B14), the
    audio-array-corruption race fix (s145/147/148), the `submitDmaRequestBatch` indirect-caller find
    (s101), the CALayer/campose SIGSEGV hunt, the regen-pipeline-idempotency root cause, and the M5
    audio gate/VI=640-stall chase (item -160..-230 above). One-paragraph-per-lineage summaries:
    `docs/PROJECT-OVERVIEW.md` §9; full raw detail: `PORTING-STATE` Sessions 99-337.

-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic).** Root cause:
    `N64Recomp` skips rewriting any `RecompiledFuncs/funcs_*.c` file that already exists on disk, so
    any patch whose regex anchor survives its own insertion stacks a duplicate on the next
    `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every
    regen is mandatory but **not sufficient by itself** -- residual intermittency's root cause is
    still unknown. **Standing rule**: audit the patch report for anything other than the expected `xN`
    count after every `fixup_game_funcs.py` run. Full detail: `PORTING-STATE` Sessions 120, 121, 126.

-11. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89).** 3 consecutive non-recurrences since s88's correctly-targeted instrument, against 8 prior crashing soaks. `ROGUESQ_LOG_ANIM_CB=1` still live if it recurs.
-10/-9. **M3 — Metal-shader-compiler SIGSEGV reproducibility** (s83 spline1: SIGSEGV inside `Metal.framework`'s `MTLCompilerFSCache`, no source on our side; still one data point). **Confirm the s83 spline div0 guard actually engages**: 0/5 fires so far (still 0 after s88/s89/s90); real fix by code inspection (genuine 0/0 IEEE division) but no same-run positive control yet.
-8. **M3 — characterize `frameStartReset` SIGBUS.** 3 occurrences (s85, s108, s156 — the 3rd, `+532`, at a call chain byte-identical to `composeNpcOrientationMatrix`'s own, raising a shared-dispatcher hypothesis); no located faulting instruction in any of the 3.
-7. **M3 — HOLD_S=60 craft stick (M3 DoD body)** once earlier items clear: `PROBE_MODE=start_only HOLD_S=60` marks 10/25/40, document the phase timeline. Gate already keeps black off; residual S1 `fs` freeze (~3769-3872 plateau) may still stall animation.
-5. Past the first sustained mission hold: expect further new failure classes (mission overlay DMA → missing-func/UnhandledJumpTarget, new VI phase, overlays 12/44 splice, texture corruption — s399's item -248 is a concrete, proactively-found instance of exactly this). Each new failure is its own work unit.
-3. **Sibling-repo housekeeping (flagged s54, not autonomous):** `~/Documents/Tools/rogue_squadron64` carries uncommitted symbol-file edits, including s54's now-superseded `mission_overlay.txt` addition and s399's `main_overlay.txt` 3-line deletion (the actual fix). Ask the user before committing there.
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
- **(s107/108→s316→s318)** Two linked overturns in the gate1/2/3 tick-producer chase: (1) "the 3
  near-identical countdown/period gates fire `tickAllActiveSongs`/`tickAudioSequencerFrame`" was never
  positive-controlled across 4 sessions (only gate1's raw inputs were measured, never its branch
  outcome) — s316 instrumented all 3, found NONE ever takes "call," contradicting the 37-call count. (2)
  That itself was overturned by s318: the diagnostic re-read the shared countdown fresh instead of the
  register (`ctx->r2`) the real branch uses, racing the true value — direct `ctx->r2` measurement showed
  gate1 calls 19/40, gate2 4/4. Believable both times: matching disassembly, and a
  read-once-for-branch/re-read-for-print pattern easy to write without reintroducing a race.
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
- **(s2-31→various, ~15 claims, grouped)** Build/pixel-getting era, each overturned within 1-2 sessions:
  Z-buffers misread as colour buffers; texrect output called invisible; RDP "emitting nothing" (real
  bug: a function-local ring high-water mark); `DPC_WRAP`/fbpair-cap misdiagnosed for missing FULL_SYNC
  (§4.6); `PRIM_ALPHA_FF` called necessary for text; a sampling-artifact black-screen; misattributed
  texture dumps, floor-band line-mask/palette/dxt theories (M1's real cause: s44-49), fog-color
  attribution, S=0-triangle phase, stale-TMEM-at-draw (§4.1), 1024-phase black screen
  (present-starvation, not zero-shade). PORTING-STATE 2-31.
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
- **(s307→s309→s313→s315)** A chain of "audio-tick stop points converge" claims, each overturned by a
  closer same-run measurement: shared-upstream-resource theory (s307) refuted by source-read (s309);
  "3 tick-producers + RSP `M_AUDTASK` all stop together at #19/20" (s307/310/311) refined by a widened
  print-cap soak to 2 real stop points, not 1 or 3 (`update3DAudioFrame` 40/40, tick-producers 37/37,
  `M_AUDTASK`'s 20/20 was its own unwidened diagnostic bug, also 40/40 once widened, s313/s315).
  Believable each time: similar small round numbers read as simultaneous unless line numbers are
  diffed. PORTING-STATE 309, 313, 315.
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
