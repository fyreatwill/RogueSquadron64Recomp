# M5 — audio de-stubbing plan

Refreshed in session 4765 (2026-10-13). This is the design gate for M5.
Session 4676 revalidated the inventory against the current checked-in
dispatch, RSP-task, fixup, and host-audio code. The active boundaries remain
the real-image/silent dispatch pair, declared-size versus legacy task staging,
private versus shared DMEM ownership, the two MusyX wait gates,
`waitForAnyAudioSlot`, generated safety exits, and the unintegrated MORT
reference decoder. No behavior change or runtime result is claimed by this
refresh; the next work unit remains the phase-gated Step 1 qualification below.
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
| A12 | `waitForMusyXAudioTaskDone` and `shutdownAudioEngine` | **Qualified s4892:** the countdown wait yields by default, and the separate `0x8014974C` producer gate yields by default; explicit `ROGUESQ_AUDIO_SPIN2_YIELD=0` remains rollback. | `musyxSynthFrame` is the named writer for the countdown and named arm/clear owner for the second flag. The same-build default/rollback run had matching producer/wait witnesses and downstream controls, so no yield-causal difference is selected. **ORIGIN:** the guest VI/audio producer writes and clears the legitimate gate; the value is legitimate while active. | Do not repeat this A/B without a new route discriminator. Keep both env arms while pursuing the callback-teardown boundary. |
| A13 | `drainAudioAndFinalizeSpeechBuffer` | The injected `tickMusyXIfActive` is now opt-in; `ROGUESQ_DRAIN_INLOOP_TICK=1` enables the rollback/control arm. A 10,000,000-iteration timeout logs and forces idle. | Slot status writers own the terminal state. The injected tick and forced idle are host-port hatches, not retail behavior. | Validate default-off against the explicit tick-on control. A named status writer followed by clean drain return is required; timeout fire is failure. |
| A14 | `shutdownMusyXVoices` status-`03` loop | Call 3 can spin waiting for `D_80154620` to be cleared; **s4296: spin now yields (`ROGUESQ_A14_YIELD`, default on, `=0` rollback; `tools/apply_s4296_a14_spin_yield.py`, live-tree). No state is forced.** | `stopVoiceSlotSynced` writes `03`; `serviceVoicePoolFrame` is the candidate zeroing writer. The writer must be observed before any force-clear. | **s4694: qualified for the port** — zero store is PC 0x8009B7EC (serviceVoicePoolFrame); yield-on returns, yield-off times out at 10M scans. Trace worker entry and status-zero store. Positive control is worker entry → zero store → shutdown return. No skip or forced zero is authorized. |
| A15 | `ROGUESQ_SPIN_YIELD` at menu/audio spins | Opt-in host yield every 100,000 iterations can allow external VI/SI messages to drain. Default is off. | This is scheduler fairness, not MusyX work. The legitimate host event source is `external_messages`; hardware would preempt the guest spin. | Use only as a route control. It must change host message progress without being counted as audio output. |
| A16 | `librecomp/src/ai.cpp` shims | `osAiGetStatus_recomp` returns `AI_STATUS_FIFO_FULL` (`0x40000000`) when host audio is buffered and zero otherwise; `osAiSetNextBuffer_recomp` queues and returns zero; `osAiGetLength_recomp` reports host buffered bytes. | s4859 qualified the image route through title/hangar with SP and nonzero PCM controls, but observed 1,024 phase-gated `set-next` rows and zero `get-status`/`get-length` rows. Retail independently reached both phases with nonzero AI length and busy status. The status/length shims are not a covered-route PCM explanation. | Do not change them or repeat the caller probe. A future AI change requires a new route discriminator, a positive caller, and nonzero source PCM. |
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
| 1 | **Qualified s4831:** re-baseline the current default image against the same-build silent control before changing any further contract edge. Both arms reached title/hangar; the image produced nonzero PCM while the silent control produced zero PCM. | Both arms reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, with 64 SP completions and no crash/abort. Phase-5 PCM source rows were `nz=768` in the image arm and `nz=0` in the silent arm. | Corrected phase-gated harness `tools/run_m5_yield_ab.sh` uses the documented multi-press autopilot and `ROGUESQ_AUDIO_UCODE=1/0` arms. Keep `=0` as the audio rollback/control; do not repeat the old request-only route. |
| 2 | Promotion to the default image arm is complete in the current source; do not repeat it as an experiment. The SP yield rollback is now one-shot. | The Step 1 row must still show the default image reaches the same title/hangar route as the stub control, completes tasks, preserves the gfx DMEM control, and identifies any downstream divergence. A request-only control must report one yielded result per request, then clear. | Treat this as a completed policy transition, not a new behavior change. `ROGUESQ_AUDIO_UCODE=0` remains the audio rollback; `ROGUESQ_SP_YIELDED_REQUEST_ONLY=1` is the SP-yield control. |
| 3 | **Qualified in s4164:** use the declared audio `ucode_data_size` for the DMEM staging DMA; the current task declares `0x800`, while the legacy path copied `0xF80`. | Both arms retained task dispatch, image `Broke`, SP completion, and route controls. The declared `0x800` arm reached title/hangar without a new failure; legacy staging changed DMEM contents but produced no downstream improvement. | One rebuilt binary with `ROGUESQ_AUDIO_LEGACY_UCODE_DMA=1` and unset, phase-gated at title and hangar. Rollback remains the env arm; no writer or writeback conclusion follows. |
| 4 | **Qualified s4677: no gate/store change authorized.** The port's `0x80094648` writer stores the retail-shaped `0x7F` channel bytes, and the gate remains live at `0x01`; C88 remains done (s2608). | Independent retail writer evidence (s4078/s4166) plus two port arms: title/hangar controls, 30 indexed writer rows per arm, real-image task exit/DMA, and nonzero hangar PCM sanity. | Do not revisit this boundary without a new discriminator. Proceed to Step 5's key-on early-return idiom audit. |
| 5 | **s4678 audit qualified; no behavior change authorized.** The eight key-on early returns remain in place after the complete idiom census. Port divisor inputs were valid (`0xC0`) at every executed divide site; no guard fired. | One rebuilt port arm reached title/hangar; normal key-on tail, slot `02` then `00`, and all route controls fired. Independent retail hangar coverage reached key-on entry/tail with no trap-PC hits. | Do not remove the returns from this evidence alone. Proceed to Step 7's status-03 service-reaping boundary; retain the invalid-input fallback. |
| 6 | **s4200: gate was not in generated code until now (wired into full fixup); drain not entered on title+hangar in tick-on or default arm, A13 dormant there (single-source).** Originally implemented in s2692: remove the in-loop drain tick from the default path; retain the explicit tick-on arm for rollback/control. | Same-run tick-on control and default-off arm must report task/SP completion, named slot/status transition, nonzero PCM joins, and the same route; a timeout or clean route alone is not success. | Same hangar phase, tick A/B in one build. Rollback with `ROGUESQ_DRAIN_INLOOP_TICK=1`. |
| 7 | **s4680 qualified H-status-writer for the covered route.** The exact port store witness recorded `0x8009B7CC` as `0x02 -> 0x03`, then `0x8009B7EC` as `0x03 -> 0x00` for the same slot; retail independently attributed the same publish/reap PCs. Shutdown call-3 was not reached in target phase. | Retail whole-RDRAM, retail title/hangar, port title/hangar, and the new port store control all fired. | Do not change the wait or force-clear status. Proceed to the complete A10 guard-class audit. |
| 8 | **s4852: A9 and A10 covered-route audits are qualified; no guard removal authorized.** A10's same-build default/guard-off pair had valid route-order SP controls, an in-range writer, identical 262 audit/traversal rows, title/hangar, and nonzero PCM in both arms; A9 remains 0 bad in ~2.4M checks at 10/13 sites, with 3 sites unreached. | Independent writer/range evidence, positive SP control, normal voice/reap traversal, slot/PCM progression, and no guard-off divergence. | Do not repeat the A10 A/B. Any future guard work requires a fresh class and explicit origin; select the next M5 contract boundary. |
| 9 | **CLOSED s4475 (no MORT-owned gap).** Integrate or correct CPU-side MORT output only if the complete task/voice matrix shows a MORT-owned gap. | `tools/mort_probe.py` reference output matches the named guest descriptor/type/rate, the CPU voice path consumes it, and the resulting PCM join is nonzero and correctly ordered. | Speech/voice phase with descriptor-class buckets; do not alter RSP dispatch. Rollback the CPU decoder/output change. |
| 10 | **Qualified s4857: no remaining AI/SDL host-queue gap on the covered route.** The same-build image arms reached title/hangar with 78/81 and 60/62 nonzero phase-5 source rows, zero host-error rows, 546/549 successful queue edges, and consumer joins carrying matching source hashes. | Source, consumer, queue, and phase controls all fired in both arms; no failed SDL queue was suppressed into a false consumer join. | Do not repeat without a new host discriminator. Proceed to A13's default-off drain boundary; retain the host bridge fix. |
| 11 | **s4836 qualified:** the generic phase-gated writer table records the legitimate producer arm at `0x80091680` (`1`) and clear at `0x800912F8` (`0`) for `0x8014974C`; the waiting route returns on both arms. The named clear logger's generated anchor is stale/missing, so its absent tag is not a runtime null. Retain `ROGUESQ_AUDIO_SPIN2_YIELD=0` as the same-build rollback. | Both arms reached title/hangar with 64 SP completions, nonzero PCM, gate rows, and no crash/abort. The prior route failure was the diagnostic's unsafe guest-thread observer, removed without changing guest behavior. No yield-causal difference is selected. | Do not repeat the A/B. Treat the generic writer table as the qualified clear witness; repair the named logger only as ordinary diagnostic maintenance if needed. |

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

## Mission-phase qualification row (s4953)

Phase control: the s4950 solo route soak (`scratch/agent/s4950_route_soak/`,
N=5), measured with `tools/vi_progress.py` (VI-progress, not `stalled=1`).

| Phase (viW / origin) | Entered (update_screen #) | Status |
|---|---|---|
| title 1024 / 0x790400 | ~#2900-2990, 5/5 | live |
| 640 / 0x696100 | ~#4470-4565, 5/5 | live |
| mission 512 / 0x690400 | ~#5720-5830, 5/5 | live, but only ~150-260 update_screens long |
| return to title 1024 | ~#5900-6080, 5/5 | live; 3/5 then re-enter 640 at ~#7550-7650 |

Positive control: phase transitions themselves (5/5 identical sequence to
+-1.5 s) and `threadPresent` ordinals advancing to #6960-#8000 at kill. No run
shows VI progress halting after mission entry (last origin change had >=37 rows
after it in every run; the 640-ending runs were killed ~55 s after re-entry).
Open caveat: the 512 phase lasts ~3-4 s before the game returns to title, so it
may be an attract/demo segment rather than a player mission. Audio (pcm) rows
exist in all runs (471 matching lines in run1) but no per-phase M5 contract
claim is made here.

## Mission-phase row (s4963, keyed route s4959, n=2)
Runs 1/2: mission scanout 0x690400 at t=186/185 s, held to t=314 s, crash=0 abort=0, pcm_rows 168, pcm_nz_rows 151/153, sample_nonflat 8641/8611. Audio non-silent in mission; no audio-induced fault. Run3 (s4964): mission onset t=182 s, held to t=307 s (0x690400 -> 0x620400 handoff seen), crash=0 abort=0, pcm_rows 164, pcm_nz_rows 128, sample_nonflat 8455. **n=3/3 valid keyed mission runs, 0 crashes, audio non-silent: H-stable on the keyed route. Steps 0-11 closed; no further de-stub step is open.**
