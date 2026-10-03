# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory
and the incremental de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3771 (2026-10-02).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-audio/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. The real Factor 5 image task is
the qualified audio arm; `ROGUESQ_AUDIO_UCODE=0` selects the silent `Broke`
control. Audio is not production-complete.

The latest independent retail/port boundary is source payload, not rendering:
retail title snapshots contain nonzero bytes in both source subranges (105/256
and 168/408), while hangar snapshots are zero (the exact FNV values are in
the evidence note). The qualified real-port source-DMA joins remain zero
(`FNV=0x762B22A5`) in the same measured span. The port's expected source
descriptor is `0x1798B0 -> DMEM 0xCB0`; its final observed writer is the
legitimate zero-valued `0x800078EC` fill before the image DMA. Exact retail
byte positions are now exported, but layout parity is still not testable at a
zero-valued port payload. See
[M5-S3736-EXACT-RETAIL-BYTE-JOIN.md](M5-S3736-EXACT-RETAIL-BYTE-JOIN.md).

The nine bounded exact-offset load candidates are closed. The complete
generated scalar-store census for the task-data object is also closed: both
qualified port arms executed target-phase zero-valued stores, with no nonzero
producer at `0x80171E70`. A new native page-fault census now proves generated
game code also writes the task-data page in both arms, but it does not capture
the stored value. Session 3756 added ARM64 source-register decoding, but its
paired capture was unevaluable: the real arm hit the MusyX crash path and the
silent arm crashed before target gating, with no target-phase rows. See
[M5-S3755-TASK-DATA-NATIVE-WRITE-CENSUS.md](M5-S3755-TASK-DATA-NATIVE-WRITE-CENSUS.md)
and [M5-S3756-TASK-DATA-NATIVE-VALUE.md](M5-S3756-TASK-DATA-NATIVE-VALUE.md).
Session 3757 moved decoding to target-only faults and added post-store
sampling; both controls and title passed, real reached hangar, but neither
arm produced a target-range fault before the known real MusyX/silent VI
retrace crashes. See
[M5-S3757-TASK-DATA-NATIVE-VALUE-RETRY.md](M5-S3757-TASK-DATA-NATIVE-VALUE-RETRY.md).
Session 3758 added target-window arm/re-arm coverage. The silent control passed
the page positive control and held the page armed across title and hangar target
ticks, but produced no target fault; the real arm crashed before its target
window in `spTaskSchedulerThread+9556`. This is incomplete paired coverage,
not a zero-value result. See
[M5-S3758-TASK-DATA-NATIVE-COVERAGE.md](M5-S3758-TASK-DATA-NATIVE-COVERAGE.md).

Session 3759 ran the complete Step 1 contract row with the retail oracle and
both port arms. The oracle whole-RDRAM control and title/hangar phases passed;
the silent arm reached title and produced phase-qualified task/route/PCM
control rows, but the real image arm crashed before any target phase at
`si_addr=0x400128d47`. This selects route instability for this capture rather
than a downstream contract gap; no audio or task-data mitigation is selected.
See [M5-S3759-STEP1-CONTRACT-RETRY.md](M5-S3759-STEP1-CONTRACT-RETRY.md).

Session 3760 qualified the image arm: in a same-build oracle/image/silent
capture, retail controls passed, image reached title and hangar with task,
DMA, image-stage, audio-return, and PCM rows, while silent crashed pre-target
at the same scheduler boundary. An image-only follow-up reached both target
VIs with the same build and full image rows, so pair interference is not the
image-arm explanation. The silent control remains unstable and the same-run
image-versus-silent contract comparison is still open. See
[M5-S3760-STEP1-IMAGE-QUALIFICATION.md](M5-S3760-STEP1-IMAGE-QUALIFICATION.md).

Session 3762 repeated the same-build concurrent contract capture. The oracle
positive control and both image/silent arms reached title and hangar. Silent
did not reproduce the s3761 pre-target scheduler crash: it emitted dispatch,
ABI/DMA-return, audio-route, PCM source/consumer, and target-phase rows, while
the image arm emitted the corresponding image-stage rows. This refutes a
deterministic silent pre-target failure and reopens the same-run Step 1
contract comparison. See the run directory under
`scratch/agent/s3762_m5_step1_silent_repeat/`.

Session 3763 compared that capture. The oracle and both port arms passed the
positive controls and reached both target VIs. Dispatch, audio return/route,
SP delivery, and PCM source/consumer counts were shared; neither arm showed
slot allocation/status or voice-audit activity. The only material arm-specific
row was the expected image-stage/DMA work in the real image arm, so
`H-M5-ImageStageOnly` is selected for Step 1. The image and PCM payloads remain
zero-valued, leaving the source-versus-output contract boundary open; this is
not authorization for a writeback or fill mitigation. See
[M5-S3763-STEP1-CONTRACT-COMPARISON.md](M5-S3763-STEP1-CONTRACT-COMPARISON.md).

Session 3761 repeated the same-build concurrent contract capture. The oracle
positive control passed and reached both target VIs; image again reached title
and hangar with 6,560 task/DMA rows, 26,248 image-stage rows, and audio/PCM
rows. Silent emitted no target rows and crashed before title at
`spTaskSchedulerThread+9556` (`si_addr=0x400128d47`), while cleanup classified
the pair as `silent_hangar=0`, `image_hangar=1`. This selects the silent
pre-target crash for this capture and leaves production repeatability and the
downstream Step 1 contract open. See
[M5-S3761-STEP1-SILENT-QUALIFICATION.md](M5-S3761-STEP1-SILENT-QUALIFICATION.md).

Session 3764 re-read the same qualified capture at the source/output boundary.
The oracle positive control and both target phases were present. Across aligned
phase-5 route ordinals, the image input DMA was already zero with no previous
writer; image-stage output and PCM source/consumer rows remained zero. This
selects `H-M5-InputProducerGap` for the measured chain and refutes an
output-consumer-first loss. It is single-capture evidence and does not name the
missing producer or authorize a writeback/fill mitigation. See
[M5-S3764-IMAGE-SOURCE-OUTPUT-BOUNDARY.md](M5-S3764-IMAGE-SOURCE-OUTPUT-BOUNDARY.md).

Session 3765 re-read the same capture at the pre-input boundary. Across 33
aligned phase-5 image input DMAs, `0x1798B0 -> DMEM 0xCB0` was all-zero with no
previous writer attribution. The separate source-span writer census records
the known legitimate zero-fill PC `0x800078EC` across the range, but no
nonzero producer. This selects `H-M5-ProducerAbsent` for the measured producer
classes and moves the next question to the clear's caller/ordering; it does
not authorize suppressing the clear. See
[M5-S3765-PRE-INPUT-PRODUCER-BOUNDARY.md](M5-S3765-PRE-INPUT-PRODUCER-BOUNDARY.md).

Session 3766 rebuilt the existing static `rs_memset` caller probes and ran
same-build image/silent arms. Both arms passed the probe controls and reached
title VI 1024 and hangar VI 512. The target clear was called from
`0x8008F2CC`, immediately after allocation of the `0x298`-byte buffer and
before cache writeback; runtime rows placed it before the `0x800078EC`
source-span rows and the input DMA. This selects `H-M5-ClearIsExpected` for
caller/order, without explaining the missing post-clear producer or changing
the clear. See [M5-S3766-CLEAR-CALLER-ORDER.md](M5-S3766-CLEAR-CALLER-ORDER.md).

Session 3767 ran the batched post-clear writer/order capture with the retail
oracle. The oracle whole-RDRAM control fired and reached title/hangar,
recording 705 and 1,125 writes in the two target source ranges. The port
image arm reached both target VIs; its phase-5 clear was followed by 244
target-span stores, all zero-valued from `0x800078EC`, with no nonzero
post-clear writer. Its input-DMA join was absent in this capture. The silent
arm failed to reach a target VI and is unevaluable, not a null result. See
[M5-S3767-POSTCLEAR-PRODUCER-ORDER.md](M5-S3767-POSTCLEAR-PRODUCER-ORDER.md).

Session 3768 mapped the retail source-span writer families to generated port
bodies: `0x80007670` is `rs_strncpy`, `0x8001E2C0` is
`initTextureLUTAndAllocBuffers`, and `0x8001F...` is `loadTextureToMemory`.
Those bodies exist in the port, but the qualified s3767 target-buffer capture
showed no family write to either title or hangar target buffer; only the
legitimate zero-valued `0x800078EC` padding followed the clear. This selects
`H-M5-RetailWriterPortEdgeAbsent` for the measured target phase while leaving
buffer/route identity mismatch open. See
[M5-S3768-RETAIL-PORT-EDGE-AUDIT.md](M5-S3768-RETAIL-PORT-EDGE-AUDIT.md).

Session 3769 ran the phase-gated family-entry census in concurrent image and
silent arms, beside the retail oracle. The oracle whole-RDRAM control passed
and reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`; both port
arms reached both phases and passed all family controls. In each port arm,
`rs_strncpy` and `loadTextureToMemory` each executed 64 rows in title and 64
in hangar, but none carried an argument in the title/hangar target ranges.
`initTextureLUTAndAllocBuffers` had no target-phase entry. Retail independently
executed the corresponding PCs in target phases. This selects other-object
execution for S/L and absent target edge for I, while leaving the legitimacy
of the other-object route unresolved. See
[M5-S3769-RETAIL-PORT-FAMILY-EDGE.md](M5-S3769-RETAIL-PORT-FAMILY-EDGE.md).

Session 3770 ran the regeneration-safe internal-store census in concurrent
image and silent arms beside the retail oracle. The oracle whole-RDRAM control
fired (77,858 writes) and reached both target VIs; both port arms reached
both target VIs, passed all three family-store controls, and matched each
other. S/L each produced 256 bounded store rows in title and hangar, all to
alternate object addresses with zero target-range rows. I produced 256 title
rows and no hangar-phase rows, also with zero target-range rows. This selects
alternate-object provenance for S/L and absent target edge for I; legitimacy
of the alternate route and its identity relative to the 0x8008F2CC clear
remain open. No mitigation was added. See
[M5-S3770-FAMILY-STORE-PROVENANCE.md](M5-S3770-FAMILY-STORE-PROVENANCE.md).

Session 3771 added the next regeneration-safe join fields: the process-wide
clear-associated allocation object from `0x8008F2CC`, exact/span membership,
and the existing route key on S/L/I family-store rows. The Debug build passed,
but the final concurrent oracle/image/silent capture was unevaluable: both
port arms crashed before target at `spTaskSchedulerThread+9556`, while retail
only reached its whole-RDRAM positive-control threshold. The first attempt
also exposed and fixed a missing generated-host `rdram` argument in the new
witness ABI. No alternate-object or route-identity hypothesis is selected or
refuted. See [M5-S3771-ALTERNATE-OBJECT-JOIN.md](M5-S3771-ALTERNATE-OBJECT-JOIN.md).

## Next steps

Work only the first applicable item. This is one monotonic backlog.

1. **M5 alternate-object legitimacy versus route identity.** Join the S/L
   alternate store destinations and I's title-only setup object to the
   `0x8008F2CC` clear-associated object, allocator result, and active route
   ordinal in one phase-gated capture. Require the retail whole-RDRAM control
   and both target VIs in image and silent arms. Distinguish a legitimate
   alternate asset object from a route/object identity mismatch. Do not
   suppress or replace the clear, inject values, or change an audio gate.
2. **M3 parked audit — `rs_zcfree` incoming `$a0` at `0x80005268`.** Only
   start if M5 is unavailable or closed. Audit the complete idiom class,
   identify the writer and legitimacy, and land a guard only for a concrete
   invalid writer. Closed `rs_free` audits are archived in PROJECT-OVERVIEW §56.
3. **Generated-symbol renaming sweep.** Only after M5 is closed and M3 has no
   new discriminator. Keep the campaign slug
   `generated-symbol-renaming-sweep` and work one bounded region per session.

## Live hypothesis table

| Hypothesis | Status |
|---|---|
| `H-RetailOnlyProducer` | Selected at s3737 for the measured hangar source boundary; retail exact positions/FNV and writer-family join are now exported. |
| `H-RetailWriterEarlier` | Selected at s3737: retail title source bytes have earlier writer PCs absent from the qualified port source path. |
| `H-PortEarlierWriterAbsent` | Selected at s3738 for the measured scalar-store class: title has only legitimate zero-fill `0x800078EC`; hangar has no target-span scalar store. |
| `H-PortWriterUnlogged` | Refuted at s3738 for the generated scalar-store witness; its positive control fired and no other target-span writer appeared. |
| `H-PortWriterLegitimateClear` | Refuted at s3738 for the measured port span: no nonzero port store preceded the zero DMA payload. |
| `H-PortFamilyNeverEntered` | Refuted at s3739 for the measured family-entry hook: both families execute in the port. |
| `H-PortFamilyEnteredWrongArgs` | Refined at s3739: families touch the target span, but value/setup provenance remains open. |
| `H-FamilyCallEdgeDropsValue` | Refuted at s3740 for the measured call/entry edges: caller and entry arguments matched in both arms. |
| `H-FamilyValueSetupAbsent` | Refuted for the measured candidate setup families; the missing qualified-route edge is elsewhere or parallel. |
| `H-RouteHandoffValueAbsent` | Selected at s3741 for the measured route edge: route-preparation source fields and the `0x8000C628` handoff value fields were zero in title and hangar, followed by zero source DMA. |
| `H-RouteHandoffDropsValue` | Refuted at s3741 for the measured edge: no nonzero predecessor value was observed before the zero handoff. |
| `H-RouteHandoffAfterClear` | Refuted at s3741 for the measured edge: the handoff was already zero before the zero source DMA; no later-clear ordering was shown. |
| `H-EarlierWriterAbsent` | Selected at s3742 for the measured scalar-store class: 512 target-phase rows per arm were all zero-valued neighboring writes, with no nonzero exact-field writer. |
| `H-EarlierWriterClears` | Refuted at s3742 for the measured scalar-store class: no earlier nonzero writer was observed before the zero route state. |
| `H-RouteStateNotSource` | Open after s3742: exact route fields had no scalar writer, so an uninstrumented/non-scalar producer versus control metadata remains unresolved. |
| `H-RouteStateNotSource` | Selected at s3751 for all nine bounded exact-offset loads: neither qualified port arm read the exact object `0x80128C70` in either target phase. |
| `H-PortSourceProducerAbsent` | Selected at s3752: the qualified real arm read zero task data at `0x80171E70` before the expected source DMA; the next boundary is its producer. |
| `H-PortSourceProducerPresent` | Refuted at s3752 for the measured source-DMA class: no nonzero hangar source payload was present at the joined reader. |
| `H-PortSourceJoinMismatch` | Refuted at s3752 at the source-DMA edge: the reader used `0x1798B0 -> DMEM 0xCB0` and joined the active route/task. |
| `H-TaskDataProducerAbsent` | Selected at s3753 for the complete generated scalar-store class: both qualified port arms had target-phase rows at `0x80171E70..0x171F70`, all zero-valued; host/RSP/non-scalar ownership remains open. |
| `H-TaskDataScalarProducerPresent` | Refuted at s3753: the positive-control census covered all generated scalar stores and found no nonzero target-phase value in either arm. |
| `H-TaskDataHostProducer` | Refuted at s3754 for PI ROM, PI SRAM, zmemcpy, and the central host-write hook: controls fired but no target-span row appeared. |
| `H-TaskDataRspProducer` | Refuted at s3754 for central RSP DMEM-to-RDRAM transfers: the RSP API control fired in both arms but no target-span row appeared. |
| `H-TaskDataNonScalarAbsent` | Selected at s3754 for the censused central host/RSP classes; arbitrary direct/native and other non-central writers remain open. |
| `H-TaskDataNativeWriteObserved` | Selected at s3755: phase-armed native page faults touched the target span in both real/silent arms; stored value remains unevaluated. |
| `H-TaskDataNativeValueDecoded` | Unevaluable at s3756: ARM64 decoding was added, but the paired run had no target-phase attribution rows; real/silent crashed in separate paths. |
| `H-TaskDataNativeValueDecoded` | Unevaluable at s3757: target-only decoding and post-store sampling were installed, but both arms had zero target faults before their crash paths. |
| `H-TaskDataNativeValueDecoded` | Parked at s3758: silent had positive-control and target-window coverage with no target fault; real crashed before target. Paired value attribution remains unevaluable. |
| `H-M5-RouteInstability` | Selected at s3759 for the Step 1 capture: oracle and silent controls reached target, but the real image arm crashed before target; downstream contract nulls remain unevaluable. |
| `H-M5-ImageReachesTarget` | Selected at s3760: the image arm reached title and hangar in the paired run and independently in an image-only run with full task/DMA/PCM rows. |
| `H-M5-ImageOnlyInterference` | Refuted at s3760: image-only reached both target VIs on the same build with the same controls. |
| `H-M5-SilentPreTargetCrash` | Selected at s3760 for this paired capture: silent crashed at `spTaskSchedulerThread+9556` before target while image and retail controls passed. |
| `H-M5-SilentPreTargetCrash` | Refuted as deterministic at s3762: oracle, image, and silent all reached title/hangar; silent emitted target-phase route/PCM rows and no crash marker. |
| `H-M5-Step1ContractGap` | Open at s3762: silent and image shared task/route/PCM progress, while image alone emitted image-stage rows; the first meaningful downstream contract difference is not yet identified. |
| `H-M5-ImageStageOnly` | Selected at s3763: same-build image/silent arms shared task return, SP delivery, PCM counts, slot/voice nulls, and both target phases; image-only work was image-stage/DMA activity. |
| `H-M5-InputProducerGap` | Selected at s3764 for the measured image chain: aligned input DMA was already zero with no previous writer, and stage/PCM rows preserved zero. Single-capture boundary; producer identity remains open. |
| `H-M5-ProducerAbsent` | Selected at s3765 for the measured pre-input producer classes: 33 aligned image input-DMA rows were zero with empty previous-writer attribution; the separate source-span census records only the known zero-fill writer `0x800078EC`. Clear caller/order remains open. |
| `H-M5-ClearIsExpected` | Selected at s3766: `0x8008F2CC` allocates and immediately clears the `0x298`-byte source buffer; the runtime clear precedes the observed source-span rows and input DMA in both port arms. |
| `H-M5-PostClearProducerAbsent` | Selected at s3767 for the measured image-arm target span: 244 phase-5 stores followed the clear, all zero-valued from `0x800078EC`; no nonzero port producer appeared. Retail independently reached both target phases and wrote both source ranges. |
| `H-M5-PostClearProducerClears` | Refuted for the measured image-arm target span at s3767: no nonzero post-clear writer preceded a later zero writer. |
| `H-M5-PostClearJoinMismatch` | Open for the downstream input-DMA join at s3767: the image arm reached both target VIs, but emitted no input-DMA row in this capture; prior s3766 coverage remains the join evidence. |
| `H-M5-RetailWriterPortEdgeAbsent` | Selected at s3768 for the measured title/hangar target buffers: retail writer families have generated port bodies, but no family write joined either target buffer in the qualified port capture. |
| `H-M5-RetailWriterHasPortEdge` | Refuted at s3768 for the measured target-buffer phases; no family write appeared in the target-span rows. |
| `H-M5-RetailWriterJoinMismatch` | Open at s3768: static family bodies exist, but the capture does not distinguish absent execution from a buffer/route identity mismatch. |
| `H-M5-RetailWriterFamilyOtherObject` | Selected at s3769 for S/L: both port arms executed each family in title and hangar, but zero entry arguments fell in either target buffer range. |
| `H-M5-RetailWriterFamilyAbsentTargetEdge` | Selected at s3769 for I: both port arms passed the family control, but no target-phase entry occurred; retail independently reached the PC. |
| `H-M5-RetailWriterFamilySameTarget` | Refuted at s3769: no S/L entry argument matched the title or hangar target ranges, and I had no target-phase entry. |
| `H-M5-ClearIsWrongOrder` | Refuted for the measured port caller/order: no legitimate producer was observed before the `0x8008F2CC` clear, and the static caller performs allocation, clear, then writeback. |
| `H-M5-JoinMismatch` | Refuted for the measured target row: static callsite, destination, fill, length, phase-5 route, and source-DMA range joined in both arms. |
| `H-M5-OutputConsumerGap` | Refuted at s3764 for the measured chain: the first observed zero preceded image-stage output and PCM consumption. |
| `H-M5-Accounting` | Refuted at s3764 for the measured rows: oracle/title/hangar controls and phase/ordinal joins were present. |
| `H-RouteStateSourceKey` | Refuted at s3751: the same-run hook control fired, but there were zero target-phase exact-object rows. |
| `H-ExactFieldUnwritten` | Selected at s3743 for generated scalar stores using literal `+0x22/+0x60`: oracle and qualified real/silent port arms had zero exact-field rows in title/hangar. |
| `H-ExactFieldNonScalar` | Refined at s3744: generated non-literal stores and RSP DMA had no exact rows; arbitrary host-side writes remain open. |
| `H-HostExactWriter` | Selected only for transient/unattributed activity after s3745: the 1 ms poll saw no persistent exact-field change, but has no writer-PC attribution. |
| `H-ExactFieldUnwritten` | Selected at s3746 for the censused central host-write APIs; no target-phase exact rows appeared after every invoked API passed its control. |
| `H-HostTransient` | Refuted at s3746 for PI ROM, PI SRAM, zmemcpy, and RSP DMEM-to-RDRAM host writes; arbitrary direct host pointer writes remain open. |
| `H-HostLiteralDirectWriter` | Refuted at s3747 by a 61-file source census: target literals occur only in diagnostics, not production host writers. Computed-pointer/generic-macro ownership remains open. |
| `H-HostExactWriter` | Refuted at s3748 for the qualified port capture: native macOS ARM64 page-fault control fired in both arms, but no phase-gated exact-field host fault occurred. |
| `H-ExactFieldUnwritten` | Selected at s3748 for the remaining arbitrary native host-write class; route-state/source interpretation remains open. |
| `H-PortFamilyWritesThenClear` | Refuted at s3739 for the qualified hangar source path: all real source-range writer payloads remained zero. |
| `H-PortSourceClearOrdering` | Selected at s3731 across `0x1797B0..0x179A48`; target-phase stores and later payloads were zero under the known fill. |
| `H-UninstrumentedPortProducer` | Refuted at s3731 for the full measured span. |
| `H-SourceLayoutMismatch` | Still unevaluable as a parity claim: the port payload is zero, although both source descriptors are aligned. |
| `H-ImageProducerZero` | Selected at s3728 for 1,804 joined hangar image rows. |
| `H-GuestContractDownstream` | Open: port callback ownership is split, but retail host-side parity and exact payload contract remain unjoined. |
| `H-AudioDrainNotConsumed` | Open after s3715; queue state is not directly joined to image-stage consumption. |
| `H-RetailHostCallbackParity` | Open; the oracle exposes guest execution/writes, not host callback/thread ownership. |
| `H-DMEMProducerAbsent` | Closed at s3699: the apparent gap was an RDRAM-to-DMEM DMA writer. |
| `H-ClearTooEarly` | Selected at s3706 for the measured source object; this is an explanation of the observed zero payload, not permission for a mitigation. |

| `H-M5-FamilyStoresAlternateLegitimateObject` | Selected at s3770 for measured S/L stores: both arms wrote only alternate object destinations in title/hangar; legitimacy relative to the clear-associated route remains open. |
| `H-M5-FamilyStoresExpectedTargetViaHiddenPointer` | Refuted at s3770 for the measured store sites: no internal store destination fell in either target buffer range in either arm. |
| `H-M5-FamilyRouteIdentityMismatch` | Open at s3770: alternate destinations are proven, but their allocator/route identity is not yet joined to the clear object. |
| `H-M5-FamilyAbsentTargetEdge` | Selected at s3770 for I: title setup stores were observed, but no hangar-phase I store bucket appeared in either arm. |

## Evidence ledger — live boundary only

- **3768 — retail writer-family edge audit:** static generated code maps
  `0x80007670` to `rs_strncpy`, `0x8001E2C0` to
  `initTextureLUTAndAllocBuffers`, and `0x8001FACC..0x8001FD2C` to
  `loadTextureToMemory`. The s3767 qualified port target rows contained only
  the legitimate zero-valued `0x800078EC` padding after the clear; the retail
  oracle independently recorded these families and nonzero title bytes. This
  selects target-buffer edge absence, while leaving route/object identity
  mismatch open. No mitigation was added. See
  `docs/M5-S3768-RETAIL-PORT-EDGE-AUDIT.md`.

- **3769 — family-entry destination census:** the oracle positive control and
  both target VIs passed. Image and silent port arms matched: S/L each had
  64 title and 64 hangar entries, all outside the target ranges; I had zero
  target-phase entries. Retail independently executed S/L/I in the target
  phases. This selects alternate-object execution for S/L and absent target
  edge for I; internal store destinations and route identity remain open. No
  mitigation was added. See
  [M5-S3769-RETAIL-PORT-FAMILY-EDGE.md](M5-S3769-RETAIL-PORT-FAMILY-EDGE.md).

- **3770 — family internal-store provenance:** the oracle whole-RDRAM control
  fired and reached title/hangar. Image and silent matched: S/L each emitted
  256 bounded title and 256 bounded hangar store rows, all outside the target
  buffers; I emitted 256 title setup rows and no hangar rows. The value field
  was retained and the family store controls fired. This selects alternate
  object destinations for S/L and an absent I hangar edge, while leaving
  clear/object/route identity open. No mitigation was added. See
  [M5-S3770-FAMILY-STORE-PROVENANCE.md](M5-S3770-FAMILY-STORE-PROVENANCE.md).

- **3762 — silent-route stability repeat:** the retail oracle passed its
  whole-RDRAM control and reached title/hangar; both image and silent arms
  reached title VI 1024 and hangar VI 512 in the same build/run. Silent did
  not reproduce the s3761 `spTaskSchedulerThread+9556` pre-target crash and
  emitted 50 dispatch, 659 ABI/DMA-return, 278 audio-return, 870 route, and
  70/285 PCM source/consumer rows, plus target phases. Image emitted 50
  dispatch, 665 ABI/DMA-return, 2693 image-stage, 283 audio-return, 885 route,
  and the same 70/285 PCM rows, plus target phases. This refutes a deterministic
  silent pre-target failure and reopens the downstream Step 1 contract; it does
  not by itself establish why image-stage rows differ. See
  `scratch/agent/s3762_m5_step1_silent_repeat/driver.log`.

- **3761 — silent-control qualification retry:** the retail oracle passed its
  whole-RDRAM control and reached title/hangar. The image arm reached both
  target VIs with 6,560 task/DMA rows, 26,248 image-stage rows, and audio/PCM
  rows. The silent arm emitted no target rows and crashed before title at
  `spTaskSchedulerThread+9556` (`si_addr=0x400128d47`); the pair gate was
  `silent_hangar=0`, `image_hangar=1`. This selects the silent pre-target crash
  for this capture, without establishing a production-wide repeatability rate.
  See [M5-S3761-STEP1-SILENT-QUALIFICATION.md](M5-S3761-STEP1-SILENT-QUALIFICATION.md).

- **3759 — Step 1 contract retry:** the retail oracle passed its whole-RDRAM
  control and reached title/hangar. The silent port arm reached title and
  emitted phase-qualified task/route/PCM control rows; the real image arm
  crashed before target at `si_addr=0x400128d47` and emitted no target rows.
  This selects pre-target route instability for this capture and does not
  qualify a downstream audio-contract gap. See
  [M5-S3759-STEP1-CONTRACT-RETRY.md](M5-S3759-STEP1-CONTRACT-RETRY.md).

- **3757 — target-only native value retry:** the same-build real/silent pair
  passed the task-page positive control and reached title VI 1024; real also
  reached hangar VI 512. Neither arm produced a target-range fault or
  post-store row. Real later crashed in `musyxBuildVoiceCommandList`; silent
  crashed in the VI retrace path before hangar. This is run-instability/no
  target-fault evidence, not a zero-value result. See
  [M5-S3757-TASK-DATA-NATIVE-VALUE-RETRY.md](M5-S3757-TASK-DATA-NATIVE-VALUE-RETRY.md).

- **3758 — native target-window coverage retry:** the silent arm passed the
  page positive control and sustained title/hangar target ticks with repeated
  re-arms, but had no target-range fault. The real arm crashed before target in
  `spTaskSchedulerThread+9556`. This parks native-value attribution rather than
  selecting a zero producer. See
  [M5-S3758-TASK-DATA-NATIVE-COVERAGE.md](M5-S3758-TASK-DATA-NATIVE-COVERAGE.md).

- **3754 — non-scalar task-data producer census:** the retail oracle passed its
  whole-RDRAM control and recorded 50,387 task-data-span writes plus 717
  source-span writes, with target-phase writers in the `0x80090A..0x800911`
  family. The paired real/silent port arms both passed all four host/RSP API
  controls and reached their measured phases; neither produced a target-span
  host/RSP row. The real arm retained 4,096 zero-valued generated scalar rows
  and the zero source-DMA join; silent remained the no-source control. This
  closes the central host/RSP producer classes and moves the boundary to
  arbitrary direct/native or other non-central ownership. See
  [M5-S3754-TASK-DATA-NONSCALAR-CENSUS.md](M5-S3754-TASK-DATA-NONSCALAR-CENSUS.md).

- **3755 — native task-data write census:** the retail control again fired and
  named the `0x80090A..0x800911` writer family. A phase-armed native page-fault
  watch in paired real/silent ports passed both target phases and recorded
  39/33 target-range faults; the PCs symbolized into generated game functions.
  The source join remained real-only (1,024 rows versus 0), but the fault
  witness did not capture store values. This selects native writer activity,
  not yet a nonzero producer. See
  [M5-S3755-TASK-DATA-NATIVE-WRITE-CENSUS.md](M5-S3755-TASK-DATA-NATIVE-WRITE-CENSUS.md).

- **3736 — exact retail byte join:** the oracle exported exact phase-gated
  byte positions and FNV for both source subranges. Retail title was
  nonzero (105/256 and 168/408); retail hangar was zero (256/256 and 408/408
  zero). The same-iteration real and silent port arms reached both phases;
  real source-DMA payload remained zero. This closes the export gap and keeps
  the boundary at the retail-versus-port writer family, not layout.
- **3734 — prior retail/port byte-layout join:** retail target-phase samples
  were nonzero in both source subranges; 1,819 qualified real-port joins had
  zero source-DMEM/output/destination payloads. Session 3736 added the exact
  retail positions/FNV that were missing here.
- **3737 — retail writer-family join:** after rebuilding a stale executable,
  the oracle again passed controls and reached both target phases. Retail
  title source bytes were written by `0x80007670`/`0x8001E2C0` families before
  the later `0x800078EC` clear; the real port reached hangar but its 512
  source writer rows and 4,082 image joins were all zero-valued. The silent
  arm emitted no source/image rows. This selects `H-RetailWriterEarlier` and
  moves the boundary to a port-side all-store census. See
  [M5-S3737-RETAIL-WRITER-FAMILY-JOIN.md](M5-S3737-RETAIL-WRITER-FAMILY-JOIN.md).
- **3738 — phase-scoped port writer census:** the oracle positive control and
  both target phases fired. The real port arm recorded 664 title-span scalar
  stores, all zero-valued `0x800078EC` byte stores, and no target-span scalar
  store after the hangar gate; silent emitted no source-DMA rows. This selects
  `H-PortEarlierWriterAbsent` for the measured scalar-store class and names
  `0x800078EC` as a legitimate zero-fill writer, not a mitigation target. See
  [M5-S3738-PORT-WRITER-CENSUS.md](M5-S3738-PORT-WRITER-CENSUS.md).
- **3739 — port family entry/setup census:** both `0x80007670` and
  `0x8001E2C0` executed and touched the measured source span, but the entries
  were shared pre-route setup and the qualified real source writer still had
  512 zero-payload rows. This refutes missing family entry and a nonzero
  family-write-then-clear path; value/setup provenance remains the boundary.
  See [M5-S3739-PORT-ENTRY-SETUP-CENSUS.md](M5-S3739-PORT-ENTRY-SETUP-CENSUS.md).
- **3740 — family value/call-edge provenance:** the fixed phase-scoped capture
  passed the oracle control and both phases. Real and silent arms had matching
  nonzero `rs_strncpy` caller/entry arguments in setup buffers; the texture-LUT
  family also matched at title setup. Neither candidate reached the qualified
  source span. Real still had 512 zero-payload source writes; silent had none.
  This refutes a call-edge value drop for the measured families and moves the
  boundary to the qualified-route predecessor/handoff. See
  [M5-S3740-FAMILY-VALUE-PROVENANCE.md](M5-S3740-FAMILY-VALUE-PROVENANCE.md).
- **3741 — qualified-route predecessor/handoff census:** the fixed oracle
  passed its whole-RDRAM control and reached title and hangar. In both target
  phases, route preparation at `0x80019CD8` had zero source fields and the
  `0x8000C628` handoff had zero value arguments. The real arm then emitted 512
  zero source-DMA rows; silent emitted none. This selects absent value at the
  measured handoff and rules out a nonzero-to-zero drop or later clear there.
  See [M5-S3741-ROUTE-HANDOFF-CENSUS.md](M5-S3741-ROUTE-HANDOFF-CENSUS.md).
- **3742 — all-generated-store route writer census:** the independent oracle
  passed its whole-RDRAM control and its title route-PC watch. The real and
  silent port arms both passed the writer-hook control and reached title and
  hangar. Their 512 target-phase route-span rows were all zero-valued writes
  from `0x8001A06C/74` and `0x8001C21C/24` to neighboring fields; no nonzero
  exact-field writer appeared. This selects absent earlier writer for the
  measured scalar-store class, while leaving non-scalar ownership versus
  metadata open. See [M5-S3742-ROUTE-VALUE-WRITER-CENSUS.md](M5-S3742-ROUTE-VALUE-WRITER-CENSUS.md).
- **3743 — exact route-field ownership:** the oracle control and both target
  phases fired; exact physical watches had no target-phase writes. A 379-site
  generated `+0x22/+0x60` witness passed controls in both arms; the qualified
  real-alone run reached title/hangar and had zero exact rows beside 512
  neighboring zero rows. This selects absent writer for that scalar class and
  leaves non-scalar/host ownership open. See
  [M5-S3743-EXACT-ROUTE-FIELD-OWNERSHIP.md](M5-S3743-EXACT-ROUTE-FIELD-OWNERSHIP.md).
- **3744 — non-scalar/DMA exact-route census:** retail passed the whole-RDRAM
  control and reached title/hangar; `0x128C92` had no writes and
  `0x128CD0..D3` had five writes from `0x8001BB14`. The qualified port passed
  both controls and both target phases; generated scalar/non-literal stores
  and RSP DMA had zero exact rows, while 512 neighboring rows were legitimate
  zero stores. Arbitrary host-side writes remain open. See
  [M5-S3744-NONSCALAR-HOST-EXACT-ROUTE.md](M5-S3744-NONSCALAR-HOST-EXACT-ROUTE.md).
- **3745 — host-side exact-route poll:** both qualified port arms passed
  controls and reached title/hangar. The portable 1 ms poll saw one initial
  exact snapshot and no later field transition in either arm; its B50 live
  RDRAM control fired five times per arm. Generated scalar/non-literal and
  RSP-DMA exact rows stayed zero. This selects the persistent-write null but
  leaves transient write-and-clear and writer-PC attribution open. See
  [M5-S3745-HOST-EXACT-ROUTE-POLL.md](M5-S3745-HOST-EXACT-ROUTE-POLL.md).
- **3746 — central host-write API census:** retail's whole-RDRAM control fired
  10,010 times and its exact-field watch found five early writes to
  `0x128CD0..D3` from `0x8001BB14`, but none to `0x128C92`. The port census
  passed per-API controls for PI ROM, RSP DMA, PI SRAM, and zmemcpy in the
  qualified silent arm and found zero target-phase exact rows; the qualified
  real arm likewise found zero. This selects absent writer for the censused
  host API class while leaving arbitrary direct host writes and
  `H-RouteStateNotSource` open. See
  [M5-S3746-HOST-WRITE-API-CENSUS.md](M5-S3746-HOST-WRITE-API-CENSUS.md).
- **3747 — remaining host RDRAM source census:** a repeatable 61-file scan
  found 11 target-literal occurrences, all in existing diagnostics, and no
  literal-target production host writer. Direct `rdram[...] =` sites were
  diagnostic fill markers; generic `MEM_*` writers are the already-censused
  APIs or runtime setup paths. This refutes only the literal-direct-writer
  class; it does not provide writer-PC attribution for computed pointers or
  external libraries. See
  [M5-S3747-HOST-RDRAM-WRITE-CENSUS.md](M5-S3747-HOST-RDRAM-WRITE-CENSUS.md).
- **3748 — native host writer-PC watch:** a single macOS ARM64 build added an
  `mprotect` watch for the exact route fields. Real and silent port arms both
  reached title/hangar and both fired the native page-fault positive control;
  neither produced an exact-field fault row. Retail independently passed the
  whole-RDRAM control, reached both phases, and observed the known
  `0x128CD0` guest write from `0x8001BB14`. This closes the remaining
  arbitrary native host-writer class for the qualified port capture while
  leaving route-state-versus-source interpretation open. See
  [M5-S3748-HOST-WRITER-FAULT-WATCH.md](M5-S3748-HOST-WRITER-FAULT-WATCH.md).
- **3751 — exact candidate load census:** retail passed its whole-RDRAM
  control and reached both target phases. The port hooked all nine sites and
  passed its hook control in both real/silent arms; real reached both phases
  with 1,024 source-reader and 512 source-writer rows, while silent reached
  both phases with no target source rows. Neither arm had a target-phase load
  whose effective base was `0x80128C70`. This selects
  `H-RouteStateNotSource` for the candidate set and refutes a candidate
  source-key read. See
  [M5-S3751-EXACT-CANDIDATE-LOAD-CENSUS.md](M5-S3751-EXACT-CANDIDATE-LOAD-CENSUS.md).
- **3752 — source producer boundary:** the retail oracle passed its control,
  reached both target phases, and attributed source-span writes to the known
  producer families. The fixed qualified real port arm passed its hook control,
  reached both phases, and joined 1,024 readers/512 writers/4,096 transitions;
  hangar reads at `0x80171E70` were already zero before the expected
  `0x1798B0 -> DMEM 0xCB0` DMA. The silent control emitted no source rows.
  This selects `H-PortSourceProducerAbsent` and moves the boundary upstream to
  task-data production. See
  [M5-S3752-SOURCE-PRODUCER-BOUNDARY.md](M5-S3752-SOURCE-PRODUCER-BOUNDARY.md).
- **3753 — generated task-data producer census:** the retail oracle independently
  passed its whole-RDRAM control and wrote the task-data span, including the
  `0x80090A..0x800911` family. The regeneration-safe port census passed its
  any-store control in both real/silent arms and recorded 4,096 target-phase
  scalar rows per arm, all zero-valued. Real still reached hangar and retained
  the zero source-DMA join; silent remained the no-source control. This selects
  `H-TaskDataProducerAbsent` for generated scalar stores and moves the boundary
  to host/RSP/non-scalar production. See
  [M5-S3753-TASK-PRODUCER-CENSUS.md](M5-S3753-TASK-PRODUCER-CENSUS.md).
- **3733 — retail source payload:** both retail target halves were nonzero;
  the full writer census named `0x80007670`, `0x8001E2C0`, and `0x8001F...`.
  The candidate port output watch had no target samples.
- **3732 — port image boundary:** a fixed real-audio capture reached title and
  hangar and fired controls; 1,903 sampled phase-5 joins had zero source-DMEM,
  output, and destination payloads. A prior paired capture was invalid, not
  evidence.
- **3731 — full-span producer census:** 78 nonzero stores occurred before the
  target route, but all 280 target-phase extension rows and later source
  payloads were zero; the known `0x800078EC` fill remained final.
- **3730 — source-layout join:** 512 source-range rows and 2,456 image-DMA
  joins used the expected descriptor; source, output, and post-write payloads
  were zero. Retail independently retained nonzero source content.
- **3728 — image payload:** 1,804 joined hangar rows had zero stage-3 source
  DMEM/output; 268 PCM consumers were also zero. This refuted a writeback or
  consumer gap at the qualified port boundary.
- **3725/3727 — route qualification:** paired real/silent arms reached both
  target phases and passed controls; only real audio produced image/source/DMA
  and image-stage rows. Silent remains the same-build control.
- **3690–3708 — source ownership and clear boundary:** input identity was
  earlier/equal, input/source/DMEM payloads matched, the expected source range
  was used, and the same `0x801797B0`/`0x298` object was legitimately cleared
  before later zero DMAs. These results move the boundary upstream; they do
  not authorize a clear suppression.

Detailed notes remain in the linked `M5-S37xx-*.md` files and the append-only
ledger. Do not repeat a boundary whose discriminator is already closed.

Session 3749 did not produce route-state evidence. A broad generated-load
transformer was abandoned after nested `S32(...)` expressions caused an
unterminated macro invocation; the regeneration recovery pass also stopped at
the existing `s3556 entry anchor count=0` fixup gate. Treat the route-state
read/use question as unevaluable, with no runtime conclusion.

Session 3750 did not produce route-state evidence either, but static and
runtime evidence invalidated the existing read/use hook itself: it samples
queue-dispatch registers rather than the exact route fields. Session 3751
then closed all nine bounded exact-offset candidates; the next route boundary
is upstream of those consumers.

## Durable operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. MusyX task data cannot be sent to
stock `aspMain`; the silent arm returns `Broke`. Never infer audio behavior
from a route that fails to reach the target phase.

Every instrument needs an independent ground-truth request, a same-run
positive control, a phase-scoped budget, and two evidence lines before its
result becomes current truth. Phase-gate animated comparisons on VI
transitions. Batch A/B arms in one build/run. A counter proving a branch ran
is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The s3579–s3584 retail-versus-port stored-value inference at `0x800078EC` is
unsupported: retail executes a byte store while the oracle had read an
aligned word containing neighboring bytes. Scalar samples measured zero
bytes with zero mismatches.

The request-only SP-yield/viewer-stall chain describes only the old diagnostic
arm. The old interpretation of the cinematic pool as an audio-slot pool was
superseded by the MusyX voice-table measurement. The claim that `0x8002BEEC`
is the retail JAL dispatch to `0x800078EC` remains route-dependent and
unreconciled.

The s3759 claim that the real image arm was pre-target unstable is superseded
as a general image-arm explanation by s3760: the same build reached both
target VIs in the paired run and again image-only. It remains valid only for
the s3759 capture; s3760 moves the unresolved paired-stability boundary to the
silent control.

## Evidence index

- [M5-S3734-RETAIL-PORT-BYTE-LAYOUT-JOIN.md](M5-S3734-RETAIL-PORT-BYTE-LAYOUT-JOIN.md)
- [M5-S3741-ROUTE-HANDOFF-CENSUS.md](M5-S3741-ROUTE-HANDOFF-CENSUS.md)
- [M5-S3743-EXACT-ROUTE-FIELD-OWNERSHIP.md](M5-S3743-EXACT-ROUTE-FIELD-OWNERSHIP.md)
- [M5-S3745-HOST-EXACT-ROUTE-POLL.md](M5-S3745-HOST-EXACT-ROUTE-POLL.md)
- [M5-S3746-HOST-WRITE-API-CENSUS.md](M5-S3746-HOST-WRITE-API-CENSUS.md)
- [M5-S3751-EXACT-CANDIDATE-LOAD-CENSUS.md](M5-S3751-EXACT-CANDIDATE-LOAD-CENSUS.md)
- [M5-S3753-TASK-PRODUCER-CENSUS.md](M5-S3753-TASK-PRODUCER-CENSUS.md)
- [M5-S3769-RETAIL-PORT-FAMILY-EDGE.md](M5-S3769-RETAIL-PORT-FAMILY-EDGE.md)
- [M5-S3770-FAMILY-STORE-PROVENANCE.md](M5-S3770-FAMILY-STORE-PROVENANCE.md)
- [M5-S3755-TASK-DATA-NATIVE-WRITE-CENSUS.md](M5-S3755-TASK-DATA-NATIVE-WRITE-CENSUS.md)
- [M5-S3758-TASK-DATA-NATIVE-COVERAGE.md](M5-S3758-TASK-DATA-NATIVE-COVERAGE.md)
- [M5-S3760-STEP1-IMAGE-QUALIFICATION.md](M5-S3760-STEP1-IMAGE-QUALIFICATION.md)
- [M5-S3736-EXACT-RETAIL-BYTE-JOIN.md](M5-S3736-EXACT-RETAIL-BYTE-JOIN.md)
- [M5-S3733-RETAIL-SOURCE-PAYLOAD.md](M5-S3733-RETAIL-SOURCE-PAYLOAD.md)
- [M5-S3732-IMAGE-PAYLOAD-BOUNDARY.md](M5-S3732-IMAGE-PAYLOAD-BOUNDARY.md)
- [M5-S3731-FULL-SPAN-PRODUCER.md](M5-S3731-FULL-SPAN-PRODUCER.md)
- [M5-S3730-SOURCE-LAYOUT-JOIN.md](M5-S3730-SOURCE-LAYOUT-JOIN.md)
- [M5-S3728-IMAGE-PAYLOAD-BOUNDARY.md](M5-S3728-IMAGE-PAYLOAD-BOUNDARY.md)
- [M5-S3725-STEP1-CONTROL-VALID.md](M5-S3725-STEP1-CONTROL-VALID.md)
- [M5-S3699-DMEM-DMA-COVERAGE.md](M5-S3699-DMEM-DMA-COVERAGE.md)
- [M5-S3706-WRITER-SETUP-REQUALIFICATION.md](M5-S3706-WRITER-SETUP-REQUALIFICATION.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3746 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
