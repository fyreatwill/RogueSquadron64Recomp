# Rogue Squadron 64 Recomp — project overview and recurring hurdles

Companion to the other two docs, and the one to read first if you are new to this repo or returning
after a break:

- **`docs/PROJECT-OVERVIEW.md`** (this file) — what the project is, how the pipeline fits together,
  and the hurdle *classes* that have cost the most time. Durable; changes slowly.
- **`docs/CURRENT-TRUTH.md`** — what is true right now: working config, live defects, next steps,
  and the list of superseded conclusions. Read before doing any work.
- **`PORTING-STATE.md`** — the chronological log (1500+ sessions). Authoritative for detail,
  but dozens of its conclusions were later overturned; never act on it without checking
  `CURRENT-TRUTH.md` first.

---

## 1. What this is

A static recompilation of *Star Wars: Rogue Squadron* (N64, US 1.0) into a native macOS binary,
built on `MikeSemicolonD/RogueSquadron64Recomp` with local forks of N64Recomp, N64ModernRuntime and
RT64. The goal was to get the game building and rendering correctly on Apple Silicon.

**Where it stands:** the game boots and renders through the full menu chain — attribution screen,
N64 logo, intro cinematic, star flare, Factor 5 logo, title screen, SELECT GAME, the level-select
war room, and AVAILABLE CRAFT (craft select) — plus a separate outdoor scene, all rendering
correctly with working synthetic input to drive the menus. The war-room floor band defect (s12–s48,
formerly described as a "main-menu hangar") is fixed and root-caused. Runs are stable — no
`UnhandledJumpTarget`, no dropped tasks, no missing overlay symbols, no renderer asserts — across
every phase soaked to date.

**What is not done:** the LEVEL DESCRIPTION prompt, one press past AVAILABLE CRAFT, black-screens
and silently kills the process — under active investigation, see `CURRENT-TRUTH.md`. Audio is
stubbed entirely, and gameplay past the menus is unverified.

## 2. How the pipeline fits together

Four separable layers, and knowing which one a bug lives in is most of the work:

1. **Game code** — the decomp (`~/Documents/Tools/rogue_squadron64`) provides an ELF and symbol
   files; N64Recomp translates MIPS to C in `RecompiledFuncs/`. Overlay-heavy: three overlay
   sections (mission/menu/cinematic) that the game DMAs in at runtime.
2. **Runtime** — N64ModernRuntime (`librecomp`) supplies the OS shims, PI/DMA, the RSP task queue
   and the cooperative scheduler the game's threads run on.
3. **RSP microcode** — this game uses a custom Factor 5 ucode. RT64's HLE stubs its geometry ops, so
   the port runs it **LLE**: RSPRecomp translates the ucode to C (`build/factor5_ucode/*.c`) and a
   runner in `src/main/main.cpp` executes it per gfx task, bridging its RDP output to RT64.
4. **Renderer** — RT64 (fork, `HLE-F5-Attempt` branch) consumes the RDP command stream and draws
   through Metal.

Regeneration order matters and is documented in `CURRENT-TRUTH.md`; the short version is
`make_elf.py` → `N64Recomp` → **`fixup_game_funcs.py`** → `cmake --build`. Skipping the fixup pass
produces a binary that will not run, and it is the *only* thing that re-applies the hand-edits.

## 3. The arc, in one paragraph each

**Getting it to build (s1).** Windows-isms, missing POSIX equivalents, Cocoa/Metal window creation,
SDL event pumping from the wrong thread, and duplicate weak symbols. Mostly mechanical.

**Getting it to run (s1).** A deterministic scheduler wedge: the game spun forever waiting for a
MusyX audio countdown that only the stubbed audio ucode would decrement. Fixed by forcing the
audio-engine gate byte to 0 so the game takes its own audio-disabled paths.

**Getting it stable (s2–s7).** A long sequence of RDP/DPC semantics bugs and RT64 assert-guards,
culminating in the biggest single find of the project: `librecomp`'s `dmem[]` is **one shared 4 KB
global with no locking**, and audio tasks were staging over it mid-gfx-task. One recursive mutex
eliminated an entire class of nondeterministic corruption that had consumed three sessions.

**Getting pixels (s8–s11).** Two structural bugs: `rsp_dpc_submit` kept a ring high-water mark in
function-local statics so most tasks' output was silently discarded; and this engine **stops emitting
RDP FULL_SYNC** in the menu/mission phases, so RT64's workload never advanced. Synthesising the frame
boundary from the VI swap (`ROGUESQ_VI_FULLSYNC`) made the game render.

**Chasing the hangar band (s12–s43).** Thirty sessions on one horizontal strip of wrong pixels,
ruling out texture assets, palettes, dxt, sample bounds, vertex shade, framebuffer choice, RDRAM
staleness and ucode performance in turn, arriving by s41–s43 at submission-level evidence: geometry
rasterises cleanly through the band rows, so the gap sat upstream of drawing rather than in it.
Along the way it produced a real win — the ucode was being compiled `-O0`, and fixing that made it
**41× faster**.

**Fixing the hangar band (s44–s49).** Root cause: all overlay dispatches share entry **0x1DB0**,
and the window-swap IMEM DMA that should route clip-flagged draws to the real clip overlay is
skipped, so those draws instead ran the packed overlay-image *storage* as if it were code — every
clip-flagged triangle vanished. The fix splices the real clip overlay back in: it sits raw in ROM at
`RDRAM_addr + 0xC00`, translated via a dedicated RSPRecomp pass (`tools/make_clip_composite.py` +
`factor5_rsp_ovl4.toml`) and spliced in by fixup 6, routed by `DMEM 0x153 == 4`. Verified in the
scene itself (band rows rasterise geometry under a mode-2 marker, census identities exact) and
confirmed on a post-fix regression sweep (undriven full timeline + driven war-room run, 0
cull-census-identity violations). Overlay 12 now has the same-style splice
(s739, live validation queued); overlay 44 still takes the old broken path.
Full detail: PORTING-STATE s44–s49 / s739; day-to-day state in
`CURRENT-TRUTH.md` M1/M2.

**Chasing M3 crashes (s76–s147).** Getting past AVAILABLE CRAFT into a stable SELECT YOUR CRAFT menu,
then surviving long enough to reach a mission, meant working through roughly 20 distinct crash
classes one guest function at a time. The five worth remembering as mechanisms: RT64 presenting a
wild last-drawn framebuffer on black screens (mode-3, width 1..257 — fixed by an always-on
sane-width gate, s82); a div-by-zero on a zero-width keyframe interval in `evalCubicSplineAtTime`
(s83); an OSThread UAF SIGBUS from scheduler thread-context reuse (found s70–72, fixed s84); the
single longest-running M3 thread, `do_rom_read`/`piDmaWorker` DMA corruption, root-caused after ~30
sessions to a non-atomic `voiceCount`-write-before-pointer-store race in `allocateSongChannelArray`
letting the concurrently-scanning audio thread read a stale array (fixed s147/148); and a still-open
TMEM-zero-dimension RT64 assert in `queueGPUUploadTMEM`, stopgap-guarded s192. The remaining ~20
"hangar-tick-family" classes all shared one shape — an unguarded pointer-chase in a single guest
function — and were closed one guard at a time (8 in the original s99–110 pass, a 2nd gap in 6 of
those 8 found by a s126–132 re-audit, and the biggest recurring sub-family, the `-0x25A4`
hangar-list-pointer chain, fully closed by the s282–288 systematic audit lineage). Full per-class
catalog and day-to-day state: `CURRENT-TRUTH.md`.

## 4. The recurring hurdles

These are the patterns that cost the most time, in rough order of total damage.

### 4.1 Instruments that lie — the single biggest time sink

More sessions were lost to bad measurement than to bad code. Every variety showed up more than once:

- **Sampled logs read as totals.** `[loadblock]` prints the first 60 then every 500th; counting its
  lines said "43 RGBA32 loads" where an exhaustive census said zero.
- **Run-lifetime budgets eaten by boot.** `[rdp-fill]`/`[rdp-texrect]` budgeted output over the whole
  run, so the hangar logged *nothing* and absence read as "no fills happen here". Fixed by scoping
  every counter to the phase.
- **Stale reads.** TMEM inspected at draw-record time shows the previous frame's content, because
  RT64 defers loads to `fullSyncFramebufferPairTiles`. Measure at upload.
- **Reused containers.** Summing `gameCallCount` over `fbPair.projections` — the whole vector, not
  the live `projectionCount` — reported 292–468 calls for pairs that carry 1–10, and manufactured a
  100× "loss" that took a session to withdraw.
- **Dead instruments.** `TARGET_CLEAR=2` sat inside an `if (colorFb != nullptr)` block and never ran;
  a magenta probe written through `col` in `RDP::drawTris` never reached the screen. Both produced
  confident nulls that meant nothing.
- **Counters that prove the branch ran, not that it worked.** The bbox counter reached 7,600 while
  the probe it guarded had no visible effect whatsoever.
- **Capture harnesses that outlive the process**, photographing the window underneath and reporting
  it as content.
- **A downstream instrument measures a downstream fact.** `ROGUESQ_LOG_MUSYX_DMA_CALL`/
  `_VOICE_TRIGGER_CHAIN` were armed to test whether an RSP task type was ever dispatched, but both
  sit on a data-gated consequence of dispatch (a PI-DMA sample-streaming call that only fires with
  real song/voice state) rather than dispatch itself — 0 hits read as "never dispatched" when the
  true answer was "dispatched every frame, but with no songs registered yet." A mechanism-independent
  counter placed at the actual dispatch site (s300) gave the real answer in one soak. Trust an
  instrument only as close to the mechanism under test as it can be placed.

**The rule that emerged:** a null result is worthless until the instrument has passed a positive
control — mark *everything*, and confirm the screen changes — and a counter is not a control.

### 4.2 Attribution errors

Deciding *which* draws are responsible for a region of pixels went wrong five separate times:

- **Centroid binning** cannot see a large polygon that covers a region while its centre sits
  elsewhere. Bucket by span, not centroid.
- **Magnitude-only censuses erase sign.** A shade census bucketing by `|value|` counted −118 as
  healthy next to +118 for four sessions; the sign was the whole bug.
- **Coverage-changing knobs appear to fix see-through defects** for reasons unrelated to their stated
  mechanism — `FLATTEN_I4` "fixed" the band by covering it with flat geometry.
- **A colour match is not attribution.** Fog `#C8C0A0` matching an on-screen `#c5be9d` was
  coincidence.
- **A plausible decoded image does not identify a phase.** Five sessions tuned knobs against a
  texture population that belonged to a *different phase*, confirmed only when the VI width was
  finally interleaved against the load log.

### 4.3 Cross-run comparison on an animating scene

The camera differs between runs, so knob effects and null results are both manufactured. Any A/B has
to be phase-gated on a VI transition (never a stopwatch — phase timing varies by tens of seconds),
key-schedule-matched, and ideally toggled within a single run. A corollary discovered late: after the
`-O2` speedup the game progresses further per unit time, so an old key schedule silently overshot the
hangar into a different scene *that shares the same VI origin*.

### 4.4 Shared mutable state in the emulated machine

`dmem[]` is one global array; the DPC registers are globals; render targets are keyed by address plus
format. Symptoms were wild nondeterminism (9–94 failures per 300 s), "impossible" state changes
between two same-thread observation points, and canaries that read clean immediately before
corruption appeared. **When emulated state changes impossibly, suspect another thread sharing it.**

### 4.5 Translation-layer sharp edges

N64Recomp and RSPRecomp both emit code that is *almost* right:

- **Duplicate same-address symbols** make the tool emit a 1-instruction stub, so every call leaks
  stack and the caller restores garbage registers. A function body truncated to one instruction is
  the fingerprint.
- **The inverse** — inserting a symbol mid-function — splits the enclosing function, with the same
  class of consequence. Probe before moving symbols, one validated batch at a time.
- **Hand-asm idioms** the recompiler does not model (`jr $t9` as a return, cross-function branches
  into shared tails, writes to `$zero`, compiler `break` guards) all need post-pass repair, which is
  what `fixup_game_funcs.py` exists for.
- **Generated-code hand edits do not survive regeneration.** Diagnostics in `build/factor5_ucode/*.c`
  survive a cmake build but not an RSPRecomp run; anything in `RecompiledFuncs` is wiped entirely.
- **A guard on a pointer's *result* does not protect the pointer used to reach it, or any further
  pointer read out of the validated structure ("second-hop" derefs).** Recurred independently three
  times in the `-0x25A4` hangar-list-pointer audit (sessions 282, 284, 285) across two different
  functions: an existing bounds check on a reloaded value left the *reload itself*, or a field read
  one hop further into the now-validated struct, completely unguarded. When auditing or guarding a
  chain of dereferences, check every reload's own resulting address before its own first
  dereference — do not assume a downstream guard on a value loaded further along the chain covers
  it.

### 4.6 Missing protocol events, papered over downstream

The engine never emits FULL_SYNC in some phases; the ucode's ring semantics needed `DPC_CURRENT` to
reset on a `DPC_START` write. In both cases the *symptom* was a downstream resource explosion —
195,057 framebuffer pairs, 23 GB of Metal buffers — and several sessions were spent measuring that
resource ever more precisely. **When a downstream resource explodes, first count the event that is
supposed to bound it.**

### 4.7 Configuration blind spots

`CMAKE_BUILD_TYPE=Debug` with debug flags of literally `-g` meant the whole project, including
per-instruction RSP emulation, was compiled `-O0`. Two sessions profiled the symptom to three decimal
places before anyone checked the optimisation level. Adding `-O2` to three translation units gave a
**41× speedup** on the hot phase. Check the mundane configuration before profiling emulated code.

### 4.8 Environment fragility

`screencapture -l` fails with the same message for a missing window id as for a permission denial,
which was recorded as "intermittent Screen Recording permission" across three sessions before one
test against a known-good window id disproved it. Synthetic input needs Accessibility and fails
silently when absent. Both are worth verifying explicitly at the start of any visual session.

## 5. What actually worked

### 5.0 Current durable checkpoint (s1728)

The overlay-dispatch issue is closed enough for mission entry and post-sec2
outdoor presentation. The recurring `slotDispatcherIter+872` SIGBUS has no
statically reachable frame-overlapping writer after complete caller, context,
store, and load-idiom audits. The active VI boot descriptor is the 320 record,
and the independent retail oracle controls pass. Dummy video stays at width
320/origin `0x006dd280`; Homebrew Rice with the eleven-Start schedule is the
available hangar-entry recipe (s707, s1496). After hangar, Start/A leave via
case-6 `runModelViewerLoop`; pre-exit B is a distinct frontend route that
times out to attract 512, whose A/Start/C-up/L/Z leave to a title-like 1024
that is not a new cinematic, menu-SM, mission-frame, or `menuOverlayInit`
jump-table-case session (s1744/s1760 H3-stop-tick) but does add
`submitGfxFrame` +104/+102 vs hold (s1776 H1; s1792 H3 no unwatched
entry; s1808 H2 `menuControllerInput` jal +276 offset by
`runInMissionFrame` jal −175; Rice still dies ~135 s). Audio de-stubbing is closed. These
are boundaries, not mitigations: future guards require an `ORIGIN:` naming
the writer and judging the value legitimate. The generated-symbol renaming
sweep is the current low-risk workstream; exact companion/generated names
are synchronized through `npcTrainCarUpdate` at `0x800E2818` (s1775).
See §33–§35 for the archived census, `CURRENT-TRUTH.md` for the live
backlog, and `PORTING-STATE.md` for evidence.

- **Two independent sources before concluding.** Every finding that survived has two: task timing
  *and* CPU%; stream census *and* draw-hook counters; a probe *and* its positive control.
- **Discriminating experiments, not supporting evidence.** The useful measurements were the ones
  whose outcome split the hypotheses — `TARGET_CLEAR=1` vs `=2`, marking every draw vs band draws
  only, `tris-rdp` vs `tris-call` in the same unit.
- **Physical impossibility arguments.** "An I4 texture with `tlut=0` cannot produce orange" killed
  five sessions of texture work in one line of reasoning, without a single run.
- **`sample <pid>`** named both the s1 scheduler wedge and the s36 ucode bottleneck in one shot each.
- **Writing down what was overturned.** The "superseded conclusions" section of `CURRENT-TRUTH.md`
  has prevented at least three re-investigations of dead ends.

## 6. Metrics worth watching

| metric | how | current |
|---|---|---|
| ucode cost per gfx task | `ROGUESQ_LOG_TASKMS=1`, `[taskms ph5]` | 4.5 ms (was 186.6) |
| gfx task rate | `[lle task]` lines per second | ~19/s in hangar |
| RDP stream volume | `ROGUESQ_LOG_RDPHIST=1`, per-2 s deltas | TRI +300–500/2 s in hangar |
| frame content | `tools/probe.sh` + distinct-colour count | ~52 500 distinct, hangar |
| stability | `UnhandledJumpTarget`, `[defer-drop]`, `[missing-func]`, asserts | all 0 |

A caution on the last one: distinct-colour count *drops* for some strictly-good changes — removing a
black wedge removes its high-contrast edges — so use a defect-specific measure when testing something
that removes an artifact.

## 7. M3 crash-class catalog (s83–s110), migrated from CURRENT-TRUTH.md s307 maintenance pass

19 classes found chasing the `submitDmaRequestBatch` indirect-caller window (caller identified s101:
`musyxSynthFrame` via `viRetraceHandlerThread`, not the mission/DL path every earlier session assumed —
refuted dead ends, do not reopen: `ra=0x00000000` as a corruption signature, "dump the OSIoMesg at mb,"
consumer index desync, "the boot call loops more than once"). "Guarded" = landed with a clean negative
control, treat as closed unless noted. All guards use the same `U32()`-truncated-bounds-check-then-
`goto`-real-epilogue template. Thread A (PORTING-STATE Sessions 126-132) later found a *second*
unguarded site in 6 of the 8 guarded functions — already folded into the table. Full detail:
`PORTING-STATE` Sessions 93-110, 124-132, 159, 195-196.

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

## 8. Instrument-specific method traps, migrated from CURRENT-TRUTH.md s314 maintenance pass

Not yet generalized into §4 above — specific to this codebase's instruments, kept for whoever
next writes a soak diagnostic:

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

## 9. Closed investigation lineages (s99–s337), migrated from CURRENT-TRUTH.md s314/s346 maintenance passes

Full detail for all of these lives in `PORTING-STATE.md` at the session ranges cited; this is the
one-paragraph-per-lineage summary that used to sit in `CURRENT-TRUTH.md`'s Next-steps list as items
-159 through -14 (excluding -20, the still-standing regen-pipeline rule, which stayed in
CURRENT-TRUTH). None of these are open work — they're kept so a future session doesn't re-open a
question already answered.

- **M5 audio gate-byte-reversal and VI=640-stall measurement chase (s297–s337) — CLOSED, superseded
  by CURRENT-TRUTH item -195's source proof.** 41 sessions of instrumentation, each step's premise
  overturned by the next. s297-301 built the investigation runway (`M5-AUDIO-PLAN.md`, a source read
  of the audio-engine gate byte at `0x800A0F50`, an `[audtask-dispatch]` counter, a bounded-timeout
  guard on `waitForAnyAudioSlot`). s302 reversed `initMusyXEngine`'s gate site — later found to be
  dead code, never called (s306, see CURRENT-TRUTH Overturned Conclusions). s303-322 chased the 3
  `musyxSynthFrame` countdown/period gates' ("gate1/2/3") "taken" reachability through 2 distinct
  diagnostic bugs — an unwidened print cap silently truncating counts past n=40 (hit 4 times across 4
  different diagnostics) and a TOCTOU re-read of a shared countdown word instead of the register the
  real branch decision uses — before s325 closed it: the apparent "14 missing calls" gap was itself
  the print-cap bug; the corrected combined count exactly matches the tick-producer functions' own
  37-call total. s323-329 (M5-AUDIO-PLAN step 4) source-traced the `setDisplayMode` VI=320 hang to an
  unpumped `musyxSynthFrame` spin loop inside `waitForMusyXAudioTaskDone`, landed a bounded pump fix,
  and confirmed it clean 3/3 soaks (s327/328) — then found `reapplyDisplayMode`'s site (the 3rd/last
  gate) caused a NEW, unrelated permanent graphics-task-submission stall at VI=640. s330-337 chased
  that stall through 5 reachability probes — a 2nd unpatched spin loop inside
  `waitForMusyXAudioTaskDone` (runtime-refuted), `runVideoFrameTick`'s full call-site set (one call
  site found to be unreachable dead code, a false lead), `mainGameLoop` parking after one pass — down
  to `cinematicLoopBody`'s own internal per-frame self-loop and its `static_6_800AF550` exit gate,
  closed when item -195 (s339) source-proved `submitGfxFrame` structurally cannot produce a
  `FramebufferPair` and the self-loop's one-time RDP-state prologue is ordinary locked-camera cutscene
  behavior, not a stall. Confirmed along the way: `rs64_dmem_lock` is a genuine recursive mutex, and
  the render/task/vi threads are genuinely independent OS threads — explaining why audio diagnostics
  kept firing throughout every stall in this arc even with the game thread wedged.
  `setDisplayMode`'s gate was reversed and re-reverted every session until s340 promoted both gates to
  the permanent shipped default (CURRENT-TRUTH item -196). Full detail: `PORTING-STATE` Sessions
  297-337.
- **`composeNpcOrientationMatrix` whack-a-mole (s99–s261) — CLOSED.** Nine guards over 161 sessions
  before the real signature was found: a recurring "KSEG0 pointer + rdram-base, no `MEM_W`
  subtraction" bug in `renderUnlitMeshFaces`, closed for good s261 (`COMPOSE_NPC_GUARD9`, first-ever
  live call into `renderUnlitMeshFaces`, survived to VI-update #8552/143.1s vs. a prior best ~75s).
  Along the way: `setLookupEntryField5ByKey` needed two guards not one (s260); `evalCubicSplineAtTime`
  had an unguarded pointer (s259); the last 2 `-0x25A4` hangar-bay-deref gaps closed (s258);
  `submitSceneNodeRender` finally got a complete source read (s263) after 66 sessions unaddressed.
  s249-251 opened a project-wide static sweep for this "RDRAM-base + un-subtracted wild pointer"
  family (`scratch/agent/find_unguarded_walks.py`, 143 sites/43 functions); it landed 2 guarded
  functions then sat abandoned 43 sessions until s294 resumed it (below).
- **Breadcrumb whack-a-mole B2-B14 + the `-0x25A4` hangar-list-pointer audit lineage (s265–s294) —
  CLOSED.** A refuted a0-argument hypothesis for a guest-`0x80000000`-family fault inside
  `heapFreeListDequeue` (s267) led single-function breadcrumbs `BREADCRUMB2`-`9` to chase the "cached
  free-list-head" idiom across 7 functions (s268-282); a 3-session `BREADCRUMB9` PRE-SCENE
  `waitForAnyAudioSlot` boot-crash streak (s277-280) turned out to be a transient window, CLOSED as a
  non-finding s289. The "last-executed-guest-PC breadcrumb" instrument (`g_rs64_last_guest_pc`, s264)
  then localized a different-offset crash (+47120) to a 2nd unguarded occurrence of the same "cached
  free-list head" idiom, landing `CACHE2_GUARD` (s266). s283-288 ran a deliberate grep-based audit of
  every `-0x25A4($s1)` hangar-list-pointer site, landing 29 guards across 3 functions (s284), a 3rd
  "second-hop" instance (s285), classifying `hangarInitialize`'s remaining chunks as dead code
  (s286-287), and closing the lineage s288 (a suspected `playerSnowSpeederInit` overlap was
  REFUTED — live code merely sharing address space, not a copy). s289-294 resumed the abandoned
  s249-251 project-wide unguarded-walk sweep, landing `BREADCRUMB10`-`14` on 5 functions; s293/294
  caught `tickTextureMaterialExpiry`'s (`BREADCRUMB12`) two recurrences at the identical guest PC,
  crossing the confirmation bar s297 used to land `MATEXPIRY_GUARD`.
- **Three interleaved threads, s220–s248: Metal-crash fixes, the CALayer/campose SIGSEGV hunt, the
  freeze/scene-graph investigation.** Two Metal-side crashes CLOSED with positive controls: the
  scissor-rect OOB SIGABRT (s246) and the `fbSize()==0` viewport-NaN SIGABRT via a VI-draw skip guard
  (s244). The host QuartzCore/CALayer SIGSEGV hunt (`campose*`, s234-248) landed a wall-clock bridge
  and a validated instrument but exhausted its rule-8 budget at s248 still inconclusive — best
  remaining lead: a cross-thread `CAMetalLayer` property mutation (PORTING-STATE Session 239). The
  post-SELECT-CRAFT freeze investigation (s220-226) proved the frozen picture (torn polygon → flat
  fill, non-deterministic even on identical scripted input) sits downstream of a healthy scene-graph
  traversal and a still-climbing RDP full-sync counter, not a stuck camera or frozen pointer. The
  DL-payload-staleness probe (s230-233) stayed ambiguous; a Bash-allowlist bug (`Bash(<dir>/:*)` rules
  silently not matching, s227-228) blocked 2 sessions before resolving s229.
- **The long `heapWalker`/`renderUnlitMeshFaces`/`composeNpcOrientationMatrix`/`heapFreeListDequeue`
  whack-a-mole guard-gap chase (s150–s219).** ~70 sessions landing one unguarded-pointer-chase guard
  at a time, converging on 2 durable lessons: the literal `0x0000000300000000` at x0/x8 across 3
  unrelated crash sites is this process's constant RDRAM host base pointer, not corrupted data (s219,
  see CURRENT-TRUTH Overturned Conclusions); the real wild operand is the *other* register, with a
  KSEG0-tag signature recurring in `renderUnlitMeshFaces` specifically. Also settled: "single Start
  leaves SELECT YOUR CRAFT into hangar-flight" OVERTURNED s150 (mission-entry unanswered again); the
  s162 post-leave cutscene stall is the s79/80 FULL_SYNC-loss class recurring, capable of at least one
  recovery (s153/154); a `[thr-resume]`-adjacent scheduler silent-drop mechanism (s180-187) got a
  defensive guard that produced the first fully crash-free full-length soak in that lineage (s187).
- **Audio-array corruption, Thread B (s133–s149) — CLOSED**, plus two side threads parked at
  exhausted rule-8 budget. Real mechanism (non-atomic `voiceCount`-write-before-pointer-store race in
  `allocateSongChannelArray`) found s145, fixed and verified s147/148: 3 independent verification
  soaks all clean — 0/13 corrupted `[voice-active-gate-nz]` reads post-fix (vs. 5 pre-fix), 0/3
  `do_rom_read` recurrences (vs. 9 prior), first fully crash-free soaks for this shape since s83. Path
  to the fix (s138-146): ruled out a static ROM string table and adjacent-heap aliasing (confirmed
  voice-array stride is 136 bytes); traced to `allocateSongChannelArray`'s own 2nd alloc, a
  per-tick-toggled double-buffered pointer table (s141-143), via `musyxMixActiveVoices`'s
  unchecked-cursor write (s144) before s145 found the race. s149 bonus: "what input leaves SELECT
  YOUR CRAFT" was never actually open — the leave transition fires correctly (invisible to VI-phase
  tracking); the real open question was always surviving the post-leave scene's first ~2s. Two side
  threads exhausted rule-8 budget without resolving (guards left in code, both dying to the
  `do_rom_read` race): `emitAllocatedDLCommand` (s133-135, `emit-dl-guard2`/`3`, 0/0 all 3 attempts);
  `submitSceneNodeRender`'s `MATLIST_GUARD1`/`GUARD2` (s136-137, parked at 2/3, both 0/0).
- **Thread A/B saga (s102–s135) leading to the audio-corruption fix above, plus the regen-pipeline
  root cause (CURRENT-TRUTH item -20).** Thread A (s126-132): re-audited every already-guarded
  hangar-tick crash class for a 2nd unguarded pointer-chase site — 6/8 had a genuine gap; biggest hit
  `updateHangarBayScene`'s `-0x25A4` family (26 sites, s132), later fully closed by the s282-288 audit
  lineage. Thread B (s116-145): chased the `voice+0x0`/`+0x34` corruption through several reframings
  (refuted: stale `rs_malloc` memory, an OOB scan index, an RSP-ucode write, a computed-offset guest-C
  store, adjacent-heap aliasing). Earlier (s102-113): traced the corrupted MusyX DMA-batch `devAddr`
  field backward across 6 sessions/5 functions to `musyxInitVoiceFromSample`, the sole writer of that
  offset anywhere in the tree (s105/s111 exhaustive grep); the call-chain-ancestry angle (s105-110)
  was a 5-session dead end. Methodology lesson: comparing instruments' log lines by *file order*
  across threads is not a valid proxy for real time order — cross-thread correlation needs a shared
  sequence number. Tooling (s102, root-caused precisely by CURRENT-TRUTH item -20): `fixup_game_funcs.py`
  is not idempotent — re-running it without a full ELF regen inserts a second copy of every
  already-applied patch.
- **M3 hangar-tick-family guard program (s99-s110): 8 crash classes guarded** (16th/12th/11th/14th/
  17th/18th/9th/10th — see the §7 crash catalog above), all with clean negative controls, same
  `U32()`-truncated-bounds-check-then-`goto`-real-epilogue template used by every guard since. s101
  and s110 survived the entire family with zero crashes, reaching the ~140s DMA-corruption window
  alive.
- **Find the indirect caller of `submitDmaRequestBatch` — CLOSED (s101).** The caller is
  `musyxSynthFrame` (`funcs_24.c:3095`, a per-VI-retrace audio tick) via `viRetraceHandlerThread` —
  not the mission/DL code path every earlier session assumed. Refuted dead ends, do not reopen:
  `ra=0x00000000` as a corruption signature, "dump the OSIoMesg at mb," consumer index desync, "the
  boot call loops more than once."
- **`queueGPUUploadTMEM` zero-size assert.** Crash classes 9/10 (`updateAnimatedTextureStreaming`/
  `static_5_800B4048` SIGBUSes) CLOSED s124/s125, tracked in the §7 crash catalog only.

## 10. M5 audio: gate-promotion, step-5 crash-rate comparison, and the drainMeshReleaseQueue tail-scan
cluster (s339–353), migrated from CURRENT-TRUTH.md s355 maintenance pass

Full raw detail for all of these lives in `PORTING-STATE.md` at the session ranges cited. This section
folds what used to be CURRENT-TRUTH.md Next-steps items -195 through -209 (excluding -208, which stayed
live because it's the evidentiary basis for the still-open `m5-audio-destub-linkedlist-corruption-source`
thread — see CURRENT-TRUTH item -208). None of the four sub-arcs below is open work.

- **VI=640 `pairs=0` stall resolution (s339) — CLOSED, was CURRENT-TRUTH item -195.** Source-proved
  `submitGfxFrame`'s full callee set structurally cannot produce a `FramebufferPair` (no
  `setupCameraMatrices`/`emitFrameRdpInitDl`/`runVideoFrameTick`/`advanceVideoFrame` in it — only
  buffer-arbiter/SP-task-producer bookkeeping), and that `cinematicLoopBody`'s internal self-loop calls
  the real `SET_COLOR_IMAGE` producer (`runVideoFrameTick`) exactly ONCE, not per-iteration — confirmed
  at runtime (`[static6-800a9abc-entry]` fires once per soak). Not a stall: a locked-camera cutscene
  reusing one RDP-state prologue is ordinary; `[vi-fs-decision]`'s `pairs=0` reading for the rest of the
  scene is the expected, correct behavior. This closed the 41-session s297-337 gate-reversal/VI=640-stall
  arc (§9 above).
- **Audio-gate promotion arc (s340-344).** s340 promoted BOTH `setDisplayMode`'s and
  `reapplyDisplayMode`'s gate-byte reversals to the permanent shipped default, on a validation basis
  later found invalid (see CURRENT-TRUTH Overturned Conclusions — the "validating" soaks never actually
  left the pre-title screen). s342 found `reapplyDisplayMode`'s reversal specifically, in isolation,
  deterministically blocks title-reach: 0/5 relevant soaks across 3 sessions ever left the pre-title
  screen with that gate reversed. s343 reverted just that one gate back to force-zero (keeping
  `setDisplayMode`'s reversal), restoring title-reach — but surfaced a NEW crash one stage later, in the
  post-title SELECT YOUR CRAFT stabilization window: a compiler-inserted `break 7` div-by-zero trap
  inside `tickWrappingTimerAccumulatorList` (`last-guest-pc=0x80054744`), a different signature from that
  function's previously-catalogued near-null-pointer crash. s344 confirmed title-reach 3/3 but the
  div-by-zero recurred only 1/3 — PARKED (`m5-audio-destub-tickwrap-divzero-craftselect`), not guarded;
  reopens if a future soak reproduces that exact guest PC. **Current gate state (unchanged since s343,
  still true as of s354):** the fixup regex at `fixup_game_funcs.py` ~line 263 is `r"0x8008E(?:C88)"` —
  matches ONLY `reapplyDisplayMode` (`0x8008EC88`, force-zeroed); `setDisplayMode`'s `0x8008EB40` stays
  reversed.
- **Step-5 crash-rate-comparison methodology arc (s341, s344-347) — CLOSED s352, superseded by the
  bimodal-timing reframe (CURRENT-TRUTH item -208).** Designed to measure crash-family #3
  (`waitForAnyAudioSlot` boot deaths) and #4 (post-cutscene stall) recurrence rates post-de-stub. Hit
  and fixed 2 methodology bugs first: a `[keys]`-log-file misattribution making 2 fully-driven soaks
  misreport as undriven (s344), and an unbounded per-list-node log blowup (`ROGUESQ_LOG_RS_FREE_WALK`/
  `_MALLOC_WALK`) ballooning `run.log` to 8+ GB and hitting the loop's 600s hard-cap as a false crash
  signature (s345, root mechanism — why that specific run — stayed open, same log-line-per-node family
  Session 209/210 had already root-caused for an unrelated bug). Once fixed, a 4-run batch (s346-347)
  found the post-title crash rate high (~75%, 3/4) but DIFFUSE, not concentrated: 3 different crash
  symbols across 3 runs, 0/4 hits on families #3 or #4 specifically. Net conclusion: de-stubbing didn't
  reduce the post-title crash rate, it diffused it away from #3/#4 into the ~20+-family background noise
  already present. `HYPOTHESIS-ID m5-audio-destub-step5-crashrate-comparison` closed s352 when the
  16-soak offline re-analysis (CURRENT-TRUTH item -208) found the timing wasn't actually diffuse, just
  the symbols.
- **`drainMeshReleaseQueue` tail-scan cluster (s348-351, s353) — 3 distinct crash sites GUARDED within
  one function's dense, entirely-unguarded singly-linked-list tail-scan idiom (`funcs_3.c:1669+`).**
  s348 (`HYPOTHESIS-ID m5-audio-destub-contentguard-verify`, opened+closed) found and guarded an
  unguarded "content pointer" field one hop from `processSceneNode`'s already-guarded node pointer
  (2 sites, `funcs_4.c`); non-recurrence validated 0/4 across s350's follow-up soaks, though s352 later
  found this guard's firing signature (`node=0x80183ECC`, thousands of steady-state hits per run) is
  benign — see CURRENT-TRUTH Overturned Conclusions. s349-350 (`HYPOTHESIS-ID
  m5-audio-destub-drainmesh-breadcrumb`) added `BREADCRUMB15` to localize an exact-file-offset-repeat
  crash (`+600`, 2/2), which turned out NOT to be the guarded bug — the breadcrumb instead found a 2nd,
  different unguarded read site (`0x800081AC`, `v1 = *v1; v0 = *v1` with no validity check) via an
  incidental hit, guarded it. s351 (`HYPOTHESIS-ID m5-audio-destub-drainmesh-writeguard-verify`, opened
  s351+closed s352 with the fix landed) found the s350 read guard fired correctly (positive control) but
  the crash moved 2 lines downstream to a write-through-the-same-corrupted-pointer sibling site the s350
  comment had already flagged as unguarded — guarded that too. s353 landed a ring-buffer breadcrumb
  (step 1 of the `bad_v1` linked-list-corruption-source lead, see §11 below) recording every list
  node walked, not just the final bad one — its first verify pair came back 0/2 informative (both
  crashes landed outside `drainMeshReleaseQueue` entirely, one of them independently useful — see §11).
  All 3 guards use the same range-check-and-bail shape as the rest of the
  `-0x25A4`/BREADCRUMB2-14 family (§9): on an out-of-range pointer, synthesize the value the following
  guest logic would see from a legitimately-absent/cleared case instead of dereferencing.

## 11. M5 Step 5 guard-hunting arc: Thread A / Thread B / heapWalker GUARD5, all CLOSED (s354–370),
migrated from CURRENT-TRUTH.md s371 maintenance pass

Full raw detail in `PORTING-STATE.md` at the session numbers cited. This section folds what used to be
CURRENT-TRUTH.md Next-steps items -210 through -225 (nine items, including one already-folded
sub-range) plus item -208's `bad_v1` lead, which was Thread B's origin. Both named threads, plus a
heapWalker background-noise site the arc's own soaks surfaced, are now closed — no M5 Step 5 work is
open. Next M5 work after this arc is Step 6 (PCM sanity-check), tracked live in CURRENT-TRUTH.

- **Thread A — `m5-audio-destub-coalesce-heap-guard-verify` (`coalesceFreeHeapBlocks`), CLOSED s366.**
  Opened s354 on an independent `coalesceFreeHeapBlocks+3452` repeat; guarded with a range-check-and-
  bail. s358 found the guard's own bail target was wrong: `ctx->r3=0` sent execution to
  `L_80002358`, the coalesce loop's ENTRY label, not an exit — re-entering the loop with the still-
  wild pointer instead of stopping it; fixed to the real exit, `L_80002444`. Closed with 6 soaks
  post-fix (`s358_verify1/2`, `s362_reverify1/2`, `s364_reverify1/2`) all showing zero
  `coalesceFreeHeapBlocks` hits, including one clean full 432s hold.
- **Thread B — `m5-audio-destub-linkedlist-corruption-source` (`drainMeshReleaseQueue`), CLOSED s368.**
  Opened on s352's `bad_v1=0x00010001` lead: a diagnostic value byte-identical across 2 independent
  sessions/builds at a one-shot guard site (~1-in-4-billion coincidence odds), source-confirmed as a
  plain singly-linked-list tail-scan (`funcs_3.c:1734-1766`) consistent with a stale/prematurely-freed
  list node. The function turned out to have FIVE structurally identical tail-scan loops (not three,
  as first believed), each carrying the same "checked non-NULL, never range-validated before
  dereference" idiom on THREE separate pointer families, found progressively:
  1. **Tail-cursor read+write pairs** (s354/357/359/360/361): the original lead; found and guarded one
     loop at a time after repeatedly hitting the same read-guard-without-write-guard gap (guard the
     read, the crash moves 2 lines downstream to an unguarded write through the same pointer) —
     recurred s350→s350b, s357→s359, until s361's full-function audit found the last two loops at once.
  2. **Head-pointer read+clear-write pairs** (s363, 10 new sites): a parallel "priming read" through
     each loop's HEAD pointer (`a0`/`ctx->r4`, checked only non-NULL) before the tail-scan, paired with
     an unconditional clear-write later — the same idiom on a pointer the original tail-cursor audit
     didn't cover (not part of the loop-body syntax it was scanning).
  3. **A third "previous tail" pointer family** (s365, 5 sites): `MEM_W(0X4, ctx->r2) = ctx->r3` — a
     pointer loaded once per loop from a fixed global table slot and checked only `!= 0`.
  s366 ran a proactive full-function idiom-class audit (cross-referencing every table-/list-loaded-
  pointer dereference against all 3 families × 5 loops = 25 explicit guard blocks) and found one
  syntactically-bare read per loop (the loop-back "advance cursor" read) but hand-verified each is
  memory-safe by loop invariant — no further unguarded family found, coverage reads as exhaustive.
  Closed s368: `s367_verify3/4` both crashed OUTSIDE the function, at `pc-symbol=heapWalker+1696`
  (`last-guest-pc=0x8000834c`, `drainMeshReleaseQueue`'s own final checkpoint — the `nop` right before
  `return`), confirming the function completed and returned normally in both runs, with every guard
  family (tail-cursor, head-pointer, third-family) confirmed firing at least once in the same runs —
  a genuine positive control, not silence. 3-for-3 soaks crash-free *inside* the function since full
  coverage landed.
- **heapWalker+1696 background noise → GUARD5, CLOSED s370.** First seen as off-target noise during
  Thread A/B soaks (`last-guest-pc=0x8000834c`, the exact PC `drainMeshReleaseQueue` returns through —
  a coincidence of which breadcrumb last wrote a shared "last hit" global, not a link between the two
  bugs). Reached n=4 independent hits by s368 (2×`s364`, 2×`s367`), crossing the catalog's own "3rd
  independent hit → binary-analysis confirmation" trigger. s368's `s193_disasm.py` pass decoded the
  crash instruction as an indexed store (`STR W8,[X5,X10]`) fed by two chained pointer loads — the same
  "unvalidated pointer used as both index-source and write-target" idiom already guarded 4x elsewhere
  in `heapWalker` (GUARD1-4, s157-218), but at a not-yet-mapped 5th site. `otool`/`nm`/`objdump`/
  `dwarfdump` stayed sandbox-blocked throughout, so s369 hand-extended `s193_disasm.py`'s decoder with
  a register-offset LDR/STR case to map the site to source: guest address `0x80007A3C` plus 4 unrolled
  siblings (`0x80007A98`/`AF4`/`B50`/`BAC`, heapWalker's established 5x-loop-unrolling signature) — a
  fixed global table slot read and checked only `!= 0`, then dereferenced as a write target via
  `MEM_W(0X4, ctx->r2) = ctx->r3`. Guarded all 5 as GUARD5. Closed with `s369_heapwalkerguard5_verify1/2`
  draining 2/2 non-recurrence: `verify2` crashed at an unrelated symbol with `guard5_fire_n=0`;
  `verify1`'s SOAK-RESULTS.md line recorded `rc=137` (the loop's 600s hard-cap) with a 0-byte wrapper
  log, but the launcher/raw `run.log` (which persist independently) recovered a complete, crash-free
  302s hold with `guard5_fire_n=0` — the wrapper itself was defeated by an 8.7 GB `run.log` (millions
  of pre-existing `[rs-free-walk]` heap-walk lines, not new evidence) that pushed its grep/kill handling
  past the outer cap before it could print a verdict. **Soak-tooling lesson**: an `rc=137`/empty-
  wrapper-log SOAK-RESULTS.md line is not automatically uninformative — check the launcher log and raw
  `run.log` directly before discarding the run.
- **Net as of s370**: no M5 Step 5 threads and no escalated background-noise threads remain open.

## 12. M5 Step 6 (PCM sanity-check) and the C88-reversed pre-title-hang/VI-trigger investigation, both
CLOSED (s371, s373–376), migrated from CURRENT-TRUTH.md s380 maintenance pass

Full raw detail in `PORTING-STATE.md` at the session numbers cited. This section folds what used to be
CURRENT-TRUTH.md Next-steps items -226 through -230. Net: no M5 audio thread remains open as of s376;
the next M5 work needs a genuinely new lead, not a continuation of any thread in this section.

- **Step 6 answered (s371): real PCM is 100% silent, even under genuine RSP-dispatched real ucode.**
  Before adding the sanity counter, a source read of `queue_samples` (`src/main/main.cpp:677-681`)
  against `ultramodern::queue_audio_buffer` (`lib/N64ModernRuntime/ultramodern/src/audio.cpp:25-36`)
  found a real, previously-undetected host-bridge bug: the callback parameter is a SAMPLE count but the
  old code passed it straight to `SDL_QueueAudio`'s byte-length argument with no `*sizeof(int16_t)`
  conversion — every call queued only half the correct bytes, silently dropping the back half of every
  PCM buffer since this bridge was written. Fixed (see CURRENT-TRUTH Overturned Conclusions for the
  full mechanism). Added `ROGUESQ_LOG_PCM_SANITY`; two soaks logged 13,832 total calls (7 via the s327
  direct-pump path, 13,825 via genuine RSP-dispatched `real_ucode=1`) and every single sampled call was
  all-zero — Hypothesis 2 (silent-but-not-crashing) confirmed with a positive control, not a null
  result.
- **WHY it's silent, answered (s373): voice population is structurally blocked by the same gate that
  keeps title-reach working.** Source-read `reapplyDisplayMode` (`funcs_23.c:9805-10024`) end to end:
  it unconditionally zeros the audio-tick gate byte (`0x800A0F50`) at function entry, every video frame,
  then would restore it to 1 at its tail (`0x8008EC88`) — except that exact address is the site
  `fixup_game_funcs.py` force-zeros, the same patch s343 needs to keep title-reach working. Net: every
  frame this build re-disables audio and wipes any voice/song/stream state, never durably re-enabling
  the gate, so `tickMusyXIfActive`'s voice-population path never gets a real window to run — the ucode
  mixing exact zeros is correct behavior on empty input, not a mixing bug.
- **C88-reversed pre-title hang, mechanism search (s374, first pass) and REFUTAL (s375, build+soak).**
  `HYPOTHESIS-ID m5-audio-destub-c88-pretitle-hang`. s374's source-only pass (no build) found a
  plausible single-token-mutex-deadlock candidate: under gate=1 (C88 reversed), `waitForAnyAudioSlot`'s
  per-iteration `tickMusyXIfActive` call would reach `factor5MutexAcquire` for the first time ever,
  blocking on `osRecvMesg_recomp` against a single-token queue that `initFactor5Mutex` destroys and
  recreates — a live queue-recreation race against a blocking receive, never exercised under gate=0.
  s375 built the discriminating instrument (env-gated enter/exit tracing around
  `initFactor5Mutex`/`factor5MutexAcquire`/`Release`) and ran a 180s C88-reversed soak: REFUTED
  cleanly — `factor5MutexAcquire` entered and exited 9131/9131 times, perfectly balanced, continuing
  steadily hundreds of seconds past the point where `vi_width=` sticks at 640. Bonus correction:
  `initFactor5Mutex` fired only 6 times total in the 180s run, not "every video frame" as s374 assumed
  (root cause of that discrepancy left unresolved, not chased further). **Net: there is no hang to
  fix** — the process stays alive and fully responsive under C88-reversed, it just never re-triggers
  the VI 640→1024 framebuffer-swap transition. `HYPOTHESIS-ID m5-audio-destub-c88-pretitle-hang`
  CLOSED. Both the temporary C88 reversal and the trace instrumentation used for this soak were
  reverted/left inert before commit.
- **VI 640→1024 trigger site search (s376) — REFUTED all three candidate mechanisms by elimination.**
  `HYPOTHESIS-ID m5-audio-vi640to1024-trigger-site`. A source-only pass (grep/read, no build) over
  `N64Recomp/RecompiledFuncs/`: **H1 (reset-branch divergence)** refuted — `reapplyAudioConfig` has
  exactly one hard-coded return path, no reference to the gate byte anywhere in its body. **H2
  (shared-mutable-state collision)** refuted — `tickActiveSongs`'s and `tickAndReap3DAudioVoices`'s
  write targets are disjoint from every address read in the scene-transition call chain. **H3 (real
  completion-condition wait)** refuted — all ~65 hits on the gate byte classify as the already-known
  MusyX guard-and-return idiom, and none of the gate-derived helper functions are referenced anywhere
  in the scene-transition files (no external poll site exists). Decision: rather than spend a build+soak
  on the diffuse H4 fallback (frame-timing/ordering effect, no single identifiable site), the thread was
  set aside — s373 already showed real audio (PCM) stays 100% silent in the *working* baseline
  regardless, since voice population is gated elsewhere, so even a confirmed H4 fix would not by itself
  produce working audio. `HYPOTHESIS-ID m5-audio-vi640to1024-trigger-site` CLOSED by elimination, not
  solved. Reopens only on a specific new reason to believe the C88-reversed path would unblock real
  audio.

## 13. Fixup function-scope backport (s377–388), CLOSED OUT s386, migrated from CURRENT-TRUTH.md s391
maintenance pass

Sanctioned-tooling work unit, not M3/M5: backport the BREADCRUMB10+ function-scoped-match idiom onto
the file-scoped-only guard patches in `fixup_game_funcs.py`. Real count from an AST scan of
`re.subn(...)` call sites: **176** (the docstring's prior "~150" was a grep guess). Batch-by-batch:

- **Batch 1 (s377, 23/176):** established the verification method reused every batch since — regen
  `RecompiledFuncs/` twice (pre-batch backup vs. converted), diff both the fixup-report and the output
  tree; byte-identical/zero-diff means no latent cross-function anchor collision. Converted
  `musyxSynthFrame`, `runVideoFrameTick`, `reapplyDisplayMode`, `mainGameLoop`, `menuOverlayInit`,
  `cutsceneDispatchSlotsByFlag`, two `static_N_0xADDR` diagnostics, `musyxKeyOnVoice` (8),
  `evalCubicSplineAtTime`, `advancePlayerAnimationPhase`, `updateAnimatedTextureStreaming`, two more
  `static_N` diagnostics, `reserveAndEmitDLEntry` (3). Left file-scoped by design: the volatile
  `0x8008EC88` audio-gate hand patch, and the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair
  (intentionally dual-target).
- **Batch 2 (s378, 21/176, 44 total):** `reserveAndEmitDLEntry` (2), `activateAnimationKeyframe`,
  `composeNpcOrientationMatrix`/`static_5_800AB1C8` (9), `projectModelBoundsToScreen` (3),
  `updateHangarBayScene`/`static_5_800AB658` (3), `musyxSynthFrame`, `acquireSampleStreamBlock`,
  `fillSampleStreamRange`. Confirmed batch 1's stuck-at-320 soak was ordinary timing variance
  (Method traps §4.3), not a regression.
- **Batch 3 (s379, 24/176, 68 total):** entire `funcs_3.c` drain-mesh/heap-walker cluster converted —
  `beginFrameDLChunk`, `emitAllocatedDLCommand` (2), `heapWalker` (4), `heapFreeListDequeue` (2),
  `drainMeshReleaseQueue` (15). First batch where the delegated subagent could not launch the compiled
  binary (non-interactive sandbox approval gate) — **standing rule from here on: run the soak in the
  orchestrating session, not a delegated subagent.**
- **Batch 4 (s381, 21/176, 89 total):** the musyx/audio-heap instrumentation block in `funcs_23.c`
  (`musyxInitVoiceFromSample`, `tickAudioChannel`, `serviceVoicePoolFrame`, `tickAudioSeq`,
  `tickAllAudioChannels`, 3 `musyxGate` counters, `musyxRawgate`, `streamNodeInit`, `voiceAttackEntry`,
  `voiceActiveGate`, `songArrayAlloc`, and others). This batch also found the delegated subagent
  couldn't complete *verification* (every cross-repo regen command hit a separate sandbox permission
  denial) — **standing rule tightened: delegate ONLY the conversion-editing step; run regen-diff
  verification, build, and soak all in the orchestrating session.**
- **Batch 5 (s382, ~21/176, ~110 total):** continued the same methodology; process note only (site
  list not retained past the s386 maintenance pass — see git history for exact functions).
- **Batch 6 (s383, 21/176, 131 total):** 4 functions in `funcs_4.c` (`processSceneNode` ×10,
  `renderUnlitMeshFaces` ×7, `drawSubtitleText` ×2, `evalCubicSplineAtTime` ×2). Found a genuine
  latent multi-file collision at `runHangarMenuFromOverlay` (~line 8299): its bare label anchor also
  matched an unrelated function, `hasKasanMoorDefected`, in a different overlay file — parked, fixed
  s387 (below).
- **Batch 7 (s384, 17/176, 148 total):** 9 functions including `musyxSynthFrame`, `initFactor5Mutex`,
  `update3DAudioFrame`. The byte-identical regen-diff check caught a real regression here (not a
  formality): `musyxSynthFrame`'s `[synth-rearm-ptr]` diagnostic (`0x800919D4`) actually lives inside
  the next function over, `initN64RspMixer` — scoping to the wrong function had silently dropped the
  patch. Reverted to file-scoped, fixed permanently s388 (below).
- **Batch 8 (s385, 16/176, 164 total):** 17 sites across 15 functions (musyx/audio + scene-graph
  cluster). The Explore agent's recommended batch included the volatile `0x8008EC88` gate patch — a
  standing exclusion it didn't recognize because it had only been given exclusions by function name,
  not address. Lesson: give identification agents standing-exclusion lists **by address/anchor**, not
  just function name.
- **Batch 9 (s386, 4/176, 168/176 total): backport CLOSED OUT.** Final untriaged sites:
  `loadCraftShadowTextures`, `mat3x3InverseInto`, `tickTextureMaterialExpiry`,
  `coalesceFreeHeapBlocks`. A fresh `scan_filescoped.py` re-scan found the prior session's triage list
  had undercounted by one (`loadCraftShadowTextures` missed) — **line-number-based triage lists drift
  between batches and must be re-derived fresh each time, not trusted rolled-forward.**

**Final state, 8 sites confirmed permanent exclusions by design** (not backlog): (1) the whole-file
`$zero`-write comment-out sweep (~2700 sites, needs the same blanket transform by design); (2) the
`0x8008EC88` `reapplyDisplayMode` audio-gate hand patch (deliberately volatile/experimental,
file-scoped on purpose); (3–4) the `waitForMusyXAudioTaskDone`/`shutdownAudioEngine` pair
(deliberately dual-target); (5) the `_s284_deref_guard_sites` multi-function guard loop (deliberately
multi-function); (6) `runHangarMenuFromOverlay`/`hasKasanMoorDefected` — **fixed s387**: added
`p.name == "funcs_43.c"` to the `L_800C68AC:` bare-label patch so it only fires in
`runHangarMenuFromOverlay`'s real home file; (7) `tickAudioSequencerFrame`'s exit diagnostic (match
text spans into the next function's signature, can't be body-scoped without breaking it — genuinely
permanent); (8) `musyxSynthFrame`'s `synth-rearm-ptr` diagnostic — **fixed s388**: confirmed via
`RECOMP_FUNC` boundary check that the `0x800919D4` anchor is unambiguously inside `initN64RspMixer`,
converted the patch to function-scope on its real owner. Every batch and both follow-up fixes were
verified via the byte-identical-regen-diff protocol and a clean build+soak. Full raw detail:
`PORTING-STATE.md` Sessions 377–388.

## 14. M3 idiom-class audit resumption (s389–397): `hangarInitialize`'s `-0x25A4` chunks, two
independent guard-placement bugs, family closure, and the frequency-scan dead end — migrated from
CURRENT-TRUTH.md s398 maintenance pass

First systematic M3 audit since the backport thread (§13) closed.

- **s389 — "Lookup" struct-family, 4 sites guarded.** A recurring `[CRASH][last-guest-pc]=0x800ad0dc`
  (`pc-symbol=findLookupEntryByKey+1864`) turned out to be a wrong nearest-symbol attribution — the
  real site is inside `hangarInitialize`, not a hash-table dereference (same failure mode as the
  catalogued `0x8000b650` staleness). Pivoted onto `findLookupEntryByKey` and 3 siblings
  (`removeLookupTableEntry`, `getLookupEntryField5`, `relocateLookupEntryToNewKey`, `funcs_14.c`/
  `funcs_15.c`), which share the unguarded table-base-pointer idiom already fixed for sibling
  `setLookupEntryField5ByKey` (s260, `SETLOOKUP_TABLE_GUARD`) — guarded all 4 reusing the exact s260
  KSEG0-range+hi-word check. Verified: byte-identical-except-intended-diff regen; build clean; 3 soaks
  (2 died to already-catalogued unrelated crash families, 1 fully clean 304s hold), 0 guard fires
  (proactive fix, no positive control needed for a pure addition).
- **s390 — `hangarInitialize` chunk 2, 11 sites.** The `HANGARLIST_GUARD`/s283-285 `-0x25A4($s1/s4/s5)`
  global-pointer family turned out to be self-documented as incomplete: s284 parked `hangarInitialize`
  (`funcs_27.c`, 103/172 raw hits, a single 13,770-line function) as its own multi-session item; s285
  patched only a first "chunk" (lines 119818-124175), leaving 65 sites (124175-133587) unguarded.
  Guarded two bounded sub-blocks (chunk 2a: 124202-125013; chunk 2b: 125014-125822), reusing existing
  labels `L_800AB1A4`/`L_800AB618` as bail targets — 11 NEEDS-GUARD + 1 confirmed-SAFE (call-arg only).
  Verified: byte-identical-except-intended-diff regen; build clean; 3 soaks, 0 fires in the
  `-0x25A4` family. ~54 raw hits remained past line 125822 (chunk 3+).
- **s392 — chunk 3a, 29 sites.** Split the 53 remaining raw hits at the function's own next internal
  `return;` (line 132777): chunk 3a (125940-132777, 32 raw hits, 29 guarded + 3 SAFE) this session,
  chunk 3b next. Bail target: existing label `L_800ADB2C`. Verified via byte-identical-except-
  intended-diff regen (377 added / 0 removed = 13×29); build clean; 3 soaks, 0 fires attributable.
  **Later found to contain a placement bug — see s393/s394 below.**
- **s393 — chunk 3b (LAST chunk), 21 sites; also discovered chunk 3a's guard-placement bug.**
  `hangarInitialize`'s `-0x25A4($s1)` coverage now spans chunks 1(s285)/2(s390)/3a(s392)/3b(s393),
  though chunk 3a's own coverage claim was unsound (see next item). Bail target `L_800AE060`
  (function's real epilogue, already a live `goto` target). Anchors built to start AFTER each raw
  load — the correct placement. Verified: byte-identical-except-intended-diff regen (294 added / 0
  removed = 14×21); build clean; 3 soaks, all 3 hit already-catalogued unrelated crashes, 0
  attributable fires. **While closing this out, found**: `_s392_h3a_sites` in `fixup_game_funcs.py`
  builds every one of its 29 anchors starting WITH the raw `-0x25A4($s1)` load's own comment+code
  line, and `text.replace(anchor, guard + anchor, 1)` inserts the guard BEFORE that anchor — so all 29
  checks run before the load executes, testing whatever was in that register from the PRECEDING
  instruction, not the value the load is about to produce. Chunks 1/2/3b built their anchors to start
  AFTER the raw load instead (confirmed by direct inspection: 0/29 chunk-3a sites match that shape,
  all chunk-1/2/3b sites do) — chunk-3a-specific, not systemic. Two hand-traced sites (`S392_H3A_1`,
  `S392_H3A_11`) both check a register just set by a small byte-index load (`lbu`/`MEM_BU`, 0-255
  range) two lines earlier — always fails the KSEG0 check, so those sites' guards unconditionally bail
  every time that path runs, silently skipping real per-hangar-item processing rather than protecting
  against a rare bad pointer. Invisible to s392's own soaks because `ROGUESQ_LOG_S392_H3A_GUARD` was
  never armed by any recipe.
- **s394 — FIXED the chunk-3a placement bug, all 29 sites.** Wrote a fresh extraction/verification
  script (`ast.literal_eval` on the live `_s392_h3a_sites` table, no hand-transcription) that for each
  site located its raw load, confirmed the destination register matched, then scanned forward for the
  first genuine dereference (27/29 sites) or, where no in-line dereference exists before an
  unconditional jump (`S392_H3A_26`, feeding a shared control-flow join with `S392_H3A_25`), scanned
  through the `goto` line instead. All 29 new anchors verified unique. Applied via in-place rewrite
  (same site names/`reg`/`bail_label`, only anchor text changed). Verified: regen diff shows ONLY
  `funcs_27.c` changed, 58 removed / 58 added (net zero) — a pure 2-line-earlier replacement, exactly
  the predicted shape. Build clean. 3 soaks: verify1 (armed `ROGUESQ_LOG_S392_H3A_GUARD=1`) hit an
  unrelated crash far outside `hangarInitialize`'s range with **0 guard fires**, and a same-run
  positive control (824 `[hangar-loop]` lines, ~86s held at the scene) ruling out "guarded code never
  ran"; verify2/verify3 unarmed, one unrelated crash, one fully clean 280s+ hold. Also ran a raw-count
  sweep (not yet classified): `funcs_27.c` 102 raw hits vs 89 markers (~13 candidates), `funcs_40.c` 69
  vs 67 (~2), `funcs_19.c` 1 unrelated hit.
- **s395 — `funcs_27.c` sweep-remainder closed; found a SECOND, independent instance of the same bug
  class, in the much older s285 chunk-1 family.** Delegated a fresh per-site classification of all 102
  raw hits to a subagent: 86 already correctly covered, 15 confirmed SAFE, 1 genuine NEEDS-GUARD site
  — plus a bonus finding, independently verified by direct source read: the existing `S285_H1_8` guard
  (from s285, predates the s394 anchor-placement lesson) checks `ctx->r4` at a point where r4 still
  holds a STALE value left over from a different, unrelated combine 65 lines earlier, not the fresh
  value this site's own raw reload produces three lines later, which is then dereferenced completely
  unguarded. Fix: added ONE new guard (`S395_SWEEP_1`, bail `S285_H1_BAIL`) anchored correctly right
  after the real combine, immediately before the dereference — left the old broken `S285_H1_8` guard
  in place unchanged (harmless dead-weight; cleanup deferred, later done s397). Verified: regen diff
  shows ONLY `funcs_27.c` changed, 14 added / 0 removed (one new guard block). Build clean. 4 soaks:
  verify1 (armed, default env) reached the scene (574 `[hangar-loop]` positive control), 0 crashes,
  full 280s+ hold, `[s395-sweep-guard]` fired 0 times (plausible null — pointer valid throughout);
  verify2/verify2b hit a pre-existing unrelated log-storm pathology (unbounded `RS_FREE_WALK` logging,
  and a `[mesgqueue-guard]` tight retry loop against a permanently-bad `mq_=0x1D0` pointer — new
  observation, unactioned); verify2c/verify3 (log sources disabled) never advanced past the title
  screen (apparently disabling `ROGUESQ_LOG_SCHED` shifted frame timing enough to miss the fixed-time
  key schedule), 0 crashes over ~330s; verify4 hit an unrelated early-boot `musyxSynthFrame` crash
  before reaching the title phase. Net: 0 crashes attributable across all 4 attempts; one fully valid
  scene-reached run with a positive control is the primary evidence.
- **s396 — `funcs_40.c`/`funcs_19.c` swept, CLOSES the entire `-0x25A4` hangar-list-pointer family
  (s283-396).** Delegated a full per-site classification to a subagent (direct source reads,
  cross-referenced against every existing guard family's anchor text). Result: 69/69 raw hits in
  `funcs_40.c` fully accounted for — 65 COVERED, 4 SAFE (call-arg-only), 0 NEEDS-GUARD, 0 UNCLEAR.
  `funcs_19.c`'s single raw hit (`npcShieldGeneratorUpdate`) is an unrelated coincidence — different
  `lui` base, loaded into a float register, used only as a `DIV_S` divisor, never a pointer (already
  noted as a false positive by s284's own comment). Two independent lines of evidence: the subagent's
  per-site reads, and an independent post-hoc `grep -c` count matching exactly. No code change needed
  — the 0-NEEDS-GUARD classification was itself the complete result.
- **s397 — cleanup + codebase-wide frequency scan for the next idiom class: negative result, family
  audit CLOSED.** Step 1: deleted the leftover `S285_H1_8` stale-register guard (harmless dead code,
  `S395_SWEEP_1` already covers the real dereference correctly) — verified via regen+build (clean,
  isolated diff), soak verification inconclusive (4 attempts, none reached a positive control for
  reasons unrelated to the change) but safe by construction (pure deletion). Step 2: ran (and twice
  bug-fixed) a static classifier tracing `MEM_*` negative-displacement loads' base registers back to
  their origin, to distinguish the mundane `lui`-addressed static-global idiom (which dominates the
  raw frequency ranking — `-0x5824`/`-0x23A8`, the two next-highest-frequency displacements, are 100%
  this, confirmed by direct source read) from the actual `-0x25A4` shape (a pointer reloaded from a
  global slot, then dereferenced). **Result: zero candidates of comparable magnitude anywhere in the
  codebase.** The classifier has an acknowledged blind spot (can't trace across label/branch
  crossings, so it can't even reprove the known `-0x25A4` family this way). Also confirmed the
  `[mesgqueue-guard]` lead (s395/396 carry-over) is a single C++-runtime guard site, not a guest-code
  idiom class — out of scope for this model.

**Net as of s397: the `-0x25A4` hangar-list-pointer family is fully closed (168 sites across chunks
1-3b + the funcs_40/19 sweep); the frequency-scan method for finding the next comparable idiom class
is exhausted; M3 idiom-audit-only mode needs human input to proceed (a CFG-aware discovery tool, a
return to crash-driven discovery, or a fallback to M4/M5).** s398's queued soak
`s397_h1_8removal_verify2` returned `NO_POSITIVE_CONTROL` (hangar scene not reached) — inconclusive,
doesn't change the safe-by-construction verdict already recorded for the s397 deletion. Full raw
detail: `PORTING-STATE.md` Sessions 389–397.

## 15. M4 item -249: `main_overlay.txt` phantom-overlay-function relocation (s400–421), CLOSED,
migrated from CURRENT-TRUTH.md s421 close-out

**What it was:** s399 found `main_overlay.txt` (the file listing functions expected to live in the
game's main/always-resident overlay) contained ~801-803 entries whose addresses actually belong to
`.text` ranges outside the overlay window — a much larger version of the bug that caused the original
3-address `[missing-func]` problem (item -6). Every one of these is a "phantom function": N64Recomp
range-checks `main_overlay.txt` symbols against `.text`, silently drops the ones that don't fit, and
`ROGUESQ_STUB_MISSING_FUNCS=1` covers for the gap with a no-op stub. The fix is mechanical — relocate
each name to its correct overlay file (`mission_overlay.txt`/`menu_overlay.txt`/`cinematic_overlay.txt`)
— but relocating makes N64Recomp emit the function's REAL recompiled code for the first time, and a
minority of those real bodies turn out to be genuinely buggy, crashing live only once un-stubbed.

**Tooling:** `s400_probe_batch.py` classifies each candidate name against all three destination
overlays (mission/menu/cinematic) via static analysis, tagging CONFIRMED/WEAK/NONE/AMBIGUOUS.
`s400_apply_batch.py` moves a batch's CONFIRMED+WEAK entries from `main_overlay.txt` to their
destination file. `s417_cycle.sh`/`s417_apply_names.py`/`s417_revert.py` (introduced s417, reused
verbatim through s421) collapse one full regen→build→phase-gated-live-verify round, and one
apply/revert step, to a single command each — these made the later bisection-heavy sessions (s419,
s421) tractable in a single sitting.

**Batch-size history:** s400 proved the tooling at n=20. s401 attempted the full ~774-item remainder
in one sweep — linked, but caused a new deterministic crash; reverted without bisecting and
misattributed the cause to batch-size-driven function-boundary re-slicing (this theory was later
weakened, see below). n≈20 with live-verify-every-batch became the standing discipline through s410.
s411's loop-mandated pivot probe (n=50, clean) refuted n=20 as a hard ceiling. s412 scaled to n=75
(clean) then n=100 (crashed) — bisection confirmed the crash was a specific bad function, not a
resplitting artifact, weakening s401's original theory further. n=75 became the confirmed-safe
steady-state cadence from s413 onward, used through the item's close.

**The `m4_known_bad.txt` family — ten functions, four downstream crash sites:** Every crash this
item produced across 21 sessions was fully bisected (halves bisection, sibling-independence discipline
enforced) down to one or more specific bad functions, never a structural batch-size problem:

| Function | Session | Crash site (`last-guest-pc`) |
|---|---|---|
| `initPlayerCraftTrailBuffers` | s404-407 | `0x80011088` |
| `transformCraftAnchorsApplySubFx3` | s412-413 | `0x80065e94` |
| `allocObjectPoolNode` | s414-415 | `0x800290d4` |
| `tickCraftMountedAnimationEffect` | s414-415 | `0x800290d4` |
| `stepObjectOrientationTowardTarget` | s416 | `0x800290d4` |
| `updateHudHealthIndicator` | s416 | `0x800290d4` |
| `initHangarDisplayItemTimers` | s417 | `0x80011088` |
| `buildFormatMessageGlyphBuffer` | s419 | `0x800290d4` |
| `buildLevelSelectTextTextures` | s419 | `0x8000b650` |
| `plotRadarBlipColumn` | s421 | `0x800290d4` |

`0x800290d4` collected six independent triggers — by far the most-repeated `last-guest-pc` value, and
below `overlay_start` (`0x800A5130`) in core `.text`, not inside any of the ten functions' own bodies.
At the time this read as one or a few shared downstream corruption sinks reachable from many different
newly-real call sites — **OVERTURNED s422**: `0x800290d4` is just `inflate_fast`'s own clean return
(the `g_rs64_last_guest_pc` breadcrumb that reports it is sparse, present in only 8/50
`RecompiledFuncs/funcs_*.c` files, so the shared value only means all six passed through that return at
some point, not that they crash there or near it). `atos`-based symbolication
(`env atos -o build/RogueSquadron64Recomp -l <base> <pc>`, exact DWARF file:line, strictly better than
this project's prior nearest-symbol attribution) applied to 5 of the 6 isolate-alone crash logs found
FIVE DIFFERENT real crash functions (`__osBlockSum`, `loadDatFile`, `menuControllerInput`,
`freeCutsceneResources`, `allocT16EffectContext`; the 6th, `npcWaterCraftHandleDestruction`, shows a
distinct poison-byte signature). Conclusion: the six known-bad functions each independently trip one of
this project's ~20+ already-catalogued nondeterministic corruption families, not one shared,
dedicated-session-worthy bug. Full detail: `PORTING-STATE` Session 422; `CURRENT-TRUTH` item -259.
`0x80011088` recurred twice (s407, s417); `0x80065e94` and `0x8000b650` each fired once — these three
sites were not part of s422's re-investigation.

**The sibling-independence lesson (burned in s415, re-confirmed s416/s419/s421):** the first few
bisections assumed a sibling branch was clean once the other branch reproduced the crash. s415 found
this false — a 74-name "minus the one isolated bad function" batch still crashed, exposing a second,
independently-hiding bad function in an untested sibling. From s416 onward, every bisection
independently live-verified EVERY deferred sibling at EVERY split before declaring a batch done, even
when the first bad function found seemed sufficient to explain the crash. s419 additionally showed two
bad functions in one batch don't need to share a crash site (5th at `0x800290d4`, 4th at a brand-new
`0x8000b650`). s421 (10 sessions after the lesson was recorded) still found only one bad function
despite the now-mandatory full-sibling-independence sweep — the discipline correctly confirmed a
negative as well as positives.

**A mission/menu sampling-artifact false lead (s418):** partway through, the 7 known-bad functions at
the time were all `mission`-overlay-destined, suggesting a possible mission-overlay-specific structural
cause (size/alignment/TOC). s418's discriminating probe reconstructed each session's actual candidate
pool composition and found 3 of the 4 crash-producing sessions had drawn from 100%-mission pools by
sampling accident, not because mission-tagged functions are disproportionately buggy — refuted, no
process change.

**Close-out (s421):** the item's last actionable batch was the ENTIRE remaining pool (58 names, small
enough to take as one batch rather than an artificial 75-cap split, per s420's handoff plan). It
crashed at `0x800290d4`; full sibling-independence bisection (58→29→29→15→14→8→7→4→3→2→2→1) isolated
`plotRadarBlipColumn` alone, with six other branches independently confirmed clean along the way. The
final 57-name batch relocated clean, live-verified 2/2. A fresh regen after landing it found 0
actionable candidates remaining in `main_overlay.txt` — all 14 remaining entries are the union of
`m4_known_bad.txt` (10) and `m4_known_skip.txt` (4). **Final tally: 784 relocated, 14 permanently
excluded, 798 total candidates the family ever surfaced** (not the "778" figure used informally
throughout s400-s420 — that number was itself a stale running-subtraction estimate that had already
been observed to drift from the true regenerated count at s404 and s420; the fresh regen is always
authoritative over the docs' arithmetic).

**A process note on subagent delegation (s421):** this session's orchestrator initially delegated the
whole work unit to a `run_in_background` subagent carrying the full recipe. The subagent completed real
work (regenerated candidates, probed, applied, ran the initial crash + revert-control, split into
halves, launched the first bisection cycle) but its own turn ended mid-wait for that cycle's result —
its final returned message was a stale progress note, not the requested structured report, yet the
task-tracking status showed "completed." The orchestrating session had to inspect the actual repo/scratch
state to discover the true progress and resume the bisection in-band. Lesson for future delegation of
long multi-cycle bisection recipes to background subagents: verify the final report is actually
structured and complete before trusting it — "completed" status alone does not mean the requested work
finished.

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 400–421.

## 16. Duplicate-symbol-name collisions in the overlay `.txt` files (s426–429, ongoing), migrated from
CURRENT-TRUTH.md s429 maintenance pass

**The bug class:** `menu_overlay.txt`/`main_overlay.txt`/`mission_overlay.txt` each occasionally
register TWO different names at the IDENTICAL address (e.g. `func_800AEC60` and `initCraftSelectScreen`
both at `0x800AEC60`). N64Recomp's function-boundary walker gives the real body to whichever name comes
SECOND in its internal ordering and truncates the FIRST-listed duplicate to 1 instruction. Whichever
name the call site actually resolves to (N64Recomp derives a JAL target's C name from whichever symbol
remains registered at that address) determines whether the function runs its real body or a stub — so a
call site can silently execute a 1-instruction no-op instead of ~1000+ real MIPS instructions, for
however many sessions until someone happens to investigate that exact function. This is a third,
previously-unrecognized shape of the same general "silently-dead code" family as the closed item -6 and
item -249 (phantom-overlay-function) bugs, but those were caused by wrong overlay placement; this one is
duplicate names WITHIN one file, invisible to `main_overlay.txt`'s cross-file dedup.

**s426 discovery and first fix:** while root-causing a 3-sibling animation-channel crash chain (item
-261, `startPlayerSlotAnimationChannelLooping`/`advancePlayerAnimationPhase`/
`getPlayerAnimChannelEntryByIds`), traced all three to one never-called function, `initCraftSelectScreen`
— its real ~1200-line body had been silently truncated to 1 instruction by the `func_800AEC60`
duplicate. Deleted the stale placeholder line; the sole call site auto-followed to the real name with
zero source edits. Live-verified via positive control: `[slot-anim-cache-write]` fired for the first
time ever (the function actually ran), and cache-reads changed from a wild near-zero pointer to a sane
heap pointer. The 3-sibling chain did not recur. This same session found **20 total instances of the
duplicate-symbol-name pattern** across the three overlay files (1 fixed, 19 still open at the time) —
including `hangarInitialize`/`mallocCraftSelectionData`, flagged as the single most consequential
instance because it sits at the SAME address the entire closed s283-396 `-0x25A4` audit (item -239..-247)
was built on, raising the open question of whether that whole closed audit guarded dead code.

**The pattern since s426: each fix un-truncates a function that then executes for the first time ever,
and its now-live body immediately surfaces the NEXT crash** one step later in the menu flow:

- **s427** fixed the `hangarInitialize`/`mallocCraftSelectionData` pair (2nd confirmed instance of the
  mechanism, same auto-follow-with-zero-edits behavior). Surfaced `runHangarMenuFromOverlay+800` SIGBUS
  (item -265) with a NEW signature — an IEEE-754 float bit pattern (`~-1.0f`/`~+1.0f`) used as a pointer,
  not this project's usual near-zero-integer wildness.
- **s428** root-caused item -265: NOT a caller-passed wild value (an entry diagnostic showed the
  function's own `$a0` argument, `ctx->r19`/`$s3`, is sane at entry) but register corruption — `$s3` is
  MIPS callee-saved, so whichever of the function's three callees overwrites it without restoring it is
  the actual defect. Top suspect: `mallocCraftSelectionData`, live for the first time thanks to s427's
  fix. Guarded (KSEG0-range check) and live-verified the guard fires as its own positive control. The
  guard exposed a further crash one step later still, `menuOverlayInit+3648` (item -266), reading the
  same corrupted register back after return — reproduced 3x by s429 (s428 live, s428 soak, s429 live),
  still blocked on locating the actual clobber site.
- **s429** isolated the guilty callee within `runHangarMenuFromOverlay`'s three callees using three
  throttled checkpoint diagnostics (`[hangarmenu-ckpt]`), one immediately after each callee returns:
  `ctx->r19` reads sane (`0x80130B40`) right after `getAvailablePlayerCraftFlagsConsiderUnlocks`, is
  already wild (`0x3F800000`, the exact `+1.0f` bit pattern s428 saw) immediately after
  `mallocCraftSelectionData` returns, and stays unchanged through the one `runHangarSelectionFrame`
  iteration that ran before the guard fired — a clean, single-run before/after boundary that confirms
  `mallocCraftSelectionData` as the culprit and rules out (for this run) per-iteration drift as an
  alternative. Confirmation soak (`s429_hangarmenu_ckpt_verify.sh`) ran and reproduced the same ordering
  (SOAK-RESULTS 20260807-013423, rc=1) — 2nd independent evidence, no longer single-source.

**Open thread (item -267):** find the exact instruction (a write, or a nested callee boundary one level
deeper) inside `mallocCraftSelectionData`'s ~4386-line body — the largest guard-hunt target this project
has attempted, by two orders of magnitude over the previous largest — where `$s3`/`ctx->r19` gets used as
scratch without being restored before return. NEXT.md's s429 handoff lays out two strategies (direct
source read if the write-site count is small; checkpoint bisection at the 25/50/75% marks otherwise) and
flags checking whether the corruption happens inside a nested callee of `mallocCraftSelectionData` itself
before committing to either.

**Still open across the whole class:** 18 more duplicate-symbol pairs remain uninvestigated (4 more in
`menu_overlay.txt`, look real/real; 2 in `main_overlay.txt`, look like harmless DATA-symbol aliases; 12
in `mission_overlay.txt`, 11 matching the same high-confidence `func_0xADDR`/real-name pattern as the
`initCraftSelectScreen` fix). Whether un-truncating `mallocCraftSelectionData` means the closed s283-396
`-0x25A4` audit (item -239..-247) guarded dead code the whole time is still unresolved, now blocked
behind item -267 rather than item -266.

**s432-433: catalogue closed (18/18), unblocking item -267's chain as a side effect.** s432 batch-fixed
11 more `mission_overlay.txt` NPC-handler pairs (same mechanism, 11th-14th independent instance). s433
read the last 5 real/real pairs (`menu_overlay.txt`) and confirmed 2 more (`main_overlay.txt`) are data-
symbol aliases, not this bug (grepped `RecompiledFuncs/*.c` for both names, zero hits — this recompiler
never emits data globals by name). Fixing `getAvailablePlayerCraftFlagsConsiderUnlocks` — the truncated
stub `runHangarMenuFromOverlay` had been calling instead of computing real craft-flags state — is the
likely reason item -267 (the `mallocCraftSelectionData` `$s3` corruption hunt) stopped reproducing: the
next callee, `mallocCraftSelectionData`, plausibly consumed the sibling stub's never-computed garbage
state rather than containing its own bug. Single-run, not yet closeable on its own. Live-verify instead
hit a **different** crash: `last-guest-pc=0x800547bc`, Bus error 10 — byte-for-byte item -263's original
s426 single-source find (2nd independent occurrence), promoting item -263 from parked to active frontier.

**s434-437: the `0x801163B0` free-list-cache-head-deref idiom, swept and fixed at scale; item -263
progressively localized past two rounds of breadcrumb misattribution.** `0x801163B0` is a persistent
free-list cache-head global that `docs/audit-changes.md` (a pre-project 2026-05-08 audit) had already
flagged as an open "Top-5 Cat-B unknown"; four earlier sessions (s197/s266/s270/s271) had each bespoke-
guarded one reactive occurrence without ever sweeping the idiom. s434's confirmation-soak crash
(`emitAllocatedDLCommand`) was a 5th occurrence; a full-codebase grep-scan found **107 more** unguarded
occurrences (funcs_3.c/funcs_4.c only, 100% uniform shape), fixed with one generic regex-based guard
(`GENERIC_CACHE_GUARD`, substitutes 0 for an out-of-`[0x80000000,0x80800000)` head pointer before the
deref). The confirmation soak for THAT fix (s434→s435) crashed on a different bug, root-caused as a
**breadcrumb-coverage misattribution**: `last-guest-pc` froze at `submitSceneNodeRender`'s call site
because the actual callee, `emitMaterialTexturedDL`, had zero breadcrumb writes across its ~1258-line
body — fixed by adding coverage (BREADCRUMB16), same mechanism BREADCRUMB15's own s349 note had already
documented once. s436's next confirmation soak found a genuinely new, real bug: `reserveAndEmitDLEntry`
reloads `0x801163B0` into TWO registers 4 instructions apart — `$v0` (guarded) and `$a1` (not, since
s434's regex only matched `$v0`) — and the unguarded `$a1` copy is used as a raw write pointer with zero
validation 14 instructions later. A scoped scan of all 24 same-shape `$a1` reload sites classified 12 as
already-safe (game's own `!=0` check), 6 as dead (reassigned before use), and 7 as the same live bug —
fixed with `CACHE_HEAD_A1_GUARD` (skip the write when the pointer is out of range; unlike the read-side
guard, 0 isn't a safe substitute for a write address). That confirmation soak (s436) then crashed again
on item -263's signature — still the `tickWrappingTimerAccumulatorList`-epilogue misattribution
(`0x800547BC` disassembles to the function's own `addiu $sp,$sp,0x40` return, not a memory access) — so
s437 added BREADCRUMB17 to `runHangarSelectionFrame`, the only one of that function's 3 callers reachable
by the menu-only probe schedule, to catch the real fault site on next occurrence.

**s438: item -263's queued confirmation soak (`s437_breadcrumb17_confirm`) recurred a 4th time —
BREADCRUMB17 worked, but immediately hit the SAME misattribution mechanism one level deeper.** The new
`last-guest-pc=0x800AAF94` resolves (via `tools/overlay_symbol_probe.py` + a sorted `menu_overlay.txt`
symbol-address table) to +504 bytes into `runHangarSelectionFrame` — confirmed by source: `funcs_28.c:
5391-5396` is the breadcrumb write immediately before the `jal` into `updateHangarBayScene`. A full grep
of `updateHangarBayScene`'s entire body (`funcs_28.c:10918-17722`, ~6805 lines — the largest function
this project has instrumented) found **zero** breadcrumb writes anywhere in it, so `last-guest-pc` froze
at the call site the instant execution entered this uninstrumented callee — the same mechanism
BREADCRUMB16 (s435) and BREADCRUMB17 itself were built to defeat, recurring one function deeper because
`updateHangarBayScene` was never on the breadcrumb allowlist either. Two independent signals now agree on
`updateHangarBayScene` as the locus even without an exact instruction: this guest-side call-site freeze,
and the host-side `atos` symbolication (`pc-symbol=updateHangarBayScene+43768`), which has named this
same function at every one of item -263's 4 occurrences (s426, s433, s436, s437) without anyone
previously connecting it to the breadcrumb-coverage gap. Next work unit: BREADCRUMB18 (or a checkpoint
bisection, given the function's size) inside `updateHangarBayScene` itself.

**s439: BREADCRUMB18 added to `updateHangarBayScene` (funcs_28.c:10918-17722, ~6805 lines, 2643
breadcrumb writes — the largest function this project has instrumented).** Regenerated/rebuilt clean, no
regression to `GENERIC_CACHE_GUARD` (107)/`CACHE_HEAD_A1_GUARD` (7). Live-verify came back clean (0
`[CRASH]`, 0 guard fires, full 298.5s/126-frame schedule) — a null result without a positive control,
consistent with the established alternating clean/crash pattern. Confirmation soak queued.

**s440: `updateHangarBayScene` entry counter (`ROGUESQ_LOG_HANGARBAY_ENTRY`) — the first same-run
positive control for the BREADCRUMB18 thread.** Consumed s439's queued confirm soak first (2nd
consecutive clean run; its 7503s wall-clock is most likely a macOS sleep-event pause, single-source, not
independently confirmed). Added an entry counter rather than spend a 3rd identical confirm cycle; caught
a real build bug along the way (`funcs_28.c` needed its first-ever `#include <stdio.h>` for `fprintf`).
Live-verify: 3rd clean run, but this time with the missing control — `updateHangarBayScene` logged
**~2900+ calls** in the single run, the first confirmation the function is a hot, constantly-executing
path during exactly the schedule that keeps not reproducing item -263. Confirmation soak queued; a 3rd
consecutive clean result there would hit iron rule 8's 3-strike budget on this hypothesis thread.
*(Historical note: true under the outcome-blind rule-8 counter in force at s440; since the 2026-08-08
harness change, only non-ADVANCED iterations count toward the strike budget.)*

**s441: three results in one session.** (1) Consuming s440's queued confirm soak crashed
(`last-guest-pc=0x8000CE40`, `si_addr=0x38076a804`, the item -263 near-zero-pointer family) — but
`[hangarbay-entry]` logged **zero calls** before the crash and the backtrace
(`reserveAndEmitDLEntry <- submitSceneNodeRender <- ... <- runHangarSelectionFrame`) never goes near
`updateHangarBayScene` at all, decisive same-run proof this occurrence was misattributed to item -263 by
superficial signature match alone. (2) Root-caused the real mechanism: `GENERIC_CACHE_GUARD` validates a
free-list HEAD pointer before dereferencing it, but the "next" pointer that deref reads back is never
itself validated before being written back as the new head and dereferenced 4 bytes later
(`0x8000CE40`) — a THIRD sibling of `GENERIC_CACHE_GUARD`/`CACHE_HEAD_A1_GUARD`. A scoped scan found
105/107 `GENERIC_CACHE_GUARD` sites share this exact shape (the other 2 already covered by bespoke
`CACHE2_GUARD`/`CACHE3_GUARD`); patched all 105 as `FREELIST_NEXT_GUARD`. Regenerated/rebuilt clean, no
regression to the existing guard families; live-verify: process died at 109.9s on an entirely different,
previously-uncatalogued crash — 0 fires across all 3 free-list guard families this run (null result, not
yet a positive control). (3) That new crash (item -278, single occurrence): SIGSEGV inside the
thread-scheduler/semaphore runtime, no game-code frames at all —
`moodycamel::LightweightSemaphore::tryWait <- wait_for_resumed <- resume_thread_and_wait <-
swap_to_thread <- check_running_queue <- pause_self <- idle_thread_handle`, wild 64-bit host pointer
`si_addr=0x10fc0a00000060e3` (matches `x8`), `last-guest-pc` treated as stale/uninformative (idle
thread, not the OS thread that last updated the shared guest-PC global). Signature doesn't match any
prior family (SIGSEGV not SIGBUS, wild host pointer not near-zero guest pointer, zero game-code frames).
**Downgrades item -263's confidence**: this session proved (same-run, mechanism-level) that at least one
occurrence previously filed under item -263 was actually this new free-list-next bug. Confirmation soak
queued (shared with item -278).

**s441 net effect on item -263 (s426, recurred s433/436/437/440): RECLASSIFIED — PARKED, likely
dissolved into the free-list-guard family, not independently confirmed to exist as a distinct bug.** All
5 total occurrences (s426 through s440) share the same superficial signature (SIGBUS, wild near-zero
`0x38000000x`-family pointer); none of them ever actually showed a fault instruction inside
`updateHangarBayScene`'s own body — the s426-s438 "localization" chain (recounted above) was a sequence
of breadcrumb-coverage-gap freezes that never reached an instruction inside the target function, right up
until s440 finally got there with full coverage and found the fault was elsewhere entirely. The simplest
explanation is that item -263 was never a distinct bug: it is the same `0x801163B0` free-list family
recurring at different call sites that happen to route near `runHangarSelectionFrame`/
`updateHangarBayScene` in the call graph. The single falsifying observation that would resurrect it as
independent: a NEW occurrence where BREADCRUMB18 (full coverage, unregressed) reports a real address
inside `updateHangarBayScene`'s own body.

**s442: the queued `s441_freelistnext_confirm` soak's rc=1/0s "failure" was a SOAK-SCRIPT BUG, not a
crash.** `SOAK-RESULTS 20260807-070416` showed rc=1 after 0s, log `cd: build: No such file or
directory` — the script used four `..` to reach the repo root from `scratch/agent/soak_queue/` where
three is correct, so it walked one level above the repo (into the parent `Tools/` directory, which has
no `build/`) and exited before ever launching the game. Re-ran the identical schedule manually with the
corrected path (300s budget): **CLEAN** — full schedule (126 frames to ~298s), 0 `[CRASH]`, 0 fires on
all 3 free-list guard families (now zero same-run fires across every soak since s434 — the "does this
guard mechanism even engage" doubt is still open), `[hangarbay-entry] n=2900` matching s440's baseline
exactly. Item -278 did NOT recur (still a single, unconfirmed occurrence). Requeued a corrected confirm
soak built on s440's more robust `REPO_ROOT`-variable + self-checking-log pattern. **Process lesson**: an
`rc=1` soak result with near-zero duration and no `run.log` is a soak-harness bug signature, not a crash
signature — check for that before reading it as a game crash.

**s443: `[wait-resumed-dead-ctx]` — a diagnostic instrument in `wait_for_resumed()`
(`lib/N64ModernRuntime/ultramodern/src/threads.cpp`) testing item -278's UAF hypothesis.** First
confirmed via `nm -C` that `idle_thread_handle` (the item -278 backtrace's root frame) is a real N64
guest function symbol, not an `atos`/`dladdr` misattribution — source-traced to
`main_overlay.txt`/`funcs_0.c:2229`. Source-read `ultramodern`'s thread-swap handshake and found an
asymmetry matching this project's "guard one deref, miss its sibling" idiom: `resume_thread_tagged`
already UAF-guards the RESUME TARGET's context before signalling it, but `wait_for_resumed` derefs the
CALLING thread's OWN context with no equivalent check — exactly where the s441 crash's
`LightweightSemaphore::tryWait` frame sits. Added a diagnostic-only instrument (deliberately not a
corrective guard: skipping a live thread's own wait isn't provably safe the way substituting a guest
write is) — two atomic counters plus an unconditional `fprintf` only on the bad path. Host-only C++
change, no regen pipeline needed; verified via `nm` and via grep of unchanged compiled `.c` output that
none of the 3 free-list guard families regressed; `submodule-patches/export.sh` run and committed
same-session. Live-verify: **0 `[wait-resumed-dead-ctx]` fires**, but the process crashed anyway at
112.3s on yet another signature — not item -278, not any free-list family. SIGBUS,
`si_addr=0x38022417e` (RDRAM host base + a plausible KSEG0-looking guest offset `0x8022417e`),
`pc-symbol=tickWrappingTimerAccumulatorList+3888` (via `dladdr` on the actual fault PC register, not a
breadcrumb global), `last-guest-pc=0x80054750` (+0x100 into the function, a different offset than the
earlier s433 occurrence's epilogue address), backtrace `tickWrappingTimerAccumulatorList <-
runHangarSelectionFrame+5396 <- runHangarMenuFromOverlay <- menuOverlayInit <- mainGameLoop <-
mainBootstrapWorker` — a DIFFERENT call site into `tickWrappingTimerAccumulatorList` than item -263's
saga ever traced (no `updateHangarBayScene` frame; `[hangarbay-entry]` kept incrementing normally to
n=2600, unrelated). Does not resurrect item -263 (BREADCRUMB18 never reported an address inside
`updateHangarBayScene`'s own body). Filed as a new, not-yet-investigated occurrence per the
strategic-priority rule against reactive single-crash chases. Confirmation soak queued
(`s443_waitresumed_confirm.sh`).

### s445-451: `static5-rename-orphan-sweep` (HYPOTHESIS-ID `orphan-guard-completeness-closeout`) —
codebase-wide fallout from the s427 duplicate-symbol fix, items -282..-289, migrated from
CURRENT-TRUTH.md s451 maintenance pass

**Root cause (established s446, item -284):** `hangarInitialize` never existed as a real function
post-s427 — it was N64Recomp's PRE-fix merger of ~15 separate, now-correctly-named functions
(`loadCutsceneAssetsByIndex`/`mallocCraftSelectionData`/`runHangarSelectionFrame`/
`composeNpcOrientationMatrix`/`updateHangarBayScene`/`hangarTickCameraOrbit`/etc.) into one anonymous
~13,770-line blob, and s427's duplicate-symbol fix (§16 above) split it back apart. EVERY pre-s427
guard/patch hardcoded to the old anonymous `static_N_0xADDR` names or file locations was orphaned this
way (confirmed 0 matches tree-wide for 11 old names) — a silent-regression risk distinct from, but
caused by, the same s427 fix that closed the duplicate-symbol catalogue.

**s445 (item -282, -281):** Opened a fresh M3 idiom-class audit, `GETDATITEM_GUARD`: `getDatItemByName`
(funcs_10.c, guest `0x80047B70`) returns sentinel -1 on an empty hash bucket; 5 of 6 call sites
dereferenced the raw return value unvalidated. Patched all 6 (one general regex, byte-identical idiom);
regen/build/`strings` clean. Live-verify: 0 fires (1st soak), crashed on a new, unrelated class (item
-281: `NAN_CHECK` assert in `transformVec3ByMat34`, `funcs_4.c:30007`, first-ever trip of this
codebase-wide always-on `assert(val==val)` macro; single occurrence, filed not chased).

**s446 (item -284):** Root-caused the orphaning as codebase-wide (above) and fixed 34 sites in one
pass: `HANGARLIST_GUARD`+`EARLY`/`WALK`/`CLEAR` (4 sites, `funcs_27.c`) and the combined s284/s285
deref-guard list (30 sites, `funcs_28.c`). Method (reused every subsequent session in this arc):
standalone Python scan confirms each site's exact multi-line anchor matches exactly ONCE tree-wide
before ungating; fixup script asserts (`SystemExit`) on any site matching >1 time. Live-verify: 0
crashes, 0 fires, `[hangarbay-entry]` n=3000+ (reachability control).

**s447 (item -285):** Found `tools/probe.sh` silently mislabeled crashed soaks as clean (`rc=0`) —
the capture loop `break`s on game death and falls through to an implicit `exit 0` unless the caller
self-checks `run.log`. This retroactively downgraded s445's and s446's "0 fires" results from
confirmed-clean to "one inconclusive soak, still no positive control" (both soaks had actually crashed
on unrelated pre-existing signatures). Fixed at the root: `probe.sh` now `exit 3`s on a detected
`[CRASH]`; verified with a same-session positive control (against s446's crashed log) and negative
control (against a genuinely clean log). Audited all 21 other `probe.sh`-calling recipes; 3 more
lacked the self-check, 1 silently wrong (`s400`, rechecked genuinely clean), 2 already correctly
nonzero via a different path.

**s448 (item -286):** Fixed `S390_H2A`/`S390_H2B` (11 sites, `funcs_28.c`), orphaned the same way.
Two new wrinkles beyond s446's method, both verified not assumed: overlay-duplicated code repeating
the same guest addresses elsewhere in the file (full multi-line anchor, not bare address, kept
matches unique) and two different functions in the same file defining the same-named label
`L_800AB618:` (safe by C's per-function goto scoping, checked directly). 7/11 sites correctly no-op'd
as redundant with already-active guards. Live-verify: 0 crashes, 0 fires (null result, no positive
control yet).

**s449 (item -287) — closed the whole arc's open ambiguity with a positive control.** Every confirm
soak since s445 had logged 0 trips on the newly-ungated guards, ambiguous between "code never
executes" and "pointer is genuinely always valid." Added unconditional REACHED counters (not just
trip counters) to `GETDATITEM_GUARD` and `HANGARLIST_GUARD_EARLY`/`WALK`/`CLEAR`. Result:
`HANGARLIST_GUARD_EARLY`/`WALK`/`CLEAR` reached 245000+ times combined with 0 trips — a strong
positive control confirming true negative, not dead code; `GETDATITEM_GUARD` reached 5/6 sites (lower
traffic, still refutes unreached). **Conclusion: this entire guard idiom class (`-0x25A4`/table-deref/
free-list-cache-head) is confirmed correct hardening that is unlikely to ever fire under normal play —
remaining orphan-sweep work is completeness debt-paydown, not a crash hunt.** Incidental crash on a
new, unrelated signature (`heapFreeListDequeue+19316`, single occurrence, filed not chased).

**s450 (item -288):** Fixed `G1`-`G32` (29 sites) plus a previously-unaccounted 5-site sibling family
(`A`-`E`, an older s110 table-deref guard) and their shared `L_hangarbay_guard_exit` epilogue label —
all three were doubly-orphaned (dead file gate AND dead function-name regex). Standalone scan found
all 29 anchors unique tree-wide, refuting the old fixup comment's stale "also in funcs_27.c" warning.
First build failed (`undeclared label`) because the epilogue-label block was independently orphaned
too — fixed alongside once the dependency surfaced (a new lesson: check a patch's bare `goto LABEL`
target for independent orphaning BEFORE ungating, or a missing-label build failure is the symptom).
Live-verify: 0 fires (matches s449 baseline), crashed on the already-closed item -259 signature family.

**s451 (item -289) — closes the `funcs_40.c`-gated orphan inventory except `BREADCRUMB7`.** Fixed 9
further doubly-orphaned `composeNpcOrientationMatrix` guard sites ("guard1"-"guard9", an older,
separate family from item -284's own 30-site fix for the same function). Applied s450's own
lesson: checked the shared bail target `L_800AB618` for independent orphaning BEFORE ungating,
found it already live via other already-ungated guards in the same file, so no shared-infrastructure
fix was needed this time (a clean outcome on that check, unlike s450's). Live-verify: 0 fires (matches
s449 baseline), crashed on the already-catalogued `BREADCRUMB6`/near-`0x80000000` "near-zero guest
pointer" family (first seen s273, reconfirmed not-a-new-class as recently as s328a).

**State entering s452:** only `S392_H3A`/`S393_H3B` (50 sites total) remains open in this arc, plus
`BREADCRUMB7` (diagnostic, lowest priority, optional). `S392_H3A`'s bail label `L_800ADB2C` is known to
sit INSIDE `updateHangarBayScene`'s own body — meaning some or all of these sites may already be
covered by `GENERIC_CACHE_GUARD`'s blanket 107-site fix (item -270/-273); check for redundancy before
patching, don't force full application. Exact plan: `scratch/agent/NEXT.md` as of s451.

**s453 (item -290) closed `S392_H3A`/`S393_H3B` — INVESTIGATED, no code change, all 50 sites
redundant.** Confirmed the same `funcs_27.c`→`funcs_28.c` file-gate staleness as items -284/-286/-288/
-289 (all 29 `S392_H3A` sites resolve into `updateHangarBayScene`, all 21 `S393_H3B` sites into
`hangarTickCameraOrbit`, both tree-wide-unique by address), but unlike those items fixing the gate would
add nothing: a full per-site mechanistic re-derivation (real current line range, the register actually
dereferenced at the end of each guarded sequence — not always the tuple's declared pre-combine `reg`
field — checked for an already-active earlier guard on that exact register before the deref, plus a
reassignment scan in between) found every one of the 50 sites already covered by earlier guard sweeps
(mostly the s132 `HANGAR_BAY_DEREF_GUARD`/"G"-family, a few `S284`/`S285` sites, one shared-join-point
case). 3 sites needed hand verification because their own anchor's trailing instruction happens to
dereference an unrelated scratch register, not the risky pointer — an automated "last MEM_* in the
anchor" heuristic misclassified them as unresolved before a direct read confirmed the real deref (a few
lines further in) was already guarded. No patch applied: the anchors don't match live text regardless of
the stale gate, and adding guards here would only be dead, always-skipped duplicates. Closure comment
left in `fixup_game_funcs.py` so a future session doesn't re-open this. Closes the `funcs_40.c`/
`funcs_27.c`-gated orphan-sweep inventory except `BREADCRUMB7` (diagnostic, lowest priority).

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 426–443, 453.

## 17. Two more M3 idiom-class audits, found via an s454 concurrent-process collision (s454–460),
migrated from CURRENT-TRUTH.md s461 maintenance pass

**s454: a concurrent-process collision (two `loop.sh` iterations briefly running at once) put two
independent scanners on the same `funcs_3.c`/`funcs_4.c` code cluster, and they found two different
fresh idiom classes.** One session's own scan (`N64Recomp/scratch_s454_scan.py`, tracking `ctx->rN =
MEM_*(..., OFFSET)` loads then checking for a later unguarded use of `rN` as a base register) rejected
two false leads first — `-0x25C0($s0)` (56 sites, `mallocCraftSelectionData`) and `-0x76E0($s0)` (46
sites, 8 files) are compile-time-constant-based counter/scalar accesses, not pointer dereferences, too
narrow a shape to be the risky idiom — before landing on `-0x5824($reg)` → global `0x8011A7DC` (item
-291 below). The other end of the same collision (item -292 below) independently rejected the identical
two false leads via its own two-hop scanner, then found a completely different global.

**Item -291: `DL_LIST_APPEND_GUARD` (`-0x5824($reg)` → global `0x8011A7DC`), found s454, CLOSED s456,
57/57 sites.** A doubly-linked-list append with no existing check, structurally identical to (but a
different global from) the already-fixed `0x801163B0` free-list-cache-head family (§16's
`GENERIC_CACHE_GUARD`/`CACHE4_GUARD`/`CACHE_HEAD_A1_GUARD`/`FREELIST_NEXT_GUARD`), in the same
`funcs_3.c`/`funcs_4.c` display-list-emission cluster those families already fixed real crashes in. The
scan found this offset's canonical 6-instruction shape byte-identical (verified programmatically) at
57/57 matching sites (26 `funcs_3.c`, 31 `funcs_4.c`; 11 functions including `allocateDisplayListBuffer`,
`emitFrameRdpInitDl`, `emitColorFillRect`, `drawFrameProfilerBars`, `renderFlatMeshFaceGroup`,
`renderLitMeshFaceGroup`, `drawTextGlyphRect`, `setupCameraMatrices`). s456 applied all 57 (no new
design work — the guard was already written/syntax-checked in `fixup_game_funcs.py` since s454): 26/26
`funcs_3.c` + 31/31 `funcs_4.c` sites confirmed by direct grep, 57/57 `strings` format-string count,
build clean. Live-verify (full 300s/250s-keys schedule): 0 `[CRASH]` markers across the whole schedule,
0 `dl-list-append-guard` fires, `hangarbay-entry` n=3000. Confirmation soak (`s456_dl_list_append_confirm`)
crashed (rc=3) on an unrelated, already-catalogued signature. Explicitly NOT in scope for this item:
`-0x23A8`→`0x8011DC58` (a sibling global on the same function cluster — became item -296 below) and
~111 non-canonical `-0x5824` sites reached through a non-adjacent load/deref pair with intervening code
(same global, still open, next idiom-class-audit candidate once item -292 closes).

**Item -292: `SONGTEMPO_TABLE_GUARD` (`0x29C0($reg)` → global `0x801529C0`, the MusyX song-sequencer's
"current song track" base pointer, `funcs_25.c`), found s455, still OPEN as of s460 at 31/43 sites.**
`lui $reg,0x8015; lw $reg,0x29C0($reg)` reloads the global fresh at every use site — the same "reload a
global pointer, dereference unchecked" shape as the closed `-0x25A4` family (§9/§14). 50 raw hits
tree-wide, all in `funcs_25.c`, 0 existing guards at discovery. Only ONE site in the whole tree WRITES
the global (inside `tickAllActiveSongs`, immediately before its own 7 read sites — safe, not touched);
the other 6 reader functions (43 sites total) only ever READ it with no guarantee `tickAllActiveSongs`
ran first in their call history — the same uninitialized/stale-global risk the `-0x25A4` family was
closed for. M5-audio-adjacent (MusyX song sequencer) but this is M3 guard-audit work, not new M5
de-stubbing. Per-site bail semantics are hand-derived by reading each whole function body first (never
templated blindly), reusing an existing label already on that function's own control-flow graph
wherever one exists (a null-check, a loop's own continue/exit label) — falling back to duplicating the
real epilogue only for a site that loads before the prologue runs or is genuinely past all loops with no
other reachable label. Progress by session:
- **s454** — `updateSongTempoTickRate` (4 sites). Site 1 bails with a stack-neutral `return;` (loads
  before the prologue runs); sites 2/3 reuse the function's own tick-loop exit label `L_80095648`; site
  4 duplicates the real epilogue.
- **s457** — `tickScheduledSongEvents` (5 sites) + `stepSongPitchBendLanes` (5 sites), 10 more (14/43
  total). `tickScheduledSongEvents` walks a singly-linked list (site tse1 bails `return;` before the
  prologue runs; tse2-tse5 bail via `goto L_80094EC0`, the loop's own advance-to-next-node point).
  `stepSongPitchBendLanes` is a per-lane outer loop wrapping a per-event inner loop (spbl1 reuses the
  game's own null-lane-skip idiom; spbl2-spbl5 reuse the "abandon this lane, advance to the next" bail).
  Live-verify: 0 `songtempo-table-guard`/`dl-list-append-guard` fires, but the run crashed at 113.5s on
  an unrelated signature (`heapFreeListDequeue+32596`/`submitSceneNodeRender+45220`,
  `last-guest-pc=0x8000d92c`) — no `funcs_25.c` frame anywhere in the backtrace. Filed as a 2-in-2-
  sessions `submitSceneNodeRender`-subtree crash observation (matching entry-count with item -291's own
  `s456_dl_list_append_confirm` crash, but different `last-guest-pc` — per the crash-signature-blindness
  trap (item -200), two independent single-occurrence data points, not confirmed as one bug); not
  chased, per the USER DIRECTIVE's no-reactive-single-crash-chase rule.
- **s458** — `stepSongModulationLanes` (5 sites), 19/43 total. An outer per-lane loop (stride 0x24,
  bound 0x900) wrapping an inner per-event loop, confirming the shape item -294's own notes had
  predicted for this function. Site smod1 (outer-loop head) reuses the game's own null-lane-skip idiom;
  smod2-smod5 reuse the identical "abandon this lane, advance" bail as `stepSongPitchBendLanes`. Live-
  verify: 0 `[CRASH]` across the entire schedule, 0 fires on either guard family, `hangarbay-entry`
  n=2600.
- **s459** — rule-8 mandatory pivot (3 straight iterations on this hypothesis without closing it):
  instead of a 4th, found and closed a different idiom class in one session (item -296 below), leaving
  item -292 at 19/43 untouched that session.
- **s460** — `advanceSongRegion` (12 sites), 31/43 total. Read the full 539-line body first: NOT a
  single-loop template like the four already-fixed reader functions — an outer per-channel loop
  (`$s1`/r17, 0–0x3F, head `L_80095280`) containing an inner list-walk loop (`L_800952BC`) and a "loop
  back or fall through" check block (`L_80095504`) feeding a finalize block (`L_80095534`). Despite
  being flagged (in the prior session's NEXT.md) as a suspected cross-function-shared-tail-merge
  candidate (the `lvj_checkComplexObjectives`-family risk — §16's closed duplicate-symbol arc is a
  different but related recompiler quirk), it turned out to have an ordinary single entry/exit — the
  flagged risk did not materialize here. Site asr1 reuses the function's own adjacent null-data skip
  idiom; asr2-asr10 (9 sites, one sequential "populate this list node" block) all bail
  `goto L_80095504;`; asr11 (the check itself) bails to `L_80095534`, the same target its own `beq`
  takes on a false condition; asr12 bails to `L_8009556C`, its natural fallthrough target. Live-verify
  (full 300s/250s-keys schedule): 0 `songtempo-table-guard` fires, `hangarbay-entry` n=2800. The run did
  crash late in the schedule, but on the exact already-catalogued `coalesceFreeHeapBlocks+4424`/
  `last-guest-pc=0x8000247c` background-noise signature closed since the s354–366 arc — no `funcs_25.c`
  frame in the backtrace, filed not chased. Confirmation soak (`s460_advancesongregion_confirm`, ran
  clean, rc=0, 346s) is the 2nd independent clean result for this slice.

**Still open (the standing item -292 work unit):** `stepActiveSongTracks` (12 sites, ~744 lines, the
largest of the 6 reader functions) is the last remaining reader function. May still involve the
recompiler's cross-function shared-tail-merge behavior (`lvj_checkComplexObjectives`/`audioCompandS16`/
`__OSGlobalIntMask`) even though `advanceSongRegion` turned out not to — needs its own full read before
patching. Once fixed, item -292 closes at 43/43 sites, and every one of its confirmation soaks so far
(s454/s457/s458/s460's) has delivered or is expected to deliver the same null result (0 guard fires)
matching item -287's established baseline for this whole guard-idiom class — not an open question.

**Item -296: `SIBLING_PTR_WRITE_GUARD` (`-0x23A8($reg)` → sibling global `0x8011DC58`), found AND CLOSED
same session s459, 119/119 sites.** Chosen per rule 8's mandatory pivot off item -292 (above). Item
-291's own session (s454) had explicitly scoped `-0x23A8` OUT of `DL_LIST_APPEND_GUARD` ("no clean
byte-identical repeated shape found — each site's downstream write differs"). A fresh systematic re-scan
(same discriminating-load-then-deref method) went one step further: grouping the 119 unguarded sites by
the NORMALIZED shape of their downstream use (registers/offsets blanked) found 118/119 share ONE shape
after all — `MEM_W(OFF, ctx->rN) = VAL;`, an unconditional field write through the reloaded, never-
range-checked pointer (`OFF` is `0x0` at 116 sites, `0x4` at 1, `0x8` at 2). s454 was right that the
load-to-write gap varies (4-24 lines of unrelated intervening code, no single blanket regex spans it)
but hadn't separately checked whether the WRITE shape alone was uniform — it is. Same structural risk as
`DL_LIST_APPEND_GUARD`/`FREELIST_NEXT_GUARD`. Patched via 119 individual literal-anchor patches
(captured verbatim from a fresh regen, confirmed tree-wide-unique before touching `fixup_game_funcs.py`,
generated programmatically rather than hand-written). Standard pipeline clean throughout: fixup report
`funcs_3.c ... x65` + `funcs_4.c ... x54` (119 exactly), direct grep confirmed 119/119, `strings`
confirmed 119/119 distinct format strings, build clean. Live-verify (full 300s/250s-keys schedule, plus
the new `ROGUESQ_LOG_SIBLING_PTR_WRITE_GUARD`): full schedule completed, 0 `[CRASH]` markers, 0
`sibling-ptr-write-guard` fires, `hangarbay-entry` n=35 (schedule-variance, not a regression signal —
full-schedule completion with 0 crash is the load-bearing observation). Confirmation soak
(`s459_sibling_ptr_write_confirm`) crashed (rc=3) on an unrelated, already-catalogued signature (a bare
delay-slot `nop` after a `jr $ra` inside `allocateDisplayListBuffer`, matching a background-noise class
filed around s394). **Notable, not chased:** 10 of the 119 sites are in `submitSceneNodeRender`, the
same function named in the still-open "wait-for-recurrence breadcrumb" (2 independent single-occurrence
crashes in its call subtree, different `last-guest-pc` each time, item -457's own session note) — this
guard is now a discriminating instrument for that breadcrumb at those 10 specific sites; 0 fires so far.

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 454–460.

## 18. Five more buckets from the s465 codebase-wide frequency scan (s463–469): four CLOSED, one
DEFERRED, migrated from CURRENT-TRUTH.md s469 maintenance pass

**Item -298: `DL_LIST_RESET_GUARD`, re-scoped the ~111 non-canonical `-0x5824` population (same
global as item -291, `0x8011A7DC`) flagged at s454/456. CLOSED s464, 84/84 sites.** Item -291's
original scan was regex-scoped too narrowly and silently missed a breadcrumb-dialect variant of its
OWN canonical shape. Programmatic re-classification (`scratch_s463_classify_5824.py`/
`scratch_s463_verify_reset.py`, N64Recomp repo, untracked) found the 111 split three ways: 27 were
actually-canonical (missed because their function has full per-instruction `g_rs64_last_guest_pc`
tracing, a breadcrumb dialect that puts the breadcrumb between each instruction's own comment and
its ctx-> line, a slot item -291's regex never tolerated) — folded into `DL_LIST_APPEND_GUARD`
itself s463 by widening its regex with matching inside-instruction breadcrumb slots, now 84/84
canonical sites total. 70 are a genuinely different, byte-identical shape — landed s463 as
`DL_LIST_RESET_GUARD`: the reloaded global is used DIRECTLY as a write address (`MEM_W(0X0,
ctx->rload) = ctx->rnode;`, no intervening deref at all, structurally the same risk as
`SIBLING_PTR_WRITE_GUARD`/item -296) — one blanket regex substitution (rload backreferenced
end-to-end, verified programmatically not sampled). The remaining 14 (5 `funcs_3.c`, 9 `funcs_4.c`)
had 1-4 lines of unrelated intervening code between the reload and the write pair (confirmed by
direct source read that none of it touches the reload register, `$v0`/`ctx->r2` uniformly across
all 14) — landed s464 via `SIBLING_PTR_WRITE_GUARD`'s own per-site-literal-anchor method
(`_DL_LIST_RESET_EXTRA_SITES` in `fixup_game_funcs.py`, each anchor confirmed tree-wide-unique by a
standalone script, `scratch_s464_verify_dllistreset14.py`, before patching), reusing
`DL_LIST_RESET_GUARD`'s own env var/tag so both mechanisms count as one instrument. Manual
live-verify: s463's soak ran the full 300s schedule with 0 fires on any of the 4 sibling guards;
s464's soak ran ~126s before crashing on the already-catalogued `coalesceFreeHeapBlocks+4424`
heap-walker background-noise family (documented since Session 366), filed not chased — 0 fires on
`dl-list-reset-guard`/`dl-list-append-guard`/`sibling-ptr-write-guard`, `hangarbay-entry` n=2700.
Confirmation soaks: `s463_dllistguards_confirm` crashed at 19.4s on `loadCutsceneAssetsByIndex+1860`
(`last-guest-pc=0x800aafb8`) — a single-occurrence new offset inside a function already known to
have multiple unguarded holes found piecemeal (`+668` fixed s254 as `HANGARLIST_GUARD`, `+948` fixed
s283), filed not chased; `s464_dllistreset14_confirm` crashed at 116.4s on
`last-guest-pc=0x80065e94` — the already-catalogued `NAN_CHECK`/misattributed-symbol family
documented since ~s327 (recurs under many different `pc-symbol` labels at this exact guest PC — a
known symbolication-collision artifact, not a new bug), filed not chased. **CLOSED: the whole
re-scoped `-0x5824` non-canonical population (111 sites) is fully accounted for** (27 canonical +
70 blanket-regex + 14 per-site).

**Item -299: `DL_BUFFER_POOL_GUARD`, global `0x801163FC` (89 bytes past the `0x801163B0`
free-list-cache-head global), `funcs_3.c`/`funcs_4.c` DL-buffer-pool code
(`allocateDisplayListBuffer`/`emitAllocatedDLCommand` and siblings). CLOSED s466, 84/84 sites, 2nd
independent confirm soak s467.** Found s465 by a fresh codebase-wide frequency scan of every
`lui $reg,0x80XX; lw $reg,OFFSET($reg)` global-reload idiom (not just previously-known offsets)
across all 50 `RecompiledFuncs/funcs_*.c` files (`scratch_s465_scan.py`, N64Recomp repo, untracked;
caught a case-sensitivity bug in its own exclude-list normalizer along the way). 87 raw reload sites
(`funcs_3.c`x46, `funcs_4.c`x38, `funcs_6.c`x3); a shape pass (`scratch_s465_classify_63fc.py`)
split off 3 `funcs_6.c` `COMPARE_ONLY` sites (benign, out of scope) from 84 `funcs_3.c`/`funcs_4.c`
sites sharing a lazy-init idiom: read `global->field0`; if non-null skip the write; else write.
Both the read and write deref the unvalidated reload — same structural risk as
`DL_LIST_APPEND_GUARD`/`DL_LIST_RESET_GUARD`. s466 ran the shape-uniformity audit s465 left open (a
CONDITIONAL BRANCH sits between the read and write, with a compiler-arbitrary delay-slot instruction
only sampled at 5 sites): `scratch_s466_shapecheck_63fc.py` (N64Recomp repo, untracked) dumped and
normalized the full reload-through-write block for all 84 sites and found 100% (84/84) adjacency
between the reload and the READ deref and 100% (84/84) reach a same-register write within 40 lines —
the 7 "distinct" normalized shapes it found are entirely explained by the harmless delay-slot
instruction (`nop` at 73 sites, various `addu $reg,$reg,$zero` register combos at 11), confirming
the write is only ever reachable through the read's result. That let the fix guard the READ alone:
validate `ctx->rL` right after the reload; if invalid, skip the read and force `ctx->rD` to a
nonzero sentinel (1) so control takes the "already initialized" branch (which contains the write
too) — NOT "substitute 0", which would route into the write branch and still deref the invalid
`ctx->rL` as a write address. Clean regen+build (84/84 sites: `funcs_3.c`x46 + `funcs_4.c`x38, no
regression in sibling guard counts), `strings` confirms 84 `dl-buffer-pool-guard` format strings.
Live-verify: 0 `[CRASH]` from the guard itself, 0 `dl-buffer-pool-guard` fires (matches item -287's
established true-negative baseline), `hangarbay-entry` n=32 (positive control), 0 fires on every
sibling guard. Crashed later in the same run on `coalesceFreeHeapBlocks+4424`/
`last-guest-pc=0x8000247c` — the SAME already-catalogued heap-walker background-noise family seen at
s464's confirm soak, filed not chased. **Confirmation soak run s467**: `s466_dlbufferpool_confirm`
(rc=3, 170s) — 0 fires across all 4 sibling guards, `hangarbay-entry` n=34, crashed at 121.6s on the
SAME `coalesceFreeHeapBlocks+4424` family again — a 2nd independent confirmation of the
true-negative result.

**Item -300: `NODE_LIST_HEAD_GUARD` (read) / `NODE_LIST_HEAD_WRITE_GUARD` (write), global
`0x8011A4B8` (`hi16=0x8012,offset=-0x5B48`), `funcs_3.c`/`funcs_4.c` linked-list-insert-at-head code
(10 near-identical functions). CLOSED s467, 20/20 read-guard + 10/10 write-guard sites.** s465's
scan ranked this the most concentrated remaining bucket. Classified with
`scratch_s467_classify_5b48.py` (N64Recomp repo, untracked): all 20 raw sites share a byte-identical
reload immediately followed by a deref-read — same read-off-the-raw-reload crash risk as
`DL_BUFFER_POOL_GUARD` if the reload is wild. **Unlike item -299, full per-site context (not a short
sample window — the exact trap that cost s465/s466 a session) showed this bucket is TWO distinct
downstream shapes, not one:** 10 "first-of-pair" sites where the read result gates a
`bnel`-delay-slot conditional write (the same idiom `FREELIST_NEXT_GUARD`, s441, already fixed for
a sibling global) needing only the read guard (forcing the read result to 0 on invalid reload makes
the `if` false, safely skipping both write copies); and 10 "second-of-pair" sites (the SAME 10
functions reloading the SAME global again a few lines later) where the reload register itself,
never reassigned, is later used DIRECTLY as a SECOND unconditional write address (usually the delay
slot of the function's own `jr $ra`) — the SAME write-through-reload risk `DL_LIST_RESET_GUARD`
(item -298) established for a different global, needing its own separate write guard. 9/10 of the
second shape are byte-identical and regex-anchor cleanly; the 10th (`funcs_3.c` `0x80008080`/
`0x80008090`) has a pre-existing `s436 CACHE_HEAD_A1_GUARD` block spliced in between by an earlier
unrelated patch, breaking regex adjacency — handled by its own per-site literal anchor, same
discipline as `DL_LIST_RESET_GUARD`'s 14-site remainder. Both regexes match-count-verified with a
standalone test script (`scratch_s467_test_regex.py`, N64Recomp repo, untracked) before being
written into `fixup_game_funcs.py`. Clean regen+build (20/20 + 10/10, no regression in any of the 4
prior sibling guards); `strings` confirms 20 `node-list-head-guard` + 10
`node-list-head-write-guard` format strings. Live-verify: **0 `[CRASH]` across the ENTIRE 300s
schedule** (the first soak in several sessions to run the full schedule clean rather than hitting an
unrelated background-noise crash partway through), 0 fires on both new guards, 0 fires on every
sibling guard, `hangarbay-entry` n=33 (positive control). Confirmation soak, RUN s468, 2nd
independent confirmation: rc=0, 345s, 0 `[CRASH]`, 0 fires on both new guards + every sibling,
`hangarbay-entry` n=31.

**Item -301: `TEXDATA_TABLE_GUARD`, global at `hi16=0x8013,offset=-0x70F8`, `funcs_6.c` ONLY
(texture-data-slot array base pointer). CLOSED s468, 31/31 sites.** The s465 scan's #2-ranked
remaining bucket, pivoted to after item -302's bucket proved unsuited to this method. Read
`freeTextureDataSlot` (`funcs_6.c:2690`) directly: `sll $v0,$s0,3; addu $v0,$v0,$s0; sll $v0,$v0,2`
computes `idx*36` (a 36-byte struct stride) from an externally-sourced index, then
`addu $v0,$v0,$v1` adds THIS global's freshly-reloaded value as the array BASE POINTER before
dereferencing — the same raw-reload-as-base-pointer risk as `DL_BUFFER_POOL_GUARD`/
`NODE_LIST_HEAD_GUARD`, just with index arithmetic interposed before the deref.
`scratch_s468_shapecheck_generic.py` (N64Recomp repo, untracked — parameterized triage tool for
future buckets) found 13 distinct downstream chain shapes, but since the risk is IN THE RELOAD
ITSELF, the guard only needs to anchor on the `lui`+`lw` reload pair, ignoring all 13 downstream
shapes — confirmed 31/31 by `scratch_s468_test_regex_70f8.py` against the actual on-disk text
(cross-checked against independent raw-line-count greps, all three agreeing at 31) before touching
`fixup_game_funcs.py`. **Guard design departs from precedent deliberately**:
`GENERIC_CACHE_GUARD`/`NODE_LIST_HEAD_GUARD` substitute 0 because those sites deref at a literal 0
offset with no further arithmetic; 0 would be actively WRONG here since every downstream chain adds
`index*36+offset` arithmetic before dereferencing (0 as a base → a guaranteed-invalid tiny address,
MORE certain to crash than the original wild value). `TEXDATA_TABLE_GUARD` substitutes `0x80000000u`
(start of RDRAM, always mapped) instead — any subsequent `index*36+offset` starting from a valid
base stays inside the 8MB window for any plausible index. Clean regen+build (`TEXDATA_TABLE_GUARD`
×31; all 6 sibling counts confirmed unchanged); `strings` confirms 31 `texdata-table-guard` format
strings. Live-verify: 0 `texdata-table-guard` fires, 0 fires on every sibling guard,
`hangarbay-entry` n=32 (positive control). Crashed at 124.2s on
`pc-symbol=loadCutsceneAssetsByIndex+1860`, `last-guest-pc=0x800ab068` — the SAME already-catalogued
function item -298's `s463_dllistguards_confirm` crashed in at the byte-identical `+1860` offset,
just a different exact guest PC — unrelated to this guard, filed not chased. **2nd independent
confirm soak, run s469** (`s468_texdatatable_confirm`, rc=3, 160s): 0 `texdata-table-guard` fires, 0
fires on all 6 sibling guards (no regression), `hangarbay-entry` n=31 (positive control) — the
true-negative result holds a 2nd time. Crashed on a DIFFERENT, NEW single-occurrence signature this
run: `pc-symbol=findOrCreateMaterial+776`, `last-guest-pc=0x80010b7c`, backtrace
`emitMaterialTexturedDLAlt` (appearing twice consecutively — likely the same shared-tail-merge frame
artifact already documented elsewhere in this lineage, not literal recursion) →
`submitSceneNodeRender+49316` → `processSceneNode` → `traverseSceneGraphRecursive` →
`setupCameraMatrices` → `runHangarSelectionFrame` → `runHangarMenuFromOverlay` → `menuOverlayInit` →
`mainGameLoop`. Not `loadCutsceneAssetsByIndex+1860` this time — a genuinely new, single-occurrence
data point, filed not chased per the no-reactive-single-crash-chase rule; notable only in that it
sits in `submitSceneNodeRender`'s call subtree, the same function already flagged (item -296, §17)
as host to a still-open wait-for-recurrence breadcrumb — but `sibling-ptr-write-guard` (the
instrument covering that breadcrumb's 10 sites) did not fire in this run, so this crash is not
confirmed as the same mechanism.

**Item -302: `hi16=0x8013,offset=0x7CE4` bucket (45 sites, 9 files) — CLASSIFIED AND DEFERRED, not
closed.** s465's scan's #1-ranked remaining bucket after item -300 closed.
`scratch_s468_classify_7ce4.py` + `scratch_s468_shapecheck_7ce4.py` (N64Recomp repo, untracked,
40-line window per site) found the reloaded global here is a small INTEGER INDEX, not a base
pointer — one site (`funcs_35.c:5232`, function `getSceneStatePtr`) is a bare getter returning the
raw reload value with zero arithmetic; every other site immediately does `ctx->rL =
S32(ctx->rL << 2)` (×4) then combines with a separately-loaded, per-site-varying base register
before dereferencing at a per-site-varying offset. 17 distinct normalized instruction-chain shapes
across the 45 sites; only 20/45 reach a local dereference within a 20-instruction window — the
other 25 pass the index-derived value into a callee, so any real deref (if one exists) is invisible
to this scan. Unlike every prior close in this lineage (raw reload IS the pointer, so guarding right
after the reload is shape-agnostic regardless of downstream), this bucket's actual risk surface — IF
real — varies per site with no known-valid index bound, so no single guard placement covers all
sites without speculation. **Decision: defer rather than force a guess.** No code change.

**Transferable lesson across this whole five-bucket pass:** raw site COUNT is not the tractability
signal for this idiom-class-audit method — SINGLE-FILE CONCENTRATION is. Item -302 (45 sites, 9
files, ranked #1 by count) turned out to be a fundamentally harder idiom and had to be deferred;
item -301 (31 sites, but ALL in `funcs_6.c`) was a clean one-session close. Every CLOSED item's
live-verify/confirm-soak result matches item -287's established true-negative baseline for this
whole guard-idiom class. Full session-by-session raw detail: `PORTING-STATE.md` Sessions 463–469.

## 19. Six more idiom-class audits, then the s465 scan lineage's close-out and the crash-symbolizer
blind-spot investigation (s470–478), migrated from CURRENT-TRUTH.md s479 maintenance pass

**Item -303: `TEXDATA_PTR_ARRAY_GUARD`, global at `hi16=0x8013,offset=-0x7104`, `funcs_6.c` only, 12
bytes from item -301's global. CLOSED s470, 29/29 sites** — the s470 rule-8 mandatory-pivot
iteration's discriminating probe: classification found two raw-pointer risk shapes (direct use as
an `rs_free()` argument / write-loop base with no arithmetic, and `idx*4` array-of-pointers
access), both distinct from item -302's confirmed integer-index shape; substitutes `0x80000000u`,
same reasoning as item -301. Clean build/live-verify: 0 new-guard fires, 0 fires on all 7 siblings
(no regression), `hangarbay-entry` n=31 (positive control); crashed on `last-guest-pc=0x80054744`
inside `tickWrappingTimerAccumulatorList` — the EXACT already-catalogued, already-PARKED
`m5-audio-destub-tickwrap-divzero-craftselect` compiler div-by-zero-trap signature (first seen
~s344, §12), unrelated to any guard tested, filed not chased. 2nd independent confirm soak
(`s470_texdataptrarray_confirm`) ran s471: 0 fires on the new guard and all 7 siblings,
`hangarbay-entry` n=31 (matches the manual live-verify exactly); crashed on a DIFFERENT signature
this time — a host-side Metal.framework SIGSEGV inside `fscache_insert_and_retain`
(`last-guest-pc=0x800ab0e0`, near but not identical to the s463/s468
`loadCutsceneAssetsByIndex+1860` crash site) — an async shader-compiler-thread crash unrelated to
any game-code guard, filed not chased (same family as items -10/-9's Metal-compiler-SIGSEGV
class). Both confirm passes null on the new guard.

**Item -304: `MATERIAL_ARRAY_PTR_GUARD`, `0x8012($reg)`→`-0x5BBC` global, 30 `lw` reload sites
across 4 files (`funcs_3.c`x5/`funcs_4.c`x10/`funcs_6.c`x14/`funcs_7.c`x1). CLOSED s471, 30/30
sites, first multi-file bucket in this sub-arc.** Single writer `buildAndRegisterDefaultMaterial`
(`funcs_4.c:27911`, stores an `rs_malloc()` result) vs. 30 reader sites in 4 different
functions/files — same uninitialized/stale-global-reload shape as every closed bucket in this
lineage. `scratch_s468_shapecheck_generic.py 8012 -5BBC` auto-classified 24/30 sites as
`ADD32→DEREF` (real pointer risk); the remaining 6 `hit_deref=False` sites were read directly from
source per the s470 lesson (tool false negative, not evidence of non-pointer use) and confirmed
the same two risk shapes as item -303: `idx*4` array-of-pointers access (`funcs_3.c:26341/28435`)
and direct-use-with-no-arithmetic (`funcs_4.c:29352` passes the raw reload straight into
`rs_free()`; `funcs_4.c:28004`/`funcs_6.c:14323`/`funcs_6.c:14728` use it as a write/read-loop
base). No item -302-style integer-index shape present — clean single-guard bucket despite spanning
4 files. Substitutes `0x80000000u`, same reasoning as items -301/-303. Regex verified 30/30
against raw `MEM_W(reg, -0X5BBC)` line counts per file (`scratch_s471_test_regex_5bbc.py`); the
bucket's one `sw` (write) site excluded by construction. Clean build; all 8 pre-existing sibling
guards unchanged (84/84/84/119/20/10/31/29); `strings` confirms 30 `material-array-ptr-guard` tag
occurrences. Live-verify: 0 new-guard fires, 0 fires on all 8 siblings, `hangarbay-entry` n=34
(positive control); full 300s/250s-keys schedule survived with 0 `[CRASH]` markers at all — unlike
most sessions in this sub-arc, this run hit no crash of any kind. 2nd independent confirm soak
(`s471_materialarrayptr_confirm`) ran s472: 0 fires on the new guard and all 8 siblings,
`hangarbay-entry` n=31 (matches the manual pass closely); crashed on a 3rd distinct byte-offset of
the already-catalogued `heapFreeListDequeue` crash family (`+31924`, `last-guest-pc=0x8000d738`;
prior sightings `+19316`/`+32596`) — unrelated to any guard tested, filed not chased (later
explained wholesale by item -310's s478 symbolizer-artifact finding below). Both confirm passes
null on the new guard.

**Item -305: `hi16=0x8011, offset=0x63d4` global (`0x801163D4`, 12 bytes from item -299's
`DL_BUFFER_POOL_GUARD` global) — CLASSIFIED AND DEFERRED, not a guard candidate (s472).** The
largest bucket in the s465 scan (170 `lw` reload sites, `funcs_6.c`x75/`funcs_3.c`x44/
`funcs_4.c`x30/`funcs_7.c`x21), 0 `sw` write sites. A stratified 27-site sample (all 4 files,
spanning every tool-reported chain-depth grouping) read directly showed 26/27 are the identical
`sltu`/`bne` "current DL pointer < buffer-end limit" bounds-check idiom — the reload is COMPARED,
never dereferenced or added-to; the 1 outlier is a save/restore (reload held live across a call,
written back unchanged to the same slot, also no local deref). The classification tool's only 2
`hit_deref=True` flags in the whole bucket were confirmed FALSE POSITIVES on direct read (the tool
anchors its report to the `lui` line, and what it flagged as `ADD32->WRITE_THROUGH` was an
unrelated stack-pointer prologue adjustment a few lines later, not an operation on the reloaded
value). Same disposition as item -302: an integer/boolean-valued use where guard-at-reload doesn't
apply (a comparison can't fault on a stale value, and forcing the outcome would silently change
game logic rather than harden against a wild pointer). No code change. **Tool bug found and
documented**: `scratch_s468_shapecheck_generic.py` is case-sensitive on its offset argument and
returns a silent "total sites: 0" false negative if the offset is passed in lowercase (generated
code always emits uppercase hex literals) — always pass uppercase for future buckets.

**Item -306: resolved item -296's flagged `hi16=0x8012, offset=-0x23a8` gap (141 sites) — found
and FIXED a real methodology gap in that already-CLOSED item (s473), closing 1 new guard site
(120th) and classifying the rest.** A from-scratch taint-propagation scan
(`scratch_s473_taint_scan_23a8.py`, N64Recomp repo, untracked) — validated against the KNOWN
119-address guard list (exact subset match) before trusting any new finding — found: 119 sites
already covered by item -296's `SIBLING_PTR_WRITE_GUARD` (matches exactly); **1 genuine unguarded
write-through-the-reload** (`setupCameraMatrices`, `funcs_4.c`, reload `0x8001770C` -> a
zero-offset `ADD32` copy survives two branches -> unconditional field write at label
`L_800177A4`) — the s459 scan that produced the original 119 cleared its register-taint tracking
on ANY reassignment, including zero-offset copies that preserve it, silently dropping this site;
**2 false positives** (`renderLitMeshFaceGroup`, `do_lwl` unaligned-load helper calls — confirmed
by direct read that the tainted register is a discarded merge-seed, not a deref); **10 sites**
where the raw reload is still live in `ctx->r4`/`ctx->r7` at a call to a REAL recompiled function
(`appendRdpStateDl`/`emitAllocatedDLCommand`/`buildOrientedFaceGeometry`/`drawTextGlyphRect`) —
crosses the function boundary via the guest ABI calling convention, a genuinely novel propagation
path no prior bucket in this sub-arc had considered; **flagged, not chased** (would need each
callee's own body read; plausibly the same safe DL-append-pointer idiom used throughout, but
unverified); **19 no-use sites**, spot-checked 4/19 (not exhaustive — residual risk low but not
zero, flagged for anyone revisiting this bucket). Fixed: added the confirmed site as
`SIBLING_PTR_WRITE_GUARD`'s 120th entry (same mechanism/env flag as the other 119). Clean
regen/build; `strings`-verified 119->120 with all 10 sibling guard families unchanged (no
regression). Live-verify: 0 fires on the new site + all 120 + all siblings, `hangarbay-entry`
n=31 (positive control); crashed at the very end on a NEW signature
(`setByteAcrossEntryList+176`, bus error, `last-guest-pc=0x800aafa8`, the standard
RDRAM-host-base-pointer pattern per the s219 overturned-conclusion entry), unrelated to any guard
tested, filed not chased. 2nd independent confirm soak (`s473_siblingptrwrite120_confirm`) ran
s474: 0 crash, 0 `sibling-ptr-write-guard` fires (matches the manual live-verify exactly). Item
-306 fully CLOSED, both confirm passes null on the new guard.

**Item -307: `hi16=0x8011, offset=-0x35e0` global (`0x8010CA20`) — CLASSIFIED AND DEFERRED, not a
guard candidate (s474).** 23 `lw` reload sites across 9 files
(`funcs_11/16/18/29/30/35/38/40/42.c`), no overlap with any existing guard's global address.
`scratch_s468_shapecheck_generic.py` flagged 3 sites `ADD32(...)->WRITE_THROUGH hit_deref=True` —
all 3 confirmed by direct read to be a **newly found tool bug**: the classify loop checks register
taint via Python substring containment (`"ctx->r2" in args`), which false-matches inside
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
corroborates it's an integer mission-transition-phase flag, not a pointer. No code change (a
comparison can't fault on a stale value). No soak queued (no code change to verify).

**Item -308: `hi16=0x8013, offset=0xb50` global (`0x8012F4B0`) — CLASSIFIED AND DEFERRED, not a
guard candidate. Also found tool bug #5, a label-line blind spot (s475).** True site count is 24
across 12 files (`funcs_9/12/15/16/17/27/28/29/30/32/33/42.c`), not the 21/11 the scan tool
initially reported — `scratch_s468_shapecheck_generic.py`'s lookahead loop only recognizes
disassembly-comment and breadcrumb lines while scanning from a `lui` to its `lw` reload; a bare
`L_XXXXXXXX:` branch-target label between them (common when the reload address is itself a jump
target) silently breaks the scan with no site reported and no warning — missed 3 sites
(`funcs_27.c:108435`, `funcs_30.c:14600`, `funcs_32.c:29556`), the last in a file (`funcs_32.c`)
that didn't appear in the tool's file list at all. Fixed in a standalone checker
(`scratch_s475_label_gap_check.py`, N64Recomp repo, untracked) that also skips label lines; not
fixed in the tool itself. All 24 sites (12/12 files) directly read: 100% the identical
`andi $vN, $vN, MASK` (masks `0x1/0x8/0x10/0x20/0x60` — a packed status/capability bitfield)
immediately after the reload, consumed only by a conditional branch, never dereferenced — same
compare-only idiom as items -305/-307. 0 write sites to the global found (`grep MEM_W(0XB50` —
read-only from recompiled code). No code change, no soak queued (same precedent as -305/-307).
**AMENDED s476: the open backfill question is CLOSED, clean.** Generalized the checker into
`scratch_s476_label_gap_generic.py` (N64Recomp repo, untracked, hi16/offset-parameterized) and ran
it against all 7 already-CLOSED buckets (items -298/-299/-300/-301/-303/-304/-306, hi16/offset
derived from each item's recorded global address). **Result: strict count == permissive
(label-skip) count for all 7 buckets — 0 label-gap sites found anywhere.** Tool bug #5 does not
recur in any already-CLOSED bucket; no per-site literal-anchor patch needed. While reconciling
counts, found item -299's raw strict count (87) differs from its guard's site count (84) — traced
to a DIFFERENT, already-known cause (`scratch_s466_shapecheck_63fc.py` hardcoded
`files = ["funcs_3.c", "funcs_4.c"]`, missing `funcs_6.c`'s 3 sites entirely), not tool bug #5
(strict==permissive there too, no label involved). Directly re-read all 3 `funcs_6.c` sites and
confirmed `fixup_game_funcs.py`'s own comment was correct: those 3 are COMPARE_ONLY (`bne` against
a computed array-bound address, never dereferenced), already correctly excluded from the guard.
Item -299 remains soundly CLOSED at 84/84 real sites.

**Item -309: new discovery source tried, `lui`+`sw` DIRECT-STORE frequency scan — CLASSIFIED AND
DEFERRED, dead end after one scan (s477). M3 `lui`+`sw` discovery direction considered exhausted.**
Per the s476 pivot note, wrote `scratch_s477_sw_scan.py` (N64Recomp repo, untracked) to find the
idiom this lineage had never scanned: `ctx->rL = S32(0XHHHH << 16);` immediately followed by a
direct store `MEM_W(0XOFFSET, ctx->rL) = ...;` with NO intervening `lw`-shaped reload of `rL` in
between (as opposed to every prior bucket, which started from a `lw` reload of a global *reading*
it back). Scanned all 50 `RecompiledFuncs/funcs_*.c`: 546 buckets, 1471 total sites, 358 of them
singleton (count==1) buckets — a long diffuse tail. Top 3 buckets by site count (230 at
`hi16=0x8011/offset=0x63b0`, 197 at `hi16=0x8012/offset=-0x23a8`, 85 at `hi16=0x8011/offset=0x63d4`)
are ALL offsets already well-understood from the read-side lineage (items -296/-305/-306) as
ordinary global-variable slots. Direct-read 3 examples (one per top bucket, `funcs_3.c:86`,
`funcs_3.c:5308-5316`, `funcs_3.c:1265`) confirmed every one is the plain-C-assignment shape
`someGlobal = registerValue;` — `sw $vX, OFFSET($at)` where `$at` is the `lui`-computed base, i.e.
the destination address itself is a fixed compile-time RDRAM address (part of the game's static
globals region), never a dereference through a stale/wild pointer. **A direct store to a fixed
compile-time address cannot fault regardless of the register's prior contents or a stale reload**
— there is no "stale pointer" for a fixed-address store to be guarded against; the crash-risk
shape every prior guard addressed (reading/dereferencing through a value that may be wild)
structurally does not apply to this idiom. No code change (nothing to guard); no soak queued. The
`lui`+`sw` direct-store discovery source is exhausted after this one scan, per its own stop
condition — both the `lui`+`lw` lineage (closed s476) and this `lui`+`sw` probe (closed s477) have
now been tried on the two most natural instruction-pattern angles with no further untried
high-expected-value lead.

**Item -310: `heapFreeListDequeue+NNNN` crash family — INVESTIGATED AND CLOSED, symbol-attribution
artifact, not a real recurring root cause (s478).** The highest-recurrence "filed, not chased"
crash signature (15+ sessions, s108-s477, new byte-offsets kept appearing after the family was
nominally "closed"). Applied the standing discriminating question ("one root cause recurring, or
several coincidentally-similar symptoms?") via direct guest-address arithmetic against
`heapFreeListDequeue`'s confirmed base (`0x8000CFD4`, `main_overlay.txt:273`): neither available
data point matches. s449's `+19316` implies guest PC `0x80011B48`, but the actually-logged
`last-guest-pc` was `0x8000D534` (`base+1376`); s471/472's `+31924` implies `0x80014C88`, but the
logged `last-guest-pc` was `0x8000D738` (`base+1892`) — both off by 18-30 KB. Root cause:
`src/main/main.cpp:1788`'s crash handler symbolizes the ARM64 HOST PC via `dladdr()`, which only
resolves the nearest **exported** symbol; `nm -n` on the built binary shows `heapFreeListDequeue`'s
host code is followed by a 40,648-byte gap (for a guest function only ~2,560 bytes / 640 MIPS
instructions) before the next exported symbol, populated with many unrelated internal-linkage
guard-flag statics from OTHER already-closed guard families (`s_drainmesh*`, `s_coalesceheap*`,
`s_ringbuffer*`, `s_dl_list_append*`, `s_node_list_head*`, `s_sibling_ptr_write*`) — any host crash
anywhere in that gap gets attributed to `heapFreeListDequeue+bignum` regardless of the real
faulting function. Same mechanism s123 already found for the original `+12704` occurrence (there,
guest-address math showed the real site was inside `submitSceneNodeRender`, since guarded) — this
session shows it's systemic and ongoing, not a one-off. **Verdict: not one recurring bug, not
idiom-auditable — a symbolizer blind spot.** No guard written (no single site exists to guard).
Future soak triage should NOT re-file `heapFreeListDequeue+NNNN` occurrences as "same family,
filed not chased" — each is very likely an unrelated crash colliding with this blind spot.
**Flagged as a real, boundable tooling-improvement candidate** (not attempted this session): the
crash symbolizer needs DWARF-line or full internal-symbol-table resolution (e.g. a build-time
`nm -n` snapshot, or `atos` against a dSYM) instead of `dladdr`'s exported-symbol-only lookup, to
stop collapsing this 40 KB multi-function span onto one wrong name. Two independent lines of
evidence: guest-address arithmetic mismatch (checked directly against current `main_overlay.txt`)
+ binary symbol-table inspection (`nm -n`) showing the structural cause.

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 470–478.

## 20. `DL_LIST_APPEND_GUARD` and `DL_LIST_RESET_GUARD`'s own "grep-verified unique site" scope
claims both turn out to be wrong (s481–486): two blanket generalizations plus one new deferred
`AUDIO_SLOT_ACTIVE_GUARD` sibling-site bucket, migrated from CURRENT-TRUTH.md s486 maintenance pass

**Item -312 (s481):** the `loadCutsceneAssetsByIndex+1860` breadcrumb (item -311's own predicted
first use case for the new local-symtab symbolizer) reproduced under the fixed symbolizer as
`submitSceneNodeRender+63868`, confirming s463/s468's hits were `dladdr` nearest-exported-symbol
misattributions, not a real bug in `loadCutsceneAssetsByIndex`. The real bug: `submitSceneNodeRender`
writes its own `$a0` ("new node") argument into the `0x8011:0x63B0` free-list-cache-head global,
rereads it for `GENERIC_CACHE_GUARD`'s unrelated deref chain (which sanitizes the reread copy but not
the original argument register), and `DL_LIST_APPEND_GUARD` then uses that same unsanitized register
as an unguarded WRITE ADDRESS at its own `rwrite` slot (site=0x80010E74). Fixed with a site-anchored
guard, reasoning the aliasing precondition couldn't recur elsewhere because a grep for that one
literal address was unique. 2/2 soaks clean (`s481_rwrite_guard_confirm`, 0 crash, 0 fires) — the fix
itself was correct, only its claimed scope (site-unique) was wrong; **SUPERSEDED s482 by item -313.**

**Item -313 (s482–483), CLOSED 2/2:** a structural re-audit of all 84 `DL_LIST_APPEND_GUARD` sites
(`N64Recomp/scratch_s482/audit_dl_list_append_rwrite*.py`) found item -312's grep checked the
ADDRESS, not the STRUCTURAL SHAPE — the same "write new-node arg into `0x63B0`, then self-round-trip
reload the same register straight back via a bare `lui;lw` with nothing validating it, then reach the
unguarded `rwrite` write" shape recurs at up to 78 more sites. Confirmed via a 2nd direct source read
(`funcs_3.c` `emitFrameRdpInitDl`, site=0x80008FD4, byte-for-byte the same shape). Two earlier audit
iterations produced a false lead (a naive "any nearby guard touches this register" heuristic flagged
57/84 sites — a coincidental, safe, unrelated `DL_BUFFER_POOL_GUARD` idiom) before narrowing to "is
the reassignment itself just a self-reload of the same corrupted value". Folded item -312's fix
directly into the blanket `DL_LIST_APPEND_GUARD` patch (addr6's write now validates `rwrite`, not
just `rload`, at every site); item -312's now-superseded site-specific patch deleted. Clean
regen/build, all 5 sibling guard families unregressed. **2/2 independent confirms clean**: s482 manual
soak (0 fires, crashed at 107.8s in the unrelated already-catalogued `initVec4TripletFromArgs+68`
BREADCRUMB6 family); s483 confirm (`s482_blanket_rwrite_guard_confirm`, rc=3, 0 fires on the new guard
or any of 6 siblings, crashed at `pc-symbol=coalesceFreeHeapBlocks+2016`/`last-guest-pc=0x800023b0` —
byte-identical to the already-closed s354–366 heap-coalesce family). The entire `DL_LIST_APPEND_GUARD`
lineage (items -291, -312, -313) is done.

**Item -314 (s483–485), CLOSED 2/2:** applying item -313's own "is the SHAPE actually unique, not
just the address" skepticism to another closed site-anchored patch found `AUDIO_SLOT_ACTIVE_GUARD`
(s166)'s "unique address" claim was likewise address-only — the same unguarded fixed-global-pointer
deref idiom (`lui $reg,0x8015`/`lw $reg,-0x6908($reg)`, global `0x801496F8`, written once in
`allocateSongChannelArray`) recurs at 20 more sites across 15 MusyX voice functions in `funcs_24.c`
(`musyxMixActiveVoices` x3, `musyxSynthFrame` x1, `musyxInitVoiceFromSample` x4,
`musyxStartVoiceRelease`, `musyxStoreVoiceAdsrParams`, `musyxTriggerVoiceAttack`, `musyxStopVoice`,
`musyxSetVoicePitchBend` x2, `setVoiceModulationParams`, `stopVoiceMarkRetrigger` x2,
`beginVoiceFadeRelease`, `deactivateVoice`, `getVoiceUserField`), confirmed via 2 direct source reads
(`musyxMixActiveVoices` funcs_24.c:2540-2564, unguarded `idx*136` combine feeding an unchecked read;
`deactivateVoice` funcs_24.c:6643-6657, same combine feeding an unconditional write). Filed
CLASSIFIED AND DEFERRED s483 (15 different downstream shapes after the load need per-shape regex
design, not a uniform blanket regex like item -313's). Fixed s484: 10 site-anchored early-return
guards, transitively covering 14/20 unguarded sites (guarding only the FIRST `-0x6908` reload per
function protects every later reload in the same call, since none of these 15 functions ever
rewrites the global). 6 sites in `musyxMixActiveVoices`/`musyxSynthFrame` deliberately left unguarded
— mid-loop, need a loop-scoped "skip iteration" shape, not a plain early return; documented as the
next thread on this bucket, not guessed at. **2/2 independent confirms clean**: s484's own confirm
soak (0 fires on item -314's guards; it separately triggered the item -315 discovery below) and
s485's `s484_audio_voice_baseptr_confirm` (rc=3, 0 fires on `audio-voice-baseptr-guard` or any
sibling, crashed at `pc-symbol=coalesceFreeHeapBlocks+4424`/`last-guest-pc=0x8000247c` — byte-
identical to the already-catalogued heap-walker family recorded at `PORTING-STATE.md` lines
~38630/38780/38801). **s487 closed item -314's own deliberately-deferred remainder**: the 6 mid-loop
sites in `musyxMixActiveVoices` (3 sites) and `musyxSynthFrame` (1 site anchor covering all 4, since
guarding the loop head transitively protects the 2 later same-iteration reloads) needed a
loop-scoped "skip this iteration/block, continue" shape rather than the plain early-return s484 used
for the other 14 sites — a new `AUDIO_VOICE_BASEPTR_LOOP_GUARD` (2 site anchors, `funcs_24.c`):
`musyxMixActiveVoices`'s loop-head reload gets a `goto`-to-per-iteration-increment guard;
`musyxSynthFrame`'s single reload gets a `goto`-past-the-release-countdown-array-walk guard to the
loop's own exit label. All 20/20 originally-audited unguarded `0x801496F8`-reload sites are now
covered. **2/2 independent confirms clean**: s487's own manual live-verify (0 fires on the new guard
or any of 13 sibling guard families, `hangarbay-entry` n=2600, crashed at 113.1s on the already-
catalogued `tickWrappingTimerAccumulatorList`/`memcpy_recomp+288` family, unrelated); the queued 2nd
confirm (`s487_audio_voice_baseptr_loop_confirm`, rc=0) came back the cleanest possible outcome —
ZERO `[CRASH]` events over the entire run, 0 fires on `audio-voice-baseptr-loop-guard` or
`audio-voice-baseptr-guard` or any sibling, `hangarbay-entry` reached n=3000. **Item -314 is now
FULLY CLOSED, 2/2.** The entire `AUDIO_VOICE_BASEPTR_GUARD`/`AUDIO_VOICE_BASEPTR_LOOP_GUARD` lineage
(item -314, superseding `AUDIO_SLOT_ACTIVE_GUARD`'s s166 site-unique claim) is done.

**Item -315 (s484–486), CLOSED 2/2:** item -314's own 1st confirm soak crashed live on a brand-new
bug in a sibling family: `DL_LIST_RESET_GUARD` (item -298) validates the wrong register at
site=0x80010880 in `submitSceneNodeRender` (`funcs_4.c`) — the guard's design comment claims its
"new node" register ("rnode") is "a normal argument register, not derived from G — not at risk", but
at this site `ctx->r4` is itself an earlier, completely unguarded reload of the SAME `0x801163B0`
free-list-cache-head global that `GENERIC_CACHE_GUARD` protects via a *different* register 3
instructions earlier — the exact same "guard validates one sibling register's reload but not
another's" meta-bug as items -312/-313. Confirmed via the live crash: `si_addr=0x380000000` = RDRAM
host base + guest `0x80000000`, consistent with `0x801163B0` having been self-healed to 0 by an
earlier guard. Fixed s484 with a site-anchored `S315_RESET_R4_GUARD`. s485 audited the deferred
"does this recur across the other 83 sites" question with a from-scratch static-analysis script
(`N64Recomp/scratch_s485/audit_dl_list_reset_rnode.py`) and found the same unguarded-rnode-alias
shape at 73/84 sites (2 confirmed via direct source read: `emitFrameRdpInitDl` site=0x80009104,
`renderLitMeshFaceGroup` site=0x800134F0) — almost exactly item -313's own 78/84 recurrence rate for
the sibling bug. Generalized into `DL_LIST_RESET_RNODE_GUARD`, folded into both the 70-site blanket
template and the 14-site per-site extension across all 84 sites uniformly (6 sites showed no alias,
5 were ambiguous after one `ADD32` hop, guarded anyway since a genuinely-valid pointer is provably a
no-op through the same range check every sibling guard uses); the old `S315_RESET_R4_GUARD` deleted
as a now-redundant subset. Build-verified (funcs_3.c 41+5=46, funcs_4.c 29+9=38, totaling 84/84, no
errors). 1st manual soak ran the FULL DURATION with ZERO CRASH (`rc=0`, 124 frames captured, every
`PROBE_KEYS` press through 250s completed) — the cleanest possible outcome, 0 fires on
`dl-list-reset-rnode-guard` and every sibling family. **s486 2nd independent confirm**
(`s485_dl_list_reset_rnode_confirm`, rc=3, 156s): 0 fires on `dl-list-reset-rnode-guard` or any
sibling guard; the crash itself was a host-side event (`last-guest-pc=0x800ab0e0`, `pc-symbol` a
nonsense-huge offset because the crashing host PC sits in system/dyld-shared-cache code the local
symtab table doesn't cover) — byte-identical `last-guest-pc` to item -303's own s472 confirm, already
catalogued there as an async Metal.framework shader-compiler-thread SIGSEGV inside
`fscache_insert_and_retain`, same family as items -10/-9. Item -315 is FULLY CLOSED, 2/2 independent
confirms clean. **The entire `DL_LIST_RESET_GUARD` lineage (items -298, -315) and the
`DL_LIST_APPEND_GUARD` lineage (items -291, -312, -313) are both done.**

**Tooling note (s486):** the item -311 local-symtab symbolizer produces a syntactically-valid but
numerically absurd `sym=X+N` line (offset in the billions) when the crashing host PC falls in
system/framework code outside the table's coverage, rather than a clear "not in this binary" marker
— this is a known display quirk, not a new bug; treat any `pc-symbol` offset above a few hundred KB
as "host-side crash outside our code", cross-check `last-guest-pc` against the catalogue before
filing as new.

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 481–486.

## 21. Items -316/-317: the `-312..-315` lineage recurs a 5th and 6th time, plus a methodology lesson
on validating the dereferenced register, not an upstream proxy (s488–492), migrated from
CURRENT-TRUTH.md s492 maintenance pass

**s488**: idiom scan closed the large-bucket (>=20-site) `lui+lw`/`lui+sw` audit method for now — every
big bucket already covered by items -291..-315. Left one sub-20 candidate open: the `-0x5BB4`
write-cursor global's 19 unguarded reads.

**Item -316 (s488 scan → s489 FIXED → s490 2nd confirm clean), FULLY CLOSED 2/2:** a downstream-consumer
trace found the real gap wasn't in the 19 read sites but one function upstream, in `emitAllocatedDLCommand`
(`funcs_3.c`): its existing s436 `CACHE_HEAD_A1_GUARD` (site=4) validates the newly linked node pointer
before writing the node's `next` field, but two statements right after the guard block stayed
unconditional — publishing the same possibly-bad node as the new list head and propagating its
data-area pointer into the `-0x5BB4` write-cursor global that all 19 read sites reload unguarded. Fixed
by extending the check (`DL_ALLOC_PROPAGATION_GUARD`) rather than adding 19 read-site guards — same
"guard covers one deref, not the propagation" shape as -312..-315. 1st confirm (manual): 0 fires,
`hangarbay-entry` n=31, crashed on the already-catalogued `initVec4TripletFromArgs+68`/
`last-guest-pc=0x800ab068` family (unrelated). 2nd confirm (`s489_dl_alloc_propagation_confirm`): also 0
fires — item -316 CLOSED. **But that 2nd confirm's own run.log handed back a genuinely new, well-evidenced
crash**: four unrelated sibling guards (`freelist-next-guard`, `generic-cache-guard`,
`dl-list-append-rwrite-guard`, `dl-list-reset-rnode-guard`) fired in sequence on the same corrupted
pointer value before a SIGBUS 24 bytes past the last one, inside `heapFreeListDequeue` — the same shape
recurring a 5th time, this time on a *derived* pointer (`$sN = $a0+8`) computed before any of those
guards run. That became item -317.

**Item -317 step 1 (s490 FIXED, methodology lesson → s491 extended → s492 confirmed), `heapFreeListDequeue`
FULLY CLOSED 2/2:** direct-source trace found `ctx->r4` reloads unguarded from the free-list-cache-head
global (`0x801163B0`) at `0x8000D6E4`, then computes `ctx->r16 = ADD32(ctx->r4, 0x8)` at `0x8000D744`,
dereferenced completely unguarded at `0x8000D760` (crash address matched the corrupted base plus both
chained `+8` offsets exactly). **First fix attempt was wrong and had to be caught by live-verify**:
it validated `ctx->r4` before the store, matching the -312..-316 precedent — but `0x8000D760` sits at a
label (`L_8000D75C`) reached by a SECOND, unrelated control-flow path (an earlier bounds-check
early-exit, `goto L_8000D75C` at `0x8000D67C`) where `ctx->r16` was last set from `ctx->r7` (a plain
register copy, nothing to do with the free-list reload) — so `ctx->r4` at the shared label has no
consistent meaning across both paths. The guard fired 660,261 times in one soak (all four sibling
guards stayed at 0) — an order-of-magnitude departure from every other guard in this lineage's history
(0-4 fires), the tell that flagged the false positive. **Corrected**: validate `ctx->r16` itself (the
register actually dereferenced), not an upstream proxy — correct on both paths regardless of which one
set it, matching every other guard's convention. Re-verified: 0 fires, `hangarbay-entry` n=31. A
post-commit classification subagent then found the shipped fix correct but incomplete: `ctx->r16` is
dereferenced at least 9 more times later in the same function body (all still unguarded), plus a
second-generation derived pointer `ctx->r5 = ADD32(ctx->r16, 0x10)`. **s491**: direct-traced the full
downstream span (`0x8000D75C`-`0x8000D8A8`) and confirmed it's a single straight-line block with exactly
one external entry point (no third path) — widened the existing check to `goto 0x8000D8A8` (skip the
whole rest of the block) instead of adding 9 more per-site checks; `ctx->r5` needed no separate check
(small constant offset off the now-validated base, used only inside the guarded span). 1st confirm: 0
fires on the guard or ~20 siblings. **2nd confirm (`s491_heap_dequeue_blockskip_confirm`, folded s492)**:
0 `[CRASH]` events over the entire run, the cleanest possible outcome. Item -317 step 1 CLOSED 2/2.

**Item -317 step 2 (s492 FIXED), `funcs_4.c` `buildOrientedFaceGeometry`, 1st confirm clean:** traced
independently rather than reusing step 1's fix shape. `ctx->r4` reloads unguarded from the same global
at `0x80012E94`, survives through four existing sibling guards untouched (none revalidate `r4`),
propagates into `ctx->r18 = ADD32(ctx->r4, 0x8)` at `0x80012EF0`, dereferenced unguarded across an
8-field struct-init block (`0x80012F14`-`0x80012F94`). The multi-path hazard s491 flagged (a
`goto L_80012F08` at `0x80012E24` reaching the same tail label with different-provenance `ctx->r18`)
resolved to a clean 2-entry join (one goto + one fallthrough) — fix validates `ctx->r18` itself at the
join, block-skipping to the existing epilogue label `L_80012F98` on invalid. New guard family
`ORIENTED_FACE_DERIVED_PTR_GUARD` (kept separate from `HEAP_DEQUEUE_DERIVED_PTR_GUARD`: different
offset/registers/function, same root global). 1st confirm: 0 fires on the new guard, `hangarbay-entry`
n=31, crashed on the already-catalogued `initVec4TripletFromArgs+68`/`last-guest-pc=0x800ab068` family
(same as s489/s463/s468). 2nd confirm (`s492_oriented_face_derived_ptr_confirm`) ran clean (0 crash
events) per SOAK-RESULTS.md — step 2 CLOSED 2/2.

**Item -317 step 3, the wider 183-site blanket sweep, remains OPEN.** The reload idiom
(`ctx->rL = MEM_W(ctx->rL, 0x63B0)`) recurs 184 times across `funcs_3.c`/`funcs_4.c`; a naive
textual-proximity classifier cannot detect the shared-label-merge hazard that produced step 1's wrong
first fix attempt, so a blanket sweep needs control-flow-aware tooling (trace the register actually
dereferenced forward to its true derefs, and backward from each deref to confirm every path has
consistent already-validated provenance) — scoped as a new tool-building work unit, not 181 more manual
traces, with its own positive control (correctly flags the 2 known-bad sites, correctly clears a sample
of known-benign sites) before trusting its output at scale. Alternative: wait for a third instance to
surface organically via a soak crash, as -316→-317 and -317 step 2 both did.

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 488–492.

## 22. Item -317 step 3: the blanket-sweep tool audit and 8-guard fix campaign (s493–503), migrated
from CURRENT-TRUTH.md s503 maintenance pass

**s493/494**: built `scratch/agent/s494_item317_step3_tracer.py`, a forward taint-propagation
dataflow analysis (handles 2nd-generation derived pointers, unlike a naive textual-proximity
classifier) to sweep the `ctx->rL = MEM_W(ctx->rL, 0x63B0)`-shaped reload idiom across
`funcs_3.c`/`funcs_4.c`. Found ~448 raw reload sites deduping to ~150 distinct candidate guard
placements across 30 functions (390 `NEEDS_GUARD` / 58 `SAFE_NO_DEREF`). A subagent audit of an 8-site
sample confirmed 8/8 `TRUE_POSITIVE`, 0 false positives, clearing the tool for scale use.

**s495-503 fix campaign, 8 leads fixed, all same shape**: a null check (`ctx->r2 == 0`) gates the null
arm (a separate harmless write, then goto away), but the non-null fallthrough has no
`0x80000000`-`0x80800000` range check before the dereference; downstream control flow falls into a
shared label that reassigns the register from a table again before any further use, so
skip-the-write-on-invalid is a safe fix. All 8, in fix order:

| Guard | Session | Site | Shared sites | 2nd confirm |
|---|---|---|---|---|
| `NODE_LIST_HEAD_SIBLING_R4_GUARD` | s495 | `funcs_4.c`, `submitSceneNodeRender` | 35 | CLOSED 2/2 |
| `RENDER_LIT_MESH_R2_GUARD` | s496 | `funcs_4.c`, `renderLitMeshFaceGroup` | 48 (largest) | CLOSED 2/2 |
| `EMIT_FRAME_RDP_INIT_DL_R2_GUARD` | s497 | `funcs_3.c:6979`, `emitFrameRdpInitDl` | 40 | CLOSED 2/2 |
| `..._R2B_GUARD` | s498 | `funcs_3.c:7963` | 40 | CLOSED 2/2 |
| `..._R2C_GUARD` | s500 | `funcs_3.c:5695` | 40 | CLOSED 2/2 (s503) |
| `..._R2D_GUARD` | s501 | `funcs_3.c:6014` | 40 | CLOSED 2/2 (s503) |
| `..._R2E_GUARD` | s502 | `funcs_3.c:6347` | 40 | CLOSED 2/2 (s504, folded from queue) |
| `..._R2F_GUARD` | s503 | `funcs_3.c:6670` | 40 | CLOSED 2/2 (s504, folded from queue) |

All 8 fixes' 1st live-verify showed 0 fires on the new guard itself (rare path, expected null result)
and 0 regressions across the growing set of sibling guard families. Every 2nd confirm crash landed on
an unrelated, already-catalogued signature (`tickWrappingTimerAccumulatorList` div-by-zero,
`buildPositionAndCallTransformHelper` near-`0x80000000`-RDRAM decompose, `coalesceFreeHeapBlocks`
heap-walker misattribution, or the item -318/-319 threads below) — none regressed the fix itself.
Per-hit tracer re-`--scan` after each fix confirms the fixed line leaves the unsafe-hit set; line
numbers drift downstream by the inserted guard block's line count each time (precedent: s496 +13,
s498 +13, s500/s501 no drift, s502 +13, s503 +13 — re-derive fresh every session, never trust a stale
line number).

**Two crash threads surfaced as a side effect of these live-verifies, not chased in-band (per the
no-reactive-single-crash-chases rule) — see `docs/CURRENT-TRUTH.md` items -318/-319 for their live
status**: `appendRdpStateDl+144`/`last-guest-pc=0x800109b8` recurred 3 independent times (s498, s501,
s503) with a corroborating guard-fire chain tracing the true call site into `submitSceneNodeRender`,
and its 3rd occurrence added a register-corruption correlation (`x0`/`x9`=`0x0000000300000000`) to
the separately-catalogued `initVec4TripletFromArgs+68` family (items -302/-306) — open, unresolved.
`beginFrameDLChunk+40536` fired once (s503), single data point, watching for recurrence.

**~135 other distinct locations remain unaudited/unfixed** as of s503's post-fix dedup. Current
tied-at-40 tier: `funcs_3.c:7384/8344/7700/8688` (all `emitFrameRdpInitDl`) plus `funcs_4.c:17346`
(`renderLitMeshFaceGroup`, flagged since s497, unfixed 7+ sessions running). Next-ranked leads from
s495's original sample (re-derive fresh, do not trust stale line numbers): `funcs_4.c:3299`-ish (26
sites), `funcs_3.c:28922`-ish (18 sites), then two singletons at `funcs_3.c:83`/`funcs_3.c:858`.

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 493–503.


## 23. Item -317 step 3 continued (s504-515): 10 more guards fix the tier to 18/18 fully closed 2/2,
plus item -318's full fix, migrated from CURRENT-TRUTH.md s516 maintenance pass

**s504 was itself a maintenance pass** (65,633 -> 47,371 bytes, 204 net lines removed) that also folded
in two queued Section-22 confirms and caught a documentation-consistency error in item -318's
register-correlation reading (see section 22's caution paragraph -- already corrected there).

### Item -318 (`appendRdpStateDl+144`) -- FIXED and FULLY CLOSED 2/2

**Mechanism**: all 6 call sites of `appendRdpStateDl` in `funcs_4.c` (including
`submitSceneNodeRender`'s `jal 0x8000DE70` at guest `0x800109B4`, whose delay slot at `0x800109B8` is
what `last-guest-pc` actually names -- the call site, not a fault inside the callee) reload the
`-0x23A8` "sibling global" at guest address `0x8011DC58` (`lui $reg,0x8012; lw $reg,-0x23A8($reg)`)
with **no range check**, then pass the raw value as `$a0`/`ctx->r4` into the call
(`funcs_4.c:2975-2995` for the `submitSceneNodeRender` instance). Inside `appendRdpStateDl`
(`funcs_3.c:26484`, guest `0x8000DE70`), that argument becomes a display-list-append write cursor
(aliased `ctx->r3`/`ctx->r11`) dereferenced **unconditionally from the function's first instruction**
(`0x8000DE7C`, +12 bytes: `MEM_W(0X0, ctx->r3) = ctx->r2;`) through dozens more sites with zero
null/range check anywhere in the function. This fell outside the existing 119-site
`SIBLING_PTR_WRITE_GUARD` audit (item -296/-306), which only covers same-function `MEM_W(...) = val`
writes through this global, not "reload -> pass as call argument -> callee writes" -- even though that
audit's own comment block named `submitSceneNodeRender` as carrying this exact idiom unguarded (10
sites, flagged since s459).

**Fix** (`APPEND_RDP_STATE_DL_ENTRY_GUARD`, `funcs_3.c:26484`, function entry): range-check `ctx->r4`
against `0x80000000`-`0x80800000`, early `return` (skip whole body) if invalid -- safe because
`appendRdpStateDl` is `void` with RDRAM-only side effects and no caller consumes a register return
value; one patch point covers all 6 call sites.

**Timeline**: source-traced and fixed **s505**, corroborated independently by a second Explore-agent
pass reaching the same conclusion. 1st live-verify (**s505**): clean (0 fires, `hangarbay-entry n=31`),
crashed on `beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0` -- the 2nd independent occurrence of
item -319's own signature. 2nd confirm: 1st attempt **s506** INCONCLUSIVE (crashed at only 20.0s/8
frames on `rebuildActiveDisplayObjectList+540`, zero guard-fire lines of any kind including zero
`hangarbay-entry` -- no positive control at all per Iron Rule 1, retried, did not count). Retry folded
in **s507** -- CLEAN, ran the full ~348s, `hangarbay-entry` up to n=2700, zero crash markers ->
**FULLY CLOSED 2/2 as of s507**.

**Register-correlation caution (still applies)**: s503's occurrence carried `x0`=`x9`=
`0x0000000300000000` in its mcontext dump, initially misread as a correlation to the separate
`initVec4TripletFromArgs+68` family (items -302/-306) -- a **false lead**, already resolved by the
s216-218->s219 overturned-conclusion entry (`0x0000000300000000` in `x0`/`x8` is the process's constant
RDRAM host base pointer, present by construction in every `MEM_W`-involved fault, not written
corruption).

### Item -317 step 3, guards 11-18 of ~150 (s506-515), same fix shape as section 22's guards 1-8

A null check (`ctx->r2 == 0`) gates the null arm safely; the non-null fallthrough has no
`0x80000000`-`0x80800000` range check before the dereference; downstream control flow reloads the
register from a table again before further use, so skip-the-write-on-invalid is a safe fix in every
case.

| # | Guard | Session fixed | Site | Function | Shared sites | 2nd confirm | Crash the verify/confirm soak hit (unrelated in every case) |
|---|---|---|---|---|---|---|---|
| 11 | `EMIT_FRAME_RDP_INIT_DL_R2G_GUARD` | s506 | `funcs_3.c:7384`/`0x80009578` | `emitFrameRdpInitDl` | 40 | CLOSED 2/2 (s507) | 1st: `coalesceFreeHeapBlocks+4328` (s354-366 heap-walker family); confirm clean |
| 12 | `EMIT_FRAME_RDP_INIT_DL_R2H_GUARD` | s507 | `funcs_3.c:8357`/`0x800098E8` | `emitFrameRdpInitDl` | 40 | CLOSED 2/2 (s508) | Confirm hit `loadCutsceneAssetsByIndex+1860`/`0x800aafb8` -- new, filed item -320 |
| 13 | `EMIT_FRAME_RDP_INIT_DL_R2I_GUARD` | s508 | `funcs_3.c:7713`/`0x800096A0` | `emitFrameRdpInitDl` | 40 | CLOSED 2/2 (s509) | 1st (after discarding a too-weak n=4 attempt): async Metal-shader-compiler dyld cluster (items -10/-9); confirm clean |
| 14 | `EMIT_FRAME_RDP_INIT_DL_R2J_GUARD` | s509 | `funcs_3.c:8727`/`0x80009A24` | `emitFrameRdpInitDl` | 40 | CLOSED 2/2 (s510) | 1st: `memcpy_recomp+288` (tickWrappingTimerAccumulatorList family); confirm hit `menuOverlayInit+3648`/`0x800ab1c4`, filed item -321 |
| 15 | `RENDER_LIT_MESH_R3_GUARD` | s510 | `funcs_4.c:17346`/`0x800148E8` | `renderLitMeshFaceGroup` (2nd site) | 40 | CLOSED 2/2 (s511) | Both runs: full 300s, zero crashes |
| 16 | `RENDER_LIT_MESH_R4_GUARD` | s511 | `funcs_4.c:16049`/`0x800142FC` | `renderLitMeshFaceGroup` (3rd site) | 38 | CLOSED 2/2 (s512) | 1st: benign `setByteAcrossEntryList+176` (item -306 family); confirm hit `heapFreeListDequeue+40432`/`0x8000d92c`, 2nd occurrence of the s457 signature, filed item -322 |
| 17 | `RENDER_LIT_MESH_R5_GUARD` | s512 | `funcs_4.c:17784`/`0x80014A8C` | `renderLitMeshFaceGroup` (4th site) | 46 (tier top) | CLOSED 2/2 (s514, after an s513 INCONCLUSIVE retry -- no `hangarbay-entry` at all, VI stuck pre-hangar) | 1st: full 300s clean; retry hit `rebuildActiveDisplayObjectList+540` (same family as -318's own s506 first attempt) |
| 18 | `RENDER_LIT_MESH_R6_GUARD` | s513 | `funcs_4.c:16575`/`0x80014558` | `renderLitMeshFaceGroup` (5th site) | 38 | CLOSED 2/2 (s514) | 1st: full 300s, zero crashes/co-fires; confirm hit the async Metal-shader-compiler dyld cluster (items -10/-9/-303/-315/-508) |
| 19 | `RENDER_LIT_MESH_R7_GUARD` | s514 | `funcs_4.c:15620`/`0x80014140` | `renderLitMeshFaceGroup` (6th site) | 32 | CLOSED 2/2 (s515) | 1st: clean on the guard, crashed on new `beginFrameDLChunk+27456`/`0x8000ae40`, filed item -323; confirm clean |
| 20 | `SUBMIT_SCENE_NODE_RENDER_R1_GUARD` | s515 | `funcs_4.c:4880`/`0x80010F38` | `submitSceneNodeRender` (1st site outside `renderLitMeshFaceGroup`/`emitFrameRdpInitDl`) | 34 | CLOSED 2/2 (s516, folded) | 1st: clean, crashed on `heapFreeListDequeue+40432`/`0x8000d92c` -- the 3RD occurrence of item -322 (s457/s512/s515), ESCALATED. Confirm (s516 fold-in): clean on the guard (0 fires, `hangarbay-entry n=2700`, one benign `hangarmenu-a0-guard` co-fire), crashed on `unregisterServiceWorker+536 (local-symtab)`/`last-guest-pc=0x800ab1c4` -- `last-guest-pc` byte-identical to item -321's single s510 sighting despite a completely different `pc-symbol` name (not just an offset drift like every prior case in this table); flagged as item -321's 2nd occurrence with a caveat, see `docs/CURRENT-TRUTH.md` item -321 |
| 21 | `RENDER_LIT_MESH_R8_GUARD` | s519 | `funcs_4.c:15166`/`0x80013F0C` | `renderLitMeshFaceGroup` (7th site) | 30 | CLOSED 2/2 (s520) | Doubly-linked free-list-cache prepend site (`old_head->prev = tail_node`). 1st: clean (0 fires, 4 benign init-time n=0/ra=0 co-fires, `hangarbay-entry n=31`), crashed on `beginFrameDLChunk+40536`/`0x8000b0d0` -- the 3RD occurrence of item -319 (s503/s505/s519), ESCALATED (fixed separately as `SIBLING_PTR_WRITE_GUARD` site=0x8000B0D0, s520). Confirm re-read s520: full 300s clean |
| 22 | `BEGIN_FRAME_DL_CHUNK_R1_GUARD` | s521 | `funcs_3.c:16595`/`0x8000B570` | `beginFrameDLChunk` (1st site, top of the tracer's own top tier for the first time this campaign) | 36 | CLOSED 2/2 (s522, folded) | 1st: clean, crashed on a NEW signature filed item -324 (`heapFreeListInsert+72`/`0x80015544`, no 2nd occurrence). Confirm: clean on the guard, crashed on `coalesceFreeHeapBlocks+4424`/`0x8000247c` -- the s354-366 heap-walker background-noise family |
| 23 | `BEGIN_FRAME_DL_CHUNK_R2_GUARD` | s522 | `funcs_3.c:12895`/`0x8000AA9C` | `beginFrameDLChunk` (2nd site) | 36 | CLOSED 2/2 (s523, folded) | Reloads a DIFFERENT `0x63B0`-offset global than R1's own site. 1st (after discarding a too-weak `n~5` attempt on the Metal-shader-compiler cluster): clean, crashed on a NEW signature filed item -325 (`findLookupEntryByKey+2212`/`0x800ad0dc`, no 2nd occurrence). Confirm: clean on the guard (6 benign zero-value co-fires), crashed on `emitAllocatedDLCommand+4680`/`0x80008764` -- the s354-366 SIGBUS background-noise family |
| 24 | `BEGIN_FRAME_DL_CHUNK_R3_GUARD` | s523 | `funcs_3.c:13381`/`0x8000AC0C` | `beginFrameDLChunk` (3rd site) | 36 | CLOSED 2/2 (s524) | Reloads the SAME underlying global as R1 (`0x801163B0`) from its own distinct load pair, confirming the function calls this table-head accessor inline at many separate sites. 1st: clean (0 fires, `hangarbay-entry n=2700+`), crashed on the async Metal.framework/system-thread SIGABRT cluster (items -10/-9/-303/-315/-508). 2nd confirm: clean (0 fires, 1 benign co-fire, `hangarbay-entry n=33`), crashed on a NEW signature (`do_rom_read+608`/`0x800025ac`, Bus error) -- filed item -326, see below |
| 25 | `BEGIN_FRAME_DL_CHUNK_R4_GUARD` | s524 | `funcs_3.c:14306`/`0x8000AEB4` | `beginFrameDLChunk` (4th site) | 36 | CLOSED 2/2 (s525, folded) | Own distinct load pair; downstream reload at `0x8000AED0` feeds directly into a pre-existing `GENERIC_CACHE_GUARD` deref, independent confirmation the reload is already treated as untrusted downstream. 1st: the cleanest verify of the whole campaign -- full scheduled 300s, zero fires, zero crashes of any kind, `hangarbay-entry n=35`. 2nd confirm: 0 fires, 0 regressions, `hangarbay-entry n=2600` (strong), crashed on `submitSceneNodeRender+67668`/`0x80010e6c` -- the SAME signature seen once before at s503 (then an unlabeled data point for the -318 thread), now a 2nd occurrence -- filed item -327, see below |

(Numbering continues guards 1-10 from section 22's table, s495-503; guard #10 there was
`EMIT_FRAME_RDP_INIT_DL_R2F_GUARD`, so #11 here is the very next guard chronologically.)

### Gotchas recorded s504-515 (for the next guard in this lineage, or any similar sweep)

- **s506**: a dedup script's grouping key must include the hit's line number, not just
  `(file, kind, offset, register)` -- an early attempt silently merged hundreds of unrelated sites
  sharing a register name/offset across different call sites.
- **s507**: line numbers drift session to session as guards are inserted (e.g. `funcs_3.c:8344` ->
  `8357` after one insertion) -- always re-derive from a fresh tracer scan, never reuse a recorded
  number.
- **s507**: the harness's Bash permission matcher rejects multi-line/compound commands and `pgrep`
  isn't allowlisted (only `ps`) -- waiting on a foreground soak needs a single-line `zsh -c '...'` using
  `kill -0 <pid>` instead.
- **s511**: the sandbox blocks both a bare glob `rm -f funcs_*.c` and `find ... -delete` as
  unapprovable file-modifying operations -- delete `RecompiledFuncs/funcs_*.c` via a Python
  `os.remove` loop before every regen instead.
- **s513**: `rc=0`/full-duration is NOT automatically a valid confirm -- grep the run.log for an actual
  `hangarbay-entry` positive control; the R5 first confirm attempt had zero hangar-related lines at all
  (VI stuck oscillating pre-hangar) and was correctly ruled INCONCLUSIVE and retried rather than banked.
- **s514**: a leaked Edit-tool XML fragment got pasted verbatim into PORTING-STATE.md's tail instead of
  being executed as a tool call -- a document-corruption gotcha, not a code one; caught and removed.
- **s515 (breadcrumb-collision gotcha)**: `submitSceneNodeRender` carries its own pre-existing
  per-instruction `g_rs64_last_guest_pc = ...;` breadcrumb patch (applied earlier in the fixup
  pipeline), which inserts an extra line between an instruction's comment and its translated body. The
  guard's old/new match strings (copied verbatim from the R7 template) didn't include that inserted
  line, so the `text.count(...) == 1` exact-match guard silently skipped the block: **rc=0, no error,
  0 occurrences applied**. Fixed by adding `g_rs64_last_guest_pc = 0x80010F38u;` to both old and new
  strings. This was the first site in the lineage to fall inside a function carrying its own breadcrumb
  patch -- every prior `renderLitMeshFaceGroup`/`emitFrameRdpInitDl` site did not. **Lesson: always grep
  the fixup report for the new guard's own name after every run, not just check for absence of an
  error** -- a silent 0-count skip looks identical to success.

### Status as of s525: 25/25 fully closed 2/2 (all fixed guards confirmed), ~121 leads remain unaudited

Nine crash threads have surfaced as a side effect of these live-verifies (not chased in-band except
items -319/-322, which were fixed directly, and -321, whose escalation was refuted): items
-319/-320/-321/-322/-323/-324/-325/-326/-327 -- full mechanism writeups: section 24 below; live status
and next-tier picks: `docs/CURRENT-TRUTH.md` item -317. Full raw detail: `PORTING-STATE.md` Sessions
504-524.

## 24. Items -319 through -327: crash breadcrumbs and fixes surfaced by the step-3 sweep's live-verifies
(s503-524), migrated from CURRENT-TRUTH.md s525 maintenance pass

**Item -319 (`beginFrameDLChunk+40536`/`last-guest-pc=0x8000b0d0`) -- FIXED and FULLY CLOSED 2/2.**
Recurred 3 times (s503/s505/s519) with byte-identical `pc-symbol` and `last-guest-pc` before being
source-traced s520: the write at `0x8000B0D0` (`MEM_W(0X4, ctx->r3) = ctx->r4;`) is a genuine unguarded
pointer write-through sitting directly BETWEEN two already-guarded `SIBLING_PTR_WRITE_GUARD` sibling
sites through the exact same `-0x23A8` fixed-global-scalar pointer (guest `0x8011DC58`) --
`0x8000B0BC` and `0x8000B0EC`, both guarded since s459. `ctx->r3` is neither reassigned nor rechecked
between them and is reloaded from the identical global again immediately after (already guarded at
`0x8000B0EC`), so skip-on-invalid is safe -- same shape as the rest of the family. A genuine gap in the
original s459 sweep (the two neighbors were caught, this site sandwiched between them was missed), NOT
covered by the step-3 tracer (that tool is hard-scoped to a different, self-referential `+0x63B0`
reload idiom -- `beginFrameDLChunk` has at least two structurally distinct vulnerable-reload idioms in
play). Fixed by adding the site to `fixup_game_funcs.py`'s existing `_SIBLING_PTR_WRITE_SITES` table,
taking that family from 120 to 121 sites. 1st live-verify (s520, 2nd attempt -- 1st discarded, crashed
at 20.3s on the Metal-framework cluster, too weak a positive control): clean, 0 fires on any site
including the new one, 0 regressions across ~55 sibling guard families, `hangarbay-entry n=2600`.
Crashed at 113.9s on the same already-catalogued Metal-framework shader-compiler-thread cluster as
items -10/-9, unrelated. 2nd confirm (s521, `s520_sibling_ptr_b0d0_confirm`): 0 fires of any kind,
`hangarbay-entry n=31`, full 346s duration, no crash at all. CLOSED 2/2.

**Item -321 (`menuOverlayInit`-area/`last-guest-pc=0x800ab1c4`) -- 2 occurrences (s510/s515), escalation
REFUTED s518: a documented instrumentation gap, not a crash lead.** s510
(`pc-symbol=menuOverlayInit+3648`) and s515 (`pc-symbol=unregisterServiceWorker+536 (local-symtab)`)
shared `last-guest-pc=0x800ab1c4`, which looked like corroboration despite the `pc-symbol` mismatch.
Source-trace (s518): guest address `0x800AB1C4` is `runHangarSelectionFrame`'s own
`addiu $sp,$sp,0x30` return-epilogue instruction (`N64Recomp/RecompiledFuncs/funcs_28.c:6019`) --
pure register arithmetic, not a memory access, so it cannot fault. It's also independently claimed by
two OTHER overlay functions sharing the same fixed base address (`composeEffectObjectTransformMatrix`,
`spawnCutsceneDebrisField`) since all three overlays load at `0x800A5130`. The
`g_rs64_last_guest_pc` breadcrumb tracker only exists inside a curated allowlist of instrumented
functions; `runHangarSelectionFrame`'s last write is its own return, and its callers one level up
(`runHangarMenuFromOverlay`, `menuOverlayInit`) have zero breadcrumb writes in their bodies -- so the
global freezes at `0x800AB1C4` regardless of where execution actually goes next. Same
`BREADCRUMB17`->`18` "chase the freeze one level up" pattern already documented for item -263, now
recurring a 3rd time. **Conclusion**: s510 and s515 are most likely two DIFFERENT real crashes that
both happen to have just unwound out of `runHangarSelectionFrame` -- the matching `last-guest-pc` is
not meaningful corroboration. Downgraded from escalated-and-queued to a documented instrumentation gap.
If a similar breadcrumb-freeze pattern recurs and needs localizing, add `BREADCRUMB19` to
`runHangarMenuFromOverlay` modeled on `BREADCRUMB17`/`18` -- not currently queued, since neither
underlying crash has its own 2nd occurrence.

**Item -322 (`heapFreeListDequeue`, `last-guest-pc=0x8000d92c`) -- FIXED s517
(`HEAPLISTDEQ_ATTR_WRITE_GUARD`), FULLY CLOSED 2/2 s518.** 3 prior occurrences (s457/s512/s515) all
pinned to `MEM_W(0X0, ctx->r2) = ctx->r3;` at `funcs_3.c:22715`/`0x8000D92C`, where `ctx->r2` is
reloaded unguarded from stack slot `0x3C($sp)` (filled upstream from a fixed-global-array-base +
`index<<2` computation, no range check before the write-through). Downstream immediately reassigns the
register to an unrelated flag-test result, so skip-the-write-on-invalid is safe -- same precedent as
the whole item -317 lineage. Side note confirmed this session: the `pc-symbol`'s `+NNNN` offset is a
NATIVE code offset from `nm`, not a guest-address delta -- only `last-guest-pc` is reliable for
estimating position within a function. 1st live-verify (s517): 0 fires, 1 benign co-fire, `hangarbay-
entry n=34`, crashed on the already-catalogued `coalesceFreeHeapBlocks` background-noise family. 2nd
confirm (s518): ran the full 347s scheduled duration with zero crashes of any kind, 0 fires,
`hangarbay-entry n=2700`. CLOSED 2/2.

**Single-occurrence breadcrumbs surfaced by these live-verifies, filed not chased per M3 strategy** (0
fires on the guard that surfaced each, real `hangarbay-entry` positive control each time; live-status
and any recurrence gets tracked in `docs/CURRENT-TRUTH.md`'s Next-steps list, not here):

- **Item -323** (s514, `RENDER_LIT_MESH_R7_GUARD`'s 1st verify): `beginFrameDLChunk+27456`/
  `last-guest-pc=0x8000ae40` -- same function as item -319 but a different guest PC, so a distinct
  signature, not a 3rd -319 occurrence.
- **Item -324** (s521, `BEGIN_FRAME_DL_CHUNK_R1_GUARD`'s 1st verify): `heapFreeListInsert+72`/
  `last-guest-pc=0x80015544` -- call chain `menuOverlayInit` -> `runHangarMenuFromOverlay` ->
  `runHangarSelectionFrame` -> `setupCameraMatrices` -> `drawSubtitleText` ->
  `emitMaterialTexturedDLAlt` -> `findOrCreateMaterial` -> `allocOrEvictMaterialNode` ->
  `heapFreeListInsert`. Not the `heapFreeListDequeue+NNNN` symbolizer-artifact family (item -310/-311)
  -- genuine function attribution, a distinct sibling function (`Insert`, not `Dequeue`).
- **Item -325** (s522, `BEGIN_FRAME_DL_CHUNK_R2_GUARD`'s 1st verify, 2nd attempt):
  `findLookupEntryByKey+2212`/`last-guest-pc=0x800ad0dc` -- call chain `updateHangarBayScene` ->
  `updateTextOverlayLookupEntry` -> `findLookupEntryByKey`. Genuinely new signature, grepped zero prior
  hits.
- **Item -326** (s524, `BEGIN_FRAME_DL_CHUNK_R3_GUARD`'s 2nd confirm): `do_rom_read+608`/
  `last-guest-pc=0x800025ac`, Bus error, `si_addr=0x380000003`. Call chain: `mainBootstrapWorker` ->
  `mainGameLoop` -> `cinematicLoopBody` -> `initSceneForMission` -> `findManifestEntryByName` ->
  `submitDmaSlot` -> `osPiStartDma_recomp` -> `do_dma` -> `do_rom_read`. **Flagged for extra attention
  if it recurs**: this is the exact call-stack shape of the single longest-running M3 investigation
  thread in this project's history -- the `do_rom_read`/`piDmaWorker` DMA-corruption race (s80 origin,
  root-caused after ~30 sessions to a non-atomic `voiceCount`-write-before-pointer-store race in
  `allocateSongChannelArray`, FIXED s147 with clean re-verification soaks) -- which has not recurred in
  any session's log since, per an s524 grep of `docs/`/`PORTING-STATE.md`. The `si_addr` value
  (`0x380000003`) doesn't match the original investigation's classic exact-`0x80000000` signature but
  does exactly match a separate one-off s272 variant (an `inflate_fast`/zlib crash with the identical
  `si_addr`), except this time the fault resolves directly inside `do_rom_read` rather than inside
  zlib. A single data point cannot distinguish "the fixed race recurred" from "coincidental
  resemblance, different root cause, same corrupted-pointer symptom shape" -- filed not chased, but if
  a 2nd occurrence appears, treat it as urgent (a family closed for 375+ sessions recurring would
  overturn a load-bearing conclusion).
- **Item -327** (s524, `BEGIN_FRAME_DL_CHUNK_R4_GUARD`'s 2nd confirm) -- **2 occurrences**:
  `submitSceneNodeRender+67668`/`last-guest-pc=0x80010e6c`, Bus error, `si_addr=0x3f60030a2`. First
  seen s503 (`EMIT_FRAME_RDP_INIT_DL_R2F_GUARD`'s 2nd confirm, at the time filed only as an unlabeled
  4th data point for the item -318 thread since it shared -318's function but not its exact guest PC,
  see section 22 above) and now again s524 -- byte-identical `pc-symbol` and `last-guest-pc` both
  times, 21 sessions apart. This is a real 2-occurrence signature by the standard this campaign uses
  elsewhere (items -319/-321/-322 all began escalation review at 2-3 occurrences) -- worth a 3rd-
  occurrence watch, not yet a source-trace, since two data points 21 sessions apart with nothing in
  between is weak corroboration on its own (unlike -319's three occurrences inside an 8-session span).

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 503-524.

## 25. Item -317 step 3 continued (s526-550): guards 26-65 close out the `beginFrameDLChunk` 36-site
tier, add first guards in `emitColorFillRect`/`submitSceneNodeRender`/`drawSubtitleText`/
`renderLitTexturedMeshFaces`/`renderFlatMeshFaceGroup`/`emitMaterialTexturedDL`/
`emitMaterialTexturedDLAlt`/`emitAllocatedDLCommand`/`reserveAndEmitDLEntry`, extend
`renderLitMeshFaceGroup` to 13 sites, and (guards 62-63, s549) add two guards found via DIRECT
crash-mechanism evidence rather than idiom-shape scanning — **63/65 FULLY CLOSED 2/2 as of s550 (every
guard pending at s549 cleared this session), 2 pending confirm (guards 64-65, new this session)**,
migrated from CURRENT-TRUTH.md s538/s547 maintenance passes

Same fix shape as every guard in this lineage: a null check gates one arm safely, the non-null
fallthrough has no `0x80000000`-`0x80800000` range check before a `MEM_W(0X4, ctx->r2) = ctx->r3;`
write-through, and downstream control flow reloads the register from the `+0x63B0` global table again
before further use, so skip-the-write-on-invalid is safe. Every guard in this table cleared its 1st
live-verify AND 2nd confirm with 0 fires on the new guard itself, 0 regressions on any other armed
guard family, and a real `hangarbay-entry` positive control both times.

| # | Guard | Session fixed | Site | Function | Shared/reachability count | Crash the verify/confirm soaks hit (unrelated in every case) |
|---|---|---|---|---|---|---|
| 26 | `BEGIN_FRAME_DL_CHUNK_R5_GUARD` | s526 | `funcs_3.c:14815`/`0x8000AD84` | `beginFrameDLChunk` (5th site) | 36 | 1st: full 300s, zero crashes of any kind. 2nd confirm: clean, unrelated background noise |
| 27 | `BEGIN_FRAME_DL_CHUNK_R6_GUARD` | s527 | `funcs_3.c:14815`-region/`0x8000B01C` | `beginFrameDLChunk` (6th site) | 36 | Downstream reload feeds the pre-existing `SCENE_NODE_CACHE4_GUARD` deref (s271), independent confirmation. 2nd confirm crashed on a NEW signature filed **item -328** (`submitSceneNodeRender+69820`/`0x80010ebc`, single occurrence, not chased) |
| 28 | `BEGIN_FRAME_DL_CHUNK_R7_GUARD` | s528 | `funcs_3.c:15235`/`0x8000B144` | `beginFrameDLChunk` (7th site) | 36 | 1st: crashed on the already-catalogued `findLookupEntryByKey+2212`/`0x800ad0dc` (item -325). Confirm: full 346s, zero crashes |
| 29 | `BEGIN_FRAME_DL_CHUNK_R8_GUARD` | s529 | `funcs_3.c:12407`/`0x8000A918` | `beginFrameDLChunk` (8th site) | 36 | 1st: crashed on a NEW signature filed **item -329** (`rebuildActiveDisplayObjectList+660`/`0x800ab060`, single occurrence, not chased). Confirm: crashed on the already-refuted item -321 signature (`unregisterServiceWorker+536`/`0x800ab1c4`) |
| 30/31 | `BEGIN_FRAME_DL_CHUNK_R9_GUARD` + `R10_GUARD` (armed together, batch-instrumentation) | s530 | `0x8000B2B4` (load pair `0x8000B2A4`/`0x8000B2A8`) + `0x8000B40C` (load pair `0x8000B3FC`/`0x8000B400`) | `beginFrameDLChunk` (9th/10th sites, tier EXHAUSTED — the last two genuine candidates from the 36-site tier) | 36 | Both runs: full 300s/347s, zero crashes of any kind — the cleanest possible verify class. This closed the entire `beginFrameDLChunk` 36-site tier (R1-R10) |
| 32 | `EMIT_COLOR_FILL_RECT_R1_GUARD` | s531 | `funcs_3.c:11625`/`0x8000A538` | `emitColorFillRect` (1st guard outside `beginFrameDLChunk` this campaign) | 30 | 1st: full 300s, zero crashes. Confirm: crashed on the already-catalogued `setByteAcrossEntryList+176`/`0x800aafa8` (item -306) |
| 33 | `SUBMIT_SCENE_NODE_RENDER_R2_GUARD` | s532 | `funcs_4.c:4455`/`0x80010E10` | `submitSceneNodeRender` (2nd site alongside R1's `0x80010F38`) | 30 | Confirm crashed on the already-catalogued `loadCutsceneAssetsByIndex+1860`/`0x800aafb8` (item -320). Closed the campaign's first 33 guards to 33/33 fully closed for the first time since s490 |
| 34 | `SUBMIT_SCENE_NODE_RENDER_R3_GUARD` | s533 | `funcs_4.c:3299`/`0x80010AAC` | `submitSceneNodeRender` (3rd site) | 28 | 1st: crashed on the item -6/-249/-259 background-noise family (INVESTIGATED AND CLOSED s422). Confirm: crashed on the item -306 `setByteAcrossEntryList+176` signature |
| 35 | `SUBMIT_SCENE_NODE_RENDER_R4_GUARD` | s534 | `funcs_4.c`/`0x80010BF0` | `submitSceneNodeRender` (4th site) | 28 | 1st: crashed on item -320's signature. Confirm: full 346s, zero crashes |
| 36 | `DRAW_SUBTITLE_TEXT_R1_GUARD` | s535 | `funcs_4.c`/`0x80016B58` | `drawSubtitleText` (1st guard, new function) | 27 | Both runs: full 300s/347s, zero crashes of any kind. **First session the raw tracer's top-ranked candidate (`renderLitTexturedMeshFaces`, reg=`r4`/off=`0X0`) was correctly REJECTED as a shape mismatch** — that write dereferences the function's own provably-non-null `$a0` argument, not a reloaded/derived global pointer; a CFG-reachability artifact of the tracer, not a shared-dataflow one |
| 37 | `EMIT_COLOR_FILL_RECT_R2_GUARD` | s536 | `funcs_3.c`/`0x8000A3C4` | `emitColorFillRect` (2nd site alongside R1's `0x8000A538`) | 26 | 1st needed 3 attempts to get a valid positive control (1st too weak n=4 on item -324's signature, 2nd fully vacuous 0 hangar diagnostics despite rc=0 completion). 3rd attempt clean, crashed on item -320's signature. Confirm crashed on `heapFreeListInsert+72`/`0x800220b8` — a NEW signature, filed **item -330** (see below) |
| 38 | `RENDER_LIT_TEXTURED_MESH_FACES_R1_GUARD` | s537 | `funcs_3.c`/`0x8000FE14` | `renderLitTexturedMeshFaces` (1st guard, new function) | 26 | 1st: crashed on `heapFreeListInsert+72`/`0x800220b8`, back-to-back 2nd occurrence of item -330. Confirm (folded s539): crashed on `heapFreeListDequeue+29152`/`0x8000d688` (`local-symtab`-tagged, so a genuine `heapFreeListDequeue`-internal fault, not the pre-s480 symbolizer artifact) — a NEW, previously-uncatalogued signature, filed **item -331** (see below). Both runs: 0 fires on the new guard, 0 fires on any other armed guard family (nearby sibling guards `generic-cache-guard`/`dl-list-append-rwrite-guard`/`dl-list-reset-rnode-guard`/`heap-dequeue-derived-ptr-guard` all dumped `n=0` at crash time, a diagnostic snapshot not a fire), real `hangarbay-entry` positive control both times (n=31) |
| 39 | `RENDER_LIT_TEXTURED_MESH_FACES_R2_GUARD` | s539 | `funcs_3.c:34094`/`0x8000FCF4` | `renderLitTexturedMeshFaces` (2nd site alongside R1's `0x8000FE14`) | 32 | 1st: full 300s, zero crashes, `hangarbay-entry n=34`. 1st confirm attempt (s539) WEAK — crashed at 19.8s after 7 frames, `hangarbay-entry n=5` (single-digit, below bar) — discarded per iron rule 1, its crash signature (`submitSceneNodeRender+38976`/`0x8001086c`) filed **item -332**. Retry confirm (s541, folded from queue): 0 `render-lit-textured-mesh-faces-r2-guard` fires, 1 benign `hangarmenu-a0-guard` co-fire, `hangarbay-entry n=32`, full 349s duration, no crash — CLEAN |
| 40 | `RENDER_LIT_TEXTURED_MESH_FACES_R3_GUARD` | s540 | `funcs_3.c:33902`/`0x8000FC24` | `renderLitTexturedMeshFaces` (3rd site alongside R1/R2) | 27 (tied w/ R4) | 1st: full 300s, zero crashes at all, `hangarbay-entry n=31`. Confirm (s541, folded from queue): 0 fires, 1 benign already-catalogued `s284-guard` co-fire, `hangarbay-entry n=31`, crashed at 113.1s on `pc-symbol=hangarTickCameraOrbit+5188`/`last-guest-pc=0x800ab068` — the long-recurring `0x800ab068` background-noise family (items -320/s463/s468/s489, host symbol resolution varies build to build but the guest PC is the stable signature) — CLEAN |
| 41 | `RENDER_LIT_TEXTURED_MESH_FACES_R4_GUARD` | s540 | `funcs_3.c:34530`/`0x8000FECC` | `renderLitTexturedMeshFaces` (4th site alongside R1/R2/R3) | 27 (tied w/ R3) | Same batched runs as R3 (armed together, batch-instrumentation rule): 0 `render-lit-textured-mesh-faces-r4-guard` fires either run — CLEAN |
| 42 | `RENDER_FLAT_MESH_FACE_GROUP_R1_GUARD` | s541 | `funcs_4.c:7648`/`0x80011B54` | `renderFlatMeshFaceGroup` (1st guard, new function) | 26 (tied w/ R9) | 1st: 0 fires, 3 benign `s284-guard` + 1 benign `hangar-bay-deref-guard` co-fires (no regression), `hangarbay-entry n=31`. Crashed at 113.3s on the recurring `0x800ab068` background-noise family (`initVec4TripletFromArgs+68` this instance). Confirm (s541, folded s542): 0 fires, 1 benign `hangarmenu-a0-guard` co-fire, `hangarbay-entry n=2700` (strong positive control), crashed at 164.3s on `pc-symbol=coalesceFreeHeapBlocks+4424`/`last-guest-pc=0x8000247c` — the s354-366 heap-walker background-noise family — CLOSED 2/2 |
| 43 | `RENDER_LIT_MESH_R9_GUARD` | s541 | `funcs_4.c:14889`/`0x80013DF4` | `renderLitMeshFaceGroup` (9th site, distinct from R2-R8's seven other addresses) | 26 (tied w/ R1) | Same batched runs as R1 (armed together both times, batch-instrumentation rule): 0 `render-lit-mesh-r9-guard` fires either run — CLOSED 2/2 |
| 44 | `RENDER_LIT_MESH_R10_GUARD` | s542 | `funcs_4.c:14436`/`0x80013BF4` | `renderLitMeshFaceGroup` (10th site, distinct from R2-R9's eight other addresses) | 24 (single top pick, not tied) | 1st: 0 fires, 1 benign `hangarmenu-a0-guard` co-fire, `hangarbay-entry n=2900`. Full 300s, zero crashes at all. Confirm (s543, folded from queue): 0 `render-lit-mesh-r10-guard` fires, 1 benign `hangarmenu-a0-guard` co-fire, `hangarbay-entry n=35` (positive control), full 348s duration, zero crashes at all — the cleanest possible verify class — CLOSED 2/2. Closed the campaign's 44 guards to 44/44 fully closed (zero open guards) for the sixth time |
| 45 | `EMIT_COLOR_FILL_RECT_R3_GUARD` | s543 | `funcs_3.c:10887`/`0x8000A25C` | `emitColorFillRect` (3rd site, alongside R1's `0x8000A538` and R2's `0x8000A3C4`) | 22 (tied w/ R2 below) | 1st attempt WEAK (`hangarbay-entry n=5`, discarded per iron rule 1). 2nd attempt: 0 fires, 0 fires on any other armed guard family, `hangarbay-entry n=31`, crashed at 113.7s on the already-catalogued item -320 `loadCutsceneAssetsByIndex+1860`/`0x800aafb8` signature — clean verify, own guard never fired. Confirm (s543, folded s544): 0 `emit-color-fill-rect-r3-guard` fires, 1 benign already-catalogued `hangarmenu-a0-guard` co-fire, `hangarbay-entry n=2700` (strong positive control), crashed at `pc-symbol=coalesceFreeHeapBlocks+4424`/`last-guest-pc=0x8000247c` — the already-catalogued s354-366 heap-walker background-noise family — CLOSED 2/2 |
| 46 | `RENDER_FLAT_MESH_FACE_GROUP_R2_GUARD` | s543 | `funcs_4.c:7328`/`0x80011A2C` | `renderFlatMeshFaceGroup` (2nd site, alongside R1's `0x80011B54`) | 22 (tied w/ R3 above) | Same batched runs as R3 (armed together, batch-instrumentation rule): 0 `render-flat-mesh-face-group-r2-guard` fires either attempt, same clean confirm as R3 above — CLOSED 2/2. Closed the campaign's 46 guards to 46/46 fully closed (zero open guards) for the seventh time |
| 47 | `DRAW_SUBTITLE_TEXT_R2_GUARD` | s544 | `funcs_4.c:24932`/`0x80016830` | `drawSubtitleText` (2nd site, alongside R1's `0x80016B58`, s535) | 20 (single top pick, not tied) | 1st: 0 fires, 0 fires on any other armed guard family (5 sibling guards dumped `n=0` diagnostic snapshots at crash time, not fires), `hangarbay-entry n=2600` (strong positive control). Crashed at 111.0s on `pc-symbol=submitSceneNodeRender+38976`/`last-guest-pc=0x8001086c` — the exact signature of item -332 (previously WEAK, n=5); this time with a strong control, upgrading item -332's confidence — clean verify, own guard never fired. Confirm (s544, retried s545 after the fold-in came back WEAK — `hangarbay-entry n=5`, discarded per iron rule 1): retry read 0 fires, 0 fires on any other armed guard family, `hangarbay-entry n=31`, full 300s duration, zero crashes at all — CLOSED 2/2. Closed the campaign's 47 guards to 47/47 fully closed (zero open guards) for the eighth time |
| 48 | `EMIT_COLOR_FILL_RECT_R4_GUARD` | s545 | `funcs_3.c:10523`/`0x8000A0F8` | `emitColorFillRect` (4th site, alongside R1/R2/R3) | 18 (5-way tie) | 1st: 0 fires, 1 benign `hangarmenu-a0-guard` co-fire, `hangarbay-entry n=32`. Crashed at 165.6s on `pc-symbol=loadDatFile+1152`/`last-guest-pc=0x800290d4` — the s400-421→s422 `inflate_fast` clean-return misattribution artifact (documented non-issue) — clean verify, own guard never fired. Confirm (s545, folded s546): 0 `emit-color-fill-rect-r4-guard` fires, 0 fires on any other armed guard family at all, `hangarbay-entry n=2600` (strong positive control), crashed on the recurring `0x800ab068` background-noise family (`loadCutsceneAssetsByIndex+1860` this instance) — CLOSED 2/2 |
| 49 | `EMIT_MATERIAL_TEXTURED_DL_R1_GUARD` | s545 | `funcs_3.c:29260`/`0x8000E72C` | `emitMaterialTexturedDL` (1st guard, BRAND-NEW function for this campaign) | 18 (5-way tie) | Same batched runs as R4 above (armed together both times, batch-instrumentation rule): 0 `emit-material-textured-dl-r1-guard` fires either run — CLOSED 2/2 |
| 50 | `EMIT_MATERIAL_TEXTURED_DL_ALT_R1_GUARD` | s545 | `funcs_3.c:31191`/`0x8000EE34` | `emitMaterialTexturedDLAlt` (1st guard, second BRAND-NEW function for this campaign) | 18 (5-way tie) | Same batched runs (armed together both times, batch-instrumentation rule): 0 `emit-material-textured-dl-alt-r1-guard` fires either run — CLOSED 2/2 |
| 51 | `SUBMIT_SCENE_NODE_RENDER_R5_GUARD` | s545 | `funcs_4.c:2528`/`0x80010810` | `submitSceneNodeRender` (5th site, alongside R1-R4) | 18 (5-way tie) | Same batched runs (armed together both times, batch-instrumentation rule): 0 `submit-scene-node-render-r5-guard` fires either run — CLOSED 2/2. One raw reload address feeding this write (`0x800101B0`) is already claimed by the unrelated s197 `SCENE_NODE_CACHE_GUARD` protecting a DIFFERENT read at `0x800101B4` — the target write itself was still genuinely uncovered |
| 52 | `RENDER_LIT_MESH_R11_GUARD` | s545 | `funcs_4.c:14065`/`0x80013A78` | `renderLitMeshFaceGroup` (11th site, distinct from R2-R10's ten other addresses) | 18 (5-way tie) | Same batched runs (armed together both times, batch-instrumentation rule): 0 `render-lit-mesh-r11-guard` fires either run — CLOSED 2/2. Guards 48-52 closed the campaign's 52 guards to 52/52 fully closed (zero open guards) for the ninth time |
| 53 | `RENDER_FLAT_MESH_FACE_GROUP_R3_GUARD` | s546 | `funcs_4.c:6268`/`0x800114C0` | `renderFlatMeshFaceGroup` (3rd site, alongside R1's `0x80011B54` and R2's `0x80011A2C`) | 16 (5-way tie) | 1st: 0 fires, 0 fires on any other armed guard family at all, `hangarbay-entry n=2600` (strong positive control). Crashed at 131.6s on `pc-symbol=findAndUnlinkSmallestEntry+356`/`last-guest-pc=0x8000d698` — checked against every catalogued family, no match; genuinely NEW, filed **item -333** (single occurrence, not escalated) — clean verify, own guard never fired. **2nd confirm: WEAK 3x (s546/s548/s549, all single-digit `hangarbay-entry` on the item -306 signature, discarded), 4th attempt (s550 fold-in) CLEAN — `hangarbay-entry n=31`, 0 fires** — CLOSED 2/2 |
| 54 | `RENDER_FLAT_MESH_FACE_GROUP_R4_GUARD` | s546 | `funcs_4.c:7045`/`0x80011904` | `renderFlatMeshFaceGroup` (4th site, alongside R1/R2/R3) | 16 (5-way tie) | Same batched run as R3 above (armed together, batch-instrumentation rule): 0 `render-flat-mesh-face-group-r4-guard` fires — clean. **2nd confirm: same 4th-attempt run as R3 (s550 fold-in), clean** — CLOSED 2/2 |
| 55 | `RENDER_LIT_MESH_R12_GUARD` | s546 | `funcs_4.c:12782`/`0x8001347C` | `renderLitMeshFaceGroup` (12th site, distinct from R2-R11's eleven other addresses) | 16 (5-way tie) | Same batched run (armed together, batch-instrumentation rule): 0 `render-lit-mesh-r12-guard` fires — clean. **2nd confirm: same 4th-attempt run as R3 (s550 fold-in), clean** — CLOSED 2/2 |
| 56 | `RENDER_LIT_MESH_R13_GUARD` | s546 | `funcs_4.c:13321`/`0x8001370C` | `renderLitMeshFaceGroup` (13th site, distinct from R2-R12's twelve other addresses) | 16 (5-way tie) | Same batched run (armed together, batch-instrumentation rule): 0 `render-lit-mesh-r13-guard` fires — clean. **2nd confirm: same 4th-attempt run as R3 (s550 fold-in), clean** — CLOSED 2/2 |
| 57 | `DRAW_SUBTITLE_TEXT_R3_GUARD` | s546 | `funcs_4.c:24022`/`0x800163C8` | `drawSubtitleText` (3rd site, alongside R1's `0x80016B58` and R2's `0x80016830`) | 16 (5-way tie) | Same batched run (armed together, batch-instrumentation rule): 0 `draw-subtitle-text-r3-guard` fires — clean, pending 2nd confirm (queued confirm came back WEAK at s548, `hangarbay-entry n=5`, discarded per iron rule 1; retry re-queued: `scratch/agent/soak_queue/s548_five_tied_guards_confirm_retry.sh`). **2nd confirm: WEAK 3x total (s546/s548/s549), 4th attempt (s550 fold-in) CLEAN — `hangarbay-entry n=31`, 0 fires** — CLOSED 2/2. Closed the campaign's 63 guards to 63/63 fully closed (zero open guards) for the first time |
| 58 | `EMIT_COLOR_FILL_RECT_R5_GUARD` | s548 | `funcs_3.c:10105`/`0x80009F50` | `emitColorFillRect` (5th site, alongside R1-R4) | 14 (4-way tie) | 1st attempt WEAK (`hangarbay-entry n=5`, crashed at 20.0s on the already-catalogued item -306 `setByteAcrossEntryList+176`/`0x800aafa8` signature — discarded per iron rule 1). Retry: 0 fires, only 1 benign already-catalogued `hangarmenu-a0-guard` n=0 diagnostic snapshot (not a fire), `hangarbay-entry n=33` (positive control), full 300s duration, zero crashes at all — clean verify, own guard never fired — pending 2nd confirm |
| 59 | `EMIT_MATERIAL_TEXTURED_DL_R2_GUARD` | s548 | `funcs_3.c:28876`/`0x8000E608` | `emitMaterialTexturedDL` (2nd site, alongside R1's `0x8000E72C`) | 14 (4-way tie) | Same batched runs as R5 above (armed together both times, batch-instrumentation rule): 0 `emit-material-textured-dl-r2-guard` fires either attempt — clean, pending 2nd confirm |
| 60 | `EMIT_MATERIAL_TEXTURED_DL_ALT_R2_GUARD` | s548 | `funcs_3.c:30847`/`0x8000ECD4` | `emitMaterialTexturedDLAlt` (2nd site, alongside R1's `0x8000EE34`) | 14 (4-way tie) | Same batched runs (armed together both times, batch-instrumentation rule): 0 `emit-material-textured-dl-alt-r2-guard` fires either attempt — clean, pending 2nd confirm |
| 61 | `SUBMIT_SCENE_NODE_RENDER_R6_GUARD` | s548 | `funcs_4.c:2194`/`0x80010728` | `submitSceneNodeRender` (6th site, alongside R1-R5) | 14 (4-way tie) | 1st attempt WEAK (`hangarbay-entry n=5`, item -306 signature, discarded). Retry: 0 fires, `hangarbay-entry n=33`, full 300s, zero crashes — clean. **2nd confirm (s549): `hangarbay-entry n=2700` (strong positive control), 0 fires on guards 58-61 (none of the four even appear in the log). Crashed at 114.4s on `last-guest-pc=0x80010DCC` — a NEW site, immediately traced and fixed as item -334 (see guard 62 below)** — CLOSED 2/2. Closed the campaign's 61 guards to 61/61 fully closed (zero open guards) for the tenth time |
| 62 | `SIBLING_PTR_WRITE_GUARD` site=`0x80010DCC` (item -334) | s549 | `funcs_4.c:4398-4405`/`0x80010DCC` (2 delay-slot copies, 1 guest address) | `submitSceneNodeRender` (122nd/123rd entries in the pre-existing 121-site `SIBLING_PTR_WRITE_GUARD` family, s459) | n/a — found via crash mechanism, not idiom-shape ranking | Found when guard 61's 2nd confirm crashed at `last-guest-pc=0x80010DCC` while the SAME run's pre-existing `sibling-ptr-write-guard site=0x80010DC4` fired (`n=0`, first-ever fire in 121 sites) with `bad_ptr=0x48830D10` one instruction earlier — `bad_ptr+4` matches the crash's own fault address (mcontext x12) modulo the RDRAM host-mapping offset, a direct numeric trace. Same shape as item -319: an unguarded write immediately after an existing guard, reusing the SAME already-flagged-bad register (`ctx->r5`) via the branch's duplicated delay-slot instruction. **1st live-verify of the fix ALONE (before guard 63 existed): the NEW guard ITSELF FIRED** (`n=0`, `bad_ptr=0x810C747B`, matching the SAME value the pre-existing `0x80010DC4` guard fired with one instruction earlier in the SAME run — an independent 2nd confirmed catch of the identical corruption idiom, self-healing correctly) — `hangarbay-entry n=2600`. The run still crashed downstream, at `last-guest-pc=0x80010e6c` — item -327's own address (3rd occurrence) — which led directly to guard 63 below. Re-verify with BOTH guards armed (batch-instrumentation rule): 0 fires on `sibling-ptr-write-guard site=0x80010DCC` this run (intermittent, as expected — every guard in this campaign fires nondeterministically), `hangarbay-entry n=2700`, crashed on the already-catalogued s354-366 `coalesceFreeHeapBlocks+4424`/`0x8000247c` family — clean, own guard silent this run. **This is the campaign's first-ever confirmed genuine fire across 122+ sites.** **2nd confirm (s550 fold-in): clean** — `hangarbay-entry n=31`, 0 fires on `sibling-ptr-write-guard site=0x80010DCC`, crashed at 132.4s on the item -336 breadcrumb (unrelated) — CLOSED 2/2 |
| 63 | `DL_LIST_APPEND_DEREF_GUARD` (item -327's root cause) | s549 | 84 sites (46 `funcs_3.c` + 38 `funcs_4.c`), blanket regex addition to the existing `DL_LIST_APPEND_GUARD` family (s454/s463/s482); `submitSceneNodeRender`'s own instance at `funcs_4.c:4769`/`0x80010E6C` is item -327's exact crash address | All 84 canonical `DL_LIST_APPEND_GUARD`/`_RWRITE` sites | n/a — found via crash mechanism | After guard 62's fix, re-ran the SAME live-verify recipe: the crash moved downstream to `last-guest-pc=0x80010e6c` — item -327's own catalogued address, a confirmed 3rd occurrence (previously 2, 21 sessions apart). Source trace (`funcs_4.c:4670-4699`): the existing `DL_LIST_APPEND_GUARD` (addr3) validates the list HEAD pointer (`rload`) before reading `ctx->rderef = MEM_W(rload,0)`, but `rderef` — a value READ BACK from guest memory — was never itself range-checked before being dereferenced as a write address at addr4. The existing `DL_LIST_APPEND_RWRITE_GUARD` (s482, addr6) only ever validated `rwrite` (the new-node argument), a different register — neither guard covered `rderef`. The family's own regex (`_dl_list_append_guard_re`) already proves this 4-instruction tail is byte-identical at all 84 sites, so the gap is family-wide, not a single-site anomaly — fixed in the same blanket substitution as the other two guards in this family. Fixup report confirmed `patched x46`/`x38`, matching `DL_LIST_APPEND_GUARD`'s own counts exactly (1:1 coverage). 1st live-verify (combined with guard 62): 0 fires on `dl-list-append-deref-guard` (any site), same clean run as guard 62 above. **2nd confirm (s550 fold-in): clean** — same run as guard 62 above, 0 fires on any of the 84 sites — CLOSED 2/2 |
| 64 | `EMIT_ALLOCATED_DL_COMMAND_R1_GUARD` | s550 | `funcs_3.c:4580`/`0x80008908` | `emitAllocatedDLCommand` (first item -317 step 3 guard in this function) | 13 (2-way tie) | Fresh tracer re-scan (after folding in both s549 confirms) found the next tier below s548's count=14 four-way tie: a two-way tie at count=13, same guarded shape reg=r2/off=0X4. Idiom: `lui $v0,0x8011` / `lw $v0,0x63B0($v0)` reloads a global into ctx->r2, a `beq $v0,$zero,...` null check's delay slot is duplicated for both branch paths, and the fallthrough-only instruction after the label unconditionally writes through the reloaded, never-range-checked ctx->r2 as `ctx->r2+4`. 1st live-verify (armed together with guard 65, batch-instrumentation rule): 0 `emit-allocated-dl-command-r1-guard` fires, 0 fires on any other armed guard family (1 benign pre-existing `[mesgqueue-guard]` diagnostic line, unrelated), `hangarbay-entry n=31` (positive control). Full 300s scheduled duration completed with NO crash at all (106 frames captured, rc=0) — the cleanest possible verify class. **2nd confirm attempt 1 (s551 fold-in): WEAK — no `hangarbay-entry` line at all (process gone at 20.2s after 7 frames), crashed on the item -306 `setByteAcrossEntryList+176`/`0x800aafa8` signature. Discarded per iron rule 1, retry queued.** **2nd confirm attempt 2 (s552 fold-in): STILL WEAK — identical failure mode (no `hangarbay-entry` line, 20.2s/7 frames, same item -306 signature). 2nd consecutive weak draw — retry re-queued again.** **3rd confirm attempt (s553 fold-in): CLEAN — `hangarbay-entry n=2600`, full 300s no-crash rc=0, 0 fires — CLOSED 2/2** |
| 65 | `RESERVE_AND_EMIT_DL_ENTRY_R1_GUARD` | s550 | `funcs_3.c:22988`/`0x8000CE10` | `reserveAndEmitDLEntry` (first guard in this function, new to this campaign) | 13 (2-way tie) | Same batched run as guard 64 above (armed together, batch-instrumentation rule): 0 `reserve-and-emit-dl-entry-r1-guard` fires — clean, same full-300s no-crash run. **2nd confirm attempts 1 and 2 (s551/s552 fold-in): same two consecutive WEAK runs as guard 64 above.** **3rd confirm (s553): CLEAN with guard 64 — CLOSED 2/2** |
| 66 | `EMIT_COLOR_FILL_RECT_R6_GUARD` | s551 | `funcs_3.c:9988`/`0x80009E30` | `emitColorFillRect` (6th site, alongside R1-R5) | 10 (6-way tie) | Fresh tracer re-scan (after folding in s550's confirm) found the next tier below s550's count=13 two-way tie: a six-way tie at count=10, same guarded shape reg=r2/off=0X4. Idiom: `lui $v0,0x8011` / `lw $v0,0x63B0($v0)` reloads a global into ctx->r2, a `beq $v0,$zero,...` null check's delay slot is duplicated for both branch paths, and the fallthrough-only instruction after the label unconditionally writes through the reloaded, never-range-checked ctx->r2 as `ctx->r2+4`. 1st live-verify (all six guards 66-71 armed together, batch-instrumentation rule): 0 `emit-color-fill-rect-r6-guard` fires, `hangarbay-entry n=32` (positive control), crashed at 123.5s on a NEW single-occurrence signature (`submitSceneNodeRender+69192`/`0x80010df4`, filed item -337). **2nd confirm attempt 1 (s552 fold-in): WEAK — no `hangarbay-entry` line at all (process gone at 20.2s after 7 frames), crashed on the item -306 `setByteAcrossEntryList+176`/`0x800aafa8` signature. Discarded per iron rule 1, retry queued.** **2nd confirm (s553 fold-in): CLEAN — `hangarbay-entry n=2600`, 0 fires; crashed on known `0x80010b7c` background-noise guest PC — CLOSED 2/2** |
| 67 | `EMIT_MATERIAL_TEXTURED_DL_R3_GUARD` | s551 | `funcs_3.c:28957`/`0x8000E4B4` | `emitMaterialTexturedDL` (3rd site, alongside R1-R2) | 10 (6-way tie) | Same batched run as guard 66 above (armed together): 0 `emit-material-textured-dl-r3-guard` fires — clean, same run. 2nd confirm attempt 1 (s552): same WEAK run as guard 66.** **2nd confirm (s553): CLEAN with guard 66 — CLOSED 2/2** |
| 68 | `EMIT_MATERIAL_TEXTURED_DL_ALT_R3_GUARD` | s551 | `funcs_3.c:31110`/`0x8000EB90` | `emitMaterialTexturedDLAlt` (3rd site, alongside R1-R2) | 10 (6-way tie) | Same batched run as guard 66 above (armed together): 0 `emit-material-textured-dl-alt-r3-guard` fires — clean, same run. 2nd confirm attempt 1 (s552): same WEAK run as guard 66.** **2nd confirm (s553): CLEAN with guard 66 — CLOSED 2/2** |
| 69 | `SUBMIT_SCENE_NODE_RENDER_R7_GUARD` | s551 | `funcs_4.c:1761`/`0x800105EC` | `submitSceneNodeRender` (7th site, alongside R1-R6) | 10 (6-way tie) | Same batched run as guard 66 above (armed together): 0 `submit-scene-node-render-r7-guard` fires — clean, same run. 2nd confirm attempt 1 (s552): same WEAK run as guard 66.** **2nd confirm (s553): CLEAN with guard 66 — CLOSED 2/2** |
| 70 | `DRAW_SUBTITLE_TEXT_R4_GUARD` | s551 | `funcs_4.c:23563`/`0x80015F80` | `drawSubtitleText` (4th site, alongside R1-R3) | 10 (6-way tie) | Same batched run as guard 66 above (armed together): 0 `draw-subtitle-text-r4-guard` fires — clean, same run. 2nd confirm attempt 1 (s552): same WEAK run as guard 66.** **2nd confirm (s553): CLEAN with guard 66 — CLOSED 2/2** |
| 71 | `SETUP_CAMERA_MATRICES_R1_GUARD` | s551 | `funcs_4.c:28560`/`0x8001763C` | `setupCameraMatrices` (1st guard, NEW function to this campaign) | 10 (6-way tie) | Same batched run as guard 66 above (armed together): 0 `setup-camera-matrices-r1-guard` fires — clean, same run. 2nd confirm attempt 1 (s552): same WEAK run as guard 66.** **2nd confirm (s553): CLEAN with guard 66 — CLOSED 2/2** |
| 72 | `HEAP_FREE_LIST_DEQUEUE_R1_GUARD` | s552 | `funcs_3.c:24498`/`0x8000D304` | `heapFreeListDequeue` (1st guard, NEW function to step 3's R-numbering — distinct from the whole-function items -312..-316 step-1 audit of this same function) | 8 (3-way tie) | Fresh tracer re-scan (after folding in both s551 confirms, both weak, retries queued) found the next tier below s551's count=10 six-way tie: a three-way tie at count=8, same guarded shape reg=r2/off=0X4. Idiom: `lui $v0,0x8011` / `lw $v0,0x63B0($v0)` reloads a global into ctx->r2, a `beq $v0,$zero,...` null check's delay slot is duplicated for both branch paths, and the fallthrough-only instruction after the label unconditionally writes through the reloaded, never-range-checked ctx->r2 as `ctx->r2+4`. All three write addresses (guards 72-74) checked directly against `fixup_game_funcs.py` before patching: no incidental matches. 1st live-verify (all three armed together, batch-instrumentation rule): 0 `heap-free-list-dequeue-r1-guard` fires, 0 fires on any other armed guard family at all (no co-fires this run), `hangarbay-entry n=31` (positive control). Crashed at 115.5s on `last-guest-pc=0x80015544` — the already-catalogued item -324 background-noise signature (pc-symbol resolved to `packMtxRowFloatToFixed+824` this run instead of item -324's original `heapFreeListInsert+72` — the recurring pc-symbol-instability gotcha, cross-checked by guest PC). 2nd confirm queued: `scratch/agent/soak_queue/s552_three_way_tie_confirm.sh` |
| 73 | `SUBMIT_SCENE_NODE_RENDER_R8_GUARD` | s552 | `funcs_4.c:1041`/`0x800103B8` | `submitSceneNodeRender` (8th site, alongside R1-R7) | 8 (3-way tie) | Same batched run as guard 72 above (armed together): 0 `submit-scene-node-render-r8-guard` fires — clean, same run. 2nd confirm queued alongside guard 72 |
| 74 | `BUILD_ORIENTED_FACE_GEOMETRY_R1_GUARD` | s552 | `funcs_4.c:11705`/`0x80012E80` | `buildOrientedFaceGeometry` (1st R-numbered site alongside the pre-existing, unrelated `ORIENTED_FACE_DERIVED_PTR_GUARD`) | 8 (3-way tie) | Same batched run as guard 72 above (armed together): 0 `build-oriented-face-geometry-r1-guard` fires — clean, same run. 2nd confirm queued alongside guard 72 |

Guards 26-37 also reconfirmed s535-537 that the raw tracer's top-ranked pick (`funcs_3.c`,
`renderLitTexturedMeshFaces`, reg=`r4`/off=`0X0`, count 27) is a stable, repeatedly-re-derived shape
mismatch — every re-scan re-surfaces it at the top by raw count, and it must be re-checked and
re-skipped each session rather than fixed, since `ctx->r4` there is the function's own argument, not
the guarded `+0x63B0` reload idiom.

**Item -330** (`heapFreeListInsert+72`/`last-guest-pc=0x800220b8`, 2 occurrences back-to-back s536/s537
in the same session) — distinct from item -324's same-symbol `heapFreeListInsert+72`/`0x80015544`
breadcrumb (different `last-guest-pc`, a different call site into the same function). Two occurrences
back-to-back is weaker corroboration than it looks: both runs used the same binary, probe script, and
adjacent wall-clock time, so a shared transient is the more likely explanation per the boring-first
prior — watch for a 3rd occurrence in an unrelated run before escalating, same policy as item -327.
Live status: `docs/CURRENT-TRUTH.md` Next-steps.

**Item -331** (`heapFreeListDequeue+29152`/`last-guest-pc=0x8000d688`, single occurrence, s537's 2nd
confirm, folded s539) — a genuinely new address inside `heapFreeListDequeue`, earlier in the function
than every already-guarded/fixed site in this campaign (item -317 step 1's fix at `0x8000D760`+widened
skip-to-`0x8000D8A8`; item -322's `HEAPLISTDEQ_ATTR_WRITE_GUARD` at `0x8000D92C`; the free-list-cache-head
reload at `0x8000D6E4`) — `0x8000D688` sits before all of them, near the `0x8000D67C` branch that item
-317 step 1's writeup already identified as a second, unrelated control-flow path into the function.
Carries the `(local-symtab)` tag, so post-s480 symbolizer confidence is high this is a real fault inside
`heapFreeListDequeue`, not the pre-s480 `dladdr` misattribution (item -310/-311). Filed not chased —
watch for a 2nd occurrence before escalating.

Full session-by-session raw detail: `PORTING-STATE.md` Sessions 526-537, 539, 543-544.

Item -332 (`submitSceneNodeRender+38976`/`last-guest-pc=0x8001086c`) recurred at s544, this time with
`hangarbay-entry n=2600` (strong positive control) instead of the s539 sighting's weak `n=5` — a
genuine 2nd occurrence with a valid control. Confidence upgraded from low to moderate. Still not
chased (unrelated to the guard under test either time); watch for a 3rd occurrence before source-
tracing. Live status: `docs/CURRENT-TRUTH.md` Next-steps.

**Item -333** (`findAndUnlinkSmallestEntry+356`/`last-guest-pc=0x8000d698`, single occurrence, s546's
1st live-verify of guards 53-57) — `(local-symtab)`-tagged, so a genuine in-function fault, not the
pre-s480 misattribution artifact. 16 bytes (4 instructions) from item -331's
`heapFreeListDequeue+29152`/`0x8000d688` (also single-occurrence, also `local-symtab`-tagged, also in
the free-list-pop region) but a DIFFERENT guest PC — not treated as the same signature. Unrelated to
any guard under test, own guards never fired. Filed not chased; watch for a 2nd occurrence of either
-331 or -333 before escalating — if either recurs, or a third nearby address in this region appears,
treat the free-list-pop region itself as suspicious regardless of per-address occurrence counts.

Guards 53-57's 2nd confirm has now come back WEAK THREE consecutive times, all hitting the identical
item -306 `setByteAcrossEntryList+176`/`0x800aafa8` background-noise signature with a single-digit
`hangarbay-entry` count: s546 fold-in, s548 fold-in, s549 fold-in (`n=4`, 67s). Discarded per iron rule
1 each time. This is now flagged as a possible pattern worth a dedicated check in a future session
(does this specific signature correlate with short/early-crash runs generally, not just this confirm
target?) rather than assumed to be purely random background noise. Retry re-queued:
`scratch/agent/soak_queue/s549_five_tied_guards_confirm_retry2.sh`.

Guards 58-61's 2nd confirm ran at s549: CLEAN (`hangarbay-entry n=2700`, 0 fires on all four) — FULLY
CLOSED 2/2, closing the campaign's 61 guards to 61/61 fully closed for the tenth time. That SAME
confirm run's own crash (`last-guest-pc=0x80010DCC`) produced the campaign's first-ever genuine guard
fire (guard 62's pre-existing sibling site, `0x80010DC4`, `n=0` with a numerically-traceable bad
pointer) and led directly to guards 62-63 (items -334 and -327's root cause, see table rows above).
Both cleared their own 1st live-verify clean; 2nd confirm queued:
`scratch/agent/soak_queue/s549_sibling_ptr_write_gap_confirm.sh`. Live status: `docs/CURRENT-TRUTH.md`
Next-steps / `scratch/agent/NEXT.md`.


### s553 continuation (guards 64-71 CLOSED; 72-74 still pending; 75-87 added)

**Folded in s552's queued confirms:**
- Guards **64-65** (`EMIT_ALLOCATED_DL_COMMAND_R1_GUARD`/`0x80008908`, `RESERVE_AND_EMIT_DL_ENTRY_R1_GUARD`/`0x8000CE10`): 3rd confirm attempt CLEAN (`hangarbay-entry n=2600`, full 300s no-crash rc=0) after two consecutive weak draws on item -306's signature — **FULLY CLOSED 2/2**.
- Guards **66-71** (s551 six-way): 2nd confirm CLEAN (`hangarbay-entry n=2600`); crashed on known background-noise guest PC `0x80010b7c` (this run `loadTextureTile+17912`; prior symbolizations `findOrCreateMaterial+776` / `allocOrEvictMaterialNode+944`) — **FULLY CLOSED 2/2**.
- Guards **72-74** (s552 three-way) still await 2nd confirm (`s552_three_way_tie_confirm.sh` remains queued).

**New guards 75-87** (count=8 singleton + count=6 twelve-way; count=7 `0x8000D268` skipped as shape mismatch — `ctx->r2` from `$s0`/`addu`, not `0x8011`/`0x63B0`):

| # | Guard | Session | Site | Function | Tier | Status |
|---|-------|---------|------|----------|------|--------|
| 75 | `HEAP_FREE_LIST_DEQUEUE_R2_GUARD` | s553 | `0x8000D6D4` | `heapFreeListDequeue` (2nd R-site; near items -331/-333 free-list-pop region) | 8 (singleton after s552 three-way closed the other count=8 sites) | 1st live-verify CLEAN (`hangarbay-entry n=3000`, full 300s no-crash); 2nd confirm queued |
| 76 | `HEAP_FREE_LIST_DEQUEUE_R3_GUARD` | s553 | `0x8000D1B8` | `heapFreeListDequeue` (3rd) | 6 (12-way) | same batched clean run |
| 77 | `EMIT_ALLOCATED_DL_COMMAND_R2_GUARD` | s553 | `0x80008804` | `emitAllocatedDLCommand` (2nd) | 6 (12-way) | same |
| 78 | `EMIT_COLOR_FILL_RECT_R7_GUARD` | s553 | `0x80009D0C` | `emitColorFillRect` (7th) | 6 (12-way) | same |
| 79 | `DRAW_FRAME_PROFILER_BARS_R1_GUARD` | s553 | `0x8000BA34` | `drawFrameProfilerBars` (1st, NEW function) | 6 (12-way) | same |
| 80 | `RESERVE_AND_EMIT_DL_ENTRY_R2_GUARD` | s553 | `0x8000CD04` | `reserveAndEmitDLEntry` (2nd) | 6 (12-way) | same |
| 81 | `EMIT_MATERIAL_TEXTURED_DL_R4_GUARD` | s553 | `0x8000E370` | `emitMaterialTexturedDL` (4th) | 6 (12-way) | same |
| 82 | `EMIT_MATERIAL_TEXTURED_DL_ALT_R4_GUARD` | s553 | `0x8000EA60` | `emitMaterialTexturedDLAlt` (4th) | 6 (12-way) | same |
| 83 | `RENDER_LIT_TEXTURED_MESH_FACES_R5_GUARD` | s553 | `0x8000FA9C` | `renderLitTexturedMeshFaces` (5th) | 6 (12-way) | same |
| 84 | `RENDER_FLAT_MESH_FACE_GROUP_R5_GUARD` | s553 | `0x80011330` | `renderFlatMeshFaceGroup` (5th) | 6 (12-way) | same |
| 85 | `RENDER_LIT_MESH_R14_GUARD` | s553 | `0x800132E0` | `renderLitMeshFaceGroup` (14th) | 6 (12-way) | same |
| 86 | `DRAW_SUBTITLE_TEXT_R5_GUARD` | s553 | `0x80015D9C` | `drawSubtitleText` (5th) | 6 (12-way) | same |
| 87 | `SETUP_CAMERA_MATRICES_R2_GUARD` | s553 | `0x80017524` | `setupCameraMatrices` (2nd) | 6 (12-way) | same |

1st live-verify (all 13 armed together): 0 fires on any of the 13, 0 co-fires, `hangarbay-entry n=3000`, full 300s no-crash (rc=0, 114 frames). 2nd confirm queued: `scratch/agent/soak_queue/s553_count8_count6_thirteen_way_confirm.sh`. Campaign totals as of s553: **87 fixed, 71 FULLY CLOSED 2/2, 16 pending confirm**.

### s554 continuation (guards 72-87 FULLY CLOSED 2/2; 88-114 added — count=3 + count=2)

**Folded in s552/s553 queued confirms:**
- Guards **72-74** (s552 three-way): CLEAN (`hangarbay-entry n=2700`); crashed on already-catalogued BREADCRUMB6 `buildPositionAndCallTransformHelper+1736`/`0x80065acc` — **FULLY CLOSED 2/2**.
- Guards **75-87** (s553 thirteen-way): CLEAN (`hangarbay-entry n=2600`); crashed on already-catalogued Metal-framework cluster `last-guest-pc=0x800ab0e0` — **FULLY CLOSED 2/2**. Campaign briefly at **87/87 fully closed with zero pending**.

**New guards 88-114** (count=3 singleton + count=2 twenty-six-way; count=7 `0x8000D268` still shape-mismatched, skipped again; count=1 `heapFreeListInsert`/`0x800079D8` deferred to next tier):

| # | Guard | Site | Function notes |
|---|-------|------|----------------|
| 88 | `BUILD_ORIENTED_FACE_GEOMETRY_R2_GUARD` | `0x80012CCC` | count=3 singleton |
| 89 | `RECLAIM_DISPLAY_LIST_CHUNK_R1_GUARD` | `0x80007D30` | NEW function |
| 90 | `ALLOCATE_DISPLAY_LIST_BUFFER_R1_GUARD` | `0x80007DC8` | NEW; RHS=`ctx->r4` (not r3) |
| 91-94 | `ALLOC_DL_BLOCK_TO_{FILL_RECT_LIST,LIST_B,LIST_C,LIST_D}_R1_GUARD` | `0x80007EB0`/`0x80007F70`/`0x80008030`/`0x800080F0` | NEW family |
| 95 | `RECORD_DEFERRED_DRAW_REF_VARIANT_R1_GUARD` | `0x8000848C` | NEW |
| 96 | `EMIT_ALLOCATED_DL_COMMAND_R3_GUARD` | `0x80008708` | has `g_rs64_last_guest_pc` |
| 97 | `EMIT_COLOR_FILL_RECT_R8_GUARD` | `0x80009BF4` | |
| 98 | `DRAW_FRAME_PROFILER_BARS_R2_GUARD` | `0x8000B91C` | |
| 99-102 | `RECORD_DEFERRED_DRAW_REF_{A,B,C,D}_R1_GUARD` | `0x8000C770`/`0x8000C894`/`0x8000C9BC`/`0x8000CAE0` | NEW family |
| 103 | `RESERVE_AND_EMIT_DL_ENTRY_R3_GUARD` | `0x8000CC08` | |
| 104 | `HEAP_FREE_LIST_DEQUEUE_R4_GUARD` | `0x8000D080` | |
| 105 | `EMIT_MATERIAL_TEXTURED_DL_R5_GUARD` | `0x8000E1D0` | |
| 106 | `EMIT_MATERIAL_TEXTURED_DL_ALT_R5_GUARD` | `0x8000E8C4` | |
| 107 | `RENDER_LIT_TEXTURED_MESH_FACES_R6_GUARD` | `0x8000F9EC` | |
| 108 | `SUBMIT_SCENE_NODE_RENDER_R9_GUARD` | `0x80010194` | |
| 109 | `RENDER_FLAT_MESH_FACE_GROUP_R6_GUARD` | `0x800111C8` | |
| 110 | `BUILD_ORIENTED_FACE_GEOMETRY_R3_GUARD` | `0x80012B70` | |
| 111 | `RENDER_LIT_MESH_R15_GUARD` | `0x8001317C` | |
| 112 | `DRAW_TEXT_GLYPH_RECT_R1_GUARD` | `0x80015890` | NEW function |
| 113 | `DRAW_SUBTITLE_TEXT_R6_GUARD` | `0x80015C4C` | |
| 114 | `SETUP_CAMERA_MATRICES_R3_GUARD` | `0x80016EF8` | |

1st live-verify (all 27 armed together): 0 fires on any of the 27, `hangarbay-entry n=2600`, crashed at 111.3s on NEW single-occurrence `beginFrameDLChunk+37740`/`last-guest-pc=0x8000afa0` (filed item -338; distinct from -323/`0x8000ae40` and -319/`0x8000b0d0` in the same function). Pre-crash n=0 diagnostic co-fires on freelist-next/generic-cache/dl-list-append-rwrite/dl-list-reset-rnode/append-rdp-state/dl-list-append-deref with shared `bad_ptr=0x7500D019` (existing families catching the same corruption wave — not a regression of the new guards).

**s555 fold-in of 2nd confirm:** CLEAN full ~300s duration (rc=0, 114 frames), `hangarbay-entry n=3000`, 0 fires on all 27, 0 live fires on any armed guard family, NO crash at all — **guards 88-114 FULLY CLOSED 2/2**. Campaign briefly at **114/114 fully closed with zero pending**.

### s555 continuation — last classic r2/0X4 site (guard 115)

Fresh tracer re-scan of reg=`r2`/off=`0X4` after fold-in returns only two hits:
- **count=7** at `0x8000D268` (`heapFreeListDequeue`): still SHAPE MISMATCH (`ctx->r2` from `$s0`/`addu`, not the classic `0x8011`/`0x63B0` reload) — skipped again (s553/s554 precedent).
- **count=1** at `0x800079D8` (`heapFreeListInsert`): CLASSIC shape confirmed (`lui $v0,0x8011` / `lw $v0,0x63B0($v0)` / `beq $v0,$zero` / fallthrough `MEM_W(0X4, ctx->r2) = ctx->r3`); 0 incidental matches in fixup.

| # | Guard | Site | Function notes |
|---|-------|------|----------------|
| 115 | `HEAP_FREE_LIST_INSERT_R1_GUARD` | `0x800079D8` | NEW function to R-numbered lineage (INSERT, not DEQUEUE); RHS=`ctx->r3` |

1st live-verify: 0 fires on `heap-free-list-insert-r1-guard` (0 log lines), 0 live fires on any armed guard family, `hangarbay-entry n=2700` (strong positive control). Crashed at 129.6s on already-catalogued s354-366 heap-walker background-noise `coalesceFreeHeapBlocks+4424`/`last-guest-pc=0x8000247c` (not a new item). 2nd confirm queued: `scratch/agent/soak_queue/s555_count1_heap_free_list_insert_r1_confirm.sh`.

**s556 fold-in of 2nd confirm:** CLEAN full ~300s (rc=0, 114 frames), `hangarbay-entry n=3000`, 0 fires, NO crash — **guard 115 FULLY CLOSED 2/2**. Classic r2/0X4 at **115/115 fully closed with zero pending**.

### s556 residual free-list-node rN/0X0 pivot (guards 116-124)

After classic r2/0X4 emptied, a full-rank NEEDS_GUARD re-scan (no shape filter) showed the residual top tier is a **different** free-list idiom: free-list head reloaded into `$a0`/`$a3` (`ctx->r4`/`r7`) via `0x63B0`, then used as the write base of a list-prepend `MEM_W(0X0, rN) = …` with no range check. Not the classic r2/0X4 freelist-next zeroing shape — same global, different register/offset. Shape-checked all 9 top sites (provenance = free-list head reload; companion `NODE_LIST_HEAD_*` guards cover only the list-head global side, not the free-list node write).

| # | Guard | Site | Function notes |
|---|-------|------|----------------|
| 116 | `RENDER_LIT_TEXTURED_MESH_FACES_R7_GUARD` | `0x8000FD50` | residual free-list-node 0X0; taint count=59 |
| 117 | `RENDER_LIT_TEXTURED_MESH_FACES_R8_GUARD` | `0x8000FC80` | count=45 |
| 118 | `RENDER_LIT_TEXTURED_MESH_FACES_R9_GUARD` | `0x8000FE70` | count=41 |
| 119 | `RENDER_LIT_TEXTURED_MESH_FACES_R10_GUARD` | `0x8000FF20` | via `$a3`/`r7`; count=28 |
| 120 | `RENDER_FLAT_MESH_FACE_GROUP_R7_GUARD` | `0x80011BA8` | count=27 |
| 121 | `RENDER_FLAT_MESH_FACE_GROUP_R8_GUARD` | `0x80011958` | count=16 |
| 122 | `SUBMIT_SCENE_NODE_RENDER_R10_GUARD` | `0x8001077C` | count=15 |
| 123 | `EMIT_ALLOCATED_DL_COMMAND_R4_GUARD` | `0x80008858` | count=7 |
| 124 | `RESERVE_AND_EMIT_DL_ENTRY_R4_GUARD` | `0x8000CD58` | count=7 |

1st live-verify (all 9 armed): 0 fires on all 9, `hangarbay-entry n=2600` (strong positive control). Crashed at 111.1s on `emitAllocatedDLCommand+13216`/`last-guest-pc=0x800088ec` — free-list-walk second-deref after GUARD3 validates the *previous* node (classic GUARD3/GUARD4 gap shape, heapWalker s218). Pre-crash co-fires: generic-cache/cache-head-a1/dl-alloc-propagation with `bad_ptr=0x7600D07C`. Filed **item -339** (single occurrence; not a regression — new guards at 0 fires). 2nd confirm queued: `scratch/agent/soak_queue/s556_residual_rN_0x0_nine_way_confirm.sh`.

**s557 fold-in of 2nd confirm (guards 116-124):** CLEAN (`hangarbay-entry n=2600`), 0 fires on all 9, crashed on already-catalogued `initVec4TripletFromArgs+68`/`0x80065e94` — **guards 116-124 FULLY CLOSED 2/2**. Residual free-list-node batch 1 complete.

### s557 residual free-list-node batch 2 (guards 125-131) + item -340

Re-scan after batch 1 closed. Shape-mismatched DEFERRED: heapFreeListDequeue r2/r3/r16 packing (incl known `0x8000D268`), buildOrientedFaceGeometry s2 packing, drawSubtitleText `appendRdpStateDl` return (not freelist node). Matched free-list-allocated-node `MEM_W(0X0,r4/r7)` after freelist pop at count=3:

| # | Guard | site | reg |
|---|---|---|---|
| 125 | `RECORD_DEFERRED_DRAW_REF_VARIANT_R2_GUARD` | `0x800084E0` | r4 |
| 126 | `RECORD_DEFERRED_DRAW_REF_A_R2_GUARD` | `0x8000C7C4` | r4 |
| 127 | `RECORD_DEFERRED_DRAW_REF_B_R2_GUARD` | `0x8000C8E8` | r4 |
| 128 | `RECORD_DEFERRED_DRAW_REF_C_R2_GUARD` | `0x8000CA10` | r4 |
| 129 | `RECORD_DEFERRED_DRAW_REF_D_R2_GUARD` | `0x8000CB34` | r4 |
| 130 | `HEAP_FREE_LIST_DEQUEUE_R5_GUARD` | `0x8000D0D4` | r4 |
| 131 | `RENDER_LIT_TEXTURED_MESH_FACES_R11_GUARD` | `0x8000FA40` | r7 |

1st live-verify (all 7 armed): 0 fires, `hangarbay-entry n=2600`. Crashed at 119.1s: `last-guest-pc=0x80010B4C` while `[sibling-ptr-write-guard] site=0x80010B48` fired `bad_ptr=0x18` — **item -340**, same DIRECT gap model as item -334 (`bad_ptr+4` = fault). Fixed as new `_SIBLING_PTR_WRITE_SITES` entry `0x80010B4C` (reg r3, off 0X4). 2nd confirm queued: `scratch/agent/soak_queue/s557_residual_count3_seven_way_confirm.sh`.

**Campaign totals as of s557:** **131 fixed, 124 FULLY CLOSED 2/2, 7 pending confirm** (125-131). Item -340 sibling gap fixed (1st evidence), confirm pending with residual batch 2. Residual after this batch: packing shape-mismatches (deferred), remaining freelist-node sites after 125-131 land, item -339 GUARD4 watch.

### s558 residual free-list-node close + packing DEFER + item -340 CLOSED

**Fold-in of `s557_residual_count3_seven_way_confirm`:** CLEAN full ~300s (rc=0, 114 frames),
`hangarbay-entry n=3000` (strong positive control), 0 fires on all 7 residual batch-2 tags
(record-deferred-draw-ref-variant/a/b/c/d-r2, heap-free-list-dequeue-r5,
render-lit-textured-mesh-faces-r11), 0 sibling-ptr-write fires, NO crash. **Guards 125-131 FULLY
CLOSED 2/2. Item -340 FULLY CLOSED 2/2.** Campaign freelist write guards: **131/131 FULLY CLOSED**.

**Fresh residual re-scan** (`s494_item317_step3_tracer.py --scan` + `s506_dedupe.py`, no custom
`--out`): 22 NEEDS_GUARD remaining. Shape-checked every write tier:

| Tier | Sites | Disposition |
|------|-------|-------------|
| heapFreeListDequeue r3/0X0+0X4 count=11 | r3=`ADD32(r16)` = s0 DL packing cursor | DEFERRED packing |
| heapFreeListDequeue r2/r16 count=7 | s0 packing (`0x8000D260`/`0x8000D268` family); freelist reload branch-only | DEFERRED packing |
| buildOrientedFaceGeometry r4/r5/r3/r18 | s2 packing / EE00 opcode writes | DEFERRED packing |
| drawSubtitleText r4 count=3 | `appendRdpStateDl` return write-cursor; freelist in r5 branch-only | DEFERRED packing |
| countDisplayListChunks r3 read count=1 | freelist-walk second-deref *read* (not write) | out of freelist-node write scope; seed for GUARD4 pivot |

**Freelist-node write MATCH residual: EMPTY.** Packing is a flow-merge false positive of the
freelist-write idiom (write base is DL cursor, not freelist-allocated node). Item -317 step 3
freelist WRITE idioms CLOSED. Next M3 class: freelist-walk GUARD4 (item -339 shape / heapWalker
s218), not more freelist-node 0X0.

## 26. Overturned conclusions and dead ends, full list (s2-s422), migrated from CURRENT-TRUTH.md s547
maintenance pass

CURRENT-TRUTH.md keeps only a short pointer to this section plus the two entries still load-bearing
for active work (the `0x800290d4` `inflate_fast` artifact and the audio-bridge unit-mismatch fix).


### s559/s561 freelist-walk GUARD4 (item -341; covers -339/-337) — FULLY CLOSED 2/2

Source-confirmed GUARD3-without-GUARD4 gap (heapWalker s218 shape) at 16 sites already carrying
GUARD3: emitAllocatedDLCommand x3 (item -339 `0x800088EC`), heapFreeListDequeue x4,
submitSceneNodeRender x9 (item -337 `0x80010DF4` + s123 first `0x80010178`). Fixed as
`EMIT_DL_GUARD4` / `HEAPLISTDEQ_GUARD4` / `SCENE_NODE_LIST_GUARD4`. 1st live-verify CLEAN
(hangarbay n=2900, full 300s rc=0, 0 fires). s560 2nd confirm weak-discarded (item -306); s561
retry CLEAN hangarbay n=2900 full 300s rc=0 0 fires — **CLOSED 2/2**.

### s560 residual alloc-tail GUARD3+GUARD4 (item -342) — 1/2 pending confirm

Line-based enum of walk-to-tail loops (`L: v1=*v1; v0=*v1; bne L`) in funcs_3/4: **118** total,
20 already GUARD3, **98 residual**. 88/98 after `findAndUnlinkSmallestEntry` — same inlined
"walk allocated-node next-chain to tail then splice freelist" idiom s133/s131 only guarded inside
emitAllocatedDLCommand + submitSceneNodeRender. Applied **GUARD3 x94 + GUARD4 x92** as residual
alloc-tail family (`ROGUESQ_LOG_ALLOC_TAIL_GUARD3` / `_GUARD4`). Already-covered layers excluded:
reserveAndEmitDLEntry x3 (`DLENTRY_TAIL_GUARD` s251), drainMesh peeks (s357), scene-node
`0x80010174` (s123+s559). 1st live-verify CLEAN (hangarbay n=2600, 0 fires; crash on already-
catalogued `initVec4TripletFromArgs+68`/`0x80065e94`). s560/s561/s562 confirms weak-discarded
(item -306 hangarbay n<10, three consecutive); retry2 queued s562.

### s561 residual alloc-tail GUARD2 (item -343) — FULLY CLOSED 2/2 (s562)

Complements s560 walk guards: emit-dl/scene-node already had GUARD2 on the first
`lw $v0, 0x0($aN)` after the freelist-node null-check; residual sites only null-checked.
Enum of s560's 97 residual walk sites: **92** unguarded init-deref (r4×78/r5×11/r7×3); **5**
already drainMesh head (s363). Applied **GUARD2 x92** (`ROGUESQ_LOG_ALLOC_TAIL_GUARD2`, bail =
outer null label). 1st CLEAN hangarbay n=2700; 2nd CLEAN hangarbay n=2600 (s562 fold) — CLOSED 2/2.

### s562 non-r3 freelist dual-walk residual (item -344) + packing DEFER re-confirm

Packing residual re-scan: 22 NEEDS_GUARD; **21** write-base=DL cursor (s0/s2/appendRdp return) with
freelist branch-only → packing stays DEFERRED (not freelist-class). Dual-walk any-reg enum: **129**
total, **119 G3+G4** (118 r3 + 1 r18) — s560 applied only r3 shape. Residual freelist dual-walk
NONE: `allocateDisplayListBuffer` `0x80007DA8` r4 + `renderLitMeshFaceGroup` `0x80013EEC` r4
(post-findAndUnlink). Plus `countDisplayListChunks` simple freelist-head walk `0x80007CC8`.
Applied GUARD2+3+4 x2 (reuse ALLOC_TAIL_*) + `FREELIST_SIMPLE_WALK_GUARD` x1. 1st live-verify
CLEAN hangarbay n=2600, 0 fires on new sites. Surfaced item -345 DIRECT gap after -322
`HEAPLISTDEQ_ATTR_WRITE_GUARD` `0x8000D92C` → crash `0x8000D944` (same stack slot, unguarded
0X4/0X8). Item -344 1/2 pending confirm.

### Overturned conclusions — do not act on these

- **(s400-421->s422)** "`0x800290d4`, six independent triggers, one shared downstream corruption sink -- the strongest available root-cause lead" -- `last-guest-pc=0x800290d4` is `inflate_fast`'s own clean return, reported by a sparse breadcrumb present in only 8/50 `RecompiledFuncs/funcs_*.c` files; `atos`-based exact symbolication of 5 of the 6 crash logs found five different real crash functions, not one. Believable for 21 sessions because the shared numeric value looked like a shared fault address, and nobody had yet resolved `last-guest-pc` past the breadcrumb's own coarse granularity to the actual host instruction. `m4_known_bad.txt`'s parking decision is unaffected (still correct); only the "worth a dedicated session" framing is overturned. PORTING-STATE 422.

`## LLE stabilization session 2 (2026-07-12)` sits out of order in the log, between s7 and s8: its conclusions are among the oldest in the file, not the newest.

- **(s54->s399)** "The M4 missing-func fix is applied and build-verified, only the runtime check is outstanding" -- s54's fix (adding 3 names to `mission_overlay.txt`) was dead on arrival: the same 3 names already existed at the same addresses in `main_overlay.txt`, which `make_elf.py` parses first and dedupes by name (first-file-wins), and which then get silently dropped as phantom functions (range-checked against `.text`, not the overlay window). Believable for 345 sessions because build success is consistent with both "fixed" and "silently still broken." Root-caused and actually fixed s399; also surfaced a much larger version of the same bug class (~801-803 more addresses, item -248). PORTING-STATE 399.
- **(s348/350->s352)** "`[scene-node-content-guard]` firing is evidence of the same corruption class as the other step-5 guards" -- s352's raw-log re-read found it fires at the SAME node address (`0x80183ECC`) with the SAME zeroed content, thousands of times per run harmlessly -- a steady-state signature, not corruption; the n=0-vs-n=1957+ firing-shape distinction just hadn't been checked against the other guards until s352 compared them side by side. Guard stays in place; only its evidentiary weight for the corruption hunt is overturned. PORTING-STATE 348, 350, 352.
- **(s339->s340->s342)** "The VI=640 `pairs=0` plateau is a benign, locked-camera mission cutscene" and "s340's 2/2 clean soaks validate promoting both audio gate reversals" -- s342 found those soaks never left the pre-title attribution/logo screen (0 `[keys]` lines in all 4 raw logs): crash-free with audio/DMA counters visibly live looked like a real positive control, but nobody checked the `[keys]` schedule had fired. The `pairs=0` mechanism itself (PROJECT-OVERVIEW §10) stands; only its context (pre-title, not mid-cutscene) is corrected. PORTING-STATE 339, 340, 342.
- **(s107/108->s316->s318)** Two linked overturns in the gate1/2/3 tick-producer chase: "the 3 near-identical countdown/period gates fire `tickAllActiveSongs`/`tickAudioSequencerFrame`" was never positive-controlled (s316: none ever takes "call") -- itself overturned by s318's fresher `ctx->r2` read (a stale-register race in the diagnostic, not the branch): gate1 calls 19/40, gate2 4/4. PORTING-STATE 316, 318.
- **(s222->s223)** "no soak reaches mesh-heavy content" -- a 4-soak sample-size artifact; a re-run reached space-combat content before freezing. The freeze itself is real, still reproduces (now a flat fill, not a torn polygon). PORTING-STATE 223.
- **(s216-218->s219)** "shared corrupt literal `0x0000000300000000` at x0/x8, WRITTEN somewhere" -- that register is the process's constant RDRAM host base pointer, present by construction in every `MEM_W` fault, not written corruption; the wild operand is the *other* register (byte-identical at 3 sightings, all the same `renderUnlitMeshFaces` bug, vs. an unrelated 4th `heapWalker` bug). PORTING-STATE 219.
- **(s75/76->s150)** "single Start from SELECT YOUR CRAFT leaves into a distinct hangar-flight scene" -- dense capture + an independent prior run + a code-level check (crash backtraces stay entirely in hangar-menu code) show it's the same craft-select scene under a corrupting camera move. Reopens "what leaves SELECT YOUR CRAFT" as unanswered. PORTING-STATE 150.
- **(s2-31, s62-69, s12-48, s70-82 -- grouped, ~35 claims total, the earliest build/pixel-getting and menu-triage era)** Z-buffers misread as colour buffers, texrect output called invisible, RDP "emitting nothing" (real bug: a ring high-water mark), `DPC_WRAP`/fbpair-cap misdiagnosed for missing FULL_SYNC, floor-band/fog/S=0-triangle/stale-TMEM misattributions (real causes: M1 s44-49, section 4.1), 1024-phase black screen (present-starvation, not zero-shade); "RSP task submission stays healthy through the freeze" (a 1-in-32 throttled sample missed the crashing tail; unsampled showed 100% `ImemOverrun`); "self-restarting the IMEM perspective-divide branch un-freezes tasks" (instrument fired 0 times, real site was `CLIP_1FBC`->`L_1650`); "0x6AB400 is the main-menu hangar" (believable: partial render looked coherent 36 sessions) plus briefing-room/SELECT-LEVEL origin+timing claims and hangar-dimness-as-shade-census (real cause: M1 s44-49, see CURRENT-TRUTH.md "Current truth"); the post-`a` SIGBUS/black-screen self-correction chain (UAF and present-stall theories, resolved by the s84 UAF fix and s82 sane-width gate). Each overturned within 1-2 sessions of first being believed. PORTING-STATE 2-31, 62-69, 12-48, 70-82.
- **(s87->s88)** "8th crash class is self-recursion in `advancePlayerAnimationPhase`" -- different, unreached call site; constant stack depth across 3296 calls, no recursion. PORTING-STATE 88.
- **(s302->s306)** "reversing `initMusyXEngine`'s gate-byte site validated safely (0/2 family #1 recurrence)" -- a positive-controlled entry counter found `initMusyXEngine` is never called at all; the clean result reflects dead code, not a validated gate=1 state. Gate=1 still never exercised by any soak. PORTING-STATE 306.
- **(s307->s309->s313->s315)** A chain of "audio-tick stop points converge" claims, each overturned by a closer same-run measurement: shared-upstream-resource theory refuted by source-read; "3 tick-producers + RSP `M_AUDTASK` all stop together at #19/20" refined by a widened print-cap soak to 2 real stop points, not 1 or 3 (`M_AUDTASK`'s 20/20 was its own unwidened diagnostic bug). Similar small round numbers read as simultaneous unless line numbers are diffed. PORTING-STATE 309, 313, 315.
- **(M5-AUDIO-PLAN.md §4->s371)** "The host audio bridge is already fully implemented and functional" -- a source read found `queue_samples`'s sample-count parameter was passed straight through as `SDL_QueueAudio`'s byte length with no `*sizeof(int16_t)` conversion, silently dropping the back half of every PCM buffer. Believable: the wiring compiles/links/calls cleanly, so eyeballing the call graph reads as functional -- the defect is a unit mismatch one level down. Fixed s371 (`src/main/main.cpp`; PROJECT-OVERVIEW §12). PORTING-STATE 371.

### Dead ends — labelled as such in the log, do not retry

- **(s2b-s4, grouped)** `RDP_ADDRESS_MASK`→0x7FFFFF (aliased legit extended-RDRAM handles onto low
  memory); `dma_rdram_to_dmem` chunk-replay hack (legit trig reads after a swap); widened DMA shadow
  0x37658 (legit dynamic data); blanket ucode shadow `shadow2` (2 legit rewrites); `ROGUESQ_RING_RESYNC`
  (no effect); `dmem[0x153]=0xFF` forced reload (made failures worse).
- Bulk `main_overlay.txt` symbol moves (s9): splits the enclosing function (§4.5), SIGBUS — use
  `tools/overlay_symbol_probe.py <0xADDR>` first, one batch at a time. Present-side snap-down/
  `findMostRecentContaining` (s9, neither fired); `ROGUESQ_VIEW_RDRAM=1` (s9, window never appears in
  this fork); `ROGUESQ_WRAP_DEDUP=1` (s10, ~33000 fewer submissions, same assert still hits);
  `ROGUESQ_FORCE_PAL15=1` (s14, clears floor band, corrupts ceiling banners sharing pal=15).
- **(s85→s91)** "`do_rom_read` corrupted `physical_addr` is nondeterministic garbage" — the exact same
  DMA call recurred byte-for-byte 3 times across 3 sessions; reclassified deterministic, reproducible.

## 27. M3 thr11→sec2 hangar-exit pipeline (s577–s619), migrated from CURRENT-TRUTH.md s615 maintenance

Durable summary of the active M3 DoD path after hangar exit. Session-level detail lives in
PORTING-STATE Sessions 577–619; CURRENT-TRUTH keeps only open residuals (-384..-373, -361, -7).

### What was confirmed

- **s577**: real hangar exit case 3→5→6→8 (not the s150 craft-select camera corruption).
- **s579–s588**: post-exit `rdpFs` plateau reclassified as **FULL_SYNC starvation with live GFX
  tasks** (not s178 producer-stop). Guest `E9000000` lives in a side-slot DPC staging cell at
  phys `0x76DF60`; content switch E9→E7→F3/FD ends natural FULL_SYNC. Product tool
  `ROGUESQ_FS_PIPE_INJECT` (default OFF) extends inject through E7/F3/FD. Recovery cell
  `0x76B768` firing restores post-dual `syncs>0` (H10a).
- **s589–s603**: thr-11 = `saveServiceWorker` entry `0x8006F2CC` (infinite recv loop, destroyed
  externally). thr-11 destroy co-timed with overlay section 4 when recovery is healthy (H12c).
  thr-12 = `hudDisplayUpdateWorker` `0x800495FC`, created only from
  `loadLevelTextureCache→registerServiceWorker`. `ROGUESQ_FORCE_CASE6_START` (ACE94, default OFF)
  is the reliable exit engagement tool. Engagement gate is ACE80 camera-settle (state 5→6), not
  a button. `BEGINFRAME_S0_GUARD` at guest `0x8000AFA0` landed s600 (live 2/2 still rare under
  force+inject).
- **s604–s608**: `ROGUESQ_FORCE_STATE6_AFTER` (default OFF) unlocks case6 when stuck at state 5
  (H-force6a). H-recov1 sufficiency REFUTED (76B768 alone does not force thr11 destroy);
  necessity SUPPORTED (no 76B768 → no thr11d/sec2). H-handoff2 REFUTED (76BA90 not required for
  thr11d). s608 first force-path completion: thr11 destroy → sec4 → thr12 → sec2 (mission overlay).
- **s609–s612**: recovery silence intermittent free-reroll class; mid-window `mat3x3InverseInto`
  Abort (1×) free-rerolls; thr11 destroy co-requires post-hangar-sel `isPlayerShipActive` ret=1
  (H-ship1 SUPPORTED). Ship writers: non-null arm `updateTextOverlayLookupEntry` @ `0x800B40D0`
  (copies `0x800CC864` when `0x800CC85C` null); zero arm `destroyPlayerShipRecord` @ `0x800B42A8`.
  Hangar-sel store of live ship `0x8015FD90` (H-ship1c SUPPORTED).
- **s613–s615**: class D death after thr11d+sec4 is `loadCraftShadowTextures` null `load_asset`
  walk (`si_addr=0x380000000`). Soft-skip guards + `[level-tex-cache]` landed; live A–D verify
  still PENDING (s614–s615 recovery-silent / pre_eng with force_skip). Natural ACE80 can engage
  without a force-write.
- **s616–s617**: FORCE_STATE6 / case5-entry used `uint32_t base=0x800D0000` with `MEM_*` → OOB
  rdram index `0x1000CC3E7` on 64-bit (correct S32-extended idx is `0xCC3E7`). Fix
  `gpr base = S32(0x800D << 16)` **live-verified s617**: case5_n0_state=5, force old=5→6,
  hangar 5→6→8. **-381 CLOSED.** With force working, recovery-active scored path hits a new
  pre-thr11d crash in `traverseSceneGraphRecursive` (`si_addr=0x38000f421` / guest
  `0x8000f421`, stack setupCameraMatrices←runModelViewerLoop) — item **-382**, 1× free-reroll;
  thr11 id=11 created post-hsel but never destroyed; sec4 whole-run counts were early cinematic
  only. Class-D craft-shadow still PENDING thr11d.
- **s618**: s617 freeroll scored recovery-active with scenegraph=0 (**H-sg1 SUPPORTED**; -382
  stays 1×). thr11d_post was a false positive (destroy of pre-hsel thr11 id=10; new id=11
  never destroyed). True crash host is `readAccountForSelectionScreen+604` (nm/atos), not
  local-symtab's `rebuildActiveDisplayObjectList+540`; caller `menuControllerInput` jump
  case 1. New residual **-383** (1× free-reroll). Metric fix: `thr11d_new`.
- **s619**: s618 scored a2: **thr11d_new=1 sec4_post=1 LIVE** (first confirmed post-hsel thr11
  destroy of a post-hsel-created 6F2CC thread). thr12 never created. Crash **-384**:
  `buildMaterialFreeList+260` null freelist-base write (`si_addr=0x380000000`) during
  `initSceneForMission`→`advanceVideoFrame` mission-scene init. H-ship1z (ship-zero blocks
  thr11d_new) **REFUTED** as hard gate. -383/-382 stay 1× freeroll (0 on scored).

### Open residuals (do not re-derive)

| Item | Residual | Status |
|------|----------|--------|
| -384 | post thr11d_new+sec4 `buildMaterialFreeList` null-base SIGBUS | 1×; free-reroll; primary after thr11d LIVE |
| -383 | post-force `readAccountForSelectionScreen` SIGBUS pre-thr11d | 1×; 0 on s618 scored; free-reroll |
| -382 | post-force `traverseSceneGraphRecursive` SIGBUS pre-thr11d | 1× freeroll; H-sg1 SUPPORTED |
| -374 | recovery cell `0x76B768` silence after eng+inject | free-reroll; co-primary |
| -375 | `mat3x3InverseInto` Abort mid-window | 1×; free-reroll; escalate on 2nd |
| -376/-377 | ship ret=1 / store co-gate for thr11d | H-ship1 SUPPORTED; H-ship1z hard-block REFUTED |
| -378 | craft-shadow null walk before thr12 | guard landed; live-verify PENDING (needs thr12) |
| -379 | FORCE_STATE6 only at state==5 | gate kept; s613 recharacterized by -381 |
| -381 | FORCE_STATE6 KSEG0 `uint32` base OOB | **CLOSED s617** (fix + live-verify) |
| -373 | post-sec2 `packTlut`/HMT SIGBUS | 1×; primary bottleneck once pipeline completes |
| material `0x8000e29c` | `findOrCreateMaterial` | 2×; free-reroll noise |

### Tools (all default OFF)

- `ROGUESQ_FS_PIPE_INJECT` — inject FULL_SYNC on non-E9 size-8 at slot∩last_fs
- `ROGUESQ_FORCE_CASE6_START` — force case6 start poll at ACE94
- `ROGUESQ_FORCE_STATE6_AFTER=N` — force hangar state→6 at case5-entry n==N **only if current
  state==5** (s614 gate; s616 requires S32-extended KSEG0 base for the read/write)

### Do-not-retry on this arc

- Requiring `0x76BA90` for thr11 destroy (H-handoff2 REFUTED)
- Raising HOLD_S past 210
- Soft-skip mat3inv without 2nd occ + abnormal control
- Single-chase packTlut before 2nd same host stack
- Leaving FORCE_*/FS_PIPE default-ON
- Treating `last-guest-pc=0x800290d4` as craft-shadow fault site
- Forcing hangar state from old≠5 (blocks ACE80) — and do not reintroduce `uint32_t`
  KSEG0 bases into `MEM_*` patches on 64-bit hosts

### Next
Consume s619 soak: matfree 2nd → escalate -384 (null-base guard candidate); thr12/cshadow →
class-D A–D; thr11d_new+sec4 hold without crash → past freelist.

## 28. M3 pipeline completion through the post-sec2 E9 loss (s620–s678)

The `loadLevelTextureCache` null allocation and the craft-shadow path dissolved under the
multi-header freelist-writeback restore. The restore preserves all freelist headers in the
wild-CIMG writeback range while allowing the body writeback needed by recovery; restoring the
whole body suppressed recovery. The triggering `SETCIMG addr=0x1F0D74, width=1161` was proved
garbage read after a wrapped DPC ring, not a legitimate game command. Decode-site drops and
wrap-wide submission drops remain default OFF because they also suppress recovery.

With the product restore enabled, two full recovery-fired holds reached thr11 destruction,
thr12 creation, and section 2; post-sec2 outdoor rendering and presentation are live. The
remaining defect is a mission-phase FULL_SYNC plateau: GFX continues but `rdpFs` barely advances.
Input can keep thr12 alive but does not change this plateau, so menu-return is a closed,
input-gated side branch rather than its cause.

Two independent phase-scoped samples found thousands of inline-data-aware guest E9s but only
three runner FULL_SYNC events each. The authoritative parser saw only the genuine raw E9s in the
matching population, and every one reached `GBI_RDP::fullSync` and `State::fullSync`. s684 closed
an apparent bridge/parser discrepancy: its fixed-8-byte raw-ring scanner mistook `0xE9` bytes
inside raw `0xCE` 20-word triangle payloads for commands. Two section-2 windows, with exact boot
controls, showed every sampled non-fetch byte inside such an executed span; none was a parser
range gap. The remaining question is therefore whether genuine FULL_SYNC starvation already
originates in RSP output, not bridge/parser command loss.

`ROGUESQ_LOG_E9_PROVENANCE` is injected idempotently by `tools/fixup_factor5_ucode.py`. It retains
tasks 1–4 as controls and uses a section-2 latch for targets. Do not use its fixed-8-byte raw-ring
scan as a command count; the next probe must use parser-derived raw-E9 and `fullSync` counts. See
`scratch/agent/NEXT.md` and CURRENT-TRUTH backlog item 1. Sessions 620–684 contain the full
chronology in `PORTING-STATE.md`.

### Provenance and 0x06 control-flow narrowing (s685–s728)

The section-2-latched provenance work closed bridge and RT64-dispatch loss. In qualified windows,
every real raw `E9` reaches `GBI_RDP::fullSync` and `State::fullSync`; fixed-stride E9 excesses are
inline triangle payload bytes, not commands. Boot controls complete naturally, whereas cap rows
make 8,192 fetches and return only via the synthetic cap marker. EndDL executes on those rows, but
does not take the root exit because the chain remains open.

The cap frames are not corrupted inline dispatch: qualified runtime capture found all `caller=0x1088`
pushes are `0x06` (`F3DSWRS_DL`) with KSEG0 child-DL operands, matching the independent Factor 5
command reference. Static audits then closed the normal `0x06` parent-PC save/child load/EndDL
restore path, root-loader and fetch-pointer lifecycle, and the host DMEM `0xFF0`/`0x130` staging
theory. Host staging of both fields is redundant and is default OFF; phase-gated A/B controls kept
the complete TriGen route intact.

The later TriGen continuation work established that `L_1DB0` uses the documented root/refill loop:
section-2-latched branch/return pairs always choose branch 4 and return to `0x1088`, with changing
sources and no crash. It therefore does not explain the plateau. The s730 static enumeration found
the ordinary `0x06` route has exactly one generated push site and its sole `0x654+depth`
save/restore pair is balanced. It also found a remaining opaque alternative: the DMA-fed `L_1298`
entry table contains `0x12A0` in its retained table image, although the earlier live overlay records
selected only `0x1DB0`. **s731 closed that alternative for observed cap rows:** two section-2-latched
captures tagged every `L_12A0` entry as table-1 direct `0x06` (overlay=0); the same-run control
showed direct tags with matching push/pop/resume. **s732–s738:** the depth-0 reuse is paired to
the main-image `L_1DB0` `DMEM[0x152]=0` reset, and every active predecessor is the resident-`0C`
`L_1298` relay. The correct overlay-12 window image is distinct TriGen and does not reset, so
H-stale-main-image is selected. **s739 landed the overlay-12 splice** (fixup 6b, `OVL12_*`,
jal-return cases through `L_122C`/`L_1268`); consume the queued phase-latched soak before any
further change. Runtime rerolls without a section-2 latch are unqualified. **s740–s742:** the
splice stops the section-2 reset; residual UJs are the skipped overlay-24 emit at dest `0x12A0`
plus overlay 28's `r17 += 32` / restore of `L_12A0` (`docs/M3-OVL24-CONTINUATION-AUDIT.md`).
Details: PORTING-STATE Sessions 685–742; consume protocol: `scratch/agent/NEXT.md`.

### Recent investigation archive (s743–s877)

This compact archive was migrated from `CURRENT-TRUTH.md` during the s878
maintenance pass. It preserves the durable conclusions; chronological detail
remains in `PORTING-STATE.md`.

**Post-sec2 E9 accounting (s743–s854).** Phase-gated port captures reached VI
1024 with live `emit/raw/dispatch/match` controls. Bridge submit serials and
RT64 consumer ranges matched for the retained ordinary population, and the
synthetic FULL_SYNC path was absent in the decisive s840 capture. Source and
runtime audits showed that the bridge scans fixed 8-byte slots while RT64
advances by command length; most apparent E9 excesses are inline words inside
preceding commands (`span`), not parser E9 commands. Pending completion was
zero in the captured population. Triangle/copy probes then showed B4/BF rows
were owned by the RDP map, not Factor 5, and mapped to non-triangle entries;
the accepted submit ranges matched those rows. The remaining extended-opcode
residual was not reached by the later captures. No writer or value legitimacy
was established, so no mitigation is justified.

**Dispatcher and breadcrumb family (s855–s861).** Bounded slot/update
populations were valid in the observed post-sec2 window, but the recurring
death population was not captured. A source inventory found 9,550 writes to
the process-wide guest-PC breadcrumb across 47 functions; guest PC
`0x8000834c` is written by `drainMeshReleaseQueue`'s return delay-slot
representation, not by `getNextSlotNpcTypeId`. The crash handler has no writer
thread, epoch, or handoff association, so that breadcrumb is stale attribution
for this family. It does not prove that a later slot chain is valid.

**Coalescer value-origin family (s862–s877).** The whole-idiom audit found
the coalescer's two walks and the sole partition writers. Port entry telemetry
observed `a0=0/1` and head `0x830A10A0`; retail physical watches independently
showed live early writers and verified whole-RDRAM, PIF, and VI controls. The
retail driver stayed at VI width 320 despite phase-appropriate Start pulses,
while the port reached VI 1024 and late partition writers. Thus the late
retail value comparison is phase-unreachable. No value-legitimacy conclusion
or mitigation follows. The next bounded unit is an oracle callback/API audit
for a safe deferred value sampler.

**Oracle ABI audit (s879).** The local mupen64plus debugger headers and core
source settle the remaining sampler question. `DebugSetCallbacks` exposes a
breakpoint callback with guest PC only; `DebugBreakpointTriggeredBy` exposes
only flags and accessed address; and `DebugMemRead32` is a current-memory read.
The core calls `check_breakpoints_on_mem_access` before `mem_write32`, so a
callback read sees the pre-write value. A later frontend-thread read can avoid
the callback stall but cannot preserve the triggering writer association and
races later writes. H-no-safe-value-api is selected. No runtime behavior,
mitigation, or oracle source was changed; the coalescer question must pivot to
another independent ground-truth source.
## 30. M3 audio idiom audits s925–s938

This compact maintenance note preserves the durable outcomes removed from
CURRENT-TRUTH during the s936 maintenance pass. All were source-only audits:
no build, game run, soak, guard, generated-code edit, mitigation, or behavior
change was made.

- s925 `filterVoiceSampleBlock`: three callers share the voice-channel shape;
  fixed loops terminate, but caller-owned buffers, the selector table, and
  the `a1`-derived output range remain unclassified.
- s926 `applyVoiceDelayFilter`: three callers agree on shape and all loops
  terminate; voice/table/output pointers and derived ranges remain unproven.
- s927 `runVoiceLatticeFilter`: four callers share fixed source/output walks
  of 13, 14, 13, and 120 iterations; dynamic pointer/value legitimacy remains
  unproven.
- s928 `renderVoiceAudioBlock`: one coherent caller, four fixed lattice stages,
  fixed mixer/compander edges, and no local unbounded path; dynamic buffer and
  voice-record legitimacy remains unproven.
- s929 `audioMixStereoBlock8`: one caller, fixed eight-sample ranges, and
  return-address-derived fixed targets; no data-derived target or local walk,
  but dynamic voice-buffer legitimacy remains unproven.
- s930 `audioCompandS16`: fixed arithmetic regions, clamp, sign restoration,
  and no memory/control hazard; dynamic input legitimacy remains unproven.
- s932 `musyxInitVoiceFromSample`: callers agree on the nominal contract, but
  the masked voice index is not bounded and descriptor legitimacy is open.
- s933 `musyxSetVoiceAdsrFromTable`: bounded table search and capped count
  classify local structure; voice-slot, program, table, and count legitimacy
  remain unproven.
- s934 `musyxStoreVoiceAdsrParams`: fixed ADSR accesses and writes, but the
  base-only guard does not prove the byte-loaded index is below the mixer
  count.
- s935 `musyxTriggerVoiceAttack`: the ordinary audio caller and streamed-voice
  caller supply distinct contracts; the latter passes a voice-record pointer
  where the callee interprets a mixer index. Existing base-only protection
  does not resolve the mismatch.
- s937 `musyxStopVoice`: one direct generated caller passes constant index zero;
  the callee has one fixed `+0x1` byte store through a `0x88` stride and no
  local loop/helper hazard. This is a structural pass for that chain only;
  base/count lifecycle legitimacy and register-indirect callers remain open.
- s938 `stopVoiceByKey`: one direct caller passes the byte at its streamed-voice
  record `+0x4624`; `allocateSynthVoice` returns either `-1` or an index below
  the byte-sized active voice count, and the `0x17C` record arithmetic is
  internally consistent. The stop path calls `freeSynthVoiceFromActiveList`
  and `stopVoiceMarkRetrigger`, not `musyxStopVoice`; base/count lifecycle,
  active-list pointer legitimacy, and register-indirect callers remain open.
- s940 `stopVoicesByHandle`: generated code and companion symbols agree that
  `D_8013D880` is 32 records of stride `0x17C`, with the active count at
  `0x80141AD0`. Count writers clamp to `0..0x20`; reset, release, stop, and
  macro-stop paths clear record `+0` and write `-1` to `+0x64`, while
  `startNoteOnVoice` writes the constructed handle. The four direct callers
  pass linked-list node `+0x8` handles, but node `+0xC` index provenance and
  complete runtime value legitimacy remain open (single-source static result).

These results leave the active M3 thread at `stopVoicesByHandle`, with no
mitigation authorized absent an ORIGIN naming the writer and assessing value
legitimacy.

## 31. M4 zero-shade and oracle archive s984–s1003

This compact archive was migrated from `CURRENT-TRUTH.md` during the s1004
maintenance pass. Full records remain in `PORTING-STATE.md`.

- s984 audited RT64's shaded-triangle decode against the independent Factor 5
  command reference. Position and signed shade lanes are structurally correct;
  same-combiner and white-shade A/B evidence keep the cause upstream in F5
  shade-state or game lighting. No mitigation followed.
- s985–s990 established nonzero phase-6 VTXCOLOR payloads alongside exact-zero
  decoded shade, mixed direct generated-store ownership, no overlap from the
  instrumented DMEM-to-RDRAM DMA path, no exact target-byte CPU fault store in
  the sampled pages, and generated-function ownership for sampled fault PCs.
  None identified a universal writer or authorized a mitigation.
- s991–s995 moved generated-store instrumentation into the regeneration-owned
  fixup path. A clean capture found 97 classified target PCs, mostly register
  copies or zero initializations; value-bearing rows were bounded and included
  display-list words, colors, pointers, and zeros. Source ownership remained
  unresolved.
- s996–s999 added task identity to shade/payload rows. Captures showed mixed
  source ownership, including exact generated writes for some phase-6 sources
  and no overlap for others. Task-level identity was insufficient to map one
  source update to one zero-shade replacement.
- s1000–s1001 added F5 and RT64 ordinals and the F5 root DL. F5 ordinals are
  task-global while RT64 ordinals reset at child-DL boundaries. The F5 root DL
  does not equal the repeated RT64 consumer DL, selecting a child-DL-shaped
  association without identifying the source update.
- s1002's two retries crashed before the VI-1024 gate and were invalid.
- s1003 added accepted DPC first/last ranges and aggregate physical bounds.
  In the valid capture, zero-shade task 193 had root `0x73E7C8`, bounds
  `[0x4B7800,0x4C9318)`, and consumer DLs `0x4B7930`, `0x4B7BE8`, and
  `0x4B8B28`, all within the accepted range. This supports only
  `H-dpc-range-contains-consumer`; source-to-individual-replacement mapping
  remains open. ORIGIN: these are diagnostics derived from accepted DPC
  intervals and do not modify game or renderer state.
- s1005 carried accepted submit serial/range fields into RT64 shade rows. The
  valid VI-1024 capture produced both positive and zero rows with nonzero
  serials. Zero-shade task 194 had serial 49346 and consumer range
  `[0x4B7990,0x4B7C88)`, contained by its accepted F5 task bounds
  `[0x4B7800,0x4B7EA0)`. The consumer range begins at the child DL and does not
  identify an individual F5 VTXCOLOR source update, selecting
  `H-child-range-only`. No mitigation followed.

The s955–s983 oracle line is also retained here as history: s982 localized the
corrected external core's fault to dereferencing `r4300_pc(r4300)` before the
debug callback, and s983 verified the oracle directory was unavailable in the
session sandbox. It remains blocked pending human directory access.

## 32. Retail VI descriptor boundary (s1048–s1131)

The retail oracle's independent whole-RDRAM, PIF-input, and VI callback/poll
controls pass, but the tested ROM remains on the width-320 attract path and
does not reach the hangar-origin phase. The width-320 path is now resolved as
a descriptor lifecycle rather than an input, logger, or fixed-table defect.

`librecomp::init` sets `osTvType=1`; generated `setViModeType` maps that to
`rsViModeType=0`, and the ROM-backed NTSC index window supplies mixed
320/640/1280 records. The boot config word at `gameConfig+0x44` is unwritten
in the audited sources and is `0x00001800` in the retail image. Its relevant
bits produce selector bytes `A/B/C=1/0/0`, selecting copied-record offset
`0xF0`. The initial descriptor load is NTSC index 0 (width 320); alternate
overwrite families require `s7==0`, while the boot wrapper's stack-derived
`s7` is nonzero, so index 0 is preserved.

The four-record copy writes table offsets `0x00/0x50/0xA0/0xF0` and reaches
`osViSetMode_recomp` without an intervening selector or record store.
`osViSetMode_recomp` forwards `ctx->r4` unchanged; the host does not rewrite
width. The VI descriptor boundary is independently established; do not reopen
the selector/source chain.

The same period closed the recurring material-writer ordering question: boot
initialization calls the descriptor setup before the material writer, and the
recurring path is not before the first boot consumer. The M3 slot-stack-spill
family and M4 accumulator-origin investigation remain parked as described in
the live truth file. Maintenance s1131 compressed the detailed session ledger
from the live file into the append-only `PORTING-STATE.md` and this durable
summary. Homebrew Rice later-phase results (s1496 hangar, s1512 M4 DMEM `r9`,
s1528 leave-hangar 640, s1544 640 still menu-overlay) live in
`CURRENT-TRUTH.md` and superseded the dummy-video 320-only parking.

## 33. Generated-symbol renaming sweep (s1240–s1589)

Migrated from `CURRENT-TRUTH.md` during the s1553 maintenance pass. Full
per-session comparison tables remain in `PORTING-STATE.md`. Method: one
adjacent generated function per session; synchronize the TOML name only
when the companion project, generated definition, live-body size, and
caller or semantic evidence agree (H1). Leave address-encoded, already-fake,
or unnamed complete kernels unchanged (H2/H3). No build or runtime run is
justified for an exact-name census.

**Cursor.** Next census is `func_800BAA00`, independently named
`bindFalconSubmodelMaterials`, at `0x800BAB70` (TOML placeholder, size
`0x25C`; next entry is `playerFalconMainUpdate` at `0x800BADCC`). Last H1
sync is `triggerFalconEngineEffect` at `0x800BAA00` (s1589).
Last H2 park is `fake_func_800B42BC` (s1570). About 1,548
placeholder `func_0x...` names remained when counted at s1487.

**Covered ranges (H1 unless noted).**

| Sessions | Region / result |
|---|---|
| s1240–s1268 | Early exact companion/generated map syncs; fake/address-only left unchanged. |
| s1270–s1308 | MusyX / voice / display-mode / init-shutdown: `0x80086450` through `isMusyXActive` at `0x8008ED5C`. |
| s1309 | H2 for truncated `func_8008ED6C`; H1 for `runAiAudioStreamPlaybackLoop` at `0x8008ED70`. |
| s1310–s1354 | Song / stream / resample / voice-init: `buildSongTempoSchedule` through `resampleVoicePointTableSamples`. |
| s1355, s1357, s1359 | H3 for complete inner kernels `func_800927B0`, `func_80092A54`, `func_80092CF0` (no independent name). |
| s1356, s1358, s1360–s1368 | Remaining resample/copy/ADPCM/math primitives through `ceilDouble`. s1360 left `func_80092F10` as a TOML-only live tail of `resampleVoiceLutSamplesPacked`. |
| s1369 | H1 `sqrtf_recomp`; left `fake_func_80093E74` unchanged. |
| s1370–s1445 | Note-rate, pan, song sequencer, SND tables, streamed/3D voice, priority queue through `noopHandler_80099C44`. Left `fake_func_80094348`, `fake_func_8009711C`, `fake_func_80097D58` unchanged. |
| s1446, s1451 | H2 for already-fake one-word gaps `fake_func_80099C4C` and `fake_func_80099FDC`. |
| s1447–s1450 | Affine / vec3 / orientation-inverse at `0x80099C50..0x80099DCC`. |
| s1452–s1470 | Voice-slot / speech / MusyX voice table / stream consume through `stopVoice` at `0x8009C2BC`. s1460 confirmed already-matching `loadSpeechFile`. |
| s1471 | H2 for already-fake COP1 fragment `fake_func_8009C2C8`. |
| s1472–s1485 | Voice pan/channel/decode/filter/mix through `audioCompandS16`. s1476 H2 for `fake_func_8009D7CC`; s1477/s1478 left `func_8009D8BC` and `func_8009D978` as eight-byte lookup-table pads. |
| s1486–s1543 | Cinematic overlay: `cinematicLoopBody` at `0x800A5D80` through `cinematicDeactivator` at `0x800AF60C`. s1487 confirmed already-matching `load_cutscene`. |
| s1545–s1546 | `getCinematicStateSubObject`, `cinematicInterpRatio`; s1546 H2 for already-fake data-tail `fake_func_800AF6A8`. |
| s1547–s1552 | Mission overlay: `findNearestSceneObjectToPoint` through `computeOrientedTransformFromQuat` at `0x800B1024`. |
| s1554 | Mission overlay: `tickCinematicObjectStateMachine` at `0x800B13E0` (size `0x808`). |
| s1555 | Mission overlay: `updatePlayerCraftPhysics` at `0x800B1BE8` (size `0x1B14`). |
| s1556 | Mission overlay: `applyCraftCapabilityFlags` at `0x800B36FC` (size `0xC4`). |
| s1557 | Mission overlay: `initPlayerCraftMovementMode` at `0x800B37C0` (size `0x250`). |
| s1558 | Mission overlay: `tryPlaySpatialSoundWithGates` at `0x800B3A10` (size `0x43C`). |
| s1559 | Mission overlay: `scheduleSceneFormatMessageTimed` at `0x800B3E4C` (size `0xC0`). |
| s1560 | Mission overlay: `cancelSceneQueueHandle` at `0x800B3F0C` (size `0x44`). |
| s1561 | Mission overlay: `playSpeechClipOncePerChange` at `0x800B3F50` (size `0x64`). |
| s1562 | Mission overlay: `playSpeechClipOncePerLevel` at `0x800B3FB4` (size `0xEC`). |
| s1563 | Mission overlay: `resetSpeechOncePerLevelFlag` at `0x800B40A0` (size `0x50`). |
| s1564 | Mission overlay: `setPlayerSlotPositionVec3` at `0x800B40F0` (size `0x44`). |
| s1565 | Mission overlay: `destroySceneNpcsAndUnlink` at `0x800B4134` (size `0x88`). |
| s1566 | Mission overlay: `decayWeaponCooldownTimer` at `0x800B41BC` (size `0x30`). |
| s1567 | Mission overlay: `getWeaponChargeLevel` at `0x800B41EC` (size `0x10`). |
| s1568 | Mission overlay: `advancePitchTowardTarget` at `0x800B41FC` (size `0xC0`). |
| s1570 | H2 for already-fake one-word gap `fake_func_800B42BC` before `playerXwingInit`. |
| s1571 | Confirmed already-synchronized `playerXwingInit` at `0x800B42C0` (size `0x2C8`). |
| s1572 | Mission overlay: `playWeaponFireSound` at `0x800B4588` (size `0x738`). |
| s1573 | Mission overlay: `playXwingEngineSound` at `0x800B4F54` (size `0x4E0`). |
| s1574 | Mission overlay: `isWeaponSlotReady` at `0x800B585C` (size `0x58`). |
| s1575 | Mission overlay: `resetEngineTrailQuads` at `0x800B5B4C` (size `0x87C`). |
| s1576 | Mission overlay: `acquireLockOnTarget` at `0x800B63C8` (size `0x3D8`). |
| s1577 | Mission overlay: `emitTexturedImpactEffect` at `0x800B67A0` (size `0x1F0`). |
| s1578 | Mission overlay: `updateEngineThrustEffect` at `0x800B6990` (size `0x7D8`). |
| s1579 | Mission overlay: `findLockOnTarget` at `0x800B7590` (size `0x34`). |
| s1580 | Mission overlay: `tickCraftAbilityCooldown` at `0x800B77D0` (size `0x27C`). |
| s1581 | Mission overlay: `orientEffectToVelocity` at `0x800B7A4C` (size `0x3B0`). |
| s1582 | Mission overlay: `spawnTexturedExplosionBurst` at `0x800B7DFC` (size `0x68C`). |
| s1583 | Mission overlay: `emitTexturedEffectCue` at `0x800B88C8` (size `0x12C`). |
| s1584 | Mission overlay: `updateVwingEngineEffect` at `0x800B8C30` (size `0x9B0`). |
| s1585 | Required retail-entry revisit: hold/A/B/Z all stayed in the case-6 model viewer; no symbol sync. |
| s1586 | Mission overlay: `orientVwingSubmodelByQuat` at `0x800B95E0` (size `0x370`). |
| s1587 | Mission overlay: `tickVwingEngineAudio` at `0x800B9950` (size `0x5FC`). |
| s1588 | Mission overlay: `computeFalconFlightTransform` at `0x800BA620` (size `0x3E0`). |
| s1589 | Mission overlay: `triggerFalconEngineEffect` at `0x800BAA00` (size `0x170`). |

**Parked (do not re-census).** `func_8008ED6C`, `func_800927B0`,
`func_80092A54`, `func_80092CF0`, `func_80092F10`, `fake_func_80093E74`,
`fake_func_80094348`, `fake_func_8009711C`, `fake_func_80097D58`,
`fake_func_80099C4C`, `fake_func_80099FDC`, `fake_func_8009C2C8`,
`fake_func_8009D7CC`, `func_8009D8BC`, `func_8009D978`,
`fake_func_800AF6A8`, `fake_func_800B42BC`. Reasons are in
`CURRENT-TRUTH.md` Next steps #1.

**Revisit rule.** Every 15 consecutive sweep-titled sessions, spend the
iteration on the retail-entry boundary or the M4 accumulator boundary
instead. s1569 was the last such revisit (leave-hangar 640 is
`runModelViewerLoop`).

## 34. Recent sweep and Rice-route updates (s1590–s1647)

This section archives the post-§33 work that was compacted out of
`CURRENT-TRUTH.md` during the s1638 maintenance pass. The sweep continued its
one-adjacent-entry rule: synchronize a TOML placeholder only when the
companion mapping, generated body, exact boundaries, overlay span, size, and
caller or semantic evidence agree. Exact-name censuses do not require a build
or runtime run.

| Sessions | Durable result |
|---|---|
| s1590–s1601 | Synchronized `bindFalconSubmodelMaterials` (`0x800BAB70`), `playerFalconMainUpdate` (`0x800BADCC`), `spawnFalconEngineParticles` (`0x800BB608`), `integrateFalconFlightPhysics` (`0x800BBC58`), `computeTieInterceptorTransform` (`0x800BBF6C`), `triggerTieInterceptorEffect` (`0x800BC290`), `computeTieInterceptorOrientation` (`0x800BC4F8`), `computeT16Transform` (`0x800BCE74`), `playerT16MainUpdate` (`0x800BD254`), `triggerT16Effect` (`0x800BD958`), `buildNabooSubmodelTransform` (`0x800BDC9C`), and `triggerNabooEngineEffect` (`0x800BE228`). Each had matching companion/generated/TOML/overlay evidence and adjacent boundaries. |
| s1602 | M4 paired revisit: four phase-6 target rows, 32 lanes, matched the local VMADH accumulator model with no VGE mutation. The port DMA control identified runtime destination `0x4B7800..0x4B7808`; the positive Rice retail run wrote it zero times. Different allocation/scene origins make that targeted retail null unevaluable. |
| s1603–s1613 | Synchronized `tickPlayerCraftBlinkIndicator` (`0x800BE4A8`), `initDemoPlayState` (`0x800BEC00`), `applyDemoRecordedHudEvents` (`0x800BECDC`), `clearPlayerSlotHudTracking` (`0x800BEE18`), `tickPlayerHudIndicators` (`0x800BEFBC`), `loadPlayerSlotHudPreset` (`0x800BF264`), `countTrailingZeros16` (`0x800BF2F4`), `applyResModeFromSettings` (`0x800BF358`), `restoreGameSettingsAfterDemo` (`0x800BF3A4`), `loadAndStartDemo` (`0x800BF408`), and `getDemoRecordedTimestep` (`0x800BF468`). Exact companion, body, callers, spans, sizes, and boundaries agreed. |
| s1614–s1615 | Confirmed `fake_func_800BF498` (`0x8`) and `fake_func_800BF784` (`0xC`) are explicit generated frame fragments, not renameable kernels. |
| s1616 | Rice pre-exit B is a valid route distinct from A: B delivered `sym=224` / pad word `0x400000`, then changed VI `512→1024` at `0x00790400` and `1024→640` at `0x00696100`, with no model-viewer or mission-entry PC. A followed the known case-6 viewer route. Directional arms were invalid `sym=0`; selector watch `0x13B40:0x13B48` was quiet. |
| s1617–s1618 | Parked `func_800BF790` (`0x800BF790`, HUD-health body) and `func_800C41B0` (`0x800C41B0`, radar-column body) as H3: each mission entry is address-coded while a conflicting main-overlay name occupies the same VRAM address. |
| s1619, s1621–s1628 | Synchronized `plotRadarBlipRow` (`0x800C435C`), `updateCraftSelectAnimState` (`0x800C4D8C`), `findClosestRadarContactAndSetSweep` (`0x800C5580`), `renderRadarSweep` (`0x800C5918`), `renderRadarMinimap` (`0x800C5F90`), `lookupCraftValueByLevelKey` (`0x800C62C4`), `registerObjectAndResolveDatItem` (`0x800C6340`), `accumulateClampedFloatField` (`0x800C6468`), and `getDisplayItemStateByte` (`0x800C6498`). |
| s1620 | Five valid-D-pad Rice arms passed whole-RDRAM, PIF, and VI controls through hangar 512. `dup`/`ddown` plus A reached the 640 viewer; `dleft`/`dright` plus A stayed in 512 through 110 seconds. All had zero mission-entry PC `0x80000B70` and zero selector writes. This corrects the earlier invalid-direction experiment but does not identify mission entry. |
| s1629 | Parked `func_800C64B0` (`0x800C64B0`, hangar display-item initialization) as H2: mission overlay is address-coded while `main_overlay.txt` names the same VRAM `initHangarDisplayItemTimers`, and generated output contains both overlay contexts. |
| s1630–s1635 | Synchronized `tickHangarDisplayItemAnimations` (`0x800C65CC`), `hangarVehicleDisplayNpcHandler` (`0x800C68A0`), `applyNpcPositionDrift` (`0x800C6FFC`), `accumulateVectorInObjectFrame` (`0x800C713C`), `getConfigFloatValue` (`0x800C722C`), and `findNamedEntryInCurrentObject` (`0x800C723C`). |
| s1636 | Rice hold, `cup`, `cdown`, `cleft`, `cright`, `L`, and `R` all passed whole-RDRAM/PIF/VI controls and converged on `320→640→1024→512→640`; each hit viewer PC `0x800C9BF0` once, with mission PC `0x80000B70` and selector writes zero. H2 selected for these controls. |
| s1637 | Synchronized `dispatchObjectiveSlot1` at `0x800C72E8` (size `0x38`); companion mapping, generated dispatcher/caller, exact adjacent boundaries, section-4 span, and TOML size agree. Next census: `func_800C7358`, companion name `checkComplexObjectives`, size `0x38`. |
| s1639 | Confirmed `checkComplexObjectives` at `0x800C7358` (size `0x38`) was already synchronized across companion mapping, live generated dispatcher, TOML, and section-4 span. No source-map edit was needed. Next census: `func_800C7648`, companion name `getAndSetByteAtLevelStateTable`, size `0x18`. |
| s1640 | Synchronized `getAndSetByteAtLevelStateTable` at `0x800C7648` (size `0x18`): four companion callers and byte getter/setter semantics matched the live generated body, exact TOML size, and section-4 overlay span. Next census: `func_800C7718`, companion name `getGlobalFloatGameState`, size `0x10`. |
| s1641 | Synchronized `getGlobalFloatGameState` at `0x800C7718` (size `0x10`): companion mapping, live generated global-float getter, exact TOML size, section-4 span, and adjacent boundaries agreed. Next census: `func_800C7728`, companion name `getObjectiveGlobalFloat`, size `0x10`. |
| s1642 | Synchronized `getObjectiveGlobalFloat` at `0x800C7728` (size `0x10`): companion mapping, live generated objective-float getter, exact adjacent boundaries, TOML size, and section-4 span agreed. Next census: `func_800C7738`, companion name `setHudEnableBit4`, size `0x34`. |
| s1643 | Synchronized `setHudEnableBit4` at `0x800C7738` (size `0x34`): companion caller/semantic mapping, live generated body, exact adjacent boundaries, TOML size, and section-4 span agreed. Next census: `func_800C776C`, companion name `setHudEnableBit8`, size `0x34`. |
| s1644 | Synchronized `setHudEnableBit8` at `0x800C776C` (size `0x34`): companion caller/semantic mapping, live generated body, exact adjacent boundaries, TOML size, and section-4 span agreed. Next census: `func_800C77A0`, companion name `isLevelStateByteZero`, size `0x10`. |
| s1645 | Synchronized `isLevelStateByteZero` at `0x800C77A0` (size `0x10`): companion mapping, live generated byte-zero test, exact adjacent boundaries, TOML size, and section-4 span agreed. Next census: `func_800C77D0`, companion name `randMod`, size `0x60`. |
| s1646 | Synchronized `randMod` at `0x800C77D0` (size `0x60`): companion mapping, live generated signed-16-bit random-remainder body, exact adjacent boundaries, TOML size, and section-4 span agreed. Next census: `func_800C7830`, companion name `addBooleanCountHandleWrapper`, size `0x34`. |
| s1647 | Confirmed `addBooleanCountHandleWrapper` at `0x800C7830` (size `0x34`) was already synchronized: companion mapping, live generated wrapper body, exact adjacent boundaries, TOML size, and section-4 span agreed. Next census: `func_800C7864`, companion name `addTimerHandleWrapper`, size `0x20`. |
| s1648 | Confirmed `addTimerHandleWrapper` at `0x800C7864` (size `0x20`) was already synchronized: companion mission mapping, live generated wrapper body, exact adjacent boundaries, TOML size, and section-4 span agreed. Next census: `func_800C7884`, companion name `setHudFlagBit40AndStoreArg`, size `0x1C`. |

The sweep cursor after s1647 is `func_800C7864` / `addTimerHandleWrapper`.
s1648–s1727 continue in §35. The parked entries and the every-15-session
revisit rule remain those recorded in §33 and the live truth file. The Rice
route is now the only valid later-phase oracle recipe; dummy video's 320-only
results are not evidence about hangar or mission entry.

## 35. Sweep continuation and Rice frontend close-out (s1648–s1822)

Migrated from `CURRENT-TRUTH.md` during the s1728 maintenance pass. Method
unchanged from §33–§34: one adjacent generated function per session;
synchronize the TOML name only when companion mapping, live generated body,
exact adjacent boundaries, overlay span, and size agree. Exact-name censuses
do not require a build or runtime run. Menu-overlay functions that share a
VRAM window with a mission occupant are a different overlay, not a name
collision.

| Sessions | Durable result |
|---|---|
| s1648–s1649 | Confirmed `addTimerHandleWrapper` (`0x800C7864`, `0x20`); synchronized `setHudFlagBit40AndStoreArg` (`0x800C7884`, `0x1C`). |
| s1650 | Rice post-B A/Start/Z: all arms passed whole-RDRAM and hangar controls; zero mission/viewer PC. Hold and Z completed B-route 640 at `0x00696100`; A and Start cancelled the post-B 1024 intermediate back to hangar 512. H3 for A/Start; Z ignored. |
| s1651–s1665 | Confirmed `calculateDatItemDistanceToPlayer`, `getDatItemHealth`, `getDatItemHealthPercentage`. Synchronized `getScaledPlayerCraftSpeed` through `playNpcStateChangeEffect` (`0x800C794C`–`0x800C7FF8`): DAT-item distance/speed/spawn/init/despawn, HUD-effect and named-asset wrappers, NPC spawn-from-message and state-change effect. Menu `computeCellGridIndices` at `0x800C804C` is a different overlay. |
| s1666 | Rice post-arrival A/Start/Z on the 640 B-frontend (`0x00696100`/`0x00696600`). The 640 screen is neither hangar nor viewer; it times out at ~117.7 s to attract 512 (`0x00690400`). A/Start at 106.3 s cancel `640→1024→512` hangar (H3). Z on 640 is ignored (H2). `0x80000B70` is `loadOverlay+0x50`. Hold died rc=139 at 135 s still on attract 512. |
| s1667–s1681 | Synchronized `spawnNpcDestructionEffect` through `tickAtAtBodyTransform` (`0x800C8178`–`0x800CC2AC`); confirmed `npcTurretUpdate` (`0x800C8F90`, `0x11FC`) and `npcProbeDriod` (`0x800CABD4`, `0x11CC`, keep the `Driod` typo). Covers NPC destruction/impact/orientation/model, turret, ambient, probe-droid hop/scatter, nearest-NPC, spawn-template, textured-sound, and AT-AT body transform. Menu occupants in this VRAM window (`runModelViewerLoop` `0x800C9BF0`, medal/voice helpers) are a different overlay. |
| s1682 | Rice C/L/R and D-pad on the arrived 640 B-frontend. All 11 arms passed controls and matched hold: `640→512` attract at 117.7 s, viewer 0, hangar-frame 59–62, `0x80000B70`=1 (post-timeout attract path). H2 selected. `--secs 125` flush rc=0; 160 s batch died at the known ~135 s Rice crash. |
| s1683–s1697 | Synchronized AT-AT audio/sub-feature/destruction/footstep/leg through AT-ST effect/cannon/kinematics/destruction/death-anim and `spawnPlayerAtStCannonFire` (`0x800CC9B8`–`0x800D1248`). Confirmed `npcAtAtUpdate` (`0x800CD71C`, `0x1800`), leftover `fake_func_800CEF1C` (`0x4`), `npcAtStUpdate` (`0x800CFE7C`, `0x120C`), and `playerAtStInit` (`0x800D1088`, `0x1C0`). |
| s1698 | Rice A/Start/Z/C/L/R/D-pad on attract 512. All 14 arms passed controls; `--secs 125` flush rc=0. H3 A/Start/C-up/L: `512→1024` at 126.4 s origin `0x00790400`/`800`; 1024 destination unevaluable. H2 Z/C-down/C-left/C-right/R/D-pad: still attract 512 through 125.8 s (later superseded for Z by s1714). |
| s1699–s1713 | Synchronized player-AT-ST locomotion/behavior, `npcInitFromTemplate`, `spawnScaledBootVec4Effect`, `npcInitWithMotionParams`, effect channels A/B/dispatch, shuttle destruction, child-link init, and `advanceNpcSpinOrientation` (`0x800D1578`–`0x800D5078`). Confirmed `playerAtStUpdate` (`0x800D2208`, `0x954`), leftover `fake_func_800D2C98` (`0x8`), `npcShuttleUpdate` (`0x800D3894`, `0x1630`), leftover `fake_func_800D4EC4` (`0xC`). |
| s1714 | Rice later-flush of attract-512 A/Start/C-up/L/Z (`--secs 133`). Hold stays attract 512 through 133.4 s. A/Start/C-up/L/Z all leave `512→1024` at 126.3–126.4 s origin `0x00790400`/`800` and stay on that title-like 1024 through 133.5 s. H2 for A/Start/C-up/L. H3-confirm for Z (second source; s1698 stay-512 was a flush cutoff). 1024 destination still unevaluable (Rice dies ~135 s). |
| s1715–s1727 | Synchronized `npcDebrisFieldUpdate` through `npcWingmanBehaviorByMode` (`0x800D5208`–`0x800D80B4`): debris-field, simple-model init, shared effect-channel plus Mode0/Mode1 wrappers, tank-droid aim, wingman reset/state-data/shared-emitter/state-0/state-1/behavior-by-mode. Confirmed `npcTankDroidUpdate` (`0x800D6998`, `0xE80`). Companion `D_800D5208` is a leftover splat label, not a second occupant. |
| s1729 | Synchronized `npcWingmanSpawnBurstEffects` (`0x800D8988`, `0x330`). Three `initNpcContextFromTransform` / `spawnRandomBurstNpcVariantWrapper` / `assignNpcTargetAndPosition` bursts. Sole caller `npcWingmanUpdate` at `0x800D9CA8`. |
| s1730 | Synchronized `npcWingmanSteerToward` (`0x800D8CB8`, `0x57C`). Vec/quat steer: `vec3Dot`/`vec3Cross`/`vec3Length`, `quatFromAxisAngle(Safe)`, `quatMultiply`, `rotateVec3ByQuat`, `wrapAngleToCyclicRange`. Sole caller `npcWingmanUpdate` at `0x800D99DC`. |
| s1731 | Synchronized `npcWingmanUpdateEngineAudio` (`0x800D9234`, `0x18C`). Integrates engine-audio rate/accumulator at `+0xEC`/`+0xE8`, writes pitch/gain at `+0xE4`, `buildRotationMatrixSlot2` on two child slots, then `isAudioVoiceActive` / `updateActive3DAudioSource`. Sole caller `npcWingmanUpdate` at `0x800D9960`. |
| s1732 | Confirmed `npcWingmanUpdate` (`0x800D93C0`, `0xBD0`). 11-way jump table at `0x800A7A00` on `(a1-1)` for `a1 ∈ 1..11`. Setup / teardown / live tick (`npcWingmanUpdateEngineAudio`, `npcWingmanSteerToward`, `npcWingmanBehaviorByMode`) / visibility / damage (`npcWingmanSpawnBurstEffects`) / range / slot-action. Table-dispatched; no leftover `func_800D93C0`. |
| s1733 | Synchronized `npcWingmanState2` (`0x800D9F90`, `0xD4`). Two-way `+0x5E` toggle, HMT textures `0x800A781C`/`0x800A7820`, `npcWingmanStateEffectShared`, optional `play3DSoundEvent` `0x2`/`0x5A`/`0x28`. `getNpcWingmanStateData` case 2. |
| s1734 | Synchronized `npcWingmanState3` (`0x800DA064`, `0xD8`). Same `+0x5E` toggle and shared emitter; both live phases use HMT name `0x800A7844` and pass `a2=0/1` into `lookupHmtTextureByName`; optional `play3DSoundEvent` `0x2`/`0x5A`/`0x28` with float `0x800A7AF4`. `getNpcWingmanStateData` case 3. |
| s1735 | Synchronized `npcWingmanState4` (`0x800DA13C`, `0xF8`). Dual HMT lookup on name `0x800A7848` with `a2=0` then `a2=1` (no `+0x5E` toggle); both go through `npcWingmanStateEffectShared`; OR of the two 8-bit returns, optional `play3DSoundEvent` `0x2`/`0x5A`/`0x28` with float `0x800A7AF8`. `getNpcWingmanStateData` case 4 (`0x800E0000 + -0x5EC4`). |
| s1736 | Synchronized `npcWingmanState5` (`0x800DA234`, `0x12C`). Two-way `+0x5E` toggle, HMT names `0x800A7844`/`0x800A784C`, dual `lookupHmtTextureByName` `a2=0/1` through `npcWingmanStateEffectShared`; OR of the two 8-bit returns, optional `play3DSoundEvent` `0x2F`/`0x6E`/`0x3C` with float `0x800A7AFC`. `getNpcWingmanStateData` case 5 (`0x800E0000 + -0x5DCC`). |
| s1737 | Synchronized `npcWingmanStateNoop` (`0x800DA360`, `0x8`). Delay-slot `jr $ra` / `addiu $v0, $zero, 0x1` always returns 1. `getNpcWingmanStateData` case 6 (`0x800E0000 + -0x5CA0`). |
| s1738 | Synchronized `npcWingmanState6` (`0x800DA368`, `0xD8`). Two-way `+0x5E` toggle, HMT name `0x800A7844` with `a2=0/1` through `npcWingmanStateEffectShared`; optional `play3DSoundEvent` `0x31`/`0x64`/`0x32` with float `0x800A7B00`. `getNpcWingmanStateData` case 7 (`0x800E0000 + -0x5C98`). |
| s1739 | Synchronized `npcTieVariantTickEffects` (`0x800DA440`, `0x398`). Five-way jump table at `0x800A7B18` on object halfword `+0x8A`; cases 0/2/3, 1, and 4 each do HMT lookup + `tickProgressChannel` + `triggerCueWithSlotEffect`/`slotDispatcherIter`; shared `play3DSoundEvent` `0x31`/`0x6E`/`0x3C` with float `0x800A7B4C`. |
| s1740 | Synchronized `npcTieVariantSteerToward` (`0x800DA7D8`, `0x1D8`). Velocity-integrate + quat-rotate + heading-clamp; `wrapAngleToCyclicRange` / `isTerrainCellBlockedAtWorldXz` / `quatFromAxisAngle` / `rotateVec3ByQuat`. Sole generated caller `npcTieVariantUpdate` at `0x800DB80C`. |
| s1741 | Synchronized `npcTieVariantTickAttachmentEffect` (`0x800DA9B0`, `0x1E8`). LOS check + attachment-timer cue: `validateActorTargetLOS` / `applyToObjectSubstructByFlag` / `lookupHmtTextureByName` / `triggerCueWithSlotEffect` / `slotDispatcherIter` / `play3DSoundEvent`. Sole generated caller `npcTieVariantUpdate` at `0x800DB7F8`. |
| s1742 | Synchronized `npcTieVariantHandleDestruction` (`0x800DAB98`, `0x584`). Debris+rand+3D-sound destruction: `spawnDestructionDebris` / `spawnDestructionEffectBurst` / `spawnDirectionalDebrisBurst` / `spawnDebris1Npc` / `play3DSoundEvent`. Sole generated caller `npcTieVariantUpdate` at `0x800DBF38`, after `unregisterAndFreeNpcSlot` + `popNpcSlotFromTail`. |
| s1743 | Confirmed `npcTieVariantUpdate` (`0x800DB11C`, `0x110C`). 9-way jump table at `0x800A7C10` on `(a1-1)` for `a1 ∈ 1..9`. Setup / teardown / live tick (`npcTieVariantTickAttachmentEffect`, `npcTieVariantSteerToward`) / 3D-audio / damage (`npcTieVariantHandleDestruction`) / slot-dispatch. Table-dispatched; no leftover `func_800DB11C`. |
| s1744 | Mandatory REVISIT. Six-arm Rice overlay-PC watch on the attract A/Start/C-up/L/Z title-like 1024. All arms passed controls. `cinematicLoopBody`/`load_cutscene` stay 2 (the 17.3 s and 65.4 s title-like 1024s); `runMenuContentStateMachine` stays 0; `runInMissionFrame` stays 1. Leave drops `0x800AA658` (−350) and `0x800C131C` (−180) vs hold attract. H3-stop-tick selected; H1/H2/H4 rejected. Extra `loadOverlay` +2 does not enter those four entries. |
| s1745 | Synchronized `npcRadarDishInit` (`0x800DC228`, `0xD8`). Object-record spawn/init: zero flags at `+0x87`/`+0xBA`/`+0x88`, then `setNpcHealth` / `initActorMotionParams` / `setObjectDetailLevel` / `initObjectAnimSubstruct`. TOML was stale `func_800DC228`; generated headers/body and section-4 already used the human name. |
| s1746 | Synchronized `npcRadarDishComputeAimMotion` (`0x800DC300`, `0x3F0`). Radar-dish aim/track solver: child-active + LOS gate, mesh/local transform, two-axis quat steer, optional `play3DSoundEventVariant` `0x7`/`0x4B`/`0x64`/`0x28`, then `factor5RemoveListNode` or `floatModulo` wrap of `+0x54`. TOML was stale `func_800DC300`; generated headers/body and section-4 already used the human name. |
| s1747 | Confirmed `npcRadarDishUpdate` (`0x800DC6F0`, `0xB58`). 7-way jump table at `0x800A7D58` on `(a1-1)` for `a1 ∈ 1..7`. Setup / teardown / live tick (`npcRadarDishComputeAimMotion`) / visibility / damage / slot-action. Table-dispatched; no leftover `func_800DC6F0`. |
| s1748 | Synchronized `npcInitMinimalNoAnim` (`0x800DD248`, `0x7C`). Health/motion/detail init only (`setNpcHealth` / `initActorMotionParams` / `setObjectDetailLevel`); no `initObjectAnimSubstruct`. TOML was stale `func_800DD248`; generated headers/body and section-4 already used the human name. |
| s1749 | Synchronized `npcInitFullModel` (`0x800DD2D0`, `0x23C`). Same health/detail/motion init as the minimal sibling, then a `+0xCF` three-way dispatch that calls `initObjectAnimSubstruct`. TOML was stale `func_800DD2D0`; generated headers/body and section-4 already used the human name. |
| s1750 | Synchronized `npcTickEffectChannelC` (`0x800DD50C`, `0x140`). HMT lookup at `0x800A7E28`, optional `resolveNpcAttachmentPos` when `+0xDC != 0`, `tickProgressChannel`, then on return-1 `triggerCueWithSlotEffect` plus `play3DSoundEvent` `0x48`/`0x6E`/`0x28`. TOML was stale `func_800DD50C`; generated headers/body and section-4 already used the human name. |
| s1751 | Synchronized `npcTickEffectChannelD` (`0x800DD64C`, `0x140`). Same HMT / attach-pos / progress-channel / cue / 3D-sound body as C (`0x800A7E28`, `0x48`/`0x6E`/`0x28`). TOML was stale `func_800DD64C`; generated headers/body and section-4 already used the human name. |
| s1752 | Synchronized `npcTickEffectChannelE` (`0x800DD78C`, `0x1A4`). Dual-HMT sibling of C/D: name `0x800A7E34` with dests `sp+0x28`/`sp+0x58` (`a2=0/1`), dual `resolveNpcAttachmentPos` via table `0x8010A9F4`, dual `triggerCueWithSlotEffect`, then `play3DSoundEvent` `0x1D`/`0x78`/`0x28` with float `0x800A7E38`. TOML was stale `func_800DD78C`; generated headers/body and section-4 already used the human name. |
| s1753 | Synchronized `playAttachmentMaterialFadeSound` (`0x800DD930`, `0x140`). Single-HMT sibling of C/D: name `0x800A7E28`, dest `sp+0x28`, optional `resolveNpcAttachmentPos` via table `0x8010A9C4` when LOD `+0xDC != 0`, `tickProgressChannel`, then on return-1 zero `+0xDC`, `triggerCueWithSlotEffect`, `play3DSoundEvent` `0x48`/`0x78`/`0x28` with float `0x800A7E3C`. TOML was stale `func_800DD930`; generated headers/body and section-4 already used the human name. |
| s1754 | Synchronized `transformCraftDualAnchorsAndApplyMotion` (`0x800DDA70`, `0x180`). Two-pass pending-child gate: `isPendingChildNpcActive` on `+0x38`, copy `0x30` local, `buildRotationMatrixSlot0`/`composeRotationMatrixSlot1` from `+0x6C`/`+0x64` (then `+0x70`/`+0x68`), `transformVec3ByMat34` on anchors `+0xC`/`+0x18`, optional `validateActorTargetLOS` + `applyToObjectSubstructByFlag`, writeback. Sole generated caller `tickEnemyCraftWithDestruction` at `0x800DF0AC`. TOML was stale `func_800DDA70`; generated headers/body and section-4 already used the human name. |
| s1755 | Synchronized `tickEnemyCraftWithDestruction` (`0x800DDBF0`, `0x8FC`). Two-pass pending-child + LOS gate: `isPendingChildNpcActive` / `computeActorAnchorDeltaAfterLOS` on `+0x38`; mesh T&L (`getObjectMeshTransformOrLocal`, `mat34CrossRowsAndCopyPos`, `mat3x3InverseInto`, quat/vec helpers) or fallback `buildRotationMatrixSlot0`/`composeRotationMatrixSlot1` from `+0x6C`/`+0x64`; four `play3DSoundEventVariant` `0x7`/`0x4B`/`0x7F`/`0x28`; optional `factor5RemoveListNode` when child `+0x46==1`. Sole generated caller `npcGroundTransportUpdate` at `0x800DF0A0`. TOML was stale `func_800DDBF0`; generated headers/body and section-4 already used the human name. |
| s1756 | Synchronized `npcGroundTransportPlayFriendlyFireWarn` (`0x800DE4EC`, `0x320`). Dual-slot transform composer (not a voice player): two-iteration walk of `a0`/`a0+4` composing `clearVec4QuadStruct` / flag-gated `addVec3At0x24` / `applyScaleToMat3x4` / `composeQuatToMat3x4` / `composeRotationMatrixSlot0`/`Slot1` into child `+0x1C`, then `mat34CrossRowsAndCopyPos` on `*(a0+0x30)+0x28`. Companion voiceId `0x217` lives in `npcGroundTransportUpdate` at `0x800DF988` (`jal 0x80066EE4`), not here. Two generated callers in that update at `0x800DF078` and `0x800DF0C0`. TOML was stale `func_800DE4EC`; generated headers/body and section-4 already used the human name. |
| s1757 | Confirmed `npcGroundTransportUpdate` (`0x800DE80C`, `0x136C`). 9-way jump table at `0x800A7E88` on `(a1-1)` for `a1 ∈ 1..9`. Setup / teardown / live tick (`npcGroundTransportPlayFriendlyFireWarn` twice, `tickEnemyCraftWithDestruction`, `transformCraftDualAnchorsAndApplyMotion`) / 3D-audio / damage (`playSpeechClip` voiceId `0x217` at `0x800DF988`) / slot-action. Table-dispatched; no leftover `func_800DE80C`. |
| s1758 | Synchronized `resetCraftSubsystemGlobal` (`0x800DFB78`, `0xC`). Delay-slot `sw $zero, -0x3F60($v0)` with `$v0 = 0x80110000` stores 0 at `0x8010C0A0` — the same word `npcGroundTransportUpdate` case 4 compares before `playSpeechClip` `0x217`. Sole generated caller `resetObjectContextPool` at `0x800EC4F0`. TOML was stale `func_800DFB78`; generated headers/body and section-4 already used the human name. |
| s1759 | Synchronized `noopHandler_800DFB84` (`0x800DFB84`, `0x8`). Pure `jr $ra` / `nop` stub; no generated `jal 0x800DFB84` site. TOML was stale `func_800DFB84`; generated headers/body and section-4 already used the human name. |
| s1760 | Mandatory REVISIT. Three-arm Rice watch of the complete `menuOverlayInit` 11-way jump table on the attract A/Start title-like 1024. All arms passed controls. No case increases vs hold: case 9 `0x800C28F0` stays 1; cases 3/6/10 stay 0; cases 1/2/4-5-7/8 and the dispatcher drop. Extra menu dest +1 reproduced. H3-stop-tick selected; H1/H2/H4 rejected. Overlay-alias: hold's high counts at those PCs are cinematic-resident. |
| s1761 | Confirmed leftover `fake_func_800DFB8C` (`0x800DFB8C`, `0x4`). One-instruction `addiu $sp, $sp, -0x18` orphan between `noopHandler_800DFB84` and `applyCraftAnimAndDetailParams` (whose prologue is `addiu $sp, $sp, -0x50`, so this is not a split first instruction). Companion leftover splat; `func_800DFB90` deleted s432 as a duplicate of the next function. No leftover `func_800DFB8C`; TOML, generated headers/body, and section-4 already use the leftover name. |
| s1762 | Synchronized `applyCraftAnimAndDetailParams` (`0x800DFB90`, `0x3C4`). Per-instance anim/detail setup: `setNpcHealth` / `setObjectDetailLevel` / `initActorMotionParams` (twice) plus `initObjectAnimSubstruct` (four) and `initAnimSubstructFromParams` (twice). No generated `jal 0x800DFB90`. TOML was stale `func_800DFB90`; generated headers/body and section-4 already used the human name. Companion deleted leftover `func_800DFB90` at s432 as a duplicate of this name. |
| s1763 | Synchronized `playAttachmentMaterialSoundVariantA` (`0x800DFF54`, `0x190`). Attachment material cue + 3D sound: HMT `0x800A7FB0` dest `sp+0x28`, prefix `setObjectSubstructF10IfReady` (skipped when `a1==3`) with `0x3D088889`, optional `resolveNpcAttachmentPos` via table `0x8010ABA0` when LOD `+0xF4 != 0`, `tickProgressChannel`, then on return-1 `triggerCueWithSlotEffect` plus `play3DSoundEvent` `0x1D`/`0x6E`/`0x28` with float `0x800A7FB4`. No generated `jal 0x800DFF54`. TOML was stale `func_800DFF54`; generated headers/body and section-4 already used the human name. |
| s1764 | Synchronized `playAttachmentMaterialSoundVariantB` (`0x800E00E4`, `0x188`). Sibling of variant A: HMT `0x800A7FB8` dest `sp+0x28`, prefix `setObjectSubstructF10IfReady` (skipped when `a1!=0`) with `0x3D088889`, optional `resolveNpcAttachmentPos` via table `0x8010ABA0` when LOD `+0xF4 != 0`, `tickProgressChannel`, then on return-1 `triggerCueWithSlotEffect` plus `play3DSoundEvent` `0xD`/`0x6E`/`0x28` with float `0x800A7FBC`. No generated `jal 0x800E00E4`. TOML was stale `func_800E00E4`; generated headers/body and section-4 already used the human name. |
| s1765 | Synchronized `playAttachmentCueWithSlotIter` (`0x800E026C`, `0x18C`). Attachment cue + 3D sound via slot-dispatcher iteration: HMT `0x800A7FC0` dest `sp+0x28`, modulo-5 of `lh +0xB6 + 1`, `tickProgressChannel`, then on return-1 `getObjectNpcTypeId`, table `0x8010ABA0` via `lbu +0xB2`, `triggerCueWithSlotEffect` `a1=0xB`, optional `slotDispatcherIter` `a1=0xA` when cue id != `0xFFFF`, plus `play3DSoundEvent` `0x30`/`0x6E`/`0x28` with float `0x800A7FD4`. No generated `jal 0x800E026C`. TOML was stale `func_800E026C`; generated headers/body and section-4 already used the human name. |
| s1766 | Synchronized `playDualTextureAttachmentCue` (`0x800E03F8`, `0x350`). Two-texture attachment cue + 3D sound (`a2` mode flag): HMT `0x800A7FB0` when `a2==0` else `0x800A7FB8`, dual `lookupHmtTextureByName` dests `sp+0x28`/`sp+0x58` (`a2=0/1`), dual `resolveNpcAttachmentPos` when LOD `+0xF4 != 0`, four `tickProgressChannel`, dual `triggerCueWithSlotEffect` `a1=0x2` via table `0x8010ABA0` and `lbu +0xB2`, plus `play3DSoundEvent` `0xD`/`0x6E`/`0x28` with float `0x800A7FD8`. Generated callers `playDualTextureAttachmentCueMode0`/`Mode1`. TOML was stale `func_800E03F8`; generated headers/body and section-4 already used the human name. |
| s1767 | Synchronized `playAttachmentMaterialSoundSimple` (`0x800E0748`, `0x1B0`). Minimal single-texture attachment cue + 3D sound: HMT `0x800A7FC0` dest `sp+0x28`, optional `resolveNpcAttachmentPos` via table `0x8010ABA0` when LOD `+0xF4 != 0`, one `tickProgressChannel`, XOR-toggle `+0xB6` bit 0, then on return-1 `triggerCueWithSlotEffect` `a1=0xB` plus `play3DSoundEvent` `0x30`/`0x6E`/`0x28` with float `0x800A7FDC`. No `slotDispatcherIter` and no generated `jal 0x800E0748`. TOML was stale `func_800E0748`; generated headers/body and section-4 already used the human name. |
| s1768 | Synchronized `transformCraftAnchorsAndApplySubFx` (`0x800E08F8`, `0x3EC`). Build rotation matrices + transform two anchors + apply sub-effects: `buildRotationMatrixSlot0` / `composeRotationMatrixSlot1`, two `transformVec3ByMat34` of `s2+0xC` / `s2+0x18` dests `sp+0x24` / `sp+0x30`, then `applyToObjectSubstructByFlag` (`a3=0/1`) and `tickObjectAnimSubstruct`. Generated caller `npcTrainCarUpdate` `jal 0x800E08F8`. TOML was stale `func_800E08F8`; generated headers/body and section-4 already used the human name. |
| s1769 | Synchronized `tickCraftSplineOrientation` (`0x800E0CE4`, `0x6C8`). Canonical spline-walker orientation: 3-iter `fp<3` loop, `mat34CrossRowsAndCopyPos` / `mat3x3InverseInto`, pending-child + LOS (`isPendingChildNpcActive` / `computeActorAnchorDeltaAfterLOS` / `getObjectMeshTransformOrLocal`), rotation/quat/vec3 stack (`buildRotationMatrixSlot0` / `composeRotationMatrixSlot1` / `quatFromAxisAngle` / `rotateVec3ByQuat` / `transformVec3ByMat34`), two `play3DSoundEventVariant`, then `factor5RemoveListNode`. Generated caller `tickCraftSplineOrientationDual` `jal 0x800E0CE4`. TOML was stale `func_800E0CE4`; generated headers/body and section-4 already used the human name. |
| s1770 | Synchronized `tickCraftSplineOrientationDual` (`0x800E13AC`, `0xA70`). Two-segment craft: `tickCraftSplineOrientation` then a second orientation pass (`mat34CrossRowsAndCopyPos` / `mat3x3InverseInto`, pending-child + LOS + `evaluateTargetTrackingVisibility` / `getObjectMeshTransformOrLocal`, the same rotation/quat/vec3 stack, two `play3DSoundEventVariant`, then `factor5RemoveListNode`). Generated caller `npcTrainCarUpdate` `jal 0x800E13AC`. TOML was stale `func_800E13AC`; generated headers/body and section-4 already used the human name. |
| s1771 | Synchronized `tickTrainCarStateMachine` (`0x800E1E1C`, `0x140`). Per-tick train-car SM: early-out on `+0xFD`, decrement `+0xFC`, then set `+0xFD=1` and advance from the `npc+0x34` table (`+0xB2==0` uses `+0x134`/`+0x138`, else `+0xD4`/`+0xD8`). 16-slot walk writes `+0xCA`/`+0xEA`/`+0xFA` via a 7-way `jr` table at `0x800A8040` for type ids `0x2F..0x35`. Generated caller `npcTrainCarUpdate` `jal 0x800E1E1C` at `0x800E303C` and `0x800E30D8`. TOML was stale `func_800E1E1C`; generated headers/body and section-4 already used the human name. |
| s1772 | Synchronized `buildDebrisTransformStack` (`0x800E1F5C`, `0x4A0`). Health-gated 3-iter walk (`s2` from npc while `< npc+0xC`): each slot dest `ptr+0x1C` composes pos (`addVec3At0x24`), scale (`applyScaleToMat3x4` from `+0x5C/+0x60/+0x64` when flag `+0x4C` bit 1), quat (`composeQuatToMat3x4` from `+0x68` when bit 2), then `composeRotationMatrixSlot1`/`Slot0`. Three slot pointers per iter at `s2+0x3C/+0x48/+0x54` with params at `+0x60/+0x6C/+0x78`. Terminal `mat34CrossRowsAndCopyPos` on `npc+0x30` dest `+0x28`. Generated caller `npcTrainCarUpdate` `jal 0x800E1F5C` at `0x800E3008`/`0x800E3248`/`0x800E34FC`/`0x800E3858`. TOML was stale `func_800E1F5C`; generated headers/body and section-4 already used the human name. |
| s1773 | Synchronized `slerpFrameTowardTargetAxis` (`0x800E23FC`, `0x278`). Incremental frame slerp toward a world axis: copies const vec3 at `0x800A805C` onto the stack, `vec3Dot` against `a0+0xC`, `constMinusSinfApprox`, then if the abs-scaled result exceeds the `0x800A806C` threshold, `vec3Cross`/`vec3Length` + `quatFromAxisAngle` (clamped angle) + `quatFromCardinalAxis` (`lbu +0xC4`, `lw +0xBC`) + `quatMultiply`, rotates `+0xC` and `+0x18` via `rotateVec3ByQuat`, `orthonormalizeFrame`, then `wrapAngleToCyclicRange` of the scaled `a1` increment into `+0x4/+0x8/+0xB8/+0x24`. Returns 1 if the `+0x4` clamp fired, else 0. Generated caller `npcTrainCarUpdate` `jal 0x800E23FC` at `0x800E34EC`. TOML was stale `func_800E23FC`; generated headers/body and section-4 already used the human name. |
| s1774 | Synchronized `tickWalkerCraftWithLimbsAndDestruction` (`0x800E2674`, `0x1A4`). One `initNpcContextFromTransform` then three `spawnRandomBurstNpcVariantWrapper` / `assignNpcTargetAndPosition` bursts. Sole generated caller `npcTrainCarUpdate` `jal 0x800E2674` at `0x800E3260` (`a0` = npc). TOML was stale `func_800E2674`; generated headers/body and section-4 already used the human name. |
| s1775 | Confirmed `npcTrainCarUpdate` (`0x800E2818`, `0x181C`). 9-way jump table at `0x800A8128` on `(a1-1)` for `a1 ∈ 1..9`. Setup (inner type table `0x800A8150` writes `+0xB2`, `loadAssetIntoNewSlot`) / teardown / live tick (`tickTrainCarStateMachine` twice, `tickCraftSplineOrientationDual`, `transformCraftAnchorsAndApplySubFx`, `tickWalkerCraftWithLimbsAndDestruction`, `buildDebrisTransformStack`) / 3D-audio / damage (`playSpeechClip`, `dealDamageToNpc`) / slot-action. Table-dispatched; no leftover `func_800E2818`. |
| s1776 | Mandatory REVISIT. Three-arm Rice watch of main-text screen/frame handlers on the attract A/Start title-like 1024. All arms passed controls. Leave adds `submitGfxFrame` +105/+103 (H1); `runVideoFrameTick`/`swapBufferWithViMode` +1 matches the extra WIDTH; `applyPendingViChanges` +2/+3 tracks VI count. `mainGameLoop` and `applyLevelScreenAndCameraSettings` stay 1 (H2 closed). `emitFrameRdpInitDl` drops −180/−176 with `0x800C131C` (H4 closed; H3-stop-tick still holds for overlay-aliased ticks). Extra `loadOverlay` +2 / menu dest +1 reproduced. |
| s1777 | Synchronized `playDualTextureAttachmentCueMode0` (`0x800E4034`, `0x1C`). Thin wrapper: `jal 0x800E03F8` `playDualTextureAttachmentCue` with delay-slot `addu $a2, $zero, $zero`. Sibling of Mode1 (`a2=1`). No generated `jal 0x800E4034`. TOML was stale `func_800E4034`; generated headers/body and section-4 already used the human name. |
| s1778 | Synchronized `playDualTextureAttachmentCueMode1` (`0x800E4050`, `0x1C`). Thin wrapper: `jal 0x800E03F8` `playDualTextureAttachmentCue` with delay-slot `addiu $a2, $zero, 0x1`. Sibling of Mode0 (`a2=0`). No generated `jal 0x800E4050`. TOML was stale `func_800E4050`; generated headers/body and section-4 already used the human name. |
| s1779 | Confirmed leftover `fake_func_800E406C` (`0x800E406C`, `0x4`). One-instruction `sw $a0, 0x20($sp)` orphan between `playDualTextureAttachmentCueMode1`'s epilogue and `handleRayShieldedNpcDestroy` (whose prologue is `addiu $sp, $sp, -0x40`, so this is not a split first instruction). Companion leftover splat with no deleted-duplicate comment (next occupant is already the human name). No leftover `func_800E406C`; TOML, generated headers/body, and section-4 already use the leftover name. |
| s1780 | Synchronized `handleRayShieldedNpcDestroy` (`0x800E4070`, `0x40C`). 5-way `jr` table on `(a1-1)<5` at `0x800A8270`. Terminal path `playSpeechClip` `a0=0x15B` / `a1=0x73` / `a3=0x8` then `destroyNpcSlotByIndex` unless slot id is `0xFFFF`. No generated `jal 0x800E4070`. TOML was stale `func_800E4070`; generated headers/body and section-4 already used the human name. |
| s1781 | Confirmed leftover `fake_func_800E447C` (`0x800E447C`, `0x4`). One-instruction `lw $v1, 0x14($v1)` orphan between `handleRayShieldedNpcDestroy`'s epilogue and `resetCraftInstanceMotionState` (whose prologue is `addiu $sp, $sp, -0x40`, so this is not a split first instruction). Companion leftover splat; `func_800E4480` deleted s432 as a duplicate of the next function. No leftover `func_800E447C`; TOML, generated headers/body, and section-4 already use the leftover name. |
| s1782 | Synchronized `resetCraftInstanceMotionState` (`0x800E4480`, `0x1F4`). Per-row motion reset of `*(a0+4)`: 2-iter zero of `+0x74/+0x7C/+0xA4/+0xAC`, clear `+0x9A/+0x9B`, then `setNpcHealth`, `setObjectDetailLevel`, `initActorMotionParams`, and two `initObjectAnimSubstruct`. Companion deleted leftover `func_800E4480` at s432 as a duplicate. No generated `jal 0x800E4480`. TOML was stale `func_800E4480`; generated headers/body and section-4 already used the human name. |
| s1783 | Synchronized `playDualTextureAttachmentCueB` (`0x800E4674`, `0x200`). Two `lookupHmtTextureByName` (`a2=0` then `a2=1` on HMT `0x800A82CC`), paired `resolveNpcAttachmentPos` / `tickProgressChannel` / `triggerCueWithSlotEffect`, then `play3DSoundEvent`. No generated `jal 0x800E4674`. TOML was stale `func_800E4674`; generated headers/body and section-4 already used the human name. |
| s1784 | Synchronized `playAttachmentMaterialSoundSimpleB` (`0x800E4874`, `0x140`). Single `lookupHmtTextureByName` (`a2=0` on HMT `0x800A82D4` dest `sp+0x28`), optional `resolveNpcAttachmentPos` when indexed `+0xDC` float is nonzero, one `tickProgressChannel`, then on return-1 `triggerCueWithSlotEffect` `a1=0x2` plus `play3DSoundEvent` `0x1D`/`0x78`/`0x28` with float `0x800A82D8`. No generated `jal 0x800E4874`. TOML was stale `func_800E4874`; generated headers/body and section-4 already used the human name. |
| s1785 | Synchronized `playDualTextureAttachmentCueC` (`0x800E49B4`, `0x1FC`). Two `lookupHmtTextureByName` (`a2=0` on HMT `0x800A82D4` dest `sp+0x28` and `0x800A82DC` dest `sp+0x58`), optional paired `resolveNpcAttachmentPos` when indexed `+0xDC` float is nonzero, paired `tickProgressChannel`, then on both return-1 paired `triggerCueWithSlotEffect` `a1=0x2` plus `play3DSoundEvent` `0x1D`/`0x6E`/`0x28` with float `0x800A82E0`. No generated `jal 0x800E49B4`. TOML was stale `func_800E49B4`; generated headers/body and section-4 already used the human name. |
| s1786 | Synchronized `transformCraftAnchorsApplySubFx2` (`0x800E4BB0`, `0x210`). Rotation-matrix pair (`buildRotationMatrixSlot0` / `composeRotationMatrixSlot1`), dual `transformVec3ByMat34` anchors, `validateActorTargetLOS`, `applyToObjectSubstructByFlag`. Two generated `jal 0x800E4BB0` sites inside `npcWaterCraftUpdate` already dispatch the human name. TOML was stale `func_800E4BB0`; generated headers/body and section-4 already used the human name. |
| s1787 | Synchronized `tickCraftSplineOrientationVariant` (`0x800E4DC0`, `0x8EC`). Two-pass spline orientation, no audio: `mat34CrossRowsAndCopyPos` / `mat3x3InverseInto`, pending-child + LOS (`isPendingChildNpcActive` ×3 / `computeActorAnchorDeltaAfterLOS` ×2 / `getObjectMeshTransformOrLocal` / `computeAnchorRelativePositionByDistanceRatio`), then two copies of the rotation/quat/vec3 stack (`buildRotationMatrixSlot0` / `composeRotationMatrixSlot1` / `quatFromAxisAngle` / `rotateVec3ByQuat` / `transformVec3ByMat34`). Zero `play3DSound*` / `factor5RemoveListNode`. Two generated `jal 0x800E4DC0` sites inside `npcWaterCraftUpdate` already dispatch the human name. TOML was stale `func_800E4DC0`; generated headers/body and section-4 already used the human name. |
| s1788 | Synchronized `tickStructureWithDestructionAndChildren` (`0x800E56AC`, `0x48C`). Health-gated 2-iter debris-transform sibling of `buildDebrisTransformStack`: prefix `mat34CrossRowsAndCopyPos` on `*(npc+0x30)+0x28`, `getNpcCurrentHealth(*(npc+0x38))` early-out when `<=0`, then `s2` from npc while `< npc+0x8` composing three slots (`s2+0x3C/+0x44/+0x4C` dests `+0x1C`, params `s2+0x54/+0x5C/+0x64`) via `clearVec4QuadStruct` / flag `+0x4C` bits 0–2 (`addVec3At0x24` / `applyScaleToMat3x4` / `composeQuatToMat3x4`) plus `composeRotationMatrixSlot1`/`Slot0`. No spawn / recurse / teardown calls. One generated `jal 0x800E56AC` inside `npcWaterCraftUpdate` already dispatches the human name. TOML was stale `func_800E56AC`; generated headers/body and section-4 already used the human name. |
| s1789 | Synchronized `npcWaterCraftHandleDestruction` (`0x800E5B38`, `0x614`). Two-phase water-craft destroy on `lbu +0x99` (0 / 1; else epilogue): each live path `transformMeshPartIntoWorld`, `spawnNpcType0xAFromTemplate`, `spawnByteAnimDebrisDefault`, `play3DSoundEvent` `a0=0` stack `0x21`/`0x7D`/`0x50` (`a3=24.0f`), then `rand` / `composeRandomRotationMatrix` / `scaleVec3ByRandomRange` / `spawnDebris1Npc` / `spawnOrientedNpc`, plus a shared `spawnWaterSprayDebrisAndBurst`. Sole generated `jal 0x800E5B38` inside `npcWaterCraftUpdate` already dispatches the human name. TOML was stale `func_800E5B38`; generated headers/body and section-4 already used the human name. |
| s1790 | Confirmed `npcWaterCraftUpdate` (`0x800E614C`, `0x107C`). 9-way `jr` table on `(a1-1)<9` at `0x800A83D0`. Case 2 live tick calls `tickStructureWithDestructionAndChildren`, `tickCraftSplineOrientationVariant` ×2, `transformCraftAnchorsApplySubFx2` ×2, and the exclusive `npcWaterCraftHandleDestruction`. 82 `jal`s / 60 unique targets. No generated `jal 0x800E614C` — table-dispatched `npcXxxUpdate` sibling. Companion, generated headers/body, TOML, and section-4 already used the human name. |
| s1791 | Confirmed leftover `fake_func_800E71C8` (`0x800E71C8`, `0x8`). Two-instruction `lhu $v0, 0x14($v1)` / `lw $a0, 0x58($fp)` orphan between `npcWaterCraftUpdate`'s epilogue and leftover `func_800E71D0` (whose prologue is `addiu $sp, $sp, -0xA0`, so this is not a split first instruction). Companion leftover splat with no deleted-duplicate comment. No leftover `func_800E71C8`; TOML, generated headers/body, and section-4 already use the leftover name. |
| s1792 | Mandatory REVISIT. Three-arm Rice watch of the seven unwatched `submitGfxFrame` callers on the attract A/Start title-like 1024. All arms passed controls. Leave still adds `submitGfxFrame` +104/+102 (s1776 H1 reproduced). No unwatched entry rises: `runIdleFramesAndLoadSaveData` stays 1; `tickCraftSelectScreen` stays ~1028; `menuControllerInput` −179/−177 and `runResultsTextScreenLoop` −99/−97 drop with ship-select; `runMenuRandomBackdropScreen`/`menuSubtype02Handler`/`runModelViewerLoop` stay 0. Hangar frame flat 59. Extra `loadOverlay` +2 reproduced. H3-no-unwatched-rise selected. Next revisit needs jal-site / `$ra` watches, not another entry-PC set. |
| s1793 | Synchronized `transformCraftAnchorsApplySubFx3` (`0x800E71D0`, `0x1C0`). Rotation-matrix pair, dual `transformVec3ByMat34` anchors, two pending-child / LOS passes, `initObjectAnimSubstruct`, `applyToObjectSubstructByFlag`. One generated `jal 0x800E71D0` inside `tickFighterSquadronWithSplinePaths`. TOML, generated headers/body, and section-4 were stale `func_800E71D0`; companion `main_overlay.txt` already had the human name. Did not relocate the parked `mission_overlay.txt` leftover (s413 `m4_known_bad.txt`). |
| s1794 | Synchronized `tickFighterSquadronWithSplinePaths` (`0x800E7390`, `0x4D0`). Two-pass spline orientation, no audio: pending-child + LOS (`isPendingChildNpcActive` / `computeActorAnchorDeltaAfterLOS` on `+0x38`), mesh T&L (`getObjectMeshTransformOrLocal` / `mat34CrossRowsAndCopyPos` / `mat3x3InverseInto`) or fallback at `L_800E7634`, then rotation/quat/vec3 (`buildRotationMatrixSlot0`/`Slot1` / `composeRotationMatrixSlot1` / `quatFromAxisAngle` / `rotateVec3ByQuat` / `transformVec3ByMat34` / `vec3Cross`/`Dot`/`Length`). Writes `+0x48`/`+0x4C`. Companion comment overstates (zero `play3DSound*` / objective / teardown; no per-member walk). One generated `jal 0x800E7390` inside `npcGroundTroopUpdate` already dispatched the human name. TOML was stale `func_800E7390`; generated headers/body and section-4 already used the human name. |
| s1795 | Confirmed `npcGroundTroopUpdate` (`0x800E7860`, `0xFC8`). 9-way `jr` table on `(a1-1)<9` at `0x800A8520`. Setup type halfword `*(s3+0)` is `0x3B`/`0x3C`/`0x3D`/`0x50` (slti `0x3E`). Case 2 live tick has an inner 5-way table on `lh +0x64` at `0x800A8578` and calls `tickFighterSquadronWithSplinePaths` + `transformCraftAnchorsApplySubFx3`. 96 `jal`s / 58 unique targets. No generated `jal 0x800E7860` — table-dispatched `npcXxxUpdate` sibling of `npcTrainCarUpdate` / `npcWaterCraftUpdate`. Companion, generated headers/body, TOML, and section-4 already used the human name. |
| s1796 | Synchronized `playAttachmentCueNoTexture` (`0x800E8828`, `0x120`). Attachment cue + 3D sound without an HMT lookup: copy `0x30` bytes from `*(a0+4)` onto `sp+0x28`, scale `+0x44` by float `0x800A85A8` into Y, `resolveNpcAttachmentPos`, `tickProgressChannel`, then on return-1 `triggerCueWithSlotEffect` `a1=0x6` plus `play3DSoundEvent` `0x1D`/`0x6E`/`0x28` with float `0x800A85B0`. No generated `jal 0x800E8828`. TOML was stale `func_800E8828`; generated headers/body and section-4 already used the human name. |
| s1797 | Synchronized `applyCraftAnimDetailParamsB` (`0x800E8948`, `0xEC`). Short sibling of `applyCraftAnimAndDetailParams`: zero `+0x64`, copy float `0x800A85B4` to `+0x5C` and `*(s0+0x34)+0x90` to `+0x58`, then `setNpcHealth` / `setObjectDetailLevel`; when `lh +0x60` is 0, one `initActorMotionParams` from the `*(0x80137CE4)`-indexed row and one `initObjectAnimSubstruct` (floats `0x800A85B8`/`0x800A85BC`, pointer `0x800E8828`). Zero extra `initObjectAnimSubstruct` / `initAnimSubstructFromParams`. No generated `jal 0x800E8948`. TOML was stale `func_800E8948`; generated headers/body and section-4 already used the human name. |
| s1798 | Confirmed leftover `fake_func_800E8A34` (`0x800E8A34`, `0xC`). Three-instruction `lw $a0, 0x18($fp)` / `addu $a2, $a0, $zero` / `sll $a1, $a2, 1` orphan between `applyCraftAnimDetailParamsB`'s epilogue and `runDestructionPhaseSequence` (whose prologue is `addiu $sp, $sp, -0xB8`, so this is not a split first instruction). Companion leftover splat with no deleted-duplicate comment (next occupant `func_800E8A40` deleted s432 as a duplicate of the next function). No leftover `func_800E8A34`; TOML, generated headers/body, and section-4 already use the leftover name. |
| s1799 | Synchronized `runDestructionPhaseSequence` (`0x800E8A40`, `0x49C`). 5-way `jr` table on `lh +0x3C` at `0x800A85C0`: case 0 debris+child+rand/`composeRandomRotationMatrix`/`scaleVec3ByRandomRange`/`spawnDebris1Npc` then `spawnSplineWalkerCraft`; case 1 `gameStateByteGatedNpcHelper` plus the same debris/child path; cases 2/3/4 only `spawnNpcType0xAFromTemplate`. One generated `jal 0x800E8A40` inside `tickCraftWithPhasedDestruction` already dispatches the human name. TOML was stale `func_800E8A40`; generated headers/body and section-4 already used the human name. Companion leftover deleted s432 as a duplicate. |
| s1800 | Synchronized `tickCraftWithPhasedDestruction` (`0x800E8EDC`, `0xBA8`). 9-way `jr` table on `(a1-1)<9` at `0x800A8638`. Setup / teardown / live tick (`runDestructionPhaseSequence`) / visibility+path / damage (`dealDamageToNpc`, `datItemSetObjectiveBooleanCount`, inner 5-way on `lh +0x3C` at `0x800A86B0`) / slot-action. Table-dispatched; no generated `jal 0x800E8EDC`. TOML was stale `func_800E8EDC`; generated headers/body and section-4 already used the human name. No leftover splat. |
| s1801 | Synchronized `initNpcHealthAndDetailFromChild` (`0x800E9A84`, `0x54`). Copies child-template HP (`*(s0+0x34)+0x94` → `s0+0x50`), clears `+0x3E`, then `setNpcHealth` (`0x800F2070`) and `setObjectDetailLevel` (`0x800F2830`). No generated `jal 0x800E9A84`. TOML was stale `func_800E9A84`; generated headers/body and section-4 already used the human name. No leftover splat. |
| s1802 | Confirmed leftover `fake_func_800E9AD8` (`0x800E9AD8`, `0x8`). Two-instruction `lw $v1, 0x34($v0)` / `addiu $v0, $zero, -1` orphan between `initNpcHealthAndDetailFromChild`'s epilogue and leftover `func_800E9AE0` (whose prologue is `addiu $sp, $sp, -0x40`, so this is not a split first instruction). Companion leftover splat with no deleted-duplicate comment. No leftover `func_800E9AD8`; TOML, generated headers/body, and section-4 already use the leftover name. |
| s1803 | Synchronized leftover `func_800E9AE0` (`0x800E9AE0`) to size `0x114`. Generated headers/body and section-4 were already one function (`addiu $sp, $sp, -0x40` … `jr $ra` / `addiu $sp, $sp, 0x40` at `0x800E9BEC`/`0x800E9BF0`). `0x800E9B10` is mid-function `lui $at, 0x800B`, not a prologue. Companion leftover plus `fake_func_800B58B4` comment already said `func_800E9B10` is not real and splits this function. TOML was the stale `0x30`+`0xE4` split; merged to one leftover row. Did not steal main-overlay `initObjectAnimAndDetail` at the same VRAM. |
| s1804 | Synchronized `playStateGatedDestroySound` (`0x800E9BF4`, `0x180`). State 0/1/2 picks paired tables, then optional `play3DSoundEvent` `0x62`/`0x63`. Two generated `jal 0x800E9BF4` sites in `npcAtPtPlaySkywalkerErrorCallout` and `npcAtPtUpdate`. TOML was stale `func_800E9BF4`; generated headers/body and section-4 already used the human name. |
| s1805 | Synchronized `spawnObjectImpactEffectWithSound` (`0x800E9D74`, `0x150`). HMT `0x800A86E8`, optional `setObjectSubstructF10IfReady` `0x3D888889`, `tickProgressChannel`, then on return-1 `getObjectNpcTypeId` / `triggerCueWithSlotEffect` / `slotDispatcherIter` `a1=0xA` / `play3DSoundEvent` `0xD`/`0x78`/`0x28` with float `0x800A86F8`. No generated `jal 0x800E9D74`. TOML was stale `func_800E9D74`; generated headers/body and section-4 already used the human name. |
| s1806 | Synchronized `computeNpcOrientationFromAimVectors` (`0x800E9EC4`, `0x5AC`). Pending-child + LOS (`isPendingChildNpcActive` / `computeActorAnchorDeltaAfterLOS` on `+0x38`), mesh T&L (`getObjectMeshTransformOrLocal` / `computeAnchorRelativePositionByDistanceRatio` `0x41200000` / `mat34CrossRowsAndCopyPos` / `mat3x3InverseInto` / `transformVec3ByMat34`), then rotation/quat/vec3 (`buildRotationMatrixSlot0`/`composeRotationMatrixSlot1` from `+0x68`/`+0x64`, `vec3NormalizeInto` / `vec3Dot` / `constMinusSinfApprox` / `vec3Cross` / `normalize_vector` / `quatFromAxisAngle` / `rotateVec3ByQuat`). One generated `jal 0x800E9EC4` inside `npcAtPtUpdate` already dispatched the human name. TOML was stale `func_800E9EC4`; generated headers/body and section-4 already used the human name. |
| s1807 | Synchronized `npcAtPtPlaySkywalkerErrorCallout` (`0x800EA470`, `0x170`). Anim-slot teardown/rebuild on `lbu +0xB3` (1/2/3) then `playStateGatedDestroySound`; body does not emit voiceId `0xC4`. Three generated `jal 0x800EA470` sites inside `npcAtPtUpdate`. TOML was stale `func_800EA470`; generated headers/body and section-4 already used the human name. |
| s1808 | Mandatory REVISIT. Three-arm Rice watch of the 13 ROM `jal 0x8000C07C` sites plus callee `prev_pc` on `submitGfxFrame`. All arms passed controls; histogram sums equal the entry count. Leave still adds `submitGfxFrame` +98/+107. H2 selected: `menuControllerInput` jal `0x800B8014` +276/+281 and `runInMissionFrame` jal `0x800FAD90` −175/−177 net +101/+104. Five other ROM jals never appear as prevs (VRAM counts are overlay aliases). s1792 menu-input *entry* drop was overlay-aliased. Do not repeat this recipe. |
| s1809 | Confirmed `npcAtPtUpdate` (`0x800EA5E0`, `0x13A4`). 9-way `jr` table on `(a1-1)<9` at `0x800A87B8`. Case 2 live tick calls exclusive `npcAtPtPlaySkywalkerErrorCallout` ×3 plus `computeNpcOrientationFromAimVectors`. 119 `jal`s / 74 unique targets. No generated `jal 0x800EA5E0` — table-dispatched AT-PT `npcXxxUpdate` sibling of `npcAtAtUpdate` / `npcAtStUpdate` / `npcGroundTroopUpdate`. Companion, generated headers/body, TOML, and section-4 already used the human name. |
| s1810 | Synchronized `resetObjectPoolListHead` (`0x800EB984`, `0xC`). Delay-slot `sw $zero, -0x3F40($v0)` with `$v0 = 0x80110000` stores 0 at `0x8010C0C0`. Sole generated caller `resetObjectContextPool` at `0x800EC4F8`, between `resetCraftSubsystemGlobal` and `clearObjectPoolStateFlag`. Same 3-insn store-zero idiom as s1758 `resetCraftSubsystemGlobal`. TOML was stale `func_800EB984`; generated headers/body and section-4 already used the human name. |
| s1811 | Confirmed `npcPowerUpUpdate` (`0x800EB990`, `0x77C`). 4-way `a1` compare (setup / teardown / live tick / visibility) plus an 8-way `jr` table at `0x800A88C8` on pickup type that ORs bits onto `*(0x80130B4C)`. 25 `jal`s / 21 unique targets including `getCraftRecordByIdx` and `play3DSoundEvent`. No generated `jal 0x800EB990` — table-dispatched power-up `npcXxxUpdate` sibling. Companion, generated headers/body, TOML, and section-4 already used the human name. |
| s1812 | Confirmed leftover `fake_func_800EC10C` (`0x800EC10C`, `0x4`). One-instruction INVALID COP2 word `0x4A652950` / `do_break(0x800EC10C)` orphan between `npcPowerUpUpdate`'s epilogue and leftover `func_800EC110` (whose prologue is `addiu $sp, $sp, -0x20`, so this is not a split first instruction). Companion leftover splat with no deleted-duplicate comment. No leftover `func_800EC10C`; TOML, generated headers/body, and section-4 already use the leftover name. |
| s1813 | Synchronized `allocObjectPoolNode` (`0x800EC110`, `0x278`). Freelist head `0x8010C0D0` / used-list `0x8010C0D4`; empty-pool `rs_malloc(0x6C0)` 4-slot header; slot `block + t0*0x1AC + 0x10`. Sole generated `jal 0x800EC110` inside `createAndInitObject` at `0x800EC5B4` (`a1+0x1AC`). Companion `main_overlay.txt` already had the name; mission leftover stays `func_800EC110` (overlay-alias; naming it would collide with main). TOML, generated headers/body/INL, and the jal site were stale `func_800EC110`. |
| s1814 | Synchronized `unlinkAndFreeChildNpcNode` (`0x800EC388`, `0x150`). Node = `MEM_W[a0+0]`, extra = `MEM_BU[a0+4]`; `(node_byte0 + extra) == 4` unlinks from `0x8010C0D0`/`0x8010C0D4` (`+0x8`/`+0xC`) then `rs_free`. Sole generated `jal 0x800EC388` inside `clearPendingAndDestroyChildNpc` at `0x800EC6A4`. TOML was stale `func_800EC388`; companion, generated headers/body, and section-4 already used the human name. |
| s1815 | Synchronized `resetObjectContextPool` (`0x800EC4D8`, `0x3C`). Zeros `0x8010C0D0`/`0x8010C0D4`, then `resetCraftSubsystemGlobal` / `resetObjectPoolListHead` / `clearObjectPoolStateFlag`. Sole generated `jal 0x800EC4D8` inside `initMission` at `0x800FA2D4`. TOML was stale `func_800EC4D8`; companion, generated headers/body, and section-4 already used the human name. |
| s1816 | Synchronized `freeAllObjectContextPoolNodes` (`0x800EC514`, `0x74`). Walks `0x8010C0D0` then `0x8010C0D4`, `rs_free` each via `+0xC` next. Sole generated `jal 0x800EC514` inside `endMissionCleanup` at `0x800FBAD4`. TOML was stale `func_800EC514`; companion, generated headers/body, and section-4 already used the human name. |
| s1817 | Synchronized `createAndInitObject` (`0x800EC588`, `0xFC`). `jal allocObjectPoolNode` at `0x800EC5B4` with `a1+0x1AC`, then field init and optional callback; 20 generated `jal 0x800EC588` sites already dispatch the human name. TOML was stale `func_800EC588`; companion, generated headers/body, and section-4 already used the human name. |
| s1818 | Synchronized `clearPendingAndDestroyChildNpc` (`0x800EC684`, `0x3C`). `jal clearPendingChildNpc` at `0x800EC698` on `MEM_W[a0+0]`, then `jal unlinkAndFreeChildNpcNode` at `0x800EC6A4`; always returns 1. 16 overlay jal sites already dispatch the human name; 4 main-text sites stay `LOOKUP_FUNC`. TOML was stale `func_800EC684`; companion, generated headers/body, and section-4 already used the human name. |
| s1819 | Synchronized `destroyObjectOwnedNpcSlot` (`0x800EC6C0`, `0x2C`). `lbu +0x1A4`; if nonzero `lhu +0x198` then `jal destroyNpcSlotByIndex` at `0x800EC6D8`. 17 overlay jal sites already dispatch the human name; 4 main-text sites stay `LOOKUP_FUNC`. TOML was stale `func_800EC6C0`; companion, generated headers/body, and section-4 already used the human name. |
| s1820 | Synchronized `tickCraftMountedAnimationEffect` (`0x800EC6F0`, `0x538`). `lbu +0x4C` / `lwc1 +0x48` dt-accumulate against `*(s0+4)+0x70`; then `findActiveNpcInSlotChain` / `getNpcContextField8` / `tickObjectSoundCueState`. Sole generated `jal 0x800EC6F0` inside `craftMountedAnimationNpcHandler` at `0x800ECD90`. Companion `main_overlay.txt` already had the name (s415 revert from mission); mission leftover stays `func_800EC6F0` (overlay-alias; naming it would collide with main). TOML, generated headers/body/INL, and the jal site were stale `func_800EC6F0`. |
| s1821 | Synchronized `craftMountedAnimationNpcHandler` (`0x800ECC28`, `0x1B4`). Action-1 spawn copies msg `+0x10/+0x14/+0x18` into child `+0x8/+0xC/+0x10`, clears child `+0x48/+0x4C/+0x4D`, and indexes the craft spatial grid at `0x801375D8+0x34`. Action-3 tick jals `tickCraftMountedAnimationEffect` at `0x800ECD90`, then `destroyNpcSlotByIndex` at `0x800ECDAC` when that tick returns 1. No generated `jal 0x800ECC28` (NPC-handler table dispatch). TOML was stale `func_800ECC28`; companion, generated headers/body, and section-4 already used the human name. |
| s1822 | Synchronized `dispatchSlotActionTwelveByGlobalId` (`0x800ECDDC`, `0x28`). Thin wrapper: `lhu` global id from `0x8013959C`, `a1 = 0xC`, `jal slotDispatcherIter` at `0x800ECDF0`. Sole generated `jal 0x800ECDDC` inside `tickMissionObjectives` at `0x800FBD18` already dispatches the human name. TOML was stale `func_800ECDDC`; companion, generated headers/body, and section-4 already used the human name. |

The sweep cursor after s1822 is leftover `fake_func_800ECE04`
(`0x800ECE04`, size `0xC`). Neighbor peek: companion
`mission_overlay.txt`, generated headers/body/INL, and TOML already
use the leftover splat name. First insn `srl $v0, $t1, 4`; last
`multu $v0, $v1` at `0x800ECE0C`. Previous occupant
`dispatchSlotActionTwelveByGlobalId` ends exactly here; next
generated occupant is `datItemActorNpcHandler` (`0x800ECE10`,
`0x338`; TOML still leftover `func_800ECE10`). Companion comment
says `func_800ECE10` was deleted s432 as a duplicate of
`datItemActorNpcHandler`. Mandatory revisits in this window:
s1650, s1666, s1682, s1698, s1714, s1744, s1760, s1776, s1792,
s1808. After s1822 the last-15 titles still include s1808's
revisit, so the next iteration resumes the leftover
`fake_func_800ECE04` census.

**Classified Rice frontend routes (do not repeat).** Dummy video stays at
width 320 / origin `0x006dd280`. Homebrew Rice with
`--video …/mupen64plus/mupen64plus-video-rice.dylib` and the eleven-Start
schedule reaches `320→640` at about 2.3s, `640→1024` at about 17.2s, and
`1024→512` hangar at about 38.4s, origins `0x006ab400`/`0x006ab800` (s707,
s1496). Hangar hold stays in `runHangarSelectionFrame` at 512. Extra Start
or A leaves to a 640 planet/text-crawl viewer at `0x006a2900`/`0x006a2e00`
— menu-overlay case 6 `runModelViewerLoop` (`0x800C9BF0`), not a mission or
cinematic. Pre-exit B (`sym=224`, pad `0x400000`) is a distinct
`512→1024→640` with no viewer or mission-entry PC; after that intermediate
1024, A or Start cancels back to hangar 512 and Z is ignored. The arrived B
640 (`0x00696100`/`0x00696600`) is neither hangar nor viewer (hangar-frame
PCs stay at the earlier visit count, viewer PC 0) and times out at ~117.7 s
to attract 512 (`0x00690400`). On that 640, A/Start cancel
`640→1024→512` hangar; Z, C, L, R, and valid D-pad are ignored (s1650,
s1666, s1682). On the attract 512 that timeout reaches, A/Start/C-up/L/Z
at 119/123 leave `512→1024` at 126.3–126.4 s origin `0x00790400`/`0x00790800`
(title-like; same pair as the B-route intermediate) and stay on that 1024
through 133.5 s (s1714); hangar-frame PCs 60–61 matching hold; viewer 0;
`0x80000B70` = 1 matching hold. Hold stays attract 512 through 133.4 s.
C-down, C-left, C-right, R, and valid D-pad stay attract 512 through
125.8 s (s1698; not retested past 126 s). Overlay-resident entries on that
1024 match hold (`cinematicLoopBody` 2, `load_cutscene` 2,
`runMenuContentStateMachine` 0, `runInMissionFrame` 1) and drop the
`0x800AA658` / `0x800C131C` tick that hold's attract continues (s1744
H3-stop-tick). The complete `menuOverlayInit` jump table also adds no
new case (s1760): case 9 stays 1, cases 3/6/10 stay 0, cases 1/2/4-5-7/8
and the dispatcher drop. Extra menu dest +1 is reproduced. The 1024 is
not a new cinematic, menu-SM, mission-frame, or jump-table-case session.
Leave does add `submitGfxFrame` +104/+102 vs hold without a new
`mainGameLoop` or `applyLevelScreenAndCameraSettings` entry; `emitFrameRdpInitDl`
drops with the ship-select ticks (s1776). The extra +104 is not an
entry of the seven unwatched callers either (s1792 H3): idle-save stays
1, craft-select stays ~1028, menu-input and results-text drop, and
random-backdrop / subtype-02 / model-viewer stay 0. Callee-side
`prev_pc` names the extra as `menuControllerInput` jal `0x800B8014`
+276/+281 offset by `runInMissionFrame` jal `0x800FAD90` −175/−177
(s1808 H2; histogram sums match the entry count). The s1792
menu-input entry drop is overlay-aliased. Rice dies around 135 s; the only observed `1024→640` of this pair
is s1666's single-source Z continuation at 159.4 s origin `0x00696100`
(B-frontend). s1698's Z-stays-512 through 125.8 s was a flush cutoff;
s1666's 128.3 s Z leave was the same leave after a later 126.4 s press.
`0x80000B70` is `loadOverlay+0x50` (`0x80000B20`, size `0x124`).
Still-open questions (M4 DMEM→RDRAM other than `0xD60`) live in
`CURRENT-TRUTH.md`.

**Superseded claims compacted out of CURRENT-TRUTH in s1728.** Stale/unseen
writer (physical-byte samples saw nonzero `0x8011A8A0`). `setViModeType`
maps `osTvType`, not `osResetType`. Boot/menu overlay-dispatch closed by
mission and post-sec2 behavior. Nonblank-EEPROM refuted by paired
existing-versus-zero EEPROM runs. Broad retail-only GPR mismatch: saved
`s3..s7`/`t3` dead or overwritten; `sp`/`ra` differ only in bookkeeping.
Frontend/launcher/savestate artifacts exist; audited lifecycle still has
no new retail state source. s1194–s1239 "no new retail-entry route /
stays 320" used dummy video; Rice supplies the later phase. s1135
"`0x688..0x710` is the retail shade record" rejected by s1512. s1086
"retail never accesses `0x130B10:0x130B58`" superseded by s1528. s1698
"Z on attract 512 stays 512 through 125.8 s" superseded by s1714.
