# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3997 (2026-10-04).

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

## Next steps

Work only the first applicable item. The backlog is monotonic; repeated
candidate results are summarized by address range rather than copied here.

1. **M5 candidate-writer census continuation.** Resume the next unclassified
   adjacent set after `0x8000523C`, using one phase-scoped table and the
   qualified legacy/real route. The discriminator is whether any candidate
   writes nonzero target/post-target payload at a matching task ordinal; a
   same-run positive control must show the table firing.

2. **M3 heap guard validation.** The accumulated guards, including the new
   free-list/active-queue ownership-alias guard, in
   `patches/heap_guards.c` are not runtime-qualified because the configured
   build has no `PatchesLib` target and the MIPS toolchain is unavailable.
   Do not add another guard before the patch pipeline is supplied and built.

3. **Generated-symbol renaming sweep.** Parked while M5 has an applicable
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
| `H-M3-FreeActiveOwnershipAlias` | Guard landed at s3996: a valid acyclic free-list and active queue must not share a terminal node; runtime qualification is blocked by the unavailable PatchesLib target. |

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

Sessions 1–3927 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`; never read it whole.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

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
