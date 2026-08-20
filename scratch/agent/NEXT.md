# NEXT work unit (s2028)

HYPOTHESIS-ID: m5-service-worker-dispatch-boundary

## Work unit

Implement one regeneration-stable A11 census for the worker/status-zero join,
then run one forced-LLE `tools/probe.sh` hangar capture with the existing
eleven-Start schedule and passive M5 breadcrumbs. Batch all of these in the
same build and same run: shutdown call 3 entry/read/return for slot 0, every
existing s2008 status writer with old/new values, worker dispatch and
`serviceVoicePoolFrame` entry/exit, the status-3 read, and the
`0x8009B7EC` store edge. Keep the drain toggle at its default unset/on state;
do not add a new mitigation, flip default audio, or enable the opt-in audio
image. The static retail writer contract is already established by s2014 and
s2022; no new instrument should be built without that ground-truth control.

## Competing hypotheses and discriminator

- H1 scheduler dispatch: shutdown call 3 observes status `0x03` and it
  persists, but no worker entry or store occurs.
- H2 service path: worker entry follows the status-3 interval and emits the
  named zeroing store before shutdown returns.
- H3 writer/reaper ordering: call 3 never observes status `0x03`; the census
  attributes an earlier writer or reaper transition that leaves the service
  reading zero.
- H4 incomplete control: the phase or s2006 positive control is absent, so
  the run cannot discriminate worker behavior and must not be interpreted.

The single discriminating table is one phase-gated row containing: VI 1024/512,
s2006 entry/exit, shutdown call 3, each status writer old/new value, status-3
read duration, worker dispatch/entry/exit, service status read, and the
`0x8009B7EC` store. H1, H2, or H3 is selected only when the row is phase-valid;
H4 is selected otherwise. A terminal crash after the complete row does not
erase the table.

## Commands

~~~sh
cmake --build build --config Debug --target RogueSquadron64Recomp
strings build/RogueSquadron64Recomp | rg 'serviceVoicePoolFrame|s2028|status-3|0x8009B7EC'
probe_env=(
  ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1
  ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1
  ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1
  ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1
  ROGUESQ_LOG_S2008_STATUS_WRITERS=1
  'PROBE_KEYS=6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start'
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1
  ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
)
env "${probe_env[@]}" zsh tools/probe.sh scratch/s73_post_a_scene/s2028-worker-boundary 120 2 > scratch/agent/s2028-worker-boundary.stdout 2>&1
~~~

Consume only bounded counts and selected rows from `run.log`; do not cat the
log.
