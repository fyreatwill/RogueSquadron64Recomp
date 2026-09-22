# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background and closed M3 audits are in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
Updated for session 3714 (2026-09-21).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-audio/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. The image task is the qualified
real-audio arm; `ROGUESQ_AUDIO_UCODE=0` / `Broke` is the silent control. Audio
is not production-complete.

The active M5 Step 4 boundary is the image-task source range
`0x1797B0..0x179930`. The port's target handoff performs a zero-fill from
`0x800078EC` (`rs_memset`, commonly `dst=0x801797B0, fill=0, len=0x298`)
followed by zero source-DMA payloads. Retail reaches the same target phase,
writes the watched source span, and repeatedly calls `0x800078E0` with
`a2=0x80` and changing structure pointers from `0x800C825C`; its source
writer is `0x800078EC` before the first target VI. The exact input-DMA ordering
and ownership is now classified: the qualified input-DMA capture joined all
244 absent-generation hangar source rows to an earlier/equal input task
identity, with no later or missing/contradictory joins. The payload capture
then showed that the selected input task already carries the zero payload;
the remaining question is its pre-DMA writer or descriptor boundary.

Session 3690 added the input-DMA event before output DMAs could overwrite the
thread-local identity. Session 3691 added pre-copy payload fields. In the
qualified real-audio arm, all 512 hangar source rows had equal zero
input/source/DMEM FNV and nonzero fields, and equal input/source task-data
pointers. This selects `H-StaleInputPayload` and refutes post-input overwrite
and pointer-only staleness for that class. See
[M5-S3691-STALE-INPUT-PAYLOAD.md](M5-S3691-STALE-INPUT-PAYLOAD.md).

Session 3692 added a complete scalar guest-store witness. Retail had hangar
writers at `0x800078EC`, `0x80007670`, and `0x8001F...` sites. The port had
384 title zero-fill rows, all at `0x800078EC`, and every one of 3,178 hangar
input rows still carried that title writer as its latest snapshot; no hangar
scalar writer ran. This refutes an immediate port-side pre-DMA clear and
identified the port-versus-retail hangar-writer gap as the next boundary. See
[M5-S3692-INPUT-WRITER-BOUNDARY.md](M5-S3692-INPUT-WRITER-BOUNDARY.md).

Session 3693 closed the immediate writer-class boundary. The qualified port
had 512 hangar DMA-to-RDRAM source-range rows, all with zero payload and zero
post-write span, while its DMEM-side writer census was active. This selects
`H-NonScalarWriterPath`: the hangar path is visible, but the DMA payload is
already zero. The next boundary is the DMEM payload producer, not a missing
guest scalar writer. See [M5-S3693-DMA-WRITER-BOUNDARY.md](M5-S3693-DMA-WRITER-BOUNDARY.md).

Session 3694 added a predecessor join for DMEM scalar/vector stores, but the
qualified real-audio retry reached title and hangar without emitting the
target source-range callback; only the RSP source-hook positive control
fired. The first paired attempt omitted `ROGUESQ_LLE_UNGATED=1` and was
invalid. No DMEM producer hypothesis is selected. The optional transition
logger was corrected so it cannot bypass the target-phase row cap. See
[M5-S3694-DMEM-PRODUCER-JOIN.md](M5-S3694-DMEM-PRODUCER-JOIN.md).

Session 3695's pre-320 real-audio stall did not reproduce in the fixed s3696
paired run. Both real and silent arms reached VI 1024 and 512 and both RSP
positive controls fired. With `ROGUESQ_LOG_M5_SOURCE_WRITER=1`, the real arm
emitted 2,048 DMEM-store rows and 512 source-range writer rows; every sampled
DMEM value and source/post-write payload was zero, while all source rows had a
predecessor sequence and 139/512 overlapped the output range. The silent arm
had no target DMEM or source-range rows. This refutes a stable audio-pump
route gate and reopens the DMEM predecessor classification; it does not select
which producer explanation is correct. See
[M5-S3696-AUDIO-PUMP-QUALIFICATION.md](M5-S3696-AUDIO-PUMP-QUALIFICATION.md).

Session 3697 classified the qualified predecessor table. Retail's independent
oracle positive control fired, and its hangar writer PCs were `0x800078EC`
(768), `0x80007670` (172), `0x8001E2C0` (11), and the `0x8001F...` family (107);
the sampled `0x800078EC` scalar stores were legitimately zero. The port's
positive controls fired, with 512 hangar source rows: all payload/post-write
bytes were zero, all 512 latest predecessors were zero vector stores, but only
147/512 overlapped the output window and 274/512 belonged to a newer route
ordinal. This selects `H-DMEMWriterWrongWindow` for the latest predecessor and
keeps `H-RetailSourceDifferent` open. See
[M5-S3697-DMEM-PREDECESSOR-CLASS.md](M5-S3697-DMEM-PREDECESSOR-CLASS.md).

Session 3698 added a per-byte coverage-aware DMEM table. The qualified run
reached both target phases, fired the RSP and DMEM controls, and emitted 512
hangar source rows. Covered bytes were zero vector stores, but 255 rows had no
observed writer for exactly `0xCC0..0xCD0`. This selects
`H-DMEMProducerAbsent` for the observed writer census and refutes a complete
`H-ZeroDMEMProducer` explanation; the retail-vs-port writer mismatch remains
open. See [M5-S3698-DMEM-COVERAGE-GAP.md](M5-S3698-DMEM-COVERAGE-GAP.md).

Session 3699 added the missing RDRAM-to-DMEM DMA writer path. The independent
retail run passed its whole-RDRAM control and reached title and hangar. The
qualified port emitted 512 hangar source rows; 255 used the `0xCB0` window,
and the formerly absent `0xCC0..0xCD0` coverage was a zero-valued DMA writer
on all of them. This selects `H-UninstrumentedDMEMWriter` and refutes
`H-GenuineZeroGap`; the remaining boundary is the DMA's zero RDRAM source
payload and its producer/layout. See
[M5-S3699-DMEM-DMA-COVERAGE.md](M5-S3699-DMEM-DMA-COVERAGE.md).

Session 3700 joined each zero output source to its RDRAM-to-DMEM source DMA.
All 512 hangar rows used the expected `0x1798B0..0x179A48` source descriptor,
with zero source bytes and zero output payload; the paired port writer snapshot
was still the title `0x800078EC` zero-fill. Retail independently showed
hangar writers at `0x80007670`, `0x8001E2C0`, and the `0x8001F...` family.
This selects `H-RetailSourceDifferent` and refutes a descriptor mismatch for
the measured range. See [M5-S3700-DMA-SOURCE-PRODUCER.md](M5-S3700-DMA-SOURCE-PRODUCER.md).

Session 3701 extended the source-side qualification through `0x179A48`.
Session 3702 removed the target-route gate from the source-range scalar census.
The paired port arms each showed 652 stores, including the retail families
`0x80007670`, `0x8001E2C0`, and `0x8001F...`; the later `0x800078EC` zero-fill
also ran. The output source DMA still carried zero bytes. This selects
`H-PrePhaseScalarProducer`: the producer exists before route publication, then
the legitimate zero-fill overwrites the range before the output DMA. See
[M5-S3702-SOURCE-PRODUCER-OVERWRITE.md](M5-S3702-SOURCE-PRODUCER-OVERWRITE.md).

Session 3703 joined the final source-store sequence to qualified output DMAs.
In both port arms the final observed writer was the 384-store, zero-valued
`0x800078EC` fill; the real arm then emitted 512 zero source and post-DMA
payload rows, with no later nonzero writer or route mismatch. Retail passed its
whole-RDRAM control and wrote the target span. This selects `H-ClearIsFinal`
and refutes `H-ProducerAfterClear` and `H-DescriptorOrdering` at the measured
boundary. See [M5-S3703-SOURCE-CLEAR-ORDER.md](M5-S3703-SOURCE-CLEAR-ORDER.md).

Session 3704 joined the target clear call itself. In both paired arms the
target call came from `0x8008F2CC` with the expected `dst=0x801797B0`,
`len=0x298`, and zero value. The clear was on the preceding route ordinal and
the real arm's later `0x1798B0..0x179930` source-DMA payload remained zero.
This selects `H-ClearLegitimateButEarly` and refutes `H-ClearWrongObject` and
`H-ProducerAfterClear` at the measured boundary. See
[M5-S3704-CLEAR-LEGITIMACY.md](M5-S3704-CLEAR-LEGITIMACY.md).

Session 3705 repeated the paired qualification with the full handoff table.
Both arms reached hangar and joined the same clear contract; the real arm's
clear was at route ordinal 525 and its later source/output rows were at
ordinals 669–670 with zero payload. The generated writer-setup probe was
absent, so allocation-object identity remains unevaluable rather than null.
This confirms ordering but does not split different-object from early-clear.
See [M5-S3705-CLEAR-HANDOFF.md](M5-S3705-CLEAR-HANDOFF.md).

Session 3706 restored the writer-setup injection through the regeneration
fixup, then requalified both paired arms. The target setup used the same
`0x801797B0`/`0x298` object as the clear; the five setup-step rows and the
source controls were positive. The final observed writer remained the
legitimate zero-valued `0x800078EC` fill before later zero input/output DMAs.
This selects `H-ClearTooEarly` and refutes different-object and post-clear
writer explanations at the measured boundary. See
[M5-S3706-WRITER-SETUP-REQUALIFICATION.md](M5-S3706-WRITER-SETUP-REQUALIFICATION.md).

Session 3707 added the clear-input/state table. Both paired arms fired its
positive control and reached identical target setup registers with identical
nonzero pre-clear object words; existing static-clear rows independently
reported zero fill. The real arm still produced zero source DMAs and the
silent arm emitted none. This selects `H-ProducerInputZero` and refutes an
already-zero shared object at this boundary. See
[M5-S3707-CLEAR-INPUT.md](M5-S3707-CLEAR-INPUT.md).

Session 3708 added the phase-gated branch table for the clear caller. The
independent retail oracle passed its whole-RDRAM control and executed all four
candidate PCs in the target phase. Both port arms had the same one-entry
`0x8008F108` branch, 18-entry `0x8008F168` loop, terminating zero, and
not-taken `0x8008F1C4`, with matching allocator inputs and route shape. This
selects `H-ClearBranchRoute` and refutes caller-state and post-clear-ordering
explanations at the measured boundary. See
[M5-S3708-CLEAR-BRANCH.md](M5-S3708-CLEAR-BRANCH.md).

Session 3709 added one phase-gated caller/allocator table. The independent
retail oracle passed its whole-RDRAM control and executed both `0x80091934`
and `0x8008F0A0` in the target route with `a1=0x561F`, `a2=0`, `s0=0x12`,
and `s2=1`. Both paired port arms fired the probe controls and matched that
selector tuple at the caller and allocator entry; the real/silent route
ordinals differed only by their arm-local publication counts (`525` vs `519`).
This selects `H-CallerSelectorRoute`, refutes caller-state divergence, and
moves the boundary to the writer/source of `MEM_W(0x80165ED0)` loaded at
`0x8009192C`. See [M5-S3709-CALLER-ROUTE.md](M5-S3709-CALLER-ROUTE.md).

Session 3710 joined that selector input to its source writer. In one paired
port build/run, both real-audio and silent arms reached title and hangar; the
phase-gated source witness saw `0x80091CC8` write `0x561F` to `0x80165ED0`,
the `0x8009192C` load read `0x561F`, and the caller preserved it. Independent
retail evidence identifies the same source PC and `v0=0x561F` at the setup
stores. This selects `H-SelectorInputWriterParity` and refutes writer
divergence and stale-load explanations at this boundary. The next boundary
is the internal AI-frequency call/return contract. See
[M5-S3710-SELECTOR-INPUT-WRITER.md](M5-S3710-SELECTOR-INPUT-WRITER.md).

Session 3711 qualified that internal contract. The valid phase-gated port run
reached title and hangar, passed the RSP/image controls, and recorded
`0x80029E78` with `a0=0x5622`, followed by `v0=0x561F` at the AI return and
the selector setup store. Independent retail evidence recorded the same input
and result, while the retail ELF gives the rounded NTSC DAC-rate calculation.
This selects `H-AIFrequencyReturnParity` and refutes return divergence and
producer-state divergence at this boundary. The image discrepancy remains
downstream. See [M5-S3711-AI-FREQUENCY-QUALIFICATION.md](M5-S3711-AI-FREQUENCY-QUALIFICATION.md).

Session 3712 qualified the next host boundary in a same-configuration paired
run. Real-audio and silent arms both reached title and hangar, passed the RSP
positive control, and produced identical host `set-frequency` and first PCM
consumer rows at `22047 Hz` (67 state rows per arm). Only real audio produced
image-stage rows. This selects `H-AIStateParity` for the port host side effect
and first consumer, and refutes audio-route-specific host-frequency divergence;
the image discrepancy remains downstream. The oracle retry passed its
whole-RDRAM control but ended before a target 512-phase post-return row, so it
adds no new retail-side-effect observation. See
[M5-S3712-AI-STATE-CONSUMER.md](M5-S3712-AI-STATE-CONSUMER.md).

Session 3713 qualified post-PCM drain in a valid same-build paired run. Both
arms reached title and hangar and passed RSP controls. At hangar, real audio
had 43 `set-next` drain rows with raw SDL queue depth 0–4581 bytes; silent had
132 rows with depth 741–4581 bytes. Both arms had zero PCM source/consumer
joins, and only real audio had image-stage rows. No target-phase guest
`get-status`/`get-length` call occurred. This selects
`H-AudioDrainDivergence` for the measured host-side boundary, but leaves
`H-AudioDrainNotConsumed` open. Raw and adjusted depth are two fields from one
port source, so this is single-source evidence; no retail drain parity claim
is made. See [M5-S3713-POST-PCM-DRAIN.md](M5-S3713-POST-PCM-DRAIN.md).

Session 3714 repeated the post-PCM drain qualification with the independent
retail oracle and a corrected same-build port pair. Retail passed its
whole-RDRAM control and showed a 1:1 hangar chain of 4,335 `set-next`, device-
busy, and success executions, with zero reject-branch executions and no named
status/length execution. Both port arms reached hangar and passed phase/RSP
controls. Real audio had 114 target `set-next` rows, queue depth 741–3813,
and 471 image-stage rows; silent had 29 rows, depth 741–4581, and zero
image-stage rows. Both had zero target status/length calls and zero nonzero PCM
rows. This confirms `H-AudioDrainDivergence` at the host queue/cadence
boundary, rules out the guest status/length shims as the measured discriminator,
and leaves the actual host consumer/callback writer open. See
[M5-S3714-POST-PCM-DRAIN-QUALIFICATION.md](M5-S3714-POST-PCM-DRAIN-QUALIFICATION.md).

The current source/stage picture is: title source rows are same-generation;
the hangar minority is generation-absent, uses `0x80171E70`, and later stages
reuse that pointer under a later route generation. Session 3686 classified
244/244 measured absent rows as later-route reuse, with zero same-route,
contradictory, or missing classifications. Sessions 3680–3683 establish that
route publication can lag source reads, while stage callbacks observe the
current publication. Do not infer ownership from pointer identity or host log
order alone.

Do not force the cinematic flag at `0x800B0934`, bypass the state machine, or
rewrite task, audio, PCM, selector, or output state. The default route's null
stage-advancer input is a known route/configuration issue; the validated
real-audio route is the comparison arm.

## Next steps

The backlog is one monotonic sequence. Work only the first applicable item.

1. **M5 Step 4 — identify the host drain consumer.** Session 3714 confirms
   `H-AudioDrainDivergence`: retail has a busy/success set-next chain, while
   the paired port arms differ in host queue depth and cadence; neither port
   arm calls guest status/length, and both have zero nonzero PCM rows. Add one
   phase-gated host table covering enqueue, SDL callback/dequeue, queue depth,
   and first image-stage join, with positive controls in both arms. Do not
   alter selector, clear, task, audio route, or payload state. Retail queue
   depth remains unmeasured.

2. **M3 parked audit — `rs_zcfree` incoming `$a0` at `0x80005268`.** Start
   only when M5 is unavailable or closed. Audit the complete idiom class,
   identify the writer and legitimacy of the value, and land a guard only if
   a concrete invalid writer is found. The closed `rs_free` audits and their
   evidence are archived in PROJECT-OVERVIEW §56; do not re-audit them.

3. **Generated-symbol renaming sweep.** Resume only after M5 is closed and
   M3 has no new discriminator. Use one bounded region/census per session and
   preserve the slug `generated-symbol-renaming-sweep` for that campaign.

## Active hypothesis table

| Hypothesis | Status and discriminating evidence |
|---|---|
| `H-LaterRouteOwnsInput` | Refuted for 244/244 measured absent rows at s3690; no input-DMA key joined the later task. |
| `H-StaleInputAcrossReuse` | Selected at s3690: 244/244 absent-generation hangar rows joined an earlier/equal input task identity. |
| `H-StaleInputPayload` | Selected at s3691: 512/512 hangar rows had equal zero input/source/DMEM payloads and equal task pointers. |
| `H-MissingGeneratedWriter` | Superseded at s3693 as the immediate explanation: the qualified port exposed a phase-visible DMA-to-RDRAM writer, so the boundary moved upstream to its zero DMEM payload. |
| `H-InputDescriptorWrong` | Refuted at s3692 for 3,178 hangar input rows: the port input ranges were the expected `0x1797B0..0x179930` span. |
| `H-PreDmaHostClear` | Refuted as an immediate pre-DMA action at s3692: no hangar scalar writer fired; the latest port writer was the earlier title zero-fill. |
| `H-NonScalarWriterPath` | Selected at s3693: 512 hangar DMA-to-RDRAM rows were visible in phase, with zero payload and zero post-write span; no hangar scalar writer fired. |
| `H-AIStateParity` | Selected at s3712 for the port: both arms matched host `set-frequency` and first PCM-consumer state at `22047 Hz`; only real audio reached image-stage rows. |
| `H-WriterOutsidePhaseGate` | Refuted at s3693 for the measured port rows: the DMA writer was visible in the hangar gate. |
| `H-ZeroDMEMProducer` | Next boundary after s3693; the DMA payload was already zero, but its producer is not yet joined. |
| `H-DMEMJoinUnevaluable` | Selected at s3694 for the new instrument only: the qualified retry reached both target VIs, but the target source-range branch produced no rows and its positive control did not fire. |
| `H-AudioPumpStableGate` | Refuted at s3696: the fixed paired real-audio arm reached both target phases and emitted all target controls. |
| `H-DMEMPredecessorClass` | Closed at s3697: 512/512 source rows carried zero vector predecessors; the latest predecessor overlapped only 147/512 rows and was on a newer route ordinal for 274/512. |
| `H-DMEMWriterWrongWindow` | Selected at s3697 for the latest-predecessor explanation: 365/512 joined stores did not overlap the output window, and the 147 overlapping stores covered only a two-byte edge. |
| `H-DMEMProducerAbsent` | Selected at s3698: 255/512 hangar rows had no observed DMEM writer for `0xCC0..0xCD0`; covered bytes were zero vector stores. |
| `H-ZeroDMEMProducer` | Refuted as a complete explanation at s3698: a repeated 16-byte output-DMEM gap had no observed covering writer. |
| `H-UninstrumentedDMEMWriter` | Selected at s3699: the missing gap coverage was an RDRAM-to-DMEM DMA writer on all 255 `0xCB0` hangar rows. |
| `H-RetailSourceDifferent` | Selected at s3700: 512/512 output rows joined the expected `0x1798B0..0x179A48` source DMA, whose bytes were zero; retail had distinct hangar writer families while the port retained the title zero-fill. |
| `H-PortSourceProducer` | Selected at s3702 for the producer census: both port arms had the retail-shaped source writer families before the target route was published. |
| `H-PrePhaseScalarProducer` | Selected at s3702: 652 source-range stores preceded/straddled the qualified run, including retail-shaped nonzero writers; the later `0x800078EC` zero-fill preceded zero output payloads. |
| `H-ClearIsFinal` | Selected at s3703: the final observed writer was the zero-valued `0x800078EC` fill before all 512 qualified zero output DMAs. |
| `H-ClearLegitimateButEarly` | Selected at s3704: both arms joined caller `0x8008F2CC` to the expected `0x801797B0`/`0x298` zero-fill before later source/output ordinals. |
| `H-ClearToDmaOrdering` | Confirmed at s3705: real-arm clear ordinal 525 preceded source/output ordinals 669–670; allocation-object identity remains unevaluable. |
| `H-ClearTooEarly` | Selected at s3706: setup and clear both used `0x801797B0`/`0x298`, while the final `0x800078EC` writer was zero before the later zero DMAs. |
| `H-ProducerInputZero` | Selected at s3707: paired setup rows had identical nonzero pre-clear object words while the static-clear witness reported zero fill. |
| `H-ClearBranchRoute` | Selected at s3708: retail and both port arms showed the same target-phase loop/branch outcomes and allocator inputs before the clear. |
| `H-CallerSelectorRoute` | Selected at s3709: retail and both port arms matched `a1=0x561F`, `a2=0`, `s0=0x12`, `s2=1`, and the caller-to-entry handoff. |
| `H-SelectorInputWriterParity` | Selected at s3710: both port arms saw `0x80091CC8` write `0x561F`; independent retail evidence saw the same PC and value. |
| `H-AIFrequencyReturnParity` | Selected at s3711: port and independent retail both observed `a0=0x5622` at `0x80029D20` and actual return `0x561F`; the next boundary is post-return side effect. |
| `H-AIFrequencyReturnDivergence` | Refuted at s3711: the valid hangar port row matched the independent retail input/result pair. |
| `H-AIFrequencyProducerState` | Refuted at s3711 for the measured call/return row: no differing producer state survived into the AI result. |
| `H-SelectorInputWriterDivergence` | Refuted at s3710 at the measured setup boundary: source PC and value matched independent retail evidence. |
| `H-SelectorInputNotWriter` | Refuted at s3710: the source store, load, and caller formed an ordered `0x561F` chain in both port arms. |
| `H-CallerStateDivergence` | Refuted at s3709: real and silent arms had identical caller/allocator selector tuples. |
| `H-CallerOrdering` | Not supported at s3709: route ordinals differed only by arm-local publication counts while the handoff tuple matched retail. |
| `H-ClearCallerState` | Refuted at s3708 for the measured caller branch inputs: real and silent arms matched, and retail matched the same loop shape. |
| `H-ClearCallOrdering` | Refuted at s3708 for the measured boundary: no producer sequence followed the clear before qualified zero source DMAs. |
| `H-ProducerStateClobbered` | Refuted at s3707 for the measured boundary: the shared object was nonzero immediately before the clear. |
| `H-ProducerUsesOtherState` | Unsupported at s3707: paired setup/object rows exposed no alternate state object. |
| `H-DifferentProducerObject` | Refuted at s3706 for the measured target call: the setup object matched the clear destination. |
| `H-ProducerAfterClear` | Refuted at s3706 for the captured source range: no later nonzero writer was observed. |
| `H-ClearWrongObject` | Refuted at s3704 for the measured target range: destination and length matched the expected image-source object. |
| `H-ProducerAfterClear` | Refuted at s3703 for the measured 512-row boundary: no later nonzero source-range writer was observed. |
| `H-DescriptorOrdering` | Refuted at s3703: the final-writer sequence and output-DMA rows had no route/task mismatch. |
| `H-ProducerOmission` | Refuted at s3702 by the phase-independent port census. |
| `H-SourceOverwrittenAfterInput` | Refuted at s3691 for 512/512 hangar rows: input and source payload fields were equal. |
| `H-StaleTaskPointerOnly` | Refuted at s3691 for 512/512 hangar rows: input and source task-data pointers were equal. |
| `H-InputDmaKeyStillUnavailable` | Selected only at the output-DMA boundary by s3688; superseded by the input-DMA key. |
| `H-SourceBeforePublish` | Selected for 778/1,024 source rows at s3680; source reads can precede route publication. |
| `H-SourceSameGeneration` | Selected for the generation-joinable stage class at s3682 and title source rows at s3683. |
| `H-LaterRouteReuse` | Selected at s3686 for 244/244 measured absent-generation hangar rows. |
| `H-AbsentDistinctTask` | Refuted at pointer level by s3684; absent rows used `0x80171E70`, also present in the stage stream. |
| `H-SelectorInterleave` | Selected at s3666; selector publication matches each task object, including alternating hangar objects. |
| `H-PrimaryInitialization` | Selected single-source at s3669; `0x800078EC` is fixed zero-fill initialization, not object payload ownership. |
| `H-PayloadBeforeSelector` | Selected at s3667; watched-span writes preceded title and hangar VI phases. |

## Recent evidence ledger

- **3690 — input-DMA ownership boundary:** 244/244 absent-generation hangar
  source rows joined an earlier/equal input task identity; none joined a
  later task and none was missing or contradictory. See
  [M5-S3690-INPUT-DMA-OWNERSHIP.md](M5-S3690-INPUT-DMA-OWNERSHIP.md).
- **3691 — stale input payload boundary:** 512/512 hangar source rows had
  equal zero input/source/DMEM payload fields and equal task-data pointers.
  See [M5-S3691-STALE-INPUT-PAYLOAD.md](M5-S3691-STALE-INPUT-PAYLOAD.md).
- **3692 — hangar input-writer boundary:** retail had multiple hangar writer
  PCs; the port had 384 title zero-fill scalar rows and 3,178/3,178 hangar
  input rows carried that stale writer snapshot. See
  [M5-S3692-INPUT-WRITER-BOUNDARY.md](M5-S3692-INPUT-WRITER-BOUNDARY.md).
- **3693 — DMA writer boundary:** the qualified real-audio port reached title
  and hangar, with 3,178 hangar input-DMA rows and 512 source-range
  DMA-to-RDRAM rows. The hangar DMA payload and post-write span were both zero;
  no hangar scalar writer fired. See
  [M5-S3693-DMA-WRITER-BOUNDARY.md](M5-S3693-DMA-WRITER-BOUNDARY.md).
- **3694 — DMEM predecessor join unevaluable:** retail controls passed and the
  port build added scalar/vector predecessor fields, but the corrected
  real-audio retry emitted no target source-range rows before the audio-pump
  stall. The transition logger's phase-gate bypass was fixed. See
  [M5-S3694-DMEM-PRODUCER-JOIN.md](M5-S3694-DMEM-PRODUCER-JOIN.md).
- **3695 — audio-pump route boundary:** retail reached hangar with active
  writer controls, while the existing qualified port arm stayed at 320 VI and
  emitted neither its RSP nor target source controls. The DMEM producer join
  remains unevaluable. See
  [M5-S3695-AUDIO-PUMP-BOUNDARY.md](M5-S3695-AUDIO-PUMP-BOUNDARY.md).
- **3696 — qualified audio-pump route:** the fixed paired run reached all
  target phases in both arms; real audio emitted 2,048 DMEM rows and 512
  source-range rows, all sampled payloads zero, with 512/512 predecessor
  sequences and 139/512 overlaps. The route stall is intermittent and the
  predecessor table is now evaluable. See
  [M5-S3696-AUDIO-PUMP-QUALIFICATION.md](M5-S3696-AUDIO-PUMP-QUALIFICATION.md).
- **3697 — DMEM predecessor classification:** retail ground truth passed its
  whole-RDRAM positive control and named four writer families. The qualified
  port emitted 512 hangar source rows; all payloads were zero, while the latest
  zero vector predecessor overlapped only 147/512 rows. See
  [M5-S3697-DMEM-PREDECESSOR-CLASS.md](M5-S3697-DMEM-PREDECESSOR-CLASS.md).
- **3698 — coverage-aware DMEM gap:** the qualified port emitted 512 hangar
  rows and 9,683 subrange records; 255 rows had no observed writer for
  `0xCC0..0xCD0`, while covered bytes were zero vector stores. See
  [M5-S3698-DMEM-COVERAGE-GAP.md](M5-S3698-DMEM-COVERAGE-GAP.md).
- **3699 — DMEM DMA coverage:** after adding the RDRAM-to-DMEM DMA witness,
  the qualified port still emitted 512 hangar rows; all 255 rows using the
  `0xCB0` window had zero-valued DMA coverage for `0xCC0..0xCD0`. The next
  boundary is the zero RDRAM source payload and its producer/layout. See
  [M5-S3699-DMEM-DMA-COVERAGE.md](M5-S3699-DMEM-DMA-COVERAGE.md).
- **3700 — DMA source producer boundary:** the qualified port joined all 512
  hangar output rows to the expected `0x1798B0..0x179A48` source DMA; source
  and output payloads were zero, while the port's latest writer was the title
  zero-fill and retail exposed distinct hangar writers. See
  [M5-S3700-DMA-SOURCE-PRODUCER.md](M5-S3700-DMA-SOURCE-PRODUCER.md).
- **3701 — source producer boundary:** retail independently reached hangar and
  showed 1,125 source-range writes from the known writer families. The
  qualified port's first 512 rows joined the correct DMA, but source and
  post-DMA payloads were zero and no current scalar writer was present. See
  [M5-S3701-SOURCE-PRODUCER-BOUNDARY.md](M5-S3701-SOURCE-PRODUCER-BOUNDARY.md).
- **3703 — final source-writer ordering:** both paired port arms recorded 652
  source stores; the final 384-store group was the zero-valued `0x800078EC`
  fill, and the real arm's 512 output DMAs remained zero. See
  [M5-S3703-SOURCE-CLEAR-ORDER.md](M5-S3703-SOURCE-CLEAR-ORDER.md).
- **3704 — clear object and ordering:** both paired port arms joined the
  `0x8008F2CC` caller to the expected `0x801797B0`/`0x298` zero-fill; the
  real arm's later source-DMA payload remained zero. See
  [M5-S3704-CLEAR-LEGITIMACY.md](M5-S3704-CLEAR-LEGITIMACY.md).
- **3705 — clear-to-DMA ordering:** both arms reached hangar and the real arm
  joined clear ordinal 525 to later zero source/output rows at ordinals
  669–670. The generated allocation probe was absent, so object identity was
  not inferred. See [M5-S3705-CLEAR-HANDOFF.md](M5-S3705-CLEAR-HANDOFF.md).
- **3706 — producer-object join:** the regenerated setup witness matched the
  clear object and the final zero writer preceded the zero source DMA. See
  [M5-S3706-WRITER-SETUP-REQUALIFICATION.md](M5-S3706-WRITER-SETUP-REQUALIFICATION.md).
- **3708 — clear-caller branch qualification:** the retail oracle and paired
  port arms showed the same target-phase allocator branch shape and inputs;
  this selects the stable route explanation. See
  [M5-S3708-CLEAR-BRANCH.md](M5-S3708-CLEAR-BRANCH.md).
- **3702 — pre-phase producer and overwrite:** the paired port arms each
  recorded 652 source-range stores, including retail-shaped producer PCs, but
  the later `0x800078EC` zero-fill remained before zero output DMA payloads.
  See [M5-S3702-SOURCE-PRODUCER-OVERWRITE.md](M5-S3702-SOURCE-PRODUCER-OVERWRITE.md).
- **3688 — keyed per-range DMA boundary:** source event, task generation, and
  route publication fields fired in output-DMA rows, but 257/258 absent-source
  rows lacked a same-event range and one was contradictory. Input-DMA identity
  remains the next boundary. See [M5-S3688-KEYED-DMA-EMISSION.md](M5-S3688-KEYED-DMA-EMISSION.md).
- **3687 — absent-source DMA ownership join:** the prior output-DMA record had
  no stable join key. This motivated the s3688 field-carrying change. See
  [M5-S3687-ABSENT-DMA-OWNER-JOIN.md](M5-S3687-ABSENT-DMA-OWNER-JOIN.md).
- **3686 — absent-source route join:** 244/244 absent-generation rows advanced
  to a later route ordinal/row; 0 stayed on the source route and 0 were
  contradictory or missing. See [M5-S3686-ABSENT-ROUTE-JOIN.md](M5-S3686-ABSENT-ROUTE-JOIN.md).
- **3685 — absent-source publication join:** all 236 measured absent rows had
  a later same-pointer stage generation. See [M5-S3685-ABSENT-PUBLICATION-JOIN.md](M5-S3685-ABSENT-PUBLICATION-JOIN.md).
- **3684 — absent-source task join:** all 220 measured absent rows used
  `0x80171E70`, also present in the stage stream. See [M5-S3684-ABSENT-SOURCE-DMA-JOIN.md](M5-S3684-ABSENT-SOURCE-DMA-JOIN.md).
- **3683 — source-centric generation census:** title was 512/512 same
  generation; hangar was 282/512 same-generation, 230 absent, 0 reversed.
  See [M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md](M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md).
- **3680–3682 — publication and generation joins:** stage rows matched the
  latest published route; source rows split exact-route and route-lagged
  classes; generation-first matching found source-before-stage ordering for
  the joinable class. See [M5-S3680-PUBLICATION-ROUTE-JOIN.md](M5-S3680-PUBLICATION-ROUTE-JOIN.md),
  [M5-S3681-SOURCE-PUBLICATION-ORDER.md](M5-S3681-SOURCE-PUBLICATION-ORDER.md), and
  [M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md](M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md).
- **3677–3679 — key boundary corrections:** pointer-only and exact
  route/task joins failed; generation and thread keys exposed publication
  timing, and s3680 corrected the route sample to actual publication.
- **3667–3676 — source and stage boundary:** source writes preceded target
  phases; the primary writer is fixed initialization; remaining writer sites
  are padding/table initialization; input reads were nonzero in title and
  zero in hangar; source/stage route ordinals did not align.
- **3659–3666 — task and selector ownership:** scalar stores were zero;
  target descriptors use a shared writer family but phase-specific task
  objects; selector publication interleaves those objects.

Earlier M3 class closeouts (sessions 3586–3658) are archived in
PROJECT-OVERVIEW §56. Earlier M5 boundary notes remain in `docs/` and the
append-only ledger; only live transitions are repeated here.

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. MusyX task data cannot be sent to
stock `aspMain`; the silent arm returns `RspExitReason::Broke`. Do not infer
audio behavior from a route that fails to reach the target phase.

Every instrument needs an independent ground-truth request, a same-run
positive control, a phase-scoped budget, and two evidence lines before its
result becomes current truth. Phase-gate animated comparisons on VI
transitions. Batch A/B arms in one build and run. A counter is not a control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

## Superseded conclusions

The s3579–s3584 inference of a retail-versus-port stored-value divergence at
`0x800078EC` is unsupported: retail executes `sb $a1, 0($v0)`, while the
oracle read an aligned word containing neighboring bytes. Scalar-store samples
measured zero bytes with zero mismatches.

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield/viewer-stall chain describes only the old diagnostic
arm. The old interpretation of the cinematic pool as an audio-slot pool was
superseded by the MusyX voice-table measurement.

The claim that `0x8002BEEC` is the retail JAL dispatch to `0x800078EC` is
route-dependent and unreconciled. Do not treat it as a writer without a new
independent discriminator.

Sessions 3512/3516 selected non-observable predecessor watches; their positive
controls remain useful, but absent predecessor rows do not establish parity,
divergence, or mutation. The s3585 standalone-slot interpretation of
`voice_record+0x64` was superseded by s3586's packed-handle audit.

## Evidence index

- [M5-S3688-KEYED-DMA-EMISSION.md](M5-S3688-KEYED-DMA-EMISSION.md)
- [M5-S3687-ABSENT-DMA-OWNER-JOIN.md](M5-S3687-ABSENT-DMA-OWNER-JOIN.md)
- [M5-S3686-ABSENT-ROUTE-JOIN.md](M5-S3686-ABSENT-ROUTE-JOIN.md)
- [M5-S3685-ABSENT-PUBLICATION-JOIN.md](M5-S3685-ABSENT-PUBLICATION-JOIN.md)
- [M5-S3684-ABSENT-SOURCE-DMA-JOIN.md](M5-S3684-ABSENT-SOURCE-DMA-JOIN.md)
- [M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md](M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md)
- [M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md](M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md)
- [M5-S3681-SOURCE-PUBLICATION-ORDER.md](M5-S3681-SOURCE-PUBLICATION-ORDER.md)
- [M5-S3680-PUBLICATION-ROUTE-JOIN.md](M5-S3680-PUBLICATION-ROUTE-JOIN.md)
- [M5-S3669-PRIMARY-STORE-CONTEXT.md](M5-S3669-PRIMARY-STORE-CONTEXT.md)
- [M5-S3667-PAYLOAD-ORDER.md](M5-S3667-PAYLOAD-ORDER.md)
- [M5-S3692-INPUT-WRITER-BOUNDARY.md](M5-S3692-INPUT-WRITER-BOUNDARY.md)
- [M5-S3693-DMA-WRITER-BOUNDARY.md](M5-S3693-DMA-WRITER-BOUNDARY.md)
- [M5-S3695-AUDIO-PUMP-BOUNDARY.md](M5-S3695-AUDIO-PUMP-BOUNDARY.md)
- [M5-S3697-DMEM-PREDECESSOR-CLASS.md](M5-S3697-DMEM-PREDECESSOR-CLASS.md)
- [M5-S3699-DMEM-DMA-COVERAGE.md](M5-S3699-DMEM-DMA-COVERAGE.md)
- [M5-S3702-SOURCE-PRODUCER-OVERWRITE.md](M5-S3702-SOURCE-PRODUCER-OVERWRITE.md)
- [M5-S3708-CLEAR-BRANCH.md](M5-S3708-CLEAR-BRANCH.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3693 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
