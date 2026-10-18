# Session 5400 generated-symbol audit

Candidate: `fake_func_800B75C4`

The generated record in `RecompiledFuncs/funcs_31.c` is exactly `0xC` bytes,
covering `0x800B75C4` through `0x800B75CC`, with `playerYwingInit` beginning at
`0x800B75D0`. Its instructions are `lui`, `lwc1`, and `mul.s`.

The companion `mission_overlay.txt` independently keeps the placeholder at
`0x800B75C4` and comments that the real function is `playerYwingInit`. The
project syms table independently classifies the same address and exact size as
`data_gap_800B75C4`, followed by `playerYwingInit` at `0x800B75D0`. There is no
companion semantic name for the fragment and no regeneration-safe mapping that
would justify inventing one.

H2 selected: this is a companion-classified split/data fragment before the real
function, not a callable preamble. No rename was made.

ORIGIN: n/a (symbol audit only; no mitigation or runtime behavior changed).
