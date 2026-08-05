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
