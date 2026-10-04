# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3908 (2026-10-03).

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) with real-audio/LLE/spin-yield/autopilot controls.
Hangar geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` selects
the silent `Broke` control; real audio is not production-complete.

The active M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are zero (`FNV=0x762B22A5`). Retail's shutdown
snapshot can retain 12 nonzero bytes, but its phase-gated hangar snapshot is
408 bytes, nonzero=0. The port descriptor `0x1798B0 -> DMEM 0xCB0` is written
by legitimate zero-valued `0x800078EC` fill activity. Session 3818 found that
sequence 664 at physical `0x179A44` is the final observed writer and every
matching input DMA had zero payload. No nonzero hangar producer is established.

The generated scalar-store census, central host/RSP writer census, native
page-fault census, and nine bounded exact-offset load candidates are closed at
their measured scopes. Do not infer a zero producer from null attribution;
target fault attribution was absent or an arm crashed before target.

## Next steps

Work only the first applicable item. This is one monotonic backlog.

1. **M3 heap guard validation — open external dependency, not a loop stop.**
   Session 3907 extended `patches/heap_guards.c`'s reciprocal-link audit from
   the free-list head pair to the complete bounded chain, rejecting cycles and
   foreign successor/predecessor links before dequeue. The change preserves
   valid chains but remains unvalidated because this checkout lacks
   `mips64-elf-gcc`/`mips64-elf-ld`; the local Apple clang rejects the MIPS
   flags. Session 3899 confirmed CMake skips the patch pipeline because this checkout
   lacks `mips64-elf-gcc`/`mips64-elf-ld`; session 3900 also found no local
   alternate MIPS backend or toolchain. A local N64Recomp binary exists, but it
   cannot produce `patches.elf`. The active-queue guard remains source-only;
   validate it when a human provides the toolchain, without adding another
   guard meanwhile.

2. **M5 audio contract qualification — remaining retail candidate-writer
   class.** Session 3900's phase-gated run passed the retail whole-RDRAM,
   title-1024, and hangar-512 controls; candidate PCs `0x80003B98`,
   `0x800044C8`, and `0x80004AB0` produced no retail rows. The paired port
   reached hangar with 3,026 image-DMA joins and no crash/abort. This closes
   that bounded class as H2 only. Session 3901's phase-gated run passed the retail whole-RDRAM,
   title-1024, and hangar-512 controls; all three PCs executed in phase but had
   zero post-target rows/samples. The paired port reached hangar with 2,836
   image-DMA joins and no crash/abort. This closes that bounded class as H2 only;
   session 3902 repeated the same discriminator for `0x80004D68`,
   `0x80004D74`, and `0x80004D78`: each executed in the qualified title phase,
   but each had zero post-target rows/samples. Retail whole-RDRAM reached
   33,193,803 writes, both target VI gates and oracle completion; the paired port
   reached hangar with 2,835 image-DMA joins and no crash/abort. This closes
   that bounded class as H2 only. Continue with `0x80004D7C`, `0x80004D84`,
   `0x80004E74`: all executed, only `0x80004E74` had a target-span phase row,
   and all had zero post-target rows/samples. Retail controls again passed;
   the paired port produced phase-5 image-DMA joins with zero payload and no
   crash/abort. This closes that bounded class as H2 only. Continue with
   `0x80004E8C`, `0x80004E90`, and `0x80004E94` all executed in the
   qualified target phase but had zero post-target rows/samples. The retail
   controls passed; the paired port reached hangar with 2,831 image-DMA joins,
   no crash/abort, and zero-valued qualified image payload. This closes that
   bounded class as H2 only. Continue with the next adjacent unclassified
   candidates; do not infer global writer absence. Session 3905 tested
   `0x80004F30`, `0x80004F34`, and `0x80004F38`: each executed during the
   qualified target phase, but all had zero post-target rows and scalar
   samples. Retail controls passed; the paired port reached hangar with
   2,800 image-DMA joins, no crash/abort, and zero-valued qualified image
   payload. This closes that bounded class as H2 only.
   Session 3906 tested `0x80004F3C`, `0x80004F44`, and `0x80004F48`: all
   executed during the qualified target phase, but each had zero post-target
   rows and scalar samples. Retail controls passed; the paired port reached
   hangar with 2,850 image-DMA joins and no crash/abort, with qualified image
   payload `FNV=0x762B22A5`, nonzero=0. This closes that bounded class as H2
   only. Continue with the next adjacent unclassified candidates.
   Session 3908 tested `0x80004F4C`, `0x80004F50`, and `0x80004F54`: all
   three executed during the qualified target phase, but each had zero
   post-target rows and scalar samples. Retail whole-RDRAM, title-1024, and
   hangar-512 controls passed; the paired port reached hangar with 2,856
   image-DMA joins and no crash/abort, with qualified image payload
   `FNV=0x762B22A5`, nonzero=0. This closes that bounded class as H2 only;
   continue with the next adjacent unclassified candidates.
   Session 3891's same-build silent/image pair passed independent
   retail whole-RDRAM, title-1024, and hangar-512 controls. Both arms reached
   hangar; the image arm changed DMEM, reached break `0x1328`, and issued two
   DMEM-to-RDRAM DMAs, but both payloads and PCM source/consumer joins were
   zero. This selects H-ContractGap over H-AudioDegeneracy at this scope.
   Do not add a writeback guard from this result.

3. **M5 image task/output edge — classify remaining retail writers.** The
   qualified port input and separate writeback-DMA edge are real, while the
   dominant retail `0x800078EC` activity is zero-fill, not an image producer.
   Sessions 3861–3896 classified many measured PCs as H2 (candidate-span
   writer rows but no post-value scalar attribution) or H3 (no candidate-span
   rows), always with positive controls and no global absence claim. The next
   bounded representatives are
   `0x80004D68`, `0x80004D74`, and `0x80004D78`. Continue only after the M3
   validation checkpoint, unless M3 remains unavailable and this is the
   selected runnable discriminator.

4. **M3 prior guard classes.** Metadata-slot, block-span, alias, active-head,
   and the expanded reciprocal-link guards are landed in
   `patches/heap_guards.c` but have no runtime result. The same
   missing-toolchain/build-target blocker applies; do not add another guard
   before validation.

5. **M5 target-phase parity is closed at current scope.** Do not repeat
   standalone qualification, paired target-VI controls, or the retail
   zero-writer census unless the route or build changes.

6. **Generated-symbol renaming sweep is parked.** Resume only after M5 has no
   applicable discriminator and M3 has a toolchain or a new discriminator.
   Keep HYPOTHESIS-ID `generated-symbol-renaming-sweep`; mapping edits do not
   evade the engineering-change stall gate.

## Live hypothesis table

| Hypothesis | Status |
|---|---|
| `H-M5-ProducerAbsent` | Selected for measured pre-input classes; only legitimate zero-fill writer observed. |
| `H-M5-ClearIsExpected` | Selected: `0x8008F2CC` clears object `0x801797B0`, length `0x298`. |
| `H-M5-RetailWriterPortEdgeAbsent` | Selected at measured target phases; no qualified retail target-buffer edge. |
| `H-M5-FamilyDisconnectedOutput` | Selected at s3835 scope; retail lacks access to the watched alternate-object span while port emits family stores. |
| `H-M5-TargetPhaseAudioDmaAbsent` | Selected at s3829; no target-phase `rs64_m5_audio_source_dma`. |
| `H-M5-TaskOutputFieldsEmptySeparateWriteback` | Selected at s3840 port scope. |
| `H-M5-RetailTaskStageRole` | Selected at s3846; exact task-generation-to-destination join remains open. |
| `H-M5-RetailDestinationAbsentTargetPhase` | Selected at s3855 for `0x1798B0..0x179A48`; lifetime writers are outside target buckets. |
| `H-M5-800078ECZeroFill` | Selected at s3857; sampled writes are zero-valued. |
| `H-M5-CandidateWriterClass` | Selected H2 for the bounded s3900–s3904 and s3908 candidate sets through `0x80004F54`; this is not global writer absence. |
| `H-M3-HeapSpanGuard` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-FreeListReciprocalLinks` | Code landed; validation blocked by absent tools/configured target. |

The many bounded candidate-PC results are intentionally summarized here:
each selected H2/H3 only for its named PC set, never as a global producer
absence. The full evidence and exact counts remain in the append-only ledger.

## Durable evidence boundary

- Retail reaches title/hangar and relevant writer PCs, while the paired port
  reaches image-DMA joins without crash/abort when the arm completes.
- Retail writes the candidate image-stage span during target phases, but the
  measured writer classes produce no qualified post-target scalar payload.
- Port task `0x80171E70`, size 1, joins the exact input DMA at matching
  generations; payloads are zero. Separate writeback joins are real.
- The repaired clear witness is `0x8008F2CC`, object `0x801797B0`, length
  `0x298`.
- The s3891 image arm proves the RSP task and two output-DMA edges execute;
  their zero payload does not identify the missing upstream writer.

Sessions 1–3897 remain in the append-only ledger. Use bounded `grep`/`sed`
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
