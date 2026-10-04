# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4013 (2026-10-04).

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) with real-audio/LLE/spin-yield/autopilot controls.
Hangar geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` selects
the silent `Broke` control; real audio is not production-complete.

The current M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are zero (`FNV=0x762B22A5`). Retail's shutdown
snapshot may retain 12 nonzero bytes, but its phase-gated hangar snapshot is
408 bytes with nonzero=0. The port descriptor `0x1798B0 -> DMEM 0xCB0` is
written by legitimate zero-valued `0x800078EC` fill activity. Sequence 664 at
physical `0x179A44` was the final observed writer; matching input DMAs had
zero payload. No nonzero hangar producer is established.

Session 3949 converted big-endian N64 PCM bytes to native `int16_t` in the SDL
callback while preserving guest address, sample count, and SDL byte length.
Session 3977 changed audio DMEM staging to the OSTask-declared
`ucode_data_size` (`0x800`) and retained the old `0xF80` copy behind
`ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1`. Session 3978 selected H3: the declared-size
arm crashed in `spTaskSchedulerThread` at `last-guest-pc=0x8000834c` before
title, while the legacy arm reached title and hangar with 5,263 task rows.
The declared-size arm was parked for diagnosis until s3994 qualified its
real-audio ABI and target phases; legacy remains the steadier census route.

The generated scalar-store census, central host/RSP writer census, native
page-fault census, and nine bounded exact-offset load candidates are closed at
their measured scopes. A null attribution is not global writer absence.

Session 3993 reran the prescribed three-arm capture from the checked-in
recipe. That attempt did not qualify the consumer discriminator because
declared/real crashed before its audio ABI row; the RSP canary and phase
controls fired, so the missing ABI row was an arm failure, not consumer
absence. Session 3994's rerun qualified all three arms: declared/real reached
3,421 real-audio ABI rows and both target phases, declared/silent reached 3,444
stub ABI rows and both phases, and legacy/real reached 3,419 real-audio ABI
rows and both phases. Declared/real and legacy/real had matching phase-5
consumer signatures (zero payload, `FNV=0xF59C39C5`; 2,205 versus 2,246
complete source/consumer joins), and no declared-only post-`0x800` marker.
The task-contract consumer boundary is closed at this measured scope; the
remaining zero payload is upstream of this consumer.

Session 3995 extended the qualified legacy/real writer census to candidate PCs
`0x80005228`, `0x8000522C`, and `0x80005230`. The retail oracle positive
control fired and both title VI 1024 and hangar VI 512 controls fired; the
oracle completed. All three candidates had `seen=0`, zero post-target samples,
and zero post-target rows. The paired port reached phase 5 with 2,904 image-DMA
joins and 2,913 audio ABI rows, with no crash or abort. H2 is selected for this
class; the result does not establish global writer absence.

Session 3996 landed the next bounded M3 ownership guard in
`patches/heap_guards.c`: after validating the active queue, the patch now
rejects an alias between the remaining free-list chain and the active queue's
terminal node before link mutation. The ordinary Debug target built
successfully. The configured `PatchesLib` target remains unavailable (`No
rule to make target PatchesLib`), so MIPS/runtime qualification is still
blocked; this is a source-level guard change, not an explanation of the
underlying corruption.

Session 3997 extended the qualified legacy/real M5 census to candidate PCs
`0x80005234`, `0x80005238`, and `0x8000523C`. The retail oracle's whole-RDRAM
positive control fired, title VI 1024 fired 154 times, hangar VI 512 fired 188
times, and the oracle completed. Each candidate had `seen=0`, zero post-target
samples/rows, and zero sequence hits. The paired port reached phase 5 with
2,853 audio ABI rows and 2,844 image-DMA joins, with no crash or abort. This
selects H2 for the measured candidate class; it does not establish global
writer absence.

Session 3998 extended the qualified legacy/real M5 census to candidate PCs
`0x80005240`, `0x80005244`, and `0x80005248`. The retail oracle's positive
control threshold fired, title VI 1024 fired 154 times, hangar VI 512 fired
158 times, and the oracle completed. No candidate, post-target, scalar-store,
or sequence evidence was emitted for any of the three PCs. The paired port
reached phase 5 with 3,046 audio ABI rows and 3,033 image-DMA joins, with no
crash or abort. This selects H2 for the measured candidate class; it does not
establish global writer absence.

Session 3999 extended the qualified legacy/real M5 census to candidate PCs
`0x8000524C`, `0x80005250`, and `0x80005254`. The retail oracle's whole-RDRAM
positive control fired, title VI 1024 and hangar VI 512 both fired, and the
oracle completed. No candidate PC hit was emitted in the target phases. The
paired port reached both target phases with 643 phase-5 audio-task rows and
647 image-DMA joins, with no crash or abort. This selects H2 for the measured
candidate class; it does not establish global writer absence.

Session 4000 extended the qualified legacy/real M5 census to candidate PCs
`0x80005258`, `0x8000525C`, and `0x80005260`. The retail oracle's whole-RDRAM
positive control fired, title VI 1024 fired 154 times, hangar VI 512 fired 187
times, and the oracle completed. Each candidate had `seen=0`, zero post-target
samples/rows/sequences, and no scalar evidence. The paired port reached phase 5
with 2,853 audio-task rows and 2,846 image-DMA joins, with no crash or abort.
This selects H2 for the measured candidate class; it does not establish global
writer absence.

Session 4001 extended the qualified legacy/real M5 census to candidate PCs
`0x80005264`, `0x80005268`, and `0x8000526C`. The retail oracle's whole-RDRAM
positive control fired; title VI 1024 and hangar VI 512 fired 154 and 152
times, and the oracle completed. Each candidate had `seen=0`, zero
post-target samples/rows/sequences, and no scalar evidence. The paired port
reached phase 5 with 3,056 audio-task rows and 3,047 image-DMA joins, with no
crash or abort. This selects H2 for the measured candidate class; it does not
establish global writer absence.

Session 4003 added the next regeneration-safe M3 guard in
`patches/heap_guards.c`: when the published active-queue head is empty, the
tail used by the append must have both `prev` and `next` null before link
publication. ORIGIN is the active-queue append writer; a predecessor on this
empty path is not legitimate ownership state. The ordinary Debug target built
successfully, but `PatchesLib` remains unavailable (`No rule to make target
PatchesLib`), so this is source/host-build evidence only and not runtime
qualification.

Session 4004 re-qualified the legacy/real M5 route after the s4002 arm failure.
The retail oracle's whole-RDRAM positive control, title VI 1024, and hangar VI
512 controls fired; the oracle completed. The paired port reached both target
phases with 3,024 audio-ABI rows and 3,007 image-DMA joins, with no crash or
abort. Candidates `0x80005270`, `0x80005274`, and `0x80005278` had zero
post-target samples, rows, and sequence hits. This is a qualified H2/null for
that candidate class, so the adjacent census can continue.

Session 4005 extended the qualified legacy/real M5 census to
`0x8000527C`, `0x80005280`, and `0x80005284`. The retail whole-RDRAM positive
control, title VI 1024, and hangar VI 512 controls fired; the oracle completed.
The paired port reached both target phases with 3,014 audio-ABI rows and 3,009
image-DMA joins without crash or abort. Each candidate had zero post-target
samples, rows, and sequence hits, selecting H2 for this class.

Session 4006 extended the qualified legacy/real M5 census to
`0x80005288`, `0x8000528C`, and `0x80005290`. The retail whole-RDRAM positive
control, title VI 1024, and hangar VI 512 controls fired; the oracle completed.
The paired port reached both target phases with 2,895 audio-ABI rows and 2,882
image-DMA joins without crash or abort. Each candidate had zero post-target
samples, rows, and sequence hits, selecting H2 for this class.

Session 4007 attempted `0x80005294`, `0x80005298`, and `0x8000529C`. Retail
controls and oracle completion passed, but the paired port emitted no title or
hangar phase control and no audio/image census rows before watchdog
termination. With no crash or abort marker, this is a route failure and the
candidate class is unevaluable, not a qualified null.

Session 4008 re-qualified the legacy/real route once as required. Retail again
passed its whole-RDRAM, title VI 1024, hangar VI 512, and completion controls,
but the paired port crashed in `spTaskSchedulerThread` at guest PC
`0x8000834C` after the RSP source-hook control and before either target phase;
it emitted zero audio/image census rows. This is the second consecutive
pre-target route failure after s4007, so the candidate census is parked and
the route requires a discriminator before another candidate sweep.

Session 4009's initial scheduler capture had a run-lifetime budget defect and
was not used as evidence. The corrected same-build capture in session 4010
passed retail whole-RDRAM, title VI 1024, and hangar VI 512 controls. The
declared/real arm reached both target phases with 3,591 audio-ABI rows and
26,847 phase-scoped scheduler rows. The legacy/real arm fired the same RSP
source-hook control, emitted only two pre-target scheduler rows with
`staging=0xF80`, then crashed at `spTaskSchedulerThread+9632` / guest
`0x8000834C` before any target phase or audio-ABI row. No successor variation
was observed. This selects H1 for the route-level split: the legacy-only
staging path is the differentiator; H2's successor-change prediction and H3's
nondeterministic-arm prediction are unsupported in this capture. Scheduler
`a0` remains a message object, not an OSTask pointer; ABI rows are authoritative
for task fields. ORIGIN: the table observes scheduler context only; it adds no
skip, guard, restore, or other mitigation.

Session 4011 corrected the parked candidate recipe to run retail, declared/real,
and legacy/real concurrently. Retail's whole-RDRAM positive control, title VI
1024 (154), hangar VI 512 (188), and oracle completion all passed. Candidate PCs
`0x80005294`, `0x80005298`, and `0x8000529C` each had zero post-target samples,
rows, and sequence hits. Declared/real reached both target phases with 3,966
audio-ABI rows and 3,944 image-DMA joins; legacy/real reached both with 3,775
audio-ABI rows and 3,758 joins, with no crash or abort. This selects H2 for the
class and closes the adjacent candidate census; the prior single-arm capture
was recipe-invalid for discrimination because it never included the declared
control. ORIGIN: diagnostic census only; no mitigation landed.

Session 4012 added a regeneration-safe hook immediately before the audio
ucode-data DMA and ran it with the existing scheduler successor table. Retail's
whole-RDRAM positive control and title/hangar VI controls passed. Both port arms
reached both target phases without crash or abort; the writer control fired in
each arm and showed the same task (`ucode_data=0x800A4E00`, declared `0x800`)
using `dma_size=0x800` in declared/real and `dma_size=0xF80` in legacy/real.
The scheduler table also showed arm-dependent task-field ordering, but its
opaque `successor` field remained zero in this capture. Since the legacy crash
did not recur under this concurrent schedule, H1/H2/H3 are not selected by the
crash discriminator. The writer mechanism is established in the port, while
the failure remains schedule-sensitive or otherwise unevaluated. ORIGIN: the
hook observes the legitimate runtime-selected DMA writer; it adds no skip,
guard, restore, or other mitigation.

Session 4013 repeated the concurrent retail/declared/legacy table with
`ROGUESQ_SPIN_YIELD=0` in both port arms. Retail's whole-RDRAM positive control
and title/hangar VI controls passed. Both arms fired the RSP source-hook and
writer controls; declared/real used `dma_size=0x800`, while legacy/real used
`dma_size=0xF80` for `ucode_data=0x800A4E00` with declared size `0x800`.
Declared/real stalled in the 640-wide pre-target route, while legacy/real
reached title VI 1024 and emitted phase-4 rows. Neither arm emitted a crash or
abort, and observed scheduler successor values remained zero. This is an
arm-dependent route result, not a clean selection of the legacy-staging crash
hypothesis: the declared arm never reached the target-phase comparison. The
writer remains established; no mitigation was added. ORIGIN: diagnostic writer
and scheduler boundary only.

## Next steps

Work only the first applicable item. The backlog is monotonic; repeated
candidate results are summarized by address range rather than copied here.

1. **M5 legacy-only scheduler follow-up.** The candidate census is now
   qualified through `0x8000529C`, and s4012 established the actual `0xF80`
   writer. s4013 with spin-yield disabled made declared/real stall in the
   640-wide pre-target route while legacy/real reached title, so the intended
   crash split was unevaluable. Re-run the same concurrent table with the
   established default `ROGUESQ_SPIN_YIELD=1` in both port arms, preserving the
   writer and opaque successor rows. Declared reaching both target phases again
   while legacy crashes after an `0xF80` writer selects the staging path;
   matching writer/successor rows with both arms reaching target phases leaves
   schedule sensitivity open; a declared pre-target stall repeats the
   arm-dependent route failure. Keep scheduler `a0` as a message object; ABI
   rows remain authoritative.

2. **M5 candidate-writer census continuation.** Closed for the measured
   adjacent range through `0x8000529C`; resume only with a new writer class or
   a new ground-truth source.

3. **M3 heap guard validation.** The accumulated guards, including the new
   free-list/active-queue ownership-alias guard, in
   `patches/heap_guards.c` are not runtime-qualified because the configured
   build has no `PatchesLib` target and the MIPS toolchain is unavailable.
   Do not add another guard before the patch pipeline is supplied and built.

4. **Generated-symbol renaming sweep.** Parked while M5 has an applicable
   discriminator and M3 lacks a validation path. Keep hypothesis slug
   `generated-symbol-renaming-sweep`; mapping edits do not reset the
   engineering-change stall gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| `H-M5-ProducerAbsent` | Selected for measured pre-input classes; only legitimate zero-fill writer observed. |
| `H-M5-ClearIsExpected` | Selected: `0x8008F2CC` clears object `0x801797B0`, length `0x298`. |
| `H-M5-RetailWriterPortEdgeAbsent` | Selected at measured target phases; no qualified retail target-buffer edge. |
| `H-M5-FamilyDisconnectedOutput` | Selected at the s3835 scope; retail lacks access to the watched alternate-object span while port emits family stores. |
| `H-M5-TargetPhaseAudioDmaAbsent` | Selected at s3829; no target-phase `rs64_m5_audio_source_dma`. |
| `H-M5-TaskOutputFieldsEmptySeparateWriteback` | Selected at s3840 port scope. |
| `H-M5-RetailTaskStageRole` | Selected at s3846; exact task-generation-to-destination join remains open. |
| `H-M5-RetailDestinationAbsentTargetPhase` | Selected at s3855 for `0x1798B0..0x179A48`; lifetime writers are outside target buckets. |
| `H-M5-800078ECZeroFill` | Selected at s3857; sampled writes are zero-valued. |
| `H-M5-CandidateWriterClass` | Bounded classes through `0x80005218` selected H2 or H3 as recorded in the append-only ledger; never global absence. |
| `H-M5-CandidateWriterClass-0521C` | Selected H2 at s3990: all three PCs absent from qualified retail target/post-target/scalar evidence while the paired legacy port qualified. |
| `H-M3-HeapSpanGuard` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-FreeListReciprocalLinks` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-ActiveQueueReachability` | Code landed in s3914; validation blocked by absent MIPS toolchain and configured patch target. |
| `H-M3-ActiveQueueOwnershipAlias` | Code landed in s3928; host target passed, patch/runtime validation remains blocked. |
| `H-M5-Step1-PreTitleRoute` | Selected H1 at s3973: image/LLE-on reached VI 512, image/LLE-off stopped at VI 1024, silent/LLE-on crashed at `0x8000834c`. |
| `H-M5-Step1-TaskContract` | H3 at s3991: declared arm crashed in the first graphics-task scheduler path at `0x8000834c` before any audio ABI row; legacy arm passed controls and reached both target phases. |
| `H-M5-Step1-TaskContract-3992` | Superseded by s3994: s3993 again failed to qualify declared/real, but s3994's same-build three-arm capture qualified it. |
| `H-M5-Step1-TaskContract-3994` | H2 selected at the measured scope: declared/real and legacy/real reached the ABI and target phases with matching zero-payload phase-5 consumer signatures; no declared-only post-`0x800` marker appeared. |
| `H-M5-CandidateWriterClass-0528` | H2 selected at s3995: retail controls and oracle completion passed, while `0x80005228`, `0x8000522C`, and `0x80005230` had no candidate or post-target evidence; paired port reached phase 5. |
| `H-M5-CandidateWriterClass-0534` | H2 selected at s3997: retail controls and oracle completion passed, while `0x80005234`, `0x80005238`, and `0x8000523C` had no candidate, post-target, or sequence evidence; paired port reached phase 5. |
| `H-M5-CandidateWriterClass-0540` | H2 selected at s3998: retail controls and oracle completion passed, while `0x80005240`, `0x80005244`, and `0x80005248` had no candidate, post-target, scalar-store, or sequence evidence; paired port reached phase 5. |
| `H-M5-CandidateWriterClass-054C` | H2 selected at s3999: retail positive, title, and hangar controls passed with oracle completion; no candidate PC hit appeared for `0x8000524C`, `0x80005250`, or `0x80005254`; paired port reached phase 5 with 643 audio-task rows and 647 image-DMA joins. |
| `H-M5-CandidateWriterClass-0558` | H2 selected at s4000: retail positive, title, and hangar controls passed with oracle completion; no candidate PC hit appeared for `0x80005258`, `0x8000525C`, or `0x80005260`; paired port reached phase 5 with 2,853 audio-task rows and 2,846 image-DMA joins. |
| `H-M5-CandidateWriterClass-0564` | H2 selected at s4001: retail positive, title, and hangar controls passed with oracle completion; no candidate/post-target/scalar/sequence evidence appeared for `0x80005264`, `0x80005268`, or `0x8000526C`; paired port reached phase 5 with 3,056 audio-task rows and 3,047 image-DMA joins. |
| `H-M5-CandidateWriterClass-0570` | H3 at s4002: retail positive, title, and hangar controls passed and all three candidates were absent, but the paired legacy/real port crashed at `0x8000834c` before target-phase controls or census rows. |
| `H-M5-CandidateWriterClass-0570-qualified` | H2 selected at s4004: the paired legacy/real port reached both target phases with positive controls, while `0x80005270`, `0x80005274`, and `0x80005278` had no post-target samples, rows, or sequence hits. |
| `H-M5-CandidateWriterClass-057C` | H2 selected at s4005: retail and paired-port controls passed, while `0x8000527C`, `0x80005280`, and `0x80005284` had no post-target samples, rows, or sequence hits. |
| `H-M5-CandidateWriterClass-0588` | H2 selected at s4006: retail and paired-port controls passed, while `0x80005288`, `0x8000528C`, and `0x80005290` had no post-target samples, rows, or sequence hits. |
| `H-M5-CandidateWriterClass-0594` | H3 selected at s4007: retail controls passed, but the paired port emitted no target phases or census rows, so `0x80005294`, `0x80005298`, and `0x8000529C` are unevaluable. |
| `H-M5-LegacyRealRoute-4008` | H3 selected: after s4007's pre-target failure, the legacy/real rerun again failed before title/hangar, this time crashing at guest PC `0x8000834C` with zero census rows; route-level task-scheduler discrimination is required. |
| `H-M5-LegacyRealRoute-4009` | Superseded by s4010: the first capture established only a legacy-only route split and was overinterpreted as H2 before the corrected staging-specific table result. |
| `H-M5-LegacyRealRoute-4010` | H1 selected at route level: declared/real reached both target phases, while legacy/real emitted two pre-target task-load rows with `staging=0xF80` and crashed at `0x8000834C` before any audio-ABI row; no successor variation appeared. |
| `H-M5-CandidateWriterClass-0594-qualified` | H2 selected at s4011: retail controls and oracle completion passed; all three candidate PCs were absent from qualified post-target evidence; both declared/real and legacy/real reached title/hangar with audio/image joins and no crash/abort. |
| `H-M3-FreeActiveOwnershipAlias` | Guard landed at s3996: a valid acyclic free-list and active queue must not share a terminal node; runtime qualification is blocked by the unavailable PatchesLib target. |
| `H-M3-EmptyActiveQueueTail` | Guard landed at s4003: an empty published active queue must have a null tail predecessor and successor; host build passed, while patch/runtime qualification is blocked by the unavailable PatchesLib target. |

## Durable evidence boundary

- Retail reaches title/hangar and relevant writer PCs; the paired port reaches
  image-DMA joins without crash/abort when the arm completes.
- Retail writes the candidate image-stage span during target phases, but the
  measured writer classes produce no qualified post-target scalar payload.
- Port task `0x80171E70`, size 1, joins the exact input DMA at matching
  generations; payloads are zero. Separate writeback joins are real.
- The repaired clear witness is `0x8008F2CC`, object `0x801797B0`, length
  `0x298`.
- The s3891 image arm proves the RSP task and two output-DMA edges execute;
  zero payload does not identify the missing upstream writer.
- Session 3973's route comparison reached VI 512 only with image/LLE-on;
  image/LLE-off stopped at VI 1024 and silent/LLE-on crashed at
  `last-guest-pc=0x8000834c`.
- Session 3990's bounded candidate census selected H2 for `0x8000521C`,
  `0x80005220`, and `0x80005224`: retail controls passed, each candidate had
  zero target/post-target/scalar evidence, and the legacy port reached both
  phases with 3,000 image-DMA joins and 3,004 task rows without crash/abort.
- Session 3998's bounded candidate census selected H2 for `0x80005240`,
  `0x80005244`, and `0x80005248`: retail positive, title, and hangar
  controls passed with oracle completion; no candidate/post-target/scalar/
  sequence evidence appeared; and the paired legacy port reached phase 5 with
  3,046 audio ABI rows and 3,033 image-DMA joins without crash/abort.
- Session 3999's bounded candidate census selected H2 for `0x8000524C`,
  `0x80005250`, and `0x80005254`: retail positive, title, and hangar
  controls passed with oracle completion; no candidate PC hit appeared; and
  the paired legacy port reached phase 5 with 643 audio-task rows and 647
  image-DMA joins without crash/abort.
- Session 4000's bounded candidate census selected H2 for `0x80005258`,
  `0x8000525C`, and `0x80005260`: retail positive, title, and hangar controls
  passed with oracle completion; no candidate/post-target/scalar/sequence
  evidence appeared; and the paired legacy port reached phase 5 with 2,853
  audio-task rows and 2,846 image-DMA joins without crash/abort.
- Session 4001's bounded candidate census selected H2 for `0x80005264`,
  `0x80005268`, and `0x8000526C`: retail positive, title, and hangar
  controls passed with oracle completion; no candidate/post-target/scalar/
  sequence evidence appeared; and the paired legacy port reached phase 5 with
  3,056 audio-task rows and 3,047 image-DMA joins without crash/abort.
- Session 4002's retail arm passed the whole-RDRAM positive control and title/
  hangar controls (154 each); candidates `0x80005270`, `0x80005274`, and
  `0x80005278` had no hits or post-target rows. The paired legacy/real port
  crashed in `spTaskSchedulerThread` at guest PC `0x8000834c` before its title
  or hangar controls and emitted zero audio/image census rows, so this class is
  unevaluable rather than H2-selected.
- Session 4004 re-qualified the legacy/real route: retail positive, title, and
  hangar controls passed; the port produced 3,024 audio-ABI rows and 3,007
  image-DMA joins without crash/abort; and `0x80005270`, `0x80005274`, and
  `0x80005278` had zero post-target samples, rows, and sequence hits. This
  selects H2 for the class and permits the next adjacent set.
- Session 4005's bounded candidate census selected H2 for `0x8000527C`,
  `0x80005280`, and `0x80005284`: retail positive, title, and hangar controls
  passed with oracle completion; no candidate post-target samples, rows, or
  sequence hits appeared; and the paired legacy port reached both target
  phases with 3,014 audio-ABI rows and 3,009 image-DMA joins without
  crash/abort.
- Session 4006's bounded candidate census selected H2 for `0x80005288`,
  `0x8000528C`, and `0x80005290`: retail positive, title, and hangar controls
  passed with oracle completion; no candidate post-target samples, rows, or
  sequence hits appeared; and the paired legacy port reached both target
  phases with 2,895 audio-ABI rows and 2,882 image-DMA joins without
  crash/abort.
- Session 4007's bounded candidate census was not qualified: retail controls
  passed, but the paired port produced no target phases or census rows before
  watchdog termination. The three candidates are unevaluable.
- Session 3991's declared-size task-staging arm emitted the RSP boot canary
  control, then crashed in `spTaskSchedulerThread` at guest PC `0x8000834c`
  before any audio-task ABI/consumer row. In the same script, the legacy arm
  emitted the task controls, reached title VI 1024 and hangar VI 512, and
  produced 4,741 audio ABI rows; therefore the declared-size audio contract
  remains unevaluable, not selected.
- Session 3992's single-build three-arm capture passed positive controls in all
  arms. Declared/real produced 3,447 audio ABI rows, declared/silent 3,460,
  and legacy/real 3,428; each reached title VI 1024 and hangar VI 512. The
  silent arm's first ABI row was `musyx_stub` with `dmem_changed=0` and
  `canary_ok=1`; both real arms entered the real audio path with
  `ucode_data_size=0x800`, `break_pc=0x1328`, and `canary_ok=0`. No
  declared-only post-`0x800` read/consumer marker appeared, so the task
  contract is still unresolved.
- Session 3993's rerun passed the RSP canary and phase controls, but
  declared/real crashed in `spTaskSchedulerThread` before an audio ABI row;
  declared/silent reached the silent ABI and title VI 1024, while legacy/real
  reached title VI 1024 and hangar VI 512 with audio rows. This run is not a
  consumer discriminator and must not be read as declared-only read absence.
- Session 3994's rerun passed the RSP canary and both phase controls in all
  three arms. Declared/real produced 3,421 real-audio ABI rows, declared/silent
  3,444 stub rows with unchanged DMEM, and legacy/real 3,419 real-audio rows.
  In phase 5, declared/real and legacy/real both observed the zero-payload
  consumer signature `FNV=0xF59C39C5`, `nz=0`; complete source/consumer joins
  were 2,205 and 2,246 respectively. No declared-only post-`0x800` marker was
  emitted. This closes the task-contract consumer discriminator at this
  scope, while leaving the upstream zero-payload writer unresolved.

Session 4008's retail arm passed all positive controls and completed, while
the legacy/real port hit the RSP source-hook control then crashed in
`spTaskSchedulerThread` at guest PC `0x8000834C` before title/hangar and
emitted zero census rows. This confirms the route is not qualified for
another candidate null; the candidate sweep is parked.

Session 4010's corrected phase-scoped table passed retail controls and the
declared/real control, while legacy/real emitted two pre-target task-load rows
with `staging=0xF80` and crashed at `0x8000834C` before any audio-ABI row. No
successor variation appeared. This selects H1 for the measured legacy route
split and permits the candidate census to resume only with route qualification
reported separately.

Sessions 1–3927 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`; never read it whole.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The initial s4009 interpretation that selected H2 from a legacy-only crash is
superseded by s4010: it showed the route split but had not separated staging
from successor state. The corrected table found the legacy `0xF80` staging row
before the crash and no successor change.

The s3579–s3584 `0x800078EC` stored-value inference is unsupported because
retail executed a byte store while the oracle read an aligned word containing
neighboring bytes. Request-only SP-yield conclusions are limited to the old
diagnostic arm. The old cinematic-pool/audio-slot interpretation was
superseded by the MusyX voice-table measurement.

## Durable operating rules

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and similar defenses are safety mechanisms, not explanations.
Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. MusyX task data cannot be sent to
stock `aspMain`; the silent arm returns `Broke`. Never infer audio behavior
from a route that fails to reach the target phase.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget, and two evidence lines before its result becomes truth.
Phase-gate animated comparisons on VI transitions. Batch A/B arms in one
build/run. A counter proving a branch ran is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

## Evidence index

See [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md),
[M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md), and
[M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md).
Detailed counts and session-specific notes remain in `PORTING-STATE.md`.
