# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. Fifteen passes so
   far (s295-330 x5, s346, s355, s364, s371, s380, s391, s398, s409, s429, s438) kept the file
   oscillating around the cap as new session detail accrues; s429/s438 migrated the s426-438
   duplicate-symbol/breadcrumb saga to PROJECT-OVERVIEW §16. Full per-pass detail in git log. 35 KB
   remains a stretch target, not a hard floor -- the "Current truth" env-var/timeline prose and the
   Regeneration section's Standing warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: DONE and fully CLOSED, no thread open (full arc: PROJECT-OVERVIEW
   §10-§12). Next M5 work needs a genuinely new lead.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md. The original
   `-0x25A4` family is closed (s283-396); its frequency-scan discovery method is exhausted for GENERAL
   next-class discovery. **But s426-429 opened a live, higher-priority in-progress thread within the
   same M3 DoD leg**: duplicate-symbol-name collisions in the overlay `.txt` files silently truncate
   real function bodies to 1-instruction stubs (a third shape of the closed item -6/-249 "phantom
   function" family). This supersedes needing separate human reconfirmation on "where to focus next"
   for now — see item -274 (current top) and PROJECT-OVERVIEW §16 for the full session-by-session arc.

Sanctioned tooling work unit (backport function-scoped matching to the file-scoped-only guard patches
in `fixup_game_funcs.py`): **CLOSED OUT as of s386/s388, no live work remains** — see item -231..-238
below and `docs/PROJECT-OVERVIEW.md` §13. M4's largest item (-249) and its `0x800290d4` follow-on
(-259) are both CLOSED — see those items below for status.

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
oldest). Current top is -278 (s441, single occurrence, UNCONFIRMED — a new SIGSEGV crash class
in the thread-scheduler/semaphore runtime, unrelated to the 0x801163B0 free-list family);
the next new item takes -279.

-278. **(s441, single occurrence) NEW crash class: SIGSEGV inside the thread-scheduler/semaphore
    runtime, no game-code frames in the backtrace.** Surfaced during `s441_freelistnext_verify`
    (see item -277 below) — after that fix's own live-verify ran clean on all 3 free-list guard
    families (0 fires) and reached `[hangarbay-entry] n=1500+`, the process died at 109.9s with
    `signal 11 (Segmentation fault: 11)`, `si_addr=0x10fc0a00000060e3` (a wild 64-bit host
    address, matches `x8`), backtrace entirely inside the native runtime:
    `moodycamel::LightweightSemaphore::tryWait` (`_ZNKSt3__113__atomic_baseIlLb0EE4loadEv`) <-
    `wait_for_resumed` <- `resume_thread_and_wait` <- `swap_to_thread` <-
    `check_running_queue` <- `pause_self` <- `idle_thread_handle`. `last-guest-pc=0x8000834c` is
    almost certainly stale/uninformative here — this crash is on the idle/scheduler thread, not
    necessarily the same OS thread that last updated the shared `g_rs64_last_guest_pc` global, so
    it should NOT be read as a guest instruction address the way it is for the free-list family.
    Signature does not match items -261/-263/-270/-272/-277 (SIGSEGV not SIGBUS; wild 64-bit host
    pointer not a 0x38000000x near-zero guest pointer; no game-code frames at all). Single
    occurrence, no positive control, not yet investigated — per iron rule 1 this is a lead, not a
    result. **Next step if it recurs**: check whether `moodycamel::LightweightSemaphore`'s
    internal state (a semaphore count / linked waiter list) was itself corrupted, or whether this
    is a genuine race in `ultramodern`'s cooperative thread-swap implementation exposed by timing
    differences from the `-j8` rebuild. Confirmation soak queued (shared with item -277):
    `s441_freelistnext_confirm.sh`.

-277. **(s441) `FREELIST_NEXT_GUARD` — a THIRD sibling of `GENERIC_CACHE_GUARD` (s434, item
    -270ish)/`CACHE_HEAD_A1_GUARD` (s436), root-causing and fixing the exact crash that consuming
    s440's queued `s440_hangarbayentry_confirm` soak hit, and which turned out to have nothing to
    do with item -263's believed locus.** That soak crashed (SOAK-RESULTS `20260807-064649`, rc=1,
    `last-guest-pc=0x8000CE40`, `si_addr=0x38076a804` — the same near-zero family as items
    -261/-263) — but `updateHangarBayScene`'s own entry counter (item -276's `[hangarbay-entry]`)
    logged **zero calls** before the crash, and the backtrace (`reserveAndEmitDLEntry <-
    submitSceneNodeRender <- ... <- runHangarSelectionFrame`) never goes near
    `updateHangarBayScene` at all — decisive, same-run proof that this specific occurrence was
    misattributed to item -263 by superficial signature match (SIGBUS, near-zero pointer) alone.
    Source-read at `funcs_3.c:0x8000CE30` found the real mechanism: `GENERIC_CACHE_GUARD` already
    validates the free-list HEAD pointer before dereferencing it (substituting 0 if out of range),
    but the VALUE that deref reads back — the list's "next" pointer, guest-memory-controlled — is
    never itself validated before being written back as the new head (safe, self-healing) and then
    dereferenced 4 bytes later (`MEM_W(0X4, ctx->r2) = 0`, the guest `sw $zero, 0x4($v0)` at
    `0x8000CE40`) — an unguarded write through a value that only had its ADDRESS-OF-ORIGIN
    checked, not itself. A scoped scan of all 107 `GENERIC_CACHE_GUARD` sites
    (`scratch/agent/s441_freelist_next_scan.py`-equivalent, done inline) found 105/107 share this
    exact byte-identical shape (varying only in address/label text); the other 2
    (`funcs_4.c` `0x8001083C`/`0x80010E3C`) are already independently covered by the pre-existing
    bespoke `CACHE3_GUARD` (s270)/`CACHE2_GUARD` (s266). Patched all 105 with `FREELIST_NEXT_GUARD`
    (`N64Recomp/fixup_game_funcs.py`) — same skip-the-write-on-bad-pointer semantics as
    `CACHE_HEAD_A1_GUARD` (0 is not a safe substitute for a write address; the write's own value is
    a hardcoded 0 so nothing downstream depends on it happening). Regenerated/rebuilt clean (0 new
    warnings beyond the pre-existing DDIV set); verified via direct grep of compiled output: no
    regression to `GENERIC_CACHE_GUARD` (107), `CACHE_HEAD_A1_GUARD` (7), `BREADCRUMB18`/
    `HANGARBAY_ENTRY`; new guard present at exactly 105 sites (66 `funcs_3.c` + 39 `funcs_4.c`,
    matching the dry-run scan count exactly). Live-verified same schedule: process died at 109.9s,
    but on an entirely DIFFERENT, previously-uncatalogued crash (item -278) — 0 fires across all 3
    free-list guard families this run (no bad pointer encountered, null result on this specific
    mechanism, not yet a positive control). Confirmation soak queued: `s441_freelistnext_confirm.sh`.
    **Downgrades item -263's confidence**: the crash this new guard fixes is proven (same-run,
    mechanism-level) to be the actual cause of at least one occurrence previously filed under item
    -263; see item -263 below for the reclassification.

-276. **(s440) `updateHangarBayScene` entry counter (`ROGUESQ_LOG_HANGARBAY_ENTRY`) — the first
    same-run positive control for item -275/-263's BREADCRUMB18 thread.** Consumed the queued
    `s439_breadcrumb18_confirm` soak first: 2nd consecutive clean run (0 crash, 0 guard fires),
    breaking the previously-strict alternating clean/crash pattern since s434. Its 7503s
    wall-clock (vs. usual ~150-350s) is most likely a macOS sleep event pausing the loop mid-run
    (steady frame/submit-count progression in the log shows the process itself ran normally,
    single-source, not independently confirmed) — noted for awareness, doesn't change the verdict.
    Rather than spend a 3rd identical confirm cycle, added an independent entry counter at the top
    of `updateHangarBayScene` (`N64Recomp/fixup_game_funcs.py`, same signature-search-splice
    approach as BREADCRUMB18) to test whether the function is even reached in these clean runs.
    Regen/build caught a real bug: `funcs_28.c` had never used `fprintf`/`stderr` before, so the
    first build failed (`use of undeclared identifier 'stderr'`); fixed with the same conditional
    `#include <stdio.h>` pattern other file-specific patches use. Verified no regression to
    `GENERIC_CACHE_GUARD` (107)/`CACHE_HEAD_A1_GUARD` (7); BREADCRUMB18 unchanged at 2643 writes.
    Live-verified same schedule: 0 crash, 0 guard fires, 126 frames to 298.0s (3rd clean data
    point) — but this time with the missing control: 34 throttled log lines show
    `updateHangarBayScene` was called **~2900+ times** in the single run. This is the first
    confirmation the target function is a hot, constantly-executing path during exactly the
    schedule that keeps not reproducing item -263, meaningfully de-risking (not eliminating) the
    "does the fault even pass through breadcrumbed code" doubt raised at item -275. Found and
    documented an instrument caveat: the counter's `ra=`/`ctx->r31` field reads 0x00000000 always
    — the call site (`funcs_28.c:5397`) is a direct C call, not a `jalr`, so the recompiler never
    populates `ctx->r31` there; the field is uninformative noise for this specific call shape, not
    a real return address. Confirmation soak queued: `s440_hangarbayentry_confirm.sh` — a 3rd
    consecutive clean result there would hit iron rule 8's 3-strike budget on hypothesis-id
    `item-263-updatehangarbayscene-localization`, forcing a pivot (top candidate: an ASAN-style
    shadow/canary check around the suspected corruption, since the mechanism now demonstrably
    passes through heavily-executed breadcrumbed code without faulting).

-275. **(s439) BREADCRUMB18 added to `updateHangarBayScene` (funcs_28.c:10918-17722, ~6805 lines,
    2643 breadcrumb writes) — item -263's work unit from item -274.** Regenerated/rebuilt clean (0
    new warnings beyond the pre-existing `DDIV` sign-conversion set); verified no regression via
    direct grep of the compiled `.c` output (fixup's stdout is silent/idempotent on a 2nd run, s437's
    documented gotcha) — `GENERIC_CACHE_GUARD` still 107 sites, `CACHE_HEAD_A1_GUARD` still 7.
    Live-verified with the full s427-438 schedule (all diagnostics armed): **0 `[CRASH]` markers, 0
    `generic-cache-guard`/`cache-head-a1-guard` fires, 126 frames captured to 298.5s** — the full
    300s schedule completed clean. Per iron rule 1 this is a null result without a positive control:
    it does NOT confirm BREADCRUMB18 is correctly placed (it never got exercised at a fault), and
    does not advance items -270/-272's still-missing guard-fire positive control either. Consistent
    with the established alternating clean/crash pattern (s434 clean, s435 crash, s436 clean, s437
    crash, s438(soak) crash, s439 clean) — one clean run is not evidence either way. Confirmation
    soak queued: `s439_breadcrumb18_confirm.sh`. If item -263 recurs, BREADCRUMB18 should report a
    real guest PC inside `updateHangarBayScene`'s own body for the first time; classify it against
    known idiom families (0x801163B0-family, `-0x25A4` hangar-list, IEEE-754-as-pointer) before
    writing any guard blind.

-274. **(s438) Item -263 recurred a 4th time via the queued `s437_breadcrumb17_confirm` soak
    (SOAK-RESULTS 20260807-035804, rc=1, 153s) — BREADCRUMB17 worked, but the new `last-guest-pc`
    immediately hit the SAME misattribution mechanism one function deeper.** `last-guest-pc=0x800AAF94`
    resolves (`tools/overlay_symbol_probe.py` + a sorted `menu_overlay.txt` symbol table) to +504 bytes
    into `runHangarSelectionFrame` — confirmed by source: `funcs_28.c:5391-5396` is the breadcrumb write
    immediately before the `jal` into `updateHangarBayScene`. A full grep of `updateHangarBayScene`'s
    entire body (`funcs_28.c:10918-17722`, ~6805 lines — the largest function this project has ever
    instrumented) found **zero** breadcrumb writes anywhere in it, so `last-guest-pc` froze at the call
    site the instant execution entered this uninstrumented callee — the identical mechanism BREADCRUMB16
    (item -271) and BREADCRUMB17 itself (item -273) were built to defeat, recurring one function deeper
    because `updateHangarBayScene` was never on the allowlist either. Two independent signals now agree
    on `updateHangarBayScene` as the locus even without an exact instruction: this call-site freeze, and
    the host-side `atos` symbolication (`pc-symbol=updateHangarBayScene+43768`), which has named this
    same function at all 4 of item -263's occurrences (s426, s433, s436, s437) without anyone previously
    connecting it to the breadcrumb-coverage gap. No build/run cycle this session (analysis of already-
    collected soak data only, per read-list #3). Next work unit: BREADCRUMB18 (or a checkpoint bisection,
    given the function's unprecedented size) inside `updateHangarBayScene` itself. Full detail:
    `docs/PROJECT-OVERVIEW.md` §16 (s438 update), `PORTING-STATE` Session 438.

-263. **(s426, recurred s433/s436/s437/s440; s441 RECLASSIFIED — PARKED, likely dissolved into
    item -277's family, not independently confirmed to exist as a distinct bug.** Originally framed
    as a fault localized INSIDE `updateHangarBayScene`'s own body (item -274, s438: two independent
    signals — a call-site breadcrumb freeze and `atos` symbolication naming that function at all 4
    early occurrences — agreed on it as the locus). item -276 (s440) instrumented the function with
    an entry counter to get a same-run positive control, then consuming that soak's own queued
    confirm (`s440_hangarbayentry_confirm`) produced the first occurrence with FULL breadcrumb
    coverage active — and it decisively did NOT localize inside `updateHangarBayScene`: the entry
    counter logged **zero calls** before the crash, and the backtrace never goes near that function
    (`reserveAndEmitDLEntry <- submitSceneNodeRender <- ... <- runHangarSelectionFrame`, a sibling
    rendering path). s441 root-caused that occurrence's actual mechanism at the instruction level —
    an unguarded free-list "next"-pointer write in `reserveAndEmitDLEntry` (item -277,
    `FREELIST_NEXT_GUARD`) — and fixed it. **What this means for the other 4 pre-s440 occurrences**:
    none of them ever showed a fault instruction inside `updateHangarBayScene`'s body either (all 5
    total occurrences, s426 through s440, matched by the same superficial signature: SIGBUS, wild
    near-zero `0x38000000x`-family pointer) — the s426-s438 "localization" chain was a sequence of
    breadcrumb-coverage-gap freezes (BREADCRUMB16 then 17 then the call site into
    `updateHangarBayScene`) that never actually reached an instruction inside the target function,
    right up until s440 finally got there with full coverage and found the fault was elsewhere
    entirely. The simplest explanation now is that item -263 was never a distinct bug: it is the
    same recurring `0x801163B0` free-list family (items -270/-272/-277) recurring at different call
    sites that all happen to route near `runHangarSelectionFrame`/`updateHangarBayScene` in the call
    graph, most of which so far have crashed before or at a breadcrumb-coverage gap rather than
    inside the instrumented function. **Do not spend further sessions chasing a fault inside
    `updateHangarBayScene`'s body** without a NEW occurrence that BREADCRUMB18 (2643 breadcrumb
    writes, full coverage, unregressed as of s441) actually reports a real address inside that
    function — that is now the single falsifying observation that would resurrect this item as
    independent. Full detail: PROJECT-OVERVIEW §16, PORTING-STATE Sessions 426, 433, 436, 438, 441.

-268..-273. **(s432-437) Duplicate-symbol catalogue closed (18/18); the `0x801163B0` free-list-
    cache-head-deref idiom swept at scale (107 sites, `GENERIC_CACHE_GUARD`) plus a 7-site `$a1`-register
    sibling bug found and fixed (`CACHE_HEAD_A1_GUARD`); item -263 progressively localized through two
    rounds of breadcrumb-coverage misattribution (BREADCRUMB16, BREADCRUMB17).** Batch-fixing the last of
    18 catalogued duplicate-symbol pairs (s432/s433) unblocked the item -265/-266/-267 chain as a side
    effect — likely because the truncated stub `runHangarMenuFromOverlay` had been calling left the next
    callee, `mallocCraftSelectionData`, consuming never-computed garbage state rather than containing its
    own bug (single-run, not independently confirmed). The live-verify that followed hit item -263's
    original s426 signature again (2nd source), promoting it to the active frontier. s434's scan for
    that crash's idiom (reload+deref of global `0x801163B0`, already bespoke-guarded 4 times before by
    s197/s266/s270/s271, each reactively) found 107 more unguarded sites; one generic guard fixed them
    all, live-verified over the deepest clean run in the saga but with 0 guard fires (no positive control
    yet). Its confirmation soak crashed on a different bug, root-caused (s435) as a breadcrumb-coverage
    misattribution — `last-guest-pc` froze at a caller's call site because the real callee,
    `emitMaterialTexturedDL`, had zero breadcrumb writes across ~1258 lines (fixed: BREADCRUMB16,
    byte-for-byte the same mechanism BREADCRUMB15's own s349 note already documented once). The NEXT
    confirmation soak (s436) found a real, distinct bug: `reserveAndEmitDLEntry` reloads the same global
    into two registers 4 instructions apart, one guarded (`$v0`) and one not (`$a1`, used as a raw
    unvalidated write pointer); a scoped scan found 6 more of the same shape, all 7 fixed
    (`CACHE_HEAD_A1_GUARD`). That soak then hit item -263 a 3rd time, still showing the ORIGINAL
    misattribution (`0x800547BC` = `tickWrappingTimerAccumulatorList`'s own epilogue instruction, not a
    memory access) — so s437 added BREADCRUMB17 to `runHangarSelectionFrame`, the only reachable one of
    that function's 3 callers, to catch the real fault site. Items -270 (`GENERIC_CACHE_GUARD`) and -272
    (`CACHE_HEAD_A1_GUARD`) both still lack a same-run positive control (0 fires across all observations
    so far) despite 100% clean runs whenever reached — promising but unconfirmed. See item -274 for
    where BREADCRUMB17 led. Full detail: `docs/PROJECT-OVERVIEW.md` §16, `PORTING-STATE` Sessions
    432-437.

-261..-267. **(s424-431) The `startPlayerSlotAnimationChannelLooping`-family crash chain: 3 siblings
    guarded (item -261), then SUPERSEDED by the real root cause — a duplicate-symbol-name collision
    truncating `initCraftSelectScreen`'s ~1200-line body to 1 instruction (item -262) — whose fix
    un-truncated code that had never run before and triggered a cascade of 3 further crashes, one per
    newly-live function.** s424/s425 guarded 2 of 3 siblings deref-ing a global (`0x800CDFAC`) whose only
    writer had never run; s426 found why (the duplicate-symbol mechanism, generalized into item -264's
    catalogue of 20 total instances) and fixed it with zero call-site edits (N64Recomp derives a JAL
    target's C name from whichever symbol survives at that address). s427 fixed the 2nd instance
    (`hangarInitialize`/`mallocCraftSelectionData`), which surfaced a NEW signature at
    `runHangarMenuFromOverlay+800` (item -265): register corruption of `ctx->r19`/`$s3` (callee-saved,
    sane at entry, wild after some callee), guarded s428 with its own positive control (the guard firing).
    That guard exposed a further crash one step later reading the same corrupted register back
    (`menuOverlayInit+3648`, item -266, reproduced 3x). s429/s431 isolated the corruption to
    `mallocCraftSelectionData` via before/after checkpoints (2nd-independent confirmation, SOAK-RESULTS
    20260807-013423), ruled out 30 of its 47 callees by static read, and reframed it (item -267) as a
    stray write corrupting a stack slot rather than a missing register restore. **s433 update: item -267
    did NOT recur** after item -269's catalogue-closing fix (a sibling duplicate-symbol stub in the same
    caller) — plausibly because that stub's never-computed garbage state, not `mallocCraftSelectionData`
    itself, was the real corruption source; single-run, not independently confirmed. Full detail:
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
