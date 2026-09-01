# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
documents are listed below. Updated for session 3514 (2026-08-31).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-image/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. Audio is not production-complete:
the Factor 5 image task is the qualified real-audio arm and
`ROGUESQ_AUDIO_UCODE=0`/`Broke` is the silent control.

The default route returns from the attract viewer and enters the cinematic
loop, but the stage advancer sees null `0x800B0934`; the initializer at
`0x800A62B4` is skipped while port skip-allow is zero. Retail independently
sets that byte and reaches title. Do not force the flag or bypass the state
machine.

M5 remains the active engineering thread. The status-03 worker/clear contract,
task ABI, completion/delivery, callback table, field348 input-to-clear edge,
send/receive zero-message boundary, first consumer boundary, source-table
selection, and corrected selector-table store/value boundary are closed at
their qualified scopes. The live gap is the producer/context contract before
the selector stores at `0x8008F228` and `0x8008F264`:

- Retail and port agree on hangar writer PCs and stored values
  (`0x80171E70`/`0x80173CB0`), but writer `s1` differs (`0x561F` vs `0x5622`).
- Session 3512's guessed retail predecessor watches were absent despite live
  stores, so that proposed join is invalid; do not repeat those addresses.
- The next useful boundary must be a genuinely new producer/context witness,
  qualified by the same independent retail controls and the port's title and
  hangar phase buckets.
- The generated host wrapper's `ra=0` remains unresolved, but prior joins rule
  out wrapper/ABI clobber at the qualified `rs_free` and source boundaries.

M5 source/output evidence establishes that retail writes legitimate nonzero
source/state values where the port previously wrote zero or selected an
`0x80110xxx` state family. The port table-selection witness later matched the
retail table family; the remaining selector writer-input context is therefore
the active discriminator. No audio state, selector, task field, or output is
to be rewritten as a diagnostic mitigation.

## Next steps

1. Trace a new producer/context boundary before `0x8008F228`/`0x8008F264`.
   Ask the independent retail oracle first, retaining its whole-RDRAM and
   selector-store positive controls. Add one regeneration-safe port witness at
   the same boundary, then run the validated real-image/LLE/spin-yield/
   autopilot route with title and hangar buckets. Join by hangar origin,
   writer PC, store ordinal, value, and predecessor-to-writer context.
2. Resolve or newly qualify the pre-title audio route before attempting the
   mixer-entry join: Session 3514's real-audio arm crashed in
   `fillSampleStreamRange` and its silent retry stopped before title. Do not
   treat zero mixer rows as evidence.
3. Keep the silent forced-LLE/no-spin result as a pre-title route-blocker
   baseline; do not repeat that arm unchanged.
4. Keep Sessions 3494–3498 real-audio route results, Session 3492 dispatch,
   Session 3488 silent qualification, and Sessions 3482–3486 producer/pointer
   captures as baselines; do not repeat unchanged captures.
5. Keep the controlled phase/PC/ordinal join rule: sequential animated-scene
   A/B rows are not evidence. A missing positive control makes a comparison
   unevaluable; matching fields close a boundary and the first divergent field
   selects the next producer edge.
6. M5 Step 3 remains gated until one output comparison names a missing
   image-task/output contract edge. `docs/M5-AUDIO-PLAN.md` is complete;
   configured-host PatchesLib validation is unavailable in this Unix checkout.
7. After M5 closes or a new discriminator is found, resume only systematic M3
   idiom-class audits. Keep retail-entry, hangar `0x8000` Y/accumulator, and
   SP-yield/MORT publication threads parked. Generated-symbol renaming remains
   last priority and closed at its measured scope.

### Active hypothesis table

For the next producer boundary:

- `H-ContextProducerParity`: predecessor context matches; an earlier
  initializer or later mutation remains.
- `H-ContextProducerDivergence`: predecessor supplies different `s1` or related
  context; that producer edge is selected.
- `H-LaterContextMutation`: predecessor matches, but an intervening guest
  instruction mutates context before the writer.
- `H-CaptureInvalid`: a same-run positive control or phase-matched writer
  control fails; the join is unevaluable.

The discriminating measurement is one independent retail capture and one
qualified port capture at the new boundary plus existing phase/store controls.
Matching predecessor fields with a later writer difference selects a mutation;
the first differing predecessor field selects its producer; failed controls
 select capture invalidity only.

Session 3514 adds a retail-qualified mixer-entry candidate at `0x80090E04`,
but the port did not reach its target phase on either tested arm. See
[M5-S3514-MIX-ENTRY-BOUNDARY.md](M5-S3514-MIX-ENTRY-BOUNDARY.md).

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and similar defenses are safety mechanisms, not explanations.
Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. The image task is the real-audio
arm; the silent arm returns `RspExitReason::Broke`. Do not infer audio behavior
from a route that fails to reach the target phase.

Every instrument needs a ground-truth request first, a same-run positive
control, a phase-scoped budget, and two independent evidence lines before its
result becomes current truth. Phase-gate animated comparisons on VI
transitions. Batch A/B arms in one build and run. A counter without a positive
control is worthless.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

The runtime's known architectural facts remain: Factor 5 custom opcodes are
documented in `docs/factor5-gbi.md`; MusyX task data cannot be sent to stock
`aspMain`; DP messages use the external-message drain; C++ exceptions must
propagate to the outer recovery boundary; and RT64's interpreter safety limit
prevents a missing DL terminator from becoming an access violation.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield/viewer-stall chain describes only the old diagnostic
arm; completion-aware default behavior returns from the attract viewer. The
old interpretation of the 1,578-entry cinematic pool as an audio-slot pool was
superseded by the MusyX voice-table measurement.

The earlier claim that `0x8002BEEC` was the retail JAL dispatch to `0x800078EC`
is route-dependent and unreconciled; later adjacent-PC captures found zero at
both addresses while `0x800078EC` was live. Do not treat it as a writer without
a new independent discriminator.

Session 3512's zero predecessor callbacks are not evidence for parity,
divergence, or later mutation. The stores and controls were live, but the
chosen predecessor addresses were not phase-observable; this invalidates that
measurement only, not the qualified writer-context divergence.

## Evidence index

Latest selector boundary:

- [M5-S3514-MIX-ENTRY-BOUNDARY.md](M5-S3514-MIX-ENTRY-BOUNDARY.md)
- [M5-S3512-SELECTOR-PREDECESSOR-BOUNDARY.md](M5-S3512-SELECTOR-PREDECESSOR-BOUNDARY.md)
- [M5-S3511-SELECTOR-TABLE-PHASE-JOIN.md](M5-S3511-SELECTOR-TABLE-PHASE-JOIN.md)
- [M5-S3510-SELECTOR-TABLE-PHASE-MISMATCH.md](M5-S3510-SELECTOR-TABLE-PHASE-MISMATCH.md)
- [M5-S3509-SELECTOR-TABLE-PORT-WRITER.md](M5-S3509-SELECTOR-TABLE-PORT-WRITER.md)
- [M5-S3508-SELECTOR-TABLE-WRITER.md](M5-S3508-SELECTOR-TABLE-WRITER.md)

Earlier active M5 boundaries:

- [M5-S3473-PORT-STATE-JOIN.md](M5-S3473-PORT-STATE-JOIN.md)
- [M5-S3463-SOURCE-VALUE-JOIN.md](M5-S3463-SOURCE-VALUE-JOIN.md)
- [M5-S3445-STATE-POINTER-ENTRY.md](M5-S3445-STATE-POINTER-ENTRY.md)
- [M5-S3444-STATE-POINTER-PRODUCER.md](M5-S3444-STATE-POINTER-PRODUCER.md)
- [M5-S3410-FIELD348-INPUT.md](M5-S3410-FIELD348-INPUT.md)
- [M5-S3376-ZERO-PCM-SOURCE.md](M5-S3376-ZERO-PCM-SOURCE.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3512 remain in the append-only ledger; archived background and
closed boundary detail remain in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
Use bounded `grep`/`sed` windows for `PORTING-STATE.md`, never read it whole.
The soak queue is consumed by automation; fold only new tail lines into the
next audit.
