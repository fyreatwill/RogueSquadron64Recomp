# NEXT work unit (s2026)

HYPOTHESIS-ID: m5-drain-shutdown-status-boundary

## Resume: s2025 selected the forced-LLE route gate

The same `tools/probe.sh` wrapper, binary, eleven-Start schedule, and passive
environment were used in both arms. The forced-LLE arm reached VI 1024 at
14.5s and VI 512 at 26.6s; the HLE arm stayed at VI 640 for the 120s phase
wait. The phase-valid LLE arm emitted 409 matched s2020/s2022 service rows,
all with slot-0 status `0x00`, and the real s2008 writer row
`pc=0x8009B2C4 old=0x01 new=0x00 shutdown_call=3`. It emitted no status-3
service interval or worker-side store before the known PI `do_rom_read` crash
at guest PC `0x80001B08`. The HLE arm had only the non-control
`0x8009BBF0` helper row and no crash.

## Work unit

Use the already-built binary and the same forced-LLE `tools/probe.sh` wrapper
in two concurrent arms. Keep the eleven boot Starts and every existing
audio/status breadcrumb identical; toggle only `ROGUESQ_DRAIN_INLOOP_TICK`.
Arm A leaves it at its current default-on setting. Arm B sets it to `0`.
Do not rebuild, add instrumentation, change the default, or enable the opt-in
audio image. Phase-gate at VI 1024, leave capture enabled for the VI 512
hangar transition, use the 120-second wrapper budget, and let each wrapper
SIGKILL its own game process.

## Competing hypotheses and discriminator

- H1 drain-tick boundary: tick-on fails to return from the ROM drain or reach
  shutdown call 3, while tick-off reaches call 3 and exposes status 3 followed
  by a `serviceVoicePoolFrame` entry and the `0x8009B7EC` store.
- H2 timing-only: both arms reach the same drain/shutdown and status result;
  the in-loop tick changes timing but is not the missing worker boundary.
- H3 worker-dispatch boundary: both arms reach call 3 and a live status-3
  interval, but neither emits a worker entry or status-zero store.
- H4 named-writer boundary: tick-off reaches call 3 but service still sees
  only `0x00` (or only the named `0x8009B2C4` `0x01 -> 0x00` transition), so
  the missing status-3 writer/source remains the selected boundary.

The single discriminating table is one row per arm containing: first VI 1024
and VI 512 times; `[drain-inloop-gate]` and drain-return markers; shutdown
call-3 entry/exit; the complete s2008 writer rows; s2020 service entry/exit;
s2022 loop status values and `zero_skip`; and the independent worker/store
edge. A phase-valid arm must also emit the s2006 entry/exit positive control.
No arm without that control can select a status result. The possible outcomes
above select H1, H2, H3, or H4 respectively; a PI crash after the table is
complete is recorded as a terminal signature, not used to erase the table.

## Commands

Define this zsh array once, then launch both commands concurrently:

~~~
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
~~~

Run concurrently:

~~~
env "${probe_env[@]}" zsh tools/probe.sh scratch/s73_post_a_scene/s2026-tick-on 120 2
env "${probe_env[@]}" ROGUESQ_DRAIN_INLOOP_TICK=0 zsh tools/probe.sh scratch/s73_post_a_scene/s2026-tick-off 120 2
~~~

The retail status sequence and writer PCs are already independently grounded
by the s2012/s2013 debugger-off and s2014/s2022 debugger-on oracle runs; this
unit adds no new instrument. If either arm lacks the phase and s2006 controls,
classify that arm as an anchor failure and do not infer H2-H4 from its null.
