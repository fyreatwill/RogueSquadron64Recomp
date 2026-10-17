# Next: RESUME M4 shared-boundary sampler through hangar

RESUME: Session 5326 completed the sampler build and positive controls but did
not reach hangar. Do not repeat the title-only schedule. The next actual work
unit is to rebuild the already instrumented port and cxd4, then launch both
arms after observing the title VI, using the same title-observed key schedule.
No new instrumentation or mitigation is needed before that run.

Port command:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
cd /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix && make all
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
env PROBE_PHASE_WIDTH=512 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
  PROBE_KEYS='2:start 8:a 14:start 20:a' \
  zsh tools/probe.sh scratch/agent/m4-port-next 240 1
```

For the cxd4 capture, use the same title-observed Start/A schedule with
`RS64_RSP_MID_STRIDE=1`; retain whole-RDRAM and VI positive controls. The
comparison is valid only if both arms reach `0x006AB400` at width 512. Do not
add a mitigation or infer from synthetic stage ordinals. The exact existing
artifacts are `scratch/agent/s5326_m4_shared_port/port.log`,
`scratch/agent/s5326_m4_shared_retail/rsm1.bin`, and
`docs/REVISIT-S5326-M4-SHARED-BOUNDARY-RESULT.md`.

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

Expected outcomes: each arm must log its positive control and reach the 512
hangar origin. Then the exact-key table selects H1, H2, or H3 as above. The
5326 result was H3 because both arms stayed at 640/title; do not compare
stopwatch timestamps or accept a stage-only join.

HYPOTHESIS-ID: m4-accumulator-boundary
