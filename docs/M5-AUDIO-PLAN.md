# M5 — audio de-stubbing plan

Written in session 1998 (2026-08-19). This is the required investigation-first
design document. This session changes no runtime code and runs no game soak.

## Contract and boundary

The current default is silent, but “audio” is not one missing function:

- `src/main/main.cpp:get_rsp_microcode` sends `M_AUDTASK` to `musyx_stub`, which
  returns `RspExitReason::Broke` without executing the task. Setting
  `ROGUESQ_AUDIO_UCODE=1` selects the already-linked
  `factor5_ucode_b` instead. The toggle is opt-in.
- `src/rsp/aspMain.cpp:aspMain` is a separate stock-ASP stub. It is not a safe
  substitute: the project documents the retail task format as Factor 5
  MusyX-derived, not stock `aspMain`.
- The guest has a MusyX engine, voice tables, song sequencer, DMA-batch
  submission, and audio-task completion waits. The voice-compression material
  identifies MORT as a codec/library boundary inside the MusyX ecosystem. The
  s2134 retail oracle proves that the named voice decode/filter pipeline is
  live on the qualified retail route. The s2135 static census maps the retail
  RSP image to the existing `factor5b_rsp.toml`/`aspMainText` pair at ROM
  `0x9ABE0` and maps the separate uncompressed `speech` MORT asset to ROM
  `0x583D90..0x8A1174`; its 546 descriptors feed the named CPU voice path.
  Do not call `factor5_ucode_b` “the MORT recompile”: it is the existing audio
  RSP image, while MORT is a separate CPU-side sample/codec boundary. The
  remaining task contract question is the retail meaning of the audio task's
  `data_ptr`, `data_size`, `output_buff`, and `data_ptr+0x100` fields.
- s2002–s2003 supplied a task/image attribution for the current opt-in arm:
  `0x80099FE0`/`0x800A4E00` are `aspMainTextStart`/`aspMainDataStart` in the
  companion symbol map, and the ROM split labels `0x9ABE0` as `aspMainText`.
  Its recompiled `SP_WR_LEN` writes changed `0x340..0xFCF` DMEM but produced
  no PCM in the first bridge census. Treat it as an audio-image candidate
  with an unvalidated MusyX/MORT task/output ABI; do not call it graphics from
  the register names alone or promote it until payload-to-AI evidence exists.
- The current generated tree is authoritative for behavior. It has live `=1`
  stores at guest `0x800A0F50` in `initMusyXEngine` (`0x8008E9F8`),
  `setDisplayMode` (`0x8008EB40`), and `reapplyDisplayMode` (`0x8008EC88`),
  with zeroing stores in their entry/failure paths and in
  `shutdownMusyXEngine`/`musyxNoopStub`. The historical force-zero comment in
  `../N64Recomp/fixup_game_funcs.py` does not match the current generated
  `funcs_23.c` because its regex does not account for the intervening
  `rs64_probe_submit_gate_store` line. Reconcile this before changing a gate.

## Complete current inventory

“Current” below means present in the generated/runtime tree, not merely
mentioned in an old plan. Diagnostic-only probes are listed separately after
the table; they must not be mistaken for behavior changes.

| ID | File and symbol | Current behavior | Guest contract; ownership | Writer / consumer | Reversible change and same-run positive control | Phase, soak, rollback |
|---|---|---|---|---|---|---|
| A1 | `src/main/main.cpp:get_rsp_microcode` → `musyx_stub` | Default `M_AUDTASK` returns `Broke`; `ROGUESQ_AUDIO_UCODE=1` selects `factor5_ucode_b`. s2160 default-on (unset and `=1`) SIGSEGV'd in `waitForAnyAudioSlot+1060` before title; polarity reverted. s2161: guest `D_80141AD0` is a legitimate `setDisplayMode`/`reapplyDisplayMode` store; the port +1060 load was unsigned PATCH `MEM_BU(0X1AD0, 0X80140000)` (host `rdram+4GB+0x141AD3`) on a `gate0` path that original wait MIPS does not load. s2162 `S32`-addressed those PATCH sites (`H-UnsignedMemBu`): same-build `=1` returns from wait (`c=0x11`/`0x10`) and reaches title+hangar; stub `=0` still does. s2163 default-on retry (`H-CinematicRegress`): unset matched `=1` at dispatch/wait but 0/3 unset and 0/2 `=1` reached title (cinematic SIGBUS or 640 stall); same-build `=0` retry reached title+hangar; polarity reverted. s2164 `H-NoSuchSite`: no unsigned KSEG0 `MEM_*` constants in the two cinematic SIGBUS functions. s2165 `H-RetailExecsValidPtr`: retail executes both crash PCs at VI 640/`0x00696100` with KSEG0 `$s1`/`$v0` (not 0). s2166 `H-RetailWriterNamed`: retail ORIGIN of `$a2+0x50` is `0x800A8144` heap `0x8025A580`. s2167 `H-PortStoreMatchesRetail`: port stores and reloads that same word; image SIGBUS is later in `matchKeywordWithPriority`. s2168 `H-RetailValidV0`: retail `$v0` at `0x800AF2CC` is `0x800CDB58` (KSEG0, not `0x80000000`); `$a0=0x802231EC` from `spawnCutsceneEffectsAndCues` `0x800A9248`. s2169 `H-PortMatchesRetailUntilLater`: port loads those retail-class values (wild=0); image 640-stalled after logged n=150. s2170 `H-NoHangAtN150`: n=150 returned (n=151 same timestamp); both arms continue to n=264 and reach title+hangar. s2171 `H-NullV0At87A8`: a failing `=1` soak refutes the four hang hyps; SIGBUS is `0x800A87A8` `lwc1 0x44($v0)` with `$v0=0` after a good `+0x50=0x8025A580`. s2172 `H-RetailHeap0NeverZero`: retail writer of phys `0x25A580` is `walkMeshdef0List` `0x80057100`; first-slot word0 is `0x800CA748`. s2173 `H-PortHeap0MatchesRetail`: port stores and reloads that same word on both arms; completing `=1` reached title+hangar with lwc zero_logged=0. `H-CinematicRegress` remains intermittent. | `M_AUDTASK` must execute the retail audio task and complete its SP/DP contract. Task ownership is MusyX-derived; MORT ownership is not established. | Guest `submit_rsp_task` writes an `OSTask`; `librecomp/rsp.cpp:run_task` stages DMEM and calls the selected function. | Keep the toggle. Both dispatch arms are validated at s2118 C88=0 and s2162 current-recipe title/hangar scope. s2163 reverted default-on after `H-CinematicRegress`. s2164–s2173 closed the unsigned-constant, retail-null, writer-named, missing-port-store, retail-wild-header, port-wild-header, hang-inside-n=150, failing-run hang-hyp, retail-zero-word0, and missing-port-word0-constructor leads. Do not re-flip, S32-address, NULL-skip, skip/allow `matchKeywordWithPriority` or the lwc, or add a wait/slot guard. | Boot through title/menu, VI-gated. Treatment rollback is unset `ROGUESQ_AUDIO_UCODE` until default-on lands, then `=0`. |
| A2 | `src/rsp/aspMain.cpp:aspMain` | Always returns `Broke`; not selected by the RS64 dispatch table. | Stock `aspMain` has a different task ABI/format and is not the retail implementation. | No live caller in this target. | Do not enable it. Positive control for any future replacement is a known-good stock-ASP task, not an RS64 `M_AUDTASK`. | Out of M5 execution until task format is proven; rollback is deletion of any experimental dispatch arm. |
| A3 | Guest gate `0x800A0F50`: `initMusyXEngine`, `setDisplayMode`, `reapplyDisplayMode`, `shutdownMusyXEngine`, `musyXNoopStub` | The three init/display tails write `1`; entry/failure/shutdown/no-op paths write `0`. Consumers branch on this byte. | This is the guest’s MusyX enabled/disabled state, not a host audio-device flag. | Writers are the named guest functions; consumers include `tickMusyXIfActive`, `musyxSynthFrame`, `waitForMusyXAudioTaskDone`, and `musyxNoopStub`. | Before flipping any store, compare generated output to the fixup anchor and ask the retail oracle which physical address writers fire and from which PCs. Positive controls in the same oracle run: whole-RDRAM watch plus the narrow target watch; port evidence must show the named writer’s value transition and a downstream task/slot outcome, not a writer counter alone. | Boot/title and hangar `VI 512 origin=0x006AB400`; use the Rice eleven-Start driver. Roll back by regenerating and restoring the exact store semantics, not by adding a second host guard. |
| A4 | `funcs_23.c:tickMusyXIfActive` | Returns immediately when `0x800A0F50 == 0`; otherwise acquires the Factor 5 mutex, ticks songs/voices, stops synth voices, and releases the mutex. | Guest audio engine scheduling; MusyX-side. It is not evidence that the RSP task completed. | Gate byte is written by A3; consumers are song/voice population and reaping. | Do not bypass this gate in the first RSP experiment. Later, reverse one writer at a time only after A1 task completion and A3 retail writer attribution are known. Positive control is a nonzero voice/slot transition plus a completed task, not entry count alone. | Gate-reversal step must be phase-gated at title and hangar; rollback one store at a time. |
| A5 | `funcs_24.c:musyxKeyOnVoice` | Eight generated `break` divide/overflow sites are replaced with early returns (`0x80090CEC`, `0x80090D04`, `0x80090D30`, `0x80090D48`, `0x80090D74`, `0x80090D8C`, `0x80090DB8`, `0x80090DD0`). | These traps protect invalid voice arithmetic in the currently incomplete/degenerate path. They are not proof that the inputs are illegitimate once real MORT/MusyX descriptors arrive. | Voice descriptors and channel records are writers; `musyxKeyOnVoice` consumes them. | Keep until a descriptor census proves the divisor/range contract. Replace one class only with a checked, contract-matching implementation. Positive control must show valid key-on records reaching the normal tail and a corresponding slot status transition. | Hangar VI 512; use `ROGUESQ_LOG_VI_CALLERS=1` and slot writer probes. Roll back the individual fixup class if valid records stop or a new trap appears. |
| A6 | `funcs_24.c` voice-array base guards | Ten entry guards (including `musyxInitVoiceFromSample`, `musyxStoreVoiceAdsrParams`, `musyxTriggerVoiceAttack`, stop/release/pitch helpers) and two loop-scoped guards in `musyxMixActiveVoices`/`musyxSynthFrame` return or skip when the voice base is outside KSEG0 RDRAM. | Defensive port safety; the legitimate contract is a live voice-array pointer in `0x80000000..0x807FFFFF`. | `allocateSongChannelArray` publishes the base/count; all MusyX voice functions consume it. | Do not remove as “audio de-stubbing.” First obtain retail PC/write evidence for the base and a port positive control showing valid in-range base plus slot activity. Any future relaxation needs an `ORIGIN:` naming the writer. | Hangar VI 512 and mission only after input path is restored; rollback each guard class independently. |
| A7 | `funcs_26.c:tickAndReap3DAudioVoices`; `funcs_25.c` song-tempo users | One voice-list-node range guard and 43 song-tick-table pointer guards skip invalid pointers rather than dereferencing them. | These are M3 safety patches around MusyX lists/sequencer tables, not the RSP stub. | Guest list/table allocators write the pointers; reaper and sequencer consumers read them. | Leave in place while bringing up audio. Audit or relax only as a separate idiom-class work unit with writer attribution. Positive control is valid list/table traversal and a matching retail write, not zero guard hits. | Not part of the first M5 toggle; rollback is the generated patch regeneration. |
| A8 | `funcs_15.c:waitForAnyAudioSlot` | The original unbounded `anyAudioSlotActive` loop has a default 500,000-iteration escape; `ROGUESQ_WAITFORSLOT_GUARD_CAP` changes the cap. | Guest waits for an audio slot condition; escape is a port safety hatch, not a completed audio task. | `isAudioSlotActive` reads the voice table; MusyX render/key-on/reap paths write slot bytes. | Keep the guard while real timing is exercised. A future removal requires a same-run proof that a valid slot reaches the expected terminal state. Positive control is a live slot-byte transition and guard-fire count of zero in the normal arm. | Pre-title and hangar phases; rollback by unsetting the experimental cap only if the default guard remains. |
| A9 | `funcs_24.c:waitForMusyXAudioTaskDone` and `shutdownAudioEngine` | The countdown spin on `0x8014998A` now pumps `musyxSynthFrame` up to 64 times. `ROGUESQ_AUDIO_WAIT_NOPUMP=1` restores the original blind spin. A second spin on `0x8014974C` remains unbounded; its current probes are diagnostic only. | The countdown must be decremented by the real audio pipeline; the flag spin is a separate guest synchronization contract. | `waitFor...` seeds/reads `0x8014998A`; `musyxSynthFrame` is the known decrementer and task producer; the owner of `0x8014974C` must be identified. | Treat the pump as a mitigation, not an explanation. First map the retail writer/consumer for both words and compare a pump-on/off arm in one build. Positive controls: countdown reaches zero and a real `M_AUDTASK` completes; `ROGUESQ_AUDIO_WAIT_NOPUMP=1` must reproduce the known failure mode if the control is valid. | Boot/title VI 320→640; do not run the blind-spin arm as an unattended soak. Roll back by disabling only the pump toggle. |
| A10 | `funcs_30.c:drainAudioAndFinalizeSpeechBuffer` | The spin has an injected `tickMusyXIfActive` by default; `ROGUESQ_DRAIN_INLOOP_TICK=0` skips it. After 10,000,000 iterations it logs and forces idle. | The ROM drain waits for slots; injected ticking and forced idle are port behavior, not the retail contract. | Slot status is written by render/release/service paths; drain reads it. | Do not default the injection off or remove the timeout until the status-3 worker starvation is explained. Positive control is a slot transition caused by a named writer plus a clean drain return; a timeout fire is evidence of failure, not success. | Hangar VI 512; exact driver is `scratch/s73_post_a_scene/run_mission_keys.sh` with eleven-Start equivalent. Roll back with `ROGUESQ_DRAIN_INLOOP_TICK=0` for the comparison arm; retain the timeout as a diagnostic hatch. |
| A11 | `funcs_26.c:shutdownMusyXVoices` | Call 3 can spin on `D_80154620` status `0x03`; there is no default timeout or yield. s1997 found no armed `serviceVoicePoolFrame` entry during this spin. | Voice shutdown waits for the service worker to clear the status; this is a live scheduler/worker contract, not a reason to skip shutdown. | `stopVoiceSlotSynced` writes status `0x03`; `serviceVoicePoolFrame` is the named zeroing writer in retail. | First trace worker dispatch and retail writer PCs. Do not add a skip or force-zero mitigation. Positive control is an armed worker entry followed by a status-zero store and shutdown return. | Hangar VI 512, after M5 plan; rollback means reverting only a future diagnostic, not the status value. |
| A12 | `ROGUESQ_SPIN_YIELD` patches in menu/audio spins | When enabled, yields for 1 ms every 100,000 iterations at menu init, menu input, and audio drain. Default is off. | Scheduler fairness workaround for cooperative host threads; not part of MusyX or MORT. | Host external-message delivery is starved by runnable guest spins; spin sites are consumers. | Use only as a same-run scheduler control, never as an audio fix. Positive control is host VI/SI dequeue progress, with guest audio counters unchanged. | Title/hangar phase gates; rollback is unset env. |
| A13 | `lib/N64ModernRuntime/librecomp/src/ai.cpp:osAiGetStatus_recomp` (not a jal target); live shortcut is `osAiSetNextBuffer_recomp` skipping `__osAiDeviceBusy` | `osAiGetStatus_recomp` always reports `0`. `osAiSetNextBuffer_recomp` queues and returns `0` with no FIFO-full check. | s2152: retail polls AI status only via `__osAiDeviceBusy` inside `osAiSetNextBuffer` (1:1). Named `osAiGetStatus`/`osAiGetLength` are absent. s2153: on the covered title/hangar route the busy check never returns FIFO-full (reject PC `0x80029EF0` = 0; success `0x80029EF4` = set-next = busy = 7983). Generated `runAiAudioStreamPlaybackLoop` ignores v0 at both jals. | Guest `runAiAudioStreamPlaybackLoop` jals `osAiSetNextBuffer`; that function jals `__osAiDeviceBusy`. Host `queue_audio_buffer` submits PCM. | Do not change `osAiGetStatus_recomp` or `osAiSetNextBuffer_recomp`. s2153 selected `H-BusyAlwaysClear`; always-queue return-0 is observationally equivalent on this route. Host SDL fullness is not the N64 AI FIFO. Positive control was whole-RDRAM plus live set-next/busy/success through title/hangar. | A13 closed at sampled retail title/hangar scope; rollback remains the current always-queue `osAiSetNextBuffer_recomp`. |
| A14 | `src/main/main.cpp:set_frequency`, `queue_samples`, `get_frames_remaining`; `ultramodern/src/audio.cpp` | SDL device is opened at requested frequency; failure leaves no device. PCM queueing now converts sample count to bytes correctly. Remaining frames are zero if no device is open. Missing callbacks are no-op by runtime contract, but this target registers all three. | Host bridge owns SDL buffering; guest/RSP owns PCM production. MORT/MusyX decoding must precede this bridge. | `osAiSetNextBuffer` calls `queue_audio_buffer`; callback calls `SDL_QueueAudio`. | Keep the byte-count fix. Validate nonzero PCM separately from device success. Positive controls: known nonzero synthetic callback data in a host-only test and `ROGUESQ_LOG_PCM_SANITY` with real ucode; all-zero PCM is a failure result, not a control. | Audio callback phase after RSP task completion; rollback is a callback-only change. |
| A15 | `lib/N64ModernRuntime/librecomp/src/rsp.cpp:DmemGuard` and `main.cpp:g_lle_task_mutex` | All RSP task staging/execution, including opt-in audio, serializes on the shared global `dmem[]` mutex. | One emulated RSP has one DMEM; serialization is required. This is an invariant, not a stub. | GFX LLE and SP/audio task paths both use the lock. | Do not remove or parallelize. Positive control is a gfx DMEM canary remaining unchanged across an audio task. | Every RSP task phase; rollback means restoring the lock before any other experiment. |

The generic `unknown_task_stub` in `main.cpp` is intentionally outside M5: it
handles malformed task types, not `M_AUDTASK`. Likewise, the many
`ROGUESQ_LOG_*` voice, slot, DMA, and gate probes are instruments, not
de-stubbing changes. They should be armed in every M5 soak, but a probe hit is
not a positive control unless it marks the mechanism’s expected state change.

## Competing hypotheses and discriminator

| Hypothesis | Prediction | Discriminating measurement |
|---|---|---|
| H-MORT-path | The missing work is a MORT/voice-codec boundary; selecting the current RSP image without naming that ABI cannot produce valid samples. | Independent retail task/ROM-segment attribution plus a port task descriptor/PCM census. A MORT-owned descriptor or decoder path selects the MORT artifact first. |
| H-degenerate-host-path | The immediate `Broke` stub and host shortcuts are the first safe layer to remove; current guest data is otherwise structurally usable. | Same-build `musyx_stub` versus `factor5_ucode_b`, with direct dispatch completion, task exit reason, slot transition, and PCM controls. A completed task with valid slots selects the host/RSP step; zero valid data does not. |
| H-MusyX-mismatch | `aspMain` cannot consume this task format; enabling it will hang or corrupt the audio task. | A known MusyX task-format witness and a controlled `aspMain` negative arm. The negative arm must be isolated and never be the default. |
| H-scheduler-independent | The s1997 status-3 hang is worker starvation independent of decoder correctness. | With audio implementation held constant, correlate worker entry/status-zero writes against the status-3 spin; an absent worker entry with a retail worker writer selects scheduler dispatch, not an audio-codec explanation. |

The first measurement is therefore not “did a counter print.” It is a complete
row of: retail writer/consumer attribution, direct `M_AUDTASK` dispatch and
exit, guest slot transition, and PCM nonzero/silence result. A null without the
same-run whole-RDRAM/oracle control is unevaluable.

## Incremental execution sequence

Every step is one work unit. Build all A/B arms in the same build, phase-gate
on VI transitions, and enqueue the soak rather than babysitting it. Every
recipe must arm `ROGUESQ_LOG_ALL`, `ROGUESQ_LOG_PCM_SANITY`,
`ROGUESQ_LOG_WAITFORSLOT_GUARD`, `ROGUESQ_LOG_AUDIO_DRAIN`,
`ROGUESQ_LOG_AUDIOTICK_TRACE`, and the voice/slot diagnostics from
`docs/debug-trace-env-vars.md`; keep `ROGUESQ_SPIN_YIELD` off unless it is the
explicit control arm.

1. **Ground truth and regeneration reconciliation.** Run the retail oracle
   positive control before adding instrumentation: whole-RDRAM write watch
   (`--watch-write 0x0:0x800000`) must fire, then a separate target watch for
   physical `0xA0F50`, `0x14998A`, and the audio-task/AI structures must name
   retail PCs. Reconcile the generated `0xF50` stores against
   `fixup_game_funcs.py`. Positive control: oracle whole-RDRAM count and a
   port `audtask-dispatch` count in the same phase. Soak: one 30-second retail
   oracle run plus one port boot/title run from the existing driver, no code
   change. Rollback: none; this is contract capture.
2. **Validate the existing opt-in RSP arm.** Use one build with default
   `musyx_stub` and `ROGUESQ_AUDIO_UCODE=1` arms. The direct discriminator is
   dispatch count, `RspExitReason`, DMEM canary, slot status transition, and
   PCM nonzero count. Soak command for the treatment is:
   `env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh m5-audio-step2 30 12`.
   Run the unset-env control from the same build and phase schedule. Rollback:
   unset `ROGUESQ_AUDIO_UCODE`.
3. **Resolve guest gate semantics one site at a time.** Do not reverse all
   `0xF50` stores. First instrument/observe the three writers and the two
   zeroing consumers, then test exactly one writer arm with the RSP arm held
   constant. Positive control is the retail PC attribution plus a guest
   gate-write count and a task/slot outcome. Soak: the step-2 command with
   `ROGUESQ_AUDIO_UCODE=1` and only one generated store changed. Rollback:
   regenerate and restore that store.
4. **Remove or replace the eight key-on early returns only after valid input
   is proven.** Use the descriptor fields and divisor values from the same
   run; preserve a checked fallback for invalid records. Positive control is
   normal key-on tail + slot `0x02` + eventual `0x00`, not entry count. Soak:
   hangar eleven-Start recipe, VI `512 / 0x006AB400`; rollback the single
   key-on fixup class.
5. **Replace waits with the real completion contract.** Audit the countdown
   decrement, `0x8014974C` worker flag, `waitForAnyAudioSlot`, drain timeout,
   and status-3 shutdown together only after steps 2–4 produce real voice
   transitions. Positive control is named writer → observed value transition
   → caller return. Soak: 600-second hangar recipe with the pump/timeout
   toggles recorded; rollback each wait change independently. A timeout fire
   is a failure and must not be promoted.
6. **Validate PCM and AI ordering.** With real voice/codec data, require
   nonzero PCM before changing `osAiGetStatus_recomp` or SDL behavior. Positive
   control is host-only known nonzero PCM plus real-ucode `pcm-sanity`; a live
   SDL device alone proves nothing. Soak: title/hangar VI transition followed
   by the same 600-second hangar recipe; rollback host callback changes only.
7. **MORT boundary work.** The s2134 retail oracle now satisfies the
   independent codec-side entry condition: all seven named decode/filter
   functions executed after the whole-RDRAM and title/hangar controls, with
   `musyxSynthFrame` and `osAiSetNextBuffer` in the same run. s2135 mapped the
   retail RSP image to the existing `factor5b_rsp.toml` pair and mapped MORT
   to the separate 546-entry `speech` asset consumed by CPU voice routines;
   no new MORT RSPRecomp config is justified by the static boundary. The
   s2136 retail oracle census passed its whole-RDRAM control, reached title
   and hangar, observed `ucode=0x80099FE0`, `ucode_data=0x800A4E00`, nonzero
   `data_ptr`/`data_size`, and zero writes to both output-buffer fields. This
   selects `H-RetailTaskMatchesFactor5b` at the task-field boundary. s2137
   then selected the matching port task/DMA boundary, including the sampled
   `field348+0x100` destination relation. s2140 closed the sampled retail
   `data_ptr+0x100` write boundary. s2138 compiled the named independent
   MORT decoder and decoded four 8000-Hz/type-0 speech rows; s2139 covered
   types `1,2,3,5` with both rates present; s2151 covered type-0 at 16000 Hz
   and type 4 (16000-only in the speech table). All six descriptor types and
   both rates now have at least one complete nonempty reference row. The
   remaining-class work is closed. s2152 closed the A13 presence/execution
   half: named `osAiGetStatus` is absent from TOML/`funcs.h`/overlays and
   is not a jal target; retail polls AI status only via `__osAiDeviceBusy`
   inside `osAiSetNextBuffer` (1:1, `7958` executions after whole-RDRAM
   and title/hangar gates). s2153 closed the reject/success half:
   `H-BusyAlwaysClear` at the covered route (reject `0`, success =
   set-next = busy = `7983`; caller ignores v0). Do not change
   `osAiGetStatus_recomp` or `osAiSetNextBuffer_recomp`. s2154 selected
   `H-CanaryComputedOnly` for the image-arm canary: no generated
   immediate in `0xF80..0xFBF`; the host `0xF80..0xF8F` gap sits inside
   the mix buffer `0xE50..0xFCF` (`span 0x180`, writers `L_1CDC` /
   `L_15F8` / `L_1EF0`). `canary_ok=0` is that working set, not a
   runaway write, and no longer blocks the `break 0`/`Broke` edge as
   unexplained corruption. s2155 then selected
   `H-CanaryOnlyInUcodeData`: mix `0xE50..0xFCF` is continuous, the
   `0xF7F..0xFC0` gap has no unused byte, and the only unused
   `>=0x10` holes in `0x000..0xFBF` sit inside ucode-data
   (`0x000..0x21F`, `0xA40..0xC2F`). A relocated host canary has
   nowhere to live in DMEM. s2157 selected `H-CanaryLogOnly`: every
   `canary_ok` site in `rsp.cpp` is storage or a fprintf/probe field;
   `run_task` completes on `Broke` alone; DMA recording ignores the
   flag (`scratch/agent/s2157_canary_host_effect.txt`). `canary_ok=0`
   no longer blocks the `break 0`/`Broke` edge as a host-side gate.
   s2158 selected `H-IsolatedOnlyByEnv`
   (`scratch/agent/s2158_image_arm_isolators.txt`): the live
   `RspUcodeFunc*` is assigned only in `get_rsp_microcode` from
   `ROGUESQ_AUDIO_UCODE`; `run_task` always calls that pointer;
   the env-true wrapper calls `factor5_ucode_b`, not `musyx_stub`.
   s2159 selected `H-PolicyOnly`
   (`scratch/agent/s2159_image_arm_default_blockers.txt`): every
   named keep-opt-in sentence in CURRENT-TRUTH, this A1 row, and the
   `get_rsp_microcode` hang comment is closed-by-selected-hypothesis
   or policy-comment. The A1 execute / SP-complete / MORT-ownership /
   both-arm-validate / task-exit+PCM / two-source-completion clauses
   are already selected (s2118, s2132–s2140, s2157). Remaining
   isolation is the env default plus historical comments, not an
   unsatisfied host-task contract. s2160 executed the A1 default-on
   flip and selected `H-RouteRegress`
   (`scratch/agent/s2160_default_on_ab.txt`): unset and `=1` both
   SIGSEGV in `waitForAnyAudioSlot+1060` from `menuOverlayInit`
   (`si_addr=0x400141ad3`); same-build `=0` reached title and hangar
   with the stub contract. Default polarity was reverted. s2161
   selected `H-RetailLoadsCount` and named the +1060 load as unsigned
   PATCH `MEM_BU(0X1AD0, 0X80140000)` on a `gate0` path. s2162
   selected `H-UnsignedMemBu`
   (`scratch/s73_post_a_scene/s2162_s32_membu_ab.txt`): after
   `S32`-addressing those PATCH sites, same-build `=1` returns from
   wait and reaches title+hangar. s2163 executed the default-on
   retry and selected `H-CinematicRegress`
   (`scratch/s73_post_a_scene/s2163_default_on_ab.txt`): unset
   matched `=1` at dispatch/wait; both failed title at 640
   `0x00696100`; same-build `=0` retry reached title+hangar.
   Polarity reverted. s2164 selected `H-NoSuchSite`.
   s2165 selected `H-RetailExecsValidPtr`. s2166 selected
   `H-RetailWriterNamed`. s2167 selected
   `H-PortStoreMatchesRetail`
   (`scratch/agent/s2167_port_store_ab.txt`): port
   `0x800A8144` stores heap `0x8025A580` at dest
   `0x800C7B0C` and the consumer load matches; image-arm
   SIGBUS is later (`matchKeywordWithPriority+88`). s2168
   selected `H-RetailValidV0`. s2169 selected
   `H-PortMatchesRetailUntilLater`
   (`scratch/agent/s2169_match_kw_ab.txt`). s2170 selected
   `H-NoHangAtN150`
   (`scratch/agent/s2170_match_kw_flow_ab.txt`): n=150
   returned; both arms reach title+hangar. s2171 selected
   `H-NullV0At87A8`. s2172 selected
   `H-RetailHeap0NeverZero`. s2173 selected
   `H-PortHeap0MatchesRetail`
   (`scratch/agent/s2173_heap0_store_ab.txt`): port
   `0x80057100` stores `0x800CA748` at dest `0x8025A580`
   and `0x800A87A0` reloads it; completing `=1` reached
   title+hangar. Next unit is a failing `=1` cinematic
   with the s2173 always-log (soak
   `s2173_image_heap0_fail`), not another default-on
   flip and not S32-addressing by guess.
   Rollback remains unset `ROGUESQ_AUDIO_UCODE`.

No step may default stock `aspMain`, remove a safety guard without an ORIGIN,
or treat a forced-idle/skip/yield as an explanation.
