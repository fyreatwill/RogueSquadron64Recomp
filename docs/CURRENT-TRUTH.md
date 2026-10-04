# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3989 (2026-10-04). This maintenance pass condensed the
operational ledger below; the append-only ledger retains the deleted detail.

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
The declared-size arm remains parked; the legacy rollback is the qualified
route for census work.

The generated scalar-store census, central host/RSP writer census, native
page-fault census, and nine bounded exact-offset load candidates are closed at
their measured scopes. A null attribution is not global writer absence.

## Next steps

Work only the first applicable item. The backlog is monotonic; repeated
candidate results are summarized by address range rather than copied here.

1. **M5 candidate-writer qualification — `0x8000521C`, `0x80005220`,
   `0x80005224`.** Run the existing same-build retail/port census with
   `ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1` on the port. Require whole-RDRAM,
   title-1024, hangar-512, oracle-completion, image-DMA, task-contract, and
   paired payload controls. H1 is a qualified candidate execution plus a
   post-store/scalar sample; H2 is clean retail absence with qualified port;
   H3 is any missing control or legacy-arm failure. Do not infer a global
   producer result.

2. **M5 audio task-contract redesign.** Explain why declared-size staging
   crashes at `0x8000834c`; name the writer/consumer requiring bytes beyond
   `0x800` before changing the qualified route. Do not treat legacy success as
   proof that the over-copy is legitimate.

3. **M3 heap guard validation.** The accumulated guards in
   `patches/heap_guards.c` are not runtime-qualified because the configured
   build has no `PatchesLib` target and the MIPS toolchain is unavailable.
   Do not add another guard before the patch pipeline is supplied and built.

4. **M5 candidate-writer census continuation.** Resume the next unclassified
   adjacent set only after item 1 closes. All prior sets through
   `0x80005218` selected bounded H2; this is not global writer absence.

5. **Generated-symbol renaming sweep.** Parked while M5 has an applicable
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
| `H-M3-HeapSpanGuard` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-FreeListReciprocalLinks` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-ActiveQueueReachability` | Code landed in s3914; validation blocked by absent MIPS toolchain and configured patch target. |
| `H-M3-ActiveQueueOwnershipAlias` | Code landed in s3928; host target passed, patch/runtime validation remains blocked. |
| `H-M5-Step1-PreTitleRoute` | Selected H1 at s3973: image/LLE-on reached VI 512, image/LLE-off stopped at VI 1024, silent/LLE-on crashed at `0x8000834c`. |

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
