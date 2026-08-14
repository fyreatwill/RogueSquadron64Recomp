# NEXT work unit (s1014)

HYPOTHESIS-ID: m4-zero-shade-accumulator-origin

Instrument one build/run at the final Factor 5 `vmadh v6,v4,v0` call site.
Record all eight lanes of `v4`, `v0`, and `ACCH:ACCM:ACCL` immediately before
and after the operation, the resulting `v6`, and the subsequent VGE selection.
Scope records to VI-1024 and include one independent positive-control RSP
arithmetic record in the same run. Do not edit generated output; use
regeneration-owned fixup/runtime instrumentation.

Competing hypotheses and discriminating measurement:

- `H-accumulator-saturation`: pre/post `ACCH:ACCM` crosses the signed range and
  VMADH returns `0x8000` through saturation.
- `H-v4-v0-arithmetic`: the post-VMADH accumulator is sign-extending and its
  middle word is already `0x8000` without saturation.
- `H-v29-selection`: the captured VGE chooses a `v29` lane equal to `0x8000`.

Discriminator: the complete tuple makes the alternatives mutually exclusive;
the positive control must visibly fire before a null result is meaningful.
