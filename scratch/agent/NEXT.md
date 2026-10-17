# Next: implement M4 shared-boundary sampler

Work unit: one instrument/build/run comparison based on
`docs/REVISIT-S5325-M4-SHARED-BOUNDARY-DESIGN.md`. First add an env-gated
stride to the existing cxd4 `RSM1` mid-task sampler, then extend the
regeneration-surviving port M4 probe with actual generated Factor 5 guest PCs.
Build both arms and run the same phase-gated hangar schedule in this iteration.
Do not add a mitigation.

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

Expected outcomes: whole-RDRAM callbacks and VI rows must be nonzero; then
the exact-key table selects H1, H2, or H3 as above. Do not compare stopwatch
timestamps. Do not accept a stage-only join.

HYPOTHESIS-ID: m4-accumulator-boundary
