# Next: run the M4 task-keyed accumulator comparison at the shared boundary

Session 5330 refuted the phase-driving block. The in-process autopilot route
reached the required `vi_width=512`, origin `0x006AB400` boundary, so the
sampler can resume. Do not use the old window-injected schedule.

Build the cxd4 sampler and port together, retain the oracle whole-RDRAM/VI
controls, and use this proven port route:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
cd /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix && make all
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
env ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M4_Y8000=1 ROGUESQ_M4_Y8000_WIDTH=512 \
  ROGUESQ_AUDIO_UCODE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 \
  ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
  ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
  ROGUESQ_AUTOPILOT_STOP_WIDTH=512 \
  PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=110 PROBE_KEYS_FROM_PHASE=1 \
  PROBE_LEAVE_OK=1 zsh tools/probe.sh scratch/agent/m4-port-next 240 1
```

Require both arms to reach the shared `0x006AB400`/512 boundary before
joining. Do not add a mitigation or infer from synthetic stage ordinals.

Competing hypotheses and discriminator:

- H1: exact task/PC/step keys agree in first/last writer and VACC value; the
  synthetic stage difference was a boundary artifact.
- H2: exact keys align but repeatably disagree in writer or VACC value; the
  port accumulator path diverges.
- H3: a positive control fails or the port cannot expose actual guest PCs;
  leave M4 unevaluable and do not infer from stage ordinals.

Discriminating table: `(VI origin,width,task serial,RSP PC,step bucket)` with
first writer, last writer, first/last `0x8000` lane, and task-end VACC. Select
only one of H1/H2/H3 from that table.

Exact ground-truth control and source commands:

```sh
tools/oracle/build/rs64_oracle --core \
  /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 8 --watch-write 0x0:0x800000 --hit-cap 3 --vi-trace
cd /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix && make all
```

Expected outcomes for the next attempt: a new method must make the port reach
the 512 hangar origin and expose an independent positive control. If either
condition fails, select H3 and stop; do not compare stopwatch timestamps or
accept a stage-only join.

HYPOTHESIS-ID: m4-accumulator-boundary
