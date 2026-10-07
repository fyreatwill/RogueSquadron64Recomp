# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4152 (2026-10-07).

Session 4152 qualified the caller-state join after a route-invalid first
attempt and a fixed two-second launch-stagger retry. Whole-RDRAM/title/hangar
controls passed. Retail `0x800078E0` rows used predecessor `0x800052C4` with
phase-keyed object/state fields and nonzero source words; the port's title
setup at `0x8008F2CC` used `s0=0xF`, `s1=0x561F`, destination `0x80178C80`,
length `0x298`, and zero fill. Hangar also included a shared-looking
`s0=0`, `s1=0x800D0000` tuple at `0x800AB694`. H-caller-state-split is
selected: the producer context differs by phase, not merely by callsite.
Generated port `ra=0` remains an instrument limitation. Evidence:
`docs/M5-S4152-CALLER-STATE-SPLIT.md`.

Session 4151 qualified the source-producer context join with the independent
retail oracle and one rebuilt port. Whole-RDRAM/title/hangar controls passed.
Retail's phase-qualified execution histogram attributed `0x800078EC` to the
`0x8002BEEC` predecessor family and `rs_memset` entry `0x800078E0` to
`0x800052C4`; the port's regeneration-safe rows used title callsite
`0x8008F2CC` and hangar callsites `0x8008F2CC`/`0x800AB694`, with distinct
argument tuples and zero values. H-producer-context-split is selected at this
boundary. Generated port `ra=0` remains an instrument limitation. Evidence:
`docs/M5-S4151-SOURCE-PRODUCER-CONTEXT-SPLIT.md`.

Session 4150 qualified the repaired setup/state join with the independent
retail oracle. The port and oracle both passed whole-RDRAM/title/hangar
controls. Port title setup matched retail's `s0=0x12`, `s1=0x561F`,
destination `0x801797B0`, length `0x298`; the dominant hangar setup matched
retail at `a0=0x80165E50`, `s0=0`, `s1=0x800D0000`, `t0=t1=4`, length `0xC`.
H-shared-source-state is selected at this setup boundary. The zero source
payload therefore remains open at the later `0x800078EC` producer/context
join. Evidence: `docs/M5-S4150-SOURCE-SETUP-SHARED.md`.

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) on the qualified real-audio/LLE/spin-yield route.
Hangar geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` is the
silent `Broke` control; real audio is not production-complete.

Session 4148 qualified the new source-construction callsite discriminator with
one rebuilt port/oracle pair. The retail oracle passed the whole-RDRAM control
and both target phase buckets, and its `0x800078EC` execution watch recorded
7,163,165 hits with predecessor `0x8002BEEC` present. The port reached title
and hangar and, after the regeneration-safe `s2240` annotation of all 88
`rs_memset` callsites, reported `0x8008F2CC` at title and `0x800AB694` at
hangar. H-retail-port-caller-split is selected: the direct port callsites do
not match the retail predecessor family. The generated `ra=0` remains an
instrument limitation. ORIGIN: the legitimate `rs_memset` callsites and
retail execution predecessor; the observed zero fill was not suppressed or
changed. Evidence: `docs/M5-S4148-SOURCE-CALLSITE.md`.

Session 4143 re-ran the A11 terminal-table capture with the independent retail
oracle and one rebuilt canonical real-audio/LLE/ungated/solo/spin-yield port.
Retail passed the whole-RDRAM positive control and recorded both title
`0x00790400/1024` and hangar `0x006AB400/512` phase buckets, including the
named slot/wait PCs. The port reached title at 46.0s but returned to 640 at
76.4s and crashed in `musyxSynthFrame+3828` before hangar; it emitted no
target-phase `wait-post-any-slot` row. H-route-invalid is selected for this
run, so the A11 writer/terminal relationship remains open and no wait, cap,
predicate, slot-state, or writeback change is authorized. ORIGIN: the
existing guest wait/slot readers and slot-status writers; no guest behavior or
mitigation changed. Evidence: `scratch/agent/s4143_a11_oracle.log` and
`scratch/agent/s4143_a11_port.log`.

The active M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are zero (`FNV=0x762B22A5`). Session 4112
qualified the exact source-span census: both declared and legacy port arms had
664 zero-valued guest stores from `0x800078EC` into
`0x178C80..0x178F18`, before their image reads; host `rsp_dmem_to_rdram`
writes to the same span were downstream zero writeback. Retail independently
reached both target phases and recorded nonzero source bytes plus the same
span's writer family. Hguest-zero-producer is selected at this boundary; no
nonzero port producer is established.

Session 4138 repaired the paired source-producer capture's oracle watch-index
table and qualified the discriminator in one rebuilt run. Retail passed the
whole-RDRAM control, title 1024, and hangar 512; its source-span watch at
index 1 recorded 664 stores, 72 nonzero post-value bytes, zero scalar-store
mismatches, and a hangar writer table with 29 PCs. The port reached title and
hangar with no crash or abort; its target-phase image rows remained zero for
the source and `0x1798B0` DMA payloads (1,854 and 1,841 rows respectively).
H-port-writer-context-split is selected at this measured boundary: retail's
phase-keyed source stores are nonzero while the qualified port payload remains
zero. The exact retail-to-port call-context join remains open. ORIGIN: retail
source-span guest stores and the port image-stage/DMA writer rows; no guest,
wait, cap, predicate, slot, or writeback behavior changed.

Session 4139 qualified the planned source-construction context discriminator
with one rebuilt port and retail oracle capture. Whole-RDRAM controls and both
title/hangar phase gates passed, and the new port marker fired in both target
phases. At title, retail's phase-gated writer execution had immediate caller
`0x800052C4`, source/destination `0x801BB9B0`, and length `0x88`; the port
writer had `ra=0`, source/destination `0x80178C80`, and length `0x298`, with
zero values. Retail's hangar tuple was also distinct (`0x8065E0A0`, length
`0x1C`), while the port used `0x80165E50`, length `0xC`. H-retail-port-caller-
split is selected at this first measured boundary. The port `ra=0` field is
not yet a valid caller attribution because the generated context does not
preserve a usable return register at this hook; it is an instrument
limitation, not a guest fact. ORIGIN: the guest `0x800078EC` store-loop
arguments and the retail oracle's previous-PC execution witness; no guest
behavior, wait, cap, predicate, slot state, or host writeback changed.
Evidence: `scratch/agent/s4140_m5_source_context/`.

Session 4140 retried the retail ground-truth preflight twice before using the
rebuilt source-context port arm. Both retail captures passed whole-RDRAM and
source-PC controls but remained at VI 640 through 75 and 90 seconds, so they
were route-invalid for the caller comparison. The port reached title 1024 at
13.5s and hangar 512 at 33.7s, firing its positive control and emitting 256
sampled zero-valued rows in each phase. Its title tuple was
`a0=0x80178C80`, `a2=0x298`, `ra=0`; hangar used `a0=0x801797B0`,
`a2=0x298`, `ra=0`. H-source-context-retry-route-invalid is selected for this
iteration only; the prior s4139 H-retail-port-caller-split remains qualified.
ORIGIN: the guest `0x800078EC` store loop and its entry tuple; no guest
behavior, wait, cap, predicate, slot state, or host writeback changed.
Evidence: `scratch/agent/s4140_port.log` and the two retail logs.

Session 4141 qualified the independent retail preflight with a live
whole-RDRAM control (12,240 writes), source-span writes (2,240), and nonempty
title/hangar phase buckets (633 title VI-1024 rows and 528 hangar VI-512 rows).
The rebuilt port arm first failed before title in `fillSampleStreamRange+8136`
at guest PC `0x8000B650`; a fixed retry reached title VI 1024 and emitted 256
source-context rows, but a 90-second retry crashed before hangar in
`fillSampleStreamRange+932` at the same guest PC. H-source-context-route-
invalid is selected for this iteration: the retail witness is qualified, but
the paired port caller tuple is unevaluable at hangar. The s4139 caller split
therefore remains the last qualified comparison. ORIGIN: the guest
`0x800078EC` source-construction/store boundary; no guest behavior, wait, cap,
predicate, slot state, or host writeback changed. Evidence:
`scratch/agent/s4141_m5_source_context/`.

The task-contract consumer boundary is closed at the measured scope: declared
and legacy real-audio arms reached both target phases with matching zero
payload consumer signatures, while the silent arm remained a valid control.
The old declared-size/legacy crash split is schedule-sensitive and is not an
audio-staging explanation. The legitimate legacy staging writer is still
`0xF80`; declared-size staging is `0x800`.

Session 4126 qualified the declared-versus-legacy audio staging A/B. On one
build, both canonical real-audio arms reached title and hangar with positive
task ABI/DMA, audio-return, PCM-source, and PCM-consumer controls and no
crash/abort. The declared arm staged `0x800`; the legacy arm staged `0xF80`
against the same declared `0x800`. Their downstream counts and zero payload
hashes matched at the measured scope. H-step3-equivalent is selected: the
declared-size staging path is a qualified no-regression result, not proof that
the legacy span is irrelevant outside this contract.

Session 4127 qualified the canonical real-audio/LLE/ungated/solo/spin-yield
route after the retail oracle positive control. The port reached title VI 1024
and hangar VI 512 with positive task handoff/return, PCM source/consumer, and
key-on controls, and no crash or abort. The target-phase wait table contained
one `waitForAnyAudioSlot` entry with `a3=0x8` followed by
`wait-post-any-slot`; the previously observed pending `chCount=16` call did
not recur. H-A11-not-reproduced is selected: the pending writer/terminal table
is unevaluable, not evidence that the wait is safe. No wait, cap, predicate,
slot state, or mitigation changed.

Session 4128 qualified the M5 Step 1 image-versus-silent contract checkpoint.
The retail oracle passed the whole-RDRAM control and reached title 1024 and
hangar 512. In the same rebuilt pair, the image arm reached both phases with
55 dispatches, 794 task ABI/DMA rows, 515 audio returns, 85 PCM-source rows,
and 515 PCM-consumer rows, with no crash or abort. A concurrent silent arm
crashed before title, so that null was rejected as route-invalid; the fixed
silent arm run alone reached both phases with 48 dispatches, 482 ABI/DMA rows,
277 returns, and no crash or abort. Its `musyx_stub` ABI rows had
`dmem changed=0`, no image-stage rows, and zero PCM payloads. Both arms'
phase-scoped PCM samples were the zero control (`FNV=0xF59C39C5`, `nz=0`).
H-contract-gap is selected at this measured boundary: the image task and
completion path are live, but the image does not produce a nonzero downstream
PCM payload relative to the silent control. This does not identify the source
writer or authorize a guest/host mitigation. ORIGIN: the next legitimate
writer boundary is the guest source-span producer at `0x800078EC` and its
caller context; no behavior changed.

Session 4129 ran the planned source-producer context census. The retail oracle
passed the whole-RDRAM positive control and reached title `0x00790400/1024`,
but did not reach hangar in either oracle invocation, so the retail/port
context comparison is route-invalid for this session. The rebuilt canonical
real-audio/LLE/ungated/solo/spin-yield port arm reached both title and hangar
with no crash or abort. Its phase-5 source-DMA context was stable across route
ordinals 644--676: `0x1797B0` length `0x38` had `FNV=0x9D4D4B25`, `nz=0`,
and `0x1798B0` length `0x198` had `FNV=0x762B22A5`, `nz=0`; host writeback
preserved both zero payloads. The guest producer positive control at
`0x800078EC` fired 664 stores overall, all observed values zero, and the run
had 294 audio returns with no crash/abort. H-route-invalid is selected for
this run only: the producer context remains unevaluable against retail, not
explained. ORIGIN: the measured writers are the guest `0x800078EC` store loop
and the image source-DMA path; no guest behavior, wait, predicate, cap, or
writeback mitigation changed.

Session 4130 reran the retail-gated source-producer census with a corrected
SIGKILL watchdog. The oracle whole-RDRAM positive control fired and reached
title (`0x00790800/1024`) and hangar (`0x006AB400/512`); the source PC watch
also fired with nonzero loop context. The oracle's requested post-value index
was malformed because execution and memory watches share one index namespace,
so those post-value rows are discarded rather than used as evidence. The
rebuilt canonical real-audio/LLE/ungated/solo/spin-yield port reached title
(`0x00790400/1024`) but crashed before hangar at 77.3s in
`musyxSynthFrame+3828` (guest PC `0x80001B08`). Its source-producer control
fired 664 stores, all zero, before the route phase. H-route-invalid is selected
for this run: the paired port context is unevaluable at hangar, so no retail
writer comparison or source explanation is established. ORIGIN: the measured
guest `0x800078EC` writer remains the legitimate boundary under test; no guest
writer, audio wait, cap, predicate, or writeback behavior changed.

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

Session 4146 added the missing allocator cursor/free-list ownership check to
`func_80007D74`. The patch now walks the bounded chain published by
`heap_free_head` and rejects `heap_bump` aliases both for a newly expanded
chain and before dequeue publication. ORIGIN: `heap_bump` is written as the
next allocation cursor, while free-list link stores own every reachable node;
an alias is not legitimate shared ownership. The ordinary Debug target
rebuilt successfully, while `PatchesLib` remains absent from this macOS CMake
graph (`No rule to make target PatchesLib`), so this is a landed static guard,
not runtime firing proof.

Session 4147 re-audited the cursor/free-list ownership class against the
checked-in patch and rebuilt the ordinary Debug target successfully. The
bounded `heap_free_head` walk rejects malformed/overlong chains and cursor
aliases before free-list dequeue publication. `PatchesLib` remains unavailable
in the configured macOS graph, so no runtime guard firing is claimed. The M3
runtime item is deferred until a host with the MIPS GCC/LD toolchain and a
configured target is available.

Session 4137 ran the prescribed M3 environment discriminator. `command -v`
found neither `mips64-elf-gcc` nor `mips64-elf-ld`, and
`cmake --build build --config Debug --target PatchesLib` failed with
`No rule to make target PatchesLib`. H-m3-toolchain-absent and
H-m3-target-missing are selected; no runtime guard behavior is inferred from
the ordinary host target. ORIGIN: the tested boundary is the configured
`PatchesLib` target and its MIPS GCC/LD dependency; no allocator writer,
guard, or runtime behavior changed.

Session 4125 completed the remaining cursor/active-queue alias idiom at the
checked-in patch boundary. `func_80007D74` now walks the bounded active queue
and rejects `heap_bump` when it aliases any active node, before the append
stores publish another allocation. The ORIGIN is the allocator's
`heap_bump` writer together with the active-queue link publishers; such an
alias is not legitimate ownership state. The ordinary Debug target rebuilt
successfully. This is a static ownership guard audit, not runtime proof that
the alias occurs; M3 runtime qualification remains blocked by the absent MIPS
GCC/LD toolchain.

The title host-sink boundary is closed on the schedule-gated declared-real
route. Retail passed the whole-RDRAM positive control and both target phases;
the port reached title and hangar with nonzero consumer PCM. In both phases
the host opened device 2 and recorded positive `call_delta`/`queued_after`
rows. This rules out device-open failure and zero enqueue at the measured
boundary; playback/drain timing remains open.

Session 4131 reran the retail-gated source-producer census with one Debug
build and the full phase-scoped probe matrix. Retail passed the whole-RDRAM
control, reached title `1024` and hangar `512`, and executed the watched
producer PC overall; this invocation did not include the required phase-keyed
PC join, so it provides no target-phase writer rows. The first canonical port
launch crashed in `fillSampleStreamRange` during 640 before either target
phase. The corrected validated Start schedule then remained in 640 for 78
seconds with no title or hangar gate and was SIGKILLed. H-route-invalid is
selected for this iteration: the retail writer/context comparison is
unevaluable and no source producer, image, wait, predicate, or writeback
explanation is authorized. ORIGIN: the only boundary under test remains the
guest `0x800078EC` writer and its source span; no guest behavior or mitigation
changed.

Session 4132 landed a regeneration-safe M3 ownership guard in
`patches/heap_guards.c`. Before advancing `heap_free_head`, the patch now
rejects any overlap between the published free-list chain and the active
queue, whose legitimate owners are the allocator's free-list link stores and
active-queue link publishers. The `PatchesLib` target is absent from this
macOS CMake configuration, so that target could not be built; the ordinary
Debug target rebuilt successfully. H-guard-not-integrated is selected for
runtime purposes: this proves source/host integration only, not that the guard
fires or preserves a valid runtime path. ORIGIN: free-list head publication
and active-queue link stores; cross-owner aliasing is not legitimate state.

Session 4133 repeated the prescribed integration discriminator without changing
the guard. `cmake --build build --config Debug --target PatchesLib` failed
immediately with `No rule to make target PatchesLib`, while the same configured
build completed `RogueSquadron64Recomp` successfully. H-guard-not-integrated
remains selected: the ordinary host target is buildable, but this checkout's
macOS CMake graph cannot compile or link the MIPS patch library, so no runtime
guard firing or valid-path preservation is claimed. This closes the current
build-only probe and does not authorize another host-only guard iteration.
ORIGIN: the tested integration boundary is the configured `PatchesLib` target
and its MIPS GCC/LD dependency; no allocator writer, guard, or runtime behavior
changed.

Session 4134 attempted the M5 status-03 worker qualification. The live external
generated tree lacked the s2008/s2007 anchors required by the existing s2028
fixup; the measured failure was `funcs_26.c s2028 helper anchor count=0`.
The compatible s2022 service branch/loop/store and shutdown-ordinal census
applied and the Debug target rebuilt successfully. The silent port fired the
service positive-control rows in VI 640 but never reached title 1024 or hangar
512 before SIGKILL. H-status03-route-invalid is selected; no writer ordering or
status-03 conclusion is allowed. ORIGIN: the named guest writer remains
`serviceVoicePoolFrame` at `0x8009B7EC`; no wait replacement, force-clear,
guard, or guest behavior changed.

Session 4135 repaired the regeneration-safe s2028 worker/status fixup for the
live generated tree: it now falls back from absent s2007/s2008 anchors to the
existing s2020/s2022 service and shutdown anchors. The Debug target rebuilt
successfully. The retail-gated silent port route qualified title 1024 and
hangar 512 with no crash or abort. The phase-scoped table emitted 9,881
service-entry rows, 9,881 service-exit rows, one `0x8009B7EC` service-store
row (`old=0x03`, `new=0`, phase 5, event sequence 2647), and one shutdown
entry/return pair in phase 4 (sequences 1007/1008). The observed store is
after that shutdown return in this event stream, so H-status03-store-after-
return is selected; the before-return worker contract is not demonstrated.
This ordering result is single-source port evidence pending an independent
retail or second-route join. No wait, force-clear, status guard, or guest
behavior changed. ORIGIN: the legitimate status writer is the guest store at
`0x8009B7EC`; the observed `03 -> 00` value is legitimate reaping state.

Session 4136 refreshed the regeneration-safe s2028 helper so its single global
join field is explicitly named `event_seq`, then rebuilt and reran the same
retail-gated silent route. Retail passed the whole-RDRAM control and both target
phases; the port passed title 1024 and hangar 512 with no crash or abort. The
qualified port stream placed the phase-5 service entry at `event_seq=2637`, the
status-03 read at 2638, the `0x8009B7EC` `03 -> 00` store at 2639, and service
exit at 2640. The phase-4 shutdown return was 1000. H-status03-after-return is
selected: the store is inside a later service call, not before the observed
shutdown return. This remains single-source port ordering evidence; no wait,
force-clear, status guard, or guest behavior changed. ORIGIN: the legitimate
writer is the guest `0x8009B7EC` store and its service worker; the observed
`03 -> 00` reaping value is legitimate.

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

Session 4144 requalified the source-construction predecessor route after the
retail preflight passed its whole-RDRAM control (12,138 writes) and both target
phase buckets. Retail's exact `0x800078EC` witness used title
`a0=0x801B08A0, a2=0x1C` and hangar `a0=0x8065E0A0, a2=0x1C`; the canonical
port reached title and hangar with its positive source-context controls but
used title `a0=0x80178C80, a2=0x298` and hangar `a0=0x801797B0, a2=0x298`, all
zero-valued. H-source-context-split is selected at this measured boundary.
The port's generated hook still reports `ra=0`, so caller attribution remains
unevaluable; this is an instrument limitation, not a guest fact. ORIGIN: the
legitimate guest `0x800078EC` source-construction store loop and the retail
oracle's previous-PC/GPR witness; no guest behavior, audio wait, cap,
predicate, slot state, or host writeback changed. The first PC-range oracle
attempt generated an unusable 3.2 GB log; the fixed exact-PC run is the
selected evidence. Evidence: `scratch/agent/s4144_retail_fixed.log` and
`scratch/agent/s4144_port.log`.

Session 4145 re-ran the planned A11 terminal table with one ordinary Debug
build, the independent retail oracle, and the canonical real-audio/LLE/
ungated/solo/spin-yield port. The oracle passed the whole-RDRAM positive
control and reached title 1024 and hangar 512; the port reached the same two
phase gates with no crash or abort. The port emitted A11 wait/post-wait rows
only in earlier width-640 phases; it emitted no target-phase rows at title or
hangar. The retail watched A11 PCs also fired overall, but no target-phase
terminal row was present. H-A11-target-phase-absent-both is selected: this
capture rules out a target-phase port-versus-retail terminal split, but does
not establish that the wait is safe or explain the source payload. ORIGIN:
the existing guest `waitForAnyAudioSlot`/`anyAudioSlotActive` reads and slot
writers; no wait, cap, predicate, slot state, or writeback behavior changed.
Evidence: `scratch/agent/s4145_m5_a11_terminal/`.

## Next steps

Work only the first applicable item. This backlog is one monotonic sequence.

1. **M5 producer object/body join:** use the qualified caller-state split to
   add one retail-oracle `--pc-field-dump` arm for `0x800078EC` alongside
   `0x800078E0`, phase-gated at title `0x00790400/1024` and hangar
   `0x006AB400/512`. Compare the bounded `s0/s1` and pointed-field rows at
   entry/body against the port's existing setup/store rows in one paired
   capture. Retain the whole-RDRAM control and both target phases; do not
   change guest behavior, audio waits, caps, predicates, slot state, or
   writeback, and do not use generated port `ra=0` as caller evidence.
2. **M3 pre-publication guard runtime qualification** remains blocked on a host
   with `mips64-elf-gcc`/`mips64-elf-ld` and a configured `PatchesLib` target;
   do not spend another host-only iteration.
3. **Generated-symbol renaming sweep.** Parked while M5 has applicable route,
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
| M5 source setup state | H-shared-source-state selected at s4150: independent retail and port setup tuples matched for the title clear and dominant hangar source-construction calls. The setup boundary is not the explanation for the later zero `0x800078EC` producer payload. |
| M3 sentinel ownership | H1 selected at source/host-build scope; runtime unqualified. |
| M5 gate value | Selected at measured scope: retail gate writes were zero-byte pre-target activity. |
| M5 descriptor selector writer | Hport-writer-live selected (s4100): the port witness control fired in title/hangar and `0x80090AAC` produced rows with retail-matching selector values; `0x80090BA4` had no port rows. |
| M5 key-on early returns | Hreturns-dead/Hguard-valid selected (s4101): retail and port reached the measured key-on route with valid `0xC0` divisors, normal tails, and slot `02`/`00` transitions; all eight guard counts were zero. |
| M5 drain-tick policy | HDrainChangesOrdering remains qualified (s4103, independently requalified s4114). Session 4113's reverse-order rerun was Hroute-invalid because tick-off crashed pre-target; s4114 qualified both arms and again found differing joined stage/route-context tables. This does not establish tick-required behavior. |
| M5 status-03 reaping | Hstatus03-chain-live remains the retail/port reachability boundary. Session 4136's qualified single-source port join selected H-status03-after-return: service entry 2637, status read 2638, store 2639, service exit 2640; the observed phase-4 shutdown return was 1000. The writer is live but the store is not before that shutdown return; no force-clear or wait change is authorized. |
| M5 A10 voice/list/table guards | H-A10-not-suppressing-valid-work selected at s4119's measured scope: retail's independent `0x80096D88` writer reached the target table root (371 hangar writes), while the qualified port reached both phases with valid traversal/table rows and zero A10 guard fires. No guard relaxation is authorized. |
| M5 A9 voice-array-base guards | H-A9-legitimate selected at s4120's measured scope: retail reached the allocator writer and 10/12 A9 PCs in hangar; the qualified port reached both phases with positive controls and zero fires at all 12 A9 guards. No guard relaxation is authorized. |
| M5 A8 key-on divide/overflow traps | H-A8-trap-live selected at s4121's measured scope: retail and qualified port both reached title/hangar with positive controls; retail hit none of the eight trap PCs, and port recorded zero guards, normal-tail progress, divisor `0xC0`, and slot `0x02`/`0x00` transitions. No trap change is authorized. |
| M5 A11 wait terminal transition | H-A11-target-phase-absent-both selected at s4145: both qualified arms passed whole-RDRAM/title/hangar controls, but neither emitted a target-phase wait/post-wait terminal row; port A11 rows were confined to earlier 640 phases. This rules out a target-phase port/retail split, not the wait's safety or the source-payload cause. |
| M5 Step 1 task contract | H-contract-gap selected at s4128: the image arm reached title/hangar with task ABI/DMA, image completion, and PCM rows, while the fixed silent control reached both phases with `dmem changed=0`; both arms' measured PCM payloads remained zero. The next boundary is source-producer context, not a task-return or host-queue mitigation. |
| M5 source-producer context | H-producer-context-split selected at s4151: retail's phase-qualified execution histogram attributed `0x800078EC` to predecessor `0x8002BEEC` and `rs_memset` entry `0x800078E0` to `0x800052C4`, while the port used title callsite `0x8008F2CC` and hangar callsites `0x8008F2CC`/`0x800AB694` with distinct tuples and zero values. The caller-state cause remains open; generated port `ra=0` is not evidence. |
| M5 producer caller state | H-caller-state-split selected at s4152: retail title entry rows had `prev=0x800052C4`, live `s0` objects and nonzero pointed words, while port title setup used `s0=0xF`, `s1=0x561F`, `0x80178C80/0x298`, and zero fill. Hangar includes a shared-looking `s0=0`, `s1=0x800D0000` family, so the split is phase/context-specific. |
| M5 Step 3 declared audio staging | H-step3-equivalent selected at s4126: qualified declared `0x800` and legacy `0xF80` arms both reached title/hangar with matching task, return, PCM, and route signatures; only the staging size differed. The legacy path is not needed for this measured no-regression contract, but semantic irrelevance outside it is unproven. |
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

The s4149 setup/state route-invalid conclusion is superseded by s4150: it was
believable because the concurrent port stayed at VI 640, but the repaired
route-stable capture reached both target phases and independently matched the
retail setup tuples. The setup boundary remains open only as a causal null.

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
