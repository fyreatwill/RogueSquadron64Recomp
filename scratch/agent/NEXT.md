# Next: expose port-side M4 task/PC keys at the shared boundary

Session 5331 reached `vi_width=512`, origin `0x006AB400`, but the port output
contained only aggregate `[m4-y8000]` counters. The next single work unit is a
regeneration-surviving diagnostic change that emits the actual port guest RSP
PC, monotonic graphics-task serial, and instruction-step bucket alongside the
existing M4 entry/flush records. Do not infer PC from stage ordinal.

Competing hypotheses and discriminator:

- H1: the existing M4 hooks already have a live task/PC/step context, but the
  logger drops it; one bounded field-path change will produce nonzero exact-key
  rows at `0x006AB400`/512.
- H2: task serial is available but actual guest RSP PC or instruction step is
  not live at these hooks; output will contain a positive task key but a
  zero/constant/unrelated PC or step.
- H3: none of the required keys is available at the hook; the same-run control
  will prove the hook fires, but the join remains impossible and the M4 thread
  must be parked again.

Discriminating measurement: in one rebuilt port run, require a positive-control
`[m4-y8000]` hook mark plus target rows containing nonzero, changing
`task_serial`, actual generated guest `rsp_pc`, and monotonic `step` at the
512-wide `0x006AB400` phase. A hook count alone is not a positive control for
the fields. Do not run the retail comparison until all three fields are live.

Before building, consult the existing ground-truth design and source fields:

```sh
sed -n '1,90p' docs/REVISIT-S5325-M4-SHARED-BOUNDARY-DESIGN.md
rg -n 'rs64_m4_y8000|task_serial|g_rs64_last_guest_pc|rs64_step|guest_pc' src build/factor5_ucode RecompiledFuncs
```

Implement the field path in the regeneration-surviving source/build route,
then run:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
env ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M4_Y8000=1 ROGUESQ_M4_Y8000_WIDTH=512 \
  ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 \
  PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/m4-port-next 240 1
```

Require the same-run hook positive control and all three fields before moving
back to the two-arm comparison. Do not add a mitigation or infer from stage
ordinals.

The later comparison's ground-truth control remains:

```sh
tools/oracle/build/rs64_oracle --core \
  /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 8 --watch-write 0x0:0x800000 --hit-cap 3 --vi-trace
```

HYPOTHESIS-ID: m4-accumulator-boundary
