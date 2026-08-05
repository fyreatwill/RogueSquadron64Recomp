# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings, `s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. History: s295-330
   ran 5 passes, most recently 668→459 lines (s330); full per-session detail in git log. 35 KB remains
   a stretch target, not a hard floor -- the "Current truth" env-var/timeline prose and the
   Regeneration section's Standing warnings stay intact deliberately; both are used every iteration.
2. **M5 audio de-stubbing**: design doc + steps 1-3 DONE (s298/300/301, item -196 corrected below).
   Step 4's `setDisplayMode` VI=320 hang is CLOSED and fix-validated (item -182..-187). `reapplyDisplayMode`'s
   site (3rd/last real gate; `initMusyXEngine`'s is dead code, s306) previously **deterministically
   prevented the game from ever reaching the title screen — 0/5 soaks across s329/s340/s341** (item -198,
   s342). **s343 reverted `reapplyDisplayMode`'s gate back to force-zero (kept `setDisplayMode`'s
   reversal); title-reach is now confirmed 3/3 across independent soaks** (s343revert/confirm1/confirm2,
   all ~45.5s, matches the 44.6-46.2s baseline). The `tickWrappingTimerAccumulatorList` div-by-zero
   crash s343 found (a DIFFERENT signature from `BREADCRUMB9`'s previously-catalogued `0x80000004`
   near-null-pointer crash) did **not** reproduce in either of 2 confirmation soaks — one ran fully
   clean through the whole hold window, the other hit an unrelated, already-catalogued
   `emitAllocatedDLCommand`/`submitSceneNodeRender` SIGBUS instead (item -200, s344): **1/3 total,
   PARKED not guarded** (insufficient evidence per Iron Rule 4). s344 reopened M5-AUDIO-PLAN step 5
   (crash-family #3/#4 rate comparison) with 4 fresh, methodology-corrected soak recipes
   (`scratch/agent/soak_queue/m5step5v2_rate_1..4.sh`) now that title-reach is robust. Next work unit
   (s344, `scratch/agent/NEXT.md`): fold in those verdicts as they land; watch for `last-guest-pc=
   0x80054744` recurring (would reopen the div-by-zero guard question) and separately tally
   crash-family #3/#4 rates against the historical ~12-21%/"every soak died earlier" baselines.
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
move; what a leave-key actually leads to is unresolved. *Done when:* 60 seconds of in-mission
rendering, craft visibly responds to synthetic input, stability counters 0, and the phase timeline
in this document covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it; the 3 `[missing-func]` addresses in the undriven outdoor-512 stretch — root-caused and
fixed s53/54 (3 mission-overlay symbols misassigned to `main_overlay.txt`; see Next-steps item -6),
**runtime confirmation still outstanding**.

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.


## Next steps, in order of expected value (s295)

Numbering convention (fixed s295, was previously three colliding sequences): items are
numbered highest-magnitude-negative (top, newest/highest priority) counting up to -1 (bottom,
oldest). Current top is -201 (s345); the next new item takes -202 and is inserted at the top.

-201. **(s345) The `m5step5v2_rate_1/2` soaks' `rc=137` was a recipe artifact — a known,
    already-catalogued self-inflicted logging blowup (PORTING-STATE Session 209/210), not evidence of
    crash-family #3/#4.** Both queued step-5 recipes hit the loop's 600s hard-cap despite their own
    launcher logs showing the driven scenario (title reach, full `[keys]`/stick schedule through the
    240s hold) completed cleanly at ~301s wall (`done wall=301s`, `game process still alive; killing` —
    a normal launcher-initiated shutdown, not a game-side hang). The recipe's own post-launcher `grep`
    passes over `run.log` never finished before the watchdog fired: `run.log` had ballooned to 8.2-8.7 GB
    (vs. the 76-233 MB every other recipe in this family produces for a similar-duration run), with
    `[rs-free-walk]` lines alone accounting for ~45% of a 200 MB sample of it — matching, almost
    exactly, the 44-82% `[rs-free-walk]` share and ~40-55x volume blowup Session 209/210 already
    root-caused and fixed for an unrelated bug hunt: `ROGUESQ_LOG_RS_FREE_WALK`/
    `ROGUESQ_LOG_RS_MALLOC_WALK` log once PER LIST NODE walked (not once per call, unlike every other
    `ROGUESQ_LOG_*` var in `run_s327waitpump.sh`), so on any run where the walker gets invoked enough
    (e.g. once per tick through a long hold window against a free list that only grows) the resulting
    fprintf volume itself burns enough real wall-clock to starve — and, worse, to outlast the loop's
    watchdog budget for — the actual soak. Session 209/210 saw the SAME family (233 MB → 210 MB **lines**,
    a ~47x jump) with byte-identical instrumentation between runs, so this is state/timing-dependent, not
    purely a fixed instrumentation cost — `confirm1`/`confirm2` (s343/s344, same script family, same
    `HOLD_S`) stayed in the normal 76-233 MB band while `m5step5v2_rate_1/2` didn't, despite no code or
    config change between them. Root mechanism (why THIS run's free-list walk ran away) is still open;
    what's closed is that the resulting `rc=137` is not itself game-side signal.
    **Fix landed**: `run_s327waitpump.sh`'s 4 heap-walker log vars (`ROGUESQ_LOG_RS_MALLOC_WALK`,
    `_GUARD`, `ROGUESQ_LOG_RS_FREE_WALK`, `_GUARD`) now use the `${VAR:-1}` pattern (matches the
    pre-existing idiom already used for `ROGUESQ_LOG_THREAD_RESUME`) — default behavior unchanged (still
    armed unless a recipe pre-exports 0), so every existing/queued recipe in this family is unaffected,
    but a new recipe chasing a non-heap-walker signal can opt out without forking the whole 148-line
    shared driver. `m5step5v2_rate_3/4` (queued, not yet run) were cancelled rather than run unmodified —
    they would have reproduced the same artifact and wasted 2 more 600s slots for zero information
    (`scratch/agent/soak_queue/cancelled/README.md` has the full note). Queued the corrected 3rd-generation
    recipes (`m5step5v3_rate_1/2.sh`) with the 4 vars opted to 0 and a `runlog_bytes`/`rs_free_walk_lines`
    field in the verdict so any future recurrence is visible without re-deriving it from file sizes by
    hand. **Deleted** the two 8+ GB `run.log`s after extracting the discriminating samples above (disk
    was at 84% used; not archived — regenerable by rerunning the cancelled recipes if ever needed, though
    they wouldn't reproduce a NEW `rc=137` under the fixed driver's `_v3` default anyway). `HYPOTHESIS-ID
    m5-audio-destub-step5-crashrate-comparison` still open, still 0 real data points toward the actual
    crash-family #3/#4 rate question — this session was pure recipe-methodology repair, 2nd iteration on
    this ID since reopen. Full detail: `PORTING-STATE` Session 345.

-200. **(s344) M5 audio de-stubbing: neither queued confirmation soak reproduces the
    `tickWrappingTimerAccumulatorList` div-by-zero from item -199 — parked, not guarded; found and fixed
    a soak-recipe methodology bug; reopened M5-AUDIO-PLAN step 5 with 4 fresh recipes.** Read the 2
    queued verdicts (`s343_tickwrap_divzero_confirm1` rc=0, `confirm2` rc=1) and, per Iron Rule 4, the
    full raw logs before trusting the recipes' own naive "any `[CRASH]` = confirmed" reading.
    **confirm2's crash is NOT the target bug**: `last-guest-pc=0x80008928` traces (Mach-O symtab walk +
    `funcs_3.c` grep, independently confirmed) to `emitAllocatedDLCommand`, not
    `tickWrappingTimerAccumulatorList` — full record shows `signal 10 (Bus error)`,
    `si_addr=0x348187680` (RDRAM host-base + a corrupted offset), backtrace through
    `submitSceneNodeRender`/`processSceneNode`/`setupCameraMatrices` — the SAME already-catalogued
    pre-existing SIGBUS family Session 301's control soak hit, unrelated to the `break 7` div-by-zero
    trap (`0x80054744`) this soak was meant to confirm. **confirm1 is genuinely clean**: `CRASH: 0` for
    the full 307s wall including the entire scheduled stick-input hold window — and, contrary to its own
    self-reported `keys_lines=0`, both confirmations actually drove the full key/stick schedule and
    reached title at 45.5s; the `keys_lines=0` reading was a recipe bug (`[keys]` lines are emitted by
    the launcher driver into its own `*_launcher.log`, never into the game's `run.log`, which is what
    the recipe grepped). **Net: title-reach now confirmed 3/3** across independent soaks (strengthening
    item -199); **the div-by-zero crash itself is 1/3 total, not 2/2 or even a clean 0/2** — does not
    meet the bar to land a guard, and does not cleanly read as "just a rare flake" either since one of
    the two confirmation attempts never actually passed through the crash's time window uneventfully (it
    died to something else first). `HYPOTHESIS-ID m5-audio-destub-tickwrap-divzero-craftselect` PARKED
    (recurs if a future soak reproduces `last-guest-pc=0x80054744` specifically). Reopened
    M5-AUDIO-PLAN step 5 (crash-family #3/#4 rate comparison) with 4 methodology-corrected recipes
    (`scratch/agent/soak_queue/m5step5v2_rate_1..4.sh`, `HOLD_S=240`, current gate config unchanged —
    no rebuild needed): fixes the `[keys]`-log-file bug and prints `last-guest-pc`/`pc-symbol` on every
    crash so future readers can tell which family fired without re-opening a 200+ MB log.
    **Method-trap, generalizes beyond this recipe**: a soak verdict of "did any `[CRASH]` marker fire"
    is only informative once compared against the target signature's own `last-guest-pc`/`pc-symbol` —
    RS64 has ~20+ independent, already-catalogued, nondeterministically-firing crash families, so a bare
    presence check will false-positive-confirm an unrelated bug at a nontrivial rate. Full detail:
    `PORTING-STATE` Session 344.

-199. **(s343) M5 audio de-stubbing: reverted `reapplyDisplayMode`'s gate to force-zero, title-reach
    restored (HA confirmed) — but a NEW crash surfaced one stage later, in the SELECT YOUR CRAFT
    stabilization window, never reachable before.** Regen'd with the fixup regex narrowed to
    `0x8008EC88`-only (force-zeroing `reapplyDisplayMode`; `0x8008EB40`/`setDisplayMode` stays
    unmatched/reversed) — confirmed via `funcs_23.c` grep, both addresses show the expected patch
    state. One inline soak (`s343revert`, `HOLD_S=240`): `phase width=1024 reached after 45.5s`
    (matches the 44.6-46.2s historical baseline), 4 `[keys]` schedule presses fired (title/menu
    genuinely reached, unlike every s329/s340/s341 soak). Then, during the 12s post-title
    "wait for SELECT YOUR CRAFT stable" window, the process died: signal 6 (abort), 36 `[CRASH]`
    lines, `last-guest-pc=0x80054744` — inside `tickWrappingTimerAccumulatorList`
    (`funcs_11.c:15057`), a.k.a. `BREADCRUMB9` (PORTING-STATE s272-291, `coalesceFreeHeapBlocks`-
    adjacent crash-family work). The PC is a compiler-inserted MIPS `break 7` div-by-zero trap
    (`divu $zero, $v1, $v0` at `0x80054738`/`0x8005473C`, then `break 7` at `0x80054744` when
    `$v0==0`; `do_break(2147829572)` — the argument is just the PC itself, not a semantic code) —
    **a DIFFERENT signature from `BREADCRUMB9`'s previously-catalogued `0x80000004` near-null-
    pointer crash** (PORTING-STATE ~26156); si_addr for this crash is `__pthread_kill`'s own address
    (abort, not SIGSEGV), confirming it's the div-trap path, not the null-pointer one. Some entry in
    the wrapping-timer list at `MEM[0x80137C84]` has a zero threshold halfword (`lh $v0, 0x0($s0)` at
    `0x80054734`). **This is byte-identical gate config to s328's `step4gate2` baseline (0/2 crashes
    across 2 soaks)** — confirmed via direct `funcs_23.c` diff this session — so either (a) this is a
    nondeterministic timing race in menu-overlay setup order that s328's 2 soaks didn't hit, or (b) ~15
    intervening sessions' unrelated code changes since s328 introduced or exposed it. Single-source (1
    crash observation); 2 confirmation soaks of the identical current build queued
    (`scratch/agent/soak_queue/s343_tickwrap_divzero_confirm{1,2}.sh`) rather than spending this
    session babysitting repeats. `HYPOTHESIS-ID m5-audio-destub-reapplydisplaymode-title-block`
    CLOSED (HA confirmed — title-reach fully restored by the single-site revert); new thread
    `m5-audio-destub-tickwrap-divzero-craftselect`. `lib/` not touched (fixup edit is in the
    standalone untracked `N64Recomp` checkout, `export.sh` not needed). Full detail:
    `PORTING-STATE` Session 343.

-198. **(s342) M5 audio de-stubbing: `reapplyDisplayMode`'s gate reversal deterministically blocks
    the game from EVER reaching the title screen (0/5 relevant soaks) — supersedes item -197's step-5
    rate-comparison plan and weakens item -196's promotion validation.** Picked up item -197's "fold
    the soak batch's verdicts into the ledger" work unit; the raw logs of the 2 completed recipes
    (`m5step5_rate_1/2`, both `rc=137`) showed only 3 `[phase] vi_width=` lines each (0->320->640 by
    2.3s) and ZERO `[keys]` presses across the full ~599s run — the game never leaves the pre-title
    attribution/logo screen, let alone reaches a menu or launches a mission. Cross-checked s340's own
    raw logs (`s340bothgates`/`s340bothgates2`, still on disk): identical signature, 0 keys, ~601s
    lifetime — **s340's promotion-decision soaks never left the pre-title screen either**, despite the
    PORTING-STATE write-up describing "ran the full 600s hold... with `STICK_SCHEDULE`" (mechanically
    impossible: `run_mission_keys.sh`'s wait-for-VI=1024 gate self-times-out and kills the game before
    the `SCHEDULE`/`HOLD_S` logic is ever reached). Isolated the regression to `reapplyDisplayMode`
    specifically: baseline (both gates force-zero) and `setDisplayMode` reversed ALONE (s328's
    `step4gate2` log) both reach title normally (45.4s, then menu keys fire on schedule); every soak
    with `reapplyDisplayMode`'s gate reversed — alone (s329) or combined with `setDisplayMode` (s340x2,
    s341x2) — has NEVER reached title, 0/5 across 3 sessions spanning weeks. The underlying
    `[vi-fs-decision] pairs=0` mechanism itself is unchanged from item -195's source-level explanation
    (`cinematicLoopBody`'s self-loop calling `runVideoFrameTick`'s chain once) — what's new is that its
    ONSET is pre-title (immediately post-logo, ~2.3s), not mid-mission-cutscene as the "locked-camera
    cutscene" framing implied, so it blocks title-screen advancement entirely rather than merely
    freezing one already-reached cutscene frame. Cancelled the remaining 4 queued
    `m5step5_rate_3..6.sh` recipes (moved to `scratch/agent/soak_queue/cancelled/`) rather than burn 4
    more 600s loop cycles reproducing a now-deterministic result. **Recommendation**: revert
    `reapplyDisplayMode`'s gate to force-zero (keep `setDisplayMode`'s reversal, validated through
    title/menu/mission-launch), re-validate title-reach is restored — this is risk reduction, not a
    re-open of the "is the plateau benign" question, since no further M5 progress is measurable while
    title is unreachable. `HYPOTHESIS-ID m5-audio-destub-step5-crashrate-comparison` CLOSED (superseded);
    new thread `m5-audio-destub-reapplydisplaymode-title-block`. No `lib/` touched, no soak run (log
    analysis only). Full detail: `PORTING-STATE` Session 342.

-197. **(s341) M5 audio de-stubbing step 5: queued a 6-run soak batch to measure crash-family
    #3/#4 rates under the now-permanent gate promotion, rather than spending the session babysitting
    repeat soaks.** Confirmed the s340 gate promotion is baked into the current build (both
    `MEM_B(...) = ADD32(0, 0X1)` writes present at `0x8008EB40`/`0x8008EC88` in
    `N64Recomp/RecompiledFuncs/funcs_23.c`, and `build/RogueSquadron64Recomp`'s mtime matches the
    regen, so no rebuild was needed). Step 5 needs a *rate* comparison (not pass/fail) against the
    historical baselines (`docs/M5-AUDIO-PLAN.md` §3: family #3 `waitForAnyAudioSlot` pre-title
    SIGSEGV ~12-21% of pre-scene soak deaths; family #4 post-cutscene stall, historically "every soak
    died earlier" before reaching it) -- both baselines predate any gate reversal, confirmed by
    re-reading §3's table before treating any rate change as s340-caused. Wrote 6 self-contained
    recipes (`scratch/agent/soak_queue/m5step5_rate_1..6.sh`) that each invoke the existing
    `run_s327waitpump.sh` driver (already arms `ROGUESQ_AUDIO_UCODE=1` plus every
    `_VOICE_ACTIVE_GATE`/`_VOICE_TRIGGER_CHAIN`/`_AUDIO_DRAIN` instrument step 5 calls for as a
    same-run positive control) with `HOLD_S=300` -- sized from s340's observed ~780s total wall at
    `HOLD_S=600` (~180s fixed overhead + HOLD_S) to fit under the loop's 600s per-recipe hard cap with
    margin. Each recipe greps its own `run.log` for `[CRASH]` (the process's own SIGSEGV/SIGBUS
    handler output, confirmed to land in the redirected log) and exits 1 if any fired, 0 otherwise --
    catches family #3 (a crash) directly; family #4 (a stall, not a crash marker) needs the full log's
    tail `vi_width`/`[vi-fs-decision]` lines read by hand, rc alone can't distinguish it, so the next
    iteration must open the full logs in `scratch/agent/soak_results/`, not just the one-line verdicts
    in `SOAK-RESULTS.md`. No soak run yet this session (queued only); no `lib/` touched. Full detail:
    `PORTING-STATE` Session 341.

-196. **(s340) M5 audio de-stubbing: promoted BOTH `setDisplayMode`'s and `reapplyDisplayMode`'s
    gate-byte reversals to the PERMANENT shipped default, closing M5-AUDIO-PLAN step 4.** Discriminating
    soak item -195 recommended: reverse both real gate sites (`initMusyXEngine`'s is dead code, s306 --
    only 2 of the 3 nominal sites are reachable) SIMULTANEOUSLY, something no prior session in the whole
    s297-339 arc had tried (every soak reversed at most 1 of 2, always re-reverting to the force-zero
    baseline at session end because the promotion decision was explicitly left open). Ran 2 soaks
    (`s340bothgates`, `s340bothgates2`, `HOLD_S=600` each, full diagnostic set armed including
    `ROGUESQ_LOG_MAINGAMELOOP_REACH`/`_CUTSCENETIMER_REACH`/`_REAPPLYDISPLAYMODE_REACH`): both clean,
    meeting M5-AUDIO-PLAN's "two clean soaks" bar (the same bar s328 used for `setDisplayMode` alone).
    Both runs: VI transitions 0->320->640 within ~2.2s (no VI=320 hang -- the s327 `musyxSynthFrame`
    pump fix holds under combined reversal), zero crash markers for the full 600s, then the
    already-characterized benign VI=640 `pairs=0` plateau (item -195: `cinematicLoopBody` genuinely
    alive -- `[static6-800a9abc-entry]`=1 both runs, DMA ring reaching n=4999/5008, audio synth counter
    956-957). H1 (both gates safe together) CONFIRMED; H2 (a new interaction only visible combined)
    REFUTED -- no failure signature distinct from either site's already-known behavior. Edited
    `fixup_game_funcs.py`'s gate regex (N64Recomp repo, untracked) to PERMANENTLY match neither address
    -- this is now the shipped default, not a per-session toggle; `docs/M5-AUDIO-PLAN.md`'s "Next work
    unit" section updated to mark step 4 DONE and point at step 5 (crash-family #3/#4 rate comparison
    vs. historical baselines, needs multiple soaks not a single pass/fail). No `lib/` touched. Full
    detail: `PORTING-STATE` Session 340.

-195. **(s339) M5 audio de-stubbing: source-proves `submitGfxFrame` structurally cannot produce a
    `FramebufferPair`, and that `cinematicLoopBody`'s self-loop calls the real `SET_COLOR_IMAGE`
    producer (`runVideoFrameTick`, via `static_6_800A9ABC`) exactly ONCE -- not per-iteration -- fully
    resolving the s329-s338 VI=640 `pairs=0` chase in 1 iteration, no new soak.** Closed
    `HYPOTHESIS-ID m5-audio-destub-submitgfxframe-vi-fs-decoupling` on its 1st iteration by source-read
    (`submitGfxFrame`'s full callee set has no `setupCameraMatrices`/`emitFrameRdpInitDl`/
    `runVideoFrameTick`/`advanceVideoFrame` -- only buffer-arbiter/SP-task-producer bookkeeping) plus
    reuse of s337's already-captured log (`[static6-800a9abc-entry]`, armed via
    `ROGUESQ_LOG_MAINGAMELOOP_REACH=1`) for a 2nd, runtime-confirmed line of evidence: exactly 1 call
    for the whole ~600s soak, matching s333's raw "`runVideoFrameTick` stops after exactly 2 calls"
    (1 from `mainGameLoop`'s single pass + 1 here = 2, an exact Fermi-check match). Conclusion: nothing
    is actually stalled -- `cinematicLoopBody`'s self-loop runs correctly the whole time (audio,
    buffer-arbiter, cutscene dispatch all alive); it just never re-emits `SET_COLOR_IMAGE` after its
    one-time pre-loop camera/RDP-state setup, so `[vi-fs-decision]`'s `pairs` counter faithfully reads
    0 for the rest of the scene. Very likely not a bug (a locked-camera cutscene reusing one RDP-state
    prologue is ordinary), and confirms s336's suspicion this thread was never an audio issue. Reframes
    the M5 decision: promoting BOTH `setDisplayMode`'s and `reapplyDisplayMode`'s gate-byte reversals
    to the shipped default is no longer blocked by an unexplained stall -- that promotion decision is
    the recommended next M5 work unit. No `lib/` touched, no soak run. Full detail: `PORTING-STATE`
    Session 339.

-188..-194. **(s330, 332-337) M5 audio de-stubbing: the VI=640 `reapplyDisplayMode` stall chase from
    the `waitForMusyXAudioTaskDone` spin-loop hypothesis through 5 reachability probes to a fully
    source-proven internal cutscene loop and exit-gate, closed by item -195's mechanism.**
    `HYPOTHESIS-ID` progression: `...waitformusyx-secondspin-hang` (closed s332, refuted) →
    `...reapplydisplaymode-reachability` (closed s333) → `...mainGameLoop-upstream-stall` (closed
    s334→s335 in 3 iterations) → `...cinematicloopbody-divergent-callees` (closed s336→s337, 3
    iterations, iron rule 8 budget) → resolved by item -195's
    `m5-audio-destub-submitgfxframe-vi-fs-decoupling`. s330 source-read found a second, unpatched spin loop inside `waitForMusyXAudioTaskDone`
    (`funcs_24.c:5540-5550`, unbounded, missed by s327's pump-fix) as a candidate mechanism. s332
    runtime-REFUTED it: the diagnostic fired once with `flag=0`, fell through immediately, while the
    stall persisted the full 600s with audio (arm/clear cycling, DMA ring reaching n=4979) staying
    fully alive. s333 found the stall a call-frame further upstream: `runVideoFrameTick` itself stops
    being invoked after exactly 2 calls for the ~598s remainder (grepped all 5 of its call sites:
    2 in `mainGameLoop`, 1 each in `menuOverlayInit`, `cutsceneDispatchSlotsByFlag`,
    `static_6_800A9ABC`). s334 found `mainGameLoop` parks after exactly ONE loop-top pass (refuting it
    as the stalled caller), while `cutsceneDispatchSlotsByFlag` cycles continuously (1152+ calls) for
    virtually the whole stall window. s335 source-proved that apparent `runVideoFrameTick` call site
    inside `cutsceneDispatchSlotsByFlag` (`funcs_27.c:118121`) is UNREACHABLE DEAD CODE -- an
    `N64Recomp` function-splitting artifact duplicating `static_6_800A9ABC`'s body past an
    unconditional `return`, with no incoming label; the climbing call count was a red herring, never a
    real caller. s336 source-proved `cinematicLoopBody` contains its own internal per-frame `goto`-loop
    (`funcs_27.c:108258`, unconditional `j`) that explains the divergence without a new caller -- it
    calls `cutsceneDispatchSlotsByFlag` and `submitGfxFrame` directly every pass and self-loops,
    exiting only via `static_6_800AF550`, a per-actor timer/threshold gate with NO audio-subsystem
    reference anywhere in its 3-level-deep traced input chain (`timeSnapshotFiller`) -- first evidence
    this stall thread may not be an M5/audio issue at all. `rs64_dmem_lock` (s330) is confirmed a
    recursive mutex and `gfx_thread`/`task_thread`/`vi_thread` are genuinely independent OS threads
    (`lib/N64ModernRuntime/librecomp/src/main.cpp:185-190`, `ultramodern/src/events.cpp:590-634`),
    explaining why audio diagnostics kept firing throughout every stall in this arc even with the game
    thread wedged. s337 instrumented `cinematicLoopBody`'s exit gate (`static_6_800AF550`) directly:
    its delta-time input never froze, but its gating pointer stayed NULL for ~89% of the run and even
    the one real exit-signal firing did not clear `[vi-fs-decision]`'s `pairs=0` reading — closing that
    question but leaving the pairing mechanism itself unexplained. Gate reverted to the full force-zero
    baseline and rebuilt clean after every session (`audio gate patched x2` reconfirmed each time); no
    `lib/` touched in any of the 7 sessions. Full detail: `PORTING-STATE` Sessions 330, 332-337.

-182..-187. **(s323-329) M5 audio de-stubbing step 4: gate-byte reversal + spin-loop chase — the arc
    from the 37-vs-40 measurement question through the fix, its confirmation, and the 3rd gate site's
    new failure mode; each step's conclusion superseded or closed by the next, ending at s330 (item
    -188).** `HYPOTHESIS-ID` progression: `...tick37-vs-hardstop40` (closed s325) →
    `...setdisplaymode-vi320-hang` (closed s327, confirmed s328) → `...step4-reapplydisplaymode-
    reversal` (closed s329, discovery only) → `...waitformusyx-secondspin-hang` (current, item -188).
    s323 refuted the "internal early-return"/"unlocated call site" framing via a NEW
    positive-controlled runtime call-site-logging instrument (0/0 for both real tick-producer targets
    vs. 40/40 for a same-run positive control), reframing gate1/2/3's "taken" measurement as a proven
    arithmetic inconsistency rather than a missing call site. s325 closed it: gate1/2/3's diagnostic
    print caps were silently truncating past `n=40` (a 4th instance of the sampling-cap-illusion bug
    already seen 3x in this investigation) — widening the cap found gate1+gate2+gate3=37, an exact
    match to the tick-producers' own independent entry count. s326 pivoted to the still-open
    `setDisplayMode` VI=320 hang and fully traced it by pure source-read: `runVideoFrameTick` calls
    `musyxNoopStub` every frame, which spins forever on a countdown (`waitForMusyXAudioTaskDone`) only
    an unreached `musyxSynthFrame` call can decrement — no soak needed, exactly `M5-AUDIO-PLAN`'s own
    predicted highest-risk regression. s327 landed and validated the fix: patched the spin loop to
    pump `musyxSynthFrame` directly (bounded, falls through regardless); 1/1 soak cleared VI=320 into
    the full menu chain, dying only to the already-catalogued unrelated `processSceneNode+1424`. s328
    closed the hypothesis with 2 confirmatory soaks (3/3 combined) — one died to another
    pre-catalogued crash family, one survived the full 240s hold with zero crashes; meets the M5
    plan's "two clean soaks" bar. Promoting the reversal to the shipped default is an open,
    explicitly-flagged decision, NOT made. s329 then tested `reapplyDisplayMode`'s site (the 3rd/last
    M5 gate) and found a genuinely NEW, unrelated failure: a permanent graphics-task-submission stall
    at VI=640 for the full 600s soak, audio staying fully alive throughout — refuting a
    same-mechanism hypothesis and motivating s330's source-read (item -188). `setDisplayMode`'s site
    was reversed and re-reverted every session (baseline force-zero restored each time, `audio gate
    patched x2` confirmed); the spin-pump patch and all diagnostics from this arc stay in the tree
    permanently, armed-but-inert by default. Full detail: `PORTING-STATE` Sessions 323, 325-329.

-160..-181. **(s297-322) M5 audio de-stubbing step 4: the gate-byte-reversal investigation's full
    measurement-chasing arc — 26 sessions building instrumentation and repeatedly narrowing a "call
    count" mystery, each step's premise superseded by the next, until s323 (item -182..-187) reframed
    it as a proven arithmetic inconsistency and s325 closed it.** s297-301 built the investigation
    runway: `docs/M5-AUDIO-PLAN.md` (s298), a source-read of the audio-engine gate byte
    (`0x800A0F50`, `musyxSynthFrame`'s only consumer), an always-on `[audtask-dispatch]` counter, a
    bounded-timeout guard on `waitForAnyAudioSlot`. s302 reversed `initMusyXEngine`'s gate site —
    later OVERTURNED s306 as dead code, never called (see Overturned Conclusions). s303/s307 reversed
    `setDisplayMode`'s site, both reproducing the VI=320 hang; s306 armed 3 gate-consumer entry/exit
    tags; s307 localized the hang to a shared upstream resource. s309-312 refined that: `[runner]`
    and `[audtask-dispatch]` are separate code paths stopping at different points (s309); the real
    `musyxSynthFrame` invocation mechanism is an indirect call through a VI-retrace callback table,
    missed by text grep (s310); an apparent "soft"(19/20)/"hard"(39/40) stop-point framing (s311/312)
    was itself an unwidened print-cap artifact. s313-322 (the gate1/2/3 "taken"/reachability chase)
    found 3 distinct stop points (37/37, 40/40), then a TOCTOU diagnostic bug (re-reading a shared
    countdown instead of the branch's own register, s318) had made gate1/2/3 look like they never
    fire at all; the corrected measurement showed real combined call rates still ~14 short of the
    tick-producers' own 37-call count — a gap s317/s321 confirmed by exhaustive grep has no missed
    static call site, and s322 confirmed isn't a stale-read bug in gate3's reachability guard either.
    `setDisplayMode`'s site was reversed and re-reverted every session (baseline restored each time,
    `audio gate patched x2` confirmed); the growing diagnostic set stays armed-but-inert by default.
    Full detail: `PORTING-STATE` Sessions 297-322.

-159..-14 (excluding -20, kept below). **Nine closed investigation lineages, s99-s294 — all CLOSED,
    no outstanding action.** Whack-a-mole guard-gap chases (`composeNpcOrientationMatrix`,
    `renderUnlitMeshFaces`, `heapWalker`, `heapFreeListDequeue`, the `-0x25A4` hangar-list-pointer
    family, breadcrumbs B2-B14), the audio-array-corruption race fix (s145/147/148), the
    `submitDmaRequestBatch` indirect-caller find (s101), the CALayer/campose SIGSEGV hunt, and the
    regen-pipeline-idempotency root cause. Full one-paragraph-per-lineage summaries migrated to
    `docs/PROJECT-OVERVIEW.md` §9 (this session's maintenance pass); full raw detail remains in
    `PORTING-STATE` Sessions 99-294.

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
  cannot reach its `SCHEDULE`/`HOLD_S` logic without first seeing VI=1024, which never happened. "Ran
  the full 600s hold... with `STICK_SCHEDULE`" in s340's own write-up was a self-contradiction (its own
  next sentence says the wait-for-1024 gate timed out) that went unnoticed because both describe the
  same 600s wall-clock window. Believable: the soaks genuinely were crash-free for the full 600s with
  audio/DMA/voice counters visibly live throughout (a real same-run positive control) — it just never
  occurred to check whether the `[keys]` schedule that was *supposed* to drive menu navigation had
  actually fired. The underlying `pairs=0` mechanism (item -195's source trace) is not overturned, only
  its context: it onsets pre-title, not mid-mission-cutscene, and (isolated s342) is specific to
  `reapplyDisplayMode`'s gate site, not `setDisplayMode`'s. PORTING-STATE 339, 340, 342.
- **(s107/108→s316→s318)** Two linked overturns in the gate1/2/3 tick-producer mechanism chase: (1)
  "the 3 near-identical countdown/period gates inside `musyxSynthFrame` fire `tickAllActiveSongs`/
  `tickAudioSequencerFrame`" was never validated with a positive control across 4 sessions (s108/s311/
  s312 measured only gate1's raw inputs, never its branch outcome) — s316 instrumented all 3 and found
  NONE ever takes "call," contradicting the functions' own 37-call count. (2) That "never calls" reading
  was itself overturned by s318: the `taken_skip` diagnostic field re-read the shared countdown fresh
  (`MEM_W`) instead of the register (`ctx->r2`) the real branch decision uses; all 3 gates race on that
  shared word, so the re-read diverged from the true value. Direct measurement of `ctx->r2` showed gate1
  takes "call" on 19/40 and gate2 on 4/4. Believable both times: the disassembly pattern matched exactly
  and raw-input constancy looked sufficient without checking the branch outcome (s316); then the
  read-once-for-branch/re-read-once-for-print diagnostic pattern is easy to write without noticing it
  reintroduces a race the first read didn't have (s318) — 3 sessions built increasingly precise
  instruments on false premises before the read pattern itself was questioned. PORTING-STATE 316, 318.
- **(s222→s223)** "no soak reaches mesh-heavy content" — a 4-soak sample-size artifact; a re-run
  reached space-combat content before freezing. The freeze itself is real, still reproduces (now a
  flat fill, not a torn polygon). PORTING-STATE 223.
- **(s216-218→s219)** "shared corrupt literal `0x0000000300000000` at x0/x8, WRITTEN somewhere" — that
  register is the process's constant RDRAM host base pointer, present by construction in every
  `MEM_W` fault, not written corruption; the wild operand is the *other* register (byte-identical at 3
  sightings, all the same `renderUnlitMeshFaces` bug, vs. an unrelated 4th `heapWalker` bug).
  Believable: byte-identical across sessions months apart. PORTING-STATE 219.
- **(s75/76→s150)** "single Start from SELECT YOUR CRAFT leaves into a distinct hangar-flight scene" —
  dense capture + an independent prior run + a code-level check (crash backtraces stay entirely in
  hangar-menu code) show it's the same craft-select scene under a corrupting camera move. Believable:
  HUD disappears, tilted silhouette against stars reads as "flying." Reopens "what leaves SELECT YOUR
  CRAFT" as unanswered. PORTING-STATE 150.
- **(s2-31→various, ~15 claims, grouped)** Build/pixel-getting era, each overturned within 1-2
  sessions: Z-buffers misread as colour buffers; texrect output called invisible; RDP "emitting
  nothing" (real bug: a function-local ring high-water mark); `DPC_WRAP`/fbpair-cap misdiagnosed for
  missing FULL_SYNC (PROJECT-OVERVIEW §4.6); `PRIM_ALPHA_FF` called necessary for text; a
  sampling-artifact black-screen; misattributed texture dumps, floor-band line-mask/palette/dxt
  theories (M1's real cause: s44-49), fog-color attribution, S=0-triangle phase, stale-TMEM-at-draw
  (§4.1), and 1024-phase black screen (present-starvation, not zero-shade). PORTING-STATE 2-31.
- **(s62-69, grouped)** "RSP task submission stays healthy through the freeze" — a 1-in-32 throttled
  sample missed the crashing tail; an unsampled histogram showed 100% `ImemOverrun` exits.
  "Self-restarting the end-of-IMEM perspective-divide branch un-freezes tasks" — the instrument fired
  0 times; the real site was `CLIP_1FBC`→`L_1650` (reconnecting `goto L_1650` unfroze `fs`).
  PORTING-STATE 62-69.
- **(s12-48, grouped — real causes already stated in "Current truth" above)** "0x6AB400 is the
  main-menu hangar" (believable: the partial render looked coherent for 36 sessions); stray
  briefing-room/SELECT-LEVEL origin+timing claims; hangar dimness/floor-band misattributed to a
  magnitude-erasing shade census / a residual-metric artifact (real cause: M1 s44-49); "no complete
  clip overlay in ROM" / "routing may be unsafe" (a stray census conflated fall-through hits with real
  dispatch). All overturned s47/s48. PORTING-STATE 12-48.
- **(s70-82, ~9 claims, grouped)** The post-`a` SIGBUS/black-screen self-correction chain — UAF
  theories, what survives past it, Start-press counting, `fs`/present-stall theories — all resolved by
  the s84 UAF fix and s82 sane-width gate. PORTING-STATE 70-82.
- **(s87→s88)** "8th crash class is self-recursion in `advancePlayerAnimationPhase`" — that call site
  belongs to a different, unreached function; an instrument showed constant stack depth across 3296
  calls, no recursion. PORTING-STATE 88.
- **(s302→s306)** "reversing `initMusyXEngine`'s gate-byte site validated safely (0/2 family #1
  recurrence)" — a positive-controlled entry counter found `initMusyXEngine` is never called at all,
  so the reversed write never executed; the clean result reflects dead code, not a validated gate=1
  state. Believable: the soaks genuinely were clean with real ucode dispatch confirmed throughout —
  only a dedicated reachability instrument could show the line hadn't run. Gate=1 still never
  exercised by any soak. PORTING-STATE 306.
- **(s307→s309→s313→s315)** A chain of "stop points converge" claims in the audio-tick investigation,
  each overturned by a closer same-run measurement: "the RSP-task freeze and audio-tick freeze land at
  the same point (task #39/tick #19), one shared upstream resource stopping both" (s307) — `main.cpp`
  source-read found separate code paths; audio ticks actually stop 18 tasks and 1930 log lines earlier
  (s309). "The 3 tick-producer functions and RSP `M_AUDTASK` submission all stop together at call #19/20
  (a SOFT stop)" (s307/310/311) — a widened, resampled print-cap soak found `update3DAudioFrame` fires
  40/40 (the real hard-stop boundary), the tick-producers stop 3 calls earlier at 37/37, and only
  `M_AUDTASK` genuinely stopped at 20/20 (s313). Then "`M_AUDTASK` genuinely stops at 20/20" itself —
  its diagnostic (`src/main/main.cpp`, native runtime code, not a `fixup_game_funcs.py` patch) had the
  identical unwidened flat-cap bug s313 had just fixed in 4 *other* diagnostics, missed because it lives
  outside the game-code patch file; widening found it also fires 40/40 (s315). Net result: 2 real stop
  points (37/37 and 40/40), not 1 or 3. Believable each time: similar small round numbers followed by
  "scheduler churn with no new work" reads as simultaneous unless line numbers are diffed; and having
  just fixed the same bug pattern elsewhere bred false confidence the remaining tag was already correct.
  PORTING-STATE 309, 313, 315.

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
