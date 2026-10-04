# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4042 (2026-10-04).

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

Session 4014 repeated the concurrent table with the established default
`ROGUESQ_SPIN_YIELD=1` in both port arms. Retail's whole-RDRAM positive control
and title/hangar VI controls passed. Declared/real reached title at 14.3s and
hangar at 23.5s with `0x800` audio staging; legacy/real reached title at 11.3s
and hangar at 19.6s with `0xF80` staging. Both fired the RSP source-hook and
audio writer controls, neither emitted `[CRASH]` or `[ABORT]`, and all observed
opaque scheduler successor values remained zero. H2 is selected for this run:
the old legacy-only crash remains schedule-sensitive or otherwise unevaluated,
not established as staging causality. ORIGIN: the hook observes the legitimate
runtime DMA-size choice; no mitigation landed.

## Session 4015 (2026-10-04) — spin-yield does not split legacy scheduler behavior

Session 4015 ran the full four-arm scheduler split: retail, declared/real with
spin-yield 1, legacy/real with spin-yield 1, and legacy/real with spin-yield 0.
Retail's whole-RDRAM positive control and title/hangar VI controls fired. All
three port arms fired the RSP source-hook and audio writer controls, reached
title at about 14.4s and hangar at 23.6–23.7s, and emitted no `[CRASH]` or
`[ABORT]`. Declared/real used `0x800`; both legacy arms used `0xF80`; all
observed opaque scheduler successor values remained zero. H2 is selected:
spin-yield does not explain the old legacy crash, which remains
schedule-sensitive or otherwise unevaluated. ORIGIN: the writer and scheduler
hooks observe legitimate runtime choices; no mitigation landed.

Session 4030 rotated the four-arm launch order so legacy/real started first.
The retail whole-RDRAM positive control and title/hangar VI controls fired.
Declared/real reached both target phases with 6,785 audio-stage rows and no
crash/abort; declared/silent reached title but not hangar; legacy/real still
failed before either target phase with 750 audio-stage rows and crashed at
guest PC `0x80001C94`. H2 is selected for arm/path recurrence despite the
changed crash PC; launch order did not qualify the legacy route. ORIGIN: the
route and phase hooks observe legitimate runtime arm choices; no mitigation
landed.

Session 4031 added a two-second gap between the same three port launches,
keeping the order `legacy-real,declared-silent,declared-real`. Retail's
whole-RDRAM positive control and title/hangar VI controls fired. Legacy/real
reached both target phases, emitted 7,024 audio-stage rows with `dma_size=0xF80`,
and had no crash or abort. Declared/real and declared/silent both crashed at
guest PC `0x8000834C` before either target phase and emitted no audio-stage
rows. H1 is selected for the measured schedule split: timing changes the
route outcome relative to s4030, but this does not establish audio staging as
the cause. ORIGIN: launch timing and task/audio hooks observe legitimate
process scheduling and runtime arm choices; no mitigation landed.

Session 4032 re-ran the same arm order with a five-second launch gap. Retail's
whole-RDRAM positive control and title/hangar VI controls fired. Declared/silent
reached both target phases and emitted 2,196 audio-stage rows using declared
`0x800` staging with no crash or abort. Declared/real and legacy/real both fired
the RSP-source control, emitted no audio-stage rows, and crashed before target
phases at guest PC `0x8000834C`; legacy showed `0xF80` staging and declared
showed `0x800` in their pre-target scheduler rows. H1 remains selected: changing
the gap from two to five seconds changed the qualifying arm from legacy/real to
declared/silent, so launch timing is a route discriminator; this still does not
establish audio staging as the cause. ORIGIN: launch timing and task/audio hooks
observe legitimate process scheduling and runtime arm choices; no mitigation
landed.

Session 4033 added a regeneration-safe M3 ownership guard in
`patches/heap_guards.c`: the active-queue sentinel published through
`heap_tail_loc` must not also be reachable from the published active chain.
The ordinary Debug target built successfully. The configured `PatchesLib`
target is still absent and fails before compilation with `No rule to make
target 'PatchesLib'`, so runtime qualification remains blocked. ORIGIN:
`heap_tail_loc` owns the active-queue sentinel and the append link stores;
the sentinel is metadata, not a legitimate active block.

Session 4034 ran the prescribed ten-second stagger with launch order
`legacy-real,declared-silent,declared-real`. Retail's whole-RDRAM positive
control and title/hangar VI controls fired. Legacy/real reached both target
phases with 7,990 audio-stage rows and no crash or abort; declared/real and
declared/silent both fired the RSP-source control but crashed pre-target at
guest PC `0x8000834C` with no audio-stage rows. H1 remains selected at the
measured route scope: timing continues to change which arm qualifies, but no
all-arm qualification exists and audio staging is not established as cause.
ORIGIN: launch timing and task/audio hooks observe legitimate runtime arm
choices; no mitigation landed.

Session 4035 ran the retail-grounded census for `0x800052A0`,
`0x800052A4`, and `0x800052A8` after the route was qualified. Retail's
whole-RDRAM positive control, title VI 1024 (154), hangar VI 512 (181), and
oracle completion all passed. Each candidate had zero post-target samples,
rows, and sequence hits. The paired port reached both target phases with
3,052 audio-ABI rows and 3,047 image-DMA joins, with no crash or abort.
H2 is selected for this candidate class; the next census starts at
`0x800052AC`. ORIGIN: retail PC watches and port phase/task hooks are
diagnostic only; no mitigation landed.

Session 4036 ran the next retail-grounded census for `0x800052AC`,
`0x800052B0`, and `0x800052B4`. Retail's whole-RDRAM positive control, title
VI 1024 (154), hangar VI 512 (181), and oracle completion all passed. No
candidate, post-target, scalar, or sequence evidence appeared. The paired
port reached both target phases with 3,052 audio-ABI rows and 3,047 image-DMA
joins, without crash or abort. H2 is selected for this class; this rules out
these three PCs as the measured retail target-phase writer class, not global
writer absence. ORIGIN: retail PC watches and port phase/task hooks are
diagnostic only; no mitigation landed.

Session 4037 ran the next retail-grounded census for `0x800052B8`,
`0x800052BC`, and `0x800052C0`. Retail's whole-RDRAM positive control and
oracle completion passed; each candidate had zero post-target samples, rows,
and sequence hits. Declared/real and legacy/real both reached title VI 1024
and hangar VI 512, with 3,855/3,805 audio-ABI rows and 3,849/3,797
image-DMA joins, respectively, without crash or abort. H2 is selected for
this class; the next census starts at `0x800052C4`. ORIGIN: retail PC watches
and port phase/task hooks are diagnostic only; no mitigation landed.

Session 4016 qualified a new gate/source boundary capture. Retail's whole-RDRAM
positive control, title VI 1024, and hangar VI 512 controls passed and the
oracle completed; it reported 17 writes to `0x800A0F50`, 192 executions of
`0x80094648`, and 1,125 writes in `0x1798B0..0x179A48`. Declared/real and
legacy/real both reached phase 5 without crash or abort, fired the RSP-source
control, and produced gate, audio-ABI, and image-DMA rows. Each port arm showed
an initial phase-5 gate `0x00` row followed by gate `0x01` rows; image-DMA joins
were 3,574 and 3,662. The oracle's global 200-line hit cap suppressed the
values of the 17 retail gate writes, so H1 versus H2 is not selected; H3 is
refuted because every required control fired. ORIGIN: diagnostic boundary
hooks only; no mitigation landed.

Session 4017 fixed that capture with oracle detail and store-field sampling.
Retail again passed the whole-RDRAM positive control, title VI 1024, hangar VI
512, and completion. All 17 writes to `0x800A0F50` were attributed to the five
observed writer PCs; every captured `source_byte` was `0x00`, and all writes
occurred before the target 512-width hangar phase (the last was at transient
1024-width origin `0x006AB800`). Both declared/real and legacy/real reached
the target phase with gate, writer, and RSP-source controls, and neither
crashed or aborted. H2 is selected at this measured gate scope: the retail
gate activity is initialization/transitional zero-byte traffic, not a
target-phase value transition. This does not explain the upstream zero PCM
payload. ORIGIN: the oracle store-field rows and port hooks observe legitimate
guest/runtime writers; no mitigation landed.

Session 4018 ran the next retail-grounded source-span writer histogram.
Retail passed the whole-RDRAM positive control, produced 631 title VI 1024
rows and 516 hangar VI 512 rows, completed, and recorded 1,125 writes to
`0x1798B0..0x179A48`. The phase-gated histogram was empty for both target
buckets; the lifetime histogram was led by `0x800078EC` (816) and
`0x80007670` (184), with the rest in the `0x8001E2C0`/`0x8001FA*` family.
The paired declared/real arm stopped before target phases and the legacy/real
arm reproduced the `spTaskSchedulerThread` crash at guest PC `0x8000834C`, so
H3 is selected for the paired discriminator. The retail phase-null is valid
only at the measured oracle scope and is not a qualified port writer-class
selection. ORIGIN: diagnostic histogram and route hooks only; no mitigation.

Session 4019 added the next regeneration-safe M3 ownership guard in
`patches/heap_guards.c`: an expansion chain returned by `func_8002221C` is
rejected before free-list splice if any node is already reachable from the
active queue. The ordinary Debug target built and `git diff --check` passed,
but the patch pipeline remains unavailable, so runtime qualification is not
claimed. ORIGIN: `func_8002221C` and its expansion-chain link stores; an
active-queue-owned node is not legitimate free-list ownership.

Session 4020 re-ran the bounded M3 qualification check for that guard. The
ordinary `RogueSquadron64Recomp` Debug target built successfully and
`git diff --check` passed. No runtime alias test was run: the configured
`PatchesLib`/MIPS patch path remains unavailable, so H1 versus H2 is still
unevaluable and H3 remains the qualification result. This confirms source and
host-build cleanliness only, not that the alias occurs. ORIGIN:
`func_8002221C` and its expansion-chain link stores; no mitigation was added.

Session 4021 re-qualified the M5 route with one same-build concurrent capture
of retail, declared/real, declared/silent, and legacy/real. Retail's whole-
RDRAM positive control and both title VI 1024 and hangar VI 512 controls fired.
All three port arms reached both target VIs, fired the RSP-source and
audio-stage controls, and emitted no crash or abort marker. Declared/real and
legacy/real used their respective `0x800` and `0xF80` staging paths; the silent
arm also reached hangar. H3 is selected: the earlier route failure remains
schedule-sensitive or otherwise unevaluated, not explained by staging size or
real-audio execution in this capture. ORIGIN: the route hooks observe
legitimate runtime arm choices; no mitigation landed.

Session 4022 attempted the next retail-grounded candidate census for
`0x800052A0`, `0x800052A4`, and `0x800052A8`. The first generated recipe was
invalid: its nested substitutions armed the prior candidate class, so that
capture is discarded. The fixed standalone recipe was then run after the
existing Debug target build. Retail's whole-RDRAM positive control, title VI
1024 (154), hangar VI 512 (181), and oracle completion passed; no candidate-PC
rows were emitted. Declared/real reached the target phases with audio/image
rows, but legacy/real remained in a 640-wide route and emitted no target-phase
census rows. H3 is selected: the candidate class is unevaluable until the
legacy route is qualified again. ORIGIN: retail oracle PC watches and port
phase/task hooks are diagnostic only; no mitigation landed.

Session 4023 requalified the M5 route with the prescribed same-build
four-arm capture. Retail's whole-RDRAM positive control, title VI 1024,
hangar VI 512, and completion controls fired. Declared/real,
declared/silent, and legacy/real all reached both target phases, fired the
RSP-source and audio-stage controls, and emitted no crash or abort marker.
Declared/real used `0x800` audio staging and legacy/real used `0xF80`.
H2 is selected for this route-level discriminator: the earlier legacy 640
stop is schedule-sensitive or otherwise unevaluated, and the route is
qualified for another retail-grounded source-writer census. ORIGIN: route
hooks observe legitimate runtime arm choices; no mitigation landed.

Session 4024 ran the fixed retail-grounded census for `0x800052A0`,
`0x800052A4`, and `0x800052A8` after the route requalification. The Debug
target built successfully. Retail's whole-RDRAM positive control fired,
title VI 1024 and hangar VI 512 controls fired, and the oracle completed.
All three candidate PCs had zero post-target samples, rows, and sequence
hits. Declared/real and legacy/real both reached phase 5 with 4,020/4,010
audio-ABI rows and 4,003/4,001 image-DMA joins respectively, with no crash
or abort marker. H2 is selected for this candidate class; the next census
starts at `0x800052AC`. ORIGIN: retail PC watches and port phase/task hooks
are diagnostic only; no mitigation landed.

Session 4025 ran the fixed retail-grounded census for `0x800052AC`,
`0x800052B0`, and `0x800052B4`. Retail's whole-RDRAM positive control,
title VI 1024, hangar VI 512, and oracle completion controls all fired; each
candidate had zero post-target samples and rows. The port discriminator did
not qualify: declared/real crashed at guest `0x8000834C` in the scheduler,
while legacy/real emitted no target-phase census before termination. H3 is
selected, so this class is unevaluable rather than a qualified null. The
candidate sweep is parked pending a route requalification.

Session 4026 added the next regeneration-safe M3 ownership check in
`patches/heap_guards.c`: an expansion chain returned by `func_8002221C` must
start with a null predecessor and preserve reciprocal `next`/`prev` links for
every bounded node before it is checked against the active queue or spliced
into the free list. `git diff --check` and the ordinary Debug target passed.
The configured `PatchesLib` target still fails with `No rule to make target
PatchesLib`, so runtime qualification remains blocked; this proves source and
host-build cleanliness, not that a malformed chain occurs. ORIGIN:
`func_8002221C` and its expansion-chain link stores; a foreign predecessor is
not legitimate free-list ownership.

Session 4027 qualified the expansion-chain guard at source and host-build scope:
`git diff --check` and the ordinary Debug target passed, while the configured
`PatchesLib` target failed before compilation with `No rule to make target
'PatchesLib'`. This rules out a source/host-build defect but leaves runtime
qualification blocked; it does not establish that a malformed chain occurs.
ORIGIN: `func_8002221C` and its expansion-chain link stores; no mitigation was
added in this session.

Session 4028 re-ran the four-arm M5 route qualification in one concurrent
capture. Retail passed the whole-RDRAM positive control and produced both
title VI 1024 and hangar VI 512 controls. Declared/silent and legacy/real each
reached both target phases, fired the RSP-source and audio-stage controls, and
emitted no crash or abort. Declared/real fired the RSP-source control but
crashed pre-target in `spTaskSchedulerThread` with last guest PC
`0x8000B650`, before its audio-stage or target-phase rows. This is H3 at the
route level: the single capture is schedule-sensitive/unevaluable and does
not establish a causal arm-specific audio failure. The `0x800052AC` writer
census remains parked. ORIGIN: diagnostic route controls and crash marker;
no mitigation landed.

Session 4029 ran the bounded M3 patch-target qualification. The configured
build graph listed `RogueSquadron64Recomp` but no `PatchesLib`, and invoking
`cmake --build build --config Debug --target PatchesLib` failed immediately
with `No rule to make target 'PatchesLib'`, before compiler, linker, or patch
input discovery. H2 is selected: the current blocker is absent build-graph
integration, not a MIPS toolchain failure. Runtime qualification of the
heap-guard patch remains blocked. ORIGIN: build-graph/toolchain diagnostic
only; no mitigation landed.

Session 4039 re-ran the route table with a 15-second launch gap and order
`legacy-real,declared-real,declared-silent`. Retail passed the whole-RDRAM
positive control and both title VI 1024 and hangar VI 512 controls. Legacy/real
reached both target phases, fired the RSP-source and audio-stage controls, and
produced 8,587 audio-stage rows using `0xF80` staging without crash or abort.
Declared/real and declared/silent each fired the RSP-source control but stayed
at the 320-wide pre-target route and crashed at guest PC `0x8000834C` before
any audio-stage or target-phase row. H1 is selected at route scope: launch
timing/order changes which arm qualifies, while this capture does not establish
audio staging as the cause. ORIGIN: launch timing and task/audio hooks observe
legitimate process scheduling and runtime arm choices; no mitigation landed.

Session 4040 added the next regeneration-safe M3 ownership guard in
`patches/heap_guards.c`: the active-queue sentinel supplied by `heap_tail_loc`
must not appear anywhere in the free-list chain before dequeue/link stores.
The ORIGIN is the free-list link writer (`func_8002221C` and its successor
stores) versus the active-queue sentinel owner; sharing that node is not
legitimate ownership. The ordinary Debug target built successfully. The
configured `PatchesLib` target still fails immediately with `No rule to make
target 'PatchesLib'`, so this is source/host-build evidence only and runtime
qualification remains blocked on build-graph integration.

Session 4041 repeated the M3 patch-target qualification on the current host.
`cmake --build build --config Debug --target PatchesLib` failed before
compilation with `No rule to make target 'PatchesLib'`, while the ordinary
`RogueSquadron64Recomp` Debug target completed successfully. This confirms the
missing target is caused by the configured prerequisite/toolchain gate rather
than a source or host-link error; runtime qualification remains blocked.
ORIGIN: build-graph/toolchain diagnostic only; no mitigation landed.

Session 4042 ran the M5 route table with a new three-second stagger in one
same-build capture. The independent retail oracle fired its whole-RDRAM
positive control and reached title VI 1024 and hangar VI 512. Declared/real
also reached both target phases, emitted 7,144 phase-5 audio-stage rows, and
had no crash or abort. Declared/silent and legacy/real both crashed before
either target phase at guest PC `0x8000834C`, with zero target-phase audio rows.
This selects H2: at least one arm qualifies, but launch schedule still splits
the route; no source-writer null is qualified. ORIGIN: route, scheduler, and
audio-stage hooks observe legitimate arm choices; no mitigation landed.

## Next steps

Work only the first applicable item. The backlog is monotonic; repeated
candidate results are summarized by address range rather than copied here.

1. **M5 route requalification.** Run a genuinely new launch-order/gap
   schedule table before another source-writer census. The retail
   positive/title/hangar controls and all three port-arm phase controls must
   qualify; classify any pre-target arm failure as H3 rather than inferring
   writer absence. Session 4042 selected H2: declared/real qualified while
   declared/silent and legacy/real failed pre-target under a three-second
   declared-first launch.

2. **M5 next source-payload discriminator.** After route qualification,
   rerun the retail-grounded writer class beginning at `0x800052C4`; do not
   infer writer absence from a port arm that fails before its target phase.

3. **M5 new source-payload discriminator.** The gate-value redesign is now
   qualified at its measured scope: retail's 17 gate writes are zero-byte
   initialization/transitional traffic before the target phase. The candidate
   census is qualified through `0x8000529C`, the legitimate `0xF80` writer is
   established, and s4015 rules out spin-yield as the sufficient explanation
   for the old crash. Select a new retail-grounded source-writer class before
   changing audio behavior; do not repeat the scheduler split. Keep scheduler
   `a0` as a message object and treat ABI rows as authoritative.

4. **M5 new source-payload discriminator.** After the `0x800052C4` class is
   qualified, select the next retail-grounded writer class; do not repeat the
   scheduler split or change audio behavior.

5. **M3 patch integration.** On a host with the MIPS toolchain, configure with
   `-DMIPS_TOOLCHAIN_DIR=<toolchain-root>` and restore the `PatchesLib` target
   before runtime-qualifying the active-queue sentinel guard from session 4040.
   The source and ordinary host target pass; do not infer runtime behavior from
   that build alone. The current macOS host has no configured MIPS compiler.

6. **Generated-symbol renaming sweep.** Parked while M5 has an applicable
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
| `H-M5-GateValue` | H2 selected at s4017: all 17 retail `0x800A0F50` writes were zero-byte activity before the target 512-width phase; no target-phase transition. |
| `H-M5-SourceWriterHistogram-4018` | H3 selected for the paired experiment: retail controls and completion passed with no target-bucket writer rows, but declared/real stopped pre-target and legacy/real crashed at `0x8000834C`; the retail phase-null is not a port writer-class selection. |
| `H-M5-RouteQualification-4039` | H1 selected: with a 15-second gap and legacy launched first, legacy/real reached both target phases while declared/real and declared/silent crashed pre-target at `0x8000834C`; timing/order remains a route discriminator, not an audio-staging explanation. |
| `H-M5-TaskOutputFieldsEmptySeparateWriteback` | Selected at s3840 port scope. |
| `H-M5-RetailTaskStageRole` | Selected at s3846; exact task-generation-to-destination join remains open. |
| `H-M5-RetailDestinationAbsentTargetPhase` | Selected at s3855 for `0x1798B0..0x179A48`; lifetime writers are outside target buckets. |
| `H-M5-800078ECZeroFill` | Selected at s3857; sampled writes are zero-valued. |
| `H-M5-CandidateWriterClass` | Bounded classes through `0x800052A8` selected H2 or H3 as recorded in the append-only ledger; never global absence. |
| `H-M5-CandidateWriterClass-0521C` | Selected H2 at s3990: all three PCs absent from qualified retail target/post-target/scalar evidence while the paired legacy port qualified. |
| `H-M3-HeapSpanGuard` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-FreeListReciprocalLinks` | Code landed; validation blocked by absent tools/configured target. |
| `H-M3-ActiveQueueReachability` | Code landed in s3914; validation blocked by absent MIPS toolchain and configured patch target. |
| `H-M3-ActiveQueueOwnershipAlias` | Code landed in s3928; host target passed, patch/runtime validation remains blocked. |
| `H-M3-ExpansionActiveOwnership` | Code landed at s4019; ordinary Debug build passed, while runtime qualification is blocked by the absent patch target/toolchain. |
| `H-M3-ActiveQueueSentinelOwnership` | Code landed at s4033; ordinary Debug build passed, while runtime qualification is blocked by the absent `PatchesLib` target. |
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
| `H-M5-RouteQualification-4028` | H3 selected: retail controls passed; declared/silent and legacy/real reached both target phases, but declared/real crashed pre-target after the RSP-source control. The single capture does not establish causal arm-specific audio failure. |
| `H-M3-FreeActiveOwnershipAlias` | Guard landed at s3996: a valid acyclic free-list and active queue must not share a terminal node; runtime qualification is blocked by the unavailable PatchesLib target. |
| `H-M3-EmptyActiveQueueTail` | Guard landed at s4003: an empty published active queue must have a null tail predecessor and successor; host build passed, while patch/runtime qualification is blocked by the unavailable PatchesLib target. |
| `H-M5-RouteQualification-4021` | H3 selected: declared/real, declared/silent, and legacy/real all reached both target VIs with route controls and no crash/abort in the same-build capture. |
| `H-M5-CandidateWriterClass-052A` | H3 selected at s4022: retail controls and candidate-null evidence passed, but declared/real reached target phase while legacy/real remained at 640 width before target phase; no writer conclusion is allowed. |
| `H-M5-RouteQualification-4023` | H2 selected: retail and all three port arms reached both target phases with positive controls; the earlier legacy 640 stop did not recur. |
| `H-M5-RouteQualification-4030` | H2 selected: with legacy/real launched first, declared/real reached both target phases, declared/silent stopped after title, and legacy/real crashed pre-target at guest PC `0x80001C94`; launch-order permutation did not qualify the route. |
| `H-M5-RouteQualification-4031` | H1 selected: a two-second launch gap let legacy/real reach both target phases while declared/real and declared/silent crashed pre-target at `0x8000834C`; timing changes route outcome, but audio staging is not established as cause. |
| `H-M5-CandidateWriterClass-052C` | H3 selected at s4025: retail controls and candidate-null evidence passed, but declared/real crashed at `0x8000834C` and legacy/real produced no target-phase rows; no writer conclusion is allowed. |
| `H-M5-RouteQualification-4032` | H1 remains selected: with a five-second launch gap, declared/silent qualified while declared/real and legacy/real crashed pre-target; the qualifying arm changed from s4031's legacy/real result. |

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
- Session 4038's bounded census for `0x800052C4`, `0x800052C8`, and
  `0x800052CC` was unevaluable: the retail whole-RDRAM positive control and
  oracle completion passed, and all three candidate PCs had zero post-target
  samples/rows, but legacy/real crashed at `0x8000834C` before title/hangar.
  Declared/real independently reached title VI 1024 and hangar VI 512 with
  3,804 audio-ABI rows and 3,787 image-DMA joins. This selects H3 for the
  candidate class, not writer absence.
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

Session 4021's same-build four-arm capture passed the retail whole-RDRAM,
title, and hangar controls. Declared/real, declared/silent, and legacy/real
all reached both target phases, fired their RSP-source/audio-stage controls,
and emitted no crash or abort marker. This qualifies the route for a new
source-writer discriminator and rules out staging size or real-audio mode as
the sufficient explanation for the earlier route failure in this capture.

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

The s4010 H1 route split is superseded at the broader four-arm scope by s4021:
declared/real, declared/silent, and legacy/real all reached both target VIs in
one qualified capture. It remains a valid description of that earlier
schedule, not evidence that staging determines route success.

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
