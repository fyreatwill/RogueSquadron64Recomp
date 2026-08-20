# NEXT work unit (s2031)

HYPOTHESIS-ID: m5-guest-gate-consumer-contract

## Work unit

Run one bounded, observational M5 gate/consumer census with the validated
opt-in route held constant. Instrument all five writers of guest byte
`0x800A0F50`, the gate-1 consumer, and the audio-task wait consumer in one
build. Join every phase-valid row to `audtask-abi`/`audtask-dma-row`, the
reserved-gap canary, PCM, and slot/status fields. Do not change any store,
default dispatch, wait behavior, or `aspMain`; keep `ROGUESQ_AUDIO_UCODE=1`
opt-in.

## Ground truth before building

Run the retail oracle first with the whole-RDRAM positive control and both
the gate byte and audio-wait word watches:

~~~sh
tools/oracle/build/rs64_oracle --core ../rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom ../rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --hit-cap 10000 --watch-write 0x0:0x800000 --watch-write 0xA0F50:0xA0F51 --watch-write 0x14998A:0x14998B --detail-watch 1 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --vi-trace > scratch/agent/s2031-groundtruth.log 2>&1
~~~

Accept the oracle only if the whole-RDRAM watch reaches its cap and retail
reaches VI 1024 or VI 512. Record the gate writer PCs, target value
transitions, and whether `0x14998A` is written; a watch count without those
controls is not evidence.

## Competing hypotheses and discriminator

- **A — legitimate disabled gate:** the port's zero at `0x800A0F50` is the
  intended writer outcome for this route. All five writer rows and the gate-1
  consumer agree on zero/skip, while retail has the corresponding named writer
  cluster and the opt-in task still returns normally. This selects gate
  semantics, without changing a store.
- **B — port writer/value divergence:** the same guest writer site or its
  caller runs with a different value/order than retail. A phase-valid writer
  row with a value/order not present in the independent retail attribution,
  or a consumer read that disagrees with the immediately preceding writer,
  selects this boundary.
- **C — wait/task boundary:** the gate is legitimately zero, but the audio
  wait consumer or countdown writer is the first missing edge. A gate-consumer
  match with no corresponding wait decrement/return, while the task/DMEM rows
  remain valid, selects this boundary and leaves the image ABI open.
- **D — incomplete control:** the census lacks the same-run s2006 service
  control, a phase-valid opt-in audio row, or the retail whole-RDRAM/VI
  controls. Do not interpret any null; repair the control only.

The single discriminator is one phase-keyed table row containing writer guest
PC/value and sequence, gate-consumer read/branch, wait word before/after and
writer PC, task arm/exit/DMEM canary, slot/status, and PCM counts. A complete
row selecting A, B, or C is the result; a field added without a branch in this
table is not a work unit. Use one opt-in run and compare its port writer PCs
to the independent retail oracle; do not use a cross-run animation comparison.

## Build and capture

First verify the current gate anchors and then make one build carrying every
writer/consumer field:

~~~sh
rg -n '800A0F50|0xA0F50|8014998A|waitForMusyXAudioTaskDone|tickMusyXIfActive' src ../N64Recomp/RecompiledFuncs ../N64Recomp/fixup_game_funcs.py
cmake --build build --target RogueSquadron64Recomp -j2
~~~

Run the exact phase-valid route used by s2030, with all passive M5 controls
and the new gate/wait census enabled:

~~~sh
env ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=180 PROBE_LEAVE_OK=1 'PROBE_KEYS=6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' zsh tools/probe.sh scratch/agent/s2031-gate-census 120 2 > scratch/agent/s2031-gate-census.stdout 2>&1
~~~

Require 24/24 s2006 service entry/exit controls, VI 1024 and hangar VI 512,
and at least one phase-valid `audtask-abi`/`audtask-dma-row` before reading
gate or wait nulls. If the wrapper does not terminate, SIGKILL the game
process/group; do not use SIGTERM.

## Expected handoff

If A is selected, the next unit is a single reversible writer/store arm,
still opt-in and with the other four stores unchanged. If B is selected,
trace the divergent writer caller/order before changing a value. If C is
selected, join the wait decrementer and consumer to the task/slot path before
touching the gate. If D occurs, repair only the missing control or phase
anchor and do not call a null an audio result.
