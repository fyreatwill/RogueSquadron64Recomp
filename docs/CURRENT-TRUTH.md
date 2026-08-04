# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how
the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = the `## LLE session N` headings,
`s10`–`s32` = the `## Session N` headings.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Set after the 300-session review. Priority order for upcoming iterations:
1. **Maintenance** (Step 0 of ITERATION.md now triggers it): this file is ~15x over its 35 KB cap
   and this headline is ~125 sessions stale. Compact per the Maintenance section of
   tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED. **[s295: done — compacted
   562,666→120,975 bytes, 7,959→1,267 lines; Step 0's 60,000-byte trigger will not re-fire until
   this file regrows past that mark. Did not reach the 35 KB stretch target — see PORTING-STATE
   Session 295 for why. Next maintenance pass should consider dropping items older than ~-100
   outright rather than further compressing them.]**
2. **M5 audio de-stubbing**: design doc first (docs/M5-AUDIO-PLAN.md — survey every audio
   stub/trap/gate in force, plan incremental de-stubbing with a validation soak per step), then
   execute stepwise. Rationale: waitForAnyAudioSlot boot deaths, voice-array corruption, slot
   reaping and MusyX DMA crash families are plausibly artifacts of the audio-disabled degenerate
   paths — de-stubbing may dissolve classes now guarded one deref at a time.
3. **M3 crash work only as systematic idiom-class audits** (the s282–s288 `-0x25A4` model), never
   reactive single-crash chases. Breadcrumbs are passive: enqueue soaks to scratch/agent/soak_queue/
   (the loop runs them between iterations), consume scratch/agent/SOAK-RESULTS.md.
Sanctioned tooling work unit, counts as ADVANCED whenever picked up: backport function-scoped
matching (the BREADCRUMB10+ slice idiom) to the ~100 file-scoped-only guard patches in
fixup_game_funcs.py, per the 2026-08-04 analysis in that file's header comment.


## Current truth (as of session 295)

    cd build && ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_STUB_MISSING_FUNCS=1 ./RogueSquadron64Recomp

Metal shader rebuilds need full Xcode on PATH:
`export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer` (bare CLT has no `metal`).

- `ROGUESQ_LLE_SOLO=1` is not optional: without it the runner runs LLE **and then falls through to
  HLE for the same task** (s9).
- Default-ON, no longer worth naming: `ROGUESQ_VI_FOLLOW_DRAW=3` (s23), `ROGUESQ_SHADE_WRAP=1`
  **per-pixel** (s24 vertex → s26 shader), `ROGUESQ_FIX_ZERO_SHADE` (s20, largely subsumed by
  wrap), `ROGUESQ_FIX_SAMPLE_BOUNDS` (s15), `ROGUESQ_VI_FULLSYNC` (s11), PresentEarly fallthrough +
  forceAdvance + `ROGUESQ_PRESENT_EARLY_FORCE` (s21), deferred-range coalescing (opt out with
  `ROGUESQ_NO_DPC_MERGE=1`, s10), **s78 wild/OOB FB refuse** in `FramebufferManager::get`
  (width>1280 or past 8MB — same family as s72 writeback; does **not** unfreeze present),
  **s182 `[fbsync-oob-skip]` guard** in `State::fullSync`'s color/depth read-into-`fbStorage`
  blocks (`rt64_state.cpp`) — s78's refuse gate returns a `refuseFb` that still carries the wild
  width/height, and this downstream RDRAM read had no bounds check of its own; skips the
  `FramebufferStorage::store` read when it would exceed the 8MB RDRAM buffer, same family as s72/s78.
- Default-OFF, keep them off: `ROGUESQ_FIX_DXT` (s22/s23), `ROGUESQ_FIX_DXT_I` (s27, null on
  hangar band), `ROGUESQ_FLATTEN_I4` / `FLATTEN_RGBA16` / `FLATTEN_CI4` (attribution probes),
  `ROGUESQ_SHADE_ONLY_MONO` (s30; pad-only, not a band fix), `ROGUESQ_SHADE_WRAP=3` (s31 shared
  wrap experiment), `ROGUESQ_SHADOW2`, `ROGUESQ_RING_RESYNC`. Diagnostics: `ROGUESQ_DUMP_IMEM_DMA=1`
  (s47, lib-side) dumps every skipped IMEM DMA to `build/imem_dma_dump.bin`
  (`scratch/s47_parse_imemdump.py` decodes). `ROGUESQ_LOG_RUNNER=1` prints a per-task RDP-opcode
  histogram (1-in-32 sampled by default — `ROGUESQ_LOG_RUNNER_ALL=1`, s64, prints every task
  unsampled; the sampled mode silently misattributes 31 tasks' counts onto whichever task is next
  sampled, a real bug for any single-task question). `ROGUESQ_LOG_SEQ=1` dumps a task's raw
  pre-translation DL bytes — **not** a valid way to answer "does this task emit SYNC_FULL": that
  question needs the post-translation histogram above (s64, positive control failed on the raw-byte
  method).
- Deleted from the code (s44, title-screen probe unchanged): `ROGUESQ_DPC_WRAP` /
  `ROGUESQ_WRAP_DEDUP` (s11 — wrap bytes are now always counted and dropped), `ROGUESQ_FORCE_PAL15`
  (s14, dead per s15), `ROGUESQ_FORCE_SHADE_WHITE` (s19, its shade line closed at s43).
  `ROGUESQ_MAX_FBPAIRS` (default 8192) engages 0 times since s11 but is KEPT deliberately — OOM
  insurance for future FULL_SYNC-less phases (M3 missions), turns a 22 GB Metal abort into a capped
  workload (s44).

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

Menu state machine (s48, extended through s75; hold/crash triage s76-s114 — full session-by-session
chase in `PORTING-STATE`, not repeated here): title —start→ SELECT GAME —start→ war room / SELECT
LEVEL —start→ **AVAILABLE CRAFT** (war-room craft holograms; footer "PRESS [A] FOR LEVEL
DESCRIPTION"). From AVAILABLE CRAFT, `a` does **not** show a level description card (s61–s69). With
process alive 65s+ post-`a` (s72/s73): **black ~5s → ~1s mission-shaped capital-ship flash (texture
garbage) → stable SELECT YOUR CRAFT** (hangar pad + full X-wing, "PRESS [A] FOR CRAFT DESCRIPTION",
multi-hue floor garbage; camera orbits). From SELECT YOUR CRAFT: **`a` no-ops** (s74); **a single
Start leaves the menu** — **OVERTURNED s150 (see "Overturned conclusions"): same craft-select scene, a
corrupting camera move, not a new environment — "what leaves SELECT YOUR CRAFT into a mission" is
reopened as unanswered.** VI stays on the 0x6AB400/0x656400 pair — origin cannot name these scenes
(s48).

**Root causes found and fixed during the s76–s114 hold/crash-triage chase** (~20 distinct crash
classes catalogued total; full session-by-session detail in `PORTING-STATE` and the "Next steps"
list below, not repeated here):
- **Post-leave black screen** (s76-s82): RT64 was presenting a wild last-drawn framebuffer (mode-3,
  width 1..257). Fixed by an always-on sane-width gate on the last-drawn store (s82) — black
  duty-cycle collapsed from 8/8 early-black holds to 0/5.
- **`evalCubicSplineAtTime` NaN abort** (s83): div-by-zero on a zero-width keyframe interval —
  guarded at the source; unvalidated by a same-run positive control but never recurred once the fix
  was in place.
- **OSThread UAF SIGBUS (`thr-resume bad=1`)** (s70-72 discovery, s84 fix): a scheduler
  thread-context reuse bug — gated with an always-on skip; got its first positive control s88
  (`bad_total=1`, process survived) — closed.
- **`do_rom_read`/`piDmaWorker` DMA corruption** — the single longest-running M3 thread (~30
  sessions, s85–s147): root-caused as a non-atomic `voiceCount`-write-before-pointer-store race in
  `allocateSongChannelArray`, letting the concurrently-scanning audio thread read against a stale
  array. **Fixed and verified s147/148** — 3 independent crash-free soaks, 0/13 corrupted reads
  post-fix vs. 5 pre-fix (see the "Next steps" list, near the top of the chronological range, for the
  fix and validation detail; full chase in `PORTING-STATE` Sessions 85-147).
- **TMEM-zero-dimension RT64 assert** (`queueGPUUploadTMEM`, first seen s86): a stopgap skip-guard
  landed s192 (see Goal stack M3 item 2) — root cause (why the tile-sample dimension is ever zero)
  still open.
- **~20 "hangar-tick-family" crash classes** (unguarded-pointer-chase shape, one guest function at a
  time, s89-s110): 8 guarded s99-110; the s126-132 re-audit found and closed a 2nd unguarded gap in
  6 of those 8; the `-0x25A4` hangar-list-pointer sub-family (the single biggest recurring source of
  new sites in this catalog) was fully closed by the s282-288 systematic audit lineage. Full crash
  catalog with per-class status: "Next steps" list below (near the chronological bottom).

**s48 scene-identity correction:** there is no "main-menu hangar". The 512-wide origin-0x6AB400
scene is the round **level-select war room**. Pre-clip-fix it rendered with every clip-needing
triangle dropped (camera inside a curved room), so the tiered console rings and holotable were
missing: the central platform read as a "landing pad", the Mos Eisley preview hologram as a parked
X-wing, and the stale-RDRAM band filled the rows the rings should cover. Post-fix the room renders
complete. VI origin **cannot** discriminate menu scenes (the war room presents from the same
0x6AB400); identify menu scenes visually from captures.

512-wide covers two different scenes; tell them apart by VI origin (0x690400 outdoor, 0x6AB400
war room) — but see s48: origin distinguishes *phases*, not which menu scene is on screen.

Remaining visual defects:
- ~~s50/s51 AVAILABLE CRAFT → black → one mission frame → `fs` freeze / SIGBUS~~ — **FIXED**
  (ImemOverrun s69; depth-writeback SIGBUS s72 — mechanism in "Root causes found and fixed" above).
  s51's "environment load confound" theory was **OVERTURNED s60**: the repro scripts set no
  `ROGUESQ_*` vars, so the binary silently took the HLE path — `uptime` is not a precondition for
  any work unit (s61 reconfirmed at load 3.93–4.41).
- ~~Hangar floor multi-hue band~~ — **FIXED and root-caused, s45–s48 (M1 closed).** Mechanism and
  fix recipe: `docs/PROJECT-OVERVIEW.md` §3 ("Fixing the hangar band"). Parked anomaly (M4): 39 of
  55 I4 uploads sample 64x128 past `masks=6/6`. Overlays 12/44 still take the old broken dispatch
  path by design — same splice recipe applies if a phase ever needs them.
- ~~Hangar dimmer than the s11 peak~~ — **largely fixed, s25** by `SHADE_WRAP` (vertex
  then s26 per-pixel).
- Outdoor 512 zero-shade is masked, not fixed: `ROGUESQ_FIX_ZERO_SHADE` + wrap both map
  the −0.5 class to white; why LLE carries `baseFixed = −32768` is unknown (s19/s20).
- Triangles with S identically zero in the 640 attribution phase: real, uninvestigated (s18).
- `[dpc-behind]` ring-wrap drops remain genuine dropped content with `DPC_WRAP` off; they are simply
  not the cause of any known black screen (s11).

Stability: clean through s27 driven hangar soaks and s49's post-clip-fix regression sweep
(undriven full timeline + driven war room). 0 `UnhandledJumpTarget`, 0 `[defer-drop]`,
0 `[dmem-race]`, 0 asserts. `[missing-func]` clean in every soaked phase to date, **except**: s49's
undriven outdoor-512 stretch stubbed 3 distinct addresses once each (0x800C7120, 0x800FBD48,
0x800FB190) with 0 aborts — never itemized before because prior soaks targeted hangar/war-room, not
outdoor. Parked as an M4 curiosity, not a blocker. **s50–s72 mission-entry path:** ImemOverrun
fixed (s69); SIGBUS from garbage depth writeback fixed (s72). Hangar/war-room/outdoor stability
from s27–s49 stands; post-`a` process now soaks well past 65s without death.


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

**M3 — first gameplay: OPENED (s50); ImemOverrun FIXED (s69); OSThread SIGBUS FIXED (s72);
post-`a` scene ID (s73); Start path isolated (s74/s75); hold/assert triage (s76/s77);
wild-FB refuse gate (s78); D3 S1–S4 (s79); VI_FULLSYNC decision V1–V4 (s80);
intermittent-black B1–B4 (s81); last-drawn sane-width gate (s82, G1);
evalCubicSplineAtTime NaN root-caused, 2 new crash classes found (s83);
thr-resume `bad=1` gated (unvalidated), 5th crash class found (s84);
frameStartReset was a fluke, do_rom_read corruption root-caused, unified
shared-race hypothesis raised (s85); shared-race test inconclusive
(do_rom_read didn't recur), 7th crash class found firing even earlier
(s86); TMEM-zero instrument landed but never fired, 8th crash class found
firing even earlier still (s87); s87's self-recursion hypothesis refuted
at the source level, correctly-targeted instrument shows no recursion,
thr-resume gate U3 closed, first crash-free soak since s83 (s88);
anim-recursion hypothesis parked after a 3rd non-recurrence, TMEM-zero
assert reproduced with a full backtrace, 9th crash class found (s89);
3rd straight "armed TMEM-zero, a newer crash preempted it" outcome,
10th crash class found, batched entry-log instruments for the 9th and
10th classes (s90); `do_rom_read` corruption proven deterministic and
reproducible (3x byte-identical), refuting the s85 "random race"
framing (s91); `ra=0x00000000` shown to be routine (not corruption
evidence), `do_rom_read` non-recurrence, 11th crash class found in
`projectModelBoundsToScreen` (s92); s92's confound-removal was never
real (script bug), fixed it, `do_rom_read` recurred immediately (4th
hit), confound theory confirmed (s93); DMA-ring producer/consumer
instrument landed and discriminates in one soak — producer fires 10x
not once (5th `do_rom_read` hit), refuting "one boot-only call" and
finding an unlocated indirect caller whose batch writes ASCII-looking
garbage into the `devAddr` field at write-time, not via a later stomp
(s94); `get_function`-chokepoint instrument landed to find that caller
directly, first soak inconclusive (died early to a 12th, recurring
crash class before reaching the target window) (s95); 2nd consecutive
inconclusive attempt — 12th class didn't recur but a brand-new 13th
crash class (RT64-internal `reinterpretTileRecord` assert) died even
earlier, instrumentation-overhead confound checked and refuted at the
source (s96); 3rd (final allowed) attempt died even earlier to a
brand-new 14th class, parking the blind DMA-caller repro per rule 8;
pivoted to instrumenting the most-recurring hangar-tick class
(composeNpcOrientationMatrix, 12th) — clean positive control, no
crash on that path, but a brand-new 15th (RT64-internal) class killed
the run instead (s97).**
AVAILABLE CRAFT reachable. **s75:** single Start → hangar-flight.
**s78–s79:** RDP-`fs` plateaus post-leave (S1). **s80:** synthetic FIRE continues.
**s81:** black = mode-3 presenting wild last-drawn. **s82:** always-on sane-width
gate — **black duty-cycle collapses**; hangar-flight visible ~5s then freezes on
last sane frame (S1 residual); death `evalCubicSplineAtTime` NaN Abort (~hold+6s).
**s83:** NaN div0 guarded at source (unvalidated, 0/2 fires); with that assert no
longer winning the race, 2 soaks died from 2 *different* crashes instead — Metal-
internal shader-compiler SIGSEGV (no source on our side), and a `thr-resume
bad=1` UAF SIGBUS (same class as s70–s72, detector exists at
`threads.cpp:198-238`, never gated). **s84:** gated the SIGBUS site (always-on
skip, `lib/` patch exported+committed); soak ran clean with 0 `bad=1` (no
positive control yet) but died **earlier** (hold+~1s) to a **new** SIGBUS in
`frameStartReset` (hangar-selection per-frame poll loop). **s85:** 2 repro
soaks — `frameStartReset` never recurred (fluke, not dominant); both instead
hit s80's parked `do_rom_read` Abort/SIGSEGV with a **garbage `physical_addr`**
(added `[rom-read]` logging, `lib/` exported+committed) that varies run-to-run
(odd-small vs. ~208 MB-OOB) — raised, not yet proven, that this is the **same**
shared-corruption race as the OSThread UAF / thr-resume `bad=1` families
rather than a 6th independent bug. **s86:** added thread-identity fields to
`[rom-read]` to test that hypothesis; one soak's `do_rom_read` stayed clean
(488 calls, all sane) so the test is inconclusive — but died *earlier* than
usual to a **7th** crash, `assert(width>0 && height>0)` in
`queueGPUUploadTMEM` for a real texture decode with a zero tile-sample
dimension (`rt64_state.cpp:1329` → `rt64_rdp_tmem.cpp:52` →
`rt64_texture_cache.cpp:1285`), not yet root-caused. **s87:** landed
`ROGUESQ_LOG_TMEM_ZERO=1` logging at the `uploadTexture` call site to
test that; it never fired (0/0) because the soak died even earlier
(hold+~3s) to an **8th** crash: SIGBUS in `advancePlayerAnimationPhase`
(`0x80062B04`) recursing into itself through an indirect call at
`0x8006426C` (`jalr` via a function pointer read from fixed global slot
`0x80139968`) — source-read hypothesis (stale/corrupted callback-table
pointer), not confirmed by a live value yet. **s88:** re-checked before
instrumenting — refuted at the source level (`0x8006426C` belongs to
`invokeMenuOverlayHeaderCallback`, unreached from the crashing call
chain; `advancePlayerAnimationPhase` itself has zero indirect calls).
Landed `ROGUESQ_LOG_ANIM_CB=1` (entry log: guest `$sp` + args, depth
proxy) targeting the actual function. Soak was the first to survive the
full hold window crash-free since s83; instrument fired 3296/3296
(positive control) with `sp` confined to 6 values (312 bytes) — no
recursion, shallow or deep, refuting both NEXT.md hypotheses for this
run. The s84 thr-resume `bad=1` gate got its first positive control in
the same run (`bad_total=1`, process survived) — **U3 closed**. Second
data point for the shared-corruption-race hypothesis (crash-free vs.
5 straight crashing soaks). **s89:** 2 more soaks, both crashed but
neither on the target bug (3rd non-recurrence, now parked per rule 8).
First full backtrace for the TMEM-zero assert (item 2): `fullSync
FramebufferPairTiles` → `uploadTile` → `uploadTexture` →
`queueGPUUploadTMEM`; the "undefined tile" logging seen the same run is
a red herring (already guarded before reaching `uploadTexture`). Found a
**9th** crash: SIGBUS in `updateAnimatedTextureStreaming`
(`funcs_11.c:13665`, via `menuOverlayInit`), likely an unchecked `MEM_W`
deref off a corrupt `a0` — same signature as the shared-corruption-race
family. Leave key closed. Origin still cannot name
scenes. **s90:** re-ran the same soak shape a 3rd time with the flag
armed; TMEM-zero still 0/4, and a **10th** crash preempted it again:
SIGBUS in `static_5_800B4048` (unconfirmed name), called from the known
`updateHangarBayScene` → `runHangarSelectionFrame` →
`runHangarMenuFromOverlay` → `menuOverlayInit` chain — same
unchecked-`MEM_W`-off-an-arg shape. `[anim-recurse]`/`thr-resume` controls
held again. Landed batched entry-log instruments for the 9th
(`ROGUESQ_LOG_ANIM_TEX_STREAM=1`) and 10th
(`ROGUESQ_LOG_HANGAR_ENTRY=1`) crash sites, built clean, not yet soaked.
Per rule 8, demoted "catch TMEM-zero with the flag armed" from primary
plan to opportunistic after 3 non-discriminating attempts.
Full detail PORTING-STATE s68–s90;
`scratch/s73_post_a_scene/LDGATE1_ANALYSIS.md`.
*Done when:* 60 seconds of in-mission rendering, craft visibly responds to synthetic input,
stability counters 0, and the phase timeline in this document covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause (currently masked, not fixed); the S=0 triangles in the 640 attribution phase; the I4
`sample=64x128` anomaly if M1 didn't consume it; the 3 `[missing-func]` addresses stubbed in the
undriven outdoor-512 stretch (0x800C7120, 0x800FBD48, 0x800FB190, s49) — **identified, s53**:
`getConfigFloatPair` / `clearMissionObjectiveFlagsAndEnterPhaseSix` / `requestMissionTransitionMode`
respectively, all real mission-overlay functions (2/3 confirmed prologue, 1/3 a plausible frameless
leaf) present only in `symbol_files/main_overlay.txt`, not `mission_overlay.txt` — the exact
"symbol assigned to a non-overlay file" failure `overlays.cpp:388` describes. Not behaviorally
silent by name (mission-phase-transition and objective-flag logic). **s54: fix applied** (3 lines
added to `~/Documents/Tools/rogue_squadron64/symbol_files/mission_overlay.txt`, a sibling checkout
with its own git repo — not `lib/`, no `submodule-patches/export.sh` needed) and the full regen
pipeline (`make_elf.py` → `N64Recomp` → `fixup_game_funcs.py` → `cmake --build`) ran clean, build
exit 0, no new warnings/errors. **Runtime confirmation still outstanding** — s54 rechecked load
post-build (3.52/3.10/3.11, 33 `claude` processes, worse than at start) and correctly skipped the
game run rather than risk a load-stalled false-negative; not yet re-attempted. That sibling repo
also carries pre-existing uncommitted changes to 3 other symbol files from earlier sessions,
unrelated to this fix — flagged for the user, not committed autonomously (s54).

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5), what bridges RSP audio output to SDL, and what the audio-gate byte
reversal implies. **Gate M5 behind M2**: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.


## Next steps, in order of expected value (s295)

Numbering convention (fixed s295, was previously three colliding sequences): items are
numbered -159 (top, newest/highest priority) counting up to -1 (bottom, oldest); relative
order is unchanged from before the fix. The next new item takes -160 and is inserted at the
top.

-159. **(s294)** Resumes the abandoned s249-251 project-wide unguarded-walk sweep; source-reads and
    breadcrumbs `stopSongByHandle` (`BREADCRUMB14`, 180 sites, `funcs_25.c:4390-4818`) -- no unique
    translation bug, same uniform unguarded-`RECOMP_FUNC` baseline as every prior candidate.
    **Headline result**: catches `tickTextureMaterialExpiry`'s (`BREADCRUMB12`) SECOND recurrence at
    the IDENTICAL guest PC as s293's soak (`0x80022094`, `funcs_6.c:12207`, a 2-byte read of
    `ctx->r16+0x8`) -- crossing the two-independent-observations confirmation bar. **This is now the
    fully-specified top-priority next work unit -- see `scratch/agent/NEXT.md` for the exact guard
    site, fix template, and validation plan; do not re-derive it here.** Full detail: `PORTING-STATE`
    Session 294.

-158. **(s293)** Lands `BREADCRUMB13` scoped to `tickSongSequence` (`funcs_25.c:4878-5317`),
    closing a 119-session-old unaddressed backlog item (s174) -- no unique translation bug. Bonus:
    this session's own validation soak caught the FIRST recurrence of `tickTextureMaterialExpiry`
    (`BREADCRUMB12`) at `funcs_6.c:12207` -- 1 of the 2 observations `BREADCRUMB12`'s now-ready guard
    rests on (see item above). Full detail: `PORTING-STATE` Session 293.

-157. **(s292)** Lands `BREADCRUMB12` scoped to `tickTextureMaterialExpiry`
    (`funcs_6.c:12135-12332`), closing the last fully-unaddressed s270 backlog item (first flagged
    s157) -- no unique translation bug, no raw caller-controlled pointer (every deref traces to an
    internally-walked global table + linked-list chain); sole candidate `ctx->r16`. Full detail:
    `PORTING-STATE` Session 292.

-156. **(s291)** Lands `BREADCRUMB11` scoped to `coalesceFreeHeapBlocks`
    (`funcs_0.c:4332-4804`), closing a 21-session-old backlog item (s270) -- no unique translation
    bug. Full detail: `PORTING-STATE` Session 291.

-155. **(s290)** Full source read of `inflate_fast` (`funcs_7.c:13553-14116`) finds no
    unique translation bug. **Key finding**: the recompiler's `MEM_B`/`MEM_BU` macros turn a register
    holding exactly 0 into `rdram + 0x80000003` -- the s272 crash's `si_addr=0x380000003` is the SAME
    long-tracked near-`0x80000000` null-pointer signature guarded ~15 times elsewhere since ~s130, not
    a novel zlib bug. Lands `BREADCRUMB10` scoped to `inflate_fast`; no guard (unvalidatable blind, 1
    observation ever). Full detail: `PORTING-STATE` Session 290.

-154. **(s289) CLOSES the elevated pre-scene `waitForAnyAudioSlot` death-rate backlog item (open since s278) as a non-finding — the elevated rate was real but confined to a 4-session window (s276-278, s280: 7/8 = 87.5%) that had already fully reverted by s281, a full session before the `-0x25A4` audit lineage (s282-288) even began.** Full detail: `PORTING-STATE` Session 289.

-153. **(s288) CLOSES the `-0x25A4($s1)` hangar-list-pointer audit lineage (s283-288) entirely — `playerSnowSpeederInit` has ZERO `-0x25A4` hits, and its apparent 3-function label overlap (flagged by s286/287 as a possible dead-duplicate signal) is REFUTED: it is genuinely live, continuously-translated code that merely shares virtual address space with `static_5_800AAD9C`/`static_5_800AB1C8`/`static_5_800AB658`, not a text/byte copy of any of them.** Full detail: `PORTING-STATE` Session 288.

-152. **(s287) CLOSES the entire `hangarInitialize` `-0x25A4` audit — chunks 3, 4, and 5 (the remaining ~89% of the function, 124187-133572) all confirmed dead unreachable duplicate code via the chunk-2 methodology, 0 new guards needed anywhere.** Full detail: `PORTING-STATE` Session 287.

-151. **(s286) Classified `hangarInitialize` chunk 2 (124187-124999) — proved by byte-for-byte diff + function-scoped goto-reachability check that it is entirely unreachable duplicate dead code (a copy of `static_5_800AAD9C`'s already-fully-guarded body), needing 0 new guards.** Full detail: `PORTING-STATE` Session 286.

-150. **(s285) Completed `hangarInitialize` chunk-1 (queued by s284/an interrupted prior session) and found+fixed a THIRD instance of the "second-hop" blind spot, this time in `static_5_800A9270` — correcting -125's "4/4, fully guarded" claim below.** Full detail: `PORTING-STATE` Session 285.

-149. **(s284, "4/4 fully guarded" claim for `static_5_800A9270` corrected by -126 above — 5/5 known sites now, not provably exhaustive) Deliberate grep-based audit of every `-0x25A4($s1)` hangar-list global-pointer reference across `RecompiledFuncs/*.c`, per s283's plan — found the audit scope was far larger than the 4 incidentally-discovered sites, landed 29 new guards across 3 functions, and found + fixed a live crash the new guards exposed.** Full detail: `PORTING-STATE` Session 284.

-148. **(s283) Source-read `static_5_800A9270`/`loadCutsceneAssetsByIndex` per s282's plan — found and closed the `+948` backlog item, PLUS 2 more unguarded sites of the same bug shape in the same function.** Full detail: `PORTING-STATE` Session 283.

-147. **(s282) Re-soaked `BREADCRUMB8`/`emitAllocatedDLCommand` per s281's plan (its 2nd session) — soak1 hit an already-catalogued site, but soak2 crashed inside `static_5_800AB658` itself (`BREADCRUMB7`'s own target), the FIRST informative hit across the whole `BREADCRUMB5`-`9` family.** Full detail: `PORTING-STATE` Session 282.

-146. **(s281) Re-soaked `BREADCRUMB7`/`static_5_800AB658` per s280's plan (its 2nd session) — 0/2 this session, 0/4 combined (s274+s281), never informative on its own target.** Full detail: `PORTING-STATE` Session 281.

-145. **(s280) Re-soaked `BREADCRUMB6`/`buildPositionAndCallTransformHelper` per s279's plan (its 2nd session) — BOTH soaks died PRE-SCENE to the identical `waitForAnyAudioSlot` boot crash (`last-guest-pc=0x8000b650`, the recurring stale `beginFrameDLChunk` value), 0 informative hits, no new crash site.** Full detail: `PORTING-STATE` Session 280.

-144. **(s279) Ran s278's step 1 (free, no-soak source-read of `tickWrappingTimerAccumulatorList`'s 4 call sites) — it REFUTES the `BREADCRUMB9` instrumentation-confound hypothesis mechanically, no soak needed.** Full detail: `PORTING-STATE` Session 279.

-143. **(s278) Re-soaked `BREADCRUMB9`/`tickWrappingTimerAccumulatorList` per s277's plan (its 3rd session) — BOTH soaks died PRE-SCENE to the identical `waitForAnyAudioSlot` boot crash, 0 informative hits, tripping the rule-8 3-strikes threshold.** Full detail: `PORTING-STATE` Session 278.

-142. **(s277) Re-soaked `BREADCRUMB9`/`tickWrappingTimerAccumulatorList` per s276's plan, no code change — soak 1 died PRE-SCENE to the identical `waitForAnyAudioSlot` boot crash a 3rd consecutive time (across s276+s277), but soak 2 broke the streak: reached the scene and ran the full 240s hold plus grace completely crash-free.** Full detail: `PORTING-STATE` Session 277.

-141. **(s276) Landed `BREADCRUMB9` on `tickWrappingTimerAccumulatorList` per s275's plan — 0/2 this session (its first), no informative hit.** Full detail: `PORTING-STATE` Session 276.

-140. **(s275) Landed `BREADCRUMB8` on `emitAllocatedDLCommand` per s274's plan — 0/2 this session (its first), no informative hit on its own target.** Full detail: `PORTING-STATE` Session 275.

-139. **(s274) Landed `BREADCRUMB7` on `static_5_800AB658` per s273's plan — 0/2 this session (its first), no informative hit. Soak 1 ran the entire 240s hold plus grace crash-free (deepest soak this investigation has recorded).** Full detail: `PORTING-STATE` Session 274.

-138. **(s273) Re-soaked `BREADCRUMB5` per s272's plan — still 0/4 combined, no informative hit ever on `reserveAndEmitDLEntry` itself.** Full detail: `PORTING-STATE` Session 273.

-137. **(s272) Landed `BREADCRUMB5` on `reserveAndEmitDLEntry` per s271's plan — 0/2 this session, no informative hit on its own target.** Full detail: `PORTING-STATE` Session 272.

-136. **(s271) Re-soaked per s270's plan — `BREADCRUMB4` still 0/2 (now 0/4 combined), but soak 1 caught a brand-new crash (`emitAllocatedDLCommand+6608`, different fault shape) and soak 2 finally caught and exactly localized `BREADCRUMB3`'s own long-elusive target: guest `0x8000B03C` inside `beginFrameDLChunk` itself — a 4th unguarded copy of the cached-free-list-head idiom, first occurrence found outside `submitSceneNodeRender`.** Full detail: `PORTING-STATE` Session 271.

-135. **(s270) Landed `BREADCRUMB4` on `processSceneNode` per s269's plan — it did NOT catch its own target in 2 soaks (0/2, breaking the 3/3 streak s267+s269 had built up), but the 2nd soak instead caught a different, symrange-confirmed real crash in `submitSceneNodeRender` (a 3rd unguarded copy of the "cached free-list-head" idiom already fixed twice before).** Full detail: `PORTING-STATE` Session 270.

-134. **(s269, superseded as top priority by s270 above) Landed `BREADCRUMB3` on `beginFrameDLChunk` per s268's plan — it didn't catch its own target in 2 soaks, but both soaks instead landed an EXACT, byte-identical crash in a different function, `processSceneNode+1184` (`si_addr=0x380000030`), that s267 had also hit once before unverified.** Full detail: `PORTING-STATE` Session 269.

-133. **(s268, superseded as top priority by s269 above) Ran s267's prescribed re-soak plan 3 more times (`run_dequeuearg1.sh`, unmodified) — still 0 reproductions of the specific `heapFreeListDequeue`-range crash `BREADCRUMB2` targets (now 0/6 across s267+s268 combined), but caught a NEW crash site sharing the exact same "guest fault address `0x80000000`" shape in a DIFFERENT, never-before-catalogued function: `beginFrameDLChunk+13420`.** Full detail: `PORTING-STATE` Session 268.

-132. **(s267, superseded as top priority by s268 above) Refuted the a0-argument hypothesis for the guest-`0x80000000`-family fault inside `heapFreeListDequeue` via a same-run positive-control trace (167k fires, last one immediately before a captured crash showed a sane in-range pointer, not `0x80000000`), and armed a 2nd guest-PC breadcrumb (`BREADCRUMB2`) scoped to that function's own body — but 3 follow-up soaks didn't reproduce this specific crash.** Full detail: `PORTING-STATE` Session 267.

-131. **(s266) Re-soaked per s265's plan, caught a genuine `submitSceneNodeRender`-range crash (offset +47120, NOT the original +19268 target), localized it via `[CRASH][last-guest-pc]=0x80010E40` to a 2nd, previously-unguarded occurrence of s197's "cached free-list head" idiom, and landed `CACHE2_GUARD` (`N64Recomp/fixup_game_funcs.py`) — 2 post-fix soaks show no recurrence of this crash, but surfaced a DIFFERENT, higher-priority bug.** Full detail: `PORTING-STATE` Session 266.

-130. **(s265) Landed the "last-executed-guest-PC breadcrumb" instrument (`g_rs64_last_guest_pc`) s264 flagged as a generically-overdue investment, verified it works correctly, but the target `submitSceneNodeRender+19268` crash did not recur in any of 6 soaks this session.** Full detail: PORTING-STATE Session 265.

-129. **(s264) Ran s263's prescribed 2nd `dequeueguard1` soak (iron rule 4) — it crashed, not clean, and a NEW disassembly-based methodology proves the crash is structurally unrelated to `heapFreeListDequeue`/`DEQUEUE_GUARD` entirely, AND that s263's justification for the guard repeated a fallacy `PORTING-STATE` Session 219 already refuted 44 sessions ago.** Full detail: PORTING-STATE Session 264.

-128. **(s263) Executed s196's 66-session-overdue prescription: source-read `submitSceneNodeRender` in full for the real 18th-crash-class mechanism.** Full detail: PORTING-STATE Session 263.

-127. **(s262) Added `renderUnlitMeshFaces` GUARD2 for the pre-loop peek-load gap a subagent-assisted re-read found — but the soak that tested it never even called `renderUnlitMeshFaces` (0/0 on the positive-control counter), so the fix is UNVERIFIED, not refuted.** Full detail: PORTING-STATE Session 262.

-126. **(s261) Closed s260's 9th `composeNpcOrientationMatrix` gap (`COMPOSE_NPC_GUARD9`) — the whole 9-guard whack-a-mole family (s100-261, 21+ sessions) is now closed as a blocker: this soak got the FIRST-EVER live call into `renderUnlitMeshFaces` (`unlit-mesh-tracer` positive control fired for the first time in this investigation's entire history), survived to VI-update #8552/143.1s (previous best ~75s, a full second phase transition past SELECT-CRAFT), and converged on the already-catalogued item -49 KSEG0-zero-extension bug for its 7th confirmed occurrence (exact `+792`/`0x380630062` signature match to s208/s254/s256).** Full detail: PORTING-STATE Session 261.

-125. **(s260) Closed s259's `setLookupEntryField5ByKey` lead, but it took TWO guards, not one — the first guard (validating the caller's argument) was a red herring; the real bug was a 2nd-level pointer loaded INSIDE the callee.** Full detail: PORTING-STATE Session 260.

-124. **(s259) Guarded the `evalCubicSplineAtTime` unguarded pointer s258's lead pointed at; soak shows the guard is inert (0 fires, no crash there) but the run advanced past it into a BRAND NEW, unrelated crash family: `activateAnimationKeyframe`'s `setLookupEntryField5ByKey` callee.** Full detail: PORTING-STATE Session 259.

-123. **(s258) Closed the 2 gaps s257's own plan found in the `-0x25A4` hangar-bay-deref-guard family (`G30`/`G31`); soak shows real forward progress even though the targeted guards got 0 fires.** Full detail: PORTING-STATE Session 258.

-122. **(s257) Mined s256's `guard8soak1` log fully (step 1, no build) -- confirmed it re-proves an already-catalogued signature with nothing new -- then widened the tracer to a genuinely uncovered site instead of burning the 3rd allowed `C_LOADED` null; the re-soak came back null on that question (no positive control this run) but surfaced a 2nd occurrence of a different, already-catalogued whack-a-mole crash blocking progress even earlier.** Full detail: PORTING-STATE Session 257.

-121. **(s256) Closed the 8th `composeNpcOrientationMatrix` gap s255 surfaced, with a real discriminating soak result.** Full detail: PORTING-STATE Session 256.

-120. **(s255) Landed item -49's next tracer-widen step (`C_LOADED`), and re-analysis of s254's OWN already-collected log answered the widen question for `B_LOADED` for free (no build): `ctx->r16` was NOT out-of-bounds right after its initial load on the call that then crashed at `+792` (5th occurrence) -- rules out "already bad at load time" again, points at the `L_80012080` loop-back reload as the next place to check (that site's existing check only validates the SOURCE address of the reload, never the reloaded RESULT -- same source-vs- value gap `B_LOADED` already closed for site B).** Full detail: PORTING-STATE Session 255.

-119. **(s254) Re-ran s253's prescribed re-soak, got a discriminating answer, found and closed a real upstream blocker, hit a known bug 27x further in.** Full detail: PORTING-STATE Session 254.

-118. **(s253) Chased the s252 `submitSceneNodeRender+18600` lead.** Full detail: PORTING-STATE Session 253.

-117. **(s252) Closed the `heapFreeListDequeue` lead NEXT.md flagged: full ~1758-line read (this time genuinely start-to-end, not just the guarded loop) found a real gap the static self-ref-walk finder can't see.** Full detail: PORTING-STATE Session 252.

-116. **(s251) Finished guarding all 3 of `reserveAndEmitDLEntry`'s flagged tail-walk candidates (`funcs_3.c`, the 3 near-identical "find insertion tail" loops at 0x8000CBE8/0x8000CCE4/0x8000CDF0) — the s169 free-list- pop guards already validated each loop's ENTRY pointer, but the walk's immediate peek-load of the freshly-walked (never-before-dereferenced) result was unguarded; traced end to end and confirmed only ONE guard per site is needed (not two, unlike `selectPostCrawlCraft`'s s250 helpers) since the walk's own input is always already-validated by either the s169 guard (iteration 1) or this new guard one iteration earlier (iteration N+1).** Full detail: PORTING-STATE Session 251.

-115. **(s250) Finished guarding all 3 of `selectPostCrawlCraft`'s s249-flagged candidates (`funcs_30.c`, 0x800CBDA8 + 0x800CBDE4 — two near-identical inlined doubly-linked-list "insert at tail" helpers): each got TWO guards (walk + peek-load), matching `renderUnlitMeshFaces`'s s219 GUARD/GUARD3 shape, not `selectPostCrawlCraft`'s own single-guard template — the loop dereferences the SAME register twice back-to-back (self-ref walk, then an unvalidated peek-load of the freshly-walked value), unlike s249's two-different-aliased-registers case.** Full detail: PORTING-STATE Session 250.

-114. **(s249) Started the project-wide static sweep for the "RDRAM-base + un-subtracted wild pointer" whack-a-mole family (s248's option 1): landed a candidate-finder script (143 unguarded-list-walk sites across 43 functions, `scratch/agent/find_unguarded_walks.py` / `unguarded_walk_candidates.json`) and fixed ONE of them (`selectPostCrawlCraft`, `funcs_30.c`, 0x800CBBD8), chosen because its name matches the "SELECT-CRAFT" transition marker this project has used for 30+ sessions.** Full detail: PORTING-STATE Session 249.

-113. **(s248) Corrected a stale NEXT.md premise (its "option 2," the NaN_CHECK-disable pivot, was already tried+reverted at s216/-57, not "unshipped" as claimed) and ran the 3rd consecutive MTL_DEBUG_LAYER=1 soak (`mtldebug4`) — inconclusive for the CALayer question a 3rd time, triggering NEXT.md's own budget-rule-8 pivot condition.** Full detail: PORTING-STATE Session 248.

-112. **(s247) Corrected a wrong s246 premise and added a 2nd clean `MTL_DEBUG_LAYER=1` family-tally data point past the SELECT-CRAFT-> mission transition — CALayer SIGSEGV family now 2/2 survived under the stricter instrument (vs. 5/10 survived without it).** Full detail: PORTING-STATE Session 247.

-111. **(s246) Implemented + soak-confirmed s245's preferred fix (b) for the scissor-rect out-of-bounds Metal SIGABRT — CLOSED, two independent positive controls, CRASH: 0.** Full detail: PORTING-STATE Session 246.

-110. **(s245, SUPERSEDED by s246's fix landing — kept for mechanism detail) Static-traced s244's new scissor-rect Metal SIGABRT to a confirmed mechanism — H2+H3 CONFIRMED, H1 refuted-and-refined, no soak needed to discriminate (two static code paths converge).** Full detail: PORTING-STATE Session 245.

-109. **(s244) Landed the `fbSize()==0` guard in `rt64_vi_renderer.cpp` (skip the VI draw for that frame) and re-soaked (`mtldebug2`) — H1 CONFIRMED with a same-run positive control: the exact `osViSetMode #12`/`viW=0` trigger point that produced s243's fatal `Viewport Validation` NaN assertion now logs `[vi zero-size guard] skipping VI draw, fbSize=(0,0)` twice and the game proceeds cleanly (assertion count 0 in the full `run.log`).** Full detail: PORTING-STATE Session 244.

-108. **(s243, SUPERSEDED by s244's fix landing — kept for mechanism detail) `MTL_DEBUG_LAYER=1` soak (`mtldebug1`) found a NEW, distinct crash — a Metal viewport-validation SIGABRT (`viewport.originX/Y/ width/height must not be infinite or NaN`) at guest decision `n=4421`, far earlier than the `n=12420` host-CALayer-teardown SIGSEGV family this soak was meant to probe.** Full detail: PORTING-STATE Session 243.

-107. **(s242) Ran the clean `malloclog2` re-soak — `CRASH: 0`, no crash to analyze, and no `malloc`-related output at all appeared in `run.log` even from the game process itself (MSL/scribble apparently print nothing to stdout/stderr on this macOS version absent a `malloc_history`-style query, which s241 already found unreachable in this sandbox).** Full detail: PORTING-STATE Session 242.

-106. **(s241) Stood up Apple malloc debug tooling per s240's plan, but the first soak (`malloclog1`) was CONFOUNDED and the "query `malloc_history`" half of the plan is UNREACHABLE in this sandbox — fix landed, clean re-soak (`malloclog2`) staged, not yet run.** Full detail: PORTING-STATE Session 241.

-105. **(s240) Instrumented and soaked `MetalSwapChain::resize()` — the s239 cross-thread `CAMetalLayer::setDrawableSize` race hypothesis is now REFUTED, with two independent lines of evidence.** Full detail: PORTING-STATE Session 240.

-104. **(s239) Static read of `lib/rt64/src/contrib/plume/plume_metal.cpp` + `rt64_present_queue.cpp` for the s238 host-CALayer-crash hypothesis — found one concrete, narrow, PLAUSIBLE-not-CONFIRMED candidate: a cross-thread `CAMetalLayer` property mutation.** Full detail: PORTING-STATE Session 239.

-103. **(s238) 3rd consecutive crashed `campose*` soak (`campose14`) — iron rule 8 budget spent, no more blind re-soaks — but this crash is a NEW kind: a HOST-side SIGSEGV inside Apple QuartzCore (`x_hash_table_remove_ptr`<-`CAMediaTimingInvalidate`<-`-[CALayer dealloc]`<-`CA::Transaction::commit`, reached via the SDL event pump inside `update_gfx`), not the guest-code SIGBUS family seen in `campose10`/`12`/`13`.** Full detail: PORTING-STATE Session 238.

-102. **(s237) Re-soaked the validated `[campose-entry]` `t=` instrument (`campose13`, tag-bump-only copy of `run_campose12.sh`) — crashed again before the hold window, the 2nd consecutive no-result soak, but with a DIFFERENT crash signature than `campose12`/`campose10`.** Full detail: PORTING-STATE Session 237.

-101. **(s236) Landed the `t=` wall-clock field on `[campose-entry]` (`ROGUESQ_LOG_CAMPOSE`, `0x800178A8`, `fixup_game_funcs.py`) that -76 called for, and positive-control-validated it** Full detail: PORTING-STATE Session 236.

-100. **(s235) Ran the payoff soak (`campose11`) the wall-clock/`hold_N` bridge (s234) was built for.** Full detail: PORTING-STATE Session 235.

-99. **(s234) Landed and positive-control-validated the wall-clock/hold_N bridge s233's NEXT.md called for, but the single validation soak crashed at the known-fragile SELECT-CRAFT->mission transition (~74.5s) before reaching the hold window, so the actual staleness-vs-freeze correlation still has not run.** Full detail: PORTING-STATE Session 234.

-98. **(s233) Closed off s232's Option B (static-data classification of the disputed `0x80332xxx` address pool) as impossible — it's unambiguously runtime heap, ~1.8MB past every static ELF section (max `0x80154690`, `scratch/agent/elf_segments.py`) — and landed+soak-validated Option A (a per-content-pointer staleness tracker, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`, same `funcs_4.c:13918` anchor) across 2/2 budgeted soaks.** Full detail: PORTING-STATE Session 233.

-97. **(s232) Landed Probe B (DL-emission payload hash diagnostic) and ran it clean — SELECT-CRAFT->mission transition survived (0 crashes) when NOT arming the epoch diagnostic, confirming s231's framing — but the payload-hash signal itself is ambiguous, not yet a finding.** Full detail: PORTING-STATE Session 232.

-96. **(s231) Refutes s230's "diagnostic I/O overhead" hypothesis with two independent attempts; the SELECT-CRAFT->mission VI transition (~73-74s) is independently fragile and 0/4 epoch-armed soaks have survived it.** Full detail: PORTING-STATE Session 231.

-95. **(s230, superseded in priority by s231 above — kept for the trail) Landed a render-cache "epoch" diagnostic in `processSceneNode` (RDRAM global 0x8011A894, `funcs_4.c:13881-13890`/`:14732-14751`, env var `ROGUESQ_LOG_RENDER_CACHE_EPOCH=1`) and confirmed it fires and shows the epoch is a LIVE, actively-changing value early in a run (not stuck) — but BOTH soak attempts with it armed crashed near the SELECT-CRAFT→mission VI transition (~73s), before reaching the freeze window (`n=15360`+).** Full detail: PORTING-STATE Session 230.

-94. **(s229, superseded in priority by s230 above — kept for the trail) Permission gate CLEARED (s228's fix confirmed working) — `deref0` soak-validated: it does NOT freeze near `flag`/`camptr`'s freeze point (`n=15360`), and keeps changing until `n=57900`, far longer than `m00`'s own already-documented lag (`n=21240`).** Full detail: PORTING- STATE Session 229.

-93. **(s228, RESOLVED s229 — kept for the trail) BLOCKED, 3rd consecutive session — the gate is NOT specific to `tools/:*`; it's a whole class of allow rules (`Bash(<dir>/:*)`, a bare directory ending in a slash) failing, while `Bash(<word>:*)` rules work fine.** Full detail: PORTING-STATE Session 228.

-92. **(s227, superseded by s228 above — kept for the trail) BLOCKED, 2nd consecutive session: `Bash(tools/:*)`/`Bash(./tools/:*)` allow rules are not authorizing matching commands this session, and the gate is confirmed broad (any `tools/`-prefixed script), not specific to `regen_n64recomp.sh`.** Full detail: PORTING-STATE Session 227.

-91. **(s226) s225's "two fixed scene-root pointers" are NOT independent globals — source trace shows both derive from the SAME camera struct s223/s224 already instrumented, and reanalysis of s224's OWN already- captured log (no new soak needed) shows the struct's `+0x0` linkage field freezes in lockstep with the struct address itself at the exact checksum-confirmed picture-freeze point, while the struct's `+0x2C` rotation submatrix (same struct, same cadence) does NOT — proving "reads a fixed address" doesn't imply "frozen value" and weakening the upstream-simulation-tick-stopped hypothesis for this specific field.** Full detail: PORTING-STATE Session 226.

-90. **(s225) The whole scene-graph chain (`traverseSceneGraphRecursive` -> `processSceneNode` -> `submitSceneNodeRender`) keeps firing at a steady rate through the ENTIRE visibly-frozen window — this rules out a scene-traversal stall as the wedge — AND, unplanned, the RDP full-sync counter (`rdpFs`) keeps climbing for nearly all of the same window in this run, overturning s224's "RDP full-sync also frozen" framing on a single-run basis.** Full detail: PORTING-STATE Session 225.

-89. **(s224) Answered NEXT.md's discriminating question: the camera's own raw pose field (`setupCameraMatrices`'s `+0x2C` submatrix `m00`, read directly, not the mat3x3InverseInto-derived inverse) keeps changing for ~60s of process time AFTER the picture (and RDP full-sync counter) have already frozen — this is a downstream scene-graph/render- submission freeze, NOT a stuck camera.** Full detail: PORTING-STATE Session 224.

-88. **(s223) Refuted the `mat3x3InverseInto`/`setupCameraMatrices` `+0x2C` determinant hypothesis with a well-controlled null (456k+ firings spanning the whole hold, determinant genuinely varying but never 0/Inf/NaN) — AND, unplanned, an exact re-run of s222's own `schedulepush2` script reached real space-combat mesh content plus the opening crawl (2nd time ever, matching s154's milestone) before freezing on a flat ground-color fill, refuting s222's "no soak has ever reached mesh-heavy content" as universal and proving run-to-run non-determinism on byte-identical scripted input.** Full detail: PORTING-STATE Session 223.

-87. **(s222) 4th consecutive null closes the "schedule density" hypothesis for good — checksum-verified, the on-screen picture freezes on a degenerate-polygon frame ~4s after leaving SELECT YOUR CRAFT and NEVER changes again for the remaining ~340s, crash-free, no matter how much scripted input follows.** Full detail: PORTING-STATE Session 222.

-86. **(s221) Closed the actual gap behind s220's `emitAllocatedDLCommand` hold-iter-1 crash — not a new bug, a 15+-session-old guard mechanism (s133) that only covered 2 of the function's 3 identical unguarded copies.** Full detail: PORTING-STATE Session 221.

-85. **(s220) Re-soak of `renderunlitguard1` (unchanged script, tag `renderunlitguard2`) leaves item -60's guard question STILL unconfirmed (`unlit-mesh-tracer`/`renderunlit-guard` both 0/0 a 2nd time), but surfaces a higher-value new lead: a 4th independent consumer of the same "raw KSEG0 guest pointer + rdram-base constant, no `MEM_W` subtraction" fault family, in `emitAllocatedDLCommand` (`funcs_3.c:2622-3210`), hit at hold-iter 1 (earliest death in the whole s209-219 lineage) while rendering the SELECT YOUR CRAFT hangar/camera-orbit scene itself — i.e. plausibly BEFORE the hold schedule's `95:start` key (documented to leave craft-select into flight) ever gets to fire.** Full detail: PORTING-STATE Session 220.

-84. **(s219) REFUTES item -59's "hunt the write site of 0x0000000300000000" premise — that value is the constant native RDRAM host base pointer, not corrupted data; there is no write site.** Full detail: PORTING-STATE Session 219.

-83. **(s218, corrected s219 — see -60) heapWalker GUARD4 landed (5 sites, the actual gap GUARD3 left open) — heapWalker signature didn't recur (hold-iter 28, far past s217's iter 1), but a THIRD independent sighting of the exact corrupt literal `0x0000000300000000` surfaced in a totally unrelated subsystem (scene-graph rendering).** Full detail: PORTING-STATE Session 218.

-82. **(s217) heapFreeListDequeue source-read done and guarded (4 sites, class-A upstream-propagation, high confidence) — but the soak never reached that code, dying instead to a RECURRENCE of the established `heapWalker`/`frameStartReset+532` signature at the earliest point of the entire s209-217 lineage (hold-iter 1, wall=0s), with the existing 10-site heapwalker guard still 0/0.** Full detail: PORTING-STATE Session 217.

-81. **(s216) NAN_CHECK-disable A/B soak ran: confirms the mechanism works (0 asserts) but REFUTES it as the dominant blocker — died even earlier (hold-iter 9) to a genuinely new SIGBUS. NAN_CHECK is back ON.** Full detail: PORTING-STATE Session 216.

-80. **(s215, A/B-tested s216 above — NAN_CHECK reverted, see -57) do_send SIGBUS reclassified: NOT the s176+ scheduler-UAF family — a mesgqueue guard is now shipped but untested live; the bigger lead is disabling `NAN_CHECK` project-wide.** Full detail: PORTING-STATE Session 215.

-79. **(s214, do_send framing here SUPERSEDED by -56 above) heapWalker's upper-32-bits guard fix SHIPPED (10/10 sites, confirmed patched in generated `funcs_3.c` before building) but is still UNTESTED live — 2 soaks in a row hit unrelated crashes before reaching heapWalker at all, so the mechanism is neither confirmed nor refuted.** Full detail: PORTING-STATE Session 214, superseded in part by Session 215.

-78. **(s213, PARTIALLY ADDRESSED s214 above — see -55; guard code now ships the upper-bits check this item asked for, but the live-fire test itself is still pending) 4th soak (deliberately varied recipe, dropped early sticks per -53) hit a genuinely NEW crash — `heapWalker+1128` — and, cross- referenced against the s99/s157/s172 guard history and a fresh source read of `recomp.h`, this crash's register shape PROVES a generalizable, project-wide blind spot in every existing `U32(ctx->rN)`-truncated guard, not just a heapWalker-specific gap.** Full detail: PORTING-STATE Session 213.

-77. **(s212) Offline cross-reference of s210/s211 logs REFUTES the "shared ~60-75s trigger" hypothesis from -52 below — clean Outcome B, no 3rd confirming run needed.** Full detail: PORTING-STATE Session 212.

-76. **(s211, SUPERSEDED s212 above — see -53; "shared trigger" question now CLOSED, not open) 3rd consecutive session (s209/s210/s211) whose only soak attempt at reaching `renderUnlitMeshFaces` failed for a DIFFERENT reason each time — 0/4 total soaks across these 3 sessions have produced a live measurement of the `ctx->r16` question.** Full detail: PORTING-STATE Session 211.

-75. **(s210, SUPERSEDED s211 above — see -52) s209's ~47x log-volume blowup is CONFIRMED self-inflicted logging overhead, not a real regression — but the minimal-logging re-soak crashed on a NEW, previously-unseen bug (`evalCubicSplineAtTime+1008` SIGBUS) before ever reaching `renderUnlitMeshFaces`, so the `ctx->r16` question below is STILL unresolved.** Full detail: PORTING-STATE Session 210.

-74. **(s209, RESOLVED s210 — see -51 above) Both soaks that session hit a
    reproducible ~47x log-volume blowup (`rs-free-walk` lines: 1.98M
    baseline vs 104.8M/172.1M, same script/duration) that appeared to
    prevent the craft-select/hangar scene from ever being reached — 0
    `renderUnlitMeshFaces` calls logged in either retry, including the
    always-on-at-call-1 positive control. s210 confirmed this was
    self-inflicted logging overhead (stripping the verbose diagnostics let
    the scene get reached normally), not a real behavioral regression. Full
    detail: PORTING-STATE Session 209.

-73. **(s208, STATUS: s262 added `renderUnlitMeshFaces` GUARD2 for a newly-found pre-loop peek-load gap (0x80011CD0, the same shape s219 fixed for the loop's back-edge but missed pre-loop) — UNVERIFIED, not refuted: the soak that carried it never called `renderUnlitMeshFaces` at all (0/0 positive control), dying instead to a recurrence of the unrelated, longer-standing "18th crash class" upstream in `submitSceneNodeRender`.** Full detail: PORTING-STATE Session 208.

-72. **(s207, SUPERSEDED framing — see -49 above for what's current)** Full detail: PORTING-STATE Session 207.

-71. **(s198) 3rd consecutive clean pass through the 18th class's death zone (still no positive control for the s197 guard) — 18th class reclassified "very likely fixed, mechanism unconfirmed"; a 2nd occurrence of the s192/s193 `runVideoFrameTick+1568` SIGBUS promotes it to the new dominant, top-priority blocker.** Full detail: PORTING-STATE Session 198.

-70. **(s197) found and guarded the one dereference in the 18th-crash-class free-list idiom that bypasses GUARD/GUARD2/GUARD3 entirely (the cached-free-list-head pop at `funcs_4.c` `L_800101AC`, taken when the global free-list cache is non-empty at entry — skips `findAndUnlinkSmallestEntry` and all 3 existing guards).** Full detail: PORTING-STATE Session 197.

-69. **(s196) landed the 13th-class `reinterpretTileRecord` guard (mirrors s192's `queueGPUUploadTMEM` pattern exactly) — but the soak never reached it, dying instead to a FRESH recurrence of the long-standing 18th crash class even earlier in decisionN, which is now the dominant blocker.** Full detail: PORTING-STATE Session 196.

-68. **(s195) re-ran s194's mcontext soak for a 2nd occurrence — s194's `processSceneNode`-adjacent crash did NOT recur; instead the soak died to a DIFFERENT, older catalogued crash (13th class, `reinterpretTileRecord`, parked at s96 "until 2nd recurrence") which just got exactly that 2nd occurrence, ~99 sessions later, byte-for-byte identical backtrace.** Full detail: PORTING-STATE Session 195.

-67. **(s194) disassembly tools confirmed still blocked (otool/objdump both denied approval again) — pivoted instead to fixing the crash handler itself, which turned out to be discarding its own best evidence.** Full detail: PORTING-STATE Session 194.

-66. **(s193) closed the "-41" open question — the s192 `queueGPUUploadTMEM` guard is now confirmed live via a positive control — but the `runVideoFrameTick` crash from s192 is STILL uncatalogued and unguarded, and remains the current blocker on any soak reaching the scene-node-ptr-guard's 9660-9792 target window.** Full detail: PORTING-STATE Session 193.

-65. **(s192) landed the `queueGPUUploadTMEM` zero-size defensive guard (`ROGUESQ_LOG_TMEM_ZERO_GUARD`, `lib/rt64/src/render/ rt64_texture_cache.cpp:1284`) that -40 recommended, but a soak with it active never exercised it** Full detail: PORTING-STATE Session 192.

-64. **(s191) re-ran the fixed `sceneptrguard` soak a 2nd time (`sceneptrguard4`, byte-identical config to s190's `sceneptrguard3`) — died again before the 9660-9800 target window (decisionN=7897, even earlier than s190's 8053), but to a DIFFERENT already-catalogued crash this time, which refutes `reserveAndEmitDLEntry` as a specific recurring blocker.** Full detail: PORTING-STATE Session 191.

-63. **(s190) landed the missing `processSceneNode` node-pointer guard (`ROGUESQ_LOG_SCENE_NODE_PTR_GUARD`, `N64Recomp/fixup_game_funcs.py`), but its effectiveness against the target self-recursion bug is still untested** Full detail: PORTING-STATE Session 190.

-62. **(s189, corrects -37's clustering claim): surveyed crash-time `decisionN` across ALL 16 historical soak logs instead of running a new soak (NEXT.md's recommended path (B)) — the "4 unrelated crash families cluster near 9770-9792" framing does not survive the full dataset, but a stronger signal was hiding in it: the `processSceneNode` crash that ended s188 is not new, it's the SAME bug recurring a 3rd and 4th time.** Full detail: PORTING-STATE Session 189.

-61. **(s188, clustering claim in this item corrected by -38 above — kept for the instrument/no-starvation finding, which still stands) landed the periodic `[sched-tick]` readout s187 called for, ran one soak (`schedtick1`): decisionN/queueN/runnextN climbed in lockstep with NO stall signature the entire run** Full detail: PORTING-STATE Session 188.

-60. **Landed the mandatory-pivot defensive guard on `rs_free`'s free-list walk (s187) — validated with a strong positive control, first fully crash-free full-length soak in the whole s180-187 lineage.** Full detail: PORTING-STATE Session 187.

-59. **`ROGUESQ_LOG_SCHED` instrument's rule-8 budget is now CLOSED (s186): 3 of 3 attempts spent, all inconclusive for candidate (a).** Full detail: PORTING-STATE Session 186.

-58. **(s182): re-attempted the stall repro now that the `FramebufferStorage::store` OOB-read crash (found this session) no longer preempts it; the nearest remaining obstacle is a non-deterministic, already-catalogued Metal-internal shader-compiler SIGSEGV (s83/s96 lineage, no source on our side).** Full detail: PORTING-STATE Session 182.

-57. **(s181): reach the stall again with the new `[thr-create-id]`/`thr=%p` instrument armed (always-on already), then cross-reference the `[thr-resume-skip] thr=%p` value against this run's `[thr-create-id]` lines to learn which specific thread was dropped.** Full detail: PORTING-STATE Session 181.

-56. **(s180, refined by s181 above): design a fix or targeted instrument for the scheduler silent-drop mechanism.** Full detail: PORTING-STATE Session 180.

-55. **(s179, superseded as top priority by s180 above): the `schedcaller`-shape soak, now closed after its 3rd attempt (see -32 above).** Full detail: PORTING-STATE Session 179.

-54. **(s178, superseded as top priority by s179 above): find and instrument the caller/scheduler of `runHangarSelectionFrame`.** Full detail: PORTING-STATE Session 178.

-53. **(s177, superseded as top priority by s178 above): re-run the `swapackwait1` soak recipe to actually catch the graphics-task-submission stall with the new producer-side instrument armed.** Full detail: PORTING-STATE Session 177.

-52. **(s176, superseded as top priority by s177 above): 2nd consecutive full-hold crash-free soak (`scenenodedepthguard2`, exact repeat of s175's recipe, new tag only) — still 0/0 on every guard in the family, including the new depth-cap guard.** Full detail: PORTING-STATE Session 176.

-51. **(s175, superseded as top priority by s176 above): source-read `processSceneNode`'s self-recursion and guarded it with a recursion-depth cap** Full detail: PORTING-STATE Session 175.

-50. **(s174, superseded as top priority by s175 above): source-read `tickMusyXIfActive`'s 5 callees found and guarded the 23rd crash class's 2nd bug** Full detail: PORTING-STATE Session 174.

-49. **(s173, superseded as top priority by s174 above): landed and validated the `rs_malloc` walk-loop deref guard NEXT.md asked for (`N64Recomp/fixup_game_funcs.py`, `ROGUESQ_LOG_RS_MALLOC_WALK_GUARD`, file-scoped `funcs_0.c`), but 2 soaks show it isn't this run's dominant early crash: 0/0 fires despite 17,683 clean `rs_malloc` calls (real negative control), one soak died to the already-catalogued s83 Metal-internal shader-compiler SIGSEGV (unrelated, no source on our side), the other died to a** Full detail: PORTING-STATE Session 173.

-48. **(s172, superseded as top priority by s173 above): fixed a real gap in the heapWalker guard (missing 5th head-deref site + all 5 walk-loops completely unguarded, `N64Recomp/fixup_game_funcs.py`/`funcs_3.c`) — 2 soaks show 0/0 on both new guards (heapWalker isn't the culprit either soak), but each soak surfaced a *different*, newer, better-characterized crash instead of heapWalker's own bug: soak 1 survived to hold-iter 27 (longest crashing soak of this family yet) then SIGBUS in `processSceneNode` (self- recursive, via `traverseSceneGraphRecursive`/`setupCameraMatrices`, `funcs_4.c:13759-14861`, not yet source-read); soak 2 died at hold-iter 1 to SIGBUS** Full detail: PORTING-STATE Session 172.

-47. **(s171, superseded as top priority by s172 above): landed the crash-instant `[vi-fs-decision]` snapshot s170 asked for (`rs64_get_vifs_crash_snapshot`, always-on, no env var — `lib/rt64/src/hle/rt64_state.cpp` + `src/main/main.cpp`), but 3 soaks of the same recipe (0/3) never reproduced the target scheduler SIGSEGV — instead hit 2 different, earlier-position crashes (a new, not-yet-characterized `submitSceneNodeRender+16780` site, and a recurrence of the old `frameStartReset`/`heapWalker`-inlining class whose guard still never fires) plus one crash-free full hold.** Full detail: PORTING-STATE Session 171.

-46. **(s170, superseded as top priority by s171 above): the s169-soak-2 runtime-scheduler SIGSEGV recurred a 2nd time (soak 3/3 of the same recipe) — closes the 14th- class pop-guard question (item -21 below, 0/3, tentatively-fixed- unconfirmed) and opens this as the live frontier.** Full detail: PORTING-STATE Session 170.

-45. **(s169, superseded as top priority by s170 above — 14th class closed 0/3, tentatively fixed but never validated with a positive control):** Full detail: PORTING-STATE Session 169.

-44. **(s168, superseded as top priority by s169 above): landed the `rs_free` free-list walk-log NEXT.md prescribed (mirrors s165's `rs_malloc` walk-log exactly, `ROGUESQ_LOG_RS_FREE_WALK=1`, `N64Recomp/fixup_game_funcs.py`, `funcs_0.c`).** Full detail: PORTING-STATE Session 168.

-43. **(s167, still valid background, superseded as top priority by s168 above): re-ran `run_audioslotguard1.sh` unmodified per s166's own plan — it did NOT stay crash-free. 2nd run died at hold-iter 96 (task #7452, fs plateau 4163) to a brand-new** Full detail: PORTING-STATE Session 167.

-42. **(s166, superseded as top priority by s167 above): source-read found and guarded a concrete unguarded-pointer deref (`isAudioSlotActive`, `funcs_24.c:5788` — base pointer from a fixed global slot, indexed, dereferenced with no null-check, the family's dominant shape) matching the 23rd crash class's call chain.** Full detail: PORTING-STATE Session 166.

-41. **(s165, superseded as top priority by s166 above): landed the `rs_malloc` free-list walk-log (`ROGUESQ_LOG_RS_MALLOC_WALK=1`, `N64Recomp/fixup_game_funcs.py`, file-scoped `funcs_0.c`, logs node addr/flags/size at `L_80001BEC` before the advance) and ran the 3rd/final `audiodrain` attempt (`audiodrain3`).** Full detail: PORTING-STATE Session 165.

-40. **(s164, superseded as top priority by s165 above, mechanism still live): audio-drain soak attempt 2/3 (`audiodrain2`) died even earlier than attempt 1 (hold-iter 2 vs hold-iter 6), NOT to a recurrence of `emitAllocatedDLCommand` but to a brand-new, never-before- seen 22nd crash class — SIGBUS inside `rs_malloc` itself (the guest heap allocator), called from `rebuildActiveDisplayObjectList` with fixed, sane arguments (`size=1024 flags=0`) identical to 14 immediately-prior successful calls the same run.** Full detail: PORTING-STATE Session 164.

-39. **s163: source-read found a concrete 3rd mechanism for the s162 stall (an unbounded audio-drain spin loop in the cutscene's own teardown path), instrument landed and validated, but the soak died even earlier than usual to a recurrence of the already-`parked` (s135) `emitAllocatedDLCommand` crash before ever reaching the stall window — zero data obtained on the actual question.** Full detail: PORTING-STATE Session 163.

-38. **NARROWED by s176 (see -28 above): the stall's onset is not fixed to the post-leave cutscene — a same-recipe soak can also freeze pre-leave, still inside SELECT YOUR CRAFT.** Full detail: PORTING-STATE Session 176.

-37. **s161: two-source rule satisfied on "survives the menu-transition + hangar-tick hold" — SUPERSEDED as the active frontier by s162 above, but still true as far as it goes.** Full detail: PORTING-STATE Session 161.

-36. **s159/s160: the 21st crash class, `drawSubtitleText`, has a landed
    guard now corroborated by 2 independent crash-free soaks (s160, s161)
    — see -13.** Still not proven the guard is *why* (0/0 positive control
    on the guard itself across both runs), but the outcome-level two-source
    rule is satisfied. Do not re-run this exact soak a 3rd time without a
    new, specific reason (see -13).

-35. **s159/s160: the 21st crash class, `drawSubtitleText`, has a landed guard corroborated by 2 crash-free soaks — see -13.** Full detail: PORTING-STATE Session 159.

-34. **s159: proved by full source read that the 15th crash class (`loadDrawState` zero-sample-size assert) cannot be caused by ANY guest-supplied tile field** Full detail: PORTING-STATE Session 159.

-33. **s157/s158: `composeNpcOrientationMatrix`'s (12th class) 7th
    unguarded site found and guarded** (`funcs_40.c:6901-6904`,
    `ROGUESQ_LOG_COMPOSE_NPC_GUARD7`) — landed, built clean, but
    **unvalidated** (0/0, the function never crashed in the s158 soak;
    see -10 above for why). s157 also found + guarded 4 new sites in
    `heapWalker` (`ROGUESQ_LOG_HEAPWALKER_GUARD`) — still unvalidated
    after 2 soaks (s157, s158) not exercising the crash path. Neither
    0/0 result is evidence the guards are wrong; both remain dormant
    until a soak's actual crash routes through them again. Full detail:
    PORTING-STATE s157/s158.

-32. **s156: refuted the "shared corrupted dispatcher" hypothesis for `static_5_800AAD9C`** Full detail: PORTING-STATE Session 156.

-31. **s155: guarded the 20th class (`loadCraftShadowTextures`,
    `N64Recomp/RecompiledFuncs/funcs_16.c:13038-13051`, bounds the
    craft-type index to 0-13 against the 14-entry sentinel table at
    `0x8013A528`) — landed, verified x1, still unvalidated (0/0 across
    2 soaks now, s155 and s156) because the process keeps dying earlier
    in the same war-room/craft-select window to other classes.
    `composeNpcOrientationMatrix`'s 5th/6th sites (s155's candidate)
    confirmed and guarded, see -8 above.

-30. **s154: the "does the FULL_SYNC-loss freeze recover" question is ANSWERED — yes, at least once — and a new, 20th crash class blocked further progress (now guarded, see -7 above).** Full detail: PORTING-STATE Session 154.

-29. **s153: the crawl-scene hang IS confirmed the same class as s79/s80's FULL_SYNC-loss (item 1 from s152 is now closed); the "does it ever recover on a long hold" question is still open — the soak built to test it got preempted by an early, unrelated crash before reaching the target window.** Full detail: PORTING-STATE Session 153.

-28. **s152: the s151 crash at this exact scene did NOT recur — instead the process HUNG, and the hang looks like the already-characterized s79/s80 FULL_SYNC-loss class recurring in a new window, not a fresh mystery.** Full detail: PORTING-STATE Session 152.

-27. **s151: a genuinely NEW post-hangar scene appeared for the first time in ~150 sessions — a "STAR WARS" logo + scrolling- crawl-style intro — before crashing again ~6s later.** Full detail: PORTING-STATE Session 151.

-26. **s150: "single Start leaves SELECT YOUR CRAFT into hangar-flight" (s75/s76) is OVERTURNED — mission-entry is unanswered again.** Full detail: PORTING-STATE Session 150.

-25. **CLOSED (s147, reconfirmed s148):** the count-then-pointer-store race in
    `allocateSongChannelArray` (Thread B's root cause) is fixed and verified -- relocated the early
    `voiceCount` write to run after the pointer-store block (`N64Recomp/fixup_game_funcs.py`). 3
    independent verification soaks (`countracefix1-3`) all clean: 0/13 corrupted
    `[voice-active-gate-nz]` reads post-fix (vs. 5 pre-fix) and 0/3 `do_rom_read` recurrences (vs. 9
    prior occurrences) -- the first fully crash-free full soaks for this repro shape since s83.
    **s149 bonus finding**: "what input leaves SELECT YOUR CRAFT" is not actually open -- screenshots
    from the same soak show the leave transition fires correctly (invisible to VI-phase tracking, same
    0x6AB400 origin pair s48 established); the real open question was always what the post-leave scene
    is and surviving its first ~2s, where the wider hangar-tick crash family (catalogued elsewhere in
    this list) keeps landing. `reserveAndEmitDLEntry` stood at 1/4 non-recurring across the
    countracefix battery -- parked, not guarded (didn't clear the "reachable and recurring" bar). Full
    detail: `PORTING-STATE` Sessions 147-149.

-24. **CLOSED (s135): `emitAllocatedDLCommand` soak hypothesis parked, 3-attempt
    budget exhausted per rule 8.** s133 -> environment-side Apple-Metal SIGSEGV; s134 -> 18th-class
    recurrence; s135 -> the separately-tracked `do_rom_read`/`piDmaWorker` corruption SIGSEGV. Guards
    `emit-dl-guard2`/`3` never fired (0/0 all 3 attempts) but both stay in the code (real fixes,
    independent of this question). Full detail: `PORTING-STATE` Session 135.

-23. **PARKED at 2/3 (s136-s137): `submitSceneNodeRender` material-batch-list guard
    (`MATLIST_GUARD1`/`GUARD2`).** Two soaks, both 0/0 on the new guards (uncontrolled null both
    times), both dying to the tracked `do_rom_read`/`piDmaWorker` corruption race. Both guards stay in
    the code regardless. Full detail: `PORTING-STATE` Sessions 136-137.

-22. **CLOSED (s147, see item above): Thread B, the audio-corruption pivot
    (`voice+0x0`/`+0x34`), longest-running open thread -- fix landed and verified.** Path to the fix
    (s138-146): ruled out a static ROM string table (s138, ~20MB away, unreachable); found 3 then
    narrowed to 2 candidate heap-adjacent allocations via `rs_malloc`/`rs_free` instrumentation
    (s139-140); named the real candidate as `allocateSongChannelArray`'s own second allocation, not
    heap-adjacency at all (s141); found it's one slot of a double-buffered pointer table selected by a
    per-tick toggle byte, with real producer/consumer functions in `funcs_24.c` (s142-143); found the
    actual bug -- `musyxMixActiveVoices` writes via an unchecked cursor with no capacity comparison,
    though never proven to be the `+0x34` writer directly (s144); s145 found the real mechanism:
    `allocateSongChannelArray` writes the new `voiceCount` to the scan-bound global *before* calling
    `rs_malloc`/storing the new pointer, a non-atomic pair with no lock, letting the
    concurrently-scanning audio thread see the new count against the still-old array -- fixed and
    verified s147/148 (see item above). Full detail: `PORTING-STATE` Sessions 138-147.

-21. **s139: landed the `rs_malloc`/`rs_free` range-overlap measurement that
    narrowed Thread B's candidate allocations from the whole heap to 3 named boot-time pointers**
    (superseded by s141's more precise identification -- see item above). Confirmed the voice array's
    per-slot stride is 136 bytes and that observed corruption hits are past the array's actual
    malloc'd length, not just past an abstract count. Full detail: `PORTING-STATE` Session 139.

-20. **Regen-pipeline reliability bug (s120, confirmed intermittent not deterministic --
    s121/s126 both ran clean 3-cycle repeats).** Root cause: `N64Recomp` skips rewriting any
    `RecompiledFuncs/funcs_*.c` file that already exists on disk, so any patch whose regex anchor
    survives its own insertion (true of every patch here) stacks a duplicate on the next
    `fixup_game_funcs.py` run unless the file is deleted first. Deleting all `funcs_*.c` before every
    regen is mandatory but **not sufficient by itself** -- 2 clean full delete-all cycles and 2 dirty
    ones have both been observed; root cause of the residual intermittency is still unknown.
    **Standing rule**: audit the patch report for anything other than the expected `xN` count after
    every `fixup_game_funcs.py` run, every session, regardless of whether the last cycle was clean -- a
    doubled diagnostic doesn't change game behavior but any conclusion resting on an exact log-line
    count should be treated as provisional until re-verified this way. Full detail: `PORTING-STATE`
    Sessions 120, 121, 126.

-19. **M3 Thread A/B saga (s116-s135), CLOSED -- superseded by the s147/148 fix above.**
    Two parallel investigative threads, both fully resolved:
    - **Thread A** (systematic re-audit of every already-guarded hangar-tick crash class for a
      *second*, unguarded pointer-chase site past the first guard): ran s126-s132 across 8
      previously-guarded functions, found 6/8 had a genuine second gap (all guarded), 2/8 clean.
      Biggest single hit: `updateHangarBayScene`'s `-0x25A4` object-field family, 26 more unguarded
      sites found and guarded in one sweep (s132) -- later resumed and fully closed by the s282-288
      audit lineage (see the top of this list).
    - **Thread B** (`voice+0x0`/`+0x34` audio-array corruption): chased across s116-s145 through
      multiple reframings (uninitialized read -> structured-content corruption -> non-atomic
      `voiceCount`-write-before-pointer-store race) -- real mechanism found s145, fix landed and
      verified s147/148 (see item above). Refuted along the way: stale/unzeroed `rs_malloc` memory
      (s122 -- the array is explicitly zero-initialized at alloc), an out-of-bounds scan index (s121
      -- every observed index was within the live count), an RSP-ucode write (s112 -- wrong ucode
      entirely, the real audio ucode has zero call sites), a computed-offset guest-C store (s113 --
      exhaustive grep found none), and an adjacent-heap-allocation aliasing theory (s122/123 -- the one
      tested candidate's address range never overlapped).
    - **Generalizable methodology lesson**: comparing two instruments' log lines by *file order*
      across different threads is not a valid proxy for real time order (s120's false positive,
      corrected s121) -- cross-thread log correlation needs a shared sequence number, not eyeballed
      adjacency.
    Full detail: `PORTING-STATE` Sessions 116-135.

-18. **M3 Thread B, early phase (s102-s113) -- superseded by the s145/147/148 resolution
    above.** Traced the corrupted MusyX DMA-batch `devAddr` field backward through 5 functions across
    6 sessions before landing on the real writer: `submitDmaRequestBatch`/`musyxSynthFrame` cleared
    (s102, faithful copy/mapping) -> `acquireSampleStreamBlock` refuted (s103, never entered) ->
    `fillSampleStreamRange` identified as the writer, computing `devAddr` from `voice+0x34` (s103) ->
    that field's allocator (`initSampleStreamBlockCache`) cleared, its inputs already corrupted at
    entry (s104) -> traced to a shared struct field read in `musyxRenderVoiceSamples`, `voice+0x34` ->
    `musyxInitVoiceFromSample` identified as the sole writer of that offset anywhere in the 45-file
    recompiled tree (s105, s111 exhaustive grep). The call-chain-ancestry angle (s105-110, "does this
    function even run on this path") was a 5-session dead end, eventually retired -- the code path
    that reads the corrupted value never actually goes through that ancestry chain. Full detail:
    `PORTING-STATE` Sessions 102-113.

-17. **Tooling (s102, root-caused more precisely s120 -- see item above):
    `fixup_game_funcs.py` is not idempotent** -- re-running it without a full ELF regen between runs
    inserts a second copy of every already-applied patch. Harmless (duplicate guards are dead code,
    first copy's `goto` always wins) but bloats generated files. Full detail: `PORTING-STATE` Session
    102.

-16. **M3 hangar-tick-family guard program (s99-s110): 8 crash classes guarded**
    (16th/12th/11th/14th/17th/18th/9th/10th -- see the crash catalog in the item below for names/sites),
    all with clean negative controls, same `U32()`-truncated-bounds-check-then-`goto`-real-epilogue
    template used by every guard in this project since. s101 and s110 are two independent soaks that
    survived the entire family with zero crashes, reaching the ~140s DMA-corruption window alive -- the
    guard program is sufficient to reliably reach that window. Full detail: `PORTING-STATE` Sessions
    99-101, 109-110.

-15. **M3 -- find the indirect caller of `submitDmaRequestBatch`: CLOSED (s101).** The
    caller is `musyxSynthFrame` (`funcs_24.c:3095`, a per-VI-retrace audio tick) via
    `viRetraceHandlerThread` -- not the mission/DL code path every earlier session assumed. Confirmed
    dead ends along the way, do not reopen: `ra=0x00000000` as a corruption signature (refuted s92,
    routine on 487+ calls), "dump the OSIoMesg at mb" (refuted s92, `mb` never dereferenced), consumer
    index desync / external RDRAM stomp (refuted s94), "the boot call loops more than once" (refuted
    s93/94, exactly 1 call site exists).

    **Crash catalog** (19 classes found chasing this window, s83-s110; "guarded" = landed with a clean
    negative control, treat as closed unless noted):

    | # | site | status |
    |---|---|---|
    | 9 | `updateAnimatedTextureStreaming` (funcs_11.c) | guarded s124, 2nd gap found+closed s127 |
    | 10 | `static_5_800B4048` | guarded s125, 2nd gap found+closed s127 |
    | 11 | `projectModelBoundsToScreen` | guarded s101, 2 more args found+guarded s128 |
    | 12 | `composeNpcOrientationMatrix` | guarded s100, 2nd independent loop found+guarded s126 |
    | 13 | RT64-internal, `reinterpretTileRecord` assert | guarded s196 after a 2nd occurrence (s195) |
    | 14 | `reserveAndEmitDLEntry` | guarded s109, confirmed clean s129 |
    | 15 | RT64-internal, `loadDrawState` zero-sample assert | root-caused RT64-internal (s159), guarded |
    | 16 | `activateAnimationKeyframe` | guarded s99, confirmed clean s130 |
    | 17 | fault inside `updateHangarBayScene` itself (5 sites) | guarded s110 |
    | 18 | `submitSceneNodeRender` free-list walk | guarded s123, 9 inlined copies found+reopened s131, root-caused as the `-0x25A4` family and closed via the s282-288 audit lineage |
    | 19 | RT64-internal SIGSEGV, `MetalFramebuffer` ctor via `createTileCopyRecord` | 1 occurrence, not source-read, not recurred |

    Thread A (s126-132, see item above) later found a *second* unguarded site in 6 of the 8 guarded
    functions -- already folded into the table above. Full detail: `PORTING-STATE` Sessions 93-110,
    124-132, 159, 195-196.

-14. **M3 — root-cause/fix the `queueGPUUploadTMEM` zero-size assert.**

-13. **M3 — characterize the 10th crash class, SIGBUS in
   `static_5_800B4048` (s90): CLOSED, guarded s125.** See crash catalog
   and item 0 above.

-12. **M3 — characterize the 9th crash class, `updateAnimatedTextureStreaming`
   SIGBUS (s89): CLOSED, guarded s124.** See crash catalog and item 0b above.

-11. **M3 — `advancePlayerAnimationPhase` SIGBUS: PARKED (s89).** 3
   consecutive non-recurrences since s88 landed the correct instrument
   (s88, animcb2, animcb3) against 8 total crashing soaks since s83. Do
   not spend a dedicated soak chasing this further; if it recurs
   incidentally during a soak run for a different reason, the
   `ROGUESQ_LOG_ANIM_CB=1` instrument is still live and ready to read.

-10. **M3 — check the Metal-shader-compiler SIGSEGV's reproducibility** (s83
   spline1: SIGSEGV inside `Metal.framework`'s `MTLCompilerFSCache`, no
   source on our side). Still only one data point.

-9. **M3 — confirm the s83 spline div0 guard actually engages.** 0/5 fires
   so far (still 0 after s88/s89/s90); real fix by code inspection (genuine
   0/0 IEEE division) but no same-run positive control yet.

-8. **M3 — characterize `frameStartReset` SIGBUS.** Demoted from
   "dominant blocker" after s85 (0 recurrences in s86–s90, 5 soaks);
   recurred s108 (2nd occurrence); **recurred again s156 (3rd
   occurrence, `+532`)** at a call chain (`static_5_800AAD9C ←
   static_5_800C6854 ← menuOverlayInit`) that is byte-identical to the
   12th class's (`composeNpcOrientationMatrix`) own chain — see item -8
   at the top of this list for the shared-dispatcher hypothesis this
   raised. Superseded: "only worth attention if it recurs more often" —
   it has (now 3 occurrences, most recent 2 in consecutive sessions);
   still no located faulting instruction/detector in any of the 3.

-7. **M3 — HOLD_S=60 craft stick (M3 DoD body)** once items 1–4 are clear:
   `PROBE_MODE=start_only HOLD_S=60` marks 10/25/40; document phase timeline.
   Gate already keeps black off; residual S1 `fs` freeze (~3769–3872 plateau,
   s82/s85/s88/s89/s90) may still stall animation — if stick marks show no
   pose change on a frozen frame, next is S1 FULL_SYNC for hangar-flight
   tasks (not leave-key, not wild-FB).

-6. **M4 — confirm the s53 missing-func fix at runtime (s54 applied + built it; only the game-run
   check remains).** Undriven outdoor-512 stretch; `grep -c "\[missing-func\]"` 3→0.
   Not load-gated (s60/s61). Full detail: PORTING-STATE s53, s54.

-5. Past the first sustained mission hold: expect further new failure classes (mission overlay
   DMA → missing-func / UnhandledJumpTarget, new VI phase, overlays 12/44 splice, texture
   corruption). Each new failure is its own work unit.

-4. **Doc housekeeping — `CURRENT-TRUTH.md` well over the ~35 KB CLAUDE.md guideline
   — thread exhausted (s55–s58).** Prefer M3 mission-content work over reopening this section.

-3. **Sibling-repo housekeeping (flagged s54, not autonomous):** `~/Documents/Tools/rogue_squadron64`
   carries uncommitted symbol-file edits including s54's `mission_overlay.txt` fix. Ask the user
   before committing there.

-2. **Band-row coverage history** (settled): s41–s49. s40's `col`-write probe fails its control.

-1. **GPU->CPU present PNG** via `NativeTarget::copyToRAM` -- a convenience, not a
    blocker.

**Done, do not redo:**
- Optimise the ucode vector path -- s38 found it was `-O0`; `-O2` gave 41x. SIMD/RSPRecomp vector work
  is unnecessary at 4.5ms/task without a new measurement justifying it.
- Confirm the ucode-performance bottleneck (s37) - find why DL submission collapses (s36) - census the
  RDP stream (s35) - localise the draw loss (s33/s34).
- Coverage attribution (`LOG_BBOX`) and load/render format mismatch (`LOG_UPLOAD`) -- every draw
  covering the band is I4 with `tlut=0`, from I4 loads.
- The s27-s31 I4-decode line (`FIX_DXT_I`, `I4_SHADE_MONO`, `SHADE_ONLY_MONO`, restricted
  `FLATTEN_I4`) -- aimed at a texture that does not paint those pixels.

(The s92-95 session-by-session DMA-caller narrative that used to live here is folded into the crash
catalog and DMA-caller finding above -- not duplicated.)

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
   - audio-engine gate stores → 0 in `funcs_23.c` (`initMusyXEngine`, `setDisplayMode`,
     `reapplyDisplayMode`; gate byte 0x800A0F50) — without this the scheduler wedges in
     `waitForMusyXAudioTaskDone`
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
- ~~Screen Recording permission is intermittent~~ — **overturned s32.** Capture and synthetic input
  both work: 74/74 `screencapture -l` succeeded across a full undriven run (73 with content, all
  phases), the game's CGWindow id was **stable** at one value for the whole run, and a driven run
  reached the hangar (512 origin 0x6AB400 at 56.0 s) off `winctl` keys. `could not create image from
  window` means the **window id is wrong**, not that permission is missing — check the id before
  blaming TCC (`winctl find <pid>`; `winctl list` is not a subcommand and prints nothing).
  `winctl trusted` reports Accessibility state directly.
- `winctl activate` (activateWithOptions:) is a cooperative request modern macOS **ignores while
  another app holds focus** — keys then get dropped with `trusted`=yes and the run silently follows
  the undriven route (s45; also the real cause of the session-25 failures regress.sh blamed on "no
  GUI session"). probe.sh/regress.sh now raise via System Events `set frontmost` (`raise_game()`);
  keep using them rather than winctl directly for driven runs.

## Overturned conclusions — do not act on these

- **Claim (s222):** "no soak has ever reached mesh-heavy content" / the
  post-`SELECT YOUR CRAFT` corruption freezes the picture within ~4s of
  leaving the menu on EVERY soak, independent of schedule. **Overturned
  (refined) by s223:** an exact byte-for-byte re-run of s222's own
  `schedulepush2` script reached genuine space-combat mesh content
  (`hold_01`-`10`) and the opening crawl (`hold_15`-`74`, matching s154's
  own "furthest ever" milestone, item -6 below) before freezing — the
  identical schedule that produced s222's total dead-hangar-freeze produced
  a run past the crawl the very next attempt. The freeze phenomenon itself
  is real and still reproduces (now on a flat ground-color fill rather than
  a torn/striped polygon), but "every soak, ~4s post-leave, no exceptions"
  was an artifact of a 4-soak sample size, not a structural guarantee —
  reaching further content is possible, apparently non-deterministically,
  with the SAME scripted input. Believable because 4 consecutive soaks
  (s180-s222 lineage) really did show the identical pattern, which looked
  like determinism until a 5th, identical-input attempt broke it. Full
  detail: PORTING-STATE Session 223, CURRENT-TRUTH item -64.

- **Claim (s216-218):** the identical corrupt literal `0x0000000300000000`
  seen at `x0`/`x8` in three crash dumps (`heapFreeListDequeue`, `heapWalker`,
  `renderUnlitMeshFaces`) is a single shared corruption source being WRITTEN
  somewhere and later read by unrelated consumers ("three-source-confirmed",
  former item -59). **Overturned by s219:** that register is this process's
  constant, unchanging native RDRAM host base pointer (already named as such
  by s194, `PORTING-STATE.md:17934` — "almost certainly the rdram host base
  pointer" — a session s216-218 never cited), present in every `MEM_W`-style
  fault by construction, not corrupted data with a write site. The actually-
  wild operand is the OTHER register (`x9`), which differs across the
  sightings: byte-identical `0x80630062` at 3 of them (s194/s199/s218, all
  the SAME already-diagnosed, never-fixed `renderUnlitMeshFaces` bug's 4th
  recurrence, not 3 independent ones) vs. `0x38d47580` at the 4th (s217,
  `heapWalker`, no KSEG0-tag shape at all — a separate bug). Believable
  because the shared constant really is byte-identical across sessions
  months apart, which does look like "the same value being written" until
  you check what that constant actually represents. Full detail: PORTING-
  STATE Session 219, CURRENT-TRUTH item -60.

- **Claim (s75/s76):** a single Start press from SELECT YOUR CRAFT leaves the
  menu into a distinct "hangar-flight" scene — an airborne X-wing outside the
  hangar. **Overturned by s150:** dense (0.2s-tick) capture across the same
  transition, cross-checked against the s76 `hold60/` archive (an
  independent prior run, not a new soak — two sources), shows the
  "airborne X-wing" frames are the *same* craft-select hangar 3D scene
  (identical X-wing pose, R2 unit, crate, wall paneling, moon backdrop)
  viewed from a progressively closer/lower camera angle with escalating
  render corruption (large striped/aliased degenerate polygons), not a
  new environment. A third, independent, code-level check confirms it:
  this session's crash (3rd recurrence of the already-catalogued 12th
  class, `composeNpcOrientationMatrix`, past both its s100/s126 guards —
  a 3rd, still-unlocated fault site) backtraces entirely through
  already-known hangar-menu functions (`menuOverlayInit` →
  `runHangarMenuFromOverlay` → `runHangarSelectionFrame` →
  `composeNpcOrientationMatrix`), none of them mission-overlay code.
  Believable because the title-yellow HUD text really does disappear and
  a tilted ship silhouette against stars reads as "flying", but the
  pre-Start static menu already shares that same starfield/moon backdrop,
  and the hangar walls stay visible in every post-Start frame examined.
  **Reopens "what leaves SELECT YOUR CRAFT into a mission" as unanswered.**
  Full detail: PORTING-STATE s150.

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its
conclusions are among the oldest in the file, not the newest.

The s2–s5 stabilization-era claims (LoadTile underflow, zeroed DL-chunk bytes, RDP-ring/trig-load
misreads of the audio `ucode_data`, "two gfx ucodes") are compressed to one line: **every one was
eventually explained by the shared-`dmem[]` race** (audio tasks staging over gfx state; fixed by
the recursive mutex, s5). Full detail: PORTING-STATE and PROJECT-OVERVIEW §3. Do not re-litigate
any s2–s4 conclusion without checking that section.
- **Claim (s5–s7):** 0x76A000/0x7DD000 are colour buffers cleared to white. **Overturned by s8:** they
  are Z-buffers (`SETZIMG` op 0x3E, 0xFFFCFFFC standard z-clear); colour buffers are 0x5D4000/0x66A000
  (640-wide), 0x6BA000/0x6DD000 (320-wide). Believable because 0xFFFC reads as white in a 16-bit
  colour buffer and the screen was white. Full detail: PORTING-STATE s8.
- **Claim (s7):** texrect draws execute but their output is invisible in the render target.
  **Overturned by s8:** `ROGUESQ_VI_FORCE_FB=0x5D4000` shows dense content — the pixels exist, the
  default present just picks a different buffer.
- **Claim (s8):** F5 geometry ops 0x01/0x02/0x03 emit zero RDP bytes (64/66 tasks), probably
  RSPRecomp culling every primitive. **Overturned by s9:** `rsp_dpc_submit`'s ring high-water mark
  lived in function-local statics, discarding any task no larger than the largest previous one;
  hoisting it to file scope (`s_submit_dl_base`/`s_submit_last_end`) fixed it — 65/65 tasks commit.
  Believable because RT64's own HLE leaves the same three ops stubbed, a second path agreeing on
  "no geometry".
- **Claims (s9, sixth pass), compressed:** "0x790000 is a z-buffer the VI never scans" (s10/s18/
  s21: it is a presented, double-buffered colour buffer — the +0x100000 z-pattern just holds
  everywhere else) and "`[dpc-behind]` counts 17 867 wrap drops in 60 s" (s10: real figure
  9 056 256 in 70 s — the counter read a sampled path).
- **Claim (s9/s10):** `ROGUESQ_DPC_WRAP=1` gives continuous rendering, and the Metal exhaustion it
  triggers must be contained with `ROGUESQ_MAX_FBPAIRS`. **Overturned by s11:** with the
  `VI_FULLSYNC` fix, wrap **off** gives more content and more detail with `[fbpair-cap]` never
  engaging — wrap-on was re-sending already-consumed ring bytes, papering over the missing FULL_SYNC
  that was the real cause (see next entry).
- **Claim (s10):** the Metal shared-memory exhaustion is a property of the post-logo tiled phase and
  the framebuffer-pair cap is the fix. **Overturned by s11:** that phase never emits RDP FULL_SYNC at
  all, so the workload never advanced (195,057 pairs, 23 GB of Metal buffers, black screen all
  downstream). Synthesising the frame boundary from the VI swap (`ROGUESQ_VI_FULLSYNC`) fixed it —
  see PROJECT-OVERVIEW §4.6. Believable because the allocation backtrace named `addFramebuffer`
  unambiguously and the cap did buy a clean 120 s run.
- **Claim (s9, third pass):** `ROGUESQ_PRIM_ALPHA_FF=1` (PRIM alpha ~3%) is needed to see text.
  **Overturned by s11:** verified, not assumed — with it off the attribution screen still renders
  fully legibly, so the hack was retired rather than replaced.
- **Claim (s9, mid-session):** the renderer regressed to black, so the 24 overlay-symbol moves must
  be reverted. **Overturned within s9:** sampling artefact — four one-shot captures at 4/8/14/20 s
  all showed black, but a 28-frame burst at 0.15 s showed 27/28 full of content; the moves were fine.
- **Claims (s12–s16), compressed:** "the 0x60xxxx I4/CI4 dumps are the hangar floor/wall assets" and
  "the 0x65xxxx RGBA16 loads are hangar assets" — both wrong (real CI sources elsewhere; the RGBA16
  loads fire during the 1024 title phase). A plausible decoded image does not identify a phase.
- **Claim (s14):** `ROGUESQ_FIX_LINE_MASK` (force `line = 2^(masks-4)` on 4-bit tiles) — wrong
  direction, the mask/line "disagreement" tiles are real. **Overturned by s15**, replaced by
  `ROGUESQ_FIX_SAMPLE_BOUNDS` (still default-on).
- **Claim (s14):** palette-bank-15 stomping (later LOADTLUTs from 0x62Bxxx replacing the red hangar
  palette) is the root of the rainbow floor band. **Overturned by s15:** the first 40 CI4 pal15
  uploads all use the red palettes with zero multi-colour loads — band pixels are warm red #ce6238, a
  layout scramble of correct colours, not a wrong TLUT bank. M1 (s44–s49) later found the real cause.
- **Claim (s13):** hangar walls need synthesised dxt, so `ROGUESQ_FIX_DXT` defaults ON. **Overturned
  by s22/s23:** it turns the 1024 title backdrop into a vertical-stripe mosaic and gives the hangar
  rainbow/static corruption; default is now OFF. Believable because s13's A/B was cross-run, the
  method s18 later rejected as unsound for animating scenes.
- **Claim (s18, first half):** the 512 phase draws flat sand-coloured polygons and fog #C8C0A0
  matches the on-screen colour. **Overturned by s18 (second half):** `ROGUESQ_FORCE_FOG` changes 0
  pixels — the sand is the **fill colour**, triangles paint black. A colour match is not attribution
  (PROJECT-OVERVIEW §4.2).
- **Claim (s18, mid-session):** textured triangles with S identically zero (base, dx, de all zero)
  explain the flat 512-phase rendering. **Overturned within s18:** those triangles are not in the 512
  phase — run-lifetime "first N" counters reported whatever phase started first. Interval-scoped
  counting finds **0** collapsed triangles in both 512 and 1024; the S=0 triangles live in the 640
  attribution phase. **Why believable:** a collapsed S coordinate is a textbook cause of flat texturing.
- **Claim (s18, fourth segment):** no RGBA32 LOADBLOCK is ever emitted in the 512 phase (exhaustive
  census: RGBA32 = 0), the TMEM high half is empty, so geometry rasterises black. **Overturned by
  s19:** `DUMP_TMEM_DRAW` at draw-record time sees **stale** TMEM — RT64 defers every LOADBLOCK to
  `fullSyncFramebufferPairTiles`; measured at upload, both TMEM halves are filled. This is the
  general "stale reads" trap, PROJECT-OVERVIEW §4.1.
- **Claim (s19):** the 1024-phase black screen is most likely the same zero-shade bug as the hangar;
  retest after the shade fix. **Overturned by s20/s21:** `FORCE_SHADE_WHITE=1` gives 0/4 content at
  1024 — the real cause is present starvation: `State::updateScreen` in PresentEarly mode
  early-returns whenever `presentEarly && !fromEarlyPresent`, and at 1024 no fbPair is ever an
  `earlyPresentCandidate`, so presents stop entirely.

- **Claim (s62/s63):** the M3 render-once-then-freeze bug is CPU-side — RSP task submission
  (`[lle task]`), command processing, and presentation all stay healthy through the freeze, so an RSP
  infinite loop is ruled out. **Overturned by s64:** both supporting observations were sampled-log
  artifacts. The `[task-brief]` iteration-cap population genuinely is unrelated (that part stands),
  but the "RSP stays healthy" read came from `[lle send_dl #N]`'s 1-in-32 throttled sampling, which
  has near-zero odds of ever landing on the run1/run2 trailing 5-6 tasks it needed to inspect — it
  only ever showed pre-freeze tasks (`Broke`, correctly). An unsampled per-task histogram
  (`ROGUESQ_LOG_RUNNER_ALL`, added s64) shows the true population: from task #3141 on, 100% of
  remaining tasks exit `RspExitReason::ImemOverrun` on real (not stub) triangle content, tracing to
  an RSP ucode branch RSPRecomp couldn't resolve. **Why believable:** the throttled log had correctly
  shown `Broke` on every task it ever sampled, so "the RSP side is healthy" looked like a repeatedly-
  confirmed fact rather than a fact about only the 96.9% of tasks the sample could ever land on.
- **Claim (s64/s66):** the freeze-phase ImemOverrun is the end-of-IMEM `bgez $2, L_0000`
  perspective-divide branch (fixup-1 hard exit); implementing a self-restart for it should un-freeze
  mission tasks. **Overturned by s67:** with both L_0000 outcomes rewritten to self-restart and the
  instrument live under `ROGUESQ_UCODE_NO_OPT=ON`, `[ucode-restart]` fired **0** times while tasks
  from #3216 on still exited ImemOverrun with `syncs=0`. Default `-O2` also DCE's the whole block
  (so an O2-only "null" would have been invalid). L_0000's static self-restart reading (s66) still
  stands as hardware truth; it is not the path freeze tasks take. **Why believable:** the source
  block literally returns ImemOverrun on both bgez outcomes, freeze onset coincides with
  triangle-heavy tasks, and the static disassembly of L_0000 is multi-source clean.
  **s68–s69 follow-through:** actual site was CLIP_1FBC → L_1650 hard exit (s68 counter ≡ every
  exit=2); reconnecting `goto L_1650` after the fixup-6 label (s69 fixup 8) drops exit=2 to 0
  and unfreezes `fs`.
- **Claim (s23):** the hangar's remaining dimness is real vertex lighting, not shade-decode, because
  its shade census is healthy. **Overturned by s25:** that census was the magnitude-only classifier
  s24 proved cannot distinguish −118 from +118 (PROJECT-OVERVIEW §4.2), so "ok" was really the
  all-negative population; driven A/B showed `SHADE_WRAP=1` brighter in 93/114 paired hangar frames.
- **Claim (s28):** `FORCE_SHADE_WHITE` kills the hangar multi-hue floor band, so the band colour is
  shade. **Overturned by s31:** on the standard hangar view the mid-ground band survives FSW —
  walls/pad go monochrome, multi-hue floor remains; warm% alone was a bad residual metric.
- **Claim (s30):** hangar mid-band is 100% untextured shade-only and `SHADE_ONLY_MONO` kills the band.
  **Overturned by s31:** the earlier census only sampled the landing-pad shade-only population; an
  improved census after the hangar found 201 textured-I4 tiles (imgs 0x604140/0x605140) alongside 73
  shade-only. Suppress/mono leave the multi-hue mid-ground; FSW proves it is TEXEL, not shade.
- **Claim (s46):** no complete clip overlay exists raw in the ROM (whole-ROM byte scan); the game
  materializes overlay images in DRAM at runtime, so only a runtime capture can recover it.
  **Overturned by s47:** all five runtime-captured overlay images are byte-identical to the ROM at
  `RDRAM_addr + 0xC00` (clip: 544/544 at ROM 0x26420). The recompiled window region is the packed
  overlay *storage* (init at window+8), which s46 read as "init image + stale clip tail" and which
  made its scan expectations wrong. **Why believable:** the window-region disassembly genuinely
  contains init code and clip-fan fragments at shifted offsets, and a byte scan for the *expected
  window layout* genuinely finds nothing.
- **Claim (s46):** ~40 window entries/task arrive via a non-L_1298 `jr` (jrc sum 247 vs 287 label
  hits), so case-level routing of the clip splice may be unsafe. **Overturned by s47** (fixup 5
  stray census): 4221/4221 `case 0x1DB0` arrivals come from the L_1298 `jr $3` (debug_line 594)
  with DMEM 0x153 already set to the requested overlay id. The excess label hits were
  fall-throughs from code above L_1DB0, which the label counters count but the dispatch does not.
  **Why believable:** the two counters were believed to measure the same population; they differ
  by exactly the fall-through paths.
- **Claim (s12–s47):** the 512-wide origin-0x6AB400 scene is the "main-menu hangar" — landing
  pad, parked X-wing, hangar walls. **Overturned by s48** — mechanism at "scene-identity
  correction" above. Proven by wall-structure identity between the s41 control frames and the s48
  full render, same origin, same input path, arrival times matching to 0.2 s. **Why believable:**
  the partial render was a coherent-looking scene for 36 sessions, and SELECT GAME's photographic
  hangar backdrop reinforced the "hangar" frame; nothing looked missing until the missing half
  rendered.
- **Claim (s47):** the briefing room presents from origin 0x656400, SELECT LEVEL from 0x696100,
  the clip fix changed menu timing, and the verify run overshot the hangar. **Overturned by
  s48:** all four wrong. The war room / SELECT LEVEL presents from **0x6AB400** (three runs); the
  0x696100 `[vi]` lines sit in the 640-wide pre-title phase; menu routing and timing are
  unchanged (title → SELECT GAME → war room, one press each, war room at 54.5 s vs s23's 54.7 s);
  and nothing was overshot — the band scene was on screen the whole time, rendering complete for
  the first time. **Why believable:** the completed render looked like a brand-new scene, so
  nearby unfamiliar origins in the log read as its identity, and "we missed the hangar" was the
  only story consistent with the hangar still existing.
- **Claim (s70 implied):** post-`a` SIGBUS is a thread lifetime bug (UAF of destroyed
  `OSThread` / `UltraThreadContext`, or double-signal). **Overturned by s71:** live-context
  set shows the crashed resume's `context` was **never created**; the good context of the same
  OSThread (`runAiAudioStreamPlaybackLoop` @ `0x801494B0`) was never destroyed; only 1/103967
  resumes had `live=0`, with a bit-diff vs the prior good pointer. **Why believable:** stack
  lands in `LightweightSemaphore::signal` after `resume_thread`, the classic UAF symptom, and
  destroy/create churn of other threads (ids 6–10) sits earlier in the same mission-entry window.
- **Claim (s71 H4 partial):** context bit-corruption is an unknown in-place smash; `last-drawn
  #1870` is only timing correlation. **Closed by s72:** the writer is the RT64 depth writeback
  immediately after that last-drawn, range `[0x140000,0x3E1332)` overlapping OSThread phys
  `0x1494B0`, with before/after snapshot proving the mutate. Width/OOB writeback gate stops
  the SIGBUS. **Why the correlation looked weak:** last-drawn only updates atomics (no RDRAM
  store); the actual store is the subsequent `copyNativeToRAM` on the paired depth FB.
- **Claim (s70–s72 residual):** after SIGBUS fix, remaining M3 defect is sustained **mission**
  texture garbage (g07 capital-ship class). **Overturned by s73:** g07 is a ~1s flash; stable
  post-`a` content for 55s+ is **SELECT YOUR CRAFT** (menu). s70 never stayed on craft-select
  only because it died at g07; s69 (25s grace, alive) already showed SELECT YOUR CRAFT. **Why
  believable:** the flash is dramatic and mission-shaped, and earlier deaths cut the timeline
  before the real destination rendered.
- **Claim (s74 residual):** leave from SELECT YOUR CRAFT may require double-Start or
  Start-after-`a` (first Start alone +3s still SELECT). **Overturned by s75:** start_only
  with unique tags leaves on one Start by +2–4s (title-yellow + hangar-flight visual).
  **Why believable:** s74 overwrote first-Start snaps with the second Start's names, so the
  only post-first-Start sample was `pre_probe_a` at +3s; short window + possible key drop
  looked like a hard double-Start rule.
- **Claim (s77 implied next):** refusing wild-width FB registration will unfreeze hangar-
  flight present (`fs` past ~3360). **Overturned by s78:** refuse fires, tilecopy control
  on 640 holds, map stays clean — **`fs` still plateaus ~3297** with high-tri `syncs=0`
  from #4252. **Why believable:** s77 showed wild FBs in the map at freeze time, so map
  pollution looked causal; same-run refuse + freeze splits registration from present.
- **Claim (s78 residual / S3):** UnhandledJump 0x0231 (exit=3 population from ~#4265)
  is what kills hangar-flight FULL_SYNC / present. **Overturned by s79:** onset of
  `syncs=0` is task **#4252** with **13** subsequent `exit=1` (Broke) high-tri tasks
  still at `syncs=0` before the first jump. Jump is real and permanent after #4265 but
  **not** the FULL_SYNC-loss root. **Why believable:** 899 jump lines dominate the
  freeze-window log and correlate with the stuck phase in wall-clock time.
- **Claim (s79 residual):** after post-leave SYNC_FULL loss, VI_FULLSYNC stalls
  (only one more `fs` advance then plateau) — so the present freeze is a synthetic
  decision failure (`fbPairCount==0` / no-trigger / FullSyncSeen). **Overturned by
  s80:** always-on `[vi-fs-decision]` shows **FIRE continues** (+141 synth) after
  RDP-`fs` plateaus; V1/V3/V4 refuted. `fs`/`rdpFs` counts DPC FULL_SYNC *opcodes*,
  not synthetic `State::fullSync()` — plateau is S1 restated. **Why believable:**
  the `[vi] fs=` field was the only advance metric in s78/s79 logs and moved in
  lockstep with healthy present earlier, so its freeze looked like the synthetic
  path stopping.
- **Claim (s80 V2 residual):** intermittent black is mysterious despite healthy
  present (`present-1024 empty=0` throughout + synthetic FIRE). **Overturned by
  s81:** `empty=0` logs only on last-drawn *address transitions*, not every
  present; mode-3 actively presents wild last-drawn (w=1..257) during black
  windows (`[vi-follow-draw]`). **Why believable:** empty=0 never flipped to 1 in
  the whole run, so "present RT always non-empty" looked continuously true.
- **Claim (s81 residual / G2):** gate may be too late or present still broken
  even if last-drawn is filtered. **Overturned by s82:** same-run skip control
  + hold pure-black 0/5 + hangar-flight content. **Why believable:** s81 black
  and wild last-drawn were co-timed but not yet proven causal by a live gate.
- **Claim (s87):** the 8th crash's mechanism is self-recursion via
  `advancePlayerAnimationPhase`'s own indirect call, `LOOKUP_FUNC` reading
  a stale/corrupted pointer from global slot `0x80139968` at guest
  `0x8006426C`. **Overturned by s88:** that call site is inside
  `invokeMenuOverlayHeaderCallback`, a different function never reached
  from `advancePlayerAnimationPhase`'s own body (which has zero indirect
  calls — only two direct `jal`s to `activateAnimationKeyframe`, whose
  own callees make no further calls at all). A correctly-targeted entry
  instrument (`ROGUESQ_LOG_ANIM_CB=1`) then showed the function is called
  at effectively constant, shallow stack depth (6 distinct `$sp` values
  across 3296 calls) — no recursion of any kind observed. **Why
  believable:** the source read that produced the claim searched a line
  range ("8130-8153") without checking which `RECOMP_FUNC` block those
  lines actually belonged to; the address happened to be the *only*
  indirect call visible in that grep window, which read as sufficient
  evidence without confirming the enclosing function name.

### Dead ends — labelled as such in the log, do not retry

- `RDP_ADDRESS_MASK` 0xFFFFFF → 0x7FFFFF (`rt64_rdp.h`, s3): 0x800000..0xFFFFFF are legitimate RT64
  extended-RDRAM handles; masking aliases them onto low memory and moved the crash earlier.
- Chunk-replay hack in `dma_rdram_to_dmem` (s3): the ucode legitimately reads trig values from
  0x170..0x280 right after a swap; 29 unhandled vs ~5.
- Widening the DMA shadow to `[ucode_data-0x1800, +0x1800)` to cover 0x37658 (s3): that content
  difference is legit dynamic data, not shadowable corruption.
- Blanket ucode-image shadow `shadow2` (s4): the engine legitimately rewrites `ucode+0x12DEA` and
  `ucode+0x7CD5C`; serving them stale gave 109 unhandled / 35 send_dl against a 256 baseline.
- `ROGUESQ_RING_RESYNC=1`, poking `DMEM[0x108]` = ring base per task (s4): no measurable change
  (41 vs 51) — aimed at a flush overflow that never existed.
- `dmem[0x153]=0xFF` to force a segment reload (s2b): made failures worse (6 exit=3 vs 2–4).
- Bulk moves of unmapped symbols out of `symbol_files/main_overlay.txt` (s9): each inserted symbol
  **splits** the enclosing function in that section — the duplicate-address truncation bug in reverse
  (general class: PROJECT-OVERVIEW §4.5) — producing a SIGBUS in `allocAndInitGridCellArray`. Use
  `tools/overlay_symbol_probe.py <0xADDR> [mission|menu|cinematic]` first (the reliable signal is the
  `addiu $sp, $sp, -N` prologue at +0), one validated batch at a time.
- Present-side snap-down and `findMostRecentContaining` fallbacks (s9):
  `present.screenVI.fbAddress()` already returns the framebuffer base and neither fallback ever fired.
- `ROGUESQ_VIEW_RDRAM=1` (s9): the game window never appears; the mode is broken in this fork.
- `ROGUESQ_WRAP_DEDUP=1` (s10): removes ~33000 redundant submissions but the run still reached
  193715 pairs and the same Metal assert.
- `ROGUESQ_FORCE_PAL15=1` (s14): clears the floor band but corrupts ceiling banners that legitimately
  share pal=15.
- **Claim (s85):** the `do_rom_read` corrupted `physical_addr` is "garbage that varies run-to-run,"
  evidence for a nondeterministic shared-corruption race. **Overturned by s91:** the exact same
  `phys=0x1C676672 ram=0xFFFFFFFF80195190 bytes=0x600` DMA call recurred byte-for-byte 3 times across
  3 sessions and 2 rebuilds — a race would not reproduce identically. Believable because s85's only
  comparison was against a *different* crash type (`thrgate2`, an alignment Abort with no logged
  value) from the same session, not a second instance of the same crash — it never actually had two
  comparable data points. Reclassified as a deterministic, reproducible bug (top of M3 next-steps).

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here, session tag is the
specific instance in PORTING-STATE:
- §4.1 instruments-that-lie: `fbPair.projections` over-count (s32), `[loadblock]` sampled-log
  miscount (s18/s19), stale TMEM at draw-record time (s19), capture harness outliving the process,
  `window_burst.sh` 60/60 false-positive (s9).
- §4.2 attribution errors: colour match ≠ attribution, fog #C8C0A0 (s18); plausible decoded image ≠
  phase ID (s17).
- §4.3 cross-run comparison: knob effects/nulls manufactured by camera drift, "7.30%" constant
  misread as an effect (s18); phase timing varies tens of seconds run-to-run, gate on
  `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1` not a stopwatch (s17 → s18/s23).
- §4.6 missing protocol events: pair/buffer/wrap counters measured instead of FULL_SYNC arrivals
  (s11).

Not yet generalized in PROJECT-OVERVIEW — specific to this codebase's instruments:
- A "crash-free, full hold survived" soak is not evidence the game did anything for that hold —
  MD5-checksum the `hold_NN.png` series before trusting a diagnostic null; s222's soak logged 991
  `[vi-fs-decision] FIRE` events and ran its full 350s hold with 0 crashes while the actual on-screen
  picture was byte-identical from `hold_04.png` onward, frozen the entire time.
- Launching a soak with `run_in_background=true` and then ending the turn before it finishes risks
  the harness reaping the whole process tree mid-run (s222 found exactly this: an orphaned soak,
  no crash logged, process gone, ~40 min stale). For soaks that fit the tool timeout, launch
  synchronously (foreground, no `&`) instead — it cannot be orphaned by a premature turn-end.
- Sparse one-shot screenshots land on genuine inter-screen transitions and read as a regression;
  always burst-sample (28 frames at 0.15 s: 27/28 with content, where 4 one-shots showed black) (s9).
- Validate a suppression instrument before believing a null result: `ROGUESQ_SUPPRESS_SHIFT=1`
  re-runs any suppression mode as a +80 px displacement so you can see it reach the screen (s18).
- The `[seq]` and `[full-hist]` walkers in `dpc_bridge` advance a fixed 8 bytes per command, so
  triangles (32–48 bytes) desync them into thousands of bogus SETCIMG addresses (`LOG_SEQ` also caps
  at 6000). Once geometry flows use `ROGUESQ_LOG_RDPHIST`, which uses RT64's own command lengths
  (s9/s11/s19).
- Histogram-drain timing misleads: the runner histogram showed 0 RDP bytes for a task the dispatch
  tracer proved had processed its full DL (s2b).
- Five frames per run does not average out camera motion, so even aggregate `pixel_stats.py` metrics
  are confounded when runs sample different moments (s18).
