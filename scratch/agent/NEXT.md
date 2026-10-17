# Next: rerun M4 shared-boundary sampler through hangar

Work unit: one phase-gated comparison using the now-landed sampler. Run the
port with the proven title-to-hangar recipe from `s5099`/`s4959` (wait for
`0x00790400`, then send Start/A keys until `0x006AB400` appears), and run the
retail cxd4 arm with the same title-to-hangar key schedule. Use stride 1 only
in the retail dump. Do not add a mitigation.

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
