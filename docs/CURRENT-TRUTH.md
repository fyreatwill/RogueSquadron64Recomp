# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4077 (2026-10-06).

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
predecessor, and full free-chain/active-queue disjointness. The ordinary Debug
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

## Next steps

Work only the first applicable item. This backlog is one monotonic sequence.

1. **M5 Step 4 downstream boundary.** Use the qualified `0x80094648` store
   rows as the source-side anchor and identify the next phase-gated writer or
   transform that should carry its channel bytes into the image/PCM path.
   Require the retail whole-RDRAM/title/hangar controls plus a same-run port
   join; do not change the gate or add a mitigation from a port-only zero.
2. **Qualify M3 patch integration (external dependency).** On a host with the MIPS toolchain, use
   the repaired discovery path to build `PatchesLib` and runtime-qualify the
   active-sentinel predecessor guard. The source and ordinary host target
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
| M5 route failure | Hnative-residue supported at silent pre-target scope (s4072): clean dummy-only reached both phases, while s4069's native-first dummy arm failed and s4071's native-first dummy arm succeeded. Timing/resource sensitivity remains open; no sink inference is made. |
| M3 sentinel ownership | H1 selected at source/host-build scope; runtime unqualified. |
| M5 gate value | Selected at measured scope: retail gate writes were zero-byte pre-target activity. |
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
