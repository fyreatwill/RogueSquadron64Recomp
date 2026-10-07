# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4123 (2026-10-07).

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) on the qualified real-audio/LLE/spin-yield route.
Hangar geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` is the
silent `Broke` control; real audio is not production-complete.

The active M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are zero (`FNV=0x762B22A5`). Session 4112
qualified the exact source-span census: both declared and legacy port arms had
664 zero-valued guest stores from `0x800078EC` into
`0x178C80..0x178F18`, before their image reads; host `rsp_dmem_to_rdram`
writes to the same span were downstream zero writeback. Retail independently
reached both target phases and recorded nonzero source bytes plus the same
span's writer family. Hguest-zero-producer is selected at this boundary; no
nonzero port producer is established.

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

## Earlier qualified evidence (compacted)

Sessions before 4110 established these durable boundaries: the native LLE route reaches attribution, logo, cinematic, title, and hangar phase gates; route qualification is schedule-sensitive, so missing phases invalidate nulls. Retail controls require whole-RDRAM activity plus title 1024 and hangar 512 transitions.

M5 audio work closed title AI production, host enqueue, and raw drain starvation at its measured boundaries. Retail and qualified port arms produced phase-scoped PCM, opened device 2, queued samples, and advanced drain depth. Device callback/output delivery remains unproven.

M5 image work moved from stage/writeback suspicion to the source span 0x178C80..0x178F18: qualified port arms enter the image path with zero bytes, while retail records nonzero bytes. The exact port-side zero producer is 0x800078EC; host writeback is downstream.

M5 route permutations repeatedly showed topology and launch-order sensitivity. Silent arms can qualify where real/image arms crash in spTaskSchedulerThread+9632 at guest PC 0x8000834C; such failures are Hroute-invalid for source and guard nulls.

M3 audits added regeneration-safe ownership guards for free/active chains, sentinel/cursor aliases, predecessor state, and expansion ownership. Ordinary host builds pass, but runtime qualification is blocked by the absent MIPS GCC/LD toolchain.

Session 4119 completed the A10 voice/list/table guard audit. The generated
source census contains 43 song-tempo table-pointer guards in `funcs_25.c` and
one voice-list-node guard in `funcs_26.c`. The retail oracle passed the
whole-RDRAM control, reached title and hangar, and wrote the shared table root
`0x801529C0` 2,542 times overall and 371 times in hangar from guest PC
`0x80096D88`. The qualified port reached title and hangar, passed the audit's
positive control, and emitted 226 valid-range traversal rows plus 30 indexed
table rows; neither A10 guard fired. H-A10-not-suppressing-valid-work is
selected at this scope. This closes guard firing, not every possible audio
cause, and no guard or writer behavior changed.

Session 4120 completed the A9 voice-array-base guard census. The generated
source contains 12 sites in `funcs_24.c`: loop sites `0x80090E78` and
`0x800913BC`, plus ten entry sites from `0x80092138` through `0x80092568`.
The retail oracle passed the whole-RDRAM control and reached title and hangar;
the allocator writer at `0x8008F0EC` executed in hangar, and retail executed
10 of 12 A9 PCs in hangar (the two remaining sites were overall-only). The
qualified real-audio/LLE/ungated/solo/spin-yield port reached both target VIs,
fired the filter and init-voice positive controls, and recorded zero fires at
all 12 A9 guards. H-A9-legitimate is selected at this measured scope: no
valid port work was suppressed by the guards, and no guard relaxation is
authorized. The first two port attempts were route-invalid (one pre-title
crash and one 640 stall) and were not used as A9 evidence. ORIGIN: the
legitimate voice-array publisher is `allocateSongChannelArray` at
`0x8008F0EC`; no mitigation or guest behavior changed.

Session 4121 completed the A8 key-on divide/overflow census. The independent
retail oracle passed the whole-RDRAM positive control, reached title
`0x00790400/1024` and hangar `0x006AB400/512`, executed the divisor publisher
at `0x80090768` 66,943 times, and executed none of the eight trap PCs. The
same-build qualified real-audio/LLE/ungated/solo/spin-yield port also passed
all controls and both target phases. Its phase-5 census reached
`entry=17,262`, `normal_tail=17,262`, zero guards at all eight sites, and
active divide sites at `0x80090CEC`, `0x80090D30`, `0x80090D74`, and
`0x80090DB8` with divisor `0xC0`; slot `0x02` and `0x00` transitions fired.
H-A8-trap-live is selected at this measured scope: the traps did not suppress
valid qualified work. ORIGIN: `0x80090768` is the legitimate `0xC0` divisor
publisher; no trap or guest behavior changed.

Session 4122 completed the A11 wait-for-any-audio-slot capture. The retail
oracle passed the whole-RDRAM positive control and reached title
`0x00790400/1024` and hangar `0x006AB400/512`, but this driven schedule did not
execute the wait/active-slot PCs; earlier independent retail evidence still
shows the wait and active-slot callee are real. The same-build qualified
real-audio/LLE/ungated/solo/spin-yield port reached both target phases with
positive audio-task and return controls. Port A11 entered three times: calls 0
and 2 returned after one iteration, while call 1 entered with `chCount=16` and
had no return before SIGKILL. The wait cap and audio-slot-active guard both
fired zero times. H-A11-nonterminal-return is selected at this measured port
scope; the wait class is live but not every qualified call reaches a terminal
return. This does not authorize removing the cap, replacing the wait, or
changing slot state. ORIGIN: the observed pending path is the existing guest
`waitForAnyAudioSlot` loop and its slot predicate; no guest writer or
mitigation changed.

Session 4123 attempted the required A11 terminal-transition table after first
running the retail oracle. Retail passed the whole-RDRAM positive control and
reached title `0x00790400/1024` and hangar `0x006AB400/512`; independent
wait/active-slot execution witnesses were live, although the wait entry itself
was not target-phase-driven in this schedule. The first same-build port launch
was route-invalid: it crashed in RT64 `copyToRAM` during 640 before title.
The fixed real-audio/LLE/ungated/solo/spin-yield launch reached title 1024 and
recorded real audio dispatch plus `waitForAnyAudioSlot` caller rows, but did
not reach the required hangar 512 phase before SIGKILL. A 120-second retry
again reached title and then returned to 640 without a hangar phase. The A11
writer/terminal table therefore remains unevaluable; H-A11-route-invalid is
selected for this iteration. This does not select a slot predicate or permit
changing the wait/cap. ORIGIN: no guest writer, wait, force-clear, or
mitigation changed.

Session 4124 reran the retail oracle first: the whole-RDRAM positive control
fired, and retail reached title `0x00790400/1024` and hangar
`0x006AB400/512`. The rebuilt canonical real-audio/LLE/ungated/solo/spin-yield
port route also reached both phases, dispatched real audio, returned 516 audio
tasks, and had no crash or abort. Its phase-4 A11 table recorded one
`waitForAnyAudioSlot` entry with `wait-post-any-slot`; no cap or active-slot
guard fired. The earlier pending `chCount=16` call did not recur, and hangar
had only status reads of `slot0=01, slot1=00, slot2=00`. H-A11-route-invalid is
rejected for this run, but the terminal-transition table for the absent pending
call remains unevaluable. This is a qualified non-reproduction, not evidence
that the pending call is safe or that a slot writer is irrelevant. ORIGIN: the
existing guest wait/predicate and slot-status writers were observed; no guest
writer, wait, cap, force-clear, or mitigation changed.

Generated-tree audits confirmed the relevant service and image functions exist outside this checkout and in the fixup inputs. Guard changes require an ORIGIN naming the legitimate writer; no force-clear, wait replacement, synthetic DMA, or default-on mitigation was authorized.

The preceding session-specific details remain in PORTING-STATE.md; only evidence that changes the current decision boundary belongs in this compact file.

Session 4110 asked the retail oracle before building the next probe. The
whole-RDRAM positive control fired with 111,644 writes and retail reached title
`0x00790400/1024` and hangar `0x006AB400/512`. Retail wrote the physical image
input/working span `0x178C80..0x178F18` 664 times and its hangar snapshot had
24 nonzero bytes; stage storage `0x166000..0x168000` and descriptor storage
were also active. The existing regeneration-safe image-stage probe was then
run in one same-build declared-size/legacy-size matrix. Both arms reached both
target VIs with positive stage/task/PCM controls and no crash or abort. In
both arms, hangar stage 0 (`DMEM 0xCC0`) was zero; stage 1 remained zero, stage
2 output/writeback was zero, and stage 3 retained `FNV=0x762B22A5`, `nz=0`.
Hpreimage-zero is selected at the qualified port boundary: retail's
independent nonzero input witness and the port's zero stage-0 witness place
the first measured zero before the transform. This rules out transform-stage
and writeback as the first zero boundary, but does not identify the port-side
source DMA or producer. ORIGIN: the legitimate writer to investigate is the
image input/source-DMA path; no skip, force-clear, or guest behavior changed.

Session 4111 corrected the port DMA witness to the full input span and reran
the same-build declared-size/legacy-size matrix with the all-DMA positive
control. Both arms reached title 1024 and hangar 512, produced positive
task/stage/PCM controls, and had no crash or abort. Their image-input pointer
was `0x80178C80`; direct reads covering `0x178C80..0x178F18` were zero
(`FNV=0xE6A1D1C5`, `nz=0` for the `0x100` read and
`FNV=0x762B22A5`, `nz=0` for the `0x198` read), matching the zero stage-0
snapshot. The all-DMA census showed no transfer into `DMEM 0xCC0`; stage 0
was entered with `field348=0x80178C80` and `source_event=0`, so the assumed
CC0 source-DMA edge is not the actual path. H-source-zero is selected at the
qualified port source boundary over H-DMA-zero; valid task/stage joins and
matching declared/legacy results rule out H-route-misjoin at this scope.
The fresh retail rerun passed its whole-RDRAM control but hit an unsupported
uCode before target VIs, so retail nonzero remains the prior independent
s4110 qualification, not this failed fresh route. ORIGIN: the legitimate
writer to investigate is the producer of the port's `0x178C80..0x178F18`
RDRAM source span; no mitigation or guest behavior changed.

Session 4112 asked the retail oracle first with the whole-RDRAM positive
control, the exact physical source-span watch, and title/hangar phase gates.
The control fired with 11,717 writes; retail reached title 1024 and hangar
512, and the span recorded 1,717 writes with a final 77/664 nonzero snapshot
(`FNV=0x215A7BAD`). The retail writer census named `0x800078EC` as the
dominant span writer (664 stores), with additional pre-target writer PCs.

Widened the regeneration-safe port guest-store witness to the qualified full
span and added that span to the host-copy census, then rebuilt once. The same
build's declared and legacy image arms both reached title and hangar with
positive task/stage/PCM controls and no crash or abort. Each arm recorded 664
zero guest stores from `0x800078EC`; each also recorded host
`rsp_dmem_to_rdram` writes whose post-span remained zero, but those writes
followed the source reads. The paired input DMA rows read zero from the span
before stage 0. Hguest-zero-producer is selected over Hhost-producer and
Hproducer-absent at this measured boundary. ORIGIN: the legitimate writer is
the guest byte-fill at `0x800078EC`; the host writeback is downstream and no
mitigation, force-clear, or synthetic DMA was added.

Session 4113 reran the Step 6 drain-tick A/B with the retail oracle positive
control and the existing reverse-order sequential harness. Retail passed all
whole-RDRAM, title/hangar, status, slot, and writer controls. The explicit
tick-on arm reached title and hangar with 1113 ABI rows, 754 SP receives, 88
nonzero source rows, 518 consumer rows, and one live tick row. The default
tick-off arm crashed in `spTaskSchedulerThread+9632` at guest PC
`0x8000834C` before title or audio-task dispatch, so it has no valid
phase-scoped comparison. This is Hroute-invalid for Step 6, not evidence that
the tick is required. The same-build concurrent diagnostic retry also showed
topology-sensitive divergence and is not promoted to truth.

Session 4114 reran the same-build Step 6 A/B with the retail whole-RDRAM,
title, and hangar controls valid. Both real-audio arms reached title and
hangar with no crash/abort, 16 VI controls, 88 PCM-source rows, 518
PCM-consumer rows, and two qualified hangar stages. Tick-on had 738
guest-receive rows and tick-off had 741; their joined stage/route-context
tables differed, so the harness selected H-DrainChangesOrdering. This
independently requalifies the existing Step 6 policy result; it does not
prove the tick is required or change runtime behavior.

Session 4115 ran the required status-03 worker inventory over the tracked
source, tools, and scratch/fixup tree. It found no implementation or probe
definition for `serviceVoicePoolFrame`, `stopVoiceSlotSynced`, status-03,
or `0x8009B7EC`; only the symbol-table names and runtime registration remain
in this checkout. The earlier qualified port artifact remains the only
runtime evidence for the worker/store chain, and the generated game tree or
its fixup is external/absent here. This leaves the current source inventory
unresolved/generated-only and does not qualify a new run or authorize a wait
or force-clear change. ORIGIN: no guest writer or mitigation was changed.

Session 4116 ran the required generated-tree/fixup boundary check. The external
`N64Recomp/RecompiledFuncs` tree, `fixup_game_funcs.py`, and the exact
`0x8009B7EC` witness are present; the ordinary Debug target rebuilt cleanly.
The retail positive control and both retail phase gates passed. The silent
port arm reached title and hangar, but the real-audio/image arm failed before
title in `spTaskSchedulerThread+9632` at guest PC `0x8000834C`; no image-arm
status-03 rows are therefore valid. The generated inputs are present, so
H-generated-absent is rejected; the status-03 worker/store chain remains
unqualified and needs a silent-arm phase-gated capture. ORIGIN: no guest
writer, wait, force-clear, or mitigation was changed.

Session 4117 ran the prescribed retail-gated silent-arm capture. The oracle
whole-RDRAM control and retail title/hangar transitions passed; the silent port
also reached title `0x00790400/1024` and hangar `0x006AB400/512`. In the port,
phase-5 status-03 service rows contained repeated entry/exit pairs. Retail's
independent PC watch fired at `0x8009B7EC` four times and at the surrounding
worker PCs, including `0x8009B30C`, `0x8009B7CC`, `0x8009B600`, `0x8009BDE8`,
and `0x8009BCF8`. Hstatus03-chain-live is selected at the measured scope:
worker/service activity and the named zeroing-store execution are real, so no
wait replacement or force-clear is authorized. The exact port-side store-to-
return join remains a diagnostic detail, not a reason to alter behavior.

## Next steps

Work only the first applicable item. This backlog is one monotonic sequence.

1. **M5 Step 3 validation:** run the declared-size versus legacy-size audio
   staging A/B in one build, using the canonical AUTOPILOT and phase-gated
   route. Require task dispatch/exit, SP completion, image-stage/DMA joins,
   slot/service, PCM, and title/hangar controls in both arms. Do not infer a
   cause from matching zero payloads; this validates or rejects the staging
   behavior change as a de-stubbing step.
2. **M5 A11 recurrence capture:** interpret the complete slot `01/02/00`
   writer and terminal table only when the pending `chCount=16` call appears
   on a qualified route. Keep the cap and wait unchanged.
3. **Qualify M3 patch integration (external dependency).** On a host with the MIPS toolchain, use
   the repaired discovery path to build `PatchesLib` and runtime-qualify the
   active-sentinel predecessor and allocator-cursor/sentinel guards. The source and ordinary host target
   already pass; do not infer runtime behavior from that build alone. This
   macOS host is blocked on installing/providing `mips64-elf-gcc` and
   `mips64-elf-ld` or using another host with them.
4. **M5 de-stubbing.** After the current route/source discriminator is closed,
   follow the incremental validation sequence in `M5-AUDIO-PLAN.md`; do not
   treat the silent control as real-audio evidence.
5. **Generated-symbol renaming sweep.** Parked while M5 has applicable route,
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
| M5 route failure | H-image-specific-failure remains selected at s4116's measured scope: the silent arm reached title/hangar, while the real-audio/image arm crashed pre-title in `spTaskSchedulerThread+9632`; the image arm's status/source nulls are unevaluable. Earlier declared/legacy image qualifications remain valid for their own schedules. |
| M5 image zero boundary | Hguest-zero-producer selected at s4112: both qualified port arms recorded 664 zero-valued `0x800078EC` stores into `0x178C80..0x178F18` before the zero input reads; host `rsp_dmem_to_rdram` writes were downstream zero writeback. Retail independently reached both phases and recorded nonzero span bytes. |
| M3 sentinel ownership | H1 selected at source/host-build scope; runtime unqualified. |
| M5 gate value | Selected at measured scope: retail gate writes were zero-byte pre-target activity. |
| M5 descriptor selector writer | Hport-writer-live selected (s4100): the port witness control fired in title/hangar and `0x80090AAC` produced rows with retail-matching selector values; `0x80090BA4` had no port rows. |
| M5 key-on early returns | Hreturns-dead/Hguard-valid selected (s4101): retail and port reached the measured key-on route with valid `0xC0` divisors, normal tails, and slot `02`/`00` transitions; all eight guard counts were zero. |
| M5 drain-tick policy | HDrainChangesOrdering remains qualified (s4103, independently requalified s4114). Session 4113's reverse-order rerun was Hroute-invalid because tick-off crashed pre-target; s4114 qualified both arms and again found differing joined stage/route-context tables. This does not establish tick-required behavior. |
| M5 status-03 reaping | Hstatus03-chain-live selected at s4117's measured scope: silent port reached both phases with repeated service entry/exit pairs, and retail independently executed the named `0x8009B7EC` zeroing-store PC plus surrounding worker PCs. Exact port-side store-to-return synchronization remains diagnostic; no force-clear or wait change is authorized. |
| M5 A10 voice/list/table guards | H-A10-not-suppressing-valid-work selected at s4119's measured scope: retail's independent `0x80096D88` writer reached the target table root (371 hangar writes), while the qualified port reached both phases with valid traversal/table rows and zero A10 guard fires. No guard relaxation is authorized. |
| M5 A9 voice-array-base guards | H-A9-legitimate selected at s4120's measured scope: retail reached the allocator writer and 10/12 A9 PCs in hangar; the qualified port reached both phases with positive controls and zero fires at all 12 A9 guards. No guard relaxation is authorized. |
| M5 A8 key-on divide/overflow traps | H-A8-trap-live selected at s4121's measured scope: retail and qualified port both reached title/hangar with positive controls; retail hit none of the eight trap PCs, and port recorded zero guards, normal-tail progress, divisor `0xC0`, and slot `0x02`/`0x00` transitions. No trap change is authorized. |
| M5 A11 wait terminal transition | H-A11-route-invalid is rejected by s4124's qualified canonical route. The run cleanly returned from one wait call but did not reproduce s4122's pending `chCount=16` call; the pending writer/terminal relationship remains open. |
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
