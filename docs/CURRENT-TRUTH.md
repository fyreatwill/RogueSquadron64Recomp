# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
documents are listed below. Updated for session 3569 (2026-09-01).

Updated for session 3569 (2026-09-01).

Session 3569 closed the zero-DMEM-payload producer discriminator on a
target-valid standalone image arm. Hangar image-task ordinals performed
overlapping vector stores, but the exact DMEM window hashes stayed zero;
source-range writebacks then carried zero payload and zero post-write hashes.
No target-phase preclear or static `rs_memset` rows fired. This selects
`H-DmemPayloadClearOrStale` and refutes a productive CPU/vector DMEM store at
this boundary. Retail independently passed its whole-RDRAM control and
observed 674 writes in the source span, including 384 from `0x800078EC`; the
detailed producer result remains port-only. See
[M5-S3569-DMEM-PAYLOAD-PRODUCER.md](M5-S3569-DMEM-PAYLOAD-PRODUCER.md).

Session 3568 closed the immediate source-range writer discriminator on a
target-valid standalone image arm. The hangar table recorded 512
`dmem_to_rdram` rows overlapping `0x1797B0..0x179930`; payload and post-write
hashes were zero, and the corresponding later RDRAM-to-DMEM reads were zero.
CPU candidate and memset rows were absent while phase and RSP controls fired.
This selects `H-SourceRangeOtherDma`: the immediate writer is a zero-payload
DMA writeback, leaving the producer of that DMEM payload open. The oracle core
was absent in this checkout, so this is port-only evidence. See
[M5-S3568-SOURCE-RANGE-PRODUCER.md](M5-S3568-SOURCE-RANGE-PRODUCER.md).

Session 3567 closed the immediate zero-DMEM-payload producer question on a
target-valid standalone image arm. In the hangar phase, RDRAM-to-DMEM DMAs
from `0x1797B0`/`0x1798B0` into `0x6F0`/`0xCB0` carried zero hashes and zero
nonzero counts before the corresponding zero writebacks; no CPU/RSP DMEM-store
row overlapped the payload window. This selects `H-DmemPayloadRdramDma` and
leaves the producer of the source-range RDRAM bytes open. The retail oracle
independently passed its whole-RDRAM control and observed 674 writes in the
watched source span, including 384 from guest PC `0x800078EC`. See
[M5-S3567-DMEM-PAYLOAD-PRODUCER.md](M5-S3567-DMEM-PAYLOAD-PRODUCER.md).

Session 3566 closed the immediate RDRAM source-range writer question on a
target-valid standalone image arm. The exact-span writer table found nine
hangar DMEM-to-RDRAM writebacks into `0x1797B0`/`0x1798B0`; their payloads and
post-write hashes were zero, and they preceded the zero stage-2/3 reads. A
preceding CPU writer at `0x800078EC` also supplied zero stores, but it was not
the immediate stage-task writer. This selects `H-SourceRangeDmaWriter` and
leaves the zero DMEM payload producer open. It is single-source port ordering
evidence; the retail oracle independently passed its whole-RDRAM control and
observed the watched span. See
[M5-S3566-SOURCE-RANGE-WRITER.md](M5-S3566-SOURCE-RANGE-WRITER.md).

Session 3565 closed the immediate image-task staging-DMA ordering question on
a target-valid standalone image arm. After fixing a process-lifetime source-
window budget that hid hangar rows, title and hangar controls both fired. In
the same hangar task ordinal, nonzero DMEM staging was followed by a clear and
then zero stage-2/3 DMAs from `0x1797B0`/`0x1798B0`; the stage addresses and
lengths matched contract. This selects `H-ZeroDmaOrdering` and leaves the
legitimate RDRAM source-range writer open. It is single-source port evidence;
the retail oracle was unavailable. See
[M5-S3565-IMAGE-STAGING-SOURCE.md](M5-S3565-IMAGE-STAGING-SOURCE.md).

Session 3564 closed the immediate image-task DMEM-producer absence question
on a target-valid standalone image arm. Title and hangar controls fired, and
the census observed nonzero vector-store staging activity in both target DMEM
windows, followed by repeated zero-valued RDRAM-to-DMEM DMAs and zero stage
payload/destination hashes. This refutes `H-DmemProducerMissing` and selects
`H-DmemProducerWrong` at the staging/clear boundary as a single-source port
result. The next boundary is the source and ordering of those zero DMAs. See
[M5-S3564-IMAGE-DMEM-PRODUCER.md](M5-S3564-IMAGE-DMEM-PRODUCER.md).

Session 3562 closed the target-validity question for the downstream image-task
contract on a standalone image arm. The same-build pair was route-invalid in
this environment and both arms stopped at VI 640, so those target nulls are
discarded. The fixed standalone image run reached title 1024 and hangar 512
with all controls live. Image-task stage/completion/DMA rows were active, but
the stage destinations were zero-valued and remained `stage-only` with zero
PCM source/consumer joins (1,059 title rows and 1,060 hangar rows); title had
13 independent consumer-only rows plus downstream slot/key-on activity. This
selects `H-ImageTaskOutputGap` at a single-source port discriminator and moves
the next boundary to the first legitimate producer of the image-stage output.
The oracle was unavailable because its debugger core and retail ROM are absent.
See [M5-S3562-IMAGE-TASK-CONTRACT.md](M5-S3562-IMAGE-TASK-CONTRACT.md).

Session 3563 closed the immediate image-stage writer discriminator on a
target-valid standalone image arm. Title and hangar controls fired, with
2,131 and 4,152 image-stage rows respectively; stage completion and RSP DMA
controls were live. Stage-2/3 source DMEM, DMA payload, and destination
hashes were zero, and the only observed writer was the legitimate
`dmem_to_rdram` DMA. Title's occasional nonzero destination bytes were
preexisting residue overwritten by that zero DMA. No CPU writer rows fired.
This selects `H-StageWriterMissing` as a single-source port result and moves
the boundary to the producer of the image-task DMEM payload. See
[M5-S3563-IMAGE-STAGE-WRITER.md](M5-S3563-IMAGE-STAGE-WRITER.md).

Session 3561 closed the paired-contention question with a target-valid
standalone image retry. The concurrent image arm was route-invalid and
crashed at `0x8000834C`, but the same-build standalone image arm reached title
1024 and hangar 512 with route, audio-return, and PCM controls live; the
concurrent silent arm reached both targets as well. The deeper caller/HMT,
base/index, task-contract, and selector rows were absent in the image arm, so
`H-ImageInputBoundary` versus `H-ImageRouteGate` remains unevaluable. The
retail oracle was unavailable because its core and ROM were absent. Resume at
the downstream image-task contract. See
[M5-S3561-IMAGE-ROUTE-TABLE.md](M5-S3561-IMAGE-ROUTE-TABLE.md).

Session 3560 refuted shared contention as the explanation for the s3559 image
route failure. A same-build image/silent pair and a standalone image arm all
passed controls, reached title VI 1024 and hangar VI 512, and continued task
handoff, audio-return, and PCM source/consumer activity. The deeper
caller/input and route-edge table was not enabled, so
`H-ImageInputBoundary` versus `H-ImageRouteGate` remains unevaluable. No
behavior changed. See
[M5-S3560-IMAGE-ROUTE-CONTENTION.md](M5-S3560-IMAGE-ROUTE-CONTENTION.md).

Session 3559 attempted the planned same-build image-versus-silent output join
after an independent retail control. Retail passed the whole-RDRAM positive
control with 59,854 writes, reached the `0x006AB400` 512-wide hangar, and
wrote both watched source/output spans. The silent port arm reached title
1024 and captured 65 frames with task/PCM controls live. The image arm crashed
before 1024 at guest PC `0x8000834C` in the paired launch; an identical
single-image retry reached only width 640 and stalled through the phase wait.
No image target-phase rows were emitted, so the image/PCM destination join is
unevaluable and this selects `H-RouteOnly`. See
[M5-S3559-IMAGE-OUTPUT-JOIN.md](M5-S3559-IMAGE-OUTPUT-JOIN.md).

Session 3558 completed the M5 Step 1 same-build image/silent qualification on
the corrected AUTOPILOT route. Retail independently passed the whole-RDRAM
positive control and reached the target route. Both port arms reached title
1024 and hangar 512 with dispatch, return, SP-completion, and PCM controls
live. The image arm emitted 2,494 ABI rows, 7,773 DMA-range rows, and 9,693
image-stage rows; the silent arm emitted no DMA-range or image-stage rows.
Image PCM samples were nonzero while silent samples were zero, but the image
summary reported zero source/consumer matches and no named slot/status or MORT
join. This selects `H-ImageTaskContractGap`: image task progress does not yet
close the downstream task-output/slot/MORT contract. The first invalid launch
used `ROGUESQ_AUTOPILOT=1` and stalled at VI 640; it is route-invalid and its
nulls are discarded. No behavior change was made. See
[M5-S3558-AUDIO-CONTRACT-QUALIFICATION.md](M5-S3558-AUDIO-CONTRACT-QUALIFICATION.md).

Session 3557 requalified the separate s3554 `slotDispatcherIter` boundary on
the canonical real-audio/LLE-solo/spin-yield/autopilot route. Autopilot and VI
controls reached title 1024 and hangar 512; the existing table emitted 2,771
entry, 2,048 pre-call, and 2,048 post-call rows, all sampled pre-call slots
were valid KSEG0, and the SP guard was silent. No crash or `0x80007904` failure
appeared before deliberate SIGKILL. This selects `H-SlotCrashAbsent`: the
s3554 failure is route-specific, while slot input, lifecycle, and overlay
causes remain unevaluable. The evidence is single-source for this iteration;
see [M5-S3557-SLOT-DISPATCH-REQUALIFICATION.md](M5-S3557-SLOT-DISPATCH-REQUALIFICATION.md).

Session 3556 requalified the port-only boundary reported as
`musyxSynthFrame+3828` with last guest PC `0x80001B08`. Static inspection shows
that PC is the delay slot of `osRecvMesg` in `rs_malloc`; retail ground truth
passed its whole-RDRAM control but had zero executions in the corresponding
range. A same-build phase-gated port table emitted 2,759 entry, 10,068
pre-receive, 10,068 post-receive, 4,279 heap-read, and 10,068 return rows,
reached the 512 hangar phase, and had no crash before SIGKILL. This selects
`H-StaleCrashLabel` at this boundary and leaves the separate s3554 dispatcher
crash unresolved. See [M5-S3556-PRETITLE-MUSYX-ROUTE.md](M5-S3556-PRETITLE-MUSYX-ROUTE.md).

Session 3555 ran the existing regeneration-safe slot-dispatch table with
positive controls live: autopilot fired, VI widths reached 640 and 1024, and
the table emitted 2,048 entry, 2,048 pre-call, and 2,048 post-call rows in
phase 3. All pre-call rows had valid KSEG0 slot pointers and no slot-SP guard
fired. The run was route-invalid for the selected s3554 boundary: it crashed
at `musyxSynthFrame+3828` with last guest PC `0x80001B08` before the dispatcher
failure. This is single-source port evidence only; dispatcher hypotheses are
unevaluable and the next boundary is the pre-title MusyX route. See
[M5-S3555-SLOT-DISPATCH-ROUTE.md](M5-S3555-SLOT-DISPATCH-ROUTE.md).

Session 3554 re-ran the canonical real-audio/LLE-solo/spin-yield/autopilot
heap-route capture with the caller table. The autopilot control fired and the
table produced 32 rows on each known caller edge plus 32 callee-entry rows,
but all were pre-title phase 3; the run never reached VI 1024 or 512 and then
crashed in `slotDispatcherIter+3508` with guest PC `0x80007904` and SIGBUS.
This selects `H-RouteCrashes`, leaves the caller/entry join unevaluable, and
moves the next boundary to the pre-title audio-slot dispatcher route. See
[M5-S3554-HEAP-ROUTE-REQUALIFICATION.md](M5-S3554-HEAP-ROUTE-REQUALIFICATION.md).

Session 3553 added the regeneration-safe caller table for both generated
heapFreeListDequeue edges. The first corrected command used a wrong probe
path. The fixed run passed the autopilot control and logged 64 caller rows,
all pre-title phase 3 rows from edge 0x80010CD8; it stalled at VI 640 and
never reached title or hangar, so the caller/entry join is unevaluable. A
fresh full regeneration also reproduced the 640 stall, while the preserved
generated state did not restore the known target route in this capture. See
M5-S3553-HEAP-CALLER-ROUTE.md.

Session 3552 requalified the cached-head branch with a fixed canonical route.
The first attempt stalled at VI 640 and was not used as evidence. The retry
passed the autopilot/VI controls, reached title `0x00790400` and hangar
`0x006AB400`, emitted 96 phase-bucketed heap-dequeue entry rows, and emitted
zero `0x8000D704` pre-store rows before deliberate SIGKILL. This selects
`H-HeapPathAbsent`: the cached-head state is not classified as corrupt, and
the next boundary is the caller/route before the branch. See
[M5-S3552-HEAP-BRANCH.md](M5-S3552-HEAP-BRANCH.md).

Session 3551 resolved guest `0x8000D704` as the cached free-list head cleanup
store after the `0x801163B0` load at `0x8000D6F4`. The final phase-bucketed
real-audio/LLE/spin-yield/autopilot capture reached title and hangar, emitted
96 heap-dequeue entry rows but no store rows, heap guards, or crash before
deliberate SIGKILL. Port cached heads were mapped KSEG0 values; legitimacy
remains unresolved because the failing path did not execute. Retail independently
passed its whole-RDRAM control and wrote the watched cache region 48,148 times,
but that watch was not PC-attributed. See
[M5-S3551-HEAP-FAILURE.md](M5-S3551-HEAP-FAILURE.md).

Session 3550 statically corrected the HMT tuple roles and reran the canonical
real-audio/LLE/spin-yield/autopilot capture. `parseHmtMaterials` uses scalar
`a0`, output pointer `a1`, nullable material-entry pointer `a2`, and mode
`a3`; 1,557 rows produced zero required-pointer violations. The run reached
the 640-wide pre-title phase, then crashed in `heapFreeListDequeue` with
`last-guest-pc=0x8000D704`. This selects `H-HmtInputValid` at the current
discriminator and moves the next probe to the heap failure. See
[M5-S3550-HMT-ROLE-TABLE.md](M5-S3550-HMT-ROLE-TABLE.md).

Session 3549 added and ran a regeneration-safe, phase-independent entry table
for `loadDebugAssets`, `registerHmtTextureInTable`, and `parseHmtMaterials`.
The corrected port passed the HMT positive control and emitted 256 rows before
the same pre-title SIGBUS (`last-guest-pc=0x8000834C`), reaching only the
640-wide pre-title VI. The entry path is present, but the provisional
pointer-like `bad` classifier also flags legitimate scalar indices/counts, so
it does not establish malformed input. This refutes `H-HmtEntryAbsent` while
leaving valid-versus-malformed input unresolved. See
[M5-S3549-HMT-INPUT-TABLE.md](M5-S3549-HMT-INPUT-TABLE.md).

Session 3548 re-ran the canonical real-audio/LLE/spin-yield/autopilot port
route from `build/`. Startup and 320-VI controls fired, but it again SIGBUSed
before title in `parseHmtMaterials+3588`/`loadDebugAssets` with
`si_addr=0x3800007e0`; audio-dispatch, caller, base/index, destination, and
task witnesses were zero. The retained retail oracle remains phase-valid, but
the fresh oracle cannot run because this checkout lacks its required
`libmupen64plus.dylib`. This selects `H-PortAssetInput` at the current
discriminator and moves the next probe to the HMT/texture input at
`registerHmtTextureInTable`; it does not identify that input's writer. See
[M5-S3548-PORT-ROUTE-REQUALIFICATION.md](M5-S3548-PORT-ROUTE-REQUALIFICATION.md).

Session 3547 added the caller/input witness immediately around the direct
`loadTextureToMemory` call at `0x80022ACC`. The independent retail oracle
passed its whole-RDRAM control, reached title 1024 and hangar 512, and
observed the caller predecessor plus the existing texture-index PCs. The
same-build real-audio port crashed before any target phase in the existing
`parseHmtMaterials+3588`/`loadDebugAssets` path (`last-guest-pc=0x80001F88`,
SIGBUS), so all new port rows were absent. This selects `H-CaptureInvalid`
for the join; caller parity/divergence remains open. See
[M5-S3547-CALLER-INPUT-PRODUCER.md](M5-S3547-CALLER-INPUT-PRODUCER.md).

Session 3546 qualified the producer boundary for `loadTextureToMemory` with
matching phase-gated port and retail execution witnesses. Both arms passed
positive controls and reached title 1024 and hangar 512. In the hangar
texture-record family, both had `a0=0x8016BCA0`, `a1=0x8003B6E0`, and
`s3=0x2004`, but retail's formed indices began `0x37, 0x39` while the port's
began `0x25, 0x27`; the resulting record pointers also differed. This selects
`H-ProducerDivergence` and moves the boundary to the caller/input producer
before `0x8001FAA0`; the legitimate stores remain unchanged. See
[M5-S3546-BASE-INDEX-PRODUCER.md](M5-S3546-BASE-INDEX-PRODUCER.md).

Session 3545 paired a new context witness with the independent retail oracle.
Both arms passed positive controls and reached title 1024 and hangar 512.
Retail's texture-record family used record bases around `0x8016F768` in hangar
with `s2=0x1A2`, `s3=s4=0x2004`, while the port used `0x8016D440`/`0x8016D464`
with `s2=0xA8`/`0xA9`, `s3=s4=0x4004`; the effective `0x8001FAF8`
destinations therefore differ. This selects `H-PortWrongDestination`: the
writes are legitimate, but the port's base/index selection diverges upstream.
See [M5-S3545-DESTINATION-CONTRACT.md](M5-S3545-DESTINATION-CONTRACT.md).

Session 3544 extended the scalar source-span census across the pre-target
run. The port reached both target VIs with positive controls live and logged
268 hangar-span CPU stores in the preceding width-640 phase, including 104
nonzero stores. The last nonzero row was `0x8001FAF8` writing `0x000F` at
`0x17992E`; the hangar clear then entered with `pre_nz=155` and exited zero.
This selects `H-PortPrephaseCPU` and rules out carried initial state for this
run. The observed writer family is the existing texture-record scalar-store
family; the operations are legitimate writes at their executed destinations,
but this does not yet explain the higher-level source selection. See
[M5-S3544-PRECLEAR-WRITER.md](M5-S3544-PRECLEAR-WRITER.md).

Session 3543 phase-qualified the source-range state immediately before and
after the two `rs_memset` clears. Title entered `0x178C80:0x178E00` already
zero; hangar entered `0x1797B0:0x179930` with 344 nonzero bytes and exited
zero. Retail independently passed the whole-RDRAM control, reached both
phases, and wrote both ranges. This selects a real pre-clear producer for the
hangar bytes while leaving its port writer identity open; title remains a
clear-before-producer case at this boundary. See
[M5-S3543-PRECLEAR-PRODUCER.md](M5-S3543-PRECLEAR-PRODUCER.md).

Session 3541 attributed the selected source-range zeroing on the corrected
real-audio port arm: the phase-qualified `0x178C80` RDRAM span received zero
byte writes from one port writer PC, `0x800078EC` (768 rows across the two
watched spans, with no candidate-store or memset rows). Retail independently
reached title and hangar, passed the whole-RDRAM control, and showed a
different multi-PC writer family plus a nonzero final source snapshot. This
selects `H-RdramWriterPort` and moves the boundary to the host/writeback
origin of the `0x800078EC` zero-fill path. See
[M5-S3541-SOURCE-RDRAM-WRITER.md](M5-S3541-SOURCE-RDRAM-WRITER.md).

Session 3542 identified that port writer as the generated `rs_memset` byte
loop at `0x800078EC`. Its phase-qualified entry arguments are
`dst=0x80178C80, fill=0, len=0x298` in title and
`dst=0x801797B0, fill=0, len=0x298` in hangar, matching the observed zero
stores. This selects `H-WritebackOrigin` and moves the boundary upstream to
the producer of the source range before the legitimate clear; see
[M5-S3542-WRITEBACK-ORIGIN.md](M5-S3542-WRITEBACK-ORIGIN.md).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-image/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. Audio is not production-complete:
the Factor 5 image task is the qualified real-audio arm and
`ROGUESQ_AUDIO_UCODE=0`/`Broke` is the silent control.

The default route returns from the attract viewer and enters the cinematic
loop, but the stage advancer sees null `0x800B0934`; the initializer at
`0x800A62B4` is skipped while port skip-allow is zero. Retail independently
sets that byte and reaches title. Do not force the flag or bypass the state
machine.

Session 3515 independently requalified the retail route: whole-RDRAM control
fired, retail reached title and the 512 hangar, and `musyxMixActiveVoices`
entry `0x80090E04` fired in the hangar. Session 3518's same-build port pair
reached title and hangar on real audio, while the silent arm crashed pre-title
at guest PC `0x8000B650` in the `fillSampleStreamRange` family. This selects a
route-specific silent-arm failure and reopens target-phase port measurements;
it does not establish the writer of the crash input.

Session 3519 independently qualified the internal callsite boundary. Retail
and the real-audio port agree on `a0=0x80165ED0` and `a1=0x12` entering the
selector path, while the later store context still differs (`s1=0x561F` retail
versus `0x5622` port). Retail identifies `0x80029E78` as the next internal
call before the differing value is observed, selecting a later mixer-path
mutation rather than an upstream producer divergence. The writer or return
contract at that internal boundary remains open.

Session 3520 qualified the next boundary with an independent retail execution
watch and a same-build port hook. Retail executed `0x80029E78` in hangar with
`a0=0x5622`, `a1=0x8A0`, `a2=0x10`, `s1=0x80165ED0`, and `v0=0x561F`. The
port's corresponding native `osAiSetFrequency_recomp` hook passed its startup
positive control but had zero hangar rows, while the downstream selector
stores and their controls remained live. This selects an execution-path
difference at the AI boundary, but not yet its caller or equivalence.

Session 3521 labeled both generated port callsites into the native AI
primitive. Retail's independent execution watch reached hangar with caller
`0x80029E64`; the port reached the same hangar phase with producer/store
controls live, but neither labeled callsite nor the host AI-boundary witness
fired there. This selects a missing or route-gated port call at the qualified
scope, not a target-phase argument mismatch. The route gate and any other
caller remain open; see [M5-S3521-SELECTOR-CALLSITE-BOUNDARY.md](M5-S3521-SELECTOR-CALLSITE-BOUNDARY.md).

Session 3522 statically enumerated the generated tree: exactly two direct
`0x80029D20`/`osAiSetFrequency_recomp` references exist, in
`initAudioSubsystem` and `reapplyAudioConfig`, whose only generated callers
are `setDisplayMode` and `reapplyDisplayMode`. A new caller-entry witness was
built, but both port captures failed before title; the corrected run crashed
at `0x8000B650` in `fillSampleStreamRange`. The independent retail controls
remained valid and again observed one hangar execution of `0x80029E78` from
`0x80029E64`. This rules out an unenumerated direct generated caller at static
scope, but leaves the runtime route gate unevaluable until a real-audio port
run reaches hangar. See [M5-S3522-SELECTOR-ROUTE-CENSUS.md](M5-S3522-SELECTOR-ROUTE-CENSUS.md).

Session 3516 qualified the selector-store boundary independently: retail
whole-RDRAM and selector-span controls fired, with five executions at each of
`0x8008F228` and `0x8008F264` in hangar. The port context hook at those same
stores reached hangar and captured `s0=0x12`, `s1=0x5622`, and values
`0x80171E70`/`0x80173CB0`; the oracle field-dump mode emitted no comparable
register rows. The earlier `0x8009192C` candidate was absent and is not a
valid predecessor on this route, so parity/divergence remains unresolved.

Session 3523 re-qualified the real-audio port with corrected control names.
The run reached title 1024 and hangar 512; startup, title, hangar, producer,
producer-context, table, and selector-store controls were live. The known
`setDisplayMode`/`reapplyDisplayMode` route witness appeared only in title,
and neither known AI callsite nor AI-boundary row appeared in hangar, while
the two selector stores and their producer context did. This selects a
phase-gated route-path difference at the known caller scope, not a target
phase argument mismatch. It does not identify an alternate caller, which was
not instrumented in this unit.

Session 3524 independently qualified that route boundary with a phase-keyed
`runVideoFrameTick` caller/guard table. Retail again reached title and hangar
and executed `0x80029E78` in hangar. The port's positive control and title
rows were live, but no known direct caller or guard row appeared in hangar,
while producer-context, both selector stores, and mixer entry remained live.
All four generated direct callers were covered. This selects a route-path
difference at static caller scope: an enclosing route gate or a
non-generated/indirect alternate path reaches the stores. See
[M5-S3524-SELECTOR-TICK-ROUTE.md](M5-S3524-SELECTOR-TICK-ROUTE.md).

Session 3525 qualified the retail immediate-store range independently: the
whole-RDRAM control fired, retail reached title and hangar, the range executed
981 times, and `0x80029E78` fired twice in hangar from `0x80029E64`. The port
entry witness was present and its startup control fired, but the corrected
real-audio LLE/spin-yield/autopilot arm crashed before title at
`last-guest-pc=0x8000834C`; no title or hangar entry rows were available. This
selects `H-CaptureInvalid` for the port comparison and leaves alternate-entry
versus route-gate hypotheses open. See
[M5-S3525-SELECTOR-STORE-ENTRY.md](M5-S3525-SELECTOR-STORE-ENTRY.md).

Session 3526 requalified the corrected real-audio port route. Startup
controls fired; the port reached title 1024 and hangar 512. In hangar the
`allocateSongChannelArray` entry witness fired once with `a0=0x12`,
`a1=0x5622`, `a2=0`, `a3=1`; both selector-store contexts and the producer
context fired. The known caller, route, and AI-boundary rows were absent in
hangar. This validates execution of the target entry/path but does not
distinguish an alternate caller from an enclosing route gate because the
generated wrapper reports `ra=0`. See
[M5-S3526-SELECTOR-STORE-ENTRY-REQUALIFIED.md](M5-S3526-SELECTOR-STORE-ENTRY-REQUALIFIED.md).

Session 3527 completed the generated caller/route discriminator. The new
phase-keyed table covered the sole direct `allocateSongChannelArray` call at
`0x80091934` and both `initN64RspMixer` callers. Positive controls and title
1024/hangar 512 were live. In hangar, `reapplyAudioConfig` reached
`initN64RspMixer`, which reached the allocate edge with matching arguments
(`a0=0x12`, `a1=0x5622`, `a2=0`, `a3=1`); `initAudioSubsystem` had no hangar
row. This selects matching caller/route parity at the qualified generated
scope and moves the discriminator later inside the producer path. It is
single-source port evidence; see
[M5-S3527-SELECTOR-MIXER-CALLERS.md](M5-S3527-SELECTOR-MIXER-CALLERS.md).

Session 3528 qualified all three allocation edges inside
`allocateSongChannelArray` with a same-build real-audio port run and an
independent retail oracle. Effective allocation inputs and returned pointers
matched at `0x8008F0D0`, `0x8008F210`, and `0x8008F23C`; retail's `$s1=0x561F`
versus the port's `$s1=0x5622` is already an entry-argument difference, not an
allocator-return defect. This selects `H-AllocParity` and moves the active
boundary upstream to the producer of `allocateSongChannelArray`'s `a1`/`s1`.
See [M5-S3528-SELECTOR-ALLOC-BOUNDARY.md](M5-S3528-SELECTOR-ALLOC-BOUNDARY.md).

Session 3529 independently qualified the immediate mixer input. Retail's
whole-RDRAM control and PC watches observed `0x8009192C`/`0x80091934` with
loaded `a1=0x561F`; the same-build port's positive controls and title/hangar
phase buckets were live, but its load witness observed `a1=0x5622`. The port
then reached the existing allocator and selector-store controls. This selects
`H-InputLoadDivergence` and moves the boundary to the writer/source of
`MEM_W(0x80165ED0)`, not the call ABI or allocator. See
[M5-S3529-SELECTOR-INPUT-BOUNDARY.md](M5-S3529-SELECTOR-INPUT-BOUNDARY.md).

Session 3530 qualified the setup writer at `0x80091CC8`. Retail's independent
physical watch included that PC in the target phase, while the same-build
real-audio port witness fired at the store with value `0x5622` in title and
hangar; the following input load and downstream controls were live. This
selects the setup-writer/input divergence at the qualified scope and rules out
a load-only or allocator explanation. The retail writer watch did not capture
its value, so the numeric writer-value comparison is single-source. See
[M5-S3530-SELECTOR-SOURCE-WRITER.md](M5-S3530-SELECTOR-SOURCE-WRITER.md).

Session 3531 qualified the port-side setup source/return contract: the
phase-keyed witness reached title and hangar, preserved `a0=0x80165ED0` and
`a1=0x12` through the setup/mutex path, loaded AI input `0x5622`, and observed
AI return `v0=0x5622`; all downstream selector controls remained live. The
independent retail watch could not start because `libmupen64plus.dylib` is
absent in this checkout. This is single-source port evidence: it rules out an
internal port-side ABI/return clobber at the qualified path, but does not
select retail source/value parity versus divergence. See
[M5-S3531-SELECTOR-SETUP-CONTRACT.md](M5-S3531-SELECTOR-SETUP-CONTRACT.md).

Session 3532 independently qualified the retail side of that contract. The
oracle's whole-RDRAM control fired 48,922 times and the target 512 hangar phase
was reached. Retail supplied the same `a0=0x5622` at `0x80091CB8` seen on the
port, but returned/stored `v0=0x561F` at `0x80091CC4`/`0x80091CC8`, versus the
port's `v0=0x5622`. This selects a return-contract divergence after the shared
source argument and rules out a source-value, load-only, or allocator cause at
this boundary. See [M5-S3532-SELECTOR-SETUP-RETURN.md](M5-S3532-SELECTOR-SETUP-RETURN.md).

Session 3533 independently requalified the return split at the internal AI
frequency boundary. The oracle's whole-RDRAM control fired 10,000 times and
its hangar-phase watches saw `a0=0x5622` entering `0x80029D20` from
`0x80091CB8`, then `v0=0x561F` at `0x80091CC4`. The same-build real-audio port
reached title and hangar with its phase-keyed setup return row showing
`v0=0x5622`. This selects the internal callee/return contract and rules out
input-load, source-writer, and allocator divergence at this scope. A new
host-side return hook fired its startup positive control but no target-phase
row; that hook is not evidence. See
[M5-S3533-SELECTOR-AI-RETURN.md](M5-S3533-SELECTOR-AI-RETURN.md).

Session 3534 resolved the semantic contract statically from the complete
retail ELF body of `osAiSetFrequency` at `0x80029D20`. Retail rounds
`osViClock / frequency` to `dacRate`, programs the AI registers, and returns
`osViClock / dacRate`; with NTSC clock 48,681,812 and input `0x5622`, this is
`dacRate=2208` and return `0x561F`. The result exactly explains the
independent retail return. This selects `H-InternalReturnSemantics` and
refutes a later store/ABI mutation at the qualified boundary. See
[M5-S3534-AI-FREQUENCY-CONTRACT.md](M5-S3534-AI-FREQUENCY-CONTRACT.md).

Session 3535 validated the host correction in one same-build real-audio
LLE/spin-yield/autopilot run. Startup AI controls fired; title 1024 and hangar
512 were reached; phase-keyed setup rows showed input `0x5622` and return/store
`0x561F` in both target phases. This closes the AI-frequency contract edge and
preserves the qualified route. The next M5 discriminator is an output/task
comparison, not another AI-return probe. See
[M5-S3535-AI-FREQUENCY-VALIDATION.md](M5-S3535-AI-FREQUENCY-VALIDATION.md).

Session 3536 qualified the output/task contract with an independent retail
oracle and a same-build real-audio port run. Whole-RDRAM and both port phase
controls were live; retail reached title and hangar and observed the target
task/mixer PCs. The port image arm dispatched and completed tasks, performed
phase-keyed image-stage DMEM/DMA work, delivered SP completion, and produced
paired PCM source/consumer rows in both phases. Every sampled image-stage and
PCM payload was nevertheless zero (`fnv=0xF59C39C5`, `nz=0`) at both endpoints.
This selects `H-ContractGap` at the payload scope, not a missing dispatch or
completion edge. No writer/value was identified, so no output state may be
changed. See [M5-S3536-OUTPUT-CONTRACT.md](M5-S3536-OUTPUT-CONTRACT.md).

Session 3537 qualified the next output boundary with a batch oracle/port
capture. Retail passed whole-RDRAM and target-phase controls and produced
nonzero bytes in the PCM ring and image destinations. The port reached both
target phases and executed source DMA, image-stage, completion, PCM source,
and PCM consumer joins, but sampled payloads remained zero; its bounded
PCM-writer rows were DMA rows rather than a nonzero CPU writer. Retail
attribution at `0x1935E0` identified `0x800078EC` in title and
`0x80018F5C`/`0x80018F60` in hangar. This selects an output-writer/ordering
contract gap, not missing task dispatch or completion. The port-side writer
remains open; see [M5-S3537-OUTPUT-WRITER.md](M5-S3537-OUTPUT-WRITER.md).

Session 3538 completed the writer/order discriminator. Retail independently
passed the whole-RDRAM control, reached title and hangar, wrote nonzero PCM
bytes, and observed the target writer PCs. The same-build real-audio port
reached both target phases with live source, consumer, image-stage, and
completion controls. Its 1,024 phase-qualified output-writer rows were all
RSP DMA writes with zero source and destination payloads; there were no
guest/CPU writer rows, and the joins were stage-only with no ordering
violation. This selects `H-PortMissingWriter` at the nonzero payload-producer
edge and rules out a later zero overwrite or invalid capture. See
[M5-S3538-OUTPUT-WRITER.md](M5-S3538-OUTPUT-WRITER.md).

Session 3539 completed the source-writer census after extending coverage from
scalar to vector RSP DMEM stores. The first scalar-only capture was invalid
for this question despite live controls. The fixed real-audio port run
reached title and hangar, logged 2,048 bounded source-window vector-store
rows, and observed nonzero broad DMEM-span contents during the producer
sequence; later image-stage snapshots remained zero (`F59C39C5`, `nz=0`), as
did PCM output. Retail independently passed its whole-RDRAM control, reached
the target run, and wrote nonzero bytes in both watched source/state ranges.
This selects `H-PortSourceOverwritten` at the broad DMEM-span boundary and
rules out an absent RSP producer and scalar-only coverage. Exact per-window
ordering remains open; see [M5-S3539-SOURCE-WRITER.md](M5-S3539-SOURCE-WRITER.md).

Session 3540 completed the exact source-window ordering probe in the title
phase. Window 2 (`0x6F0..0x9F0`) became nonzero, then returned to the all-zero
hash before stage consumption; window 3 stayed zero. A post-copy DMA from RDRAM
`0x178C80` produced the zero state, followed by a later nonzero refill. This
selects `H-SourceWindowOverwritten` for the title-phase port path and moves the
active boundary to the writer of RDRAM `0x178C80`. The run did not reach 512
hangar, so this exact ordering is single-source title evidence; session 3539's
retail nonzero-writer result remains the independent second line. See
[M5-S3540-SOURCE-WINDOWS.md](M5-S3540-SOURCE-WINDOWS.md).

M5 remains the active engineering thread. The status-03 worker/clear contract,
task ABI, completion/delivery, callback table, field348 input-to-clear edge,
send/receive zero-message boundary, first consumer boundary, source-table
selection, and corrected selector-table store/value boundary are closed at
their qualified scopes. The live gap is the producer/context contract before
the selector stores at `0x8008F228` and `0x8008F264`:

- Retail and port agree on hangar writer PCs and stored values
  (`0x80171E70`/`0x80173CB0`), but writer `s1` differs (`0x561F` vs `0x5622`).
- Session 3512's guessed retail predecessor watches were absent despite live
  stores, so that proposed join is invalid; do not repeat those addresses.
- The next useful boundary must be a genuinely new producer/context witness,
  qualified by the same independent retail controls and the port's title and
  hangar phase buckets.
- The generated host wrapper's `ra=0` remains unresolved, but prior joins rule
  out wrapper/ABI clobber at the qualified `rs_free` and source boundaries.

M5 source/output evidence establishes that retail writes legitimate nonzero
source/state values where the port previously wrote zero or selected an
`0x80110xxx` state family. The port table-selection witness later matched the
retail table family; the remaining selector writer-input context is therefore
the active discriminator. No audio state, selector, task field, or output is
to be rewritten as a diagnostic mitigation.

## Next steps

0. M5 Step 3 image-task source DMA: identify the producer/data source that
   supplies the zero bytes loaded from `0x1797B0`/`0x1798B0`. Session 3569
   selected `H-DmemPayloadClearOrStale`: overlapping vector stores were
   nonproductive, and no target-phase preclear or static memset fired before
   the zero writebacks. Census the source DMA's upstream RDRAM writer and
   payload, retaining task ordinal and phase joins. Do not rewrite output or
   PCM state.

1. Keep the s3554 slot-dispatch failure parked as route-specific absence. The
   s3557 table had valid KSEG0 inputs and no `0x80007904` failure, so do not
   add a slot guard or rewrite slot data. Revisit only with a new route
   discriminator.
2. Keep the HMT role result as valid at this discriminator: nullable `a2` is
   an intended branch, and the sampled required pointers were mapped. Do not
   repeat the provisional non-pointer scalar classifier or treat its old
   `bad` rows as malformed-input evidence.
3. Keep the silent-arm `fillSampleStreamRange` crash as a separate route
   defect. Do not infer target-phase behavior from the silent arm or treat it
   as evidence that the real-audio mixer boundary is broken.
4. Keep the silent forced-LLE/no-spin result as a pre-title route-blocker
   baseline; do not repeat that arm unchanged.
5. Keep Sessions 3494–3498 real-audio route results, Session 3492 dispatch,
   Session 3488 silent qualification, and Sessions 3482–3486 producer/pointer
   captures as baselines; do not repeat unchanged captures.
6. Keep the controlled phase/PC/ordinal join rule: sequential animated-scene
   A/B rows are not evidence. A missing positive control makes a comparison
   unevaluable; matching fields close a boundary and the first divergent field
   selects the next producer edge.
7. M5 Step 3 is now the active boundary: the image route survived paired
   contention, but its deeper input-versus-route edge remains open. The old
   image task/output join is parked until that edge is qualified. The
   AI-frequency contract is now corrected;
   `docs/M5-AUDIO-PLAN.md` is complete;
   configured-host PatchesLib validation is unavailable in this Unix checkout.
8. After M5 closes or a new discriminator is found, resume only systematic M3
   idiom-class audits. Keep retail-entry, hangar `0x8000` Y/accumulator, and
   SP-yield/MORT publication threads parked. Generated-symbol renaming remains
   last priority and closed at its measured scope.

### Active hypothesis table

The active work unit is now M5 Step 3 source-DMA payload qualification.
Session 3569 selected `H-DmemPayloadClearOrStale`: target-phase overlapping
vector stores left the exact DMEM windows zero, no clear or static memset row
fired, and the writeback payload remained zero. The next witness must identify
the upstream RDRAM writer/data source for the zero source DMA. Retail supplied
independent source-span activity; the detailed producer selection is port-only.

Session 3567 selected `H-DmemPayloadRdramDma`: target-phase RDRAM-to-DMEM
DMAs sourced `0x1797B0`/`0x1798B0` into the image-task payload windows with
zero hashes, and no overlapping CPU/RSP DMEM store was observed. The next
witness must identify who produced those source-range RDRAM bytes before the
DMA. Session 3566's `H-SourceRangeDmaWriter` remains the immediate writeback
boundary; no behavior changed.

Session 3564 selected `H-DmemProducerWrong`: target DMEM windows received
nonzero vector-store staging activity, but repeated zero-valued source DMAs
preceded zero stage payload and destination hashes. The next witness must
identify the source and ordering of those zero DMAs. Session 3563's
`H-StageWriterMissing` result is superseded at this narrower scope because its
writer census did not include the upstream DMEM stores; no behavior changed.
Session 3562
selected `H-ImageTaskOutputGap`: a target-valid standalone image arm had zero
valued stage rows with no source/consumer joins, despite completion/DMA and
title downstream consumer activity. The next witness must identify the first
legitimate producer of the stage destination. Session 3560
refuted `H-SharedContention`: paired and standalone image arms reached title
and hangar with task/return/PCM controls live. The next witness must split
`H-ImageInputBoundary` from `H-ImageRouteGate` using the deeper caller/input/
route table. Session 3558 selected `H-ImageTaskContractGap`: the corrected
same-build image/silent pair reached title and hangar; image DMEM/DMA/stage
activity and nonzero PCM were present, while the image-stage summary had zero
source/consumer matches and no named slot/status or MORT join. That downstream
join remains parked until the route edge is qualified. Session 3557
selected `H-SlotCrashAbsent` for the separate s3554 slot-dispatch failure:
the route-valid table had valid KSEG0 inputs and no failing consumer, so the
slot input/lifecycle/overlay hypotheses remain parked. Session 3556
selected `H-StaleCrashLabel` at the previously reported `0x80001B08` boundary:
that PC is the delay slot of `osRecvMesg` in port `rs_malloc`, and a validated
same-build route completed through hangar with the new table live. The next
witness must return to `slotDispatcherIter` guest PC `0x80007904` and join its
caller/entry route, without rewriting heap, audio, PCM, image-task, output, or
texture state. The `0x80091CC8` internal return contract is closed by Sessions
3534–3535. The silent-arm route defect is parked separately.

Session 3541 moved the live boundary to the port's zero-fill writer origin.
The corrected writer hook records zero-valued writes at `0x178C80` from one
port PC (`0x800078EC`), while retail independently records a distinct writer
family and a nonzero final range. The next discriminator is the source and
writeback contract behind that port PC. Session 3542 closed that identity:
the zero is a deliberate `rs_memset` clear of the source range, so the active
discriminator is now the pre-clear producer.

Session 3539 moves the live boundary upstream into the image-task DMEM source.
Vector stores execute in both source-window address classes and broad-span
contents become nonzero during that sequence, but the stage-2 source snapshot
is zero. The next discriminator is exact per-window ordering, not another
scalar-store census.

For the silent-arm route:

- `H-SilentRouteCrash`: the silent route has a route-specific failure in the
  `fillSampleStreamRange` family while real audio reaches the target phase.
- `H-SharedRouteBlocker`: both arms stop before title, selecting a shared
  blocker.
- `H-RealAudioRouteFailure`: real audio fails before the target phase.
- `H-CaptureInvalid`: startup, oracle, or phase controls fail.

Session 3518 selected `H-SilentRouteCrash`: oracle controls passed, the silent
arm crashed pre-title at `0x8000B650`, and the real image arm reached title and
hangar. The crash origin remains unresolved.

For the next upstream argument boundary:

- `H-AllocParity`: all three allocator edges match retail through their
  returns, so the divergence is upstream of the callee entry.
- `H-InputLoadDivergence`: session 3529 observed retail load `0x561F` versus
  port load `0x5622`, selecting the source/writer edge at `0x80165ED0`.
- `H-InputLoadParity`: the loaded value matches but differs before the call,
  selecting an intervening generated instruction or wrapper contract.
- `H-CaptureInvalid`: a same-run positive control or phase-matched writer
  control fails; the join is unevaluable.

Session 3530 selected `H-SetupWriterInputDivergence` at the qualified scope.
The next unit qualified the writer's source arguments/return contract rather
than repeating the same store census.

Session 3532 selected `H-SetupWriterReturnDivergence`: retail and port agree on
the `0x5622` AI-frequency input, but retail returns/stores `0x561F` while the
port returns/stores `0x5622`. The next boundary is the internal AI-frequency
callee/host return path.

Session 3519 selected `H-ContextProducerParity` at the callsite and
`H-LaterContextMutation` for the first observed value difference: retail and
port agree on the call inputs, but retail's internal call returns/feeds
`0x561F` while the port store context remains `0x5622`. The next discriminator
is the phase-matched context at `0x80029E78` and the following store. A differing
call input selects that function's producer; matching input with differing
output/store selects its internal contract or a subsequent mutation; failed
controls make the capture invalid.

Session 3520 selected `H-PortBoundaryAbsentInHangar`: the retail watch fired in
hangar, the port hook's startup positive control fired, and the port hook had
zero hangar rows while downstream stores remained live. This is a path result,
not a proof that the host primitive is the exact instruction equivalence.

Session 3521 selected `H-PortCallMissing`: both labeled generated calls had
startup controls but zero hangar rows, while retail's independent watch and the
port producer/store controls were live. The next discriminator is a route-gate
or alternate-caller census, not another repeat of these two callsites.

Session 3523 selected `H-RouteGate` at the qualified caller scope: the
real-audio port reached title and hangar with live producer/store controls,
but the known display-mode route witness and known AI callsite/boundary rows
were title-only or absent in hangar. This is a phase-gated path result, not a
proof that an alternate caller exists; the next discriminator is the enclosing
`runVideoFrameTick` branch/caller or a separately instrumented alternate path.

Session 3527 supersedes that route-gate interpretation at the generated
caller scope: the new hangar rows show a live `reapplyAudioConfig` route and
the sole direct allocate edge with matching arguments. The remaining open
question is the first producer/context divergence between mixer entry and the
selector stores.

Session 3528 narrows that open question upstream: the three allocator edges
are parity-qualified by retail and port, so no allocator or freelist
mitigation is warranted. The legitimate pointer difference is already
present in the callee's entry argument.

Session 3514 adds a retail-qualified mixer-entry candidate at `0x80090E04`,
but the port did not reach its target phase on either tested arm. See
[M5-S3514-MIX-ENTRY-BOUNDARY.md](M5-S3514-MIX-ENTRY-BOUNDARY.md).

Session 3515 independently requalified that retail entry in the hangar with a
positive control; see [M5-S3515-ORACLE-ROUTE.md](M5-S3515-ORACLE-ROUTE.md).

Session 3518 requalified the real-audio port route and isolated a silent-arm
pre-title crash; see [M5-S3518-AUDIO-ROUTE-PAIR.md](M5-S3518-AUDIO-ROUTE-PAIR.md).

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and similar defenses are safety mechanisms, not explanations.
Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. The image task is the real-audio
arm; the silent arm returns `RspExitReason::Broke`. Do not infer audio behavior
from a route that fails to reach the target phase.

Every instrument needs a ground-truth request first, a same-run positive
control, a phase-scoped budget, and two independent evidence lines before its
result becomes current truth. Phase-gate animated comparisons on VI
transitions. Batch A/B arms in one build and run. A counter without a positive
control is worthless.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

The runtime's known architectural facts remain: Factor 5 custom opcodes are
documented in `docs/factor5-gbi.md`; MusyX task data cannot be sent to stock
`aspMain`; DP messages use the external-message drain; C++ exceptions must
propagate to the outer recovery boundary; and RT64's interpreter safety limit
prevents a missing DL terminator from becoming an access violation.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield/viewer-stall chain describes only the old diagnostic
arm; completion-aware default behavior returns from the attract viewer. The
old interpretation of the 1,578-entry cinematic pool as an audio-slot pool was
superseded by the MusyX voice-table measurement.

The earlier claim that `0x8002BEEC` was the retail JAL dispatch to `0x800078EC`
is route-dependent and unreconciled; later adjacent-PC captures found zero at
both addresses while `0x800078EC` was live. Do not treat it as a writer without
a new independent discriminator.

Session 3512's zero predecessor callbacks are not evidence for parity,
divergence, or later mutation. The stores and controls were live, but the
chosen predecessor addresses were not phase-observable; this invalidates that
measurement only, not the qualified writer-context divergence.

Session 3516's `0x8009192C` zero is likewise a capture-invalid predecessor
measurement, not evidence about selector parity or divergence. The corrected
live-store watches were positive, and the port store context was observed, but
the oracle did not provide a matching register tuple.

## Evidence index

Latest output boundary:

- [M5-S3565-IMAGE-STAGING-SOURCE.md](M5-S3565-IMAGE-STAGING-SOURCE.md)
- [M5-S3566-SOURCE-RANGE-WRITER.md](M5-S3566-SOURCE-RANGE-WRITER.md)
- [M5-S3567-DMEM-PAYLOAD-PRODUCER.md](M5-S3567-DMEM-PAYLOAD-PRODUCER.md)
- [M5-S3564-IMAGE-DMEM-PRODUCER.md](M5-S3564-IMAGE-DMEM-PRODUCER.md)
- [M5-S3539-SOURCE-WRITER.md](M5-S3539-SOURCE-WRITER.md)
- [M5-S3536-OUTPUT-CONTRACT.md](M5-S3536-OUTPUT-CONTRACT.md)
- [M5-S3552-HEAP-BRANCH.md](M5-S3552-HEAP-BRANCH.md)

Latest selector boundary:

- [M5-S3533-SELECTOR-AI-RETURN.md](M5-S3533-SELECTOR-AI-RETURN.md)
- [M5-S3534-AI-FREQUENCY-CONTRACT.md](M5-S3534-AI-FREQUENCY-CONTRACT.md)
- [M5-S3530-SELECTOR-SOURCE-WRITER.md](M5-S3530-SELECTOR-SOURCE-WRITER.md)
- [M5-S3532-SELECTOR-SETUP-RETURN.md](M5-S3532-SELECTOR-SETUP-RETURN.md)
- [M5-S3529-SELECTOR-INPUT-BOUNDARY.md](M5-S3529-SELECTOR-INPUT-BOUNDARY.md)
- [M5-S3514-MIX-ENTRY-BOUNDARY.md](M5-S3514-MIX-ENTRY-BOUNDARY.md)
- [M5-S3528-SELECTOR-ALLOC-BOUNDARY.md](M5-S3528-SELECTOR-ALLOC-BOUNDARY.md)
- [M5-S3525-SELECTOR-STORE-ENTRY.md](M5-S3525-SELECTOR-STORE-ENTRY.md)
- [M5-S3519-SELECTOR-CALLSITE-CONTEXT.md](M5-S3519-SELECTOR-CALLSITE-CONTEXT.md)
- [M5-S3520-SELECTOR-AI-BOUNDARY.md](M5-S3520-SELECTOR-AI-BOUNDARY.md)
- [M5-S3521-SELECTOR-CALLSITE-BOUNDARY.md](M5-S3521-SELECTOR-CALLSITE-BOUNDARY.md)
- [M5-S3516-SELECTOR-STORE-CONTEXT.md](M5-S3516-SELECTOR-STORE-CONTEXT.md)
- [M5-S3517-SELECTOR-PRODUCER-CONTEXT.md](M5-S3517-SELECTOR-PRODUCER-CONTEXT.md)
- [M5-S3512-SELECTOR-PREDECESSOR-BOUNDARY.md](M5-S3512-SELECTOR-PREDECESSOR-BOUNDARY.md)
- [M5-S3511-SELECTOR-TABLE-PHASE-JOIN.md](M5-S3511-SELECTOR-TABLE-PHASE-JOIN.md)
- [M5-S3510-SELECTOR-TABLE-PHASE-MISMATCH.md](M5-S3510-SELECTOR-TABLE-PHASE-MISMATCH.md)
- [M5-S3509-SELECTOR-TABLE-PORT-WRITER.md](M5-S3509-SELECTOR-TABLE-PORT-WRITER.md)
- [M5-S3508-SELECTOR-TABLE-WRITER.md](M5-S3508-SELECTOR-TABLE-WRITER.md)

Earlier active M5 boundaries:

- [M5-S3473-PORT-STATE-JOIN.md](M5-S3473-PORT-STATE-JOIN.md)
- [M5-S3463-SOURCE-VALUE-JOIN.md](M5-S3463-SOURCE-VALUE-JOIN.md)
- [M5-S3445-STATE-POINTER-ENTRY.md](M5-S3445-STATE-POINTER-ENTRY.md)
- [M5-S3444-STATE-POINTER-PRODUCER.md](M5-S3444-STATE-POINTER-PRODUCER.md)
- [M5-S3410-FIELD348-INPUT.md](M5-S3410-FIELD348-INPUT.md)
- [M5-S3376-ZERO-PCM-SOURCE.md](M5-S3376-ZERO-PCM-SOURCE.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3519 remain in the append-only ledger; archived background and
closed boundary detail remain in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
Use bounded `grep`/`sed` windows for `PORTING-STATE.md`, never read it whole.
The soak queue is consumed by automation; fold only new tail lines into the
next audit.
