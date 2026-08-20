# NEXT work unit (s2030)

HYPOTHESIS-ID: m5-optin-rsp-arm-contract

## Work unit

Execute step 2 of `docs/M5-AUDIO-PLAN.md`: validate the existing
`ROGUESQ_AUDIO_UCODE=1` arm against the unset/default `musyx_stub` arm.
Use one build for both arms and phase-gate the comparison on VI 1024 and
hangar VI 512. Do not enable stock `aspMain`, change the default dispatch,
reverse a guest gate, or promote the opt-in image.

## Ground truth before building

Run the retail oracle first with its whole-RDRAM positive control and a narrow
watch on the MusyX gate byte:

~~~sh
tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ../rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 35 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F51 --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start --vi-trace > scratch/agent/s2030-groundtruth.log 2>&1
~~~

The ground truth is usable only if the whole-RDRAM watch reaches its cap and
the retail run reaches VI 1024 or VI 512. Record gate-writer PCs and whether
the target watch sees `0 -> 1`/`1 -> 0`; a watch count without those
controls is not evidence.

## Competing hypotheses and discriminator

- **A — degenerate host path:** the default `musyx_stub` is the immediate
  blocker. The opt-in arm reaches a real task exit, preserves the DMEM canary,
  produces a valid slot/status transition, and emits nonzero PCM; the default
  arm does not. This selects the opt-in RSP step.
- **B — image/task ABI mismatch:** the opt-in arm dispatches but does not
  complete the task contract, or produces only zero/invalid PCM and no valid
  slot transition. The default and treatment then share the relevant failure.
  This keeps the arm opt-in and moves the next step to task/image attribution.
- **C — guest gate/scheduler boundary:** both arms show the same task/slot
  outcome while the guest gate or wait path remains degenerate. A task exit
  without PCM or a gate transition without task completion selects this
  boundary, not a host audio-device change.
- **D — incomplete control:** either arm lacks the same-run non-audio RSP task
  completion/DMEM-canary control or fails to reach the phase anchors. The run
  is unevaluable and must be repaired before interpreting A-C.

The single discriminator is the phase-keyed row containing dispatch arm,
`RspExitReason`, task count/exit, DMEM canary, gate/slot before-after values,
and PCM nonzero/byte counts. A positive non-audio RSP completion control must
fire in the same run. Compare arms by VI phase, not elapsed time.

## Build and capture

After the oracle succeeds, verify the existing dispatch strings and build one
binary:

~~~sh
strings build/RogueSquadron64Recomp | rg 'audtask-dispatch|PCM|pcm-sanity|DmemGuard'
cmake --build build --target RogueSquadron64Recomp -j2
~~~

Run the two phase-gated arms from the same build. Keep the default arm unset;
the treatment alone sets the opt-in image. Arm all passive breadcrumbs in both
recipes:

~~~sh
env ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 'PROBE_KEYS=6:start 11:start 16:start 21:start 26:start 31:start' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s2030-audio-stub 120 2 > scratch/agent/s2030-audio-stub.stdout 2>&1
env ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 'PROBE_KEYS=6:start 11:start 16:start 21:start 26:start 31:start' PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/s2030-audio-optin 120 2 > scratch/agent/s2030-audio-optin.stdout 2>&1
~~~

Inspect only bounded counts and phase/width rows from each `run.log`.
Require the same s2006/service positive controls in both arms before reading
audio nulls. If a wrapper does not terminate, SIGKILL the game process/group;
do not use SIGTERM.

## Expected handoff

If A is selected, the next unit is the first reversible gate/slot contract
step in `M5-AUDIO-PLAN.md`, still opt-in. If B is selected, keep the stub and
trace the task image/ABI before any gate change. If C is selected, census the
guest gate and wait writer/consumer with an independent retail attribution.
If D occurs, repair only the missing control or phase anchor and do not call a
null an audio result.
