# NEXT work unit (s1194)

HYPOTHESIS-ID: m4-vmadh-accumulator-origin

Work unit: perform one bounded static audit of the producer chain feeding the
Factor 5 `vmadh v6,v4,v0` shade calculation. Do not build or run.

Read `docs/F5-UCODE-REFERENCE.md` first, then enumerate the generated VMADH
sites and the preceding writes/loads to the relevant vector lanes. Compare
the port-side VMADH model and the paired combiner evidence already summarized
in `CURRENT-TRUTH.md`.

Competing hypotheses and discriminator:

- H1: a producer fails to initialize or preserve the accumulator/vector lane.
  Discriminator: a complete static chain reaches `vmadh` with an uninitialized
  or overwritten operand.
- H2: the source lanes are correct but VMADH lane/order modeling is wrong.
  Discriminator: the generated/reference command and the independent control
  disagree with the port-side lane mapping.
- H3: the fixed sentinel is a legitimate Factor 5 lighting/clipping state.
  Discriminator: all producers and lane mapping are accounted for, with no
  uninitialized write and no model disagreement.

Exact commands:

rg -n -C 12 -e 'vmadh|VMADH|v4|v6' /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp /Users/williambuckley/Documents/Tools/N64Recomp --glob '*.{c,h,cpp,hpp,md,txt}'
rg -n -C 8 -e 'shade|VTXCOLOR|0xFFFF8000|0x00008000' /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp --glob '*.{c,cpp,h,md,txt}'
git diff --check

If H1 is selected, identify the exact producer before proposing any
mitigation. If H2 is selected, the next unit is a static model correction. If
H3 is selected, design the smallest ground-truth-backed probe only after
reading the oracle instructions and defining a positive control.
