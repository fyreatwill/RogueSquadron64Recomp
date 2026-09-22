# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background and closed M3 audits are in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
Updated for session 3701 (2026-09-21).

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
Retail's positive control reached hangar and showed 1,125 writes from the
known hangar writer families. The qualified port reached hangar with all
controls live; its first 512 source rows joined the expected DMA, but source
and post-DMA payloads remained zero and no current scalar writer was present.
This confirms `H-RetailSourceDifferent`; the next boundary is the producer or
layout that supplies the zero RDRAM source. See
[M5-S3701-SOURCE-PRODUCER-BOUNDARY.md](M5-S3701-SOURCE-PRODUCER-BOUNDARY.md).

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

1. **M5 Step 4 — identify the producer/layout of the zero RDRAM source.**
   `H-RetailSourceDifferent` is selected: the first 512 qualified hangar rows
   joined the correct `0x1798B0..0x179A48` source DMA, but its source bytes
   were zero and no current port writer matched retail's hangar families.
   Trace the source descriptor's producer and publication before the DMA,
   carrying the retail writer census, RSP, DMEM, and 512-row controls in one
   phase-gated run. A legitimate nonzero producer matching retail selects
   `H-PortSourceProducer`; no producer selects `H-ProducerOmission`; a
   divergent owner/range reopens `H-InputDescriptorWrong`.

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
| `H-PortSourceProducer` | Refuted at s3701 for the first 512 qualified rows: the port source DMA was correct but had zero payload and no current writer matching retail's hangar families. |
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
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3693 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
