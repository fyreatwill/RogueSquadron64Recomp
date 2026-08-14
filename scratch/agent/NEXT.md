# NEXT work unit (s1134)

HYPOTHESIS-ID: m4-ground-truth-accumulator-origin

Perform one bounded M4 ground-truth preparation step: read the oracle and
Factor 5 reference instructions needed to define an independent accumulator
origin measurement, then identify the smallest complete pre/post discriminator
that can be armed in one future build/run. Do not build or run this iteration.
Do not add instrumentation yet.

Competing hypotheses and discriminator:

- H-game-writes: the retail oracle can attribute a legitimate writer/value
  transition for the accumulator before the zero-shade read.
- H-runtime-only: the oracle sees no matching retail writer, so the port/runtime
  or recompiled execution remains the only source under test.
- H-unreachable: the oracle controls do not reach the corresponding shaded
  emitter phase, making this discriminator unavailable rather than negative.

Discriminator: an oracle whole-RDRAM positive control plus a targeted physical
watch covering the candidate accumulator address range, with PC attribution
and phase reachability. A retail writer/value transition selects H-game-writes;
zero targeted hits after a healthy whole-RDRAM control selects H-runtime-only
only if the shaded phase is reached; no phase reach selects H-unreachable.

Required reading/commands:

```sh
sed -n '1,240p' tools/oracle/README.md
sed -n '1,260p' docs/F5-UCODE-REFERENCE.md
rg -n -i 'accumulator|shade|VGE|vmadh|zero-shade|M4' tools/oracle docs ../N64Recomp/RecompiledFuncs/funcs_*.c | head -240
```
