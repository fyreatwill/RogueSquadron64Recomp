# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4107 (2026-10-06).

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) on the qualified real-audio/LLE/spin-yield route.
Hangar geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` is the
silent `Broke` control; real audio is not production-complete.

The active M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are zero (`FNV=0x762B22A5`); retail's
phase-gated hangar snapshot is 408 bytes with nonzero=0. The port descriptor
`0x1798B0 -> DMEM 0xCB0` is written by legitimate zero-valued
`0x800078EC` fill activity. No nonzero hangar producer is established.

The task-contract consumer boundary is closed at the measured scope: declared
and legacy real-audio arms reached both target phases with matching zero
payload consumer signatures, while the silent arm remained a valid control.
The old declared-size/legacy crash split is schedule-sensitive and is not an
audio-staging explanation. The legitimate legacy staging writer is still
`0xF80`; declared-size staging is `0x800`.

M3 has landed regeneration-safe ownership guards in `patches/heap_guards.c`
for free-list span/reciprocal links, active-queue reachability and aliasing,
empty-queue tail state, expansion ownership, the active sentinel's
predecessor, allocator-cursor/sentinel aliasing, and full free-chain/active-queue disjointness. The ordinary Debug
target builds. Runtime qualification is
blocked because this host has neither `mips64-elf-gcc` nor `mips64-elf-ld`, so
CMake still omits `PatchesLib` after the cross-platform discovery repair. The
installed Clang also has no MIPS backend, and local filesystem checks found no
toolchain or rebuildable source tree. The sentinel guard's ORIGIN is
`heap_tail_loc` and the active-queue append stores; a predecessor on the
sentinel path is not legitimate ownership state.

The title host-sink boundary is closed on the schedule-gated declared-real
route. Retail passed the whole-RDRAM positive control and both target phases;
the port reached title and hangar with nonzero consumer PCM. In both phases
the host opened device 2 and recorded positive `call_delta`/`queued_after`
rows. This rules out device-open failure and zero enqueue at the measured
boundary; playback/drain timing remains open.

## Recent qualified evidence

- Retail oracle whole-RDRAM, title-VI, and hangar-VI positive controls are
  required and have passed on qualified captures. A candidate null is valid
  only when the paired port also reaches both target phases.
- Candidate writer classes through `0x8000529C` have been qualified in
  adjacent batches where the port completed; candidate PCs had no target or
  post-target evidence. The `0x800052C4` class is not qualified: recent route
  permutations (sessions 4043–4046) left no arm reaching both target phases.
- Route permutations through sessions 4030–4032 and 4034, 4039, 4042–4046
  changed which port arm failed or qualified. This confirms a schedule/route
  discriminator is needed; it does not identify the missing source writer.
- Session 4047 qualified the sentinel guard only at source/host-build scope;
  session 4049 repaired cross-platform discovery but still found no MIPS
  toolchain. `PatchesLib` was absent and no runtime behavior was inferred.
- Session 4050 reconfigured on macOS, confirmed no `mips64-elf-gcc` or
  `mips64-elf-ld` on PATH, observed the expected CMake skip and missing
  `PatchesLib` target, and rebuilt the ordinary target successfully. Runtime
  qualification remains unevaluable on this host.
- Session 4051 repeated the M3 discriminator: both MIPS tools remain absent,
  `PatchesLib` remains absent, and the ordinary target builds. This is a
  prerequisite block, not runtime evidence; do not repeat until a toolchain or
  another qualified host is available.
- Session 4052 tested the block's alternate routes. `clang --target=mips`
  failed with no compatible target; its assembler also rejected MIPS. No
  MIPS GCC/LD, MIPS Linux cross tools, or generated patch artifacts were found
  locally. The M3 dependency remains external; work is re-scoped to the M5
  route discriminator until a qualified MIPS host is supplied.
- Session 4053 ran a new reversed launch order with 7-second inter-arm gaps.
  The retail oracle positive control fired and reached title 1024 and hangar
  512. All three port arms failed before title 1024: declared-real and
  legacy-real crashed in the scheduler path, while declared-silent reached
  only a 640-width phase. This selects H3 for this schedule; its source-writer
  nulls are unevaluable and do not advance the writer census.
- Session 4054 ran one same-build sequential arm-isolation matrix while the
  retail oracle remained active. Retail passed the whole-RDRAM control and
  reached title 1024 and hangar 512. Isolated declared-real reached both
  targets and reproduced the zero-payload image signature
  (`FNV=0x762B22A5`, nonzero=0); isolated declared-silent and legacy-real both
  crashed in `spTaskSchedulerThread` before target phases. This qualifies the
  declared-real route for the `0x800052C4` census, while the other two arms
  remain unevaluable.
- Session 4055 ran the qualified declared-real route with the retail oracle and
  all three candidate callsites (`0x800052C4/8/CC`) armed together. Retail
  passed the whole-RDRAM control and reached title 1024 and hangar 512, but
  every candidate reported `seen=0`, `n=0`, and no phase-gated store row.
  Declared-real reached both target phases and again produced
  `FNV=0x762B22A5`, nonzero=0. The candidate class is therefore H3/
  unevaluable as a source-writer class, not H1 or H2.
- Session 4056 ran a new same-build concurrent process-topology matrix with
  the retail oracle and declared-real, declared-silent, and legacy-real arms
  active together. Retail passed the whole-RDRAM control and reached title 1024
  and hangar 512. Both declared arms reached both target phases; legacy-real
  again crashed in `spTaskSchedulerThread` before them. This selects H1 for
  the startup-dependency hypothesis: process topology changes which arms
  qualify. It does not qualify a source-writer null for legacy-real.
- Session 4057 ran the next retail-grounded predecessor batch with the
  whole-RDRAM/title/hangar controls and declared-real port arm. Retail passed
  all controls and both target phases; the port reached both target phases and
  retained `FNV=0x762B22A5`, nonzero=0. `0x800C825C` had zero target-phase
  rows, selecting H3/unevaluable for that predecessor. The paired
  `0x800078E0/EC` target summaries were also zero, while `0x800078EC`
  independently had 816 scalar source-span stores, all zero with mismatch=0.
  This does not identify the upstream zero producer.
- Session 4058 audited the free/active ownership idiom and found the existing
  `free_chain_disjoint_from_active_tail` check did not reject an alias at an
  earlier active-queue node. Added a bounded whole-active-chain comparison in
  `patches/heap_guards.c`, with ORIGIN comments naming `heap_free_head` and
  `heap_other_listhead` as the separate guest owners. The ordinary Debug target
  built successfully; MIPS runtime qualification remains unavailable.
- Session 4059 rebuilt the ordinary Debug target after the overlap-guard commit,
  passed `git diff --check`, and confirmed that `PatchesLib` has no generated
  build target on this host. This is a host-build qualification only; it adds
  no runtime evidence and does not reopen the M3 toolchain prerequisite.
- Session 4060 ran the prescribed same-build retail-oracle/declared-real capture.
  Retail passed the whole-RDRAM positive control and both title/hangar phase
  controls; the port also reached both phases with `FNV=0x762B22A5` and
  nonzero=0. Exact hangar-phase post-target attribution produced zero rows for
  `0x800C825C`, `0x800078E0`, and `0x800078EC`. The oracle did record 816
  scalar-zero stores from `0x800078EC`, but those requested-PC rows were tagged
  to transition state `origin=0x006AB800`, width 1024, not the exact hangar
  bucket; mismatch=0. This rules out treating `0x800078EC` as the exact
  hangar-phase writer, but does not identify a replacement producer.
- Session 4061 repeated the immediate-writer capture with explicit transition
  and hangar buckets in one run. Retail passed the whole-RDRAM positive control
  and reached title `0x00790400/1024` and hangar `0x006AB400/512`; the port
  reached both phases with no crash/abort and retained `FNV=0x762B22A5`,
  nonzero=0. Retail recorded 816 mismatch-free zero scalar stores from
  `0x800078EC`, but its detailed rows were in the `0x006AB800` transition
  (live width 512) or a width-1024 `0x006AB400` phase; the exact
  `0x006AB400:512` bucket had no candidate rows. H2 is selected: this
  zero-fill is not the exact hangar writer, so a different producer or an
  absent producer remains open.
- Session 4062 qualified the next source-span class with the same retail and
  port controls. `0x80007670` executed 1,563 times while the retail exact-
  hangar source-range watch was active, but its exact `0x006AB400:512` target
  rows were zero; no mismatch-free scalar sample attributed a target write to
  this PC. H2 is selected for this class, so the ranked census advances to its
  adjacent `0x800076A0` class.
- Session 4063 redirected the M5 measurement to the title AI endpoint. The
  retail oracle passed the whole-RDRAM positive control and reached title 1024
  and hangar 512; its `osAiSetNextBuffer` witness recorded nonzero title PCM
  on 1,015 of 1,204 title writes and nonzero hangar PCM on 229 of 242 writes.
  The qualified declared-real port arm reached both target phases and its
  matching source and host-consumer witnesses were nonzero in title (44
  phase-scoped rows each). H2 is selected: title PCM is produced and queued by
  the port, so the missing-audio question moves to the SDL/device sink rather
  than the AI producer. The silent control was not used to override this
  endpoint result; the first incomplete recipe crashed pre-title and is
  unevaluable.
- Session 4064 first ran the sink capture concurrently and hit the known
  schedule-sensitive `spTaskSchedulerThread` crash before target phases; the
  retail positive control still passed, so that arm was unevaluable. A fixed
  schedule-gated rerun waited for the retail positive-control marker before
  launching the port. Retail again reached title 1024 and hangar 512 with
  nonzero AI output, while the port reached both phases and produced nonzero
  consumer PCM. The host logger recorded device 2 and positive queue calls in
  both phases, with no `[CRASH]` or `[ABORT]`. Hqueue is selected: the SDL
  enqueue/device boundary is live, so the next discriminator is playback/drain
  timing.
- Session 4065 reran the same schedule-gated retail/declared-real capture with
  the drain logger actually enabled. Retail passed the whole-RDRAM positive
  control and produced nonzero title/hangar AI output; the port reached both
  target phases and produced phase-scoped consumer rows. Drain rows were
  present in both phases and stayed positive while host queue calls remained
  positive: title values ranged through 741–3813 bytes and hangar repeatedly
  tracked 767–1537 bytes, with no zero-drain starvation pattern. Hplay is
  selected, ruling out immediate queue-drain starvation; the remaining sink
  question is device callback/output behavior.
- Session 4066 attempted one same-build native-SDL versus
  `SDL_AUDIODRIVER=dummy` A/B after the retail whole-RDRAM control. The dummy
  arm reached title 1024 and hangar 512 with positive queue and drain rows;
  the native arm crashed in `spTaskSchedulerThread` before both targets. A
  fixed native-only isolation repeated the pre-target crash while retail
  again passed its positive control. The native-versus-dummy sink comparison
  is unevaluable; this is additional Hroute evidence, not an SDL backend
  conclusion.
- Session 4067 ran the prescribed native-SDL silent control with
  `ROGUESQ_AUDIO_UCODE=0` after the retail whole-RDRAM control fired. The
  silent native arm reproduced the same `spTaskSchedulerThread+9632` crash
  before title 1024 or hangar 512; no phase-scoped host queue/drain result
  exists. This selects Hnative-backend over Hreal-route for the native
  pre-target failure, while leaving the actual scheduler corruption origin
  open. The prior real-arm run was not used as silent evidence because the
  recipe defaulted to `ROGUESQ_AUDIO_UCODE=1` until the explicit override was
  supplied.
- Session 4068 ran native-SDL silent and `SDL_AUDIODRIVER=dummy` silent arms
  concurrently in one same-build capture, with the retail whole-RDRAM control.
  The control fired; both port arms independently crashed before title 1024 or
  hangar 512 at `spTaskSchedulerThread+9632`, with identical fault address
  `0x400128d47` and last guest PC `0x8000834c`. This selects Hshared-scheduler
  over Hdevice-init for the silent pre-target failure. It does not identify
  whether the shared defect is guest queue/state corruption or process-topology
  interaction; no sink conclusion is available.
- Session 4069 reran the same retail-gated silent arms sequentially in one
  capture. The retail whole-RDRAM positive control fired. Native silent reached
  title 1024 and hangar 512, while dummy silent still crashed before either
  phase at `spTaskSchedulerThread+9632` with fault `0x400128d47` and guest PC
  `0x8000834c`. This selects Htopology/resource interaction over a deterministic
  shared guest-state defect, but leaves a dummy-specific startup failure open;
  no sink conclusion was drawn from the dummy arm.
- Session 4070 audited the active-queue ownership guard class and found that
  `heap_other_listhead` was checked for KSEG0 validity but not for aliasing the
  `heap_tail_loc` allocator sentinel. Added a regeneration-safe guard in
  `patches/heap_guards.c`; its ORIGIN is the active-head/sentinel publication
  pair, and the sentinel is metadata rather than legitimate queue ownership.
  The ordinary Debug target built successfully. `PatchesLib` remains
  unavailable because this host has no configured MIPS patch target/toolchain;
  runtime qualification is not inferred.
- Session 4071 repeated the retail-gated sequential native-silent then
  dummy-silent capture with the portable macOS driver. Retail passed the
  whole-RDRAM positive control and reached title 1024 and hangar 512. Native
  reached both phases with no crash/abort, and dummy also reached both phases
  with no crash/abort. Since session 4069's dummy arm crashed under the same
  topology, this selects Hschedule/resource sensitivity over a deterministic
  dummy-state defect; it does not qualify native-vs-dummy sink behavior.
- Session 4072 ran dummy-silent alone after the retail whole-RDRAM positive
  control, with no native predecessor. Retail reached title 1024 and hangar
  512; dummy-only also reached both gates with no crash/abort. This supports
  Hnative-residue over a deterministic dummy-start dependency, but remains a
  route/schedule result rather than sink evidence.
- Session 4073 ran the clean dummy-silent launch-timing A/B after the retail
  whole-RDRAM positive control. Both the immediate and fixed-7-second-delayed
  dummy arms reached title 1024 and hangar 512 with no crash/abort. This
  strengthens Hnative-residue and rejects an immediate-versus-delayed dummy
  phase-gate split for this recipe; it does not qualify the sink because both
  arms were silent controls.
- Session 4074 first ran the prescribed same-build default-image/silent pair.
  Retail passed the whole-RDRAM, title, and hangar controls; silent reached
  both target phases, but the image arm crashed before its first audio
  dispatch in `spTaskSchedulerThread+9632` at fault `0x400128d47` (guest PC
  `0x8000834c`). The pair was therefore route-invalid. The fixed image-only
  rerun kept the same retail controls and reached hangar without a crash:
  the image changed DMEM, emitted two DMAs, exited at `0x1328`, completed SP
  service, and delivered the guest completion message. Its hangar stage-3
  output and PCM source/consumer rows remained zero (`FNV=0x762B22A5`,
  `nz=0`), while the gate was zero. This closes image task/DMEM/DMA/SP
  coverage at the isolated route and leaves the named hangar-output writer
  boundary open; it does not authorize a gate change.

Detailed counts and every failed or superseded run remain in the append-only
ledger. Use bounded `grep`/`sed` windows for that file; never read it whole.

Session 4076 audited the session-4075 `0x80094648` boundary. Retail passed
whole-RDRAM, title, and hangar controls; the named PC produced 88 hangar-bucket
execution rows and 72 mismatch-free nonzero scalar stores to
`0x00141AD8..0x00141AEC`. The generated port source contains the guest store,
but its `s2609` host witness was absent because the fixup's broad s2586-entry
guard skipped the insertion after regeneration. The s4075 port null is
therefore unqualified for path divergence; a regenerated witness run is
required. ORIGIN: `0x80094648` is the legitimate guest indexed channel-span
writer; the fix is diagnostic-only.

Session 4077 reran the regenerated witness on the isolated image route. The
retail oracle again passed whole-RDRAM, title, and hangar controls and reported
88 hangar-bucket `0x80094648` rows. The port passed title and hangar with no
crash or abort; its new positive control fired in both phases and emitted 11
hangar rows. Those rows matched the retail-shaped relation: destinations began
at `0x80141AD8` and requested/stored bytes were both `0x7F`. H94648-port-store-live
is selected: the port reaches the named indexed writer, so the zero hangar
PCM/image payload is downstream or in a later producer/transform boundary, not
evidence that this store was skipped. ORIGIN: the legitimate writer is the
guest `sb` at `0x80094648`; the witness remains diagnostic-only.

Session 4078 grounded the next consumer before instrumentation: retail read the
physical `0x00141AD8..0x00141AEC` span 89,976 times after the whole-RDRAM
positive control, and the only exact generated reader is `0x8008D5E4` in
`tickAllAudioChannels`. A regenerated port witness at that load reached title
and hangar, with 256 sampled rows and hangar activity before the phase budget;
effective addresses covered `0x80141AD8..0x80141AEC`, and sampled values were
`0x7F`, matching the qualified writer value. Hconsumer-live is selected: the
indexed channel span is consumed on the port, so the zero PCM/image payload is
downstream of this load. The first oracle-first schedule crashed at the known
pre-target scheduler boundary; the port-first retry qualified the controls and
is the result used here.

Session 4079 grounded the next transform with the retail oracle before adding
the port witness. Retail passed the whole-RDRAM positive control and executed
`0x800923E4` 100,372 times; 100,359 executions had caller `0x8008D710`,
including both title and hangar phase buckets. Two probe-route port attempts
were invalid: both died at `fillSampleStreamRange+932` before title, so their
nulls were not interpreted.

The fixed direct-AUTOPILOT image route passed the same oracle controls and
both port target phases. The regenerated port call/state witnesses each
produced 128 title and 128 hangar rows. At the hangar call boundary, the port
carried `a1=0`, `a3=0`, and `scaled=0`, while retail's paired oracle calls
carried nonzero `a1`/`v1` values in the same phase (including
`a1=0x004A79E0`). The downstream port state witness remained zero at the
sampled `+0x44/+0x48` words. Htransform-value is selected at the call-input
boundary: the qualified channel load reaches the callsite, but the port's
transform inputs are zero where retail's are not. The state comparison is
port-only and is not treated as independent retail attribution. ORIGIN: the
legitimate transform inputs are the guest register values prepared before
`0x8008D710`; these are diagnostic-only witnesses, not a mitigation.

Session 4080 added a regeneration-safe setup witness at `0x8008D70C` for
`$s2/$s3/$s0`, prepared `$a1/$a2/$a3`, and `$v1`/scaled. The regenerated
source and ordinary Debug target both qualify. The direct-AUTOPILOT retry
reached title and a hangar VI marker but produced no hangar setup/call rows;
the fixed `tools/probe.sh` retry failed to reach its 1024 gate. Hcoverage is
selected for this iteration, so no setup register is classified as the first
divergence and Htransform-value remains unchanged. The fresh oracle attempt
did fire its whole-RDRAM positive control but was terminated at the wrapper
layer before target-phase output, so it adds no new retail phase evidence.

Session 4081 reran the witness on the exact qualified direct-AUTOPILOT s4079
route. Retail passed the whole-RDRAM, title, and hangar controls; the port
produced 256 channel-load, setup, call, and state rows, including 128 hangar
setup rows. Every sampled setup row had `s2=0`, `s0=0`, `v1=0`, `a1=0`,
`a3=0`, and `scaled=0`; `s3` matched nonzero prepared `a2`. Together with
s4079's paired retail nonzero call inputs, Hsetup-divergent is selected: the
first qualified zero inputs are already present at the setup boundary, so the
producer search moves earlier. ORIGIN: the legitimate transform inputs are
the guest setup registers before `0x8008D70C`; this is diagnostic-only.

Session 4082 added a regeneration-safe predecessor witness at the four earlier
stages `0x8008D5D0`, `0x8008D5EC`, `0x8008D614`, and `0x8008D674`. The
qualified port route reached both target phases, fired the existing
`0x8008D5E4` channel-load control, and produced predecessor rows at all four
PCs; the first stage's `$s2` and the later `$s0` path were zero in the sampled
port rows. A separate completed retail-oracle run passed the whole-RDRAM
control and recorded 90,484 executions of `0x800923E4` before its required
SIGKILL, with caller `0x8008D710` and nonzero title-phase `$a1` values. The final paired rerun
crashed before the port witness, so it is not used as a null. Hpre-early is
selected: the search moves before `0x8008D70C`, but no earlier writer is yet
identified. ORIGIN: the legitimate values are the guest arithmetic results at
the four predecessor instructions; the witness is diagnostic-only.

Session 4083 first ran a retail-grounded predecessor capture with the
whole-RDRAM positive control and both target phases; retail executed all four
predecessor PCs. The first concurrent port arm hit the known
`spTaskSchedulerThread+9632` schedule-sensitive crash before target phases,
so its null was rejected. A fixed control-first retry qualified the retail
controls and the isolated port reached both phases with 256 arithmetic rows,
including 128 hangar rows. Retail's `0x8008D5D0`/`0x8008D5EC` rows and the
port's corresponding `0x8008D5CC`/`0x8008D5E8` operands were shaped as zeros;
retail's `0x8008D614` rows carried nonzero `v1` and products, while the port's
`0x8008D610` rows had `lhs=0`. Both sides kept the later `0x8008D674` source
zero. Hvoice-modulator-return is selected: the first qualified divergence is
the value returned by the `0x80084860` call feeding `0x8008D610`, not the
earlier multiply or later shift. ORIGIN: the legitimate source is the guest
`0x80084860` return/input at the `0x8008D610` arithmetic site; the new rows
are diagnostic-only.

Session 4084 added a regeneration-safe witness at the `0x8008D624` callsite
and inside `0x80084860`, including phase-scoped entry/return rows. Retail
passed the whole-RDRAM and title/hangar controls and recorded hangar entry
arguments `a0=0x8013D880`, `a1=0x8013D952`, with pre-call `v0=0x00800000`;
the qualified port callsite carried the same tuple. Retail's post-call
`0x8008D62C` witness and the port callee return both reported
`v0=0x00002000` for the corresponding hangar call. Hcallee-match is
selected: this call's inputs and return agree, so its caller-side use or a
different earlier callsite remains open. The first expanded paired port retry
missed target phases and was rejected; the isolated rerun reached hangar and
provided the qualified port rows. ORIGIN: the legitimate value is the guest
`0x80084860` return; the witness is diagnostic-only.

Session 4085 added a regeneration-safe witness after each caller-side
instruction at `0x8008D62C`, `0x8008D630`, `0x8008D634`, `0x8008D638`, and
`0x8008D63C`. The retail oracle passed the whole-RDRAM positive control and
both target phases. The qualified port reached both target phases and emitted
512 post-call rows, including the hangar bucket. Its post-instruction values
matched retail's sequence: `0x2000 -> 0x40 -> 0 -> 0`, with `$s3` unchanged
through preparation and updated at `0x8008D63C`. Hcaller-use is selected;
the search moves to the separate `0x8008D5FC` call. The first wrapper attempt
orphaned the oracle before launching the port; a fixed port continuation
supplied the qualified route. ORIGIN: the values are legitimate guest return
and arithmetic registers; all hooks are diagnostic-only.

Session 4086 added a regeneration-safe witness at the separate `0x8008D5FC`
call and its first post-return instruction `0x8008D604`, retaining the
`0x8008D610` arithmetic witness. The first capture's parser searched for
fields in the wrong order; its logs already showed both controls and port
hangar rows, so it was rejected as Hcoverage. The fixed rerun qualified all
controls and produced 14 hangar call rows, 43 hangar return rows, and 24
arithmetic rows. Retail's watched `0x8008D5FC` return values varied by voice
record, including `0x4203`, `0x9C46`, and `0x3F80`, while the port's sampled
`0x8008D604` result repeated `0x3F80`; the port's `0x8008D610` lhs remained
zero. Hnext-return is selected: the first qualified mismatch is inside
`evaluateVoiceModulatorRecord` on the `s0 + 0xC0` call path. ORIGIN: the
legitimate value is the guest return from `0x80084860`; the hooks are
diagnostic-only.

Session 4087 ran the callee-path discriminator. The retail oracle passed the
whole-RDRAM positive control and both target phases; its hangar
`0x8008D5FC -> 0x80084860` rows included varying nonzero returns. The first two
port attempts were Hcoverage. A qualified timing retry reached title and
hangar and retained 86 `0x8008D604` post-call rows, but the new detail hooks at
`0x8008488C`, `0x800848A8`, and `0x800848C4` produced zero rows even though
`funcs_20.c.o` references the hook symbol. The saved guest `ra` was zero in
the existing callee witness, invalidating the planned return-address filter;
removing that host-side filter still produced zero detail rows. The callee
entry/load/return hypotheses remain unevaluable; the next discriminator is
hook transport/linkage. ORIGIN: the new values are legitimate guest callee
inputs and branch results; this was diagnostic-only.

Session 4088 added a host-side synthetic detail-hook control and rebuilt the
Debug target successfully. The first combined capture had an oracle gate that
checked the wrong VI-line shape; the fixed recipe passed the retail
whole-RDRAM and hangar controls. Its port arm then crashed in
`fillSampleStreamRange` before title/hangar, so no host-control or generated
detail row was phase-qualified. A retry using the previously qualified timing
route also crashed before target phases. This is Hcoverage, not evidence for
hook transport or callee entry/load/return. The generated object still has the
detail-hook relocation; a future qualified run must put the synthetic control
on the already-observed `0x8008D604` post-call path so host transport is
positive even when the `0x8008D5FC` call is absent. ORIGIN: the synthetic row
is diagnostic-only; no guest value or mitigation changed.

Session 4089 moved the synthetic detail-hook control from the `0x8008D5FC`
callee witness to the already-observed `0x8008D604` post-call hook and rebuilt
the Debug target. The oracle whole-RDRAM positive control fired and reached
title 1024, executing all five watched PCs; it did not reach the required
retail hangar phase in this capture. The port reached title 1024 and hangar
512 with 86 post-call rows. The synthetic row (`pc=0xC0DEC002`) fired once
from the post-call path, and the genuine detail hooks produced 511 rows in
addition to it. This positively proves host transport and generated detail
hook linkage at title scope, refuting Htransport there; entry/return
value-classification remains pending a retail-and-port hangar-qualified run.
The missing retail hangar gate makes the overall capture Hcoverage, not a
callee-value result. ORIGIN: the synthetic and detail values are
diagnostic-only; no guest value or mitigation changed.

Session 4090 ran the corrected callee-value comparison. The oracle whole-RDRAM
positive control and title/hangar phase controls fired; the port reached both
phases and emitted the synthetic transport row plus 85 title and 86 hangar
samples at each of `0x8008488C`, `0x800848A8`, and `0x800848C4`. For the
paired records, the port detail values matched the retail register handoff:
for example record `0x8013D9AC` was `(0x1, 0x40, 0x0)` and retail's successive
watched states supplied `(v0=0x1, a0=0x40, a0=0x0)`; record `0x8013D9BE`
matched `(0x1, 0x41, 0x0)`. Hcallee-entry/load/return is selected as matched
at the sampled scope, so the search moves downstream of `0x800848C4`; this
does not prove the later transform globally because the port is sampled and
the oracle is not record-synchronized. ORIGIN: these are legitimate callee
register/value observations; all hooks are diagnostic-only.

Session 4091 qualified the first post-callee return boundary: the port
`0x80084AB8` return support matched the low-16-bit `s0` support observed at
retail, selecting Hlater-transform at that sampled boundary. The rows were
not record-synchronized, so later transform stages remain open.

Session 4092 ran the required oracle-only key-on/divisor capture. The
whole-RDRAM positive control and both title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400` phase gates fired. All eight key-on early-return PCs
(`0x80090CEC` through `0x80090DD0`) recorded zero executions, while the
known publisher `0x80090768` executed 50,643 times, including printed rows in
both target buckets with values including `0x180`. Hreturns-dead is selected
for this measurement: no target-phase key-on site is reachable, so Step 5
must not remove or replace the returns. This does not prove why the caller
does not enter the sites or authorize a guard change. The capture wrapper
also corrected its parser after the run; the raw oracle summary, not the
initial wrapper counters, is the evidence. This is single-source retail
ground truth; a port-side witness is still required before any behavior
change.

Session 4093 ran the required oracle-only caller/tail capture with the
whole-RDRAM positive control and both target phase transitions. Retail reached
title and hangar; `0x80090A3C` executed 53,505 times (12,964 title rows and
6,988 hangar rows), and its normal tail `0x80090DE8` matched those executions.
The divisor publisher `0x80090768` executed 53,513 times (12,961 title and
7,000 hangar rows). The eight early-return PCs remained at zero. This selects
Hdescriptor-branch over Hcaller-gap and Hpublisher-misjoin at retail scope:
the key-on entry and normal tail are live, while the guarded descriptor branch
is not. It is single-source retail ground truth; qualify the paired port
boundary before changing the returns.

Session 4094 ran the repaired same-build declared-real port boundary capture
with the retail whole-RDRAM positive control and title/hangar phase controls.
The clean capture reached port title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`; the retail control fired and reached both target
transitions. The port key-on table recorded `entry=102806` and
`normal_tail=102806` in the hangar bucket, with all eight early-return sites
at `guard=0`; the live divisor sites had `div=102806` and the alternating
sites remained zero. This selects Hport-descriptor-branch over Hport-caller-gap
and Hport-returns-live at the qualified boundary. The port publisher was not
independently counted in this run, so publisher attribution remains open;
there is no basis to remove or replace any return. The first wrapper launch
left a game process after its controller was interrupted and its mixed logs
were discarded; only the isolated clean output was used.

Session 4095 extended that capture with an independent retail PC/field tuple
watch in the same run. The whole-RDRAM positive control and both retail and port
phase controls fired. Retail recorded 26,913 executions each at
`0x80090A3C` and `0x80090DE8`, plus 27,016 at publisher `0x80090768`; its
normal-tail descriptor rows carried selector values `1..7`. The port reached
both phases, retained live entry/tail counts (`110,901` in the final hangar
bucket), and its pointer/branch rows carried selector `0` with the same
`0xC0` mix-length inputs; all eight returns remained zero. Htuple-diverge is
selected: the first measured mismatch is the descriptor branch selector, not
the caller or return guards. This is two-source evidence at the route/tuple
boundary (retail oracle plus port witness), but the rows are not
record-synchronized, so it does not yet name the missing writer. ORIGIN: the
selector is a legitimate guest descriptor field; no mitigation or guest
behavior changed.

Session 4096 performed the bounded M3 expansion-chain ownership audit required
by the no-churn pivot. `func_8002221C`'s fresh chain was checked for link
reciprocity and active-queue overlap, but the active sentinel was not checked
until after the expansion could be spliced. Added a regeneration-safe guard in
`patches/heap_guards.c` that validates the fixed `heap_tail_loc` metadata slot,
the sentinel's predecessor/successor state, and fresh-chain disjointness before
any splice store. ORIGIN: `func_8002221C` owns fresh free-list nodes and
`heap_tail_loc` owns allocator metadata; an alias is not legitimate ownership
state. The ordinary Debug target built successfully; MIPS patch/runtime
qualification remains unavailable because this host lacks `mips64-elf-gcc` and
`mips64-elf-ld`.

Session 4097 ran the retail selector-range census with the whole-RDRAM positive
control and both target VI buckets. The control reached 10,000 callbacks;
title VI 1024 and hangar VI 512 both fired; the physical range
`0x00171E22..0x00172D00` recorded 713,374 writes. Hangar's high-volume writers
were `0x800907A0` (`sb +0x84`) and `0x8008F64C/50` (`+0x60/+0x5C`), not the
known `s1+0x22` selector-store sites. This is single-source retail evidence:
it narrows the writer census but does not yet prove selector absence because
the exact candidate PCs were not armed with store-field rows.

Session 4098 repeated that census with exact store-field dumps for all seven
known `s1+0x22` candidates. The whole-RDRAM control fired; retail reached
title VI `0x00790400/1024` (632 phase VIs) and hangar VI
`0x006AB400/512` (385 phase VIs). In the hangar bucket, `0x80090AAC` wrote
5,086 rows and `0x80090BA4` wrote 154 rows; the other five candidates had no
rows. Selector values and source fields were present in the matching records.
Hwriter-live is selected at retail scope. This names two live selector
writers but does not yet prove which writer/value the port fails to reproduce.

Session 4100 repaired the regeneration-safe port selector-writer witness and
ran one retail-gated declared-real capture. Retail passed the whole-RDRAM
positive control and reached title `0x00790400/1024` and hangar
`0x006AB400/512`; the port reached both phases. The new witness control fired
in both target phases, and `0x80090AAC` produced 512 title and 512 hangar rows.
No port `0x80090BA4` row appeared. Retail's independent store-field rows
attributed 157 exact target rows to `0x80090AAC` and carried matching selector
values, so the port writer boundary is live; a null at these two sites is
rejected. This is two-line evidence for the live-port-writer result, with
retail and port rows not record-synchronized. ORIGIN: selector fields are
legitimate guest descriptor state; the hooks are diagnostic-only and changed
no guest behavior.

Session 4101 completed the eight-site key-on early-return audit in one
control-first capture. The retail oracle whole-RDRAM positive control fired
and the retail log contained exact title and hangar target rows; the port also
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. In the port
hangar bucket, entry and normal-tail counts were both 4,383, the three
divide-witness sites that execute each had divisor `0xC0` and 4,383 rows, and
all eight early-return guard counts were zero. Slot transitions included
`02` (13) and `00` (5). The four alternating break-6 sites were not reached,
matching the valid divisor path. Together with the independent retail result
that all eight PCs are unreachable, this selects Hreturns-dead/Hguard-valid
for the measured route: no early return is implicated and none may be
removed or replaced. ORIGIN: the `0x80090768` publisher owns the legitimate
`0xC0` cmd-list divisor; the audit was diagnostic-only.

Session 4102 ran the M5 drain-tick A/B with the retail whole-RDRAM, title, and
hangar controls. The original stub -> tick-on -> tick-off order produced
`H-CoverageInvalid`: tick-on reached hangar with VI/task/SP/PCM controls but
the required `[drain-inloop-gate]` marker was absent, while tick-off crashed
before target phases at `spTaskSchedulerThread+9632` / guest PC `0x8000834c`.
The fixed reverse-order rerun removed that route failure: both tick-on and
tick-off reached title and hangar and had matching positive counts (VI 16,
ABI 1137/1129, SP 756/772, PCM source 88, consumer 518, lifecycle 1142/1136),
but both still had `gate=0` and remained unqualified. The binary contains
`[drain-tick]` but no `[drain-inloop-gate]` string, so the recipe's gate
predicate is stale and cannot discriminate policy. This is two-source evidence
for coverage invalidity (same-build port arms plus binary-string audit), not a
drain-policy result. ORIGIN: no guest behavior changed; only the recipe arm
order was made selectable to test schedule residue.

Session 4103 repaired the stale predicate in the existing recipe and reran the
same-build reverse-order A/B. The retail oracle passed all controls; both
image arms reached title and hangar with positive VI/task/SP/PCM/lifecycle
controls and two stage rows each. Each arm emitted one live `[drain-tick]`
row, both parsed as `gate=0x00`. Tick-on had ABI/SP/PCM-source/consumer
counts 1135/758/88/518; tick-off had 1131/756/88/518. The phase-5 join table
was not identical: tick-on and tick-off used different ordinals and event
ordering, while both still qualified. This selects HDrainChangesOrdering at
the measured scope: the injection changes audio lifecycle ordering without
being required for route reachability or the measured PCM joins. It does not
prove audible playback equivalence. Two evidence lines are the independent
retail controls and the paired qualified port arms. ORIGIN: the changed
predicate is diagnostic-only; no guest/runtime behavior changed.

Session 4104 built the ordinary Debug target successfully and queued a fresh
retail-grounded status-03 service-reaping capture. The recipe arms the retail
whole-RDRAM positive control, the complete physical voice-status range, the
status-03 publisher/republisher/worker/shutdown PCs, and the port's existing
phase-gated service and status instrumentation. It requires title and hangar
controls on both sides and kills both processes with SIGKILL. No guest or
runtime behavior changed; the worker/writer verdict is pending the queued soak.

Session 4105 consumed the status-03 service-reaping capture. The queued
recipe first failed because zsh did not provide `print`; after repairing the
output commands and the moved-script root path, the rerun passed the retail
whole-RDRAM positive control but the port crashed in
`spTaskSchedulerThread+9632` before title or hangar. The verdict was
`Hroute-invalid`; worker-entry, status-zero-writer, and shutdown-return nulls
are unevaluable. No force-clear or wait change is authorized.

Session 4106 rebuilt the ordinary Debug target and ran a same-build sequential
image/silent contract matrix after the retail whole-RDRAM positive control.
Retail reached title 1024 and hangar 512. The silent port arm reached both
target phases. The image arm produced repeated audio-stage (`dma_size=0x800`)
and scheduler/task rows, but stayed at VI 640 and reached neither target
phase; no crash or abort marker was present. The phase-gate source and the
independent task/stage source agree on an image-specific route failure, so
image downstream service, status, slot, and PCM nulls remain unevaluable.
This selects H-image-specific-failure at the measured route scope, not an
audio-degeneracy explanation. The default image arm remains unqualified, and
no status-03 or wait behavior changed.

Session 4107 added a regeneration-safe M3 ownership guard in
`patches/heap_guards.c`: `heap_bump` is rejected when it aliases the active
queue sentinel published through `heap_tail_loc`. The ORIGIN is the allocator
cursor publication versus the sentinel metadata owner; that alias is not
legitimate allocator state. The ordinary Debug target built successfully, but
`PatchesLib` remains unavailable (`No rule to make target 'PatchesLib'`) on
this host, so runtime qualification is still unevaluable.

## Next steps

Work only the first applicable item. This backlog is one monotonic sequence.

1. **M5 Step 1: isolate the image-arm route failure on a qualified
   phase-gated route.** Keep silent as the same-build route control and compare
   default declared-size image staging with the legacy `0xF80` image staging
   arm after the retail whole-RDRAM/title/hangar controls. Require the port
   phase gates before interpreting service, status-03, slot, DMA, or PCM
   nulls. Do not force-clear status 03 or change the wait.
2. **Qualify M3 patch integration (external dependency).** On a host with the MIPS toolchain, use
   the repaired discovery path to build `PatchesLib` and runtime-qualify the
   active-sentinel predecessor and allocator-cursor/sentinel guards. The source and ordinary host target
   already pass; do not infer runtime behavior from that build alone. This
   macOS host is blocked on installing/providing `mips64-elf-gcc` and
   `mips64-elf-ld` or using another host with them.
3. **M5 de-stubbing.** After the current route/source discriminator is closed,
   follow the incremental validation sequence in `M5-AUDIO-PLAN.md`; do not
   treat the silent control as real-audio evidence.
4. **Generated-symbol renaming sweep.** Parked while M5 has applicable route,
   writer, or audio work. Keep slug `generated-symbol-renaming-sweep` if it
   resumes; mapping-only edits do not reset the engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 producer absent | Hangar span closed as retail parity (s3820). Title AI producer is nonzero in retail and declared-real port (s4063); the isolated image arm still has zero hangar output. Session 4077 qualifies the port `0x80094648` store with retail-shaped nonzero values, so the missing boundary is downstream of that indexed writer. |
| M5 title host sink | Hplay selected (s4065): device 2 opens, host queue calls are positive, and drain depth advances without zero-starvation; s4066 native-SDL qualification is blocked by pre-target route failure, so device callback/output behavior remains open. |
| M5 clear is expected | Selected for clear witness `0x8008F2CC` writing object `0x801797B0`, length `0x298`. |
| M5 consumer disconnected | Selected at the measured task/output scope; upstream zero payload remains open. |
| M5 channel-span consumer | Hconsumer-live selected (s4078): retail reads the span and the port loads retail-shaped `0x7F` bytes at `0x8008D5E4` in title/hangar. |
| M5 voice modulation transform | Hlater-transform selected at s4091's first demonstrated boundary: the port `0x80084AB8` return values are the low 16 bits of `s0` after the source `andi`, and every sampled port value (`0`, `0xF00`, `0x1900`, `0x2000`, `0x3F80`) occurs in the qualified retail title/hangar support. The independent rows are not record-synchronized, so a later transform remains open. |
| M5 route failure | H-image-specific-failure selected at s4106's measured scope: silent reached both target phases, while the image arm emitted task/audio-stage rows but remained at VI 640. The cause is still open; image downstream nulls remain unevaluable. |
| M3 sentinel ownership | H1 selected at source/host-build scope; runtime unqualified. |
| M5 gate value | Selected at measured scope: retail gate writes were zero-byte pre-target activity. |
| M5 descriptor selector writer | Hport-writer-live selected (s4100): the port witness control fired in title/hangar and `0x80090AAC` produced rows with retail-matching selector values; `0x80090BA4` had no port rows. |
| M5 key-on early returns | Hreturns-dead/Hguard-valid selected (s4101): retail and port reached the measured key-on route with valid `0xC0` divisors, normal tails, and slot `02`/`00` transitions; all eight guard counts were zero. |
| M5 drain-tick policy | HDrainChangesOrdering selected at measured scope (s4103): both qualified image arms emitted one live `gate=0x00` tick row and matched route/PCM controls, but their phase-5 join ordering/ordinals differed. Tick injection is not required for reachability or measured PCM joins; audible equivalence remains unproven. |
| Generated symbol sweep | Parked until higher-priority M5/M3 work is inapplicable. |

## Durable evidence boundary

Retail reaches title/hangar and can attribute relevant writer PCs. The paired
port can reach image-DMA joins when its arm completes. The port task
`0x80171E70`, size 1, joins the exact input DMA at matching generations, but
payloads are zero; separate writeback joins are real. The s3891 image arm
proves the RSP task and two output-DMA edges execute; zero payload does not
identify the missing upstream writer.

The qualified consumer comparison used same-build declared/real,
declared/silent, and legacy/real arms. It found no declared-only post-`0x800`
marker and matching phase-5 zero-payload signatures. The candidate census is
qualified only through the latest completed class; route failure invalidates a
null, rather than proving absence.

The title playback/drain capture is independently controlled by the retail
whole-RDRAM and title/hangar AI-output witnesses. On the paired port, the
declared-real route reached both phase gates; host enqueue rows and raw drain
rows were positive in both phases. This closes immediate queue-drain
starvation at the measured SDL queue boundary, but does not prove that the
device callback delivers samples to an audible output.

## Superseded conclusions

The overlay/menu-only explanation, intrinsic VI-640 flakiness, missing-input
and wait-return explanations, global-zero image-DMA theory, route-wide PCM-gap
theory, and force-zero default policy are superseded at their measured
scopes. They were plausible before qualified routes, same-build controls, or
independent retail attribution existed.

The s4075 inference that the port did not reach the `0x80094648` store is
superseded by s4076's source audit. It was believable because the port had
entry/branch rows and no target-store rows, but the generated source contained
the store and the fixup had silently omitted the target-store witness.

The early s4009/s4010 staging-based route explanation is superseded by later
same-build route tables: launch order and timing change the qualifying arm,
but neither staging size nor real-audio mode is sufficient as a causal
explanation. The s3579–s3584 stored-value inference is unsupported because a
retail byte store was compared with an aligned word containing neighboring
bytes. Request-only SP-yield conclusions are limited to the old diagnostic
arm.

The s4088 conclusion that detail-hook transport remained open is superseded
by s4089: it was believable because the first positive control was attached
to an unqualified callsite, but moving it to `0x8008D604` fired the synthetic
row and exposed genuine detail rows.

## Durable operating rules

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and similar defenses are safety mechanisms, not explanations.
MusyX/MORT audio remains partially stubbed; MusyX data must not be sent to
stock `aspMain`.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget, and two evidence lines before its result becomes truth.
Phase-gate animated comparisons on VI transitions and batch A/B arms in one
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
Durable background migrated to `PROJECT-OVERVIEW.md`; detailed counts and
session-specific notes remain in `PORTING-STATE.md`.
