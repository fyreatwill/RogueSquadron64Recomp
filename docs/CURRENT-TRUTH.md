# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and evidence remain in the ledger and `scratch/agent/`.

Current maintenance marker: Session 3288 (2026-08-29).

Session 3288 asked the port whether the 640 viewer hold enters
`L_800C2B00` / `0x800C2B84` and whether `0x800C2D50` ever takes.
Same-run controls: `[m5-postwait]` viewer `entry` and `[phase]`
`640 @ 0x0066A500` both fired. `2B00` and `2B84` were silent. `2D50`
ran three times, all fallthrough, `$s2=0` `$s5=0`, `$f24` = 1/30 then
2/30 then 5/30. No taken `2D50`, no `2DA0`, no return. First-10
prints would have shown n=4+ if the join kept running. This selects
`H-PortFadeOutNeverEntered` and refutes `H-PortF24NeverZero`,
`H-PortS5Lost`, `H-PortTailReached`, and `H-PortCoverageInvalid`.
Retail (s3287) ran `2D50` 243 times then took. No M5 Step 3.
Evidence: `scratch/agent/s3288_port_viewer_fade.md`.

Session 3287 asked retail whether `0x800C2B84` (`bc1tl $f24==0`)
fires near the 6.8 s `runMenuModelViewerScreen` return, or
`0x800C2D50` reaches `L_800C2DA0` without it. Whole-RDRAM 10000-write
control, title `1024 @ 0x00790400`, and `0x800C2E00` at 6.7 s all
passed. `0x800C2B84` ran 31 times at 6.1–6.6 s (`prev_pc=0x800C2B80`);
`0x800C2D50` ran 243 times from 2.6 s with `$v0=1`; last 2B84 then
taken beq (`prev_pc=0x800C2D50`) then `0x800C2DA0` at 6.6 s then
`0x800C2E00`. In-function `$s5=1` writer is only the `0x800C2B88`
delay slot. Combined with s3285's zero `0x800C2B88` hits, this
selects `H-DelaySlotWatchMiss` and refutes
`H-BeqTakenWithoutFadeStore`, `H-Da0WithoutBeq`, and
`H-ExitCoverageInvalid`. Evidence:
`scratch/agent/s3287_viewer_s5_exit.md`.

Session 3285 landed Session 3270's free-list alignment + cyclic-walk
cap on the generated host functions that actually link
(`allocateDisplayListBuffer` / `allocDLBlockToFillRectList`).
ORIGIN: those functions consume guest allocator pointers; legitimacy
was not independently proven. Safety guard, not a VI-640 or audio
explanation. The same session's Rice run had zero `0x800C2B88` hits
and a 6.8 s slot jal; that `H-RetailNoFadeStore` reading is
superseded by Session 3287. Evidence:
`scratch/agent/s3285_freelist_live_guard.md`,
`scratch/agent/s3285_viewer_frame_exit.md`.

Session 3284 asked retail whether first `menuOverlayInit` (`$a1=9`,
2.0–6.9 s) enters `runMenuModelViewerScreen` (`0x800C28F0`). Viewer
entry at 2.5 s (`prev_pc=0x800C5C98`) during `640 @ 0x0066aa00`;
first return at 6.7 s. This selected `H-RetailViewerThenReturn`.
Evidence: `scratch/agent/s3284_first_menu_model_viewer.md`.

Session 3283 asked retail what occupies the gap between the 2.0 s
first `menuOverlayInit` entry and the 17 s `0x8003E13C` jal.
Continuation `0x8003E094` at 6.9 s (`prev_pc=0x800C5D94`); cinematic
jal `0x8003E10C` / entry `0x800A5D80` in the same 0.1 s bucket;
`0x8003E13C` at 17.0 s. This selected `H-FirstReturnsThenCinematic`.
Evidence: `scratch/agent/s3283_menu_return_vs_cinematic.md`.

Session 3282 asked retail whether `menuOverlayInit` (`0x800C58A0`)
enters early and waits until 17 s before its `runVideoFrameTick` jal
(`0x800C5A18`), or first enters at 17 s. Two entries, each with an
immediate jal: 2.0 s `prev_pc=0x8003E08C` (`$a1=9`) during VI 320,
then 17.0 s `prev_pc=0x8003E13C` (`$a1=2`) during VI 640. This
selects `H-MenuReentry`. The 17 s jal is the post-cinematic
`mainGameLoop` site, not a wait inside the first activation, and not
the unused `(s3, 2, 0xB)` site at `0x8003E0CC`. Evidence:
`scratch/agent/s3282_menu_entry_vs_jal.md`.

Session 3281 asked retail who calls `runVideoFrameTick` (`0x80001354`)
at the 17.2 s 1024-edge. The 17.0 s tick has `prev_pc=0x800C5A18`
(`menuOverlayInit` jal); the only other post-arm tick is 6.7 s
`initSceneForMission`. This selected `H-TickParentMenu`. Session 3282
shows that 17 s jal is the second of two `menuOverlayInit` activations.
`--pc-phase-log-width` had deferred the 320-phase first tick. Evidence:
`scratch/agent/s3281_tick_parent.md`.

Session 3280 asked retail who calls `initVideoSubsystem` (`0x8001A098`)
at the 640→1024 rewrite. All three entries have `prev_pc=0x80018378`
(`advanceVideoFrame` jal). The 17.2 s 1024-edge is 0.1 s before 1024
VI at origin `0x0062bd00`, `$a0=0x200`. This selected
`H-RewriteCallerPreTitle`. Evidence:
`scratch/agent/s3280_initvideo_caller.md`.

Session 3279 asked retail whether the four OSViMode slot +8 words ever
hold 1024. Dummy video stayed at `320 @ 0x006dd280` (documented RDP
stall). Rice arms passed the whole-RDRAM 10000-write control, title
`1024 @ 0x00790400`, and hangar `512 @ 0x006AB400`. While title 1024 was
live, every slot snapshot was word `0x00000400` (FNV `0x4795eec9`). The
only writer is `0x8001B6B0` (`initVideoSubsystem` 4×0x50 copy). This
selects `H-RetailTableHas1024`. Combined with Session 3278's port
census, `H-MissingTableRewrite` is two-source for table contents.
Evidence: `scratch/agent/s3279_retail_osvimode_slots.md`.

Session 3278 censused the four OSViMode slots from `osViSetMode_recomp`.
Same-run controls: four `[osViSetMode]` rows (including swapBuffer
`0x80128C90` width 320) each paired with a `[vi-mode-table]` dump, plus
`[m5-port-vi-control]` at width 640 origin `0x66A500`. Every slot was 320
on calls 1–2 and 640 on calls 3–4; none was 1024. Call 4
(`applyPendingViChanges`) had `pendingB=0x11` / `pending_mask9=0x1` and
published slot `0x80128DF0` width 640. This selects `H-MissingTableRewrite`
and refutes `H-PendingBitGap`. `H-RequestMaskNever1024` is not selected
(no 1024 template; the pending path is live). `H-PortTargetPublicationAbsent`
still holds. Evidence:
`scratch/agent/s3278_osvimode_table_census.md`.

Session 3277 landed the `swapBufferWithViMode` jal delay-slot `$a0`
correction. Call 2 now requests copied-mode dest `0x80128C90` width 320; the
width-2 `[osViSetMode]` and `[phase]` rows are gone. Phase still stops at
`640 @ 0x0066A500` with no 1024 request. This selects `H-DelaySlotNotCausal`
and refutes `H-FixupMissed`. ORIGIN: jal `0x8001BB54`; hardware passes
`0x80128C90` (legitimate copied OSViMode), the skip-goto left `0x80128CD4`
(width 2, not legitimate). Evidence:
`scratch/agent/s3277_swapbuffer_delay_slot.md`.

Session 3276 completed the port target-VI publication/commit audit. CMake's
`RECOMP_FUNCS_DIR` (`../N64Recomp/RecompiledFuncs`) plus the host VI wrappers
enumerate every `osViSetMode` caller, so `H-PortPublicationSourceUnavailable`
is refuted. The live post-640 publisher is `applyPendingViChanges`
(`viRetraceHandlerThread` at `0x80019914`); it requested width 640 at slot
`0x80128DF0`. No 1024 request was published. `H-PortTargetPublicationAbsent`
is selected. `selectAndApplyViMode` is teardown-only. Session 3274's
target-span PC `0x800078EC` is `rs_memset`, not a VI publisher. Evidence:
`scratch/agent/s3276_m5_target_vi_publication_audit.md`.

Session 3275 completed the M5 port route-writer parity capture. The first
recipe run was invalid because its parser counted downstream controls only
after a target phase, making the missing-target branch unreachable. The fixed
same-build pair passed the retail oracle controls and, in both port arms,
passed the host positive controls and phase-4 VI control at `640 /
0x0066A500`; neither reached a target phase or emitted a target-span row.
The fixed driver selects `H-PortTargetStillMissing` as single-source
port-boundary evidence. It rules out invalid coverage, but does not select
writer parity or mismatch and does not authorize audio/output changes.
Evidence: `scratch/agent/s3275_m5_route_writer_parity.md`.

Session 3274 ran the prescribed independent retail target framebuffer-span
capture. The whole-RDRAM positive control recorded 13,204 writes, and VI
tracing reached title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`.
The target span `0x00790000..0x00790C00` recorded 3,096 writes; the selected
hangar-phase histogram attributed 3,072 to `0x800078EC` and 12 each to
`0x8001804C` and `0x8001805C`. The adjacent `0x8008EB00..0x8008ED00`
execution watch was live but produced no target-span writes. This selects
`H-TargetSpanWriter` as valid single-source oracle evidence, not a complete
two-source explanation: the retail target writer is now concrete, while the
port's corresponding route/order and writeback remain unmeasured. No port or
audio behavior changed. Evidence: `scratch/agent/s3274_m5_target_span_writer.md`.

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

Sessions 3262–3264 audited the local VI-640 publication boundary under the
false premise that `RecompiledFuncs/` was absent from this checkout.
Session 3276 superseded that: CMake's `RECOMP_FUNCS_DIR` is
`../N64Recomp/RecompiledFuncs`. Evidence:
[`VI640-BOUNDARY-AUDIT.md`](VI640-BOUNDARY-AUDIT.md),
[`VI640-REQUEST-STATE-BLOCK.md`](VI640-REQUEST-STATE-BLOCK.md).

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
renaming. M5 design is complete in `docs/M5-AUDIO-PLAN.md`. Session 3288
selects `H-PortFadeOutNeverEntered`: the 640 viewer hold never
enters `$s2==2` fade-out, and `2D50` stops after three
fallthroughs. Session 3287 selected `H-DelaySlotWatchMiss` on
retail. Session 3276's `H-PortTargetPublicationAbsent` still holds.
No M5 Step 3 audio change is authorized until a like-for-like
target row exists.

1. Port viewer-loop stall after the third `2D50` fallthrough: last
   site is `L_800C29E0`, one of the six fallthrough callees
   (`waitForPrevFrameDone` … `submitGfxFrame`), or `$s2==0`
   `L_800C2A40`. One fixup probe at those sites plus keep the
   s3288 fade census. One Debug rebuild, one 30 s run with
   `ROGUESQ_LOG_M5_POSTWAIT=1`. Viewer `[m5-postwait]` entry plus
   `[phase]` 640 / `0x0066A500` plus `2D50` n=3 fallthrough are
   the controls. Do not add a skip, allow, restore, or wait
   bypass. No M5 Step 3.
2. Session 3285 moved the 3270 alignment + cycle-cap class onto the
   generated host walks that link here. Remaining: validate
   `patches/heap_guards.c` on the configured Windows/MIPS host
   (`PatchesLib`). Do not repeat the local missing-target build. The
   guard is not evidence that the VI-640 route or audio is corrupt.
3. After the pre-VI-640 scheduler crash is repaired or explained, capture
   consumed-message identity at `0x80019CD0` with `ROGUESQ_RECV_TRACE`
   positive controls. Session 3269 selected `H-RecvWatchUnavailable`. Require
   caller, message pointer, type byte, and `89F/28D44` in the same phase.
4. Execute M5 plan Step 3 only after a valid target-phase Step 1/2 row names
   one missing image task/output contract edge. Keep the change to exactly one
   proven writer/consumer relation.
5. Closed static M3 classes, retain existing traps/guards as safety only:
   A8 key-on divisor, A12 `0x8014974C`, A9 voice-array base, A10 3D voice-list
   head, 43-site `SONGTEMPO_TABLE_GUARD`. `-0x68A8`/`-0x68B0` is
   `H-NotPatchable`. Status-03 is a named `stopVoiceSlotSynced` /
   `serviceVoicePoolFrame` contract.
6. Generated-symbol sweep remains closed (Sessions 3210/3212/3217).
7. M4 restage destination is hangar `gspTask` (`0x800377C8`) with physical
   `output_buff` `0x0075C000` / `0x00781800`. Keep the external retail-entry
   boundary, hangar `0x8000` Y / accumulator arithmetic, and M5 SP-yield/MORT
   publication threads parked pending a new target-phase discriminator. The
   corrected MORT descriptor edge is `+0x190` to `dmaVoiceSampleAndSignal`.

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

Sessions 3262–3264 selected `H-SourceUnavailable` / `H-PortPublicationSourceUnavailable`
because `RecompiledFuncs/` is absent from this repository root. That was
believable as a local-tree probe; CMake's `RECOMP_FUNCS_DIR` is
`../N64Recomp/RecompiledFuncs`, which is present and contains the VI
publisher bodies. Session 3276 used that tree to complete the caller table.

Session 3274's target-span writer `0x800078EC` was treated as a candidate
VI/output publisher. It is `rs_memset` (`0x800078E0`). The span is being
filled; that PC does not publish a VI mode.

The `swapBufferWithViMode` delay-slot width-2 request looked like a VI-mode
publisher bug that might block title 1024. Session 3277 restored hardware
`$a0` order; the copied mode is width 320 and the 1024 request is still
absent. Believable because the illegitimate width-2 pointer was a real
generated-code defect on the only swap-time `osViSetMode` path.

Session 3278 left retail's four-slot table unevaluated at title. Session 3279
measured every slot +8 word as 1024 while title `1024 @ 0x00790400` was live.

Session 3279 left open that the 1024 copy might be a title-only publisher.
Session 3280 named the 1024-edge jal as `advanceVideoFrame` `0x80018378`,
already the port's 640 publisher, so a title-only overlay caller is
refuted. The invocation still sits 0.1 s before 1024 VI at origin
`0x0062bd00`.

Session 3280 left open which of four `runVideoFrameTick` parents is live
at 17.2 s, and NEXT.md treated that tick as per-frame. Session 3281
measured two ticks only: `initSceneForMission` at 6.7 s, then
`menuOverlayInit` at 17.0 s. The 1024-edge parent is the menu jal.

`--pc-phase-log-width` defers `--watch-pc` until the first listed VI
bucket (`g_defer_exec_watches`). Session 3281 armed at 2.3 s
`640 @ 0x0066A500`; 320-phase ticks were unevaluable. Session 3282
armed at first VI and recovered the missing 2.0 s first activation.

Session 3281 left open whether `menuOverlayInit` waits until 17 s
before its jal. Session 3282 measured two immediate entry→jal pairs
at 2.0 s and 17.0 s; the wait-inside-one-call reading is refuted.
The 17 s site is `mainGameLoop` `0x8003E13C`, not `0x8003E0CC`.

Session 3282 left the 15 s gap occupant open. Session 3283 measured
return at 6.9 s then `cinematicLoopBody` (`prev_pc=0x8003E10C`) until
the 17 s jal. A long first inner loop, and a gap of other
`mainGameLoop` work without cinematic, are refuted. Boot attract is
menu `$a1=9`, cinematic, then menu `$a1=2` — not the architecture
sketch of menu `$a1=9`, menu `(s3, 2, 0xB)`, then cinematic.

Session 3283 left open whether first `$a1=9` enters
`runMenuModelViewerScreen`. That was believable as a port
mis-dispatch: s3278 logged a 640-phase viewer entry with no return.
Session 3284 measured the same `0x800C5C98` jal at 2.5 s on retail,
then a 6.7 s return, so the port is stuck inside a screen retail
also uses.

Session 3284 left the 2.5–6.7 s occupant as the `$f24==0` `$s5=1`
store at `0x800C2B88` then a possible slot wait. That was believable
because the generated fade-out path is the only `$s5=1` addiu in the
function. Session 3285 measured zero `0x800C2B88` hits and a single
6.8 s slot jal then `jr ra`, and selected `H-RetailNoFadeStore`.
Believable as a delay-slot PC the oracle can name: Session 3287
measured `0x800C2B84` live at 6.1–6.6 s and the taken beq immediately
after the last 2B84, so the store ran and Mupen omitted the
nullifiable delay-slot PC.

Session 3278/3284's "port holds inside `runMenuModelViewerScreen`
the way retail does until fade-out" is too coarse. Session 3288
measured three `2D50` fallthroughs (`$s2=0`) then silence, so the
port is not looping that join while waiting for `$s2==2`.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Evidence index

Recent evidence includes
`scratch/agent/s3288_port_viewer_fade.md`,
`scratch/agent/s3287_viewer_s5_exit.md`,
`scratch/agent/s3285_freelist_live_guard.md`,
`scratch/agent/s3285_viewer_frame_exit.md`,
`scratch/agent/s3284_first_menu_model_viewer.md`,
`scratch/agent/s3283_menu_return_vs_cinematic.md`,
`scratch/agent/s3282_menu_entry_vs_jal.md`,
`scratch/agent/s3281_tick_parent.md`,
`scratch/agent/s3280_initvideo_caller.md`,
`scratch/agent/s3279_retail_osvimode_slots.md`,
`scratch/agent/s3278_osvimode_table_census.md`,
`scratch/agent/s3277_swapbuffer_delay_slot.md`,
`scratch/agent/s3276_m5_target_vi_publication_audit.md`,
`scratch/agent/s3275_m5_route_writer_parity.md`,
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
