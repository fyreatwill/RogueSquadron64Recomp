# Session 3183 — generated-symbol sweep `0x80190000..0x801A0000`

## Hypotheses and discriminator

- `H-SemanticMatch`: a placeholder in the interval has an exact companion
  semantic function name.
- `H-DataGap`: a placeholder is independently classified as a non-callable
  fragment and can be mechanically renamed to `data_gap_<address>`.
- `H-Ambiguous`: the companion record is fake, duplicate, overlay-colliding,
  or otherwise lacks enough evidence and must remain unchanged.

The discriminator was one bounded helper census with `--require-rename`,
followed by an independent search for placeholder `RECOMP_FUNC` definitions
in the same address interval.

## Result

The required-rename helper selected zero generated references, changed zero
references in zero files, and returned its expected no-rename exit code 2.
The independent search found no `func_*`, `fake_func_*`, or `static_*`
placeholder definition in the interval.

This selects the closed-band outcome: no exact semantic or data-gap rename is
authorized, and ambiguous fragments remain untouched. No build, game run, or
runtime behavior changed.
