# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
notes are linked below. Updated for session 3581 (2026-09-01).

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
tuples. This selects a retail-versus-port stored-value divergence at the
writer boundary; the earlier producer and exact DMA ordering remain open.
This is single-source oracle evidence.

Do not force the cinematic flag at `0x800B0934`, bypass the state machine, or
rewrite task, audio, PCM, selector, or output state. The default route's null
stage-advancer input is a known route/configuration issue; the validated
real-audio route is the comparison arm.

## Next steps

The backlog is one monotonic sequence. Work only the first applicable item.

1. M5 Step 3: independently qualify the nonzero retail source value and its
   producer/order. The oracle selects nonzero target-phase words and joins
   changing buffers and lengths through `0x800078EC`, but has no separate DMA
   event identifier. Use the source-span writer histogram plus phase-gated
   field table in `scratch/agent/NEXT.md`; keep DMA ordering open if no event
   is exposed.
2. Keep the s3554 slot-dispatch failure parked as route-specific absence.
   Revisit only with a new route discriminator; do not add a slot guard.
3. Keep the silent-arm `fillSampleStreamRange` crash separate from the
   real-audio target path, and do not infer target behavior from it.
4. After M5 closes or gains a new discriminator, perform only systematic M3
   idiom-class audits. Retail-entry, hangar `0x8000` Y/accumulator, and
   SP-yield/MORT publication threads remain parked.
5. Generated-symbol renaming remains last priority. Resume only when M5 is
   closed and M3 is parked with no new discriminator.

## Active hypothesis table

| Hypothesis | Discriminating result |
|---|---|
| H-RetailWriterSame | Selected for target-phase identity/order: `0x800078EC` writes at 47.4 s before target VI at 48.5 s. |
| H-RetailWriterOther | Refuted for the target-phase write; earlier setup writers are separate activity. |
| H-RetailOrdering | Exact DMA ordering remains unmeasured. |
| H-RetailValue | Nonzero target-phase words selected; parity against the port remains open. |
| H-RetailProducer | `0x800052C4` is the immediate caller of `0x800078E0`; the earlier constructor of the nonzero words remains unresolved. |
| H-RetailDmaOrder | No separate DMA event identifier was exposed; ordering remains open. |
| H-CaptureInvalid | Refuted for this run: whole-RDRAM, source-span, writer-PC, and target-phase controls all fired. |

The current work-unit slug is `m5-image-task-retail-source-writer`.

## Recent evidence ledger

Only the latest boundary transitions are repeated here; the append-only ledger
and evidence notes retain the full history.

- **3577 — remaining retail zero-fill edge:** retail controls fired and
  `0x800C825C` repeatedly reached `0x800078E0` with `a2=0x80` and changing
  structure pointers, unlike the port's `0x801797B0/0/0x298` tuple. Input
  divergence is selected; writer identity and ordering remain open.
- **3579 — retail source writer:** controls and target phase fired. The
  target-phase source span was written by `0x800078EC` at 47.4 s before the
  first 512-wide target VI at 48.5 s. Writer identity and pre-target order
  selected; ordinary watch rows did not report stored values, so value parity
  remains open. See [M5-S3579-RETAIL-SOURCE-WRITER.md](M5-S3579-RETAIL-SOURCE-WRITER.md).
- **3581 — retail source producer/value:** controls fired; the target
  transition joined `0x800052C4 -> 0x800078E0 -> 0x800078EC` with buffer/
  length tuples and nonzero post-store words. No independent DMA event was
  exposed, so producer construction and exact DMA order remain open. See
  [M5-S3581-RETAIL-SOURCE-PRODUCER.md](M5-S3581-RETAIL-SOURCE-PRODUCER.md).
- **3576 — retail predecessor input:** retail `0x800052C4` reached
  `0x800078E0` with varied lengths (`0x18`, `0x3C`, `0x208`, `0x4F0`,
  `0x1008`, `0x8000`), not the port tuple. This selected an observed-edge
  input divergence.
- **3573–3575 — entry contract:** port zero-fill arguments were qualified;
  the retail entry and controls were live, but the first caller watch was
  not retained. Those runs were unevaluable for parity/order, not evidence of
  absence.
- **3571–3572 — transition join:** port nonzero initialization preceded a
  zero-fill from `0x800078EC`, and the first target source DMA carried zero.
  Retail independently showed the writer family in the source span.
- **3563–3570 — source/output chain:** target image-stage and source-range
  DMAs completed, but payloads were zero; the immediate observed writer was a
  legitimate zero-valued DMA/writeback. No missing dispatch or completion was
  established.
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

## Evidence index

Latest boundary notes:

- [M5-S3577-RETAIL-ZERO-FILL-REMAINING-EDGE.md](M5-S3577-RETAIL-ZERO-FILL-REMAINING-EDGE.md)
- [M5-S3579-RETAIL-SOURCE-WRITER.md](M5-S3579-RETAIL-SOURCE-WRITER.md)
- [M5-S3576-RETAIL-ZERO-FILL-PREDECESSOR.md](M5-S3576-RETAIL-ZERO-FILL-PREDECESSOR.md)
- [M5-S3573-ZERO-FILL-CONTRACT.md](M5-S3573-ZERO-FILL-CONTRACT.md)
- [M5-S3572-SOURCE-TRANSITION-JOIN.md](M5-S3572-SOURCE-TRANSITION-JOIN.md)
- [M5-S3565-IMAGE-STAGING-SOURCE.md](M5-S3565-IMAGE-STAGING-SOURCE.md)
- [M5-S3566-SOURCE-RANGE-WRITER.md](M5-S3566-SOURCE-RANGE-WRITER.md)
- [M5-S3567-DMEM-PAYLOAD-PRODUCER.md](M5-S3567-DMEM-PAYLOAD-PRODUCER.md)
- [M5-S3564-IMAGE-DMEM-PRODUCER.md](M5-S3564-IMAGE-DMEM-PRODUCER.md)
- [M5-S3539-SOURCE-WRITER.md](M5-S3539-SOURCE-WRITER.md)
- [M5-S3536-OUTPUT-CONTRACT.md](M5-S3536-OUTPUT-CONTRACT.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3577 remain in the append-only ledger; archived boundary detail is
in `PROJECT-OVERVIEW.md` and the notes above. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
