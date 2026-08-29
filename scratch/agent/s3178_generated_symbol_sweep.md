# Session 3178 generated-symbol sweep

## Work unit

Bounded regeneration-safe sweep of generated records in
`0x80150000..0x80160000`.

## Hypotheses and discriminator

- `H-SemanticMatch`: an exact companion-qualified callable name remains.
- `H-DataGap`: a selected placeholder is a non-callable data fragment.
- `H-Ambiguous`: the record is synchronized, fake, colliding, or otherwise
  insufficiently identified and must remain unchanged.

The discriminator was the complete helper selection plus an independent
generated-definition search for the same interval.

## Result

The helper selected five records: `0x801529C0 D_801529C0` and
`0x80153420 D_80153420` as `ambiguous-or-fake`, plus
`0x80154670 numSpeechSamples`, `0x8015467C speechSampleOffsets`, and
`0x80154684 speechFile` as `already-synchronized`. It changed `0` references
in `0` files and returned its expected no-rename error under
`--require-rename`. The independent `RECOMP_FUNC` definition search found no
`func_`, `fake_func_`, or `static_` placeholder body in the interval.

This closes the band without a semantic rename. The visible five-record
selection is the same-run positive control that the census reached the
requested band; no runtime behavior, build, or generated source changed.
