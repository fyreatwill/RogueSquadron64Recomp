# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory
and the incremental de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3847 (2026-10-03).

## Current state

The validated native route boots through attribution, N64 logo, intro cinematic,
star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) using real-audio/LLE/spin-yield/autopilot controls. Hangar
geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` selects the silent
`Broke` control; real audio is not production-complete.

The active M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are both zero (`FNV=0x762B22A5`). Retail's
shutdown snapshot can retain 12 nonzero bytes, but its phase-gated hangar
snapshot is 408 bytes, nonzero=0. The port descriptor `0x1798B0 -> DMEM 0xCB0`
is finally written by legitimate zero-valued `0x800078EC` fill activity.
Session 3818 joined the active generated scalar-store census: sequence 664 at
physical `0x179A44` is the final observed writer, and every matching input DMA
had zero payload. No nonzero hangar producer is established.

The generated scalar-store census, central host/RSP writer census, native
page-fault census, and nine bounded exact-offset load candidates are closed at
their measured scopes. Do not infer a zero producer from a null attribution;
target fault attribution was absent or an arm crashed before target.

The qualified S/L family writes alternate objects and I has no hangar edge. A
paired retail/port target capture found zero retail reads or writes in physical
`0x165000..0x16C000` while retail still executed S/L family PCs. The repaired
clear witness identifies `0x8008F2CC`, object `0x801797B0`, length `0x298`.

## Next steps

Work only the first applicable item. This is one monotonic backlog.

1. **M3 heap block-span guard validation — open dependency.** Session 3841
   changed full-block checks in `patches/heap_guards.c` from base-only
   `kseg0_ok` to `block_ok`, requiring a complete `0x100`-byte object below
   `0x80800000`. ORIGIN: `func_8002221C` and free-list link stores publish
   block bases; the guard rejects only an impossible boundary-crossing object.
   Session 3842 could not validate it: CMake has no `PatchesLib` target, the
   configured MIPS compiler is absent, and `build/Debug/N64Recomp.exe` is
   absent. Restore/reconfigure those tools, build the patch ELF and library,
   then run the allocator-route smoke. Do not claim H1/H2 before that.
2. **M5 retail task-to-stage join — open exact discriminator.** Session 3847
   narrowed the target to `0x167000..0x169B00` and found stable phase-scoped
   retail writers `0x80015BC8` and `0x8000F3A0`, with 1,155 task rows and no
   crash. This selects a real phase-correlated writer set, but the oracle
   capture still does not expose an individual task generation's destination
   and length. Watch both writer PCs with their live arguments and join their
   rows to the target task sequence; do not infer exact ownership from the
   phase histogram alone.
3. **M5 image task/output edge — qualified port result.** Session 3839 joined
   the named port input contract to `0x1798B0 -> DMEM 0xCB0`; session 3840
   found 452/458 matching separate writeback-DMA joins to `0x1798B0`, length
   `0x198`, despite empty ABI output fields. Do not add a writeback guard or
   infer a destination from the port address; qualify retail first.
4. **M5 target-phase parity — closed at current scope.** s3820/s3823/s3844
   supplied independent retail and validated port target coverage and exact
   hangar zero-payload parity. Do not repeat standalone qualification or the
   retail zero-writer census unless the route/build changes.
5. **Generated-symbol renaming sweep — parked.** Resume only after M5 has no
   applicable discriminator and M3 has a toolchain or a new discriminator.
   Keep HYPOTHESIS-ID `generated-symbol-renaming-sweep`; do not use mapping
   edits to evade the engineering-change stall gate.

## Live hypothesis table

| Hypothesis | Status |
|---|---|
| `H-M5-ProducerAbsent` | Selected for measured pre-input producer classes; only legitimate zero-fill writer observed. |
| `H-M5-ClearIsExpected` | Selected: `0x8008F2CC` clears the source object before the image edge. |
| `H-M5-RetailWriterPortEdgeAbsent` | Selected at measured target phases; retail writer families have no qualified target-buffer edge. |
| `H-M5-RetailWriterFamilyOtherObject` | Selected for S/L; stores target alternate objects. |
| `H-M5-RetailWriterFamilyAbsentTargetEdge` | Selected for I; no hangar-phase family edge. |
| `H-M5-FamilyDisconnectedOutput` | Selected at s3835 scope: retail has no access to the watched alternate-object span while port emits family stores. |
| `H-M5-TargetPhaseAudioDmaAbsent` | Selected at s3829: no `rs64_m5_audio_source_dma` invocation during target phases, despite lifetime controls. |
| `H-M5-FamilyAfterImageStage` | Selected at s3832–s3834: joined family work follows image stage/route context and has no PCM source/consumer match. |
| `H-M5-TaskOutputFieldsEmptySeparateWriteback` | Selected at s3840 port scope. |
| `H-M5-RetailTaskOutputFieldParity` | Selected at s3844 for empty fields; s3846 selects shared destination role at bounded scope, exact task join remains open. |
| `H-M5-RetailTaskStageRole` | Selected at s3846: retail task and candidate image-stage region are both active in hangar with independent phase/whole-RDRAM controls. |
| `H-M3-HeapSpanGuard` | Code landed; validation blocked by absent MIPS toolchain/configured targets. |

## Evidence ledger — recent durable boundary

- **3835:** Rice retail reached title/hangar and S/L PCs, but had zero
  reads/writes in physical `0x165000..0x16C000`; port emitted 1,280 family
  stores. Alternate output is disconnected at this scope.
- **3839:** Port task `0x80171E70`, size 1, joined the exact input DMA at matching
  generations; all payloads were zero. Matching image-DMA joins refute a missing
  downstream edge.
- **3840:** Qualified retry found empty port ABI output fields and 452/458
  separate writeback joins. First attempt crashed before target and was rejected.
- **3841–3842:** Heap block-span guard was implemented with an explicit ORIGIN;
  build validation is blocked by missing MIPS compiler, N64Recomp executable,
  and `PatchesLib` target. The single refuting experiment is a reconfigured
  patch build followed by allocator-route smoke.
- **3844:** Fixed paired retail/port capture reached both target VIs on both
  arms with positive controls and no crash/abort. Retail had 516 hangar task
  rows; port had 3,342 named rows, 11,582 stage rows, and 2,870 image-DMA
  joins. All qualified ABI output fields were zero; retail source was
  `0x80173CB0`, so destination-role equivalence remains open.
- **3846:** Paired capture passed whole-RDRAM and both target-VI controls with
  no crash/abort. Retail had 1,144 hangar type-2 task rows and writes in both
  `0x173CB0..0x173DB0` (120,550) and candidate image-stage
  `0x167000..0x16C000` (930,770). Port had 2,964 image-DMA joins. This
  selects shared destination role, but the broad retail watch does not yet
  join an individual task generation to an exact stage destination.
- **3847:** Paired capture passed whole-RDRAM, title/hangar VI controls, and
  no-crash validation. The exact target range had title writer PCs
  `0x80015BC8`/`0x8000F3A0` at 86,146/117 stores and hangar counts
  12,706/38,214; retail produced 627 title and 528 hangar type-2 task rows.
  This confirms phase-correlated writer activity but leaves the per-task
  destination/length join unresolved.

Earlier s3730–s3838 evidence is preserved in the append-only ledger and linked
session notes. Do not repeat a boundary whose discriminator is closed.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The s3579–s3584 retail-versus-port stored-value inference at `0x800078EC` is
unsupported because retail executed a byte store while the oracle read an
aligned word containing neighboring bytes. Request-only SP-yield conclusions
are limited to the old diagnostic arm. The old cinematic-pool/audio-slot
interpretation was superseded by the MusyX voice-table measurement.

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

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
run `./submodule-patches/export.sh` and commit refreshed patches. Never run
submodule update, checkout, clean, or hard reset commands. Kill runs with
SIGKILL and run from `build/`. A mitigation-shaped change needs an `ORIGIN:`
line naming the writer and stating whether its value is legitimate.

## Evidence index

See the session-specific notes and:

- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)
- [M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md)
- [M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md)
- [M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md)

Sessions 1–3844 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
