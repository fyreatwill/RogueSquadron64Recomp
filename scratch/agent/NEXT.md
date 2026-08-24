# NEXT work unit (s2286) — M5 Step 1 trace-light route discriminator

HYPOTHESIS-ID: m5-step1-route-requalification

## Work unit

Run one same-build, phase-gated silent/image pair using the corrected
eleven-Start route: `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`,
`ROGUESQ_LLE_SOLO=1`, `ROGUESQ_SPIN_YIELD=1`, and
`ROGUESQ_M5_C88_VALUE=0`. Keep the independent retail oracle and launch the
image arm only after the silent arm reaches `512 @ 0x006AB400`.

Use the existing task/DMEM/DMA, audio-return/SP, gate, bounded
slot-dispatch/link, voice/MORT, PCM, B40, route-state, and phase diagnostics,
but remove `ROGUESQ_LOG_VI_CALLERS=1` from the s2285 recipe. That is the route
discriminator: s2285 reached title but crashed in the off-target 640 return
with the high-volume VI-caller arm enabled. Do not change runtime code,
defaults, guards, or audio dispatch.

## Competing hypotheses and discriminating measurement

- H-LoggerPerturbation: removing the high-volume VI-caller trace restores the
  qualified route. The silent arm reaches hangar and the gated image arm also
  reaches hangar, allowing the complete Step 1 row to be compared.
- H-RouteIntrinsic: the trace-light arm still reaches title, returns to
  `640 @ 0x00696100`, and crashes at `slotDispatcherIter+3508` / guest PC
  `0x80007904` before hangar. This selects route failure at this scope and
  leaves all downstream audio nulls unevaluable.
- H-AudioContract: both arms reach the target phase and the image arm adds a
  task/output/service/slot/voice/MORT/PCM edge while the silent arm remains
  the control. This selects the missing audio contract boundary without
  promoting the image arm.
- H-RouteInvalid: the oracle positive control, port route controls, or either
  target phase is absent. Do not interpret any downstream null from that arm.

The discriminating measurement is one phase-keyed table per arm containing
task dispatch/fields/source, DMEM change and DMA ranges, image exit and SP
completion, service entry/return, gate, slot/status/reap, bounded slot/link
rows, voice/MORT rows, PCM source/consumer joins, and title/hangar route. A
result is interpretable only if the oracle passes the whole-RDRAM threshold at
10,000 writes and reaches both title and hangar, both port arms pass B40 and
route-state controls, and both reach `512 @ 0x006AB400`. Branch counters are
not positive controls.

## Exact commands

1. Create `scratch/agent/run_s2286_m5_step1_trace_light_pair.sh` with
   `apply_patch`, based on the corrected s2285 driver. Keep its oracle gate,
   silent-first hangar gate, SIGKILL watchdogs, and bounded summary. In the
   common port environment retain:
   `ROGUESQ_LOG_M5_TASK_CONTRACT=1`, `ROGUESQ_LOG_AUDIO_RETURN=1`,
   `ROGUESQ_LOG_PCM_BOUNDARY=1`, `ROGUESQ_LOG_M5_GATE_CONTRACT=1`,
   `ROGUESQ_LOG_SLOT_DISPATCH=1`, `ROGUESQ_LOG_SLOT_LINK=1`,
   `ROGUESQ_LOG_FILTER_VOICE_AUDIT=1`, `ROGUESQ_LOG_M5_B40_ROUTE=1`,
   `ROGUESQ_LOG_M5_ROUTE_STATE=1`, `ROGUESQ_LOG_PHASE=1`,
   `PROBE_PHASE_WIDTH=1024`, and `PROBE_KEYS_FROM_PHASE=1`; do not set
   `ROGUESQ_LOG_VI_CALLERS`.
2. Check syntax:
   `zsh -n scratch/agent/run_s2286_m5_step1_trace_light_pair.sh`
3. Run from the repository root:
   `zsh scratch/agent/run_s2286_m5_step1_trace_light_pair.sh s2286_m5_step1_trace_light_pair`
4. Summarize with bounded `grep`/`tail` only: oracle whole-RDRAM/title/hangar
   controls, both port route controls, silent/image title/hangar gates, the
   per-phase task/DMA/SP/service/slot/voice/MORT/PCM rows, and terminal crash
   or timeout. If the silent hangar gate is absent, do not launch or interpret
   the image arm.
