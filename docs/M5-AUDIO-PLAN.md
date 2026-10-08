# M5 — audio de-stubbing plan

Refreshed in session 3977 (2026-10-04). This is the design gate for M5.
Session 3303 supersedes the linked-runtime part of Session 2791's SP-yield
conclusion. The weak task-start implementation clears stale request state, but
the linked strong override shadows that function without clearing it. More
importantly, the same-build A/B proved that reporting a request as a yielded
completion causes the viewer scheduler's E70/E80F loop; returning not-yielded
restores E60, scheduler sends/clears, submit returns, and viewer progress.
Task interruption and resumption remain unimplemented.

Session 3038 re-surveyed the checked-in audio/runtime sources and the available
fixup surface after the phase-gated s2978 port-route capture. The document was
already present, so this refresh reconciles it with the current tree rather than
opening a second plan. The external
`RecompiledFuncs/` snapshot is not present in this checkout; generated audio
behavior therefore remains represented by the checked-in anchors and fixup
scripts. The survey found no new active audio stub or gate outside this
inventory.

The survey also closes the planning question for the first M5 unit: the only
production `M_AUDTASK` choices remain the real Factor 5 image and the explicit
silent `musyx_stub` control; `aspMain`, `unknown_task_stub`, and the RSP
non-`Broke` failure path are not valid de-stubbing targets. The default drain
tick is forced off at process startup, and the image canary, route identity,
PCM joins, gate/slot traces, and MORT decoder are diagnostic or validation
surfaces rather than hidden audio implementations. The coupled contract is
task dispatch → DMEM/DMA and `Broke` → SP completion → guest service/slot
progress → PCM publication; changing only one stub return cannot validate that
chain. The current qualified port configuration can reach title and hangar,
but the s3028 pair used a driver that remained at pre-title VI 640, so that
pair's downstream nulls remain unevaluable. The first behavior change is
therefore still not authorized by this survey: Step 1 must run with the
validated AUTOPILOT/phase-gated route, then Step 3 may implement one named
missing contract edge.

Session 3231 made the dispatch boundary task-local: `get_rsp_microcode` reads
`ROGUESQ_AUDIO_UCODE` for each `M_AUDTASK`, preserving the explicit silent arm
without allowing the first dispatched task to pin later tasks to that arm.
The image and silent smoke controls retained their expected dispatch and
SP-completion rows, but stopped before the target title phase; this is a
runtime qualification fix, not evidence of downstream audio output.

Session 3949 implemented the host-side PCM representation edge from Step 10:
`queue_samples` now constructs native-endian `int16_t` values from the two
network-order bytes in each N64 sample before calling `SDL_QueueAudio`. The
sample count, guest address, and queued byte length remain unchanged. This
does not select a Factor 5 task writer or prove nonzero PCM; it is the concrete
host-boundary behavior change required before that qualification can be used.

Session 3977 implemented the next task-contract edge: audio RSP staging now
uses the OSTask-declared `ucode_data_size` instead of unconditionally copying
`0xF80` bytes. The qualified task rows declare `0x800`; the old span therefore
read beyond the image into the reserved DMEM gap. `ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1`
retains the previous span as a same-build rollback arm. This is a runtime
behavior change, not proof that the image produces valid PCM; the next soak
must compare both arms with the existing dispatch, SP-completion, DMA, slot,
PCM, and VI controls.

The source-level inventory was checked directly in `main.cpp`,
`librecomp/rsp.cpp`, `librecomp/ai.cpp`, `ultramodern/audio.cpp`,
`src/rsp/aspMain.cpp`, and the Factor 5 audio fixup/generated image. It found
no additional production audio stub or gate beyond A1–A20 below. In
particular, `musyx_stub` is the only explicit silent M_AUDTASK control,
`factor5_ucode_b` is the selected real image, `aspMain` is not a live RS64
route, and `Broke` remains the required task completion edge. This is a design
survey result, not evidence that either audio arm produces correct PCM.

## Boundary and current policy

Rogue Squadron has two audio data paths that must not be conflated:

- The Factor 5 audio RSP image is the recompiled `factor5_ucode_b` selected by
  `ROGUESQ_AUDIO_UCODE=1`. It is sourced by `factor5b_rsp.toml` from ROM
  `0x09ABE0` and is labelled `aspMainText`/`aspMainDataStart` in the companion
  map. It is not a MORT decoder.
- MORT is a CPU-side speech/sample codec boundary. The retail `speech` asset
  contains MORT descriptors, and the generated guest voice decode/filter path
  is live. `tools/mort_probe.py` is an independent reference decoder and
  validation tool; it is not the runtime audio implementation and does not
  justify a second RSP image.

The current default is the Factor 5 image: `get_rsp_microcode` routes
`M_AUDTASK` to `factor5_ucode_b`. `ROGUESQ_AUDIO_UCODE=0` selects
`musyx_stub`, which returns `RspExitReason::Broke` without touching DMEM, as
the silent control arm. Stock `aspMain` is also a `Broke` stub and is not
selected by this project's task dispatch. Never use it as a replacement for
the retail task contract.

The image arm performs DMEM work,
`SP_WR_LEN` DMA writes, and reaches the generated `break 0` completion edge;
the host accepts only `Broke`. The image-stage canary is inside the generated
`0xE50..0xFCF` mix-buffer span, so `canary_ok=0` is diagnostic data, not a
completion or writeback gate. s2220 matched the retail `reapplyDisplayMode`
(`0x8008EC88`) polarity and reached service, slot completion, and nonzero PCM
controls with C88=`1`. s2608 made that guest store the compiled default
(`ROGUESQ_M5_C88_VALUE=0` is the force-zero rollback). Hangar PCM and the
remaining slot/voice checkpoints below are still open.

The s2665 source survey covered `src/`, `patches/`, the checked-in runtime,
the generated-function snapshot where available, and
`tools/fixup_factor5_ucode.py`. `patches/` contains no audio override or
audio host stub. The fixup script owns the regeneration-safe image return,
iteration-cap, and image-stage probe insertions; those are represented by A3
and the diagnostic inventory below. The generated game-function fixups are
outside this checkout, so their active audio behavior is represented by the
checked-in generated anchors and the existing fixup-controlled guards rather
than by hand edits. No additional active audio stub, trap, gate, or safety
hatch was found outside the inventory below.

## Complete inventory of active stubs, traps, gates, and safety hatches

“Active” means present in the source or generated/fixup pipeline and capable of
affecting audio behavior. A diagnostic-only row is explicitly marked. The
writer and legitimacy column is intentional: no mitigation may be promoted
without naming the writer and proving the value is legitimate.

| ID | Site | Current behavior | Contract, writer, and legitimacy | Safe next action and positive control |
|---|---|---|---|---|
| A1 | `src/main/main.cpp:get_rsp_microcode` → `musyx_stub` / `factor5_ucode_b` | Default `M_AUDTASK` selects `factor5_ucode_b`; `ROGUESQ_AUDIO_UCODE=0` selects the silent `musyx_stub` control. | The task must complete its SP/guest contract. The guest submits the `OSTask`; `librecomp/rsp.cpp:run_task` invokes the selected function. This is the primary de-stubbing boundary. | Keep both arms in one build. Require task dispatch/exit, task-field identity, DMA/readback, service return, slot progress, PCM source/consumer joins, and route phases. Roll back by setting `ROGUESQ_AUDIO_UCODE=0`. |
| A2 | `src/rsp/aspMain.cpp:aspMain` | Always returns `Broke`; no live RS64 caller selects it. | Stock ASP has a different ABI/format. Retail is the Factor 5/MusyX image, not this stub. | Keep out of dispatch. A future stock-ASP test needs a known-good stock task as its control, never an RS64 task. |
| A3 | `factor5b_rsp.toml`, generated `factor5_ucode_b`, `tools/fixup_factor5_ucode.py` | The image has real DMEM/DMA work, a generated `break 0` at `0x1328`, and returns `Broke`. Its RSP status/DMA busy polls are modeled by the host helpers; invalid indirect targets return `UnhandledJumpTarget`. | `data_ptr`, `data_size`, `output_buff`, `yield_data_ptr`, and the `data_ptr+0x100` relation are task ABI fields, not guessed PCM destinations. `SP_WR_LEN` is the image writer; host DMA records its actual ranges. | Preserve the generated/fixup path. The positive control is a completing image task with nonzero DMEM/DMA and a matched retail task-field row; a `Broke` return alone is insufficient. |
| A4 | `librecomp/rsp.cpp:run_task` | Stages the OSTask and `ucode_data` into DMEM, serializes DMEM, calls the selected function, and treats any exit other than `Broke` as failure/assertion. | `Broke` is the current completion convention. `task_thread_func` then sends `sp_complete`; failure invokes the runtime quick-exit path. | Do not weaken the exit assertion or quick-exit path. Control: `run-task-return=1` followed by `sp-complete-enter/return`, with no `UnhandledJumpTarget`. |
| A5 | `librecomp/src/sp.cpp:osSpTaskYield_recomp` / `osSpTaskYielded_recomp` | The runtime records a process-local yield request but does not interrupt or resume a task. Completion-wins is the default; `ROGUESQ_SP_YIELDED_REQUEST_ONLY=1` is the rollback/control arm and now consumes each reported request once. | The request is legitimate, but it is not a legitimate yielded-completion result for the non-interrupting host. Repeatedly reporting one request traps the scheduler in its retry path, so the control arm must be one-shot. The image task still completes through `Broke` and host SP completion. | Keep completion-wins as the production default, use request-only only for paired validation, and validate E60 → scheduler send/clear → submit return → viewer return/title. The strong task-start override resets stale requests at each new task. |
| A6 | Guest gate `0x800A0F50` in `initMusyXEngine`, display-mode writers, shutdown, and no-op paths | The init/display tails write `1`; entry/failure/shutdown/no-op paths write `0`. `tickMusyXIfActive` and task/wait helpers branch on it. | This is a guest MusyX enabled state, not an SDL or RSP completion flag. Writers are named guest functions; retail writer PCs and values must be independently observed before changing any store. | Leave stores unchanged. A gate experiment changes exactly one writer and measures the same-run retail writer, gate value, task/slot outcome, and route phase. A writer count alone is not a control. |
| A7 | Generated `tickMusyXIfActive` and `musyxSynthFrame` gate paths | A zero `0x800A0F50` returns before voice/song ticking; a nonzero gate enters the MusyX mutex, sequencer, voice, and reaping work. | Gate writer is A6; voice and song tables are guest-owned. A live function entry does not prove valid voice population. | Do not bypass the gate as an audio fix. Positive control requires a nonzero gate, valid voice base, a slot transition, and a completed task in the same phase. |
| A8 | `musyxKeyOnVoice` divide/overflow class | Eight generated trap sites are defensive early returns at `0x80090CEC`, `0x80090D04`, `0x80090D30`, `0x80090D48`, `0x80090D74`, `0x80090D8C`, `0x80090DB8`, and `0x80090DD0`. | Session 3220 named the sole cmd-list divisor publisher: `musyxRenderVoiceSamples` at `0x80090768` stores mix `$a2`, constantly `0xC0` from all three `musyxSynthFrame` sites, into ping-pong cmd-list `+0x60` (`D_80149708`/`D_8014970C`). Mixer-voice ADSR `sw $zero, +0x60` sites write `D_801496F8`, a different malloc. `lhu +0x60` makes all four `break 6` sites unreachable. The four `break 7` sites are the game's own divide-by-zero handler (uninit first-frame ping-pong heap, which hardware also has). | Keep. Do not remove or replace a trap. Retail/port in-range proof and the normal-tail key-on plus slot `0x02` then `0x00` control still require a title/hangar image-arm route. |
| A9 | Generated voice-array base guards in `funcs_24.c` | Entry and loop guards return/skip when the voice-array base is outside KSEG0 RDRAM. | Session 3219 named the sole generated publisher: `allocateSongChannelArray` at `0x8008F0EC` stores the first `rs_malloc` into `D_801496F8`; `D_801496FC` is a same-malloc alias. No invalid or overlapping distinct-base store exists at generated-source scope. Two consumers (`musyxStartVoiceRelease`, `setVoiceModulationParams`) lack the A9 KSEG0 skip; they are readers, not publishers. Runtime in-range values and a downstream voice/slot effect remain unevaluable until a target-phase M5 route exists. | Keep. Do not add or relax a guard. Retail/port in-range proof still requires a title/hangar image-arm route. |
| A10 | Generated voice/list/table pointer guards in `funcs_25.c`/`funcs_26.c` | Invalid voice-list nodes and song-tick-table pointers skip work instead of dereferencing. | Guest allocators write these pointers; the guards are M3 safety machinery, not proof that the RSP stub is the cause. | Exclude from the first de-stub. Audit as one complete idiom class only after valid audio data exists; control is valid traversal plus matching writer evidence. |
| A11 | `waitForAnyAudioSlot` / `anyAudioSlotActive` | The formerly unbounded loop has a default 500,000-iteration escape; `ROGUESQ_WAITFORSLOT_GUARD_CAP` selects an alternate cap. | The loop reads slot bytes; render/key-on/reap/service writers must create the terminal state. Escaping is not task completion. | Keep the cap while changing audio. Control is a slot `01/02/00` transition and clean wait return with zero guard fire. Do not add a new wait skip. |
| A12 | `waitForMusyXAudioTaskDone` and `shutdownAudioEngine` | **De-stubbed s4192:** unset `ROGUESQ_AUDIO_WAIT_NOPUMP` now yields (`yield_self_1ms`) so the real producer clears the countdown (16 -> 0, ~200 yields); `=0` restores the old pump (which measured 16 -> 16, a no-op skip), `=1` the blind spin. The separate `0x8014974C` spin remains unbounded. | `musyxSynthFrame` is the known countdown writer; ownership of the second flag remains unresolved. The pump is a mitigation, not an explanation. | Compare pump on/off only after the task and slot controls are live. Positive control is named writer → observed zero → caller return, not elapsed time. Do not run the blind-spin arm unattended. |
| A13 | `drainAudioAndFinalizeSpeechBuffer` | The injected `tickMusyXIfActive` is now opt-in; `ROGUESQ_DRAIN_INLOOP_TICK=1` enables the rollback/control arm. A 10,000,000-iteration timeout logs and forces idle. | Slot status writers own the terminal state. The injected tick and forced idle are host-port hatches, not retail behavior. | Validate default-off against the explicit tick-on control. A named status writer followed by clean drain return is required; timeout fire is failure. |
| A14 | `shutdownMusyXVoices` status-`03` loop | Call 3 can spin waiting for `D_80154620` to be cleared; **s4296: spin now yields (`ROGUESQ_A14_YIELD`, default on, `=0` rollback; `tools/apply_s4296_a14_spin_yield.py`, live-tree). No state is forced.** | `stopVoiceSlotSynced` writes `03`; `serviceVoicePoolFrame` is the candidate zeroing writer. The writer must be observed before any force-clear. | Trace worker entry and status-zero store. Positive control is worker entry → zero store → shutdown return. No skip or forced zero is authorized. |
| A15 | `ROGUESQ_SPIN_YIELD` at menu/audio spins | Opt-in host yield every 100,000 iterations can allow external VI/SI messages to drain. Default is off. | This is scheduler fairness, not MusyX work. The legitimate host event source is `external_messages`; hardware would preempt the guest spin. | Use only as a route control. It must change host message progress without being counted as audio output. |
| A16 | `librecomp/src/ai.cpp` shims | `osAiGetStatus_recomp` returns `AI_STATUS_FIFO_FULL` (`0x40000000`) when host audio is buffered and zero otherwise; `osAiSetNextBuffer_recomp` queues and returns zero; `osAiGetLength_recomp` reports host buffered bytes. | Retail uses `__osAiDeviceBusy` inside set-next; on the covered route it does not take the FIFO-full branch and the caller ignores v0. The status/length shims are currently unexercised by the qualified port route, so their contract is not a PCM explanation. | Do not change them in the first de-stub step. Control is whole-RDRAM plus retail busy/success and port source/consumer PCM joins; a future AI change requires a positive caller and nonzero source PCM. |
| A17 | `ultramodern/src/audio.cpp` and `main.cpp` host bridge | Callbacks are registered; SDL device failure leaves no device. `queue_audio_buffer` converts bytes to sample count, and `queue_samples` now passes `samples*sizeof(int16_t)` to SDL. | RSP/guest produces PCM; host owns buffering. The former sample/byte mismatch was fixed and is not a remaining de-stub target. | Keep the fix. Validate nonzero PCM independently of SDL device creation; a device-open message is not a PCM control. |
| A18 | `DmemGuard` and `g_lle_task_mutex` | All RSP DMEM users, including audio, serialize on the shared DMEM lock. | One emulated RSP owns one DMEM; without serialization audio staging can trample graphics state. | Keep as an invariant. Positive control is a graphics DMEM canary surviving an audio task; never parallelize as an audio optimization. |
| A19 | `unknown_task_stub` and task-thread failure path | Unknown task types return `Broke`; a failed task causes quick exit. | This handles malformed/uninitialized types, not `M_AUDTASK`, and must not hide an image `UnhandledJumpTarget`. | Keep out of M5 treatment. Control is distinct task-type logging plus normal M_AUDTASK dispatch/exit. |
| A20 | CPU MORT boundary and `tools/mort_probe.py` | No second runtime RSP MORT implementation is selected. Generated CPU voice decode/filter functions and the separate `speech` asset are the live retail-shaped path; the tool decodes reference rows. | MORT owns speech/sample representation, while the Factor 5 image owns its RSP task. Six descriptor types and both sampled rates have independent reference coverage. | Do not start a MORT RSP pass. If a later change is needed, attach it to a named CPU decode/output join and validate against the reference decoder before touching task dispatch. |

The following are instruments, not de-stubbing changes: `audtask-dispatch`,
`audtask-abi`, `audtask-dma-*`, `audtask-image-stage`, `audio-route`,
`pcm-boundary-*`, gate/slot/voice traces, C88 probes, and the image canary.
They are useful only when phase-scoped and paired with a positive control.

## Competing hypotheses and discriminating measurement

| Hypothesis | Prediction if true | Result that would select or reject it |
|---|---|---|
| H-AudioDegeneracy | The silent `M_AUDTASK` path and related degenerate gates create the wait, slot, PCM, or voice failures. One real edge produces a new downstream control without merely changing route reachability. | Same-recipe stub/image comparison shows task completion plus predicted service, slot, voice, or PCM progress. A route-only change rejects this explanation. |
| H-ContractGap | A host return is insufficient because the MusyX task/DMEM/DMA/output ABI is incomplete. | Image DMEM/DMA activity exists but the task-field, output, slot, or PCM joins do not close. This keeps the image arm under contract qualification and directs work to the missing edge. |
| H-MixedPipelines | Factor 5 image audio and CPU MORT speech are separate pipelines. | RSP task controls can be complete while MORT descriptor/voice controls remain independent, or vice versa. A single global “audio default” cannot be treated as proof for both. |
| H-GateArtifact | A current guest gate or trap suppresses legitimate work. | Only independent retail writer/value evidence, plus the corresponding port writer and downstream transition, authorizes changing that gate/trap. A guard hit by itself is not evidence. |

### s2979 planning result

`H-audio-stubs-share-one-contract` is selected for the design scope. This is
not a claim that the silent stub caused the VI-640 route stop. The source
survey shows that an audio task's observable contract is distributed across
the selected RSP function, `run_task`, `sp_complete`, the guest MusyX service
and slot state, and the AI/PCM boundary. The image arm already performs real
DMEM/DMA work; the silent arm is intentionally useful as the no-write control.
Consequently the first replacement must preserve a same-build silent arm and
measure the complete chain. The current route stop means that the required
positive control has not yet run at the target phase, so no gate, wait, voice,
or writeback mitigation is selected by this plan.

The discriminator is one phase-keyed row containing all of these fields:

`M_AUDTASK` dispatch and exit; task fields and source hash; DMEM change and
DMA/readback ranges; service entry/return; status `01/02/00` and status `03`
reaping; voice-array/reap activity; PCM source and consumer joins; MORT entry
and descriptor class; and route phase (`640` target origins, title
`1024 @ 0x00790400`, hangar `512 @ 0x006AB400`). The whole-RDRAM oracle watch
is the required independent positive control before interpreting any narrow
retail null. A counter that proves only that a branch ran is not a control.

## Incremental execution sequence

Every row below is one behavior change, except the explicit ground-truth
checkpoints. Build every A/B arm together, gate on VI transitions, and enqueue
the validation soak rather than babysitting it. All recipes must run from the
build directory with the ROM present and terminate the process group with
SIGKILL.

| Step | One behavior change | Positive control and expected downstream signal | Phase-gated soak and rollback |
|---|---|---|---|
| 0 | No behavior change: reconcile the retail contract and current generated/fixup anchors. | Oracle whole-RDRAM watch fires; retail reaches the target route and names writers for `0xA0F50`, task fields, voice/status words, and AI calls. Port has `audtask-dispatch`, SP completion, and route controls. | Oracle plus the existing port driver, with `PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1`. Rollback: none. Do not add an instrument before this control. |
| 1 | Re-baseline the current default image against the same-build silent control before changing any further contract edge. This is a qualification checkpoint, not a behavior change. | Stub: `M_AUDTASK` returns with no DMEM/DMA. Image: nonzero DMEM changes, image completion at `0x1328`, `Broke`, SP completion, and matching task fields. The image must also report the predicted service/slot/PCM rows or explicitly show the missing edge. | Phase-keyed title/hangar run using `ROGUESQ_AUDIO_UCODE=0` and the default image arm from one build; retain `ROGUESQ_LOG_ALL` and PCM/task joins. Rollback: set `ROGUESQ_AUDIO_UCODE=0`. The run is invalid if both port arms remain before the target phase. |
| 2 | Promotion to the default image arm is complete in the current source; do not repeat it as an experiment. The SP yield rollback is now one-shot. | The Step 1 row must still show the default image reaches the same title/hangar route as the stub control, completes tasks, preserves the gfx DMEM control, and identifies any downstream divergence. A request-only control must report one yielded result per request, then clear. | Treat this as a completed policy transition, not a new behavior change. `ROGUESQ_AUDIO_UCODE=0` remains the audio rollback; `ROGUESQ_SP_YIELDED_REQUEST_ONLY=1` is the SP-yield control. |
| 3 | **Qualified in s4164:** use the declared audio `ucode_data_size` for the DMEM staging DMA; the current task declares `0x800`, while the legacy path copied `0xF80`. | Both arms retained task dispatch, image `Broke`, SP completion, and route controls. The declared `0x800` arm reached title/hangar without a new failure; legacy staging changed DMEM contents but produced no downstream improvement. | One rebuilt binary with `ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1` and unset, phase-gated at title and hangar. Rollback remains the env arm; no writer or writeback conclusion follows. |
| 4 | Change one `0x800A0F50` writer or one gate consumer, only after independent retail writer/value evidence selects it. **C88 default store is done (s2608):** unset writes guest `$v0` at `0x8008EC88`; `ROGUESQ_M5_C88_VALUE=0` is the rollback. Title PCM joins; hangar PCM does not. | Same-run retail writer and value transition, matching port writer, nonzero gate branch, completed task, and slot/voice downstream transition. Remaining: hangar `0x80094648` value/dest vs sampled PCM. | Title and hangar VI phases using AUTOPILOT. Rollback that exact store/consumer. Any mitigation-shaped diff needs `ORIGIN:` naming the writer and legitimacy. |
| 5 | Remove or replace the eight key-on early returns as one audited idiom class, only after valid descriptors/divisors are proven. | Normal key-on tail, slot `02` then `00`, no new status-03 hang, and descriptor fields match the retail class. | Hangar `512 @ 0x006AB400`; keep an invalid-input fallback in the same arm. Rollback the generated/fixup class. |
| 6 | **s4200: gate was not in generated code until now (wired into full fixup); drain not entered on title+hangar in tick-on or default arm, A13 dormant there (single-source).** Originally implemented in s2692: remove the in-loop drain tick from the default path; retain the explicit tick-on arm for rollback/control. | Same-run tick-on control and default-off arm must report task/SP completion, named slot/status transition, nonzero PCM joins, and the same route; a timeout or clean route alone is not success. | Same hangar phase, tick A/B in one build. Rollback with `ROGUESQ_DRAIN_INLOOP_TICK=1`. |
| 7 | Replace one remaining wait/timeout hatch with the observed worker contract, beginning with status-03 service reaping. | `serviceVoicePoolFrame` or the independently named retail-equivalent worker enters, stores zero, and the shutdown/drain returns without force-idle. | Hangar phase with status/worker writer table. Rollback the single wait change; never force-clear an unexplained status. |
| 8 | Relax one voice-base/list/table guard class only after the writer and valid range are proven. | Retail writer attribution, in-range port pointer, normal voice/reap traversal, slot transitions, and no guard-triggered work loss. | One idiom class per build, hangar then mission. Rollback the class and record `ORIGIN:` if any guard/skip is involved. |
| 9 | Integrate or correct CPU-side MORT output only if the complete task/voice matrix shows a MORT-owned gap. | `tools/mort_probe.py` reference output matches the named guest descriptor/type/rate, the CPU voice path consumes it, and the resulting PCM join is nonzero and correctly ordered. | Speech/voice phase with descriptor-class buckets; do not alter RSP dispatch. Rollback the CPU decoder/output change. |
| 10 | Revisit AI/SDL only if a nonzero PCM source exists but the source/consumer or host playback join fails. | Same buffer address, sample count, full byte count, hash, and nonzero span at AI source, callback consumer, and SDL queue. | Host boundary test plus title/hangar phase; rollback host-only bridge change. Do not use `osAiGetStatus=0` as the explanation for absent PCM. |

## Validation row required for every step

The soak summary must report, per phase and arm:

`dispatch → task fields/source → DMEM/DMA → image exit → SP completion →
service → status/slot → voice/reap → MORT class → PCM source → PCM consumer →
route phase`.

The summary is invalid if the whole-RDRAM oracle control, port route control,
or phase transition is absent. Nulls before the target phase are unevaluable.
The current default image path stays unchanged until a complete row selects a
further behavior change and its rollback condition is satisfied; the silent
arm remains available as the same-build control.

## Regeneration and safety

Changes to generated audio diagnostics belong in the fixup scripts. The
required order is `make_elf.py`, N64Recomp, `fixup_game_funcs.py` or
`fixup_factor5_ucode.py`, then CMake. Never hand-edit generated
`RecompiledFuncs/funcs_*.c` for an audio behavior change. Do not enable stock
`aspMain`, remove a safety guard without an `ORIGIN:` line, force a slot/gate
value, or treat a `Broke` return without downstream joins as proof of working
audio.
