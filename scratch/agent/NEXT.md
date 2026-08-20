# NEXT work unit (s2025)

HYPOTHESIS-ID: m5-phase-route-lle-vs-wrapper

## Resume: s2024 inverse route split

s2024's corrected same-window run used the eleven-Start boot schedule. The
forced-LLE run_mission_keys.sh arm reached VI 1024 at 48.9s; the direct
no-LLE tools/probe.sh arm delivered all eleven key sends but stayed at VI 640
through 120s. The arms used different wrappers, so this selects neither LLE
nor the wrapper as the cause. Both had live s2020/s2022 body controls and no
s2008 writer positive-control row.

## Work unit

Isolate the LLE toggle from the runner/input wrapper. Use the same already-
built binary, the same tools/probe.sh wrapper, the same eleven-Start boot
schedule, and one shared passive/body/writer environment in two concurrent
arms. Arm A adds ROGUESQ_LLE_FORCE=1, ROGUESQ_LLE_UNGATED=1, and
ROGUESQ_LLE_SOLO=1; arm B has none of those variables. Include
ROGUESQ_STUB_MISSING_FUNCS=1 in the shared environment so the only intended
toggle is LLE. Phase-gate both at VI 1024, stop each on phase, process loss,
or 120 seconds, and kill the exact game PID with SIGKILL. Do not rebuild,
add instrumentation, or change default audio behavior.

## Competing hypotheses and discriminator

- H1 lle-required: only the LLE arm reaches VI 1024; the no-LLE arm stays at
  VI 640 or dies. The LLE path is the selected phase gate.
- H2 wrapper-confound: both same-wrapper arms have the same pre-1024 terminal
  outcome. The s2024 split came from run_mission_keys.sh versus tools/probe.sh
  or their input timing, not LLE.
- H3 hle-sufficient: both same-wrapper arms reach VI 1024. LLE is not required
  and the s2024 split was runner-specific.
- H4 hle-only: only the no-LLE arm reaches VI 1024. The direct HLE path is the
  working route and the forced-LLE arm is the failing branch.

The discriminating measurement is one table with each arm's first phase
vi_width=1024, last pre-1024 width and terminal signature, plus counts for
[s2020-svc], [s2022-svc], [s2008-status-control], and [s2008-status-writer].
Only a phase-valid arm with a live s2008 positive control can reopen the
status-writer/read join; a lone n=0 helper row is not that control.

## Ground-truth control

No new diagnostic is being built. The s2024 retail whole-RDRAM control is
already valid in this iteration (10,000 callbacks). If the run is repeated
in a later iteration, arm the same control before any instrument change:

~~~
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 8 --watch-write 0x0:0x800000 --hit-cap 1 > scratch/agent/oracle_s2025_whole_control.log 2>&1
~~~

## Arms

Use this shared environment and schedule:

~~~
BASE='ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 ROGUESQ_LOG_DMA=1 ROGUESQ_LOG_DMA_CALLER=1 ROGUESQ_LOG_PCM_SANITY=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_WAITFORSLOT_GUARD=1 ROGUESQ_LOG_S2008_STATUS_WRITERS=1 PROBE_KEYS="6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start" PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=120 PROBE_LEAVE_OK=1'
~~~

Arm A adds the three LLE variables and runs:

~~~
env $BASE ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 zsh tools/probe.sh scratch/s73_post_a_scene/s2025-lle 120 2
~~~

Arm B runs the same command without the three LLE variables:

~~~
env $BASE zsh tools/probe.sh scratch/s73_post_a_scene/s2025-hle 120 2
~~~

Launch both concurrently, poll their run logs for VI 1024, and record the
first transition before killing each process. Do not interpret a missing
s2008 row without its positive control as a status-value result.
