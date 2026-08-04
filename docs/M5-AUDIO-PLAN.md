# M5 — audio de-stubbing plan

Written s298. Investigation-first per the M5 goal-stack entry in `docs/CURRENT-TRUTH.md` — this is
a design doc, no code changes in this session. Survey done by 3 parallel agents (fixup/toml/env-var
grep, runtime dispatch/DMEM/SDL grep, PORTING-STATE crash-history grep); findings below are sourced
from that survey, not re-derived from memory.

## 1. Where audio is actually stubbed today (one point, not many)

Contrary to the loose framing in the M5 goal-stack entry ("the MusyX ucode already recompiles ... as
a never-called artifact"), the stub is a **single function pointer swap**, and everything else
audio-related in the codebase is either a downstream defensive reaction to it or genuinely unrelated:

- **The actual stub**: `musyx_stub()` in `src/main/main.cpp:110-112` — registered as the `M_AUDTASK`
  handler in `get_rsp_microcode()`'s dispatch switch (`main.cpp:594-595`, `case M_AUDTASK: return
  &musyx_stub;`). It returns `RspExitReason::Broke` immediately with **zero ucode instructions
  executed** — the game thinks the audio task completed instantly. `factor5_ucode_b` (the recompiled
  MusyX ucode, from `factor5b_rsp.toml` → `factor5_ucode_b_recompiled.c`) is compiled, linked, and
  declared (`main.cpp:78`) but the dispatch switch never returns it — dead code at runtime, not
  broken code.
- **The guest-side reinforcement**: `N64Recomp/fixup_game_funcs.py:94-101` force-zeros the
  audio-engine-enable gate byte (`0x800A0F50`) at its 3 store sites (`initMusyXEngine`,
  `setDisplayMode`, `reapplyDisplayMode`), so the *guest game code itself* believes audio is off and
  takes its own degenerate paths, independent of the RSP-side stub. Comment in the patch: "force
  audio-engine-disabled (MusyX stubbed; spin-wait wedges coop scheduler)" — this was a **fix**, not
  an arbitrary choice (see §3, crash family #1).
- **Downstream of the gate**: 8 `musyxKeyOnVoice` divide-by-zero/overflow compiler traps
  (`fixup_game_funcs.py:113-123`) replaced with early `return` — needed because voice data is
  uninitialized (a direct consequence of the engine never running), not an independent disable.
- **Independent of the gate**: the `allocateSongChannelArray` count/pointer race fix (s147,
  `fixup_game_funcs.py:2318-2400`) is a real correctness fix in code that runs every VI-retrace tick
  regardless of the enable gate (`musyxSynthFrame`'s bookkeeping is unconditional). This stays as-is
  through de-stubbing — it is not part of the stub, don't touch it.
- **~15 env-gated diagnostic loggers** already exist covering the audio call chain end to end
  (`ROGUESQ_LOG_AUDIO_DRAIN`, `_VOICE_TRIGGER_CHAIN`, `_MUSYX_DMA_CALL`, `_INIT_VOICE_SAMPLE`,
  `_SONG_ARRAY_LIFECYCLE`, `_VOICE_ACTIVE_GATE`, `_VOICE_CURSOR`, `_STREAM_NODE_INIT`), all default
  OFF. These are exactly the instruments the de-stubbing soaks below need — no new logging plumbing
  required, just arm them.

**Open question RESOLVED (s300, step 1 of §4): task submission is NOT gated.** Source-read of
`tickMusyXIfActive` (`N64Recomp/RecompiledFuncs/funcs_23.c:6785`) and `musyxSynthFrame`
(`funcs_24.c:3146`), both reading the same gate byte (`lui $v0,0x800A` / `lbu $v0,0xF50($v0)` =
`0x800A0F50`):

- `tickMusyXIfActive` (called from ~15 gameplay sites across `funcs_15/28/29/30/40/41/42/43.c`) DOES
  fully short-circuit on gate==0 — a single `beq $v0,$zero,L_8008DA3C` at its very top skips
  `factor5MutexAcquire`, `tickActiveSongs`, `tickAndReap3DAudioVoices`, `stopAllSynthVoices`,
  `factor5MutexRelease` entirely. This is where songs/voices would normally get added.
- `musyxSynthFrame` — the **separate**, per-VI-retrace tick (confirmed s101 called via
  `viRetraceHandlerThread`, independent of `tickMusyXIfActive`) — checks the same gate byte 5 times
  in its body but only ever uses it to skip narrow slices: `update3DAudioFrame` (1 check,
  `0x800912A8`) and, inside the per-voice loop, `tickAllActiveSongs`/`tickAudioSequencerFrame` (a
  2nd read of the same byte at `0x8009145C`, re-checked because the loop runs once per voice). The
  voice-mixing call (`musyxMixActiveVoices`) and the DMA-batch/task-submission call
  (`LOOKUP_FUNC(ctx->r3)` at `0x80091684`, confirmed by the s102 diagnostic comment at that exact
  site to be `submitDmaRequestBatch`) sit on the **unconditional** path after the gate checks — no
  branch skips them when the byte is 0.
- Corroborating structural evidence, independent of this trace: crash family #1 (`docs/M5-AUDIO-PLAN.md`
  §3) — the original *incomplete* stub caused a **boot-time scheduler wedge**
  (`waitForMusyXAudioTaskDone` spinning on a countdown only real ucode execution decrements). That
  hang could only happen if the RSP audio-task pipeline (submission → dispatch → completion) already
  runs every frame regardless of the gate — otherwise there would be nothing for the incomplete stub
  to fail to complete. The existence of that historical crash family is itself independent proof that
  `M_AUDTASK` submission is not gate-suppressed.

**Both lines of evidence agree**: swapping `musyx_stub` → `factor5_ucode_b` (step 2) is **not** a
provable no-op — it is a live first exercise of the recompiled ucode, on every VI retrace, on
whatever (largely degenerate, since `tickMusyXIfActive`'s song/voice population is fully gated off)
task data `musyxSynthFrame` currently produces. Per §4 step 2's own outcome-2 branch, this needs
soak scrutiny from the start, not a trivial "did the phase timeline change" check.

**s173 contradiction, also resolved this session**: `PORTING-STATE.md` Session 173 inferred the gate
byte was "nonzero mid-run" from a crash backtrace passing through `tickMusyXIfActive`'s body (only
reachable past the gate check). A full-tree grep of every store to offset `0xF50` off base `0x800A`
found exactly **one** site that ever writes a value other than a hardcoded literal 0:
`initMusyXEngine` (`funcs_23.c:9537`, `sb $v0,...` where `$v0=1` on init success) — and that is the
exact site `fixup_game_funcs.py:94-101`'s regex force-zeros. `setDisplayMode`, `reapplyDisplayMode`,
`shutdownMusyXEngine`, and `musyxNoopStub` all contain their own **native** `sb $zero,0xF50($at)`
(hardcoded 0, needs no patch, already always-0). So under the patch, nothing in the recompiled guest
code can ever legitimately set that byte nonzero — if s173's inference was accurate, the only
remaining explanations are (a) the patch wasn't applied in that build, or (b) a wild/corrupting write
clobbered ordinary BSS at that address, consistent with this project's dominant crash theme. Not
investigated further this session (out of step-1's scope) — flagged for whoever next touches the
`waitForAnyAudioSlot`/crash-family-#3 thread, since a corrupted gate byte would be a new, previously
unconsidered mechanism for that family.

## 2. The DMEM-sharing question is already answered — it's not new work

The M5 goal-stack entry frames "how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization built in s5)" as an open design question. It isn't — s5's mechanism already handles
this and requires no new work:

- There is exactly **one** global `uint8_t dmem[0x1000]` (`N64ModernRuntime/librecomp/src/rsp.cpp:13`),
  shared by every RSP task regardless of type.
- `rs64_dmem_lock`/`rs64_dmem_unlock` (weak hooks declared `rsp.cpp:40-41`, `DmemGuard` wraps
  `run_task`'s staging+execution) are strongly implemented in `src/main/main.cpp:184,189-190` as a
  single `std::recursive_mutex g_lle_task_mutex`, taken by **both** `rs64_dmem_lock/unlock` and the
  gfx LLE runner (`factor5_gfx_runner`) before touching `dmem[]`.
- This mutex exists *because* concurrent gfx/audio DMEM access was already found to corrupt state
  ("trig-looking data over the dispatch tables", `main.cpp:176-183`) — it is the s5 fix for exactly
  the hazard the goal-stack entry worries about. Audio and gfx RSP execution are already fully
  serialized through this one lock; enabling real audio ucode execution does not require any new
  synchronization design, only exercising the existing one under a case (audio) it hasn't run
  through since the lock was added.
- Genuine future risk, not a blocker: true gfx/audio *concurrency* (as opposed to correct
  serialization) is not on the table without per-task DMEM storage, since the memory itself is
  shared, not just its access. Out of scope for de-stubbing — the game only needs correct
  serialized execution, not parallelism, to produce audio.

## 3. What flipping the gate byte implies — and the actual crash-risk balance

Reversing the gate-byte force-zero makes the guest game code itself believe audio is enabled,
activating voice-triggering, `tickMusyXIfActive`, real `waitForAnyAudioSlot` waits, and real
`allocateSongChannelArray` traffic — paths that today mostly run in a degenerate all-empty state.
The PORTING-STATE crash history for the 4 documented audio-adjacent crash families is more mixed
than the goal-stack's rationale ("several recurring crash families are plausibly artifacts of the
audio-disabled degenerate paths") suggests — worth stating precisely before spending soak budget:

| # | crash family | status | relationship to the audio-disable stub |
|---|---|---|---|
| 1 | Boot-time scheduler wedge (`waitForMusyXAudioTaskDone` spin on a countdown only real ucode decrements) | **closed (s1)** | **Confirmed caused by the incomplete stub** — but the fix was disabling audio *harder* (the gate byte), not de-stubbing. Reversing the gate directly re-exposes this exact, previously-fatal hang unless the ucode now actually completes tasks and decrements the countdown for real. **This is the single highest-risk regression of this whole plan** — see §4 step 3. |
| 2 | `voice+0x34`/`voice+0x0` DMA corruption ("Thread B", ~30 sessions) | **closed (s147)** | **Confirmed unrelated** — a non-atomic count/pointer race in code that runs unconditionally every VI-retrace regardless of the gate. Already fixed; not expected to be affected by de-stubbing either way. |
| 3 | `waitForAnyAudioSlot` pre-title SIGSEGV (23rd crash class) | **open/parked**, ~12-21% of pre-scene soak deaths | **Plausible, never confirmed** — `tickMusyXIfActive` is gated on the same byte, and s173 saw it apparently nonzero mid-run (an unresolved contradiction with the disable patch that this plan's step 1 should also help clarify). No positive-control evidence either way. |
| 4 | Post-cutscene ~92s stall hypothesis | **abandoned/inconclusive** | **Plausible, never confirmed or refuted** — every soak built to test it died to unrelated earlier crashes first. |

Net: **1 of 4 confirmed-related** (and that one argues for caution, not optimism — de-stubbing
recreates the exact condition that already caused one fatal hang), **2 of 4 plausible-but-unconfirmed**
(the ones the goal-stack's optimism is actually banking on), **1 of 4 confirmed-unrelated**. This
doesn't argue against doing M5 — the user directive already set its priority — but it means the
first de-stubbing step must be defensive about crash family #1 specifically, not just "flip the
switch and see."

**Separate pre-existing landmine, independent of this plan**: `waitForAnyAudioSlot`
(`fixup_game_funcs.py:2054-2119`, instrumented s163 but never fixed) is a tight `while
(!anyAudioSlotActive()) { tickMusyXIfActive(); }` spin with **no timeout**. It's currently benign
because the stub resolves it fast (empty voice state converges instantly). Real audio load with real
timing makes an actual hang here more likely, not less. Recommend landing a bounded-iteration guard
on this loop as a cheap risk-reduction step before step 3 below, independent of whether it ends up
being the mechanism behind crash family #3.

## 4. Incremental de-stubbing sequence — one validation soak per step

Each step below is a single work unit (one iteration). Do not combine steps — the whole point is
isolating which layer, if any, causes a regression. Arm every existing audio diagnostic env var
(§1's list) in every soak from step 1 onward; they're free and already built.

**Step 1 — source-read only, no code change, no soak.** Determine whether the guest ever calls
`osSpTaskStartGo` for a real `M_AUDTASK` while the gate byte reads 0, versus the gate short-circuiting
task creation before it reaches the RSP task queue. Trace `initMusyXEngine`/`tickMusyXIfActive`/
`musyxSynthFrame` forward from the gate-byte read to find where (if anywhere) task submission is
skipped. This determines whether step 2 is provably a no-op (safe structural change) or already
changes behavior (needs its own soak scrutiny). Free — do this first regardless of session budget.

**Step 2 — DONE (s300).** Landed as an env-gated toggle, not an unconditional swap: `main.cpp:594-620`
`case M_AUDTASK` now dispatches `&factor5_ucode_b` when `ROGUESQ_AUDIO_UCODE` is set (any non-`0`
value), else falls through to `&musyx_stub` unchanged — default behavior is untouched until a human
decides to flip the env var on by default. Also landed an always-on `[audtask-dispatch]` counter
(logs `n`/`real_ucode` for the first 20 dispatches then every 256th) as **ground truth** for whether
`M_AUDTASK` is dispatched at all — step 1's `musyx-dma-call`/`voice-trigger-chain` instruments turned
out to measure a different mechanism (PI-DMA sample streaming, gated on real song/voice state) and
fired 0 times in every soak, which would have read as a false null if trusted alone. The counter
settled it directly: **`M_AUDTASK` dispatches continuously from `n=0` at process boot**, independent
of `ROGUESQ_AUDIO_UCODE` and of the gate byte — confirms and strengthens step 1's conclusion with a
2nd, more direct instrument.

3 soaks run (`env ROGUESQ_AUDIO_UCODE=1 HOLD_S=15|60 PROBE_MODE=start_only zsh run_mission_keys.sh
...`, title→3xStart→a→probe→hold(+stick pulses)→grace, per the existing s73 driver):
- **Treatment, 86s wall** (`audiostep2_s300`, predates the counter): title reached 45.1s, full
  key/stick sequence, 60s hold, **0 `[CRASH]`**, `exit=2: 0`, `UnhandledJump: 0`, `missing-func: 0`.
- **Treatment, 33s wall** (`audtasktreat_s300`, counter live): title reached 44.8s, `real_ucode=1`
  confirmed firing from `n=0`, dispatch count into the hundreds within the run, **0 `[CRASH]`**, same
  clean stability line.
- **Control, `ROGUESQ_AUDIO_UCODE` unset** (`audtaskctrl_s300`): `real_ucode=0` confirmed (musyx_stub,
  default path), dispatch counter firing identically from boot — then died mid-hold to a **pre-existing,
  unrelated** crash (`reserveAndEmitDLEntry`/`submitSceneNodeRender`, the known
  `x0=0x0000000300000000` RDRAM-host-base signature already catalogued in `CURRENT-TRUTH.md`'s crash
  catalog, item -15 class #18/#14 lineage) — confirms this project's baseline crash rate is nonzero on
  the unmodified path too; 1 control run is not enough to compare rates, and that wasn't the goal here.

**Verdict**: no hang before title screen, no new `[CRASH]` signature, no `[missing-func]`, in either
treatment soak, across roughly 1,500+ combined `M_AUDTASK`→`factor5_ucode_b` dispatches (extrapolated
from the counter's growth rate) spanning boot through title, menu navigation, and a stick-driven hold
in the level-select war room. `factor5_ucode_b` itself is not observably broken under real dispatch
load. This is 2 clean runs, not the "multiple soaks, rate comparison" bar step 5 sets for the
crash-family question — sufficient for step 2's narrower "does the ucode itself crash/hang" check,
not sufficient to claim anything about crash-family rates yet (that's step 5, after the gate is
reversed).

**Step 3 — land the `waitForAnyAudioSlot` bounded-timeout guard** (§3's landmine), independent of
gate state, as risk reduction before real audio timing is exercised. Validation soak: confirm the
existing ~12-21% pre-scene `waitForAnyAudioSlot` death rate is unaffected (this guard should be a
pure safety net, not change steady-state behavior) — a same-run positive control needs the guard's
fire-counter to stay at 0 in a normal soak, proving it isn't firing spuriously.

**Step 4 — reverse ONE gate-byte site at a time, starting with `initMusyXEngine`** (earliest in
boot, so a regression is caught before menu/gameplay complexity compounds it). Validation soak
specifically watches for crash family #1's exact signature (`waitForMusyXAudioTaskDone` /
`shutdownAudioEngine` hang, boot-time scheduler wedge) recurring — this is a confirmed historical
failure mode being deliberately re-exposed, not a hypothetical. If it recurs: the ucode from step 2
is completing dispatch (`Broke`/return) but not actually decrementing the real countdown the guest
spin-waits on — needs a source-level fix in the ucode's task-completion signaling, not a gate
re-revert. If it doesn't recur after 2 clean soaks: reverse `setDisplayMode`'s site next, same
validation, then `reapplyDisplayMode` last.

**Step 5 — once all 3 gate sites are reversed and boot/menu is stable**, this is the actual test of
the goal-stack's rationale: soak through the pre-title/title/menu phases the usual way and check
whether crash families #3 (`waitForAnyAudioSlot` SIGSEGV) and #4 (post-cutscene stall) change rate
relative to their documented historical baselines (~12-21% and "every soak died earlier" respectively).
Use the existing `ROGUESQ_LOG_AUDIO_DRAIN`/`_VOICE_ACTIVE_GATE`/`_VOICE_TRIGGER_CHAIN` instruments
(already armed from step 1 onward) to get a same-run positive control that real voice/slot activity
is actually occurring, not just that the crash rate moved for an unrelated reason. This step needs
multiple soaks (rate comparison, not a single pass/fail) — budget accordingly, don't treat 1-2 clean
runs as confirmation per the standing 0/2-is-a-weak-null lesson from the `MATEXPIRY_GUARD` thread.

**Step 6 — validate real PCM reaches SDL, not just that the guest stopped hanging.** The host bridge
(`ultramodern::audio_callbacks_t`, `audio.cpp`'s `queue_samples`/`SDL_QueueAudio` wiring in
`main.cpp:622-638`) is already fully implemented and functional — confirmed by the runtime survey,
not assumed. Nothing needs to be built here. The check needed is a sanity counter (e.g.
non-zero-sample-rate or a simple checksum logged from `queue_samples`) proving the buffers
`osAiSetNextBuffer` hands over actually contain non-silent, non-garbage data once the ucode is live
— a format mismatch between `factor5_ucode_b`'s output and what `osAiSetNextBuffer`/`queue_samples`
expect would otherwise pass every crash-rate check above while still producing silence or noise.

## 5. Summary of what this doc changes vs. the existing goal-stack framing

- The stub is one function-pointer swap (`main.cpp:594-595`), not a diffuse set of gates — the
  incremental sequence above can isolate "did the ucode itself break" (step 2) from "did enabling
  the guest-side gate break" (step 4) from "did real audio content break something downstream" (step
  5), rather than one big flip.
- The `dmem[]` sharing question the goal stack posed as open is already answered by the existing s5
  mutex — no new design work needed there, only validation that it holds up under real audio
  traffic (implicitly covered by every soak above).
- The host SDL/`ultramodern` audio-output bridge is already fully built and functional — it does not
  need any work as part of this plan. Only the RSP-side ucode dispatch and the guest-side enable gate
  need touching.
- The expected payoff for M3 crash-family dissolution is weaker than the goal-stack's phrasing
  implied: 1 of 4 documented audio-adjacent crash families is confirmed related to the stub, and that
  one argues for caution (a historical fatal hang gets re-exposed), not for an easy win. 2 of 4 are
  plausible-but-unconfirmed — step 5 is where that gets tested for real, not assumed going in.

## Next work unit

Steps 1-2 are DONE (s300, see §4). Execute **step 3** next: land the `waitForAnyAudioSlot`
bounded-timeout guard (§3's landmine, `fixup_game_funcs.py:2054-2119`) — independent of gate state,
a pure risk-reduction change ahead of step 4's gate-byte reversal. Validation soak needs the guard's
own fire-counter to stay at 0 in a normal soak (same-run positive control that it isn't firing
spuriously) while confirming the existing pre-scene death rate is otherwise unaffected.
`ROGUESQ_AUDIO_UCODE=1` should stay armed in that soak (step 2's toggle, not yet made default) so the
guard gets exercised under the same real-dispatch condition step 2 validated, not the degenerate stub
path.
