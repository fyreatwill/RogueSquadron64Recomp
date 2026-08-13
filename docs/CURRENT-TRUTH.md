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

## Current truth (reviewed through s823; compacted in maintenance s776)

The durable history for s2–s775 is in `docs/PROJECT-OVERVIEW.md` §§3–28 and
the chronological ledger. The active facts are:

- The s817 source audit found four generated callers of `runVideoFrameTick`.
  Its `lhu 0x4($s3)` reads the frame record's scalar field, not a pointer.
  The menu and mission callers populate their corresponding `+0x14` fields
  from table/state values immediately before the call. The two main-loop
  calls pass the static `D_80037560+0x10` record, but the generated tree has
  no writer for its corresponding `D_80037574` halfword. This selects
  intentional structured state for the dynamic callers but leaves the static
  record's ROM/data initializer unresolved; no legitimacy claim or mitigation
  follows. **s818 resolves it:** the section mapping places `D_80037560` at
  ROM `0x38160`; the ROM bytes at `D_80037574` contain the big-endian
  halfword `0x00E0`. The surrounding record contains the `mainGameLoop`
  pointer `0x8003DFA0`, and `getBootConfigField14` independently loads
  `lhu 0x7574($v0)` from this object. No generated absolute store targets
  the field. This selects **H-static-field-rom-intended** over a hidden
  runtime writer; it is not a mitigation or a claim about the later VI phase.

**s819 resolves the semantic role:** all 18 generated callsites of
`getBootConfigField14` are in seven routines covering vehicle/frame setup,
subtitle and sprite geometry, HUD scaling, and mission-transition overlays.
Each uses the returned `0x00E0` as a screen-height/display scalar: it is stored
in frame/overlay `+0x14` fields, converted for geometry ratios, or used in
screen-coordinate calculations. The only other generated `0x7574` literals
use bases `0x800A` or `0x800B` and are unrelated addresses, not
`D_80037574`. This selects **H-static-field-display-mode** over timing-state
and compatibility-accessor alternatives. No build, run, code change, or
mitigation was made.

**s820–s821 select H-authoritative-advance, repeated:** two independent valid
post-sec2 captures reached VI width 1024, passed their provenance controls, and
showed authoritative parser/full-sync advancement after the gate. s820 had
aligned `e9_b=29` and `rdpFs` 219→611; s821 had `e9_aligned=1` on task 545
and `rdpFs` 219→521, with sampled `[rdp-fullsync]` records. Both later ended
in the separate `slotDispatcherIter+872` SIGBUS family. This refutes a total
post-sec2 authoritative-dispatch loss, but not the remaining discrepancy
between abundant aligned-stream E9s and the authoritative count; no mitigation
or stability claim follows.

**s822 accounting-boundary audit selects H-different-populations:**
`e9_aligned` is produced by the inline-data-aware guest-DL walker in
`main.cpp`, only for selected tasks controlled by `ROGUESQ_LOG_DL_SYNC2` and
the phase/task sampling gates; it is stored on the current `g_e9prov` task and
then printed at task end. The `e9_a/e9_b` values are separate fixed-stride
guest-DL walk counts, not authoritative parser counts. The `rdpFs` value in
`[vi-fs-decision]` is `g_cumulative_fullsyncs`, a process-lifetime bridge
submission count: it increments for real size-8 E9 submissions and for
synthetic E9 submissions when `ROGUESQ_FS_PIPE_INJECT` is enabled, and is not
reset at task or phase boundaries. The authoritative advance ring is a
different diagnostic: it records parser commands only while
`ROGUESQ_LOG_RDP_ADVANCE` is enabled, resets at each LLE task start, and keeps
the latest 512 records. Therefore the s820/s821 `e9_aligned` versus `rdpFs`
rates cannot establish parser loss without a task-scoped join. No reset/cap
defect was found and no mitigation is justified.

**s823 task-scoped join selects H-join-defect:** the new bridge-submitted and
parser-side counters both passed the positive control in one run (`bridge=1`,
`parser=1` on tasks 1–4), but the first capture had no post-sec2 target rows
because the existing section latch tested table index 2 while the observed
start matches were sections 3 and 4. Changing the diagnostic latch to the
observed menu section 3 produced 124 positive sec2 provenance rows, but the
64-task latch window ended before later aligned-E9 tasks. Widening the join
logger to include any task with nonzero `e9_aligned` still produced no
`scope=aligned` join rows, despite `[dl-sync-probe2]` recording nonzero
`e9_aligned` on tasks 624–632. Both fixed captures reached VI 1024 and passed
the existing controls; both later hit the separate `slotDispatcherIter+872`
SIGBUS family. This proves the current callback/task ownership join is not
valid, and does not classify bridge/parser loss. No game logic or mitigation
was changed.

**s824 resolves the join defect:** source inspection found
`rs64_e9prov_task_end(task_serial)` at `src/main/main.cpp:658`, immediately
after `factor5_ucode` returns, while the inline-data-aware walker calls
`rs64_e9prov_aligned(task_serial, ...)` later at line 975. The LLE mutex covers
the runner and prevents another LLE task from overwriting `g_e9prov`; the
capture's 40 nonzero callback records all had `passed==current`, including the
positive controls. The corresponding task-join rows immediately before those
callbacks had `aligned=0`, proving the join was evaluated before the callback.
This selects **H-callback-order**, not global overwrite or serial mismatch.
VI 1024 was reached at 78.3s; the later 53-frame SIGBUS was the separate
`cutsceneDispatchSlotsByFlag+7288` / guest `0x8000834c` family. The telemetry
join must be reordered or split into post-callback reporting before parser-loss
interpretation. No game logic, parser accounting, or mitigation changed.

ORIGIN: the callback is emitted by the post-task guest-DL diagnostic walker;
the stale `aligned=0` row is produced by task-end telemetry before that walker.

Next work unit: make the smallest telemetry-only repair that records the
inline-walker result after `rs64_e9prov_aligned` returns (or defers the join
until that callback), keeping bridge/parser counters unchanged. Build once and
run `zsh scratch/agent/s790_postsec2_reachability.sh` with the existing
VI-1024 gate and positive controls. Expected discriminator: a post-callback
row with `passed==current` and `aligned>0` on the same task proves the join is
repaired; a mismatch or absent callback row reopens the ownership audit.

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
  sample or mitigation is justified. The next unit is a bounded pre-chain
  writer-attribution run.
- The s792 bounded writer-attribution unit ran the low-noise reachability recipe twice.
  Both attempts passed the provenance positive control (`emit=1`, `raw=1`,
  `dispatch=1`, `match=1`, four records) but stopped at VI 640 before the 1024 gate.
  The first timed out with 1,124 free-list faults, 21 writeback records, and one wild
  writeback/restore; the fixed repeat crashed in `viRetraceHandlerThread` with
  `si_addr=0x380000004`, after 388 free-list faults, 21 writeback records, and one
  wild writeback/restore. The aligned s785/s786/s787 records contain the immediate
  `hit=1` wild-writeback event for s786 but not for the Metal-barrier s785 or tile-copy
  s787 failures. This selects H-independent-writers for the known wild-writeback path,
  leaves parser reachability unevaluable, and justifies no mitigation.
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
  failure class, not a justification for a guard. The s791 source audit then
  found disjoint consumers; next is a bounded writer-attribution run.
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

The s801 VI audit and s819 static-field audit now precede parser work: the
port's game-side selector requests only 640 after the transition, while retail
independently reaches 1024; the static `0x00E0` field is a legitimate display
height. Resume parser reachability only with a post-sec2 phase-gated capture.

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

**s820–s821 parser result:** two independent valid post-sec2 captures reached
VI 1024 and showed authoritative `rdpFs`/FULL_SYNC advancement after the gate
(219→611 and 219→521). This closes the claim that authoritative advancement is
totally lost after section 2. The aligned-E9 versus authoritative-count
discrepancy remains open for source/telemetry accounting; the later
`slotDispatcherIter+872` SIGBUS is a separate crash family.

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
- The s790 low-noise reachability repeat passed same-run positive controls
  (`scope=control`, `emit=1`, `raw=1`, `dispatch=1`, `match=1`, four records)
  but died at VI 640 before the 1024 gate. It was a SIGBUS in
  `viRetraceHandlerThread` at `si_addr=0x380000004`, last guest PC
  `0x8000b650`, with 1,124 `[fl-zero-fault]` records. There was no post-sec2
  parser sample and no writeback/restore correlation. This selects
  H-prechain-transient for s790 and leaves H-parser-chain and H-writer-co-gate
  unevaluable; it adds a fourth distinct pre-chain family without naming a
  common writer or justifying mitigation.
- The s791 source audit classified the s790 `0x380000004` failure as an
  independent consumer, not a shared pre-chain idiom. `viRetraceHandlerThread`
  only dereferences fixed queue/global addresses; its `last-guest-pc=0x8000b650`
  is the existing stale `beginFrameDLChunk` stamp. The other recent failures
  are disjoint: s785 Metal barrier, s786 `rs_malloc` free-list use, and s787
  host-only RT64 tile-copy sizing. No active source or trace identifies a
  writer common to these consumers. This selects H-independent-consumers and
  leaves parser and writer-co-gate hypotheses unevaluable; no mitigation is
  justified. The s792 writer-attribution repeat found the same pre-gate family
  and independently recorded the wild-writeback split described above.

   **s792 writer-attribution update:** both low-noise attempts passed provenance controls
   but stopped at VI 640 before the 1024 gate. The immediate wild-writeback event was
   present in s786 and both s790 attempts, but absent from aligned s785 Metal-barrier
   and s787 tile-copy failures. This selects independent known writers; parser reachability
   remains unevaluable and no mitigation is justified. Next is one stability-oriented
   post-sec2 parser-chain capture.

   **s793 parser-chain update:** the first s790 attempt again timed out at VI 640,
   but its fixed repeat passed the same positive controls (4/4), reached VI 1024 at
   48.3s, and then produced 1,531 authoritative E9 dispatch records and 1,475
   `rdp-fullsync` records before a SIGBUS in `parseDatItemSubtypes1To5+3800`
   (`si_addr=0x380000000`, guest PC `0x800547bc`). The independent dispatch and
   State/fullSync counters advanced together, so this arm refutes
   H-parser-handler-loss; it does not distinguish authoritative-advance loss from
   a phase/co-gate because no aligned-walker E9 total was captured. No mitigation is
   justified. Next is a source/telemetry audit of the phase-5 E9 accounting boundary.

   **s794 accounting-boundary update:** the source audit found that the aligned
   count is sampled per selected task, whereas the authoritative advance ring is
   reset per LLE task and capped at 512 records. The s793 phase-5 log shows the
   authoritative dispatch and State/fullSync hooks advancing in the same parser
   chain. This selects H-measurement-scope, refutes no parser boundary, and
   justifies no mitigation. Next is one unified phase-5 counter capture.

   **s795 unified-capture update:** the new diagnostic built successfully and
   its final phase-gated run reached VI 1024, captured 18 frames, and had no
   crash. The same run passed four provenance positive controls and emitted four
   unified control rows with `fetched=1`, `handler=1`, and `state_fullsync=1`.
   The aligned walker independently emitted `e9_aligned=1` on those controls,
   but every unified row had `aligned=0` and `guest_dl=0xFFFFFFFF`. Two earlier
   attempts exposed and fixed task-sampling and handler-counter defects; the
   final result selects **H-parser-measurement / task-key join still broken**,
   not a parser-loss or phase-co-gate hypothesis. No parser conclusion or
   mitigation is justified. Next: trace the callback/task serial at both sides
   of the join and make the aligned value attach to the same task-end record.

   **s796 join-trace update:** callback-entry and task-end rows were added with
   both the passed and current task serials, plus a phase-scoped log budget.
   The build succeeded, but the prescribed run timed out after 180 seconds at
   VI 640; it emitted no aligned-walker or unified parser row, so the four
   parser controls were not exercised. This is an unevaluable pre-chain death,
   not evidence for callback-key mismatch, unreachable callback, or shared-state
   overwrite. No parser conclusion or mitigation is justified. Next: obtain a
   stable post-sec2 / VI-1024 sample with this instrumentation before interpreting
   the join rows.

   **s797 repeat:** two concurrent arms ran the join instrumentation for the
   full 240-second timeout and both remained at VI 640. They emitted 497/502
   ordinary E9-dispatch rows but zero provenance, unified, callback/task-end,
   or authoritative-advance rows. This repeats H-prechain-transient and leaves
   the join unevaluable; no parser conclusion or mitigation is justified.
   Next: one lower-volume stability capture retaining the join and positive
   controls.
   **s798 lower-volume repeat:** two concurrent arms used only the unified
   provenance/join/advance diagnostics and the same phase-gated key schedule.
   Both ran to the 240-second VI-1024 timeout at VI 640, with zero provenance,
   unified, callback/task-end, or authoritative-advance rows. The lower log
   volume did not recover the post-sec2 gate; this selects only
   H-prechain-transient for the tested recipe and leaves all join hypotheses
   unevaluable. No parser conclusion or mitigation is justified. The s799
   read-only audit found the launcher passed the intended
   `PROBE_PHASE_WIDTH=1024`, `PROBE_PHASE_TIMEOUT=240`, and phase-relative key
   mode, while both logs independently recorded the 0→320→640 VI sequence and
   no 1024 transition. This refutes H-recipe-gate and
   H-instrumentation-interference for the tested recipe and selects
   H-runtime-transition. The s800 stability-oriented capture was gated at VI
   640, reached that gate at 2.6 seconds, and then ran to completion with 90
   frames while remaining at width 640; it emitted no provenance, unified,
   callback, authoritative, or 1024-phase rows. This is a clean repeat of the
   runtime-transition result, not parser evidence. The next unit is a source
   audit of the VI-width transition writer and its gate, followed by one
   bounded writer-attribution capture only if the audit identifies a concrete
   candidate. **s801 source audit:** the port has one VI publication chain:
   game `osViSetMode` writes a pending `ViState::mode`, the VI thread's
   `update_vi()` copies `mode->comRegs.width` into `regs.VI_WIDTH_REG`, and
   the graphics thread consumes the prior-frame `ScreenUpdateAction` through
   `update_screen()`. The `[phase]` observer reads that same live register, so
   a published 1024 cannot be hidden by the renderer consumer. The s799 log
   shows calls #3–#6 after the 640 transition selecting only 640-wide modes;
   no 1024 `osViSetMode` request occurred. The immediate candidate is the
   game-side `selectAndApplyViMode` branch at `0x8001BB70–0x8001BBC0`, which
   selects from the `0x80128D50` mode table using globals at `0x8011A865–867`,
   rather than a host-side VI suppression. Retail ground truth reaches 1024
   at 17.3s driven and 49.7s undriven, so H-renderer-consumer is refuted and
   H-game-state is selected for the port recipe only. Next: one batched,
   phase-gated capture logging those selector bytes, selected mode
   pointer/width, and `osViSetMode` calls, with the oracle whole-RDRAM
   positive control plus VI trace retained as the independent control.

   **s802 selector trace:** retail ground truth passed the whole-RDRAM control
   (2,251,867 writes in 12s) and independently wrote the actual selector
   region `0x11A860–0x11A870` 24 times. The port probe build passed its
   `osViSetMode` positive control (six calls, including 640-wide modes), but
   neither the only generated caller at `0x800186C0` nor
   `selectAndApplyViMode` emitted its control marker. The selector function is
   therefore not reached in this tested 0→320→640 recipe; its null is not a
   selector-state result. The post-640 calls still select only 640-wide modes.
   This refutes the narrow claim that `selectAndApplyViMode` is the active
   writer on this path and pivots to the reachable direct mode callers/state
   gate. The source audit and runtime log are independent lines; no
   mitigation is justified. Correct the stale prose above: the generated
   MIPS computes selector addresses `0x8011A865–867` from `lbu -0x579B/-C/-E`.
   **s803 caller audit:** the generated tree has five `osViSetMode_recomp`
   callsites: `preNmiResetThread` at `0x80001764` (fixed OS VI data
   `0x80039790/0x80039330/0x80039BF0`), `initVideoSubsystem` at
   `0x8001B720` (conditional `0x80128E40/0x80128E90`),
   `applyPendingViChanges` at `0x8001B8DC` (conditional
   `0x80128E40/0x80128E90`), `swapBufferWithViMode` at `0x8001BB54`
   (`0x80128C90`), and `selectAndApplyViMode` at `0x8001BC28`
   (`0x80128C90` after copying one of its four 0x50-byte table rows).
   The sole selector caller is `freeRenderSubsystemResources` at
   `0x800186C0`; s802 proved that caller and selector are absent from the
   tested 0→320→640 path. Existing mode traces show the direct buffers are
   640-wide on the post-640 path, while the copied `0x80128C90` buffer is
   capable of carrying 320, 640, or 1024 depending on its source contents.
   This refutes the claim that the selector is the only 1024-capable route
   and selects the reachable direct-caller gate as the next target. No
   mitigation was added. Next: one batched, phase-gated callsite trace for
   `initVideoSubsystem`, `applyPendingViChanges`, and `swapBufferWithViMode`,
   retaining the existing `osViSetMode` logger and oracle positive control.
   The s804 result supersedes this as the active next step: audit the writers
   and state gates that populate the 640-only direct mode buffers.

   **s804 direct-caller trace:** the grounded oracle passed the whole-RDRAM
   positive control (2,251,959 writes) and independently wrote every candidate
   mode region. The port's same-run `osViSetMode` control fired six times and
   all three direct markers fired. After the 640 transition,
   `initVideoSubsystem` requested 640 from `0x80128E40`/`0x80128DA0`,
   `applyPendingViChanges` requested 640 from `0x80128DF0`, and
   `swapBufferWithViMode` requested 640 from `0x80128C90`; the selector marker
   stayed silent. The phase stayed at 640 for roughly 80 seconds without a
   crash before the capture process was SIGKILLed. This selects H-recipe-state
   for the tested recipe and refutes H-direct-caller and the narrow
   H-overlay-dispatch prediction that a direct marker would carry 1024; the
   state writer remains unidentified. No mitigation was added.

   **s805 source audit:** the four candidate direct buffers are rows in the
   ROM-backed `0x80128D50` mode table; the generated tree contains no later
   writer that can turn a 640 row into a 1024 row. `swapBufferWithViMode` and
   the unreachable `selectAndApplyViMode` are the only publishers into the
   copied `0x80128C90` buffer. The reachable direct callers select rows using
   stack/config bytes in `initVideoSubsystem`, pending masks at
   `0x80128E90`/`0x80128E94`, and selector bytes at `0x8011A862`/`0x8011A865–868`;
   `applyPendingViChanges` additionally gates publication on pending bits.
   This selects **H-state-gate** over H-mode-buffer-writer and
   H-missing-dispatch. The next unit is one batched marker at the reachable
   row-selection predicates, retaining all existing callsite, host VI, and
   oracle positive controls. No mitigation is justified.

   **s806 reachable-gate trace:** the oracle ground-truth arm passed the
   whole-RDRAM positive control (2,236,680 writes in 12 seconds) and
   independently recorded 24 writes to `0x11A860–0x11A870`; its VI trace
   remained at the expected 320 phase for this horizon. The regenerated port
   build passed its host VI/mode positive control and emitted six batched
   `[vi-gate]` rows. After the 640 transition, `initVideoSubsystem` selected
   `0x80128E40` at width 640, `applyPendingViChanges` selected `0x80128DF0`
   at width 640 with pending `0x00000000/0x00000011`, and a later
   `initVideoSubsystem` again selected a width-640 row; selector publisher
   controls remained silent. The source audit and same-run runtime trace are
   independent lines of evidence. This selects **H-state-gate** over
   H-mode-buffer-writer and H-missing-dispatch for the tested recipe; it does
   not identify the state writer or explain the retail phase divergence. No
   mitigation was added. Next: enumerate writers and state gates for the
   pending masks and selector/config bytes before another run.

   **s807 writer inventory:** a complete generated-tree audit found only three
   pending-mask store functions: `requestViFeatureChange` writes
   `0x80128E90` from `$a0`, `beginSceneRenderFrame` writes `0x80128E94`
   from `$a0`, and `clearPendingViChanges` plus the tail of
   `applyPendingViChanges` clear both words. Selector/config stores are in
   `setViewStateBytesAndFadeScale`, `setViewStateTripletBytes`, the video-state
   update routine at `0x80017C80–0x80017CEC`, and the feature-application
   branches in `applyPendingViChanges`; no other generated absolute stores
   exist. Callers of the two pending writers are enumerated across the
   generated tree (scene/render paths in funcs 9, 28–30, 33, 49), while the
   selector setters have callers in funcs 9 and 36. This rules out an
   unenumerated state writer and a post-table 640 overwrite, but source alone
   cannot classify which caller supplies the 640 values at the transition.
   H-state-writer remains selected; the next unit is writer attribution, not
   parser work or mitigation. No build or run was needed.

   **s809 request-mask classification:** the complete caller audit found seven
   direct `requestViFeatureChange` callers, but only `runMenuModelViewerScreen`
   at `0x800C2984` requests `a0=0x11`; the other callers request `0x17`, `0x1`,
   or `0x8`. In the same phase-gated port capture, the `0x11` request wrote
   pending mask `0x00000011`, and `applyPendingViChanges` consumed it and
   published `0x80128DF0` at width 640. Later, the 1024 transition came from
   `initVideoSubsystem` selecting `0x80128DA0`, with no second `0x11` request.
   Host `osViSetMode` and phase controls fired; 11 sec2 E9 provenance records
   carried `emit=1`, `raw=1`, `dispatch=1`, and `match=1`. The run then crashed
   in `slotDispatcherIter+872`, unrelated to the VI path. Source inventory
   plus same-run ordering selects **H-0x11-intended-640** and refutes
   H-0x11-misrouted; the later 1024 selection predicate remains open, so
   H-later-1024-route is not closed. No mitigation was added. Next: audit the
   reachable `initVideoSubsystem` row-selection predicate that produces the
   1024 mode, then capture that predicate with the existing controls.

   **s810 initVideoSubsystem predicate classification:** the source branch at
   `0x8001B6D8–0x8001B720` selects `0x80128DA0` when its gate
   `(stack[0x17F] < 1 || $fp != 0)` is true and `stack[0x15F] == 0`.
   The regeneration-safe probe printed those predicate values in the fixed
   phase-gated run: the later 1024 call observed `stack15f=0`, `stack17f=0`,
   `fp_nonzero=1` and selected `0x80128DA0`; the independent host decoder
   reported width 1024 for the same call. The run passed the host VI, phase,
   and E9 positive controls but later crashed in `slotDispatcherIter+872`
   (guest PC `0x80007904`). Source and same-run runtime evidence select
   **H-init-1024-intended** and refute H-init-state-misrouted. This does not
   identify where the argument state is populated or explain the retail phase
   divergence; no mitigation was added. Next: audit the reachable callers and
   argument-structure writers feeding `initVideoSubsystem`.

   **s811 argument-state audit:** the complete generated-tree inventory found
   exactly two reachable direct callers, both in `advanceVideoFrame` at
   `0x80018378` and `0x80018564`; no generated store targets the argument
   bytes at offsets `0x1EF`, `0x1F3`, or `0x1FF`. The first same-recipe capture
   reached 1024 and passed host-VI and E9 controls, but the existing probe did
   not record those bytes, so it was unevaluable for intended-versus-corrupt
   argument state. A regeneration-safe `[vi-arg]` probe was added to the
   fixup and both callsites. Four subsequent fixed-recipe attempts all died
   before the 1024 gate at width 320 in the same `initVideoBootWrapper+2196`
   / guest `0x80001C94` family and emitted no argument record. This is a
   pre-gate recurrence, not evidence about the argument bytes. The next unit
   is one successful phase-gated run with `[vi-arg]` enabled; no mitigation is
   justified.

   **s812 argument-state capture:** the fixed `[vi-arg]` recipe again died
   before the 1024 gate. It reported width 320, emitted no `[vi-arg]` or
   1024/E9 discriminator, and crashed in `initVideoBootWrapper+2196`
   (`si_addr=0x3800002CC`, guest PC `0x80001C94`). This is a second
   pre-gate recurrence in the same boot-crash family and is unevaluable for
   intended-versus-corrupt argument state; no mitigation or hypothesis
   classification is justified. Next: repeat the same bounded capture until
   a 1024-gated record is obtained.

   **s813 repeat:** both fixed `[vi-arg]` arms died at width 320 before the
   1024 gate, with no argument, phase, or E9 discriminator. Both had the same
   `initVideoBootWrapper+2196`, `si_addr=0x3800002CC`, and guest PC
   `0x80001C94` signature. This is a third stalled iteration on the
   argument-state slug, so the capture hypothesis is not classified and no
   mitigation is justified. Pivot next to a bounded source audit of the
   `0x80001C94` crash site and its immediate state/allocator accesses.

   **s814 source audit:** the two s813 logs have the same host fault operands
   (`x9=0x800002CC`, `si_addr=0x3800002CC`) and both stop before any `[vi-arg]`
   line. In the current generated source, `initVideoBootWrapper+2196` maps to
   the diagnostic probe's `MEM_BU(0x1EF, ctx->r5)` evaluation, not to the
   `0x80001C94` return path. The probe's address transform maps the observed
   fault to `ctx->r5=0x800000E0`; its dereference becomes the host address
   `0x3800002CC`. The `0x80001C94` stamp is stale state left by the nested
   `rs_malloc` return. This selects **H-boot-crash-host-translation** in the
   narrower probe-side-access sense, and does not establish that the game's
   caller structure is malformed. Next: replace the probe's speculative byte
   dereferences with pointer-only logging in the regeneration fixup, rebuild,
   and run one bounded phase-gated capture with the existing positive controls.
   No mitigation to game logic was added.

   **s815 pointer-only probe capture:** the fixup removed the three speculative
   `MEM_BU` reads from `[vi-arg]`, and the regenerated build applied both
   callsites once. The first capture omitted `ROGUESQ_LOG_VI_ARGS` and was
   invalid despite positive phase/E9 controls; the corrected rerun reached
   width 1024 at 79.5 seconds, produced four positive E9 provenance controls,
   and emitted five pointer-only records (`ptr=0xE0`, `0x1E0`, `0x154`,
   `0x1C0`, `0x154`) with no probe fault. It completed 300 seconds / 89
   frames with zero crash markers. This supports **H-probe-only** for the
   s813 pre-gate crash, but does not establish caller-structure legitimacy;
   all recorded `ra` values were zero. **s816 source audit:** both direct calls
   pass `a1` from `advanceVideoFrame`; its main and secondary call paths retain
   the caller's second argument as the value passed to `initVideoSubsystem`.
   The only reachable `advanceVideoFrame` caller, `runVideoFrameTick`, builds
   that argument from `lhu 0x4($s3)` where `$s3` is its frame-structure `a0`,
   then sign-extends it to 16 bits. The observed `0xE0`, `0x1E0`, `0x154`, and
   `0x1C0` values are therefore scalar frame-state values, not guest
   structure pointers. This selects **H-pointer-is-small-offset** over
   H-pointer-is-guest-structure and H-caller-state-stale for the observed
   origin, while the field's semantic producer remains open. No code or
   mitigation was added. **s818 resolves the static producer:** the ROM
   mapping places `D_80037560` at ROM `0x38160`, whose `+0x14` halfword is
   `0x00E0`; `getBootConfigField14` independently reads `0x80037574`, and
   no generated absolute store targets that field. This selects
   H-static-field-rom-intended and refutes a hidden runtime writer for this
   field. Next: enumerate `getBootConfigField14` callers and remaining
   `D_80037574` uses to classify the scalar's semantic role, source-only.

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
