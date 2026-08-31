# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and evidence remain in the ledger and `scratch/agent/`.

Current maintenance marker: Session 3367 (2026-08-31). Compacted from
60,004 bytes / 986 lines to 47,173 bytes / 786 lines; durable s3201–s3302 archive is
PROJECT-OVERVIEW section 54.

Session 3360's independent retail callback-table watch passed the whole-RDRAM
positive control (10,020 writes), reached title 1024 and hangar 512, and
recorded 20 callback-slot writes. Writers were guest PCs `0x80007928` (9),
`0x80007968` (6), and new writer `0x80017D08` (5); one sampled post-value was
`0x8009123C`. This refutes the callback-table physical-alias/no-write theory
and the claim that only the two known helpers write the range, but does not
yet pair `0x80017D08` with the problematic value. Evidence:
`scratch/agent/s3360_m5_callback_table_oracle.md`.

Session 3361's regeneration-surviving port writer census passed host, PCM,
title, and hangar controls with no crash. It paired `0x80007928` with
`0x8009123C` (3 stores), `0x80007968` with zero (3 clears), and
`0x80017D08` with halfword values `0x400/0x800` (5 stores). Thus the third
retail writer is not the port source of the problematic callback value, and
the known `0x80007928` store is. Evidence:
`scratch/agent/s3361_m5_callback_table_writer_source.md`.

Session 3362's bounded generated-tree census found exactly one inline
`0x800919D4` load and `0x800919EC` `jalr`, both in `initN64RspMixer`. The
function loads the target from the global slot initialized at `0x80091900`
and sets `$a0` to the literal `0x8009123C` immediately before the call. No
second generated caller, shared-state argument setup, unresolved generated
edge, or host-side rewrite was found. This classifies the observed transfer
as a concrete guest caller with a literal argument; the static result is
single-source, with hardware execution of the same chain independently
captured in Session 3346. Evidence:
`scratch/agent/s3362_m5_callback_argument_static_census.md`.

Session 3363's independent retail oracle passed whole-RDRAM (10,025 writes),
callback-table (25 writes), title 1024, and hangar 512 controls. It captured
`0x800919EC -> 0x80007910` with `$a0=0x8009123C` in both target phases, while
the separate direct `0x8009BC50` path passed `0x8009B5A8`. This selects
`H-RetailLiteralArgument` and refutes an alternate retail argument or absent
retail chain. Together with Session 3362's static census this is two-line
evidence; the missing port source/target census remains open. Evidence:
`scratch/agent/s3363_m5_retail_callback_argument.md`.

Session 3364's rebuilt qualified port run passed host/task/PCM controls, title
1024, and hangar 512 with zero crash/abort markers. Its aggregate census
captured the same callback edge as retail, `0x800919EC -> 0x80007910` with
`$a0=0x8009123C`, plus the known port store `0x80007928 -> 0x8009123C` and
initializer `0x80091900 -> 0x80007910`. This selects `H-PortMatchesRetail`
and refutes `H-PortWriterMismatch` and `H-PortProbeGap` for the qualified
route. The callback source/target qualification is closed; no behavior
change was made. Evidence: `scratch/agent/s3364_m5_port_callback_edge.md`.

Session 3365 rebuilt the Debug target and attempted the downstream contract
census with the existing markers. Two phase-gated probes and a 45-second
direct no-input run all stayed in non-target 640 attract (`0x62BD00`). The
corrected run passed host/audio positive controls (host-boundary=1,
audio-task=61, PCM-sanity=30), but target-phase consumer-entry and
PCM-boundary rows were zero; no run had title/hangar or crash/abort markers.
These attempts are route-invalid/unevaluable, not evidence for a downstream
hypothesis. The next attempt must use the known valid 90-second direct recipe
from s3364. Evidence: `scratch/agent/s3365_m5_downstream_contract.md`.

Session 3366 corrected the route recipe and qualified the downstream contract.
The valid LLE port run reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, with callback transfer/entry controls live and no crash or
abort markers. The `0x80019B74` consumer-entry marker remained zero, while PCM
source and consumer boundaries both fired. Audio task joins used the
`musyx_stub` arm and reported `dma_count=0`, no source/consumer matches, and
`complete=0`. This selects `H-PortConsumerIndirectGap` and records the stubbed
audio divergence; it does not implicate the PCM boundary. Evidence:
`scratch/agent/s3366_m5_downstream_contract.md`.

Session 3367 completed the generated-tree consumer indirect-dispatch census:
150 `LOOKUP_FUNC` sites were enumerated, with no literal target matching the
named service, child stores, accumulator, or `startSongSequence` consumer.
`startSongSequence` has three direct callers; the service and accumulator
remain definitions reached only through register-loaded guest-state edges.
The companion symbol references independently confirm the target identities,
so this supports `H-GeneratedConsumerEdgeAbsent` only for the static map and
does not prove runtime absence. Evidence:
`scratch/agent/s3367_m5_consumer_indirect_dispatch_census.md`.

Session 3358 validated the session 3357 task-start pointer guard on the live
route. The Debug binary reached title VI `1024 @ 0x00790400` at 14.6 s and
hangar VI `512 @ 0x006AB400` at 26.5 s with 56 audio task dispatches and
zero crashes. This selects `H-TaskPtrAlwaysValid` and refutes
`H-TaskPtrWrongRangeModel`: the guard accepts all legitimate task pointers
and the route is unchanged. The unchecked host-entry dereference class at
`osSpTaskStartGo_recomp` is closed with both build and runtime confirmation.
Evidence: `scratch/agent/s3358_task_ptr_guard_validation.md`.

Session 3357 completed a bounded M3 audit of the active task-start host
boundary. `osSpTaskStartGo_recomp` now validates the complete `OSTask` range
before each of its three `TO_PTR` dereferences, accepting both sign-extended
and zero-extended KSEG0 addresses and returning cleanly for invalid input.
ORIGIN: the guest supplies the task pointer; it is legitimate only when the
full object lies in KSEG0 RDRAM. Evidence: source diff and successful Debug
build.

Session 3356 completed the independent retail callback-table writer capture.
The whole-RDRAM control fired 10,019 writes and the driven run reached title
1024 and hangar 512. The callback range fired 19 writes: 11 from guest PC
`0x80007928` and 8 from `0x80007968`; post-values were only
`0x8009B5A8`, `0x8009123C`, or zero. Retail therefore refutes an unobserved
host/runtime table writer and stale-state explanation for these transitions;
all observed writes use the known registration/clear helpers. This does not
explain the port's pre-existing `0x8009123C` occupants. Evidence:
`scratch/agent/s3356_m5_callback_table_oracle.md`.

Session 3354 completed the bounded M5 consumer source/target census. Retail
ground truth passed whole-RDRAM, title, and hangar controls and showed
`0x80019B74` dispatching the callback-table entry at `0x8011A8A4` to
`serviceVoicePoolFrame 0x8009B5A8` 2,171 times; the accumulator ran 1,163
times. The qualified port run passed callback-loop, host/task, PCM, title,
and hangar controls, but its table stayed
`[80003250,8009123C,8009123C,8009123C]` and all five consumer markers were
zero. This selects `H-PortConsumerIndirectGap` over a status/slot gate or
probe mismatch and identifies the missing table publication/dispatch edge,
but not its writer. No behavior change was authorized. Evidence:
   `scratch/agent/s3354_m5_consumer_source_census.md`. Session 3355's static
   callback-table census found only the generated writer at `0x80007928` and
   clear at `0x80007968`; direct registrations provide only `0x80003250` and
   `0x8009B5A8`. The dispatcher uses the same base and correct four-slot
   indirect call. This refutes table alias and dispatcher explanations and
   leaves a runtime/unresolved-indirect writer for the pre-existing
   `0x8009123C` occupants. Next: obtain independent retail physical watches
   for all callback slots, then inspect/build one host-boundary census only
   after the watch's positive control fires. Evidence:
   `scratch/agent/s3355_m5_callback_table_static_audit.md` (single-source).
   Session 3356's independent retail oracle passed whole-RDRAM, title, and
   hangar controls and attributed all 19 callback-table writes to guest
   `0x80007928` (11) or `0x80007968` (8), with post-values only
   `0x8009B5A8`, `0x8009123C`, or zero. This refutes a retail host/runtime
   writer and stale-state transition for the observed writes. Next: build one
   regeneration-surviving port host-boundary census for the same table; do not
   change behavior or add a mitigation.

Session 3355's static callback audit found only the known registration/clear
helpers and no alternate alias or generated writer for the port occupants.
The unresolved class is runtime/indirect writing. Evidence:
`scratch/agent/s3355_m5_callback_table_static_audit.md`.

Session 3353 found no direct or literal generated edge to the service and
accumulator consumers; only register-loaded `jalr` sites remain. Evidence:
`scratch/agent/s3353_m5_consumer_edge_census.md`.

Session 3352 qualified the route: retail controls and all five consumer PCs
were live, while the port controls passed and all five exact-site markers
were zero. This selects `H-PortConsumerIndirectGap` for the qualified route.
Evidence: `scratch/agent/s3352_m5_port_consumer_entry.md`.

Session 3351 independently confirmed retail reaches all five named consumer
PCs in hangar, refuting `H-ConsumerWrongNames`; it does not split port
reachability from a port status/slot gate. Evidence:
`scratch/agent/s3351_m5_retail_consumer_oracle.md`.

Session 3350 guarded four public message-queue entry points before `TO_PTR`;
the Debug target rebuilt and valid queue behavior was unchanged. ORIGIN: the
guest supplies queue pointers, which are legitimate only in KSEG0 RDRAM.
Evidence: `scratch/agent/s3350_m3_mesgqueue_api_guard.md`.

Session 3349 found the service/accumulator consumers lack direct generated
callers and have unresolved `LOOKUP_FUNC` edges; the static map is incomplete.
Evidence: `scratch/agent/s3349_m5_consumer_reachability_audit.md`.

Session 3348's qualified route had positive controls and slot/status activity,
but zero hits for the four named consumers, selecting
`H-PortConsumerUnreached`. Evidence:
`scratch/agent/s3348_m5_slot_status_qualification.md`.

Session 3346 independently observed the guest chain
`0x800919D4 -> 0x800919EC -> 0x80007910`, refuting host dispatch for that
occupant transfer. Evidence: `scratch/agent/s3346_m5_retail_indirect_exec.md`.

Session 3345 confirmed `0x80007910` is a legitimate immediate initializer
stored at `0x80091900`; there is no source-table load to trace. Evidence:
`scratch/agent/s3345_m5_pointer_provenance_audit.md`.

Session 3344's retail capture attributed six corrected-slot writes to guest
PC `0x80091900`, refuting stale-pointer state. Evidence:
`scratch/agent/s3344_m5_retail_pointer_source.md`.

Session 3343 redesigned callback-writer capture to aggregate rows and drain
them from the phase poller. In one same-build matrix, both the no-writer and
aggregate-writer LLE arms passed host/task controls and reached title 1024 and
hangar 512 without a crash; the aggregate arm retained target-phase rows for
`0x80091900 -> 0x80007910` and `0x80007928 -> 0x8009123C`. This refutes the
prior per-event-output scheduler perturbation and makes the port pointer-writer
discriminator target-valid. A separate audio/image arm crashed before controls
and is route-invalid. Retail ground truth independently recorded one write at
the corrected physical `0x001499D4` slot. Evidence:
`scratch/agent/s3343_m5_callback_writer_aggregate.md`.

Session 3341's retail ground truth passed the whole-RDRAM control and recorded
zero writes at the requested physical `0x001099D4` watch, while generated
address arithmetic shows the indirect load at `0x800919D4` actually reads
physical `0x001499D4`, initialized by store PC `0x80091900`. A port probe
observed that store writing `0x80007910` in phase 2, but both corrected port
retries crashed in the scheduler before title/hangar controls. The pointer
source remains unresolved; no behavior change is authorized. Evidence:
`scratch/agent/s3341_m5_callback_pointer_source.md`.

Session 3342 built once and ran concurrent no-probe/probe route controls. The
no-probe arm passed host control and reached VI-1024 and hangar VI-512 without
crashing; the callback-writer probe arm passed its positive store control but
crashed in `spTaskSchedulerThread` before target phases. This selects
instrumentation-sensitive route invalidity for the current recipe, refutes a
build-wide scheduler failure, and leaves logging perturbation versus a
probe-side generated effect unresolved. The pointer-source census remains
unauthorized. Evidence: `scratch/agent/s3342_m5_scheduler_route_control.md`.

Session 3340 selected `H-IndirectTransfer`: retail's independent
`registerSiCallback` previous-PC histogram includes `0x800919EC` (5/9), and
the port's regeneration-surviving transfer marker shows that site passing
`0x8009123C` directly into the callback in both title and hangar phases. The
port's direct `0x8009BC50` transfer passes `0x8009B5A8` instead. Host/task/PCM
controls and title/hangar VI controls passed. This identifies the transfer
site but not the writer of the indirect function pointer; no behavior change
is authorized. Evidence: `scratch/agent/s3340_m5_callback_transfer.md`.

Session 3338 added a regeneration-surviving entry probe at
`registerSiCallback` (`0x80007910`). The valid fixed recipe passed host/task,
title-1024, and hangar-512 controls; entry captured `0x8009123C` in phase 2
and later target phases, but `$ra` was zero on every row. This refutes a
store-versus-entry mismatch but does not identify the caller; zero is a
single-source generated-context result, not an address-zero caller finding.
Evidence: `scratch/agent/s3338_m5_callback_entry.md`.

Session 3337 selected the early callback-table store writer. The port passed
host/task controls and reached title 1024 and hangar 512. An ungated exact
store hook observed `0x80007928` writing `0x80003250` and then
`0x8009123C` during phase 2; the callback census changed to
`[80003250,8009123C,0,0]` in the same early window. This selects
`H-PortEarlyStore` and refutes a clean-store explanation or census-only
transient for the observed transition. The exact caller supplying
`0x8009123C` to `registerSiCallback` remains unresolved. No behavior change is
authorized. Evidence: `scratch/agent/s3337_m5_callback_early_store.md`.

Session 3336 resolved the phase-gating failure in the callback registration
callsite probe. Retail passed whole-RDRAM, callback-table, and title/hangar
controls; the port passed host/task/phase controls and reached 1024 and 512.
The only direct callsite rows were `0x80002FDC -> 0x80003250` and
`0x8009BC50 -> 0x8009B5A8`; neither registered `0x8009123C`. The port table
still changed to `[80003250,8009123C,0,0]` before those later calls. This
refutes a direct generated callsite for the observed occupant transition and
leaves the exact registry-store writer/loader unresolved. No behavior change
is authorized. Evidence: `scratch/agent/s3336_m5_callback_exact_caller.md`.

Session 3335 selected the runtime-writer class for the pre-existing callback
occupants. Retail passed the whole-RDRAM control, watched 19 callback-table
writes, and executed `0x80007928` with `0x80003250` and `0x8009123C`. The
qualified port passed task/host, title 1024, and hangar 512 controls; its 1-ms
callback census observed `[80003250,0,0,0]`, then
`[80003250,8009123C,0,0]`, then `[80003250,8009123C,8009123C,0]`. The
captured last PCs (`0x80001F88`, `0x80007A68`) are asynchronous nearby
markers, not exact store PCs; the first maps to the caller returning after
`registerSiCallback(0x80003250)`. This selects runtime-generated population
as a class, leaves the exact `0x8009123C` caller unresolved, and authorizes
no behavior change. Evidence: `scratch/agent/s3335_m5_callback_occupant_writer.md`.


Session 3334 completed callback-writer attribution through the registration
edge. Retail passed the whole-RDRAM and callback-table controls, reached
hangar, and executed `0x80066AA4 -> 0x8009BBA0`, `0x8009BC50 -> 0x80007910`,
`0x8009B5A8`, and `0x8009BD7C`. The qualified port also reached title/hangar
and passed task/host controls. Its initializer and registration callsite ran,
passing the legitimate `0x8009B5A8`, but the `0x80007928` store did not run;
the table was already `[0x80003250,0x8009123C,0x8009123C,0x8009123C]`.
This refutes `H-PortCallbackWriterIsInit` and `H-PortCallbackWriterUnobserved`
for the qualified route and leaves the pre-existing `0x8009123C` writer or
loader unresolved. No behavior change is authorized. Evidence:
`scratch/agent/s3334_m5_callback_writer_attribution.md`.

Session 3332 completed the M5 callback-table population audit. The
`0x80019B74` VI-retrace dispatcher walks the four-entry SI callback table at
`0x8011A8A4`; the only generated registrations are `0x80003250` from SI
thread startup and `0x8009B5A8` from `initMusyXVoiceTable`. `0x8009BD7C` is a
downstream voice routine, not a registered callback target. This selects
`H-CallbackTargetsInstalled` for `0x8009B5A8`, refutes callback-target absence
for that target, and leaves runtime reachability of `initMusyXVoiceTable` and
the indirect child edge unresolved. No behavior change is authorized.
Evidence: `scratch/agent/s3332_m5_callback_table_audit.md`.

Session 3330 completed the reachable-hangar M5 slot/status qualification. The
port image arm passed VI-1024 and VI-512 plus task/PCM controls, but produced
zero slot/status rows and zero executions of retail's named consumer PCs
`0x80094648`, `0x8009B600`, `0x8009B85C`, and `0x8009BDE8`. The actual MusyX
voice table stayed `max=1 active=0 mask=0` in the same target phase. This
selects `H-PortSlotStatusMissing` for the recipe, with single-source port
evidence; it names no missing writer and authorizes no behavior change.
The run later hit the known unaligned PI-DMA abort after the controls fired.
Evidence: `scratch/agent/s3330_m5_slot_status_qualification.md`.

Session 3331 statically audited the four retail PCs and both watch ranges.
All four PCs have generated bodies: `0x80094648` is in `startSongSequence`
with three direct generated callers, `0x8009B600` and `0x8009B85C` are in
`serviceVoicePoolFrame`, and `0x8009BDE8` is in
`accumulateVoiceSampleOffset`. The latter three have no direct generated
callsite because the audio callback path is indirect. The indexed
`0x80141AD8+` channel writer and literal `0x80154620` voice-table accesses are
present; `0x80141AD0` is not a literal generated access. This selects no
hypothesis: absence and range mismatch are not supported, while a caller gate
cannot be proven without tracing callback-table population. Evidence:
`scratch/agent/s3331_m5_slot_status_source_audit.md`.

Session 3329 resolved the apparent title blocker in one phase-gated port run:
the image arm committed VI-1024 at 50.3 s, reached hangar VI-512 at 94.2 s
with the extended 60/90/120-second autopilot, and passed task/PCM controls.
The actual MusyX voice table stayed at max=1, active mask 0 through the
transition; the existing 1,578-entry count was the cinematic dispatcher pool,
not audio slots. This refutes `H-VICommitAbsent` and `H-VoiceReapingAbsent` as
route blockers for this recipe. Evidence:
`scratch/agent/s3329_m5_slot_status_discriminator.md`.

Session 3328 ran the port-side slot/status qualification (180 s watchdog,
bounded logging). The image arm reached VI-1024 at 14.6 s with autopilot and
ran 31,512 audio task joins, 89 PCM source/consumer pairs, 6,308 DMA rows, and
7,796 route-prepare rows in phase 4. Two new findings: (1) no vi-commit for
VI-1024 appeared — the last M5 route vi-commit was seq=9 with
`requested_width=1024 committed_width=640 commit_phase=3`, so all 7,796
phase-4 route-prepare rows show `key_match=0`; (2) slot-pool count grew
monotonically from 4 to 1578 over 64.5 s in the title phase with no slot
freeing observed. The game never reached VI-512 (hangar) and was SIGKILL at
180 s. No B40-writer, slot-allocation, or slot-submission rows. This selects
`H-PortRouteStillIncomplete` and authorizes no behavior change. Single-source
evidence. Evidence: `scratch/agent/s3327_m5_slot_status_port/image.log`.

Session 3327's retail-first slot/status capture passed the whole-RDRAM control,
observed 108 target-phase writes in `0x141AD0:0x141AF0` and 48,349 writes in
`0x154620:0x1546A0`, and saw `0x80094648`, `0x8009B600`, `0x8009B85C`, and
`0x8009BDE8` execute in the hangar phase. The same-build port image arm reached
title 1024 and produced task/PCM controls but did not reach hangar within the
lighter 120-second watchdog, so the port-side like-for-like comparison remains
incomplete. This selects `H-RetailSlotConsumer` for the retail branch only and
authorizes no behavior change. Evidence:
`scratch/agent/s3327_m5_slot_status_consumer.md`.

Session 3317 could not run the configured-host PatchesLib discriminator in
this Darwin checkout: `E:/mips-toolchain` is absent. The substitute source
reconciliation found no M5 Step 3 writer/consumer edge beyond the existing
A1–A20 inventory in `docs/M5-AUDIO-PLAN.md`; this is single-source evidence
and authorizes no behavior change. Evidence:
`scratch/agent/s3317_m5_plan_reconciliation.md`.

Session 3319 established that the configured-host PatchesLib discriminator is
genuinely unavailable in this checkout, but it is not a project-wide stop.
The documented pipeline has no host-only alternative; the native arm64
`build/N64Recomp` artifact cannot produce the missing MIPS ELF. There is no
local MIPS compiler/linker, `patches/patches.elf`, or generated
`RecompiledPatches/patches.c`. The host build remains an open dependency,
while the next unit is rescopeable to an independent retail publication
capture. Evidence: `scratch/agent/s3319_unblock_routes.md`.

Session 3320's independent retail capture passed the whole-RDRAM positive
control, armed at VI 640/origin `0x00696600`, and observed the target
`osViSwapBuffer` call from `0x8001BE24` with physical `$a0=0x00790000`.
The post-swap join was live but capped before a target-specific next-VI row
could be retained. This selects `H-RetailTargetSwap` and establishes the
retail publication edge, but names no missing port image-task/output edge.
Evidence: `scratch/agent/s3320_retail_target_publication.md`.

Session 3321 completed a bounded static census of the linked generated host
allocator consumers. All six free-list traversal dereferences in
`allocateDisplayListBuffer` and `allocDLBlockToFillRectList` have adjacent
KSEG0/alignment guards; both loop-back sites also have the s3285 cycle cap.
The three separate cache-head loads in the same functions have existing
generic guards. This closes the generated free-list-walk class as safety-only
and authorizes no behavior change. Evidence:
`scratch/agent/s3321_generated_freelist_walk_audit.md`.

Session 3323 changed the independent retail post-swap latch to accept every
pre-swap width and retain `pre_width`. One 90 s Rice capture passed 10,000
whole-RDRAM writes, 1,849 watched `osViSwapBuffer` executions, and 5,369 VI
frames. It latched/joined 1,849/1,849 rows with zero pending, dropped, or
overflow; every row was 640→640/other 640-origin or 1024→1024, with no
640→1024 title row. This selects `H-NonImmediateTitleSwap` for the watched
`0x80035500` edge and refutes table-capacity and 640-only-latch explanations,
but is single-source evidence and does not name the transition publisher.
Evidence: `scratch/agent/s3323_retail_all_width.md`.

Session 3324 rebuilt the Debug target and attempted the M5 Step 1
image-versus-silent qualification. The oracle passed whole-RDRAM, title
1024, and hangar 512 controls, but both port arms stalled at VI 640 before
the target phase and produced no task/audio joins. A fixed lighter-route
rerun was attempted but its detached runner did not persist to produce arm
logs. This is route-invalid evidence: it rejects no audio contract
hypothesis and authorizes no M5 behavior change. Evidence:
`scratch/agent/s3324_m5_step1_qualification.md`.

Session 3325 reran M5 Step 1 under the supervised pair driver. The independent
oracle passed 10,000 whole-RDRAM writes plus title 1024 and hangar 512. Both
port arms reached target phases without crash/abort. The silent arm produced
2,425 task-ABI rows but zero DMA-range or image-stage rows; the image arm
produced 1,436 ABI, 3,019 DMA-range, and 6,162 image-stage rows. Audio-route
and PCM boundary rows appeared in both arms, while slot allocation/submission
remained zero in both. This selects `H-ContractGap` for the Step 1
discriminator: image execution is present but no image-only output/slot edge
was observed. It names no legitimate missing writer and authorizes no behavior
change. Evidence: `scratch/agent/s3325_m5_step1_image_vs_silent.md`.

Session 3326 ran the required retail-first boundary capture with whole-RDRAM,
title, and hangar controls. Retail target-phase writes occurred in the slot
range from `0x80094648` and in the status range, but the candidate PCM/output
spans had no title or hangar writer rows despite the positive control. The
same-build image pair reached title/hangar and retained image DMA/stage plus
PCM source/consumer controls, while slot allocation/submission and guest
kind-1 writer rows remained zero. This selects `H-RetailDoesNotWriteOutput`
for those candidate spans and moves the missing-edge search upstream to the
slot/status relation. Evidence:
`scratch/agent/s3326_m5_retail_boundary.md`.

Session 3322 widened the independent retail post-swap table to 4096 rows and
ran the any-VI join with Rice. The route reached title 1024 at 49.1 s and
returned to 640. Positive controls passed: 10,000 whole-RDRAM writes, 1,852
`osViSwapBuffer` executions, and 5,374 VI frames. The join retained 195/195
rows with zero pending, dropped, or overflow; all were 640→640 rows and none
was the 640→1024 title transition. This refutes table-capacity saturation and
no-following-VI, but does not yet distinguish a non-immediate title swap from
the join's 640-only latch filter. Evidence:
`scratch/agent/s3322_retail_post_swap_join.md`.

## Recent evidence ledger

The detailed per-session narrative is retained in the append-only ledger and
PROJECT-OVERVIEW. Durable operational conclusions are:

- s3358 validated the task-start guest-pointer guard; title 1024 and hangar
  512 passed with 56 audio dispatches and no crash.
- s3356's independent retail watch attributed all callback-table writes to
  guest PCs `0x80007928` or `0x80007968`, leaving the port's pre-existing
  `0x8009123C` occupants unresolved.
- s3351–s3354 show retail executes all five named M5 consumers, while the
  qualified port reaches hangar with no named consumer hits; unresolved
  register-loaded `jalr` edges remain the active boundary.
- s3344–s3346 establish the legitimate pointer initializer and guest chain
  `0x800919D4 -> 0x800919EC -> 0x80007910`.
- s3325–s3329 establish target-route reachability but no named port
  slot allocation/submission edge.
Sessions 3313–3320 established the retail/port cinematic and VI baselines:
retail sets the skip-allow byte late and reaches the initializer/title, while
the port keeps it zero; retail's swap edge is real but has no immediate
640→1024 row. The B1C and PatchesLib details are in the ledger and evidence
index; neither authorizes a behavior change.

The s3312 retail/port cinematic discriminator selected `H-RetailFlagSet`:
retail's skip-allow byte becomes 1 late and reaches the initializer/title,
while the port keeps it zero. Evidence remains in
`scratch/agent/s3312_retail_cine_init_path.md` and the ledger.

The s3311 port capture confirmed `H-FlagByteSkip`: the time predicate ran
but the flag-byte branch stayed taken on `$a0=0`, so the initializer jal did
not fire. This is the port-side counterpart to s3312 and is not an M5 change.
Evidence: `scratch/agent/s3311_cine_init_jal.md`.

The s3310 retail capture showed `0x800B0934` is initialized only after the
finite loop, then cleared on exit; the port's null pointer during the loop is
therefore hardware-like, while its flag-byte mismatch remains causal.
Evidence: `scratch/agent/s3310_retail_b0934_writer.md`.

Session 3308 selected `H-PtrZeroSkip`: the stage advancer's pointer check
was live and always saw zero, so it returned zero. The queued 600 s soak
had no crash but no title transition. Evidence:
`scratch/agent/s3308_stage_advancer.md` and the ledger.

Session 3307 selected `H-PortLoopNoExit`: the port stayed in the cinematic
loop with the exit gate at zero, unlike retail's finite-loop return. Evidence:
`scratch/agent/s3307_cinematic_loop.md`.

Retail s3306 independently reached the cinematic return and title after
about 1002 loop iterations, confirming the finite-loop reference behavior.
Evidence: `scratch/agent/s3306_retail_cinematic_exit.md`.

Sessions 3305–3308 establish the cinematic baseline: the viewer returns,
then the port's stage advancer sees a null pointer and returns zero, so the
exit gate never opens; retail's finite loop eventually initializes the stage.
Detailed captures remain in the ledger and evidence index.

Sessions 3303–3304 established the completion-aware SP-yield contract as
the default: the request bit is legitimate, but not a yielded-task result on
this host because no interrupt/resume path exists. Evidence remains in the
ledger and `scratch/agent/s3303_yield_status_ab.md`.

## Current state

The native port builds and boots through attribution, the N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) on the validated spin-yield/F5-LLE route. Hangar visuals
still have geometry/color artifacts. Audio is not production-complete: the
Factor 5 image task is the qualified real-audio arm and `musyx_stub`/Broke is
the silent control.

The current default after Session 3304 returns from the attract viewer
and enters `cinematicLoopBody` (`0x800A5D80`), then stays at VI
`640 @ 0x0066A500` because `cinematicStageAdvancer` always skips on a
null `0x800B0934`. That null persists because
`jal cinematicInitializer` at `0x800A62B4` never fires. Session 3312
shows retail also leaves time-pred `0x800A626C` not-taken (`$v1=1`
on all 1189 printed rows); the hardware path is skip-allow `$a0`
going 0→1 at 48.1 s so `0x800A6274` falls through, first 6288
`$v0=0`, then the jal, then AF4B8 stores KSEG0 `0x800D9780`. Port
Session 3311 keeps `$a0=0` so 6274 always takes. Skip-allow is 1 if
incoming `$a0` is set (`getControllerNewButtonsPressed` `& 0x9000`
at `0x800A6208`) else `lbu 0x800B0B1C` at `0x800A6244`; prologue
`0x800A5EE8` zeros that byte. Retail Session 3306 exits that loop
at 48.8 s and reaches title `1024 @ 0x00790400` at 49.2 s. Boot
attract on both sides is menu `$a1=9` → `runMenuModelViewerScreen`
→ cinematic → second menu `$a1=2` (`0x8003E13C`), not the
architecture sketch of menu `$a1=9`, menu `(s3, 2, 0xB)`, then
cinematic.

`H-PortTargetPublicationAbsent` still holds: the live post-640
publisher is `applyPendingViChanges` (`viRetraceHandlerThread` at
`0x80019914`); it requested width 640 at slot `0x80128DF0`. Retail
title 1024 rewrites all four OSViMode slot +8 words to `0x00000400`
via `initVideoSubsystem` (`0x8001B6B0`) from `advanceVideoFrame`
`0x80018378`. Port Session 3278 never published a 1024 template.

The latest same-build M5 image-versus-silent qualification passed dispatch,
whole-RDRAM, title, and hangar controls. The image arm alone executes
DMA/image stages, but both arms still have PCM boundary and route rows and
neither has slot allocation/submission. This selects `H-ContractGap` as a
single-capture discriminator result; it does not name the missing writer or
authorize an audio, route, VI, gate, wait, voice, destination, or output
change. Do not remove the status-03 wait hatch.

Retail target-phase `osViSwapBuffer` (`0x80035500`) is caller
`0x8001BE24`, `$a0=0x80790000` (physical `0x00790000`), origins
`0x00790400/0x00790800`. The port has a target-row logger but never
emits the row (`H-PortRowMissing`). Session 3274's target-span writer
`0x800078EC` is `rs_memset`, not a VI publisher.

`PatchesLib` cannot be built on this Unix checkout: no target, cache
points at `E:/mips-toolchain`, no local `mips64-elf-*`, no generated
`RecompiledPatches/patches.c`. That is `H-GuardHostMissing`, not
guard evidence. Do not retry the local missing-target build. M5 Step
3 remains gated.

## Next steps

Priority is maintenance, M5 de-stubbing, systematic M3, then generated-symbol
renaming. M5 design is complete in `docs/M5-AUDIO-PLAN.md`. Session 3304's
completion-aware SP-yield lifecycle returns the viewer; Session 3312
shows retail reaches `jal cinematicInitializer` because skip-allow
`$a0` goes 1 at 48.1 s, not because count hits 1190. Port Session
3311 keeps `$a0=0` so 6274 always takes and `0x800B0934` stays
null. Session 3276's `H-PortTargetPublicationAbsent` still holds.
No M5 Step 3 audio change is authorized until a like-for-like
target row exists.

1. M3 task-start guest-pointer guard is landed and runtime-validated. The
   full-width KSEG0 predicate at `osSpTaskStartGo_recomp` passes all
   legitimate task dispatches; title `1024 @ 0x00790400` and hangar
   `512 @ 0x006AB400` were both reached in the validation run with 56 audio
   task dispatches and zero crashes (`H-TaskPtrAlwaysValid` selected,
   `H-TaskPtrWrongRangeModel` refuted). This class is closed. Evidence:
   `scratch/agent/s3358_task_ptr_guard_validation.md`.
   Next: choose the next M3 idiom class to audit systematically (see item 7),
   or advance M5 Step 1 consumer-dispatch investigation (item 2).
2. M5 Step 1 remains `H-ContractGap`, now narrowed by Sessions 3330–3348:
   the reachable port hangar has valid task/PCM controls but no slot/status
   rows or named retail consumer-PC executions, selecting
   `H-PortSlotStatusMissing` on single-source port evidence. The callback audit
   proves `0x8009B5A8` is registered by `initMusyXVoiceTable`, while
   `0x8009BD7C` is not a table target. The voice probe is inactive
   (`max=1 active=0`) but this is not yet a replacement for the
   slot/status finding. Session 3333 showed retail reaches the initializer,
   service callback, and child. Session 3334 showed the port initializer passes
   `0x8009B5A8`, but `registerSiCallback` finds the table full and cannot store
   it; the three `0x8009123C` occupants remain unattributed. Next: identify
   the writer/loader that populated those occupants, retaining the retail
   whole-RDRAM and port task/host controls. Session 3336 found no direct
   generated callsite registering `0x8009123C`; the table is already
   `[80003250,8009123C,0,0]` before the later `0x8009BC50` call. Next: capture
   Session 3338 proves the `0x8009123C` value is already present at
   `registerSiCallback` entry, but generated `$ra` is zero for all entries, so
   the writer remains unresolved. Session 3340 proves the port's
   `0x800919EC` indirect transfer supplies `0x8009123C`, matching retail's
   independent previous-PC edge; the direct `0x8009BC50` site supplies
   `0x8009B5A8`. Next: identify the writer/source of the function pointer
   loaded at `0x800919D4`, retaining the retail whole-RDRAM and port
   task/host/title/hangar controls. Session 3341's retail watch at
   `0x001099D4` was quiet, while the port's concrete initializer store at
   `0x80091900` emitted `0x80007910`; both port retries crashed before target
   phases, so this is route-invalid and selects no pointer-source hypothesis.
   The s3342 paired control shows the no-probe route reaches title/hangar but
   the callback-writer logging arm crashes in `spTaskSchedulerThread` before
   target VI. Session 3343's aggregate table removed the per-event output: the
   probe arm passed host/task/title/hangar controls and retained five
   target-phase `0x80091900 -> 0x80007910` rows plus the `0x80007928` table-store
   row. The prior logging-perturbation explanation is selected for that route.
   Session 3344 completed that capture: retail passed whole-RDRAM, title, and
   hangar controls and wrote physical `0x001499D4` six times, all from guest
   PC `0x80091900`; the execution watch had zero hits. This selects
   `H-PointerWriter` and refutes `H-StalePointer` for the target route. Next:
   trace the source value and separately validate whether the slot is consumed
   through an uninstrumented indirect edge. Session 3345 resolved the source:
   both retail and port use the legitimate immediate `0x80007910` initializer
   at `0x80091900`; there is no source memory access to instrument. The
   remaining discriminator is retail execution attribution versus host
   dispatch at the later `0x800919D4`/`0x800919EC` edge. Session 3346 observed
   the complete guest chain `0x800919D4 -> 0x800919EC -> 0x80007910`, with the
   target entry's `prev_pc` equal to `0x800919EC`, under live whole-RDRAM and
   title controls. This selects `H-GuestJalr` and refutes host dispatch for
   the observed occupant transfer. The driven retry stalled before hangar and
   added no slot write. Next: qualify the port slot/status writer and consumer
   rows in reachable hangar; do not change a contract edge or add a
   mitigation. Session 3347's rebuilt port run passed host/task/PCM controls
   and reached title 1024 but stalled before hangar, so it selected none of
   the three hypotheses. Session 3348 used the validated extended route,
   reached VI 512 with positive controls, and found target-phase slot/status
   activity but zero hits for all four named consumer PCs. This selects
   `H-PortConsumerUnreached`. Session 3349 found one direct consumer chain for
   `0x80094648`, but no direct or statically resolved indirect chain to the
   service/accumulator consumers. The static map is incomplete and selects
   none of the three reachability hypotheses. Session 3351's independent
   retail oracle passed the whole-RDRAM control, reached hangar
   `512 @ 0x006AB400`, and executed all five watched PCs with stable
   previous-PC chains. This refutes `H-ConsumerWrongNames` and proves the
   retail route is live, but cannot split a port reachability gap from a port
   status/slot gate. Session 3353's static census found the three direct
   `startSongSequence` callers but no direct or literal indirect generated edge
   to `serviceVoicePoolFrame` or `accumulateVoiceSampleOffset`; generic
   register-loaded `jalr` sites are the remaining unresolved class. The
   companion symbol map independently confirms the target identities. This
   supports `H-PortConsumerIndirectGap` and refutes a name/probe mismatch, but
   does not name the dynamic pointer/table writer. Next: obtain independent
   retail ground truth for the dynamic callback/function-pointer source and
   then build one regeneration-surviving port census of the same source/target
   table; do not change behavior or add a mitigation.
   Session 3360's retail physical callback-table watch passed the whole-RDRAM
   control and recorded 20 slot writes, including guest writer `0x80017D08`
   in addition to `0x80007928` and `0x80007968`. The alias/no-write theory is
   refuted; exact writer-to-value pairing remains the next port census. See
   `scratch/agent/s3360_m5_callback_table_oracle.md` (single-source).
   Session 3361's port census paired the known `0x80007928` store with
   `0x8009123C`, the `0x80007968` path with zero, and the additional
   `0x80017D08` writer with `0x400/0x800` halfwords. This refutes
   `H-PortWriterIsThirdGuestSite` and leaves the upstream source/call path
   that supplies `0x8009123C` to `registerSiCallback` as the next boundary.
   Evidence: `scratch/agent/s3361_m5_callback_table_writer_source.md`.
   Session 3364's rebuilt qualified port run passed host/task/PCM, title, and
   hangar controls with zero crash/abort markers. It captured the same
   `0x800919EC -> 0x80007910` transfer and `$a0=0x8009123C` as retail, plus
   `0x80007928 -> 0x8009123C` and `0x80091900 -> 0x80007910`. This selects
   `H-PortMatchesRetail` and refutes `H-PortWriterMismatch` and
   `H-PortProbeGap`; the callback source/target qualification is closed.
   Next: qualify the downstream service/slot/voice/PCM contract in one
   phase-gated port run. Evidence:
   `scratch/agent/s3364_m5_port_callback_edge.md`.
Session 3367 closes further static consumer enumeration as a discriminator:
the generated tree has no literal indirect target for the named consumers,
and only register-loaded guest-state callback edges remain. Next M5 work must
obtain independent retail status-03 worker/zeroing evidence before any wait
or slot change. Evidence:
`scratch/agent/s3367_m5_consumer_indirect_dispatch_census.md`.
2. M5 Step 1 remains `H-ContractGap`, narrowed by Sessions 3326–3329 and
   3348: retail
   writes slot/status and executes the named consumer PCs in the hangar phase
   (`H-RetailSlotConsumer`). The port image arm now reaches hangar with the
   extended autopilot; the prior title stop was schedule-dependent for this
   recipe. The route commits 1024 and 512, and the actual MusyX voice mask is
   zero/max=1 rather than exhausted. Session 3348 found the port slot/status
   activity live in hangar but did not observe the four named consumers,
   selecting `H-PortConsumerUnreached`. Next: audit the consumer call graph
   and callback edges. Do not change a contract edge or add a mitigation.
3. Keep configured-host PatchesLib validation as an open dependency. When
   that host is available, run `cmake --build build --config Debug --target
   PatchesLib` to distinguish build availability from source/link failures.
   Do not repeat the local missing-target check; Session 3319 confirmed the
   missing MIPS stage and generated input here.
4. Treat the B1C source investigation as closed at the observed phase: no
   alternate writer or ordering edge exists in the generated tree, and neither
   conditional nonzero path fired in Session 3314. Do not repeat the same
   6208/6238/6248/6274/62B4 census. Reopen only with a new retail/port
   discriminator for the data-dependent predicates.
5. Session 3321 completed the generated free-list-walk census: all six
   traversal dereferences and three cache-head loads are guarded. The guard
   is not evidence that the VI-640 route or audio is corrupt; do not reopen
   this class without a new writer or an unguarded generated site.
6. Retail target publication remains an `osViSwapBuffer`-related edge
   (`0x80035500`, usually caller `0x8001BE24`, physical `$a0=0x00790000`),
   but Session 3323's all-width join found no 640→1024 row. Treat the title
   transition as non-immediate relative to that watched edge; identify the
   ordering/publisher with a new retail discriminator before calling it a
   missing port edge. The next discriminator should watch the retail mode
   setup/apply callers in one capture; the next M5 change remains gated until a port-side
   like-for-like target row names one missing image-task/output contract edge.
6. Execute M5 plan Step 3 only after a valid target-phase Step 1/2 row names
   one missing image task/output contract edge. Keep the change to exactly one
   proven writer/consumer relation.
7. Closed static M3 classes, retain existing traps/guards as safety only:
   A8 key-on divisor, A12 `0x8014974C`, A9 voice-array base, A10 3D voice-list
   head, 43-site `SONGTEMPO_TABLE_GUARD`. `-0x68A8`/`-0x68B0` is
   `H-NotPatchable`. Status-03 is a named `stopVoiceSlotSynced` /
   `serviceVoicePoolFrame` contract.
8. Generated-symbol sweep remains closed (Sessions 3210/3212/3217).
9. M4 restage destination is hangar `gspTask` (`0x800377C8`) with physical
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

CMake's `RECOMP_FUNCS_DIR` is `../N64Recomp/RecompiledFuncs`. The recomp
direct C call to `submitGfxFrame` does not write guest `$ra` `0x800C2D98`
into `0x40($sp)`; a saved-ra viewer gate on that word is dead. Static
boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a
defensible name. Stable companion duplicate-prefix and preamble mappings
belong in `tools/rename/build_redefs.py`.

`--pc-phase-log-width` defers `--watch-pc` until the first listed VI
bucket (`g_defer_exec_watches`). Arm at first VI when a 320-phase
event matters. Mupen can omit a nullifiable delay-slot PC (Session
3285 vs 3287 at `0x800C2B88`).

The strong `osSpTaskStartGo_recomp` override omits the weak
implementation's request clear, while `osSpTaskYielded` reports
request state even though the runtime never interrupts a task.
Session 3304's completion-aware default is the live contract;
`ROGUESQ_SP_YIELDED_REQUEST_ONLY=1` restores the old stall.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. Full failed
experiments remain in the ledger and archived overview.

Sessions 3262–3264 selected `H-SourceUnavailable` /
`H-PortPublicationSourceUnavailable` because `RecompiledFuncs/` is
absent from this repository root. Believable as a local-tree probe;
CMake's `RECOMP_FUNCS_DIR` is `../N64Recomp/RecompiledFuncs`. Session
3276 used that tree to complete the caller table.

The `swapBufferWithViMode` delay-slot width-2 request looked like a
VI-mode publisher bug that might block title 1024. Session 3277
restored hardware `$a0` order; the copied mode is width 320 and the
1024 request is still absent. Believable because the illegitimate
width-2 pointer was a real generated-code defect on the only
swap-time `osViSetMode` path.

Sessions 3288–3302 described the port's viewer stall through
`H-PortFadeOutNeverEntered`, `H-SubmitRecvBlocked`,
`H-PortSchedSendMissing`, `H-Ed0CompareSkip`, and the type-2
yield/busy-byte chain. Those findings were accurate under the
then-default request-only `osSpTaskYielded` contract and remain
reproducible with `ROGUESQ_SP_YIELDED_REQUEST_ONLY=1`, but they no
longer describe the default runtime after Session 3304. They were
believable because the runtime itself reported a requested task as
yielded; Session 3304's completion-aware default reaches E60, keeps
SENT/SRET matched, and returns from the viewer. The downstream
missing title publication is not superseded. Per-session retail
parity for that stall (s3291–s3302) is archived in PROJECT-OVERVIEW
section 54.

Session 3305 selected `H-CinematicEntryStalls` because `0x800A6618`
was silent after entry. Believable as a hang at the first
instruction; Session 3307 measured a live loop with a stuck
exit-gate, so the missing return is `H-PortLoopNoExit` not an
entry stall.

Session 3307 left the stuck 6074 `$v0` as a skip/stage/dt
predicate or a too-slow loop. Believable because retail needed
~1003 iters / 48.8 s. Session 3308 measured `$v1=0` at
`0x800AF55C` on every call, so the stage/dt path never runs.

Session 3328's `H-PortRouteStillIncomplete` interpretation treated the
1,578-entry `0x80130BB0` cinematic dispatcher pool as an audio slot pool and
read its title plateau as a causal hang. It was believable because the poll
was labelled slot-pool and the run stopped at title VI-1024. Session 3329's
same-build extended-autopilot run reached hangar VI-512, committed both 1024
and 512, and sampled the actual MusyX voice table separately; the title stop
was schedule-dependent for that recipe. The old interpretation is superseded
for this route, while the slot/status contract gap remains open.

Session 3308 treated `cinematicInitializer` `sw` at `0x800AF4B8`
as a setup writer that should have run before the first
advancer. Believable from the architecture table ("sets state
ptr at 0x800B0934"). Session 3310 measured that store at 48.1 s
from in-loop `jal 0x800A62B4`, after 972 null-ptr advancer
calls. `H-PtrZeroSkip` still describes the port; it is not by
itself the port-vs-retail mismatch.

Session 3310 left the missing port jal as an unspecified skip
of `0x800A62B4`. Believable as a single unreached call.
Session 3311 measured 626C live (`taken=0`, count < 1190) and
6274 always taken on `$a0=0`, so the jal is reached-and-skipped
by the flag-byte gate, not unreached.

Session 3311 treated retail 62B4 at 48.1 s as consistent with a
~30 Hz loop reaching count >= 1190 and bypassing 6274.
Believable from the MIPS (626C taken skips the flag). Session
3312 measured 626C `$v1=1` on all 1189 printed rows; hardware
sets skip-allow `$a0` to 1 at 48.1 s instead.

The prescribed Session 3306 30 s undriven Rice recipe does not
reach the cinematic return: first attract still has exit-gate
`$v0=0` at 30 s. Believable because Session 3283 with Start
returned at 17.0 s. Without Start the finite loop runs ~1003
iterations and returns at 48.9 s.

Session 3274's target-span writer `0x800078EC` was treated as a
candidate VI/output publisher. It is `rs_memset` (`0x800078E0`).
The span is being filled; that PC does not publish a VI mode.

Session 3278 left retail's four-slot table unevaluated at title.
Session 3279 measured every slot +8 word as 1024 while title
`1024 @ 0x00790400` was live. Session 3280 named the 1024-edge
jal as `advanceVideoFrame` `0x80018378`, already the port's 640
publisher, so a title-only overlay caller is refuted.

`--pc-phase-log-width` deferred 320-phase ticks in Session 3281.
Session 3282 armed at first VI and recovered the 2.0 s first
`menuOverlayInit` (`$a1=9`). The 17 s jal is the second
activation (`$a1=2` from `mainGameLoop` `0x8003E13C`), not a wait
inside the first call and not unused site `0x8003E0CC`. Session
3283 measured the 2.0–17 s gap as viewer return at 6.9 s then
`cinematicLoopBody` until the 17 s jal. Session 3284 measured
retail `runMenuModelViewerScreen` entry at 2.5 s and return at
6.7 s, so the port is stuck inside a screen retail also uses —
then Session 3304 unstuck the viewer and moved the stop into
the cinematic.

Session 3285's `H-RetailNoFadeStore` (zero `0x800C2B88` hits) is
superseded by Session 3287: `0x800C2B84` was live at 6.1–6.6 s
and the taken beq followed the last 2B84, so Mupen omitted the
nullifiable delay-slot PC.

Session 2791 described stale request clearing in the weak
`librecomp` `osSpTaskStartGo_recomp` as the active lifecycle.
Believable from `sp.cpp`; the linked strong override in
`src/main/upstream_compat.cpp` shadows it and does not clear
the request. Session 3303 shows clearing alone is not the
decisive contract: reporting the request as a yielded completion
causes E70/E80F, while not-yielded status restores the viewer
scheduler and submit loop.

## Evidence index

Live-thread evidence:
`scratch/agent/s3322_retail_post_swap_join.md`,
`scratch/agent/s3312_retail_cine_init_path.md`,
`scratch/agent/s3311_cine_init_jal.md`,
`scratch/agent/s3310_retail_b0934_writer.md`,
`scratch/agent/s3308_stage_advancer.md`,
`scratch/agent/s3307_cinematic_loop.md`,
`scratch/agent/s3306_retail_cinematic_exit.md`,
`scratch/agent/s3305_postviewer_continuation.md`,
`scratch/agent/s3304_yield_lifecycle_default.md`,
`scratch/agent/s3303_yield_status_ab.md`.
VI/publication: `s3276_m5_target_vi_publication_audit.md`,
`s3278_osvimode_table_census.md`,
`s3279_retail_osvimode_slots.md`.
M5 route: `s3272_m5_step1_pair.md`,
`s3246_m5_port_vi_boundary_audit.md`.
Latest route-invalid qualification: `s3347_m5_slot_status_route_invalid.md`.
M3: `s3285_freelist_live_guard.md`,
`s3249_m3_status03_audit.md`.
Use `grep -n` plus a bounded `sed` window for `PORTING-STATE.md`; never
read that multi-megabyte ledger wholesale. The soak queue is consumed
by automation; fold only new tail lines into the next audit. Session
3210 closes the generated-symbol sweep.
