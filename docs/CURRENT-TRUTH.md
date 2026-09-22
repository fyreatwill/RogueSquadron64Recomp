# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
 background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
notes are linked below. Updated for session 3686 (2026-09-21).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-image/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. The Factor 5 image task is the
qualified real-audio arm; `ROGUESQ_AUDIO_UCODE=0`/`Broke` is the silent control.
Audio is not production-complete.

The active M5 Step 3 boundary is the image-task source range
`0x1797B0..0x179930`. The port's target handoff sees a deliberate zero-fill
from `0x800078EC` (`rs_memset`, with tuples such as
`dst=0x801797B0, fill=0, len=0x298`) followed by zero source-DMA payloads.
Retail independently reaches the target phase, writes the watched source
span, and repeatedly calls `0x800078E0` with `a2=0x80` and changing structure
pointers from `0x800C825C`, unlike the port tuple. The target-phase retail
source writer is `0x800078EC` and runs before the first observed target VI. A
new oracle capture observed nonzero words and joined the
`0x800052C4 -> 0x800078E0 -> 0x800078EC` path with changing buffer/length
tuples. Session 3584 watched the qualified source buffer itself: all controls
and the target phase fired, but its phase histogram was mixed and exposed no
stable earlier constructor or distinct DMA/copy PC. The earlier-constructor
boundary is therefore unavailable to this oracle, not disproven; exact DMA
ordering remains open. The immediate producer context remains qualified, but
session 3659 found
that the stored-value divergence is not established: the oracle sampled an
aligned word after `sb`, including three bytes that instruction did not write.
Nonzero intermediate words cannot establish nonzero bytes written by memset. See
[M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md](M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md).

Session 3660 joined the live audio task/source contract. Retail's independent
`0x80033FCC` task watch and the port's task ABI/source-DMA rows both reached
title and hangar under positive controls. Target retail descriptors use
`0x80171CE0` (title) and `0x80171E70` (hangar), and the port reproduces those
addresses, but the port also interleaves `0x80173B20`/`0x80173CB0` objects with
different sizes, hashes, and DMA sources. This selects
`H-SameLogicalObject` for matching target rows while leaving the payload writer
and ownership of the interleaved objects open. See
[M5-S3660-AUDIO-SOURCE-OWNERSHIP.md](M5-S3660-AUDIO-SOURCE-OWNERSHIP.md).

Session 3661's phase-gated writer census passed the whole-RDRAM and task
controls in the oracle and the title/hangar and ABI controls in the port. The
phase-active descriptor ranges share a writer family headed by `0x80090DE4`,
but the phase-inactive ranges have no phase-gated writes: title writes
`0x173B20`/`0x173CB0`, while hangar writes `0x171E70`/`0x173CB0`. This selects
a shared producer for active ranges, not one universal writer for all four;
pre-phase initialization and interleaved-object ownership remain open. Session
3662 joined the family arguments to the task rows: title uses task data
`0x80173B20` and writer `$s1=0x80173B30`, while hangar uses `0x80171E70` and
`$s1=0x80171E80`. This selects a shared logical producer with phase-specific
field offsets; exact payload/DMA ordering remains open. See
[M5-S3662-WRITER-ARGUMENTS.md](M5-S3662-WRITER-ARGUMENTS.md).

Session 3663 added writer caller fields and an all-phase bucket. The retail
positive controls fired, and `0x80090DE4` retained `prev_pc=0x80090DE0` and
`$ra=0x80090ABC` across target and non-target phase buckets, ruling out a
caller-family split. Its task rows were title `0x80173B20` and hangar
`0x80173CB0`, unlike s3662's hangar `0x80171E70`; logical ownership remains
unresolved. The paired port arm crashed before phase controls, so this caller
result is single-source retail evidence. See
[M5-S3663-WRITER-CALLERS.md](M5-S3663-WRITER-CALLERS.md).

Session 3664's fixed route-task join passed the whole-RDRAM and title controls
and emitted 120 joined rows, but the capture remained in the title task loop
and never reached hangar 512. Within title, VI origin `0x00790400` selected
task data `0x80171CE0`, while `0x00790800` selected `0x80173B20`; both joined
the same `0x80090DE0`/`0x80090ABC` writer caller. This selects route-specific
task selection for the title buffer pair, not an all-phase producer. Hangar
ownership remains unevaluable. See
[M5-S3664-ROUTE-TASK-JOIN.md](M5-S3664-ROUTE-TASK-JOIN.md).

Session 3665 corrected an initially unarmed execution-watch capture by adding
explicit `--watch-pc` arms. The corrected retail run passed whole-RDRAM
(`275,347` writes), all four descriptor watches, both title origins, and both
hangar origins; it emitted `1,876` valid type-2 task rows and `2,656` writer
field rows with no invalid pointers or overflow. Title retained the s3664
mapping, but each hangar origin interleaved task data `0x80171E70` and
`0x80173CB0`. The dominant writer caller stayed `0x80090DE0`/`0x80090ABC`,
with a minor `ra=0x80090BB4` variant on hangar rows. This refutes a simple
one-task-per-origin route rule, supports a shared caller family, and leaves
object selection unresolved. See
[M5-S3665-HANGAR-TASK-JOIN.md](M5-S3665-HANGAR-TASK-JOIN.md).

Session 3667 phase-gated the image source span against selector/task activity.
The first source-span writes occurred at 6.8–7.0 s, before title VI at 17.4 s
and hangar VI at 38.4 s. The span had 674 writes; writer `0x800078EC`
accounted for 384, `0x80007670` for 172, and twelve smaller sites for 118.
No source-span writes appeared in the phase-gated title or hangar buckets,
while all whole-RDRAM, descriptor, selector, title, hangar, and task controls
fired. This selects `H-PayloadBeforeSelector` for the watched span and refutes
post-selector source activity, but object-specific writer/DMA ownership remains
open because multiple writers were observed. See
[M5-S3667-PAYLOAD-ORDER.md](M5-S3667-PAYLOAD-ORDER.md).

Session 3668's corrected oracle capture passed whole-RDRAM, all four
descriptor, title, hangar, and type-2 task controls. It recorded 674 source
span writes and 822 valid task rows. Bounded field-context joins for the
smaller source-writer sites followed task data `0x80173B20` in title and
`0x80173CB0` in hangar, but did not join the alternate `0x80171CE0`/
`0x80171E70` objects. The joins are latest-task-per-VI-bucket, not exact
store-to-task edges; `0x800078EC` was excluded from field dumping after its
high-cardinality rows prevented the first run reaching hangar. This is
single-source retail evidence and leaves primary-writer ownership unresolved.
See [M5-S3668-PRESELECTOR-WRITER-JOIN.md](M5-S3668-PRESELECTOR-WRITER-JOIN.md).

Session 3669's bounded exact-store capture passed whole-RDRAM, all four
descriptor, title, hangar, and type-2 task controls. All 384 stores by primary
writer `0x800078EC` carried invariant `$a0=0x801797B0`, `$a1=0`, `$a2=0x298`,
and `$ra=0x8008F2D4`, selecting a fixed zero-fill initializer rather than an
object-specific payload writer. This is single-source retail evidence; the
remaining source-span writers and exact DMA ordering remain open. See
[M5-S3669-PRIMARY-STORE-CONTEXT.md](M5-S3669-PRIMARY-STORE-CONTEXT.md).

Session 3670's corrected bounded exact-store capture passed the same controls
and covered all 290 remaining source-span stores: `0x80007670` accounted for
172 and the eleven smaller writer sites accounted for the rest. Static
disassembly identifies `0x80007670` as zero-padding in `rs_strncpy`, while the
smaller sites populate texture-data table record fields; their exact-store
contexts match those roles. This selects `H-RemainingInitialization` and
refutes these sites as object-specific audio payload owners. It is supported
by independent retail execution evidence plus static disassembly, but source
DMA ordering and later task ownership remain open. See
[M5-S3670-REMAINING-STORE-CONTEXT.md](M5-S3670-REMAINING-STORE-CONTEXT.md).

Session 3671's concurrent 55-second capture passed the oracle whole-RDRAM and
type-2 task controls and the port title/hangar and audio-task controls. The
port emitted 7,221 DMA rows; every watched source-span row was
`dmem_to_rdram` with zero nonzero payload bytes, including repeated
`0x1798B0..0x179930` writebacks. Target-phase task rows were dominated by
`0x80171E70`, while `0x80171CE0` appeared in the preceding phase. This
selects a zero-payload writeback path for the observed port rows and rejects
the claim that those rows are input DMAs consuming initialized records. It
does not expose the input RDRAM-to-DMEM ordering or join it exactly to task
ownership; the DMA direction was the opposite of the planned source-read
discriminator. The DMA result is single-source port evidence, with the
oracle providing independent drive/task controls. See
[M5-S3671-DMA-ORDER.md](M5-S3671-DMA-ORDER.md).

Session 3672 added a phase-gated RDRAM-to-DMEM witness for the same source span
and reran the qualified concurrent capture. All controls passed; 1,024 input
rows were observed (512 title, 512 hangar) alongside 512 writeback rows. Title
input payloads were nonzero (`source_nz=112/216` for its two chunks), while
hangar input payloads were zero; source and post-DMEM hashes matched in both
phases. This selects `H-InputDmaObserved` and refutes
`H-OnlyWritebackObserved`, but makes zero input phase-specific rather than a
global explanation. Direction/value rows remain single-source port evidence.
See [M5-S3672-INPUT-DMA-ORDER.md](M5-S3672-INPUT-DMA-ORDER.md).

Session 3673 joined each source-span input row to the active port audio task
by recording `s_pending_audio_task->data_ptr` in the reader witness. All 512
title rows carried `0x80171CE0` and nonzero source payloads; all 512 hangar
rows carried `0x80171E70` and zero source payloads. The ABI/task-object rows
and live task-pointer rows agree in the same run, selecting
`H-SameTaskInput` and `H-HangarZeroProducer` for this span and refuting
`H-InterleavedTaskInput`/`H-HangarZeroTransform` there. Other image-stage
objects and the producer of the hangar-zero bytes remain open. See
[M5-S3673-INPUT-TASK-OWNERSHIP.md](M5-S3673-INPUT-TASK-OWNERSHIP.md).

Session 3674 extended the stage witness with the live task pointer. Title
stage-2/3 rows were dominated by `0x80171CE0` (467/469 and 463/465), with two
rows per stage using `0x80173B20`; hangar stage-2/3 rows were dominated by
`0x80171E70` (796/797 each), with one row per stage using `0x80171CE0`.
Source-span rows remained `0x80171CE0` in title and `0x80171E70` in hangar,
and retail task controls reported those same dominant pointers. This selects
phase-dominant same-task ownership and stable hangar ownership, but refutes a
universal selector because sparse interleaved rows remain. Exact source-row
to-stage-row ordinal joining was not established because the two route ordinal
streams did not align in this capture. See
[M5-S3674-STAGE-TASK-JOIN.md](M5-S3674-STAGE-TASK-JOIN.md).

Session 3675's corrected concurrent capture passed the oracle whole-RDRAM,
source-span, descriptor, title, hangar, and type-2 controls plus the port
source-hook, phase, ABI, and stage controls. Title stage-2/3 alternate task
pointer `0x80173B20` occurred at route ordinals 1, 460, and 463; its stage-2
destinations varied across `0x80167350`, `0x80166A50`/`0x80166D50`, and
`0x80167650`. Hangar's alternate `0x80171CE0` occurred at ordinal 464 with
stage-2 destination `0x80167950`. This selects route-sequence correlation
over a single destination mapping, but exact source-reader/stage event joining
remains open, so callback timing is not refuted. See
[M5-S3675-SPARSE-STAGE-EXCEPTIONS.md](M5-S3675-SPARSE-STAGE-EXCEPTIONS.md).

Session 3676 added a thread-local source-span input event to stage rows. The
oracle and port controls fired, with 1,024 source-span input rows and 1,854
stage rows. Sparse title ordinal 1 had no source event; title ordinals 460/463
and hangar ordinal 464 retained event 1029, whose source row belonged to route
ordinal 92. Later hangar stages retained event 6372 from route ordinal 667.
This is single-source port evidence for callback/task timing, but the
thread-local handoff cannot distinguish cross-thread timing from missing
ownership. This led to the bounded task-keyed shared-record run in s3677. See
[M5-S3676-SPARSE-STAGE-EVENT-JOIN.md](M5-S3676-SPARSE-STAGE-EVENT-JOIN.md).

Session 3677 added and corrected a shared source/stage record keyed by task
pointer plus route ordinal/row. The qualified run passed oracle whole-RDRAM,
descriptor, title, hangar, and type-2 controls plus all port source/phase/ABI/
stage controls. It recorded 1,024 source rows and 1,922 stage rows. Across
3,770 bounded join-report observations there were 0 exact task-and-route
matches, 3,760 same-pointer/different-route fallbacks, 2
different-task fallbacks, and 8 missing records. Normal rows often differed by
one route ordinal; sparse rows retained much older same-pointer records. This
refutes pointer-only matching and an exact route/task join, while supporting
route/callback timing without distinguishing cross-thread timing from
publication lag. See
[M5-S3677-TASK-KEYED-SOURCE-STAGE-JOIN.md](M5-S3677-TASK-KEYED-SOURCE-STAGE-JOIN.md).

Session 3678 carried a monotonic generation from each port `M_AUDTASK`
`get_rsp_microcode` handoff into the source and stage witnesses. The qualified
run passed the oracle whole-RDRAM, descriptor, title, hangar, and type-2
controls plus the port source/phase/ABI/stage controls. It recorded 1,024
source rows and 1,903 stage-2 rows: 0 exact generation/route matches, 230
same-generation/different-route rows, 1,671 different-generation/
same-pointer rows, 1 different-generation/same-route row, and 1 unmatched row.
This refutes universal handoff-generation/route identity and leaves a mixed
cross-thread-or-stale-publication explanation: generation mismatch dominates,
but route drift also occurs. It is single-source port evidence because retail
cannot expose a host generation. See
[M5-S3678-TASK-GENERATION-JOIN.md](M5-S3678-TASK-GENERATION-JOIN.md).

Session 3679 carried a stable host-thread key from the port `M_AUDTASK`
handoff into the source and stage witnesses. The qualified concurrent run
passed the oracle whole-RDRAM, descriptor, title, hangar, and type-2 controls
and the port source/phase/ABI/stage controls. It recorded 1,024 source rows
and 1,254 stage-2 rows; every stage row had `handoff_thread=1` and
`event_thread=1`. This selects `H-SameThreadPublicationLag` over
`H-CrossThreadOwnership` for this run, while leaving the stale-record or
publication-order mechanism open. It is single-source port evidence for
thread identity; retail supplies the independent reachability controls. See
[M5-S3679-TASK-THREAD-JOIN.md](M5-S3679-TASK-THREAD-JOIN.md).

Session 3680 corrected the publication boundary by recording latest route
identity when `rs64_audio_route_prepare` publishes it, rather than sampling
the older route at `M_AUDTASK` handoff. The qualified run passed oracle watch/
task controls and port phase, source-hook, ABI, DMA, source, and stage controls.
All 3,836 stage rows matched both carried generation and latest route
ordinal/row. Source rows split 246 exact generation/route matches and 778
generation-only rows, showing source reads can precede route publication while
stage callbacks observe the current publication. This refutes stale stage
publication and stage-route sequencing as explanations of s3678's mismatch;
that mismatch was a handoff-boundary measurement artifact. Source-publication
ordering and exact input-DMA ownership remain open. See
[M5-S3680-PUBLICATION-ROUTE-JOIN.md](M5-S3680-PUBLICATION-ROUTE-JOIN.md).

Session 3681 added the publication snapshot to every source-span input-DMA
row and joined source events to stage events by task generation. The qualified
capture passed all oracle and port controls, reached title and hangar, and
emitted 1,024 source rows and 3,903 stage rows with no crash or abort. All
source rows had current task generation; 240 had current route publication and
784 were route-lagged. Every route-lagged source event preceded the first stage
event with the same generation, and no reversed source/stage ordering occurred.
The remaining 240 source rows had no same-generation stage row in the bounded
census; the existing fallback joined their stages to older source records, so
they do not prove a different-task owner. This selects
`H-SourceBeforePublish` for the dominant class and refutes the measured
`H-DmaPublicationRace` form, while leaving `H-SourceWrongTask` open for the
unmatched class. The ordering result is single-source port evidence; retail
independently validates route reachability and activity. See
[M5-S3681-SOURCE-PUBLICATION-ORDER.md](M5-S3681-SOURCE-PUBLICATION-ORDER.md).

Session 3682 added a generation-first stage matcher after the exact
route/ordinal class. The qualified run passed retail whole-RDRAM, descriptor,
title, hangar, and type-2 controls plus port phase/source-hook/ABI/DMA/source/
stage controls. It emitted 1,024 source rows and 1,879 stage rows with no crash
or abort. Generation-first matching produced 442 stage rows (182 title, 260
hangar), with equal source/stage generations and source events preceding stage
events. The remaining stage rows were 2,046 pointer-history, 5 broad-history,
and 10 unmatched. This selects `H-SourceSameGeneration` for the generation-
joinable class, but a stage-first matcher cannot classify source rows with no
stage callback; source-centric ownership of the prior 240-row minority remains
open. See [M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md](M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md).

Session 3683 added a source-centric generation census to the same qualified
capture. Retail whole-RDRAM, descriptor, source-span, title, hangar, and type-2
controls fired; the port reached title and hangar with source/stage/ABI/DMA
controls and no crash or abort. Title ended with 512/512 source rows having a
same-generation stage record and source-before-stage ordering. Hangar ended
with 282/512 same-generation rows, 230 generation-absent rows, and 0 reversed
rows. This selects `H-SourceWrongTask` for the measured hangar minority over
`H-SourcePublicationRace`, while extending `H-SourceSameGeneration` to the
hangar majority. It is single-source port evidence; generation absence does
not identify the guest producer or exact input-DMA owner. See
[M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md](M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md).

Session 3684 joined the generation-absent hangar source rows to input-DMA
and stage task pointers. The qualified capture passed all retail and port
controls, reached title and hangar, and recorded 512 hangar source rows; 220
had no matching stage generation. All 220 carried task pointer `0x80171E70`,
which also occurred in the stage stream, so no distinct task object was
selected by pointer. This refutes `H-AbsentDistinctTask` at the measured
pointer level and leaves later publication versus no-stage-consumer open. See
[M5-S3684-ABSENT-SOURCE-DMA-JOIN.md](M5-S3684-ABSENT-SOURCE-DMA-JOIN.md).

Session 3685 reran the qualified capture after fixing the census parser. All
retail and port controls passed, and the port reached title and hangar without
a crash or abort. Hangar had 512 source rows, 236 without a same-generation
stage row; every one used `0x80171E70` and had a later stage row with that
pointer and a greater generation. This selects `H-AbsentPublicationGap` over
`H-AbsentNoStageConsumer` for the measured minority. The later-stage relation
is single-source port evidence; exact route sequencing and input-DMA ownership
remain open. See
[M5-S3685-ABSENT-PUBLICATION-JOIN.md](M5-S3685-ABSENT-PUBLICATION-JOIN.md).

Session 3666 joined the selector publication to the task stream. The
immediately preceding selector value matched every task data pointer: title
selected `0x80173B20`/`0x80171CE0`, while each hangar origin interleaved
`0x80171E70`/`0x80173CB0`. The dominant writer caller remained shared. This
selects `H-SelectorInterleave` and refutes stable-selector downstream object
selection; payload writer and DMA ordering remain open. See
[M5-S3666-SELECTOR-INTERLEAVE.md](M5-S3666-SELECTOR-INTERLEAVE.md).

Do not force the cinematic flag at `0x800B0934`, bypass the state machine, or
rewrite task, audio, PCM, selector, or output state. The default route's null
stage-advancer input is a known route/configuration issue; the validated
real-audio route is the comparison arm.

## Next steps

The backlog is one monotonic sequence. Work only the first applicable item.

1. M5 Step 3: distinguish stale same-thread task publication from route
   sequencing, then resolve exact DMA ordering and downstream task ownership
   after
   selector interleave. Session 3667 selected `H-PayloadBeforeSelector`
   for source span `0x1797B0..0x179930`: its first writes were at 6.8–7.0 s,
   before title/hangar VI, and no writes landed in target phase buckets. The
   span has multiple writers, dominated by `0x800078EC`, so join each source
   writer (and any exposed DMA/copy event) to the selected object and task.
   Require whole-RDRAM, title, and hangar controls. See
   [M5-S3667-PAYLOAD-ORDER.md](M5-S3667-PAYLOAD-ORDER.md).
   Session 3664 ruled out neither hangar object ownership nor a shared
   all-phase producer. Session 3662 selected
   `H-SharedLogicalProducer`: the dominant writer family joins
   the phase task rows at `data_ptr+0x10` in both title and hangar. Next
   distinguish the phase-inactive ranges from pre-phase initialization and
   identify the payload writer/source-DMA ordering for matching and
   interleaved objects. Session 3660 qualified matching target descriptors,
   but the port interleaves additional source objects. Continue
   to identify the writer/ownership boundary for the target and interleaved
   descriptor ranges (`0x80171CE0`, `0x80171E70`, `0x80173B20`, `0x80173CB0`)
   with phase-gated retail writer-PC watches and the existing port task/source
   rows. The s3659 scalar-store capture refuted
   the old nonzero-memset inference: 1,844 sampled stores wrote zero, all
   matching the source register. The aligned words were nonzero in 829 cases.
   Exact DMA ordering remains open; do not add a writeback/zero-fill mitigation.
   S3669's exact-store context identifies primary `0x800078EC` as a fixed
   zero-fill initializer (`a0=0x801797B0`, `a1=0`, `a2=0x298`, `ra=0x8008F2D4`)
   rather than an object-specific writer. This is single-source evidence and
   removes the primary writer from the object-ownership candidate set; join
   the remaining `290` source-span writes, especially `0x80007670` and the
   smaller writer PCs, to selector/task objects and any exposed DMA/copy
   event. S3668's smaller-writer joins are only single-source,
   latest-task-per-VI-bucket evidence. See
   [M5-S3669-PRIMARY-STORE-CONTEXT.md](M5-S3669-PRIMARY-STORE-CONTEXT.md).
   Session 3670 removed all 290 remaining source-span CPU stores from the
   object-payload candidate set: `0x80007670` is `rs_strncpy` zero padding and
   the smaller sites populate texture-data records. The next discriminator is
   a same-run ordering/join of source-DMA events with the selected task rows.
   S3671 showed that the existing watched span reports `dmem_to_rdram`
   zero-payload writebacks, so those rows are not source reads. S3672 exposed
   the opposite direction: title reads carry nonzero data, while hangar reads
   are zero and hash-identical after staging. Next join the observed input-DMA
   event/route ordinal to the selected task object and determine whether the
   hangar zero source is produced by the same logical object or a distinct
   pre-task state. S3673 selected matching task ownership for the watched
   source span and phase-specific pre-staging zero; it did not identify the
   hangar-zero producer or other stage ownership. Session 3674 found
   phase-dominant stage-task matches but sparse pointer exceptions, and the
   exact source/stage route ordinals did not align. Session 3675 classified
   the sparse exceptions: title alternates occurred at route ordinals 1, 460,
   and 463 with varying stage-2 destinations, while the hangar alternate
   occurred at ordinal 464. This favors route-sequence selection over a fixed
   destination mapping, but the source-reader/stage event key is still
   missing. Next add one shared event/route sequence to the stage and source
   witnesses, then test whether each exception's input-DMA event carries the
   same pointer. See
   [M5-S3675-SPARSE-STAGE-EXCEPTIONS.md](M5-S3675-SPARSE-STAGE-EXCEPTIONS.md),
   [M5-S3676-SPARSE-STAGE-EVENT-JOIN.md](M5-S3676-SPARSE-STAGE-EVENT-JOIN.md),
   [M5-S3674-STAGE-TASK-JOIN.md](M5-S3674-STAGE-TASK-JOIN.md),
   [M5-S3673-INPUT-TASK-OWNERSHIP.md](M5-S3673-INPUT-TASK-OWNERSHIP.md),
   [M5-S3672-INPUT-DMA-ORDER.md](M5-S3672-INPUT-DMA-ORDER.md), and
   [M5-S3671-DMA-ORDER.md](M5-S3671-DMA-ORDER.md).
   S3677 refuted pointer-only and exact route/task matching. S3678's mismatch
   was measured against the handoff-boundary route and is superseded by s3680:
   after moving the route sample to actual publication, all 3,836 stage rows
   matched both generation and route. Source rows still split 246 exact versus
   778 generation-only, so the next discriminator is source-read versus route-
   publication ordering and exact input-DMA ownership. S3681 selected
   source-before-publication for 784 route-lagged rows and found no reversed
   source/stage ordering, but 240 source rows had no same-generation stage row.
   Session 3682 made the matcher prefer task generation before pointer/history
   fallback and classified 442 stage rows, but did not classify source rows
   lacking a stage callback. S3683's source-centric census classified title
   source rows as 512/512 same-generation and hangar rows as 282/512
   same-generation, 230 generation-absent, and 0 reversed. This selects
   `H-SourceWrongTask` for the hangar minority over a publication race, but
   does not identify its guest producer or exact input-DMA owner. Next join
   generation-absent source rows to the input-DMA event and selected task
   object in one phase-gated capture. S3684 found 220 absent-generation
   hangar rows, all with `0x80171E70`, also present in the stage stream. Next
   compare later same-pointer publications against no-stage-consumer rows.
   S3685 found all 236 generation-absent rows had a later same-pointer stage
   generation, selecting `H-AbsentPublicationGap`; the ABI publication key
   was not joinable. Next classify whether the later stage is on the same or
   a later route ordinal and preserve the source event/DMA identity. Do not
   add a guard. See [M5-S3685-ABSENT-PUBLICATION-JOIN.md](M5-S3685-ABSENT-PUBLICATION-JOIN.md).
2. Keep the s3554 slot-dispatch failure parked as route-specific absence.
   Revisit only with a new route discriminator; do not add a slot guard.
3. Keep the silent-arm `fillSampleStreamRange` crash separate from the
   real-audio target path, and do not infer target behavior from it.
4. M5's exact DMA ordering remains unresolved and unavailable to the current
   oracle. While it is parked, perform only systematic M3 idiom-class audits.
   Sessions 3586–3658 closed the generated `jal rs_free` census through
   `funcs_7.c`, all of `funcs_6.c`, all of `funcs_4.c`, all of
   `funcs_2.c`, plus `processAssetLoadStep`/`mainEventQueueWorker`
   `0x48($s0)`, `findManifestEntryByName` `$s2`,
   `freeManifestSegmentAssets` `0x40($s0)`,
   `teardownAssetManifestService` `*0x80110D50`, and the earlier
   MusyX/MORT field families. `funcs_5.c`, `funcs_3.c`, and `funcs_0.c`
   have zero sites. The only remaining Gap is s3636
   `attachedMeshOverlayNpcHandler` `0x1C`/`0x20`: opcode 2 frees those
   words when setup stores type `-1` or parent mesh `+0xC` is NULL,
   without a prior NULL store. Do not re-audit a Complete class. Do not add a
   pointer guard without a concrete invalid writer. Do not land a skip-path
   NULL store for that Gap unless a later census identifies that same writer.
   The closed-class list and per-session notes live in
   [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §56.
   The next M3 unit is `rs_zcfree` `rs_free` of incoming `$a0` at
   `0x80005268` (last original `jal 0x80001C98` in `funcs_1.c`).
5. Generated-symbol renaming remains last priority. Resume only when M5 is
   closed and M3 is parked with no new discriminator.

## Active hypothesis table

| Hypothesis | Discriminating result |
|---|---|
| H-RetailWriterSame | Selected for target-phase identity/order: `0x800078EC` writes at 47.4 s before target VI at 48.5 s. |
| H-RetailWriterOther | Refuted for the target-phase write; earlier setup writers are separate activity. |
| H-RetailOrdering | Exact DMA ordering remains unmeasured. |
| H-RetailValue | Whole-word nonzero samples do not establish a nonzero byte store; s3659 measured 1,844 zero bytes with zero mismatches. |
| H-RetailProducer | `0x800052C4` is repeatedly the immediate caller of `0x800078E0`; no earlier constructor was exposed by the repeated field table. |
| H-RetailDmaOrder | No separate DMA event identifier was exposed; ordering remains open. |
| H-SameLogicalObject | Selected at s3660 for matching target task rows; the same task contract and target descriptor addresses recur, while interleaved objects have differing payload/source-DMA identities. |
| H-DifferentObject | Applies only to s3660's interleaved helper rows; not selected for matching target rows. |
| H-SharedPhaseProducer | Selected at s3661 for phase-active descriptor ranges: the same `0x80090DE4`-headed writer family writes target/interleaved ranges within each phase. |
| H-SharedLogicalProducer | Selected at s3662: title task `0x80173B20` joins writer `$s1=0x80173B30`, and hangar task `0x80171E70` joins `$s1=0x80171E80`; phase-specific fields use the same logical task contract. |
| H-SeparateLogicalProducer | Refuted for the joined target rows at s3662; separate low-level destination bases were not observed after task-argument joining. |
| H-SharedCallerSeparateObject | Selected only at caller level by s3663: `0x80090DE0`/`0x80090ABC` spans target and non-target buckets, but task-object identity remains route-dependent. |
| H-RouteTaskSelection | Selected within s3664/s3665 title buffers, but refuted as a complete rule for hangar: both 512 origins interleave `0x80171E70` and `0x80173CB0`. |
| H-SharedLogicalProducerAllPhases | Not selected: s3665 confirms a shared caller but not one logical task object across hangar rows. |
| H-SelectorInterleave | Selected at s3666: the immediately preceding selector publication equals each task data pointer, including both alternating hangar objects. |
| H-SeparateProducer | Not supported at caller level: dominant `0x80090DE0` remains shared; minor `$ra` variant needs field joining. |
| H-SharedProducerWithTwoObjects | Refuted at s3666: selector source changes with the task object. |
| H-DmaAfterSelector | Refuted for watched source span at s3667: all 674 writes preceded title/hangar phase buckets; DMA identity remains unexposed. |
| H-SeparatePayloadWriter | Open: source span has multiple writers (`0x800078EC` dominates), but object-specific ownership is not joined. |
| H-PayloadBeforeSelector | Selected for watched source span at s3667: first writes at 6.8–7.0 s preceded title VI at 17.4 s and hangar VI at 38.4 s. |
| H-PreSelectorObjectWriter | Limited single-source selection at s3668 for smaller writer sites: title joins `0x80173B20`, hangar joins `0x80173CB0`; latest-task-per-VI-bucket only. |
| H-PrimaryWriterContext | Superseded at s3669: bounded exact-store context identifies `0x800078EC` as fixed initialization; alternate ownership remains open. |
| H-PrimaryInitialization | Selected single-source at s3669: all 384 exact `0x800078EC` stores used invariant `a0=0x801797B0`, `a1=0`, `a2=0x298`, `ra=0x8008F2D4`; remaining writers are open. |
| H-OneWriterAllRanges | Refuted at s3661: title and hangar have different phase-active subsets, with no phase-gated writes to the other ranges. |
| H-PrePhaseInitialization | Remains open for phase-inactive ranges; absence inside a phase does not identify their earlier writer. |
| H-CaptureInvalid | Refuted for s3659 and s3660: whole-RDRAM, source/task, writer-PC, and target-phase controls fired. |
| H-MortComplete | Selected structurally: the `0x8009D7D0..0x8009DD7C` path has complete bounded stages and publication edges. |
| H-MortGap | No concrete missing/invalid writer, consumer, base, or bound was found. |
| H-MortMisread | Not supported: the range is a coherent CPU voice-filter/mix/compand path. |
| H-NextClassComplete | Selected for `teardownAssetManifestService` `*0x80110D50`: one flags-0x81 extra-heap malloc store / one destructor with original NULL skip; generated boot caller passes size 0 so the malloc is an unreferenced original branch. |
| H-NextClassGap | Refuted for this `*0x80110D50`. Remains selected for overlay `0x1C`/`0x20` (s3636). |
| H-NextClassUnevaluable | Not selected: one word, one malloc store, one destructor. |
| H-ExceptionTiming | Supported at s3677: 0 exact route/task joins, 3,760 same-pointer/different-route report fallbacks, and stale sparse records; cross-thread timing versus publication lag remains open. |
| H-ExactTaskRoute | Refuted at s3677: the shared task-pointer/route-keyed record produced 0 exact matches across 1,922 stage rows and 3,770 report observations. |
| H-TaskPointerReuse | Selected at s3677: same task pointers were reused across route ordinals, so pointer-only joins attached older source records. |
| H-GenerationRouteIdentity | Refuted at s3678: 0 exact generation/route matches across 1,903 stage-2 rows. |
| H-RoutePublicationLag | Remains supported: 230 rows shared a generation but differed in route. |
| H-CrossThreadTask | Remains supported, single-source: 1,671 rows had different generations despite the same task pointer. Thread identity is the next discriminator. |
| H-StageCurrentPublication | Selected at s3680: all 3,836 stage rows matched latest generation and route publication; s3678's mismatch used the wrong boundary. |
| H-SourceBeforePublication | Selected at s3680 for 778/1,024 source rows: generation matched but source route identity preceded the latest route publication. |
| H-SourceSameGeneration | Selected at s3682 for 442 stage rows: generation-first matching found equal nonzero source/stage generations with source before stage; source rows lacking a stage callback remain open. |
| H-SourceWrongTask | Selected single-source at s3683 for 230/512 hangar source rows with no same-generation stage record; guest producer/ownership remains open. |
| H-SourcePublicationRace | Refuted for the s3683 measured source rows: 0 reversed stage-before-source rows; title and matched hangar rows were source-before-stage. |
| H-AbsentDistinctTask | Refuted at s3684's pointer level: all 220 generation-absent hangar source rows used `0x80171E70`, also present in the stage stream. |
| H-AbsentNoStageConsumer | Refuted for the measured s3685 rows: all 236 generation-absent rows had a later same-pointer stage generation. |
| H-AbsentPublicationGap | Selected at s3685 for generation-absent hangar rows; s3686 resolved the measured route relation. |
| H-SameRoutePublicationLag | Refuted at s3686: 0/244 absent-generation rows had a later same-pointer stage on the source route. |
| H-LaterRouteReuse | Selected at s3686: 244/244 classified absent-generation rows advanced to a later route ordinal/row while retaining pointer `0x80171E70`. |
| H-NoStableRouteJoin | Refuted at s3686 for the measured rows: 0 contradictory or missing-route classifications. |

The current work-unit slug is `m5-audio-source-ownership`.

## Recent evidence ledger

- **3683 — source-centric generation census:** the qualified concurrent
  capture passed retail whole-RDRAM, descriptor, source-span, title, hangar,
  and type-2 controls plus port source/stage/ABI/DMA controls. Title had
  512/512 same-generation source rows; hangar had 282/512 same-generation,
  230 generation-absent, and 0 reversed. This selects `H-SourceWrongTask` for
  the measured hangar minority over a publication race, but is single-source
  port evidence and leaves guest producer/input-DMA ownership open. See
  [M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md](M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md).

- **3684 — absent-source DMA/task join:** the qualified concurrent capture
  passed all controls and recorded 512 hangar source rows, 220 without a
  matching stage generation. Every absent row used task pointer `0x80171E70`,
  also present in the stage stream; distinct task-pointer ownership was not
  selected. Later publication versus no stage consumer remains open. See
  [M5-S3684-ABSENT-SOURCE-DMA-JOIN.md](M5-S3684-ABSENT-SOURCE-DMA-JOIN.md).

- **3685 — absent-source publication join:** the fixed qualified capture
  passed all controls and recorded 512 hangar source rows, 236 without a
  same-generation stage row. Every absent row used `0x80171E70` and had a
  later stage row with that pointer and a greater generation; no row lacked a
  later same-pointer stage. This selects `H-AbsentPublicationGap` over
  `H-AbsentNoStageConsumer`, while exact route sequencing and input-DMA
  ownership remain open. See
  [M5-S3685-ABSENT-PUBLICATION-JOIN.md](M5-S3685-ABSENT-PUBLICATION-JOIN.md).

- **3686 — absent-source route join:** the qualified concurrent capture
  passed all retail and port controls and recorded 512 hangar source rows.
  Among 244 rows without a same-generation stage, 0 matched the source route,
  244 matched a later route, and 0 were contradictory or missing. This selects
  `H-LaterRouteReuse` over same-route publication lag for the measured rows;
  exact input-DMA ownership remains open. See
  [M5-S3686-ABSENT-ROUTE-JOIN.md](M5-S3686-ABSENT-ROUTE-JOIN.md).

- **3678 — task-generation source/stage join:** the qualified concurrent
  capture passed all controls and recorded 1,024 source rows and 1,903
  stage-2 rows. There were 0 exact generation/route matches, 230
  same-generation/different-route rows, and 1,671 different-generation/
  same-pointer rows. This is mixed, single-source port evidence; thread
  identity remains open. See
  [M5-S3678-TASK-GENERATION-JOIN.md](M5-S3678-TASK-GENERATION-JOIN.md).

- **3677 — task-keyed source/stage join:** the corrected concurrent capture
  passed all oracle and port controls and recorded 1,024 source rows and
  1,922 stage rows. Across 3,770 report observations there were 0 exact
  task-pointer/route matches, 3,760 same-pointer/different-route fallbacks, 2
  different-task fallbacks, and 8
  missing records. This selects task-pointer reuse and supports timing or
  publication lag, but does not distinguish cross-thread ownership. See
  [M5-S3677-TASK-KEYED-SOURCE-STAGE-JOIN.md](M5-S3677-TASK-KEYED-SOURCE-STAGE-JOIN.md).

- **3669 — primary exact-store context:** the corrected retail oracle capture
  passed all controls and recorded 384 exact `0x800078EC` stores, all from the
  same zero-fill call context (`a0=0x801797B0`, `a1=0`, `a2=0x298`,
  `ra=0x8008F2D4`). This selects primary initialization but is single-source;
  the remaining 290 source-span writes and DMA ordering remain open. See
  [M5-S3669-PRIMARY-STORE-CONTEXT.md](M5-S3669-PRIMARY-STORE-CONTEXT.md).

- **3668 — pre-selector writer context:** the corrected retail oracle capture
  passed all controls and reached title and hangar. Smaller writer-site field
  joins followed `0x80173B20` in title and `0x80173CB0` in hangar, but did not
  establish exact store-to-task edges or primary `0x800078EC` ownership. This
  is single-source evidence. See
  [M5-S3668-PRESELECTOR-WRITER-JOIN.md](M5-S3668-PRESELECTOR-WRITER-JOIN.md).

- **3667 — payload ordering:** the corrected phase-gated oracle capture passed
  whole-RDRAM, descriptor, title, hangar, selector, and task controls. The
  first writes to `0x1797B0..0x179930` occurred at 6.8–7.0 s, before title VI
  at 17.4 s and hangar VI at 38.4 s; 674 writes were attributed to multiple
  PCs, dominated by `0x800078EC` (384). This selects payload-before-selector
  for the watched span and leaves object-specific ownership/DMA identity open.
  See [M5-S3667-PAYLOAD-ORDER.md](M5-S3667-PAYLOAD-ORDER.md).

- **3666 — selector interleave:** the corrected phase-gated oracle capture
  passed all controls and joined the selector publication to 1,878 task rows.
  Selector source matched task data exactly, including both alternating hangar
  objects, selecting `H-SelectorInterleave`. Payload writer and source-DMA
  ordering remain open. See
  [M5-S3666-SELECTOR-INTERLEAVE.md](M5-S3666-SELECTOR-INTERLEAVE.md).

- **3664 — route task join:** the fixed bucket-local join passed the
  whole-RDRAM and title controls and emitted 120 rows. Title buffer origins
  selected distinct task data pointers (`0x80171CE0` versus `0x80173B20`)
  under one writer caller family; the capture never reached hangar, so
  all-phase ownership remains open. See
  [M5-S3664-ROUTE-TASK-JOIN.md](M5-S3664-ROUTE-TASK-JOIN.md).

- **3665 — hangar task join:** the corrected execution-watch run passed all
  controls and emitted 1,876 valid task rows. Title retained its origin split;
  each hangar origin interleaved `0x80171E70` and `0x80173CB0` under the same
  dominant caller family. See
  [M5-S3665-HANGAR-TASK-JOIN.md](M5-S3665-HANGAR-TASK-JOIN.md).

- **3659 — corrected store-width evidence:** all 1,844 sampled retail memset
  stores were zero with zero mismatches, despite 829 nonzero containing words.
  Oracle build and UBSan regression tests passed. Both title/hangar controls
  fired. See [M5-S3659-SCALAR-STORE-EVIDENCE.md](M5-S3659-SCALAR-STORE-EVIDENCE.md).
- **3660 — audio task/source ownership join:** the independent retail task
  dump and port ABI/source-DMA rows passed controls and reached title and
  hangar. Matching target descriptors recur, but interleaved port objects have
  different sizes, hashes, and DMA ranges; source ownership remains open. See
  [M5-S3660-AUDIO-SOURCE-OWNERSHIP.md](M5-S3660-AUDIO-SOURCE-OWNERSHIP.md).
- **3661 — descriptor writer-PC census:** whole-RDRAM and task controls passed.
  Title's active `0x173B20`/`0x173CB0` ranges and hangar's active
  `0x171E70`/`0x173CB0` ranges share the `0x80090DE4`-headed writer family;
  inactive ranges were not written during their phase. See
  [M5-S3661-DESCRIPTOR-WRITERS.md](M5-S3661-DESCRIPTOR-WRITERS.md).
- **3662 — writer-argument/task join:** whole-RDRAM and task controls passed.
  The title and hangar task data pointers joined the dominant writer-family
  `$s1` fields at `+0x10`, selecting shared logical ownership. See
  [M5-S3662-WRITER-ARGUMENTS.md](M5-S3662-WRITER-ARGUMENTS.md).
- **3663 — writer caller/all-phase census:** whole-RDRAM, title/hangar VI,
  and task controls passed. The caller identity was stable across phase
  buckets, but the hangar task tuple differed from s3662; logical ownership
  remains unresolved. See [M5-S3663-WRITER-CALLERS.md](M5-S3663-WRITER-CALLERS.md).

Only the latest boundary transitions are repeated here; the append-only ledger
and evidence notes retain the full history. Sessions 3586–3657 M3 class
closeouts are archived in PROJECT-OVERVIEW §56.

- **3682 — generation-first source/stage join:** the qualified capture passed
  retail and port controls and reached title and hangar. Generation-first
  matching produced 442 stage rows (182 title, 260 hangar) with equal
  nonzero generations and source-before-stage ordering. The stage-first
  diagnostic cannot classify source rows with no stage callback; exact
  input-DMA ownership remains open. See
  [M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md](M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md).

- **3658 — teardownAssetManifestService rs_free of *0x80110D50:**
  Live writer is `initDmaSlots` flags-0x81 `rs_malloc($s3)`
  store at `0x80004708`. Flag-zero path stores NULL. The only
  generated `initDmaSlots` caller is boot `0x800011EC` with
  `$a0 = 0`, so the malloc is an unreferenced original branch.
  Destructor `0x80005000` has an original NULL skip and zero
  generated callers. `initRsMallocHeap` and `*0x80111260` are
  consumers. Adjacent `0xD48`/`0xD4C`/`0xD54` are size and
  worker-handle words. This selects `H-NextClassComplete`. See
  [M3-S3658-TEARDOWN-ASSET-MANIFEST-SERVICE-RS-FREE-AUDIT.md](M3-S3658-TEARDOWN-ASSET-MANIFEST-SERVICE-RS-FREE-AUDIT.md).
- **3657 — freeManifestSegmentAssets rs_free of 0x40($s0):** `$s0`
  is `0x80110A80 + idx*0x50`. Live writer is flags-9
  `rs_malloc` store at `0x80004920`. Two mutually exclusive
  destructors (`$a0 == -1` gated by `0x4E==1`; else single-slot).
  Post-free clears `0x4E`, not `0x40`. `find_manifest_entry`
  `0x80003AC8` walks the payload as a directory. ROM name-table
  `+0x18` is 0; skip does not fire. Six generated callers pass the
  find return or leftover `*0x80137CFC`. This selects
  `H-NextClassComplete`. See
  [M3-S3657-FREE-MANIFEST-SEGMENT-ASSETS-RS-FREE-AUDIT.md](M3-S3657-FREE-MANIFEST-SEGMENT-ASSETS-RS-FREE-AUDIT.md).
- **3656 — findManifestEntryByName rs_free of $s2:** `$s2` is
  flags-9 `rs_malloc(8)` at `0x800048A4`, never stored. DMA dest then
  destructor `0x8000490C`; delay-slot `lw $s2, 0x0($a0)` consumes
  header word 0 as a ROM offset (`$a0` still the malloc). Skip when
  name-table `+0x18 != 0` leaks the unpublished 8-byte buffer; that
  word is ROM-DMA'd by `initDmaSlots`, not this pointer. Slot `+0x40`
  is the later payload malloc. This selects `H-NextClassComplete`. See
  [M3-S3656-FIND-MANIFEST-ENTRY-BY-NAME-RS-FREE-AUDIT.md](M3-S3656-FIND-MANIFEST-ENTRY-BY-NAME-RS-FREE-AUDIT.md).
- **3655 — processAssetLoadStep rs_free of 0x48($s0):** `$s0` is
  `D_80110D60 + (*0x80111240)*0x74`. Live writers are flags-9
  `rs_malloc(0x10)` at `0x80003EA0`/`0x80003F0C` and
  `rs_malloc(0x1000)` at `0x80003FC4`. Type-2 enqueue NULLs the word.
  In-step destructor `0x80003E7C` frees the 0x10 buffer and NULLs;
  caller `0x8000450C` frees leftover (0x1000 or already-NULL).
  `0x10($s0)` is z_stream `next_in`, not a sibling free. This selects
  `H-NextClassComplete`. See
  [M3-S3655-PROCESS-ASSET-LOAD-STEP-RS-FREE-AUDIT.md](M3-S3655-PROCESS-ASSET-LOAD-STEP-RS-FREE-AUDIT.md).
- **3653 — initSaveData rs_free of $s2 and freeSaveDataBuffer *0x80112724:**
  `$s2` is flags-8 `rs_malloc(*0x801126C4)` at `0x800065E0`, never
  stored to a global. Two mutually exclusive frees.
  `*0x80112724` is flags-0x81 `rs_malloc` stored at `0x800063D0`;
  remaining loads are consumers. Re-init leaks; it is not a second
  free. See
  [M3-S3653-INIT-SAVEDATA-RS-FREE-AUDIT.md](M3-S3653-INIT-SAVEDATA-RS-FREE-AUDIT.md).
- **3652 — freeRenderSubsystemResources rs_free of *0x8011A444 and four siblings:**
  Live writers are `buildAndRegisterDefaultMaterial` flags-0 `rs_malloc`
  stores at `0x80017D28` / `0x80017D4C` / `0x80017D80` / `0x80017E64` /
  `0x80017E74`. One destructor wrapper; host
  `MATERIAL_ARRAY_PTR_GUARD` is not an original skip. `funcs_4.c`
  `jal rs_free` is exhausted. See
  [M3-S3652-FREE-RENDER-SUBSYSTEM-RESOURCES-RS-FREE-AUDIT.md](M3-S3652-FREE-RENDER-SUBSYSTEM-RESOURCES-RS-FREE-AUDIT.md).
- **3651 — uploadTextureDescriptorData rs_free of $s1:**
  `$s1` is incoming `$a1`, the delay-slot interior
  `0x0($s2) + (*(*s2+0xC)*($s1&0xFFFF)+0x14)` of the
  `loadAssetIntoNewSlot` converted-buffer malloc at
  `0x80054970`. Only generated caller is
  `tickWrappingTimerAccumulatorList`. Byte 2 of that
  header is 0 (`fillTextureDescriptorNoCopy` /
  dest-already-set `loadAndDecodeTexture`).
  `copyTextureDescriptorWithData` (the malloc-and-set-1
  clone) is unreferenced. Original byte-2 skip is taken;
  the interior is never passed to `rs_free`. Matching
  destructor of the header is `freeAnimationPhasePool`
  (closed s3634), a different pointer. This selects
  `H-NextClassComplete`. See
  [M3-S3651-UPLOAD-TEXTURE-DESCRIPTOR-DATA-RS-FREE-AUDIT.md](M3-S3651-UPLOAD-TEXTURE-DESCRIPTOR-DATA-RS-FREE-AUDIT.md).
- **3650 — destroyTextureLUTs rs_free of *0x80128F08 / *0x80128EFC:**
  Live writers are `initTextureLUTAndAllocBuffers` flags-0
  `rs_malloc` stores at `0x8001E274` / `0x8001E290`.
  `initTextureMaterialPools` is an unreferenced clone.
  One destructor pair. Host TEXDATA substitutions are not
  original skips. See
  [M3-S3650-DESTROY-TEXTURE-LUTS-RS-FREE-AUDIT.md](M3-S3650-DESTROY-TEXTURE-LUTS-RS-FREE-AUDIT.md).
- **3649 — maintenance compaction:** `docs/CURRENT-TRUTH.md` exceeded the
  60,000-byte trigger (60,386 bytes / 1,020 lines). Closed M3 `rs_free`
  session-by-session narrative was migrated to PROJECT-OVERVIEW §56; the
  live next unit is unchanged. Soak-queue tail added no post-3577 result.
- **3648 — loadDebugAssets rs_free of $s0:** `$s0` is the matching
  `get_asset_size_extra` `rs_malloc($s2, 8)` at `0x80024768`. Never stored
  to a global. Incoming `$s3` is `*0x8010E008`. The ROM string at
  `0x80000A48` is overwritten before the free. DMA slot `+0x24` is dest
  only; `teardownAssetDma` does not `jal rs_free`.
  `registerHmtTextureInTable` copies pixels and keeps a texture-id
  halfword at `0x80128F22`. One destructor; `-1` skip is paired. Two
  generated callers; zero overlay lookup. One `jr $ra`. `funcs_7.c`
  `jal rs_free` is exhausted. This selects `H-NextClassComplete`. See
  [M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md](M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md).
- **3636 — attachedMeshOverlayNpcHandler rs_free of 0x1C($s0):** `$s0` is
  `$s2=0x4($s1)` on opcode 2. The only heap-pointer writer of `0x1C`/`0x20`
  is `dispatchOverlaySetupByParentAssetName` `rs_malloc(0x80, 0)` at
  `0x80053DBC` (two-iter `+0x4` walk). Unmatched parent name stores type
  `-1` and skips that loop; NULL parent mesh skips setup. Opcode 2 still
  frees both words with no NULL store. Sibling `freeListEntryPointers` is
  unreferenced. Nine player-craft `spawnNpcOfType` sites. This selects
  `H-NextClassGap`. See
  [M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md](M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md).
- **3584 — retail source-buffer writer:** all three watches and the target
  phase fired; source-buffer writes were mixed, with 176 phase hits at
  `0x800078EC` and no stable distinct constructor/DMA PC. The
  earlier-constructor boundary is unavailable to this oracle; exact DMA
  ordering remains open. See
  [M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md](M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md).
- **3577–3583 — source/input and retail writer/producer:** retail controls
  fired. Target-phase source span was written by `0x800078EC` at 47.4 s
  before the first 512-wide target VI at 48.5 s. The joined tuple is
  `0x800052C4 -> 0x800078E0 -> 0x800078EC` with changing buffer/length
  values and nonzero post-store words, unlike the port's
  `0x801797B0/0/0x298` zero-fill. No independent DMA event identifier was
  exposed. See [M5-S3579-RETAIL-SOURCE-WRITER.md](M5-S3579-RETAIL-SOURCE-WRITER.md),
  [M5-S3581-RETAIL-SOURCE-PRODUCER.md](M5-S3581-RETAIL-SOURCE-PRODUCER.md),
  [M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md](M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md),
  [M5-S3583-RETAIL-PRODUCER-REPEAT.md](M5-S3583-RETAIL-PRODUCER-REPEAT.md).
- **3571–3576 — source/input boundary:** port zero-fill from `0x800078EC`
  preceded a zero first target DMA; retail independently reached
  `0x800078E0` with varied lengths, not the port tuple. Sessions 3573–3575
  were unevaluable for parity/order (caller watch not retained).
- **3563–3570 — source/output chain:** target image-stage and source-range
  DMAs completed, but payloads were zero; the immediate observed writer was
  a legitimate zero-valued DMA/writeback. No missing dispatch or completion
  was established.
- **3532–3535 — AI-frequency contract:** retail and port shared input
  `0x5622`; retail's correct NTSC rounding returned/stored `0x561F`, and the
  host path was corrected and validated. This boundary is closed.

New soak verdicts read at maintenance time added no post-3577 result; the
tail contained older queued outcomes only.

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. The image task is the real-audio
arm; the silent arm returns `RspExitReason::Broke`. Do not infer audio behavior
from a route that fails to reach the target phase.

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

The runtime facts that remain operationally important are: Factor 5 custom
opcodes are documented in `docs/factor5-gbi.md`; MusyX task data cannot be sent
to stock `aspMain`; DP messages use the external-message drain; C++ exceptions
must propagate to the outer recovery boundary; and RT64's interpreter safety
limit prevents a missing DL terminator from becoming an access violation.

## Superseded conclusions

The s3579–s3584 inference of a retail-versus-port stored-value divergence at
`0x800078EC` is unsupported. The retail ROM instruction is `sb $a1, 0($v0)`
(`0xA0450000` at ROM offset `0x84EC`), but the oracle read the entire aligned
word. A byte zero-fill legitimately leaves nonzero neighboring bytes until
later stores clear them. The new scalar-store samples distinguish this case.

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield/viewer-stall chain describes only the old diagnostic
arm; completion-aware default behavior returns from the attract viewer. The
old interpretation of the cinematic pool as an audio-slot pool was superseded
by the MusyX voice-table measurement.

The claim that `0x8002BEEC` is the retail JAL dispatch to `0x800078EC` is
route-dependent and unreconciled. Later adjacent-PC captures found zero at
both addresses while `0x800078EC` was live; do not treat it as a writer without
a new independent discriminator.

Sessions 3512 and 3516 selected non-observable predecessor watches. Their
positive stores/controls remain useful, but the absent predecessor rows are
capture-invalid and do not establish parity, divergence, or mutation.

The s3585 description of `voice_record+0x64` as a standalone slot index is
superseded by s3586's writer audit: the field is a packed handle; only its low
byte indexes the voice table. The writer list still found no concrete invalid
low byte, so the runtime allocator/lifetime boundary remains open.

## Evidence index

Latest boundary notes. Remaining M3 `rs_free` notes for s3586–s3657 stay on
disk and are indexed in PROJECT-OVERVIEW §56; do not treat absence here as
deletion.

- [M3-S3658-TEARDOWN-ASSET-MANIFEST-SERVICE-RS-FREE-AUDIT.md](M3-S3658-TEARDOWN-ASSET-MANIFEST-SERVICE-RS-FREE-AUDIT.md)
- [M3-S3657-FREE-MANIFEST-SEGMENT-ASSETS-RS-FREE-AUDIT.md](M3-S3657-FREE-MANIFEST-SEGMENT-ASSETS-RS-FREE-AUDIT.md)
- [M3-S3656-FIND-MANIFEST-ENTRY-BY-NAME-RS-FREE-AUDIT.md](M3-S3656-FIND-MANIFEST-ENTRY-BY-NAME-RS-FREE-AUDIT.md)
- [M3-S3655-PROCESS-ASSET-LOAD-STEP-RS-FREE-AUDIT.md](M3-S3655-PROCESS-ASSET-LOAD-STEP-RS-FREE-AUDIT.md)
- [M3-S3654-UNREGISTER-SERVICE-WORKER-RS-FREE-AUDIT.md](M3-S3654-UNREGISTER-SERVICE-WORKER-RS-FREE-AUDIT.md)
- [M3-S3653-INIT-SAVEDATA-RS-FREE-AUDIT.md](M3-S3653-INIT-SAVEDATA-RS-FREE-AUDIT.md)
- [M3-S3652-FREE-RENDER-SUBSYSTEM-RESOURCES-RS-FREE-AUDIT.md](M3-S3652-FREE-RENDER-SUBSYSTEM-RESOURCES-RS-FREE-AUDIT.md)
- [M3-S3651-UPLOAD-TEXTURE-DESCRIPTOR-DATA-RS-FREE-AUDIT.md](M3-S3651-UPLOAD-TEXTURE-DESCRIPTOR-DATA-RS-FREE-AUDIT.md)
- [M3-S3650-DESTROY-TEXTURE-LUTS-RS-FREE-AUDIT.md](M3-S3650-DESTROY-TEXTURE-LUTS-RS-FREE-AUDIT.md)
- [M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md](M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md)
- [M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md](M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md)
- [M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md](M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md)
- [M5-S3678-TASK-GENERATION-JOIN.md](M5-S3678-TASK-GENERATION-JOIN.md)
- [M5-S3680-PUBLICATION-ROUTE-JOIN.md](M5-S3680-PUBLICATION-ROUTE-JOIN.md)
- [M5-S3660-AUDIO-SOURCE-OWNERSHIP.md](M5-S3660-AUDIO-SOURCE-OWNERSHIP.md)
- [M5-S3668-PRESELECTOR-WRITER-JOIN.md](M5-S3668-PRESELECTOR-WRITER-JOIN.md)
- [M5-S3671-DMA-ORDER.md](M5-S3671-DMA-ORDER.md)
- [M5-S3583-RETAIL-PRODUCER-REPEAT.md](M5-S3583-RETAIL-PRODUCER-REPEAT.md)
- [M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md](M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md)
- [M5-S3581-RETAIL-SOURCE-PRODUCER.md](M5-S3581-RETAIL-SOURCE-PRODUCER.md)
- [M5-S3579-RETAIL-SOURCE-WRITER.md](M5-S3579-RETAIL-SOURCE-WRITER.md)
- [M5-S3577-RETAIL-ZERO-FILL-REMAINING-EDGE.md](M5-S3577-RETAIL-ZERO-FILL-REMAINING-EDGE.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3658 remain in the append-only ledger; archived boundary detail is
in `PROJECT-OVERVIEW.md` and the notes above. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
