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
