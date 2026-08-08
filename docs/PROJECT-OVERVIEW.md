# Rogue Squadron 64 Recomp — project overview and recurring hurdles

Companion to the other two docs, and the one to read first if you are new to this repo or returning
after a break:

- **`docs/PROJECT-OVERVIEW.md`** (this file) — what the project is, how the pipeline fits together,
  and the hurdle *classes* that have cost the most time. Durable; changes slowly.
- **`docs/CURRENT-TRUTH.md`** — what is true right now: working config, live defects, next steps,
  and the list of superseded conclusions. Read before doing any work.
- **`PORTING-STATE.md`** — the chronological log, 43 sessions deep. Authoritative for detail,
  but roughly two dozen of its conclusions were later overturned; never act on it without checking
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
cull-census-identity violations). Overlays 12/44 still take the old broken path by design — the same
splice recipe applies if they ever matter. Full detail: PORTING-STATE s44–s49; day-to-day state in
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
~38630/38780/38801).

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
