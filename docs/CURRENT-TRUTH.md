# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4194 (2026-10-07).

Session 4192: M5 A12 de-stub landed. The countdown wait at `0x8014998A` now defaults to a yielding spin (`ROGUESQ_AUDIO_WAIT_NOPUMP` unset = mode 2): the real producer takes the countdown 16 -> 0 in ~200 x 1 ms yields and title/hangar are reached. The old musyxSynthFrame pump left the countdown at 16 (64-pump ceiling, stall row every wait) - it was a silent skip, so the s327 "only decrementer" justification is superseded. `=0` restores the pump, `=1` the deadlocking blind spin (control). Pre-wait width-320 segfault (`si_addr=0x400128d47`) seen in 2 of 6 arm-runs, unrelated. See PORTING-STATE s4192.

Session 4191: caller continuation `0x8008F4C0` (after `jal 0x8008F858`) matched retail in the hangar on v0/v1/a0/a2/s0/s1/s2; title row lost to oracle hit cap (port-only). initSampleStreamBlockCache object path is register-parity clean entry-to-return; no divergence found, so stop parity qualification and take the next M5 de-stub step.

Session 4190: hangar caller-continuation `0x8008F8A8` (return from `rs_malloc`) matched retail on v0/v1/s0/s1/s2; `ra` differs by native-call convention only. Oracle `--watch-pc` never fires on the `jr` delay slot `0x8008F958` (0 hits despite the matched store), so the retail return is unpaired; next watch the caller continuation `0x8008F4C0`.

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and
hangar VI 512 (`0x006AB400`) on the qualified real-audio/LLE/ungated/solo/
spin-yield route. Hangar geometry and color artifacts remain. The real audio
path is not production-complete; `ROGUESQ_AUDIO_UCODE=0` is the silent control.

The active M5 boundary is the source payload and its producer context, not
rendering. Qualified retail and port hangar source spans are zero on the port
(`FNV=0x762B22A5`) but nonzero in retail. The port's exact target-span guest
scalar/non-scalar observations show the legitimate later `rs_memset` clear at
`0x800078E0/0x800078EC`; the earlier nonzero state is written by the host ROM
asset path (`pi_rom_to_rdram`) before the clear. No mitigation or guest
behavior change is authorized from this boundary.

Session 4164 independently requalified M5 Step 3. Declared-size staging
(`0x800`, the OSTask-declared span) and legacy staging (`0xF80`) both reached
title and hangar with matching task/SP/route, zero-payload, and downstream
signatures. The declared arm is sufficient at this boundary; legacy staging
adds DMEM writes without a measured downstream benefit. ORIGIN: `rsp.cpp`
staging DMA is the writer and the OSTask declaration is legitimate.

Session 4167 completed a clean canonical same-build real-image/silent port
pair after two route-invalid attempts caused by missing route flags and stale
game child processes. Both clean arms passed the positive controls, reached
title VI 1024 and hangar VI 512, and had live gate/task/SP/PCM instrumentation.
The gate was `0x01` in both arms; hangar PCM source and consumer rows were
present but zero-valued in both (`384` samples, `FNV=0xF59C39C5`, `nz=0`).
The real image completed its DMEM/DMA path (`break_pc=0x1328`, `dma_count=3`)
while the silent arm had `dma_count=0`. No downstream real-versus-silent
divergence was measured, so H-upstream-zero-payload remains selected and no
gate change is authorized.

Session 4168 reproduced the same boundary with a self-cleaning concurrent pair.
Both arms fired the positive control and reached title VI 1024 and hangar VI
512. In hangar, real-image and silent PCM source/consumer rows were both zero
(`384` samples, `FNV=0xF59C39C5`, `nz=0`); the real arm logged 3,846 audio-stage
rows and 3,890 image-queue rows, while the silent arm logged no image-queue
rows. The silent arm later bus-crashed after the target phases, so that crash
does not invalidate the phase result. This independently requalifies
H-upstream-zero-payload and rules out route invalidity for this clean pair; no
gate or consumer change is authorized.

Session 4169 qualified the port-side gate writer contract in a fresh concurrent
real-image/silent pair. Both arms fired the positive control and reached title
VI 1024 and hangar VI 512. Both recorded the same four gate-writer rows,
including `0x8008EC88` storing `0x01` in hangar after the `0x8008ED48` and
`0x8008EB7C` zero stores. Gate consumers saw `0x01` in 1,021 real and 1,022
silent hangar rows. Real and silent task/SP completion routes were live; real
had image DMA while silent had none. PCM source/consumer rows remained zero in
both arms (`384` samples, `FNV=0xF59C39C5`, `nz=0`). This selects
H-port-writer-parity and moves the open boundary to the upstream producer
context; no writer or gate change is authorized.

Session 4170 qualified that upstream boundary with the independent retail
oracle and the port in one phase-gated run. Both arms fired the whole-RDRAM
positive control and reached title VI 1024 and hangar VI 512. Retail recorded
664 nonzero post-store bytes in the target source span, with writers including
`0x800078EC` and the `0x8008F*`–`0x800910*` producer family. Port source-span
writer/DMA rows remained `FNV=0x762B22A5`, `nz=0`, and its source-context rows
were zero-valued. This selects a producer-context/source-writer mismatch over
producer parity; no writer or payload mitigation is authorized.

Session 4171 qualified the first matched source-span writer family in the
same phase-gated oracle/port run. Retail scalar stores at `0x80090268`,
`0x80090278`, and `0x8008FF04/0C/14` were observed with zero store-sample
mismatches; the port emitted the same PCs in hangar with matching target-span
destinations and nonzero values. Both arms fired the positive control and
reached title VI 1024 and hangar VI 512. Port image DMA and PCM rows remained
zero-valued (`0x762B22A5` source span and `0xF59C39C5` PCM), so this selects
writer-counterpart parity and moves the boundary to caller/object context.
No behavior change is authorized.

Session 4172 landed and built an M5 task-contract guard in the runtime. The
declared audio `ucode_data_size` is now rejected before DMEM staging when it
is zero or exceeds the `0xFC0` DMEM limit; the explicit legacy `0xF80` arm is
unchanged. This protects the task/SP contract but does not explain the
qualified zero PCM payload: the valid `0x800` task remains on the same image
path. ORIGIN: the guest OSTask producer owns `ucode_data` and
`ucode_data_size`; invalid span metadata is not legitimate audio input.

Session 4173 qualified the matched-writer context join with independent retail
and port arms. Both fired the whole-RDRAM positive control and reached title VI
1024 and hangar VI 512. Retail field dumps at all five watched PCs fired in
hangar and showed per-object source words `0x00C0006F/C6/D7/DE`, branch state,
and changing object bases. The port source-context rows remained on the
matched `0x800AB694 -> 0x800078EC` path with target-span bytes zero and the
source-producer rows carrying their existing destination/value records. The
contexts are not equivalent at the measured object/field boundary, selecting
H-context-mismatch; the first divergent object-field input is now the open
boundary. Port image input and PCM remained zero (`0x762B22A5` /
`0xF59C39C5`, `nz=0`). No behavior change is authorized.

Session 4174 added a regeneration-safe port witness for the same five
object/field producer PCs and qualified it against the independent retail
oracle. The whole-RDRAM control fired; the port phase trace reached title 1024
and hangar 512, and the witness control fired once per target phase with 512
capped rows covering all five PCs. After correcting an initial raw-byte endian
mistake, port rows still did not reconcile with retail: object bases/layouts
differed and the port `s0+0x60`, `s0+0x22`, and `s1+0x22` values diverged from
the retail field table. This selects H-legitimate-field-mismatch over an
instrumentation alias; the wrapper's exact-origin verdict was false only
because it missed the observed phase-origin spelling, so raw phase lines are
the route evidence. The first divergent object-field input remains open; no
audio, gate, writer, or payload behavior changed.

Session 4175 tested the first static candidate for the open object-field
boundary, `recycleSampleStreamBlock` at `0x8008F9C8`, with a
regeneration-safe entry snapshot joined to the five target-PC rows. The first
phase-gated version was unevaluable because the entry occurs before the target
VI; the fixed version latched the entry snapshot and emitted it at
target-phase field rows. Both matched runs fired the whole-RDRAM control and
reached retail/port title 1024 and hangar 512, while the oracle reported zero
executions at `0x8008F9C8` (`0x80090268`/`0x80090278` each 73,352 hits;
`0x8008FF04`/`0x8008FF0C` 67,918 hits). Port target-field controls fired in
both phases but produced zero entry joins. This rules out `0x8008F9C8` as the
executed entry boundary; it does not move the object-field mismatch or
authorize behavior changes.

Session 4176 qualified the next independent retail predecessor range. The
whole-RDRAM control and both title/hangar phase gates fired; the range
`0x8008F900:0x8008FB00` executed 4,480,806 times, while exact
`0x8008F9C8` remained at zero. The earliest executed range entry was
`0x8008F900`, entered from `0x8008F8FC` (142 executions). This selects
H-earlier-executed-entry over H-static-entry-unexecuted-at-range and
H-route-invalid, making `0x8008F900` the next port witness boundary. No
audio, gate, writer, payload, or mitigation behavior changed.

Session 4177 independently requalified that retail predecessor boundary with
the exact target-PC joins. The whole-RDRAM control and both title/hangar phase
gates fired; the range `0x8008F900:0x8008FB00` executed, and exact
`0x8008F900` executed 71 times with `PREVIOUS_PC=0x8008F8FC`. This selects
H-entry-executed and makes `0x8008F900` the next port witness boundary. The
retail result is ground truth only; no port, audio, gate, writer, payload, or
mitigation behavior changed.

## Next steps

Session 4178 qualified the regeneration-safe port witness at `0x8008F900` in
a paired oracle/port run. The whole-RDRAM positive control, both retail target
phases, and both port target phases fired. The port witness joined to the
existing object-field witness in title and hangar, proving the predecessor
executes on the qualified port route. The oracle emitted no phase-gated field
rows for `0x8008F900` because its observed retail origins were
`0x00790800`/`0x006AB800`, while the recipe gated `0x00790400`/`0x006AB400`;
entry-context parity remains unevaluable. This rejects H-route-invalid but
does not select H-entry-context-match or H-earlier-producer-mismatch. No
audio, gate, writer, payload, or mitigation behavior changed.

Session 4180 reran the paired predecessor measurement with isolated output and
the stable retail phase origins. The whole-RDRAM positive control, both retail
phases, both port phases, and both port predecessor joins fired. Retail's
`0x8008F8FC` and `0x8008F900` rows each had 71 hits and showed
`s0=0x48`, `s1=0x1B000`, `source_word=0`, `branch_selector=1`,
`branch_state=0x1100`. Port predecessor joins matched `s0=0x48` and
`s1=0x1B000`, but its helper reported pointed fields as `0xFFFFFFFF` because
it rejects those low raw register values as non-KSEG pointers. This selects
H-predecessor-register-parity and identifies the source/branch comparison as a
measurement-alias defect; the earlier s4179 divergence conclusion is
superseded. No audio, gate, writer, payload, or mitigation behavior changed.

Session 4181 repaired the port predecessor witness to use raw physical-address
semantics for low `s0`/`s1` values, then reran the paired measurement. The
whole-RDRAM control, both target phases, 71 retail hangar predecessor hits,
and two port joins all fired. At the shared hangar phase, retail and port
matched `s0=0x48`, `s1=0x1B000`, `source_word=0`, `source_byte=0`,
`branch_selector=1`, and `branch_state=0x1100`. The first attempt was
unevaluable because the recipe used stale retail origin `0x006AB400`; the
corrected rerun used observed retail origin `0x006AB800`. This selects
H-entry-body-mismatch: the predecessor context is parity and the next boundary
is inside `0x8008F900`. No audio, gate, writer, payload, or mitigation
behavior changed.

Session 4182 added a regeneration-safe witness at the pre-instruction body
boundary `0x8008F900`, recording raw registers and first derived store
addresses/values. The body begins with arithmetic and stores rather than a
guest load, so the witness does not invent one. The retail oracle arm passed
the whole-RDRAM control, reached title/hangar, and recorded 71 phase-gated
`0x8008F900` executions using both observed title/hangar origin variants. The
real-audio port arm crashed before title at `spTaskSchedulerThread+9772` (last
guest PC `0x8000834c`); the silent port control stopped at width 640. Neither
port arm qualified a target phase, so zero port body rows are route-invalid and
do not select body mismatch or parity. The body boundary remains open; no
audio, gate, writer, payload, or mitigation behavior changed.

Session 4183 reran the body discriminator after correcting its port arm from
silent to real audio. The retail positive control and both title/hangar phases
qualified, but the silent attempt crashed at VI width 320 with SIGSEGV and the
real-audio attempt stopped at the same width with SIGBUS; both reported
`spTaskSchedulerThread+9772`, last guest PC `0x8000834c`. Neither port arm
reached a target phase or emitted body rows. This independently requalifies
H-body-route-invalid; body mismatch versus parity remains unevaluable. The
recipe still lacks the canonical autopilot/stop-width settings used by the
earlier qualified route, so no body, audio, gate, writer, payload, or
mitigation conclusion is authorized.

Session 4184 restored the canonical autopilot schedule and
`ROGUESQ_AUTOPILOT_STOP_WIDTH=512` in the existing body-witness recipe. The
whole-RDRAM positive control, both retail phases, both port phases, and 130
port body rows qualified (59 title, 71 hangar). At the shared hangar body
entry, port rows matched the independent retail execution tuple for
`a0/a1/a2`, `s0/s1`, and the first derived store value; the retail field tuple
also matched (`s0=0x48`, `s1=0x1B000`, zero source word/byte, selector `1`,
state `0x1100`). This selects H-body-entry-parity and moves the open boundary
after the first body stores. No audio, gate, writer, payload, or mitigation
behavior changed.

Session 4185 extended that canonical paired run with an independent oracle
physical watch for the body-store range and exact `0x8008F90C`/`0x8008F910`
store PCs, including post-store scalar controls. The whole-RDRAM control,
both retail phases, both port phases, and 130 port body rows qualified. At the
shared hangar tuple, retail and port matched the body store/link addresses
(`0x8017D9E0`/`0x8017D9F8` and `0x8017D9FC`) and both exact retail store PCs
had nonzero, mismatch-free post-store samples. This selects
H-next-store-parity and moves the open boundary after the second body
store/link tuple. The oracle GPR callback does not expose a stable written
value field, so the conclusion is limited to the independently matched
address/link and scalar-write contract; no audio, gate, writer, payload, or
mitigation behavior changed.

Session 4186 extended the same canonical paired run to the loop-control tuple
at `0x8008F914`/`0x8008F918`. The whole-RDRAM positive control, both retail
phases, both port phases, and 130 port body rows qualified; port emitted 260
loop rows. At the shared hangar phase, port showed `a2=0x47` then `0x48`,
`s0=0x48`, and compare `1` then `0`. Independent retail execution watches
recorded 71 hits at each exact PC with the same `s0=0x48`, `s1=0x1B000`, and
the expected predecessor relation. This selects H-loop-control-parity and
moves the open boundary to the `0x8008F91C` loop branch. No audio, gate,
writer, payload, or mitigation behavior changed.

Session 4187 extended the canonical paired run to the `0x8008F91C` branch.
The whole-RDRAM positive control, both retail phases, both port phases, and
130 port branch rows qualified. Port took the branch for `a2=0x02..0x47` and
fell through at `a2=s0=0x48` in both title and hangar. Independent retail
recorded 71 branch hits with the same `v0=1` for 70 iterations and `v0=0` at
the terminal iteration. The oracle's `0x8008F920` watch had zero hits because
its debugger accounts for the delay-slot execution under the branch PC; this
is a measurement limitation, not a route failure. This selects
H-branch-parity and moves the open boundary after the delay-slot increment,
at the loop exit successor. No audio, gate, writer, payload, or mitigation
behavior changed.

Session 4188 extended the canonical paired run to the loop-exit successor at
`0x8008F924`. The positive control, both retail phases, both port phases, and
two port successor rows qualified. At the terminal hangar iteration, port and
independent retail matched `v0=0`, `a2=s0=0x48`, and the unchanged predecessor
context; the oracle recorded the same successor PC. The first post-loop load
is `0x801499C8`, and the port witness read `0xE0D91780` there. This selects
H-successor-parity and moves the open boundary into the first post-loop loaded
state. No audio, gate, writer, payload, or mitigation behavior changed.

Session 4189 extended the canonical paired run to the first post-loop load/use
at `0x8008F928`, `0x8008F938`, and `0x8008F93C`. The first attempt was
route-invalid because the port crashed at `spTaskSchedulerThread+9772` before
VI 320; the fixed rerun qualified the whole-RDRAM control, both retail phases,
and both port phases. At the shared hangar phase, the independent retail oracle
and port matched the loaded word at `0x801499C8` (`0xE0D91780`), the loaded
`v1` (`0x8017D9E0`), the derived `v0` (`0x8017E0A0`), and the resulting store
address (`0x8017E088`). Title tuples also matched (`0x402C1980`,
`0x80192C40`, `0x801931E0`, and `0x801931C8`). This selects
H-load-use-parity and moves the open boundary to the post-loop store/caller.
No audio, gate, writer, payload, or mitigation behavior changed.

Work only the first applicable item. This backlog is one monotonic sequence.

1. **M5 audio de-stubbing:** A12 countdown wait de-stubbed (s4192); A12 second spin at `0x8014974C` CLOSED as never-stuck (s4193: entered once, flag already 0, no spin; nothing to de-stub). A14 status-03 shutdown wait CLOSED as never-entered (s4194: 4/4 entries status 0x00, call 2 only; tools/audit_a14_shutdown_wait.py). Next: M5 Step 8 (voice-base/list guard class; needs retail writer + valid range first) or the first genuinely stuck wait. Object-path parity qualification is closed (s4187-s4191); do not add witnesses there.
2. **M3 pre-publication guard runtime qualification** remains blocked on a host
   with `mips64-elf-gcc`/`mips64-elf-ld` and a configured `PatchesLib` target;
   do not spend another host-only iteration.
3. **Generated-symbol renaming sweep.** Parked while M5 has applicable route,
   writer, or audio work. Keep slug `generated-symbol-renaming-sweep` if it
   resumes; mapping-only edits do not reset the engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 producer absent | Hangar source-span census is closed as retail parity at the measured boundary. The missing port nonzero payload is upstream/earlier provenance, not an established missing guest store. |
| M5 pre-clear provenance | H-host-ROM-writer selected at s4163: `pi_rom_to_rdram` writes legitimate nonzero target bytes before the later guest clear; generated guest scalar and non-scalar target rows are zero-valued at the clear. |
| M5 source setup state | H-shared-source-state selected at s4150: independent retail and port setup tuples match for the title clear and dominant hangar source-construction calls. The setup boundary is not the measured explanation for the later zero producer payload. |
| M5 producer caller state | H-caller-state-split selected at s4152, with s4153 selecting H-entry-body-shared: retail preserves producer object/state into `0x800078EC`, while port context differs earlier. Generated port `ra=0` is an instrument limitation, not guest evidence. |
| M5 Step 3 declared audio staging | H-step3-equivalent independently requalified at s4164: declared `0x800` and legacy `0xF80` arms match at the measured downstream contract. Semantic irrelevance outside that contract is unproven. |
| M5 Step 4 retail gate ground truth | H-retail-gate-writers selected at s4166: the independent oracle whole-RDRAM control fired in both target phases; `0x800A0F50` was written 14 times by five PCs, with `0x8008EC88` producing the observed nonzero value. The watched `0x80094648`, `0x80090AAC`, and `0x80090BA4` words had zero writes in this retail route. This selects the port parity measurement, not a gate change. |
| M5 Step 4 port parity | H-upstream-zero-payload selected at s4167: the clean canonical pair reached title/hangar and live gate/task/PCM controls. Both arms had gate `0x01` and zero-valued hangar PCM source/consumer rows; only the real image's DMEM/DMA activity differed. The initial route-invalid attempts are excluded because they stopped at VI 640 or crashed with stale game children present. |
| M5 Step 4 producer context | H-writer-counterpart-parity selected at s4171: retail and port both exercised `0x80090268`, `0x80090278`, and `0x8008FF04/0C/14` in hangar; port target-span rows carried matching nonzero values and destinations. The downstream port DMA/PCM remained zero-valued, so caller/object context is the next boundary. |
| M5 writer object context | H-context-mismatch selected at s4173: retail field dumps fired for all five PCs and showed changing per-object source words/branch fields, while the port matched source-context path retained zero target-span values and did not expose equivalent object-field state. The first divergent object-field input is open; no behavior change is authorized. |
| M5 object-field witness | H-legitimate-field-mismatch selected at s4174: the corrected port witness fired in both target phases and recorded all five producer PCs. Its runtime-memory field values and object records did not reconcile with the independent retail field table after using `MEM_W/MEM_BU/MEM_HU` semantics. The earlier raw-byte result is superseded as an endian instrumentation defect. |
| M5 object-entry boundary | H-entry-body-mismatch selected at s4181: after repairing the port witness to raw physical-address semantics, retail and port matched `s0=0x48`, `s1=0x1B000`, source word/byte, selector, and branch state at the shared hangar phase. The open boundary is inside `0x8008F900`. |
| M5 object-body witness | H-successor-parity selected at s4188: the canonical route qualified both target phases and two port successor rows; independent retail and port rows matched terminal `v0=0`, `a2=s0=0x48`, and the successor PC. The first post-loop load is `0x801499C8`; the open boundary is its loaded state/use. |
| M5 object load/use witness | H-load-use-parity selected at s4189: the qualified paired route matched the independent retail loaded word, loaded `v1`, derived `v0`, and post-store address in both title and hangar target phases. The open boundary is the post-loop store return/caller. |
| M5 task contract | H-contract-gap selected at s4128: image task handoff/completion is live, but image and silent controls both have zero measured PCM payload at the tested scope. |
| M5 consumer disconnected | Selected at the measured task/output scope; upstream zero payload remains open. |
| M5 title host sink | H-play selected at s4065: device 2 opens, host queue calls are positive, and drain depth advances. Native device callback/output behavior remains open. |
| M5 image zero boundary | H-guest-zero-producer selected at s4112: qualified port arms recorded zero-valued `0x800078EC` stores into the source span before zero image reads; host writeback is downstream zero data. |
| M5 gate value | Selected at measured scope: retail gate writes were zero-byte pre-target activity. |
| M5 descriptor selector writer | H-port-writer-live selected at s4100: port witness rows fire and `0x80090AAC` has retail-matching selector values; `0x80090BA4` has no port rows. |
| M5 key-on early returns | H-returns-dead/H-guard-valid selected at s4101: valid divisors, normal tails, and slot transitions; no guard relaxation authorized. |
| M5 drain-tick policy | H-Drain-Changes-Ordering remains qualified at s4103/s4114. Tick-required behavior is not established because the reverse-order arm was route-invalid. |
| M5 status-03 reaping | H-status03-after-return selected by qualified port ordering at s4136: service entry, read, `03 -> 00` store, and exit are ordered after the observed shutdown return. No force-clear or wait change is authorized. |
| M5 A10/A9/A8 guards | A10 and A9 guards are not suppressing measured valid work; A8 trap PCs are live but do not fire on qualified retail/port routes. No relaxation is authorized. |
| M5 A11 wait terminal transition | H-target-phase-absent-both selected at s4145: target-phase wait/post-wait terminal rows were absent in both qualified arms. This is not a safety proof. |
| M3 sentinel ownership | H1 selected at source/host-build scope; runtime remains unqualified because this macOS graph lacks the MIPS toolchain and `PatchesLib` target. |
| Generated symbols | Parked until higher-priority M5/M3 work is inapplicable. |

## Durable evidence boundary

Retail reaches title/hangar and can attribute relevant writer PCs. The paired
port can reach image-DMA joins when its arm completes. The port task
`0x80171E70`, size 1, joins the exact input DMA at matching generations, but
payloads are zero; separate writeback joins are real. The task and output edges
therefore execute, but zero payload does not identify the missing upstream
writer.

The qualified consumer comparison used same-build declared/real,
declared/silent, and legacy/real arms. It found matching phase-5 zero-payload
signatures. A route failure invalidates a null; it never proves absence.

Session 4166 supplied the independent retail line for Step 4. The oracle's
whole-RDRAM watch reached its 10,000-callback positive-control threshold and
the driven route reached title `1024 @ 0x00790400` and hangar `512 @
0x006AB400`. Its narrow gate watch recorded 14 writes: the writer set was
`0x8008EA34`, `0x8008EB40`, `0x8008ED48`, `0x8008EB7C`, and `0x8008EC88`;
post-store samples were zero for the `ED48`/`EB7C` rows and nonzero for the
`EC88` row. The three candidate consumer/selector watches had no writes.
This is independent retail evidence only; port parity and downstream joins
remain open.

The title playback/drain capture is independently controlled by retail
whole-RDRAM and title/hangar AI-output witnesses. On the paired port,
declared-real reaches both phase gates and host enqueue/raw drain rows are
positive in both phases. This closes immediate queue-drain starvation at the
measured SDL queue boundary, not device delivery to audible output.

## Superseded conclusions

The s4179 H-earlier-producer-mismatch conclusion at `0x8008F8FC` is
superseded by s4180. Its retail row was valid, but the port helper's
`0xFFFFFFFF` fields came from a KSEG-only guard while the shared predecessor
registers were low raw values (`0x48` and `0x1B000`), so those fields were not a
like-for-like comparison.

The s4180 H-predecessor-register-parity conclusion is refined by s4181: the
shared register values were correct, but the pointed-field reads were not yet
like-for-like. The corrected raw-address witness and independent retail rows
now establish parity at the shared hangar phase; the open boundary is the
`0x8008F900` body.

The overlay/menu-only explanation, intrinsic VI-640 flakiness, missing-input
and wait-return explanations, global-zero image-DMA theory, route-wide PCM-gap
theory, and force-zero default policy are superseded at their measured scopes.
They were plausible before qualified routes, same-build controls, or
independent retail attribution existed.

The early staging-based route explanation is superseded by same-build route
tables: launch order and timing affect qualification, but neither staging size
nor real-audio mode alone explains the measured boundary. The s3579–s3584
stored-value inference is unsupported because a retail byte store was compared
with an aligned word containing neighboring bytes.

The s4075 missing-store inference is superseded by the source audit: the
generated source contained the store and the fixup had silently omitted its
witness. The s4088 detail-hook conclusion is superseded by s4089, where a
corrected callsite fired the positive control. The s4149 setup/state
route-invalid conclusion is superseded by s4150's route-stable retail match.

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
Detailed counts and session-specific notes remain in `PORTING-STATE.md`.
