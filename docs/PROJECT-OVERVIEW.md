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

`0x800290d4` collected six independent triggers — by far the most-repeated site, and below
`overlay_start` (`0x800A5130`) in core `.text`, not inside any of the ten functions' own bodies. This
points at one or a few shared downstream corruption sinks reachable from many different newly-real
call sites, not ten unrelated bugs — the standing top lead for a dedicated M3/M4 root-cause session
once the project's next focus is set (see CURRENT-TRUTH's USER DIRECTIVE). `0x80011088` recurred
twice (s407, s417); `0x80065e94` and `0x8000b650` each fired once.

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
