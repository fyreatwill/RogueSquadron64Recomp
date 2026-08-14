# NEXT work unit (s1135)

HYPOTHESIS-ID: m4-ground-truth-accumulator-origin

Implement the first arm of the paired M4 measurement in one build: add a
phase-gated, bounded probe at the exact final `VMADH v6,v4,v0` in the Factor 5
recompiled ucode, capturing `r9`, all four lanes of `v4`, `v0`, `ACCH:ACCM:ACCL`,
and `v6` immediately before/after VMADH and after the following VGE. Include
the existing independent RSP accumulator positive control in the same run.
Do not run the retail oracle until this port capture supplies the stable
physical record range for its targeted watch.

Competing hypotheses and discriminating outcomes:

- H-arithmetic: post-VMADH differs from the local model computed from the
  captured operands and accumulator; the accumulator/product implementation
  is implicated.
- H-vge-store: post-VMADH matches the model, but post-VGE or the stored record
  differs; VGE/store semantics remain implicated.
- H-source-state: the complete port tuple and store agree, so the next arm
  must compare the same record range against retail PC-attributed writers.

Discriminator: the exact pre/post tuple plus a visibly firing independent RSP
positive-control row in one phase-gated run. A counter at `L_16B8` is not a
control. The oracle follow-up must use `--watch-write 0x0:0x800000` and a
targeted watch derived from this run, with `--vi-trace`; a targeted null is
valid only if the shaded phase is reached.

Expected command after the probe is implemented:

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
```
