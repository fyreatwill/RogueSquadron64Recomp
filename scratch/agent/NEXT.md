Single next work unit: perform one new M4 accumulator-boundary experiment. Start
from the independent retail oracle, then design one batched comparison that can
distinguish a writer/origin divergence from an unjoinable capture schema. Do not
repeat the exact phase/image/PC/progress join or the ranked comparison whose
lane masks were empty. The experiment must include positive controls in both
arms and all candidate comparison arms in the same build/run where applicable.

Competing hypotheses and discriminator:

1. H1: a new portable boundary key joins equivalent retail and port events and
   exposes a real accumulator writer/origin divergence.
2. H2: the new key joins, but the accumulator lanes remain absent/equal; the
   current writer hypothesis remains unproven.
3. H3: the new key still cannot join the arms despite positive controls; the
   capture boundary, not a writer, is the blocking fact and needs a different
   source or schema.

The discriminator is the batched cross-arm join outcome plus lane activity,
validated by whole-RDRAM, VI, mapped-PC, and image positive controls in both
arms. Before building instrumentation, inspect the existing retail parser and
`docs/F5-UCODE-REFERENCE.md`; write the proposed key and all competing outcomes
here before implementation.

Expected commands:

    sed -n '1,240p' docs/F5-UCODE-REFERENCE.md
    rg -n 'M4|accumulator|normalized|rank|lane|writer' tools docs | head -120
    rg -n 'retail|port|whole.RDRAM|mapped.*PC|image' tools/analyze_m4_*.py | head -160

HYPOTHESIS-ID: m4-accumulator-boundary-revisit
