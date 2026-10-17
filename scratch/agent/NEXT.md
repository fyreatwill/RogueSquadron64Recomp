# Next: obtain a new phase-driving or shared-boundary capability

Session 5329 reran the already instrumented port after a fresh retail oracle
positive control. The title-observed Start/A schedule still left the port at
width 640/origin `0x00696100`; it never reached the required 512-wide hangar
boundary. Do not repeat this schedule or compare cxd4 rows without a shared
boundary. Human input is needed to supply or approve a new independently
validated phase-driving/observation method.

The failed port recipe, retained for provenance only:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
cd /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix && make all
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
env PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='2:start 8:a 14:start 20:a' \
  zsh tools/probe.sh scratch/agent/m4-port-next 240 1
```

If a new method is supplied, rebuild both arms, retain whole-RDRAM and VI
positive controls, and require both arms to reach `0x006AB400` at width 512
before joining records. Do not add a mitigation or infer from synthetic stage
ordinals.

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
