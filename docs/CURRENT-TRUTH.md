# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
documents are listed below. Updated for session 3520 (2026-08-31).

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

Session 3515 independently requalified the retail route: whole-RDRAM control
fired, retail reached title and the 512 hangar, and `musyxMixActiveVoices`
entry `0x80090E04` fired in the hangar. Session 3518's same-build port pair
reached title and hangar on real audio, while the silent arm crashed pre-title
at guest PC `0x8000B650` in the `fillSampleStreamRange` family. This selects a
route-specific silent-arm failure and reopens target-phase port measurements;
it does not establish the writer of the crash input.

Session 3519 independently qualified the internal callsite boundary. Retail
and the real-audio port agree on `a0=0x80165ED0` and `a1=0x12` entering the
selector path, while the later store context still differs (`s1=0x561F` retail
versus `0x5622` port). Retail identifies `0x80029E78` as the next internal
call before the differing value is observed, selecting a later mixer-path
mutation rather than an upstream producer divergence. The writer or return
contract at that internal boundary remains open.

Session 3520 qualified the next boundary with an independent retail execution
watch and a same-build port hook. Retail executed `0x80029E78` in hangar with
`a0=0x5622`, `a1=0x8A0`, `a2=0x10`, `s1=0x80165ED0`, and `v0=0x561F`. The
port's corresponding native `osAiSetFrequency_recomp` hook passed its startup
positive control but had zero hangar rows, while the downstream selector
stores and their controls remained live. This selects an execution-path
difference at the AI boundary, but not yet its caller or equivalence.

Session 3516 qualified the selector-store boundary independently: retail
whole-RDRAM and selector-span controls fired, with five executions at each of
`0x8008F228` and `0x8008F264` in hangar. The port context hook at those same
stores reached hangar and captured `s0=0x12`, `s1=0x5622`, and values
`0x80171E70`/`0x80173CB0`; the oracle field-dump mode emitted no comparable
register rows. The earlier `0x8009192C` candidate was absent and is not a
valid predecessor on this route, so parity/divergence remains unresolved.

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

1. Identify the port callsites entering `osAiSetFrequency_recomp` and compare
   them with the retail caller context for `0x80029E78`, retaining whole-RDRAM,
   selector-span, and hangar selector-store controls. Distinguish a missing
   port call from a caller/route mismatch; do not rewrite the value.
2. Keep the silent-arm `fillSampleStreamRange` crash as a separate route
   defect. Do not infer target-phase behavior from the silent arm or treat it
   as evidence that the real-audio mixer boundary is broken.
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

The active work unit is now the caller/route boundary for the retail
`0x80029E78` execution on the real-audio route. The silent-arm route defect is
parked separately.

For the silent-arm route:

- `H-SilentRouteCrash`: the silent route has a route-specific failure in the
  `fillSampleStreamRange` family while real audio reaches the target phase.
- `H-SharedRouteBlocker`: both arms stop before title, selecting a shared
  blocker.
- `H-RealAudioRouteFailure`: real audio fails before the target phase.
- `H-CaptureInvalid`: startup, oracle, or phase controls fail.

Session 3518 selected `H-SilentRouteCrash`: oracle controls passed, the silent
arm crashed pre-title at `0x8000B650`, and the real image arm reached title and
hangar. The crash origin remains unresolved.

For the next producer boundary:

- `H-ContextProducerParity`: predecessor context matches; an earlier
  initializer or later mutation remains.
- `H-ContextProducerDivergence`: predecessor supplies different `s1` or related
  context; that producer edge is selected.
- `H-LaterContextMutation`: predecessor matches, but an intervening guest
  instruction mutates context before the writer.
- `H-CaptureInvalid`: a same-run positive control or phase-matched writer
  control fails; the join is unevaluable.

Session 3519 selected `H-ContextProducerParity` at the callsite and
`H-LaterContextMutation` for the first observed value difference: retail and
port agree on the call inputs, but retail's internal call returns/feeds
`0x561F` while the port store context remains `0x5622`. The next discriminator
is the phase-matched context at `0x80029E78` and the following store. A differing
call input selects that function's producer; matching input with differing
output/store selects its internal contract or a subsequent mutation; failed
controls make the capture invalid.

Session 3520 selected `H-PortBoundaryAbsentInHangar`: the retail watch fired in
hangar, the port hook's startup positive control fired, and the port hook had
zero hangar rows while downstream stores remained live. This is a path result,
not a proof that the host primitive is the exact instruction equivalence.

The next discriminating measurement is one independent retail caller-context
capture and one qualified port capture that labels every port callsite into the
native AI primitive. A matching caller with no target-phase port entry selects
a missing/route-gated call; a target-phase entry with differing arguments
selects caller context; failed controls make the capture invalid.
Matching predecessor fields with a later writer difference selects a mutation;
the first differing predecessor field selects its producer; failed controls
 select capture invalidity only.

Session 3514 adds a retail-qualified mixer-entry candidate at `0x80090E04`,
but the port did not reach its target phase on either tested arm. See
[M5-S3514-MIX-ENTRY-BOUNDARY.md](M5-S3514-MIX-ENTRY-BOUNDARY.md).

Session 3515 independently requalified that retail entry in the hangar with a
positive control; see [M5-S3515-ORACLE-ROUTE.md](M5-S3515-ORACLE-ROUTE.md).

Session 3518 requalified the real-audio port route and isolated a silent-arm
pre-title crash; see [M5-S3518-AUDIO-ROUTE-PAIR.md](M5-S3518-AUDIO-ROUTE-PAIR.md).

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

Session 3516's `0x8009192C` zero is likewise a capture-invalid predecessor
measurement, not evidence about selector parity or divergence. The corrected
live-store watches were positive, and the port store context was observed, but
the oracle did not provide a matching register tuple.

## Evidence index

Latest selector boundary:

- [M5-S3514-MIX-ENTRY-BOUNDARY.md](M5-S3514-MIX-ENTRY-BOUNDARY.md)
- [M5-S3519-SELECTOR-CALLSITE-CONTEXT.md](M5-S3519-SELECTOR-CALLSITE-CONTEXT.md)
- [M5-S3520-SELECTOR-AI-BOUNDARY.md](M5-S3520-SELECTOR-AI-BOUNDARY.md)
- [M5-S3516-SELECTOR-STORE-CONTEXT.md](M5-S3516-SELECTOR-STORE-CONTEXT.md)
- [M5-S3517-SELECTOR-PRODUCER-CONTEXT.md](M5-S3517-SELECTOR-PRODUCER-CONTEXT.md)
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

Sessions 1–3519 remain in the append-only ledger; archived background and
closed boundary detail remain in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
Use bounded `grep`/`sed` windows for `PORTING-STATE.md`, never read it whole.
The soak queue is consumed by automation; fold only new tail lines into the
next audit.
