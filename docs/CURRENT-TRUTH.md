# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and evidence remain in the ledger and `scratch/agent/`.

Current maintenance marker: Session 3273 (2026-08-29).

Session 3273 ran the prescribed independent retail target-writer capture.
The whole-RDRAM positive control, title `1024 @ 0x00790400`, hangar
`512 @ 0x006AB400`, and one target-phase row all passed. The selected
metadata-span watch had 24 target-phase writes from `0x80094648`, but every
row was the sentinel `0x7F7F7F7F` at `0x00141AD8..0x00141AEC`; the requested
`0x8008EB8C` and `0x8008EBBC` PCs had no target rows. The non-sentinel table
was `0/16` for all three PCs, so the driver selected
`H-TargetRowsInsufficient`. This is a valid single-source instrument result,
not evidence that the retail target writer is absent: the watch covered a
metadata field rather than the target framebuffer. No port or audio behavior
changed. Evidence: `scratch/agent/s3273_m5_route_boundary.md` and the
`s2297_m5_target_only_writer_sequence` capture.

Session 3272 ran the required M5 Step 1 same-build image-versus-silent pair.
The independent retail oracle passed the whole-RDRAM 10,000-write control and
reached title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`. Both port
arms visibly dispatched their selected audio arm, but neither reached title
or hangar; both stopped at pre-title `640 @ 0x0066A500` and later emitted
off-target `640 @ 0x00696100`. No downstream audio rows are interpretable.
This selects `H-RouteInvalid` for Step 1, not an audio-contract gap. Evidence:
`scratch/agent/s3272_m5_step1_pair.md` and the captured pair directory.

Session 3271 re-attempted the prescribed validation of the Session 3270
free-list guard class. `cmake --build build --config Debug --target
PatchesLib` still exits immediately with `No rule to make target PatchesLib`;
the cache points at `E:/mips-toolchain`, no local MIPS compiler/linker is
installed, and `RecompiledPatches/` is absent. This selects
`H-GuardBuildUnavailable` for this checkout only. No guard compilation,
valid-path execution, or cyclic-chain fixture ran, so no guard behavior or
VI/audio conclusion follows. Evidence:
`scratch/agent/s3271_guard_validation.md`.

Session 3270 completed the next M3 free-list/active-queue guard-class change
in `patches/heap_guards.c`. The existing KSEG0 predicate now also rejects
misaligned guest pointers, and the fresh free-chain walk aborts after the
maximum possible number of 0x100-byte blocks in RDRAM, closing the cyclic-list
spin path before queue mutation. ORIGIN: `func_80007D74` consumes pointers
published by the guest allocator and active-queue metadata; their legitimacy
was not independently proven, so this is a safety guard, not an explanation
of the VI-640 or audio route. The configured local `PatchesLib` target still
does not exist (`make: No rule to make target PatchesLib`), so compile/runtime
validation remains pending on the Windows/MIPS host. Evidence:
`scratch/agent/s3270_m3_free_list_guard.md`.

Session 3269 ran the prescribed independent retail scheduler identity
capture. The whole-RDRAM write control reached 10,000 hits; the run reached
title origins `0x00790400/0x00790800`, hangar origin `0x006AB400`, and 3,565
VI frames. `0x80019CD0` executed 7,900 times from `0x80019CCC`, including
target-origin rows, but this watch interface exposed only stable queue/context
registers (`a0=0x8011A420`, `a1=0x8011D460`, `s1=1`) and no accepted-message
pointer, type, or `89F/28D44` identity. This selects
`H-RecvWatchUnavailable` as a valid single-source instrument result; message
mutation, another task type, and type-2 absence remain unresolved. Evidence:
[`s3269_scheduler_identity.md`](../scratch/agent/s3269_scheduler_identity.md)
and `scratch/agent/s3269_scheduler_identity.log`.

Session 3268 ran the prescribed independent retail aligned selector-region
capture. The whole-RDRAM write control reached 10,000 hits; the run reached
the 640-wide phase and produced 3,569 VI frames. The widened selector region
`0x00114A800..0x00114A900` had zero reads, while pending state had 23,704
reads and the watched boundary PCs executed 3,764 times. This selects
`H-SelectorNotReadInObservedPhases` as a single-source instrument result
only; it does not explain the port boundary or prove the selector is dead.
Evidence: `scratch/agent/s3268_selector_region.md` and its capture log.

Session 3267 ran the prescribed independent retail aligned selector-read
capture. The whole-RDRAM write control reached its 10,000-hit cap, and the run
reached title VI 1024 and hangar VI 512. The selector range
`0x00114A864..0x00114A86C` had zero reads, while pending state
`0x00128E94..0x00128E9C` had 23,720 reads and the watched boundary PCs ran
3,766 times. This selects `H-SelectorWatchUnavailable` as an instrument
result, not a runtime explanation: `H-RequestState`, `H-BoundaryConsumer`,
and `H-Phase4SteadyState` remain unresolved. Evidence:
[`s3267_vi_selector_aligned.md`](../scratch/agent/s3267_vi_selector_aligned.md)
and `scratch/agent/s3267_vi_selector_aligned.log`.

Session 3266 ran a new independent retail read-watch capture for the VI-640
request-state edge. Both the generic 180-second and fixed 60-second runs
passed the whole-RDRAM positive control and reached title 1024 plus hangar
512. The fixed run observed 23,594 reads of pending state
`0x80128E94/98`, with detailed PCs inside `applyPendingViChanges` and its mode
helpers, but zero reads of selector bytes `0x8011A865..67`; those reads may be
aligned word loads and are therefore unevaluable, not absent. The oracle still
does not print read values or phase labels, so `H-RequestState`,
`H-BoundaryConsumer`, and `H-Phase4SteadyState` remain unresolved. No port or
audio behavior changed. Evidence: [`s3266_vi_request_state_reads.md`](../scratch/agent/s3266_vi_request_state_reads.md)
and its two captured logs.

Session 3265 ran the required independent retail VI request-state capture.
Both runs passed the whole-RDRAM positive control. The fixed phase-gated run
reached VI 640 origin `0x0066A500`, title 1024, and hangar 512; it observed
`applyPendingViChanges` 2,266 times, all from caller `0x80019914`. This proves
the producer is live at the VI-640 boundary, but the oracle exposes only entry
registers, not the function's internal state loads or successor branch.
`H-RequestState`, `H-BoundaryConsumer`, and `H-Phase4SteadyState` therefore
remain unresolved. No port or audio behavior changed. Evidence:
`scratch/agent/s3265_vi_request_state.md` and its two captured oracle logs.

Session 3264 repeated the bounded availability audit for the VI request-state
edge. `RecompiledFuncs/` remains absent; `applyPendingViChanges` is still
available locally only as symbol metadata (`0x8001B7F0`, size `0x2AC`) and the
probe template's expected caller (`0x80019914`). The host VI wrappers cannot
expose the function's state loads or branch successors. This selects
`H-SourceUnavailable` for the local checkout and leaves
`H-RequestState`, `H-BoundaryConsumer`, and `H-Phase4SteadyState` unresolved;
no build or runtime instrumentation was run. Evidence:
[`VI640-REQUEST-STATE-BLOCK.md`](VI640-REQUEST-STATE-BLOCK.md).

Session 3263 repeated the bounded availability audit for the VI request-state
body. `RecompiledFuncs/` is absent; `applyPendingViChanges` exists locally
only as symbol metadata (`0x8001B7F0`, size `0x2AC`) and the probe template's
expected caller (`0x80019914`). The host VI wrappers cannot expose the
function's state loads or branch successors, so `H-RequestState`,
`H-BoundaryConsumer`, and `H-Phase4SteadyState` remain unresolved. No build or
runtime instrumentation was run. The next satisfying input is the generated
body/provenance or an independent retail trace of its state inputs. Evidence:
[`VI640-REQUEST-STATE-BLOCK.md`](VI640-REQUEST-STATE-BLOCK.md).

Session 3262 audited the local VI-640 publication boundary. The host wrappers
only forward/observe `osViSetMode` and consume committed VI registers; the
generated `RecompiledFuncs/` tree containing `applyPendingViChanges` is absent,
and the only local reference is the regeneration probe's expected call site at
`0x80019914`. The function's state loads and branch successors are therefore
not locally enumerable, so `H-RequestState`, `H-BoundaryConsumer`, and
`H-Phase4SteadyState` remain unresolved. No build or instrumentation was run;
the next satisfying input is the generated body or an independent ground-
truth trace of its state inputs. Evidence: [`VI640-BOUNDARY-AUDIT.md`](VI640-BOUNDARY-AUDIT.md).

Session 3261 audited and captured the pre-target VI publication boundary. The
positive-controlled run entered phase 4 at width 640/origin `0x0066A500`, then
made exactly one further `osViSetMode` call from `applyPendingViChanges`, again
requesting width 640. Scheduler receive progress and route preparation
continued, but no target-mode request or target origin appeared during 60 s.
This selects `H-BoundaryProducer` at the VI-mode publication edge, rules out a
producer-wide stop and an explicit phase-4 terminal contract, and leaves the
upstream state/writer that should request the target mode unresolved. Evidence:
`scratch/agent/s3261_vi640_boundary.md` and
`scratch/agent/s3261_vi640_boundary.log`.

Session 3260 ran the repaired scheduler identity capture from the actual Unix
`build/` output (the documented `build/Debug` directory is absent). Positive
controls fired, and accepted phase-2 rows contained valid message pointers,
types `0x02/0x01/0x81`, and `89F/28D44`. The port then remained at phase 4
width 640/origin `0x0066A500` for the full 60-second run, with no crash
markers, and never reached the target VI-640 wall. The target-phase type-2
discriminator is therefore unevaluable; no scheduler or audio behavior
changed. Evidence: `scratch/agent/s3260_scheduler_identity.md`.

Session 3259 compared the available external regenerated scheduler body with
the Debug binary and found a fourth case outside the prior scheduler
hypotheses: the `s2948` diagnostic itself evaluated `MEM_HU(ctx->r17, 0x22)`
after `r17` had legitimately been set to state value `1` at `0x80019C84`.
The original `0x80019CD8` instruction only loads the received message pointer;
the extra halfword read generated the reported Bus error at
`spTaskSchedulerThread+2864`. Applying the existing regeneration-preserved
KSEG0 guard for the diagnostic source reads rebuilt successfully, and a
30-second `ROGUESQ_LOG_ALL=1` run emitted no crash, abort, Bus-error,
access-violation, or `last-guest-pc` marker. This rules out the current
missing-marker, compiler-drift, and baseline-crash interpretations at this
fault site, but does not identify the target-phase message. Evidence:
`scratch/agent/s3259_scheduler_probe_origin.md`.

Session 3258 audited the checked-in host scheduler path and Debug binary. The
faulting generated instruction is an ordinary guest-RDRAM `MEM_HU(0x22, r17)`
load at the `spTaskSchedulerThread` host symbol; the runtime SP queue path has
no matching host-pointer dereference. Because the external regenerated
`RecompiledFuncs/` tree and fixup markers are absent, the producer and
legitimacy of `r17` cannot be classified locally. This rules out the checked-in
host queue contract as the identified fault but selects none of
`H-Regeneration-Missing-Patch`, `H-Regeneration-Compiler-Drift`, or
`H-Port-Baseline-Crash`. No guard or scheduler behavior change is authorized.
Evidence: `scratch/agent/s3258_scheduler_contract_audit.md` (single-source
binary mapping plus checked-in runtime source).

Session 3257 ran the checked-in Debug baseline with the scheduler identity
hook disabled. The build succeeded, but the process reproduced the early Bus
error at `spTaskSchedulerThread+2864` before VI 640 (width 320 was the last
phase row; fault address `0x380000021`, last guest PC `0x8000834C`). The
external regenerated N64Recomp tree and its marker set are not mounted here,
so this confirms the local control crash but does not distinguish missing
fixup markers, compiler drift, and an inherent baseline crash. Evidence:
`scratch/agent/s3257_baseline_scheduler.md`.

Session 3256 added a regeneration-preserved post-return scheduler identity
capture at `0x80019CD0`. The independent retail oracle passed its whole-RDRAM
positive control and executed that call site 7,620 times through title and
hangar. The port emitted one valid pre-target row (`msg=0x80112AE0`, type 1),
but both instrument and disabled-hook control runs crashed in the regenerated
tree at the same 320-phase scheduler location. Required VI-640 coverage is
therefore invalid; no scheduler hypothesis is selected and the row must not be
used to claim target-phase type-2 absence. Evidence:
`scratch/agent/s3256_scheduler_identity.md`.

Session 3255 ran the scheduler receive-type discriminator. The existing
`ROGUESQ_RECV_TRACE` controls fired, but the new type field was unevaluable:
the wrapper saw `$a1=0`, and the queue snapshot was empty because external
messages are delivered inside `osRecvMesg` after the pre-call copy. The port
reached VI 640 `0x0066A500`, not title 1024. No type-2 hypothesis is selected
and no scheduler/audio behavior changed. Evidence:
`scratch/agent/s3255_vi640_recv_type.md`.

Session 3254 completed the M3 `func_80007D74` free-list dequeue/active-queue
pointer audit and landed a guard-class change in `patches/heap_guards.c`.
Every dereference of the allocator-returned chain, published successor, queue
metadata slot, tail node, and tail successor now has a KSEG0 check; invalid
metadata returns before queue writes, and an invalid successor is cleared from
the free-list head. The valid path remains equivalent in intent. ORIGIN:
`func_80007D74` consumes guest-owned allocator and queue pointers; their
legitimacy was not independently proven, so this is a safety guard rather than
an explanation of the hangar defect. The configured `PatchesLib` build still
fails before compilation with `No rule to make target PatchesLib` because this
checkout lacks the configured MIPS/generated-patch prerequisites. Evidence is
single-source static audit plus the exact build failure; runtime guard
validation remains pending on the configured Windows/MIPS host.

Session 3253 ran the independent retail oracle with a whole-RDRAM positive
control and target 1024 gates. `0x8008EC88` executed once only at the
1024-to-512 transition, with `$a0=0x1B0` and live origin `0x006AB800`; it did
not execute at `0x00790400` or `0x00790800`. This selects
`H-TargetStoreMisaligned`, rules out candidate absence, and leaves the exact
target writer unresolved. The existing port record shows this store is
already the nonzero C88 default, so no port or audio behavior changed.
Evidence: `scratch/agent/s3253_retail_target_store.md`.

Session 3252 ran the independent retail oracle with a whole-RDRAM positive
control and watched `reapplyDisplayMode` entry/call/return. All three PCs
executed twice, but only at 1024/origin `0x006AB800` and 512/origin
`0x006AB400`, after the target title transition at `0x00790400/0x00790800`.
The explicit target-phase join produced zero rows. This selects
`H-RetailWriterMisaligned`, rules out candidate absence, and requires a new
target-boundary writer angle; no port or audio behavior changed. Evidence:
`scratch/agent/s3252_retail_route_writer.md`.

Session 3251 reran the exact configured `PatchesLib` build and confirmed the
same external block: the target inventory has no `PatchesLib`, neither MIPS
tool is installed, and `RecompiledPatches/patches.c` is absent. This is the
third stalled guard-host attempt in the current thread, so the next unit
pivots to the existing retail pre-title route-state writer boundary. No M5
Step 3 validation or audio/guard behavior change was performed.

Session 3250 reran the exact configured `PatchesLib` build. It exited 2
immediately with `No rule to make target PatchesLib`; the cache still points at
`E:/mips-toolchain`, and this checkout has no MIPS compiler/linker or generated
`RecompiledPatches/patches.c`. The M5 Step 3 runtime validation therefore did
not run. This confirms `H-GuardHostMissing` for the local environment, not the
guard's behavior; no audio or mitigation change is authorized.

Session 3249 completed the build-independent MusyX status-03 idiom audit.
The generated snapshot has a legitimate status-03 publisher in
`stopVoiceSlotSynced` (`0x8009B30C`) and a named service consumer/reaper in
`serviceVoicePoolFrame` (`0x8009B680` → `0x8009B7EC`), with a second legitimate
streaming publication at `0x8009B7CC`. `shutdownMusyXVoices` is a waiter over
that contract, not an unexplained publisher. This selects
`H-Status03NamedContract`; the status-03 wait hatch remains authorized and no
guard, force-clear, or audio behavior change is justified. Evidence:
`scratch/agent/s3249_m3_status03_audit.md`.

Session 3248 proved the guard-build block is an external dependency and
re-scoped the loop. The exact `PatchesLib` build still exits 2 because this
Unix checkout has no target, MIPS GCC/LD, or generated Rogue Squadron patch
output; the CMake source confirms those prerequisites are required. The
sibling Starfox generated patch artifact is not a valid substitute. This is
not guard evidence and does not authorize M5 Step 3, but it no longer stops
the loop. The next unit is a build-independent complete static audit of the
MusyX status-03 publication/consumer idiom class.

## Current state

The native port builds and boots through attribution, the N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) on the validated spin-yield/F5-LLE route. Hangar visuals
still have geometry/color artifacts. Audio is not production-complete: the
Factor 5 image task is the qualified real-audio arm and `musyx_stub`/Broke is
the silent control.

Session 3244 re-attempted the prescribed guard validation. The configured
Unix build has no `PatchesLib` target, its cache points at the unavailable
`E:/mips-toolchain`, and `RecompiledPatches/patches.c` is absent. This is an
environment block, not evidence for or against the guard. M5 Step 3 remains
gated behind a successful MIPS/generated-host validation.

Session 3245 tested the block's alternatives. The checked-in N64Recomp binary
accepts a TOML config path, not a help-mode substitute for the patch pipeline;
the CMake source creates `PatchesLib` only when MIPS GCC, the configured
N64Recomp executable, and make all exist. The exact target build still returns
`No rule to make target PatchesLib`; no local `mips64-elf-*` toolchain or
generated `RecompiledPatches/patches.c` exists. Route 3 therefore re-scoped the
next unit to a build-independent port-side VI/output-boundary audit. The guard
validation remains an open external dependency and M5 Step 3 remains gated.

Session 3246 completed that audit. The source has a target-row logger and the
same-build image/silent artifacts both pass the VI positive-control logger but
stop at width 640/origin `0x0066A500`; neither emits the target row. Retail's
independent target relation is caller `0x8001BE24`, `$a0=0x80790000` (physical
`0x00790000`), with origins `0x00790400/0x00790800`. This selects
`H-PortRowMissing`, not a like-for-like mismatch: the port relation is
unevaluable until it reaches the target phase. No M5 output/audio behavior
change is authorized. Evidence:
`scratch/agent/s3246_m5_port_vi_boundary_audit.md`.

Session 3247 retried the configured `PatchesLib` build. It returned `No rule to
make target PatchesLib` (exit 2); the cache still points to `E:/mips-toolchain`,
and this checkout has neither a `PatchesLib` target nor generated
`RecompiledPatches/patches.c`. This selects `H-GuardHostMissing`, is not guard
evidence, and blocks M5 Step 3 pending the configured Windows/MIPS host.
Evidence: `scratch/agent/s3247_guard_validation.md`.

Session 3241 supplied a new target-phase retail output relation: the
independent oracle's `osViSwapBuffer` edge (`0x80035500`) runs from caller
`0x8001BE24` with framebuffer `$a0=0x80790000` (physical `0x00790000`) while
the target VI alternates `0x00790400/0x00790800`. The whole-RDRAM positive
control, title, and hangar gates all passed. This selects a target-phase
`H-PortBoundary` comparison, but is single-source oracle evidence and does
not yet authorize a port behavior change. The next unit must compare this
relation with the port's corresponding swap/output row before any M5 Step 3
change.

The latest same-build M5 image-versus-silent qualification (Session 3235)
passed dispatch controls in both arms but reached only pre-title VI 640
(`0x0066A500`). Independent retail controls reached title and hangar. Thus all
target-phase audio/task/DMA/service/slot/voice/MORT/PCM nulls are unevaluable;
no audio, route, VI, gate, wait, voice, destination, or output change is
authorized without a named legitimate writer and ordering edge. Do not remove
the status-03 wait hatch.

## Next steps

Priority is maintenance, M5 de-stubbing, systematic M3, then generated-symbol
renaming. M5 design is complete in `docs/M5-AUDIO-PLAN.md`. Session 3273
reached the retail target phase but its metadata-span/candidate-PC table was
insufficient: only sentinel housekeeping from `0x80094648` was observed.
The next M5 unit must watch the actual target framebuffer span and adjacent
generated-PC range in one independent retail run; do not infer writer absence
or change audio behavior. Session 3272
made the Step 1 pair route-invalid again: retail reached title/hangar, while
both port arms stopped before title at `640 @ 0x0066A500`; downstream audio
nulls remain unevaluable. The next M5 unit is a route-boundary audit or
ground-truth capture that can make the port reach a like-for-like target row;
do not change audio behavior or interpret the missing joins. Session 3236
completed the Step 3 edge-selection gate without selecting an edge: the
required target-phase port row is still absent, so no audio behavior change
is authorized. Session 3237's fresh census selected a new unresolved repeated
MusyX pointer class; Session 3238 split it by effective address. Four NPC-list
uses are `0x80139750` and one objective float is `0x800A9750`, both aliases.
The true MusyX chain has allocator writer `0x8008F228`, derived-head writer
`0x80091074`, indexed command-list/synth consumers, and teardown frees at
`0x80091E28`/`0x80091F78`. `rs_malloc` returns zero on its no-fit path and
the allocation publication has no success check, selecting a possible null
consumer. Teardown's missing visible clear and any post-free/concurrent
consumer remain unresolved. Session 3240 audited the complete
`musyxBuildVoiceCommandList` loop and caller: the selected pointer is
dereferenced at `0x80091078` before the voice loop, and the caller has no
error/reinitialization contract. `H-NotPatchable` is selected for this class;
no patch or allocator mitigation is authorized. Evidence:
`scratch/agent/s3240_m3_musyx_null_contract.md`.

1. Watch the actual target framebuffer span `0x00790000..0x00790C00` and the
   adjacent generated-PC range `0x8008EB00..0x8008ED00` in one independent
   retail run. Include the whole-RDRAM positive control, title/hangar gates,
   and a phase writer histogram for the target span. A target-phase write with
   an attributable PC selects a legitimate writer candidate; a live target
   phase with no target-span writes selects an unresolved upstream/output
   boundary; missing controls invalidate the run. This replaces the
   metadata-only `H-TargetRowsInsufficient` capture and authorizes no M5
   behavior change by itself.
2. Obtain the configured Windows/MIPS build artifact or generated patch
   outputs, then validate Session 3270's expanded free-list guard class.
   Require successful patch compilation, unchanged valid-path behavior, and a
   controlled cyclic-chain fixture that returns before queue writes. This
   guard is not evidence that the VI-640 route or audio is corrupt.
3. Capture the consumed-message handoff around generated `0x80019CCC` and
   `0x80019CD0` with positive controls. Session 3269 reached both target
   origins and proved the receive watch live, but its interface exposed no
   message pointer/type/`89F`/`28D44` fields, selecting
   `H-RecvWatchUnavailable`. Use adjacent-PC detail plus a phase-gated field
   dump in one run; do not infer message mutation, another task type, or
   type-2 absence from the missing fields.
4. Capture retail scheduler message identity at generated `0x80019CD0` with
   positive controls. Session 3268 widened the selector watch to
   `0x00114A800..0x00114A900` and still saw zero reads, while pending state and
   boundary PCs were live; this selects `H-SelectorNotReadInObservedPhases`
   only and moves the investigation upstream. A target row with type `0x02`
   and anomalous `89F/28D44` selects `H-SpMsgMutated`; another valid type
   selects `H-OtherOsTask`; a valid target wall with no type-2 row selects
   `H-Type2AbsentAtRecv`. Missing target correlation remains unresolved.
   Do not add a port field or change audio behavior.
4. After the boundary audit, capture the scheduler message identity at the
   generated `0x80019CD0` receive call site with positive controls. A type-2
   target row selects `H-SpMsgMutated`; a valid non-type-2 target row selects
   `H-OtherOsTask`; a valid target wall with no accepted type-2 row selects
   `H-Type2AbsentAtRecv`.
5. Repair or explain the pre-VI-640 scheduler crash before capturing message
   identity. Session 3257's checked-in control build reproduced a Bus error
   at `spTaskSchedulerThread+2864` after width 320, with
   `last-guest-pc=0x8000834C`; it reached no VI-640 wall. The external
   regenerated tree and marker set are unavailable in this checkout, so do
   not claim missing-marker or compiler-drift selection from this run. The
   next discriminator must inspect the host scheduler source/register
   contract and identify one safe, testable distinction between the invalid
   guest-derived value and a legitimate scheduler message/slot before any
   mitigation is landed. Preserve the existing competing hypotheses in
   `scratch/agent/NEXT.md` and do not repeat the local baseline until a new
   code-level discriminator is prepared.
   After the crash is repaired or explained, capture the scheduler message
   identity at the generated `0x80019CD0` receive call site (or expose the
   runtime's consumed-message value), with `ROGUESQ_RECV_TRACE` positive
   controls. Require a caller identity, message pointer, type byte, and
   `89F/28D44` in the same phase before selecting `H-SpMsgMutated`,
   `H-OtherOsTask`, or `H-Type2AbsentAtRecv`.
3. Validate Session 3254's complete free-list guard class on the configured
   receive call site (or expose the runtime's consumed-message value), with
   `ROGUESQ_RECV_TRACE` positive controls. The wrapper-level `$a1`/queue
   snapshot probe from Session 3255 is unevaluable because external delivery
   occurs inside `osRecvMesg`; do not interpret its zero type rows. Require a
   caller identity, message pointer, type byte, and `89F/28D44` in the same
   phase before selecting `H-SpMsgMutated`, `H-OtherOsTask`, or
   `H-Type2AbsentAtRecv`.
   Session 3256's hook is present in the fixup path, but the regenerated tree
   crashes in the 320 phase even with the hook disabled. First repair or
   account for that regenerated-tree regression; do not repeat the capture
   until the port reaches the VI-640 wall.
2. Validate Session 3254's complete free-list guard class on the configured
   Windows/MIPS host, then run the bounded M5 Step 3 gate only if the build
   produces `RecompiledPatches/patches.c`. The exact local build remains
   unavailable and must not be repeated until that host or generated artifact
   is supplied. The guard change is not evidence that the free-list values are
   corrupt; its ORIGIN is the guest allocator/queue publication contract.
   The existing M5 target-row comparison remains `H-PortRowMissing`: the
   image/silent pair has a valid VI control but no target row. Require the
   target framebuffer physical address, VI origin, caller/order, and
   image-versus-silent distinction before any M5 behavior change.
2. Once the external guard validation is available, resume the target-phase
   port/retail boundary work with a like-for-like target framebuffer row.
   The current comparison is `H-PortRowMissing`: the existing image/silent
   pair has a valid VI control but no target row. Require the target
   framebuffer physical address, VI origin, caller/order, and
   image-versus-silent distinction before any M5 behavior change. Only a
   like-for-like mismatch or a newly proven legitimate writer/consumer edge
   can authorize Step 3.
   Session 3241's retail row is caller `0x8001BE24`, `$a0=0x80790000`
   (physical `0x00790000`), target origins `0x00790400/0x00790800`, with the
   whole-RDRAM positive control and title/hangar gates valid. This is
   single-source oracle evidence pending the port-side line.
   The guard build is currently an external dependency; the port-side audit
   may proceed independently, but no M5 behavior change is authorized until
   the guard validation is obtained.
   Session 3248 proved the local dependency is real and re-scoped active work
   to the status-03 idiom audit in `scratch/agent/NEXT.md`. Do not substitute
   the sibling Starfox generated patch artifact, Clang, or the host-only
   `build/N64Recomp` binary for this validation.
   The one satisfying experiment remains the exact `PatchesLib` build plus
   the existing Step 3 recipe on a configured Windows/MIPS host.
   Session 3250 and Session 3251 reran the exact `PatchesLib` target and found
   no target in the configured Unix build, with no local MIPS/generated patch
   prerequisites. This is external-host evidence only; do not treat it as
   guard validation. The satisfying experiment remains the exact build plus
   Step 3 recipe on a configured Windows/MIPS host. Per the three-attempt
   stall rule, do not repeat this local command until that host or its
   generated artifacts are supplied.
   Session 3252 found the watched `reapplyDisplayMode` triplet live but
   misaligned: it ran at `0x006AB800`/`0x006AB400`, not at the target
   `0x00790400`/`0x00790800` transition. The target-phase join was empty
   despite the whole-RDRAM and title controls. Do not add port counters or
   infer a target writer from this candidate; the next oracle angle should
   watch the target-phase store/writer boundary directly.
   Session 3253 watched the direct `0x8008EC88` store with valid whole-RDRAM,
   title, and target-origin controls. It fired once only at the subsequent
   1024-to-512 transition (`0x006AB800`/`$a0=0x1B0`), not at either target
   origin. Do not change the already-nonzero port C88 store or infer target
   causation from it; the next oracle angle should watch the other named
   target-boundary writer `0x8008ED48`.
   Session 3249 completed the status-03 static audit and found named,
   legitimate publication and service-reaping edges. This closes the current
   status-03 idiom selection without authorizing a wait or status change.
   Session 3236 compared the M5 inventory and Step 1/2 evidence with the
   valid controls from Session 3235. No candidate has independent writer PC,
   destination span, payload polarity, and completion-order evidence at the
   target phase: both port arms stop at VI 640 while retail reaches title and
   hangar. This closes the current selection attempt without authorizing a
   contract, gate, wait, route, or output change. Do not repeat the parked
   qualification; a new M5 change requires a newly proven target-phase edge.
   Session 3236 compared the M5 inventory and Step 1/2 evidence with the
   valid controls from Session 3235. No candidate has independent writer PC,
   destination span, payload polarity, and completion-order evidence at the
   target phase: both port arms stop at VI 640 while retail reaches title and
   hangar. This closes the current selection attempt without authorizing a
   contract, gate, wait, route, or output change. Do not repeat the parked
   qualification; a new M5 change requires a newly proven target-phase edge.
   The `-0x68A8`/`-0x68B0` null-consumer class is now closed as a static,
   non-patchable risk; the next active work must supply a new discriminator.
   Earlier same-build qualification evidence remains below for provenance.
   Session 3235 ran the same-build silent/image pair after adding the
   phase-scoped `[m5-port-retail-target]` commit field. Retail passed the
   whole-RDRAM positive control and reached target `0x00790400` plus hangar
   `0x006AB400`; both port arms passed dispatch controls but stopped at
   `0x0066A500`/640 and emitted no target commit or downstream audio joins.
   Because the requested 1024 phase was not reached, the parity result is
   unevaluable and does not select framebuffer mismatch, origin selection, or
   audio-boundary causation. Repeating this qualification is parked; proceed
   to the first authorized M5 behavior change in `M5-AUDIO-PLAN.md`.
   Session 3234 repaired the context join's deferred-watch/latch gates and
   passed the whole-RDRAM positive control (10,000 writes) while capturing the
   target route at `0x00790A00`. Retail `__osViNext` context was valid with
   `framep_phys=0x00790000` and candidates `0x00790400/0x00790800`; route
   `$a0=0x8014090E` is not a framebuffer. The same run captured the known
   attract and hangar candidate pairs, independently validating the field
   readout across phases. This closes the oracle join/filter and supplies the
   concrete target candidate for the next same-build port parity measurement;
   it does not yet identify the writer or authorize a port-origin change.
   Session 3233 repaired the retail oracle join: the prior implementation
   silently discarded the target route's following 640-to-1024 transition
   because it accepted only the attract origins `0x00696100/0x00696600`.
   With an any-next-VI diagnostic arm, the positive-controlled run produced
   two joins, including pre/next origin `0x00790A00`; the route `$a0` was
   `0x8014090E` (physical `0x0014090E`), not a framebuffer. This validates
   route execution and join ordering but does not select a legitimate writer
   or port origin-selection hypothesis. Next, use a target-phase join that
   captures the actual VI context/framebuffer fields, not route `$a0`.
   Session 3232's independent retail runs passed the whole-RDRAM control,
   reached title and hangar, and fired all four established route PCs at the
   `0x00790A00` transition. The `osViSwapBuffer` phase join returned
   `latched=0, joined=0` in both full-schedule captures, so the
   writer-to-swap discriminator is unevaluable. A shorter retry took a direct
   `0x0066A500 -> 0x00790400` route and its zero route counts are unevaluable.
   Do not infer a legitimate writer or port origin-selection defect from
   these runs; repair the oracle join around a route execution PC before
   adding port counters.
   Session 3231 changed `get_rsp_microcode` to read `ROGUESQ_AUDIO_UCODE`
   per `M_AUDTASK` instead of caching the first task's arm. Same-build image
   and silent smoke controls produced 46/45 dispatch rows and 552 SP-return
   rows respectively, with every row on its requested arm and no crash or
   abort. This closes the stale-selector hypothesis at the dispatch boundary
   only; both runs stopped before title, so downstream audio/task/DMA/service/
   slot/voice/MORT/PCM conclusions remain unevaluable. The next work unit
   returns to the independent retail VI-swap/origin attribution below.
   Session 3230's same-build silent/image capture selected
   `H-PhaseDifferentEdge`: both port arms reached 640/origin `0x0066A500`
   and emitted the same live VI-commit and audio-return rows, while retail's
   four watched route PCs occur at 640/origin `0x00790A00` before title. This
   closes the exact-origin alias join and does not establish a missing port
   sequence. The next work unit is a ground-truth retail VI-swap/commit
   attribution at the `0x00790A00` transition, with a whole-RDRAM control, to
   identify the legitimate origin writer and compare its physical buffer to
   the port's `0x0066A500` commit before adding more port counters.
   Session 3229 watched retail caller, reapply entry, reapply call, and return
   branch in one run. The whole-RDRAM control reached 10,000 callbacks; all
   four watches fired once in order at 640 origin `0x00790A00`, then retail
   reached title 1024. The caller and return values match the port's
   `audio-return` row at `0x0066A500` with `target=0`. This refutes an absent
   retail caller and gives no evidence of a wrong value or local ordering
   defect, but it is not a like-for-like port comparison because the phase
   origins differ. The next work unit is to redesign the phase join around the
   observed transition, not add another return-branch field.
   Session 3227 proved the retail `reapplyDisplayMode` entry/call edge is
   live, with two calls at 640 origins `0x00696100` and `0x00790500` before
   title 1024; no call occurred at the port's `0x0066A500` stop. The
   whole-RDRAM positive control and title gate passed, so this is a valid
   phase-boundary correction, not a null instrument. It does not yet select
   writer-absent, wrong-value, or ordering. The next discriminator is the
   return branch at `0x8008EBC8`, watched with the two corrected 640 origins,
   then aligned to the port's phase-3 route and phase-4 audio-return rows.
   If alignment remains impossible, redesign the boundary before adding
   instrumentation.
   Session 3226 closed the first concrete field candidate: retail writes to
   `0x80141AD0/1` and `0x8013B038` are early `setDisplayMode`/
   `reapplyDisplayMode` configuration stores, not the missing pre-title route
   publication. The positive-control oracle reached title 1024, and the
   static port audit matched the writer PCs, so no value or ordering change is
   authorized from this field class. The actual route consumer boundary
   remains open. Session 3225 independently revalidated the locally available,
   retail-qualified phase-relative route
   `3:start,7:start,11:start,15:a,30:start,45:start,60:a,75:start,90:a`:
   retail passed the whole-RDRAM positive control and reached title 1024,
   while the same-build port silent/image pair stopped at VI 640 origin
   `0x0066A500`. Matching input edges and continued recv progress, alongside
   identical route-state output with `target=0`, select `H-PortStateBoundary`
   over input or scheduler stall. The next work unit is a bounded audit of the
   pre-title route-state writer/publication edge, not another audio null.
   The next discriminator is an oracle execution watch on
   `reapplyDisplayMode` entry/call (`0x8008EB5C`, `0x8008EBC0`) with the same
   whole-RDRAM positive control, then a bounded comparison of its live
   arguments and return branch against the port.
2. Execute M5 plan Step 3 only after a valid target-phase Step 1/2 row
   identifies one missing image task/output contract edge. Keep the change to
   exactly one proven writer/consumer relation, with retail writer PC,
   destination span, payload polarity, and completion ordering as controls.
   Do not infer a writer or apply a mitigation from the retail route `$a0`.
3. A12's `0x8014974C` publication class is closed by Session 3221: the only
   guest stores are `setupSongRenderBuffers` zero-init, `musyxSynthFrame`
   terminal clear, and its fixed-one pre-callback publication. The waiters
   remain safety-only; no timeout, force-clear, or new guard is authorized.
4. After a route-boundary change, rerun the existing same-build phase-gated
   pair with `ROGUESQ_AUDIO_UCODE=0/1` and `ROGUESQ_LOG_ALL=1`. Require image-
   arm DMEM, DMA, `Broke`/SP completion, service, slot, and PCM joins; retain
   the silent arm as the no-write control.
5. Closed static M3 publication classes, retain existing traps/guards as
   safety only: A8 `musyxKeyOnVoice` divide/overflow has one live cmd-list
   divisor store (`musyxRenderVoiceSamples` at `0x80090768`, constant
   `0xC0`); the four `break 6` sites are unreachable after `lhu +0x60`; the
   four `break 7` sites are the game's own divide-by-zero handler
   (evidence: `scratch/agent/s3220_m3_keyon_divisor_descriptor.md`). A12's
   flag census is recorded in
   `scratch/agent/s3221_m3_a12_flag_publication_census.md`. A9
   voice-array base (`D_801496F8`) has one store at `0x8008F0EC` in
   `allocateSongChannelArray` (evidence:
   `scratch/agent/s3219_m3_voice_array_base_publication.md`); A10 3D
   voice-list head (`0x80153414`) has only the named insertion/removal/reset
   family (evidence: `scratch/agent/s3216_m3_voice_list_publication_bound.md`);
   the 43-site `SONGTEMPO_TABLE_GUARD` class has writer `startSongSequence` at
   `0x80096D88`. No new guard work is authorized on these classes.
6. Generated-symbol sweep remains closed at the evidence boundary (Sessions
   3210/3212/3217). `static_4_80106C50` was renamed to
   `lvc_registerObjectiveBooleanCounts`; `func_80092F10` is a data-gap
   exclusion overlapping `packFourLutResampledSamples` at `0x80092F94`.
7. M4 restage destination identity is now known: hangar gfx tasks use
   `gspTask` (`0x800377C8`) with physical `output_buff` `0x0075C000` /
   `0x00781800`, not the port runtime dest `0x4B7800` and not DMEM `0x670`.
   Keep the external retail-entry boundary, hangar `0x8000` Y / accumulator
   arithmetic, and M5 SP-yield/MORT publication threads parked pending a
   new target-phase discriminator. The corrected MORT descriptor edge is
   `+0x190` to `dmaVoiceSampleAndSignal`; `+0x194` is the speech source.

## Durable boundaries and operating rules

Factor 5 uses [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is fixed enough for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a same-run positive control,
phase-scoped budgets, and two independent lines of evidence before promotion.
Phase-gate animated comparisons on VI transitions and build every A/B arm
together. A null without a positive control is worthless.

Regeneration order is `make_elf.py` → N64Recomp → `fixup_game_funcs.py` → CMake.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
export submodule patches in the same iteration. Never run `git submodule update`,
`git checkout -- lib/...`, `git clean`, or `git reset --hard`. Kill runs with
SIGKILL and run from `build/`. A mitigation-shaped change requires an `ORIGIN:`
line naming the writer and stating whether the value is legitimate.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. Full failed
experiments remain in the ledger and archived overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Evidence index

Recent evidence includes
`scratch/agent/s3272_m5_step1_pair.md`,
`scratch/agent/s3240_m3_musyx_null_contract.md`,
`scratch/agent/s3226_m5_route_writer_oracle/RESULTS.md`,
`scratch/agent/s3220_m3_keyon_divisor_descriptor.md`,
`scratch/agent/s3225_m5_route_boundary.md`,
`scratch/agent/s3219_m3_voice_array_base_publication.md`,
`scratch/agent/s3218_m4_retail_dest/RESULTS.md`,
`scratch/agent/s3217_generated_symbol_rename.md`,
`scratch/agent/s3216_m3_voice_list_publication_bound.md`,
`scratch/agent/s3213_m3_voice_list_table_audit.md`,
`scratch/agent/s3209_generated_symbol_rename.md`,
`scratch/agent/s3208_generated_symbol_rename.md`,
`scratch/agent/s3207_generated_symbol_rename.md`,
`scratch/agent/s3205_generated_symbol_rename.md`,
`scratch/agent/s3204_generated_symbol_rename.md`,
`scratch/agent/s3203_generated_symbol_rename.md`,
`scratch/agent/s3202_generated_symbol_rename.md`,
`scratch/agent/s3192_m5_step1_contract_pair.md`,
`scratch/agent/s3185_retail_producer_wait/RESULTS.md`, and generated-symbol
reports `scratch/agent/s3197_generated_symbol_rename.md` through
`scratch/agent/s3203_generated_symbol_rename.md`. Use `grep -n` plus a bounded
`sed` window for `PORTING-STATE.md`; never read that multi-megabyte ledger
wholesale. The soak queue is consumed by automation; fold only new tail lines
into the next audit. Session 3210 closes the generated-symbol sweep; see
`scratch/agent/s3210_generated_symbol_rename.md`.
