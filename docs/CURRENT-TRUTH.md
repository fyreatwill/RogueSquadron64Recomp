# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
evidence documents are listed below. Updated for session 3543 (2026-09-01).

Session 3543 phase-qualified the source-range state immediately before and
after the two `rs_memset` clears. Title entered `0x178C80:0x178E00` already
zero; hangar entered `0x1797B0:0x179930` with 344 nonzero bytes and exited
zero. Retail independently passed the whole-RDRAM control, reached both
phases, and wrote both ranges. This selects a real pre-clear producer for the
hangar bytes while leaving its port writer identity open; title remains a
clear-before-producer case at this boundary. See
[M5-S3543-PRECLEAR-PRODUCER.md](M5-S3543-PRECLEAR-PRODUCER.md).

Session 3541 attributed the selected source-range zeroing on the corrected
real-audio port arm: the phase-qualified `0x178C80` RDRAM span received zero
byte writes from one port writer PC, `0x800078EC` (768 rows across the two
watched spans, with no candidate-store or memset rows). Retail independently
reached title and hangar, passed the whole-RDRAM control, and showed a
different multi-PC writer family plus a nonzero final source snapshot. This
selects `H-RdramWriterPort` and moves the boundary to the host/writeback
origin of the `0x800078EC` zero-fill path. See
[M5-S3541-SOURCE-RDRAM-WRITER.md](M5-S3541-SOURCE-RDRAM-WRITER.md).

Session 3542 identified that port writer as the generated `rs_memset` byte
loop at `0x800078EC`. Its phase-qualified entry arguments are
`dst=0x80178C80, fill=0, len=0x298` in title and
`dst=0x801797B0, fill=0, len=0x298` in hangar, matching the observed zero
stores. This selects `H-WritebackOrigin` and moves the boundary upstream to
the producer of the source range before the legitimate clear; see
[M5-S3542-WRITEBACK-ORIGIN.md](M5-S3542-WRITEBACK-ORIGIN.md).

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

Session 3521 labeled both generated port callsites into the native AI
primitive. Retail's independent execution watch reached hangar with caller
`0x80029E64`; the port reached the same hangar phase with producer/store
controls live, but neither labeled callsite nor the host AI-boundary witness
fired there. This selects a missing or route-gated port call at the qualified
scope, not a target-phase argument mismatch. The route gate and any other
caller remain open; see [M5-S3521-SELECTOR-CALLSITE-BOUNDARY.md](M5-S3521-SELECTOR-CALLSITE-BOUNDARY.md).

Session 3522 statically enumerated the generated tree: exactly two direct
`0x80029D20`/`osAiSetFrequency_recomp` references exist, in
`initAudioSubsystem` and `reapplyAudioConfig`, whose only generated callers
are `setDisplayMode` and `reapplyDisplayMode`. A new caller-entry witness was
built, but both port captures failed before title; the corrected run crashed
at `0x8000B650` in `fillSampleStreamRange`. The independent retail controls
remained valid and again observed one hangar execution of `0x80029E78` from
`0x80029E64`. This rules out an unenumerated direct generated caller at static
scope, but leaves the runtime route gate unevaluable until a real-audio port
run reaches hangar. See [M5-S3522-SELECTOR-ROUTE-CENSUS.md](M5-S3522-SELECTOR-ROUTE-CENSUS.md).

Session 3516 qualified the selector-store boundary independently: retail
whole-RDRAM and selector-span controls fired, with five executions at each of
`0x8008F228` and `0x8008F264` in hangar. The port context hook at those same
stores reached hangar and captured `s0=0x12`, `s1=0x5622`, and values
`0x80171E70`/`0x80173CB0`; the oracle field-dump mode emitted no comparable
register rows. The earlier `0x8009192C` candidate was absent and is not a
valid predecessor on this route, so parity/divergence remains unresolved.

Session 3523 re-qualified the real-audio port with corrected control names.
The run reached title 1024 and hangar 512; startup, title, hangar, producer,
producer-context, table, and selector-store controls were live. The known
`setDisplayMode`/`reapplyDisplayMode` route witness appeared only in title,
and neither known AI callsite nor AI-boundary row appeared in hangar, while
the two selector stores and their producer context did. This selects a
phase-gated route-path difference at the known caller scope, not a target
phase argument mismatch. It does not identify an alternate caller, which was
not instrumented in this unit.

Session 3524 independently qualified that route boundary with a phase-keyed
`runVideoFrameTick` caller/guard table. Retail again reached title and hangar
and executed `0x80029E78` in hangar. The port's positive control and title
rows were live, but no known direct caller or guard row appeared in hangar,
while producer-context, both selector stores, and mixer entry remained live.
All four generated direct callers were covered. This selects a route-path
difference at static caller scope: an enclosing route gate or a
non-generated/indirect alternate path reaches the stores. See
[M5-S3524-SELECTOR-TICK-ROUTE.md](M5-S3524-SELECTOR-TICK-ROUTE.md).

Session 3525 qualified the retail immediate-store range independently: the
whole-RDRAM control fired, retail reached title and hangar, the range executed
981 times, and `0x80029E78` fired twice in hangar from `0x80029E64`. The port
entry witness was present and its startup control fired, but the corrected
real-audio LLE/spin-yield/autopilot arm crashed before title at
`last-guest-pc=0x8000834C`; no title or hangar entry rows were available. This
selects `H-CaptureInvalid` for the port comparison and leaves alternate-entry
versus route-gate hypotheses open. See
[M5-S3525-SELECTOR-STORE-ENTRY.md](M5-S3525-SELECTOR-STORE-ENTRY.md).

Session 3526 requalified the corrected real-audio port route. Startup
controls fired; the port reached title 1024 and hangar 512. In hangar the
`allocateSongChannelArray` entry witness fired once with `a0=0x12`,
`a1=0x5622`, `a2=0`, `a3=1`; both selector-store contexts and the producer
context fired. The known caller, route, and AI-boundary rows were absent in
hangar. This validates execution of the target entry/path but does not
distinguish an alternate caller from an enclosing route gate because the
generated wrapper reports `ra=0`. See
[M5-S3526-SELECTOR-STORE-ENTRY-REQUALIFIED.md](M5-S3526-SELECTOR-STORE-ENTRY-REQUALIFIED.md).

Session 3527 completed the generated caller/route discriminator. The new
phase-keyed table covered the sole direct `allocateSongChannelArray` call at
`0x80091934` and both `initN64RspMixer` callers. Positive controls and title
1024/hangar 512 were live. In hangar, `reapplyAudioConfig` reached
`initN64RspMixer`, which reached the allocate edge with matching arguments
(`a0=0x12`, `a1=0x5622`, `a2=0`, `a3=1`); `initAudioSubsystem` had no hangar
row. This selects matching caller/route parity at the qualified generated
scope and moves the discriminator later inside the producer path. It is
single-source port evidence; see
[M5-S3527-SELECTOR-MIXER-CALLERS.md](M5-S3527-SELECTOR-MIXER-CALLERS.md).

Session 3528 qualified all three allocation edges inside
`allocateSongChannelArray` with a same-build real-audio port run and an
independent retail oracle. Effective allocation inputs and returned pointers
matched at `0x8008F0D0`, `0x8008F210`, and `0x8008F23C`; retail's `$s1=0x561F`
versus the port's `$s1=0x5622` is already an entry-argument difference, not an
allocator-return defect. This selects `H-AllocParity` and moves the active
boundary upstream to the producer of `allocateSongChannelArray`'s `a1`/`s1`.
See [M5-S3528-SELECTOR-ALLOC-BOUNDARY.md](M5-S3528-SELECTOR-ALLOC-BOUNDARY.md).

Session 3529 independently qualified the immediate mixer input. Retail's
whole-RDRAM control and PC watches observed `0x8009192C`/`0x80091934` with
loaded `a1=0x561F`; the same-build port's positive controls and title/hangar
phase buckets were live, but its load witness observed `a1=0x5622`. The port
then reached the existing allocator and selector-store controls. This selects
`H-InputLoadDivergence` and moves the boundary to the writer/source of
`MEM_W(0x80165ED0)`, not the call ABI or allocator. See
[M5-S3529-SELECTOR-INPUT-BOUNDARY.md](M5-S3529-SELECTOR-INPUT-BOUNDARY.md).

Session 3530 qualified the setup writer at `0x80091CC8`. Retail's independent
physical watch included that PC in the target phase, while the same-build
real-audio port witness fired at the store with value `0x5622` in title and
hangar; the following input load and downstream controls were live. This
selects the setup-writer/input divergence at the qualified scope and rules out
a load-only or allocator explanation. The retail writer watch did not capture
its value, so the numeric writer-value comparison is single-source. See
[M5-S3530-SELECTOR-SOURCE-WRITER.md](M5-S3530-SELECTOR-SOURCE-WRITER.md).

Session 3531 qualified the port-side setup source/return contract: the
phase-keyed witness reached title and hangar, preserved `a0=0x80165ED0` and
`a1=0x12` through the setup/mutex path, loaded AI input `0x5622`, and observed
AI return `v0=0x5622`; all downstream selector controls remained live. The
independent retail watch could not start because `libmupen64plus.dylib` is
absent in this checkout. This is single-source port evidence: it rules out an
internal port-side ABI/return clobber at the qualified path, but does not
select retail source/value parity versus divergence. See
[M5-S3531-SELECTOR-SETUP-CONTRACT.md](M5-S3531-SELECTOR-SETUP-CONTRACT.md).

Session 3532 independently qualified the retail side of that contract. The
oracle's whole-RDRAM control fired 48,922 times and the target 512 hangar phase
was reached. Retail supplied the same `a0=0x5622` at `0x80091CB8` seen on the
port, but returned/stored `v0=0x561F` at `0x80091CC4`/`0x80091CC8`, versus the
port's `v0=0x5622`. This selects a return-contract divergence after the shared
source argument and rules out a source-value, load-only, or allocator cause at
this boundary. See [M5-S3532-SELECTOR-SETUP-RETURN.md](M5-S3532-SELECTOR-SETUP-RETURN.md).

Session 3533 independently requalified the return split at the internal AI
frequency boundary. The oracle's whole-RDRAM control fired 10,000 times and
its hangar-phase watches saw `a0=0x5622` entering `0x80029D20` from
`0x80091CB8`, then `v0=0x561F` at `0x80091CC4`. The same-build real-audio port
reached title and hangar with its phase-keyed setup return row showing
`v0=0x5622`. This selects the internal callee/return contract and rules out
input-load, source-writer, and allocator divergence at this scope. A new
host-side return hook fired its startup positive control but no target-phase
row; that hook is not evidence. See
[M5-S3533-SELECTOR-AI-RETURN.md](M5-S3533-SELECTOR-AI-RETURN.md).

Session 3534 resolved the semantic contract statically from the complete
retail ELF body of `osAiSetFrequency` at `0x80029D20`. Retail rounds
`osViClock / frequency` to `dacRate`, programs the AI registers, and returns
`osViClock / dacRate`; with NTSC clock 48,681,812 and input `0x5622`, this is
`dacRate=2208` and return `0x561F`. The result exactly explains the
independent retail return. This selects `H-InternalReturnSemantics` and
refutes a later store/ABI mutation at the qualified boundary. See
[M5-S3534-AI-FREQUENCY-CONTRACT.md](M5-S3534-AI-FREQUENCY-CONTRACT.md).

Session 3535 validated the host correction in one same-build real-audio
LLE/spin-yield/autopilot run. Startup AI controls fired; title 1024 and hangar
512 were reached; phase-keyed setup rows showed input `0x5622` and return/store
`0x561F` in both target phases. This closes the AI-frequency contract edge and
preserves the qualified route. The next M5 discriminator is an output/task
comparison, not another AI-return probe. See
[M5-S3535-AI-FREQUENCY-VALIDATION.md](M5-S3535-AI-FREQUENCY-VALIDATION.md).

Session 3536 qualified the output/task contract with an independent retail
oracle and a same-build real-audio port run. Whole-RDRAM and both port phase
controls were live; retail reached title and hangar and observed the target
task/mixer PCs. The port image arm dispatched and completed tasks, performed
phase-keyed image-stage DMEM/DMA work, delivered SP completion, and produced
paired PCM source/consumer rows in both phases. Every sampled image-stage and
PCM payload was nevertheless zero (`fnv=0xF59C39C5`, `nz=0`) at both endpoints.
This selects `H-ContractGap` at the payload scope, not a missing dispatch or
completion edge. No writer/value was identified, so no output state may be
changed. See [M5-S3536-OUTPUT-CONTRACT.md](M5-S3536-OUTPUT-CONTRACT.md).

Session 3537 qualified the next output boundary with a batch oracle/port
capture. Retail passed whole-RDRAM and target-phase controls and produced
nonzero bytes in the PCM ring and image destinations. The port reached both
target phases and executed source DMA, image-stage, completion, PCM source,
and PCM consumer joins, but sampled payloads remained zero; its bounded
PCM-writer rows were DMA rows rather than a nonzero CPU writer. Retail
attribution at `0x1935E0` identified `0x800078EC` in title and
`0x80018F5C`/`0x80018F60` in hangar. This selects an output-writer/ordering
contract gap, not missing task dispatch or completion. The port-side writer
remains open; see [M5-S3537-OUTPUT-WRITER.md](M5-S3537-OUTPUT-WRITER.md).

Session 3538 completed the writer/order discriminator. Retail independently
passed the whole-RDRAM control, reached title and hangar, wrote nonzero PCM
bytes, and observed the target writer PCs. The same-build real-audio port
reached both target phases with live source, consumer, image-stage, and
completion controls. Its 1,024 phase-qualified output-writer rows were all
RSP DMA writes with zero source and destination payloads; there were no
guest/CPU writer rows, and the joins were stage-only with no ordering
violation. This selects `H-PortMissingWriter` at the nonzero payload-producer
edge and rules out a later zero overwrite or invalid capture. See
[M5-S3538-OUTPUT-WRITER.md](M5-S3538-OUTPUT-WRITER.md).

Session 3539 completed the source-writer census after extending coverage from
scalar to vector RSP DMEM stores. The first scalar-only capture was invalid
for this question despite live controls. The fixed real-audio port run
reached title and hangar, logged 2,048 bounded source-window vector-store
rows, and observed nonzero broad DMEM-span contents during the producer
sequence; later image-stage snapshots remained zero (`F59C39C5`, `nz=0`), as
did PCM output. Retail independently passed its whole-RDRAM control, reached
the target run, and wrote nonzero bytes in both watched source/state ranges.
This selects `H-PortSourceOverwritten` at the broad DMEM-span boundary and
rules out an absent RSP producer and scalar-only coverage. Exact per-window
ordering remains open; see [M5-S3539-SOURCE-WRITER.md](M5-S3539-SOURCE-WRITER.md).

Session 3540 completed the exact source-window ordering probe in the title
phase. Window 2 (`0x6F0..0x9F0`) became nonzero, then returned to the all-zero
hash before stage consumption; window 3 stayed zero. A post-copy DMA from RDRAM
`0x178C80` produced the zero state, followed by a later nonzero refill. This
selects `H-SourceWindowOverwritten` for the title-phase port path and moves the
active boundary to the writer of RDRAM `0x178C80`. The run did not reach 512
hangar, so this exact ordering is single-source title evidence; session 3539's
retail nonzero-writer result remains the independent second line. See
[M5-S3540-SOURCE-WINDOWS.md](M5-S3540-SOURCE-WINDOWS.md).

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

1. Identify the producer that populates the source range before the legitimate
   `rs_memset(dst=0x80178C80/0x801797B0, fill=0, len=0x298)` clear. Use one
   phase-qualified pre-clear snapshot/writer census with the existing positive
   control and downstream joins; do not change audio, PCM, or output state.
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
   image-task/output contract edge. The AI-frequency contract is now corrected;
   `docs/M5-AUDIO-PLAN.md` is complete;
   configured-host PatchesLib validation is unavailable in this Unix checkout.
7. After M5 closes or a new discriminator is found, resume only systematic M3
   idiom-class audits. Keep retail-entry, hangar `0x8000` Y/accumulator, and
   SP-yield/MORT publication threads parked. Generated-symbol renaming remains
   last priority and closed at its measured scope.

### Active hypothesis table

The active work unit is now the image-task output payload producer. Session
3538 selected `H-PortMissingWriter` at the observed destination scope:
retail's independent writer watches produced legitimate nonzero bytes, while
the port's phase-qualified DMA writer read and wrote zero payloads, with no
CPU/host writer and no later overwrite. The legitimate port-side source
writer is still unidentified, so no output state is to be rewritten. The
`0x80091CC8` internal return contract is closed by Sessions 3534–3535. The
silent-arm route defect is parked separately.

Session 3541 moved the live boundary to the port's zero-fill writer origin.
The corrected writer hook records zero-valued writes at `0x178C80` from one
port PC (`0x800078EC`), while retail independently records a distinct writer
family and a nonzero final range. The next discriminator is the source and
writeback contract behind that port PC. Session 3542 closed that identity:
the zero is a deliberate `rs_memset` clear of the source range, so the active
discriminator is now the pre-clear producer.

Session 3539 moves the live boundary upstream into the image-task DMEM source.
Vector stores execute in both source-window address classes and broad-span
contents become nonzero during that sequence, but the stage-2 source snapshot
is zero. The next discriminator is exact per-window ordering, not another
scalar-store census.

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

For the next upstream argument boundary:

- `H-AllocParity`: all three allocator edges match retail through their
  returns, so the divergence is upstream of the callee entry.
- `H-InputLoadDivergence`: session 3529 observed retail load `0x561F` versus
  port load `0x5622`, selecting the source/writer edge at `0x80165ED0`.
- `H-InputLoadParity`: the loaded value matches but differs before the call,
  selecting an intervening generated instruction or wrapper contract.
- `H-CaptureInvalid`: a same-run positive control or phase-matched writer
  control fails; the join is unevaluable.

Session 3530 selected `H-SetupWriterInputDivergence` at the qualified scope.
The next unit qualified the writer's source arguments/return contract rather
than repeating the same store census.

Session 3532 selected `H-SetupWriterReturnDivergence`: retail and port agree on
the `0x5622` AI-frequency input, but retail returns/stores `0x561F` while the
port returns/stores `0x5622`. The next boundary is the internal AI-frequency
callee/host return path.

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

Session 3521 selected `H-PortCallMissing`: both labeled generated calls had
startup controls but zero hangar rows, while retail's independent watch and the
port producer/store controls were live. The next discriminator is a route-gate
or alternate-caller census, not another repeat of these two callsites.

Session 3523 selected `H-RouteGate` at the qualified caller scope: the
real-audio port reached title and hangar with live producer/store controls,
but the known display-mode route witness and known AI callsite/boundary rows
were title-only or absent in hangar. This is a phase-gated path result, not a
proof that an alternate caller exists; the next discriminator is the enclosing
`runVideoFrameTick` branch/caller or a separately instrumented alternate path.

Session 3527 supersedes that route-gate interpretation at the generated
caller scope: the new hangar rows show a live `reapplyAudioConfig` route and
the sole direct allocate edge with matching arguments. The remaining open
question is the first producer/context divergence between mixer entry and the
selector stores.

Session 3528 narrows that open question upstream: the three allocator edges
are parity-qualified by retail and port, so no allocator or freelist
mitigation is warranted. The legitimate pointer difference is already
present in the callee's entry argument.

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

Latest output boundary:

- [M5-S3539-SOURCE-WRITER.md](M5-S3539-SOURCE-WRITER.md)
- [M5-S3536-OUTPUT-CONTRACT.md](M5-S3536-OUTPUT-CONTRACT.md)

Latest selector boundary:

- [M5-S3533-SELECTOR-AI-RETURN.md](M5-S3533-SELECTOR-AI-RETURN.md)
- [M5-S3534-AI-FREQUENCY-CONTRACT.md](M5-S3534-AI-FREQUENCY-CONTRACT.md)
- [M5-S3530-SELECTOR-SOURCE-WRITER.md](M5-S3530-SELECTOR-SOURCE-WRITER.md)
- [M5-S3532-SELECTOR-SETUP-RETURN.md](M5-S3532-SELECTOR-SETUP-RETURN.md)
- [M5-S3529-SELECTOR-INPUT-BOUNDARY.md](M5-S3529-SELECTOR-INPUT-BOUNDARY.md)
- [M5-S3514-MIX-ENTRY-BOUNDARY.md](M5-S3514-MIX-ENTRY-BOUNDARY.md)
- [M5-S3528-SELECTOR-ALLOC-BOUNDARY.md](M5-S3528-SELECTOR-ALLOC-BOUNDARY.md)
- [M5-S3525-SELECTOR-STORE-ENTRY.md](M5-S3525-SELECTOR-STORE-ENTRY.md)
- [M5-S3519-SELECTOR-CALLSITE-CONTEXT.md](M5-S3519-SELECTOR-CALLSITE-CONTEXT.md)
- [M5-S3520-SELECTOR-AI-BOUNDARY.md](M5-S3520-SELECTOR-AI-BOUNDARY.md)
- [M5-S3521-SELECTOR-CALLSITE-BOUNDARY.md](M5-S3521-SELECTOR-CALLSITE-BOUNDARY.md)
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
