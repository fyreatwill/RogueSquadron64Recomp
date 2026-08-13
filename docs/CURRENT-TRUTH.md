# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`, which is chronological and contains superseded conclusions.
New here, or back after a break? Read **`docs/PROJECT-OVERVIEW.md`** first — what the project is, how the four layers fit together, and the hurdle classes that have cost the most time.
Session tags: `s1` = 2026-07-09/10 build + overlay work, `s2`–`s9` = `## LLE session N`, `s10`–`s32` = `## Session N`.

## USER DIRECTIVE (2026-08-04, human-set — overrides Next-steps ordering until satisfied)
Priority order for upcoming iterations, set after the 300-session review:
1. **Maintenance** (Step 0 of ITERATION.md triggers it at 60,000 bytes): compact per the Maintenance
   section of tools/agent/ITERATION.md; a >=200-net-line shrink counts as ADVANCED.
2. **M5 audio de-stubbing**: DONE and fully CLOSED; next M5 work needs a genuinely new lead.
3. **M3 crash work only as systematic idiom-class audits**, never reactive single-crash chases.

## Current truth (reviewed through s788; compacted in maintenance s776)

The durable history for s2–s775 is in `docs/PROJECT-OVERVIEW.md` §§3–28 and
the chronological ledger. The active facts are:

- The oracle identity audit (s775) found byte-identical executable, core, RSP,
  input-plugin, and ROM artifacts. Fresh configs differed only in
  `Core/EnableDebugger`.
- The matched 70-second debugger A/B (s774) had positive controls: debugger-on
  recorded 11,785,277 whole-RDRAM writes, 4,199 VI, and all 11 PIF presses;
  debugger-off independently sampled VI for the full run. Both remained at
  width 320/origin `0x6dd280`. This refutes polling failure and late debugger
  interference, but does not yet explain the oracle's phase divergence.
- The port's M3 path is live through post-sec2 outdoor presentation. The open
  blocker is the FULL_SYNC/E9 loss; aligned task streams contain many E9s while
  the authoritative parser sees very few. The latest overlay-return audit
  (s761–s765) left `0x1E8C` reachability unevaluable after two pre-window
  crashes. Do not classify that hypothesis from those nulls.
- M5 audio de-stubbing and prior idiom-class campaigns are closed. Product
  freelist restore is ON; garbage-CIMG and wrap-drop mitigations remain OFF.
- The s786 low-noise post-sec2 reachability repeat reached VI width 1024 after
  48.1 seconds with the phase-relative key schedule firing and repeated
  positive provenance controls (`emit=1`, `raw=1`, `dispatch=1`, `match=1`).
  It crashed at 50.4 seconds after 15 frames in
  `allocAndInitGridCellArray+624` (SIGBUS, fault address `0x380000014`, last
  guest PC `0x80001c94`). The section-2 provenance latch fired, but no usable
  post-sec2 parser-chain sample preceded the crash. This is a different crash
  family from s785's Metal barrier failure; it leaves the FULL_SYNC parser
  hypotheses unevaluable and adds no explanation or mitigation.
- The s787 stability repeat passed the same provenance positive controls
  (`emit=1`, `raw=1`, `dispatch=1`, `match=1`) but died before the 1024 gate:
  VI reached 640, then RT64 aborted in `FramebufferManager::findTileCopyId`
  during `State::fullSync` (last guest PC `0x8000834c`). Across s785-s787,
  three consecutive pre-chain runs failed in distinct families (Metal barrier,
  grid allocation, framebuffer tile-copy). This selects the bounded
  H-prechain-deterministic failure class, not a parser hypothesis; no parser
  sample or mitigation is justified. The next unit is a systematic
  allocation/grid crash-idiom audit.
- The s788 source audit found the active generated tree at
  `../N64Recomp/RecompiledFuncs`, and the build manifest compiles that exact
  tree; stale-generated-view is therefore refuted for this unit. The s786
  `allocAndInitGridCellArray+624` site is the grid initializer's third
  `rs_malloc` call, while s787's `findTileCopyId` assertion has only two RT64
  call sites and receives `callTile.tileCopyWidth/Height` or an RDP-derived
  tile rectangle, not a grid allocation. The s786 fault (`0x380000014`) and
  mcontext values `0x80000000`/`0x80000014` identify malformed free-list state
  consumed by `rs_malloc`; existing `[fl-zero-fault]` records independently
  show the same allocator consuming out-of-range free-list slots. No source
  or trace evidence identifies one writer shared by the s785 Metal barrier,
  s786 allocator, and s787 tile-copy families. This is a mixed pre-chain
  failure class, not a justification for a guard. Next: systematic
  `rs_malloc`/free-list writer audit.
- The matched s778 oracle runtime check with the alternate `R4300Emulator`
  again found no later retail VI phase: debugger-on had 11,782,489
  whole-RDRAM positive-control writes, 4,198 VI callbacks, and all 11 PIF
  presses; debugger-off independently produced 70 raw VI polls, all at width
  320/origin `0x6dd280`. This refutes the alternate execution backend as the
  missing phase for this recipe. Exact-recipe reachability versus
  schedule/timing sensitivity remains unresolved.
- The matched s779 oracle repeatability run used three concurrent emulator-1
  debugger-on arms with the all-RDRAM positive control, VI/PIF traces, and the
  eleven-entry Start schedule. All three stayed at width 320/origin
  `0x6dd280`, with 11,768,897 / 11,771,521 / 11,768,897 whole-RDRAM writes,
  4,193 / 4,194 / 4,193 VI callbacks, and all eleven PIF presses. This
  strengthens the exact-recipe 320-only explanation and selects it over
  timing sensitivity for this recipe; it does not explain the documented
  later retail timeline.
- The matched s780 oracle horizon A/B ran two concurrent emulator-1 arms for
  130 seconds with the whole-RDRAM positive control, VI/PIF traces, and all
  eleven Start presses. Both recorded 21,635,499 whole-RDRAM writes, 7,799
  VI callbacks, all eleven presses, and only width 320/origin `0x6dd280`.
  This selects H-oracle-exact-recipe-320 over H-late-phase for the tested
  driven recipe and rules out a transition merely delayed beyond 70 seconds;
  it does not explain the documented later retail timeline.
- The matched s777 oracle runtime check again found no later retail VI phase:
  debugger-on had the whole-RDRAM positive control (11,768,621 writes), 4,193
  VI callbacks, and all 11 PIF presses; debugger-off raw polling stayed at
  width 320/origin `0x6dd280` for the full 70 seconds. The off arm's rc=3 is
  the oracle's documented clean zero-hit result. This refutes late debugger
  interference for this recipe; schedule/timing versus expected-320 behavior
  remains unresolved.
- The s781 oracle input-only A/B held the same 130-second emulator-1 recipe
  and positive controls while comparing no input presses against the eleven
  Start schedule. The undriven arm recorded 21,588,309 whole-RDRAM writes and
  7,799 VI callbacks; the driven arm recorded 21,618,393 writes, 7,793 VI
  callbacks, and all eleven PIF Start presses. Both remained width 320/origin
  `0x6dd280` for the full horizon. This refutes input schedule alone as the
  explanation for the documented later phase; input-plugin attachment versus
  the exact runtime recipe remains unresolved.
- The s782 no-press input-plugin A/B resolved that last input distinction:
  the unattached arm had 21,588,123 whole-RDRAM writes / 7,799 VI and the
  attached-input arm had 21,605,494 writes / 7,788 VI. Both stayed at width
  320/origin `0x6dd280` for 130 seconds. This refutes input-plugin attachment
  as the missing phase trigger and selects a remaining runtime/ROM discrepancy.
- The s785 low-noise post-sec2 reachability preflight reached VI width 1024
  after 47 seconds, with provenance controls live (emit=1, raw=1,
  dispatch=1, match=1) and the phase-gated key schedule firing. It then
  crashed 30.2 seconds into capture after 9 frames in the Metal renderer
  barrier path (si_addr=0x60, last guest PC 0x8000834c). No post-sec2
  parser-chain result was obtained. This selects H-640-transient for the
  s784 pre-target failures, but leaves the chain hypotheses unevaluable.
- The s783 stock-front-end audit found the stock CLI starts with no
  `Input-SDL-Control1` section and falls back to `InputAutoCfg.ini`, while the
  oracle materializes an explicit keyboard section. A fresh 130-second oracle
  run with the same attached SDL input path, `R4300Emulator=1`, retail ROM,
  debugger/whole-RDRAM positive control, VI/PIF traces, and eleven verified
  Start presses recorded 21,618,871 writes and 7,793 VI callbacks, but stayed
  at width 320/origin `0x6dd280` throughout. This refutes the concrete
  input-config fallback difference as the phase trigger; no port runtime code
  changed.

**ORIGIN:** this compaction retains the latest measured facts and pointers;
deleted session narrative is recoverable from `PORTING-STATE.md` and git.

## Goal stack — work strictly top-down

A milestone is done only when its definition-of-done is met **and documented here**. The
autonomous loop (`tools/agent/loop.sh`, contract in `tools/agent/ITERATION.md`) always draws its
work unit from the top open milestone, so this ladder is what keeps it from idling.

**M1 — hangar band root cause and fix: DONE (s48).** Mechanism: `docs/PROJECT-OVERVIEW.md` §3.

**M2 — post-clip-fix regression sweep: DONE (s49).** Stability baseline: 1138 tasks, fanjal=9448,
0 cull-census-identity violations. The 3 `[missing-func]` addresses **DONE/CLOSED s399** (item -6).

**M3 — first gameplay: OPENED (s50), still open.** AVAILABLE CRAFT and SELECT YOUR CRAFT reachable
and stable; ~20 crash classes closed s50-s294. Leave-key "hangar-flight" OVERTURNED s150; **s577
REAL hangar exit CONFIRMED** (case 3→5→6→8). Post-exit FULL_SYNC starvation product-fixed via
`ROGUESQ_FS_PIPE_INJECT` (default OFF; items -354..-358). Pipeline status as of **s671**:
- thr11 (`saveServiceWorker` `0x8006F2CC`) → sec4 → thr12 (`hudDisplayUpdateWorker` via
  `loadLevelTextureCache`) → **sec2 LIVE** under product multi-header restore.
  **s668 dual-source:** thr11d→ok136c→thr12→sec2. **s669 dual-source offline:**
  post-sec2 outdoor content LIVE ~195–200s (VI 512 0x620000/0x690000, present
  swap FIRE) then **menu sec3 return**; thr12 long-lived; **rdpFs plateau**
  (syncs=0 / E9 starved) entire thr13 window; packTlut=0. **s670 split:**
  menu-return/thr12-teardown is **input-gated** (-422). **s671: -422
  CONFIRMED dual-source and CLOSED** (2/2 pulsed attempts: thr12 alive
  >1000s, 0 sec3 return, 0 packTlut) while the **rdpFs plateau itself is
  untouched by both inject (Arm A) and input (Arm B)** — stays open as -421,
    **s675 confirms command-boundary E9 is abundant** in two independent
  post-sec2 samples (4,444/12,924 and 9,549/13,135 tasks) while runner
    FULL_SYNC appears in only 3 tasks per sample. Walker misalignment is
    refuted as the sole explanation. **s676 dispatch discriminator:** one
    recovery-active post-sec2 run had aligned walker E9 sum **32,150** in
    **6,719** positive task probes, while the authoritative RDP parser's
    cumulative E9 count advanced by only **2**. Every authoritative E9 seen
    reached `GBI_RDP::fullSync` and `State::fullSync`. Thus the dominant loss
    is before authoritative dispatch; map/handler and State accounting are
    ruled out for those commands. Residual rank: (1) **-421 authoritative
    parser advance/control-flow mismatch** then rdpFs
  starvation mechanism / packTlut (-373), (2) B8
  co-gate -393, (3) -387 **5×**. Do **not** productize DROP_GARBAGE_CIMG; do
  **not** re-soak thr11d rate (-419 CLOSED) or re-run the -422 input pulse
  (CLOSED, no residual).
- Co-gates: recovery (-374/-413/-414/-418), mat3inv (-375), ship (-376/-377/-392/-393),
  class-D (-378), FORCE_STATE6 (-381 CLOSED), freeroll (-382..-384), thr12 path
  LIVE under headers (-385 dissolved), sinfApprox (-386 1×), do_rom_read
  (-387 **5×**). thr11d metric = post-hsel destroy of `0x8006F2CC` only (s618).
  Tools default OFF: `FORCE_STATE6_AFTER`, `FORCE_CASE6_START`, `FS_PIPE_INJECT`,
  `ALLOW_WILD_W`, `FL_HDR_HARD_SKIP`, `FL_HDR_RESTORE=0`, `FL_RESTORE_MODE=body`,
  `DROP_WRAP_RDP`, `DROP_GARBAGE_CIMG`. Product ON: freelist multi-header restore.
  Diagnostics: `ROGUESQ_LOG_CIMG_RAW`, `ROGUESQ_LOG_DL_SYNC2`.
- Full durable arc: **`docs/PROJECT-OVERVIEW.md` §27**; items -349..-422; Sessions 577-675.
DoD = **cutscene→in-mission** + craft input.
*Done when:* 60s in-mission render, craft responds to synthetic input, stability 0, phase timeline
covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause; S=0 triangles in the 640 attribution phase; the I4 `sample=64x128` anomaly if M1 didn't
consume it. The 3 `[missing-func]` addresses, the `main_overlay.txt` phantom-overlay-function
family, and its `0x800290d4` clustering are all **DONE/CLOSED** (items -6/-249/-259).

**M5 — audio de-stubbing: DONE and fully CLOSED (s297-376).** No outstanding thread; next M5 work
needs a genuinely new lead (rechecked s570: zero new leads, intentionally-left stubs still C88
force-zero + default `real_ucode=0`; due again s573+). Full arc: `docs/PROJECT-OVERVIEW.md` §9-§12.

## Backlog — one monotonic sequence (reviewed and compacted s729)

Legacy negative identifiers remain searchable in `PORTING-STATE.md` and
`docs/PROJECT-OVERVIEW.md`; this active backlog uses the single monotonic sequence below. Closed lineages are not backlog items.

1. **Oracle phase divergence — OPEN, H-oracle-runtime-or-ROM-discrepancy selected.**
   s780's two-arm 130-second horizon run kept every driven arm at
   width 320/origin `0x6dd280`, with 21,635,499 whole-RDRAM positive-control
   writes, 7,799 VI callbacks, and all eleven PIF Start presses per arm. This
   rules out a merely late transition in the driven recipe. s781 also kept both
   no-press and eleven-Start arms at 320-only, with positive whole-RDRAM writes
   in both and all eleven PIF presses in the driven arm. Next: phase-gated A/B
   no-press runs that differ only in whether the verified input-SDL plugin is
   attached. **s782 completed that test:** the unattached arm had 21,588,123
   whole-RDRAM writes / 7,799 VI and the attached arm had 21,605,494 / 7,788;
   both were 320-only at `0x6dd280` for the full 130 seconds. This refutes
   input-plugin state. s783's stock-CLI audit found only an input-config
   fallback difference (missing `Input-SDL-Control1` versus explicit keyboard
   defaults); the fresh 130-second oracle arm with the attached input path and
   verified eleven Start presses still stayed 320-only with positive controls.
   This refutes that difference. Next: return to the M3 FULL_SYNC parser/control-flow
   audit; do not change the port runtime for the oracle discrepancy.
- **Overturned: H-oracle-runtime-environment-divergence (s777).** s777's
bounded identity audit found byte-identical oracle/core/RSP/input/ROM artifacts;
the matched configs differ only by `EnableDebugger`. This rules out artifact,
plugin-path, config-generation, ROM, and input-plugin identity drift, but not
an emulator/runtime behavior difference. s774's
70-second A/B made debugger-off raw polling independently visible for the full
run: 70 samples after initialization stayed at width 320/origin `0x6dd280`,
while debugger-on independently recorded 4,199 VI, all 11 PIF presses, and
11,785,277 positive-control writes. This refutes the poll-observation and
debugger-interference explanations for the 320-only result. s777 independently
reproduced the same result with 11,768,621 writes and 4,193 VI callbacks.
s778's alternate-backend A/B reproduced the 320-only result with positive
controls, refuting the execution-backend explanation for this recipe. It was
believable because the identity audit ruled out artifact and plugin drift while
leaving runtime behavior as the remaining broad class.

2. **M3 / legacy -421 — post-sec2 FULL_SYNC plateau: OPEN.** Outdoor rendering and presentation remain live through section 2, but genuine FULL_SYNC commands are scarce while GFX continues. **s784:** the batched parser-chain audit was unevaluable: both the verbose-chain run and its low-noise fixed rerun had positive control tasks (`emit=1`, `raw=1`, `dispatch=1`, `match=1`) but died at VI 640 before the 1024/post-sec2 gate; the first was a `viRetraceHandlerThread` SIGBUS and the fixed rerun an abort. No parser conclusion is supported. **s765:** 6w landed, but two same-recipe soaks crashed before the `0x1E7C`/`0x1E8C` reachability window; controls were positive, so the null is unevaluable. **s764:** `0x1E7C` `$30`-return LIVE (`153==0x1C`); UJ 91→0; dest `0x12A0/20` stays LIVE; 4/4 `dl06=2/2/0`. E9 still not restored (12/64, still `src0=0x000178`, rdpFs plateau). Next: obtain one post-sec2 reachability result with a stability-oriented recipe before interpreting the parser chain. **s763:** `0x1ECC` `$30`-return LIVE. **s762:** `0x1EBC` `$30`-return LIVE. **s761:** `0x13C0` jal-`L_112C` return LIVE; ovl20 04-return class CLOSED. **s760:** `0x13B8` clip-hand LIVE. **s759:** ovl20 dest-`0x12A0` route LIVE. **s758:** overlay 0x20 is dest-`0x12A0` emit, not an E9 producer. **s757–s752:** ovl1c dest + jal-returns + `$30` pair LIVE. **s751–s748:** ovl10/18/14 LIVE. **s743:** ovl24+ovl28 route **stops the post-s739 UJ storm**. **s740:** resident-`0C` splice stops the section-2 `L_1DB0` reset.

   **s787 update:** the repeat had positive controls but died at VI 640 in RT64
   `findTileCopyId` before the 1024 gate. With s785's Metal barrier and s786's
   grid-allocation failures, this is the third distinct pre-chain family;
   next is a systematic `rs_malloc`/free-list writer audit before another
   reachability soak. **s788:** the source audit refuted stale generated view
   and separated s787's host-only zero-height tile-copy assertion from s786's
   malformed free-list consumption. It did not identify a writer common to
   all three families; do not add a grid or RT64 mitigation. **s789:** the
   bounded writer audit named RT64 `copyNativeToRAM` writeback of garbage
   `SETCIMG addr=0x1F0D74, width=1161` as the immediate writer for the s786
   malformed range; the six game-side allocator/header writers are normal
   bookkeeping paths. This selects H-freelist-writer for s786 and keeps s787
   disjoint; no mitigation was added.
- The s789 bounded writer audit enumerated all six active game-side free-list
  writers: `rs_malloc`, `rs_free`, `buildHeapFreeList`,
  `coalesceFreeHeapBlocks`, `rs_memset`, and `heapWalker`. The CMake manifest
  consumes that exact generated tree. Existing `[fl-zero-fault]` evidence
  names the immediate wild-range writer as RT64 `copyNativeToRAM` processing
  garbage `SETCIMG addr=0x1F0D74, width=1161`; the game-side writers perform
  allocator bookkeeping and no source writer explains that operand. This
  selects H-freelist-writer for s786's allocator corruption, with RT64 as the
  named writer, and keeps s787's zero-height tile-copy assertion independent.
  No mitigation is justified.

3. **M3 co-gates / legacy -374, -375, -378, -382..-384, -387, -393.** These are passive
   recurrence breadcrumbs, not reactive work: recovery-cell silence, one-off math/scene crashes,
   craft-shadow, `do_rom_read+608`, and the B8 ship gate. Enqueue self-contained soaks when a
   recipe adds information; pursue only a systematic idiom-class audit after recurrence.

4. **M4 correctness.** Outdoor `baseFixed=-32768` zero-shade, attribution S=0 triangles, then
   I4 `sample=64x128`; each needs an independently controlled experiment.

5. **Tooling / legacy -20.** Intermittent regeneration omission: delete generated `funcs_*.c`
   before regen and audit `fixup_game_funcs.py` counts. Escalate only with a reproducible case.

## Closed lineages — do not reopen

- **M5 audio (legacy -160..-230): CLOSED.** A new audio lead is required; see
  PROJECT-OVERVIEW §9–§12 and `docs/M5-AUDIO-PLAN.md`.
- **Hangar-exit → sec2 pipeline (legacy -349..-422): CLOSED except backlog item 1.** Product
  multi-header freelist restore is ON. `DROP_WRAP_RDP` and `DROP_GARBAGE_CIMG` remain OFF:
  suppressing the garbage SETCIMG writeback also suppresses recovery. The exact w=1161 CIMG was
  proven garbage after ring wrap, not a legitimate game command. Detail: PROJECT-OVERVIEW §27.
- **Idiom-class audits (legacy -231..-348): CLOSED.** The duplicate-symbol, frequency-scan,
  `DL_LIST_APPEND_GUARD`, and sibling/freelist campaigns are archived in PROJECT-OVERVIEW §13–§26.
  Do not revive an individual crash without a new class-level enumeration.

### Standing / open non-pipeline items

-20. **Regen-pipeline reliability bug (s120, intermittent).** `N64Recomp` skips rewriting existing
    `funcs_*.c`; delete all before every regen is mandatory but residual intermittency unknown.
    **Standing rule**: audit patch report for unexpected counts after every `fixup_game_funcs.py`.
    PORTING-STATE 120/121/126.

-11. **`advancePlayerAnimationPhase` SIGBUS: PARKED s89, RECURRED s424, GUARDED s425** (see -261).

-10/-9. **Metal-shader-compiler SIGSEGV** (s83, one data point). **s83 spline div0 guard**: 0/5
    fires; real fix by inspection, no same-run positive control yet.

-8. **`frameStartReset` SIGBUS** — 3 occurrences (s85/s108/s156); no located faulting insn.

-7. **M3 DoD gate.** Mission-entry pipeline is live through sec2; the only active blocker is
    backlog item 1. Product settings and the durable causal chain are in PROJECT-OVERVIEW §27.

-6. **(s53→s399) M4 `[missing-func]` addresses: DONE, CLOSED s399.** PORTING-STATE 399.

-5. Past first sustained mission hold: expect new failure classes (mission overlay DMA,
    missing-func/UJ, new VI phase, overlays 12/44, texture corruption). Each is its own unit.

-3. **Sibling-repo housekeeping (not autonomous):** `~/Documents/Tools/rogue_squadron64`
    carries uncommitted symbol-file edits. Ask user before committing there.

-2/-1. **Band-row coverage history** (settled s41-49). **GPU->CPU present PNG** via
    `NativeTarget::copyToRAM` — convenience, not a blocker.

**Done, do not redo:** optimising the ucode vector path (s38: `-O0`→`-O2` gave 41x); the
ucode-performance→DL-submission-collapse→RDP-census→draw-loss chain (s33-s37); coverage
attribution/format-mismatch (`LOG_BBOX`/`LOG_UPLOAD`); the s27-s31 I4-decode line.

## Regeneration and build pipeline

Game functions (s1) — all four steps, in order:

1. `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py`
2. `cd ~/Documents/Tools/N64Recomp && ./build/N64Recomp rogue_squadron.toml`
3. `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py` — **required**, re-applies hand-edits
   idempotently: `$zero` writes commented (~2700); `fake_func_*` → `__builtin_trap()`; cross-
   function branch traps; audio-engine gate stores → 0 in `funcs_23.c` for
   `setDisplayMode`/`reapplyDisplayMode` only (`initMusyXEngine` site reversed s302); `jr $t9`
   in `convertMat3x4ToN64Mtx` → plain `return`; `musyxKeyOnVoice` break 6/7 → early return;
   `evalCubicSplineAtTime` div0 guard (`[spline-div0]`).
4. `cd build && cmake --build . -j8`

RSP ucode (only when a ucode toml changes): `~/Documents/Tools/N64Recomp/build/RSPRecomp` on
`factor5_rsp.toml` / `factor5_boot_rsp.toml` → `build/factor5_ucode/*.c`, then
`tools/fixup_factor5_ucode.py`. **s47/s739: before the fixup, also run
`python3 tools/make_clip_composite.py [4|10|12|14|16|18|24|0x1C|28|0x20|32]` + RSPRecomp on
`factor5_rsp_ovl4.toml`, `factor5_rsp_ovl10.toml`,
`factor5_rsp_ovl12.toml`, `factor5_rsp_ovl14.toml`,
`factor5_rsp_ovl18.toml`, `factor5_rsp_ovl1c.toml`,
`factor5_rsp_ovl20.toml`, and
`factor5_rsp_ovl24.toml`**. `factor5b_rsp.toml`
is the **MusyX audio** ucode; stays in the build as a never-called artifact (s5).

Standing warnings:
- `lib/N64ModernRuntime` and `lib/rt64` carry **uncommitted working-tree patches** — never
  `git submodule update --force`. Mirror via `submodule-patches/export.sh`.
- ROM must sit next to the executable in `build/`; otherwise silent "place your ROM" dead VI (s8).
- Hand-edited diagnostics in `build/factor5_ucode/*.c` / `RecompiledFuncs` die on regen — put them
  in fixup scripts.
- settings.json Bash allowlist matches FIRST WORD: prefix env assignments with `env` (s44).
- Harness: `clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m`;
  capture with `tools/probe.sh` / `tools/regress.sh`. Kill with SIGKILL, not SIGTERM (s9).
  Python decoders: `scratch/venv/bin/python` (s18).
- `regress.sh` must not write probe images as `.*` hidden names (s26).
- ~~Screen Recording permission intermittent~~ — overturned s32: wrong window id, not permission.
- `winctl activate` ignored while another app holds focus — use `probe.sh`/`regress.sh`
  `raise_game()` (System Events `set frontmost`) instead (s45).

## Overturned conclusions — do not act on these

Full list (11+ entries spanning s2-s422, each with why it was believable and what refuted it),
plus the early-era dead-ends list: `docs/PROJECT-OVERVIEW.md` §26. Load-bearing for active work:
- **(s400-421→s422)** `0x800290d4` "six independent triggers" is `inflate_fast`'s clean return.
- **(M5-AUDIO-PLAN.md §4→s371)** host audio `queue_samples`→`SDL_QueueAudio` unit-mismatch, fixed s371.
- **(s578→s579)** post-exit `rdpFs` plateau is **not** the s178 graphics-task-submission stall —
  s178 is `stalled=1 pairs=0` + producer stop; s577 post-exit keeps submitting GFX with present
  FIRE pairs=4 while only FULL_SYNC dies (item -349).
- **(s715→s716)** zero `L_15AC` markers meant live TriGen bypassed the resident relay. This was
  believable because phase-6 summaries showed 9--15 live TriGen samples with no marker. It was
  refuted by s716's separate TriGen route budget: the live DMA word is `0x15AC` and every first
  route enters `L_15AC`, selector `0x0C`, then `L_1298→L_1DB0`; the old shared detail budget had
  already been consumed by other inline commands.

### Dead ends — labelled as such in the log, do not retry

Full list (early ucode/DMA/overlay hacks, s2b-s91) migrated to `docs/PROJECT-OVERVIEW.md` §26.

## Method traps

Mechanism already generalized in PROJECT-OVERVIEW.md §4 → pointer only here:
- §4.1 instruments-that-lie; §4.2 attribution errors; §4.3 cross-run comparison on animating
  scenes (gate on `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1`); §4.6 missing protocol events.
- Other instrument traps: PROJECT-OVERVIEW §8.
- **crash-signature blindness (s344)**: soak "any `[CRASH]`" is not evidence for a SPECIFIC target
  unless `last-guest-pc`/`pc-symbol` matches — ~20+ independent crash families. Also: grepping
  game `run.log` for driver `[keys]` is wrong (launcher log only). Item -200.
- **repeated-`last-guest-pc` is not repeated-bug proof outside the audited set (s595)**: only
  ~52/2499 functions track `g_rs64_last_guest_pc`. N identical addresses can be N different
  crashes sharing one instrumented caller. Check audited set before "Nth occurrence" escalation.
  Item -347.
