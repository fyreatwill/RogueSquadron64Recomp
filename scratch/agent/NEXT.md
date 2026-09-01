# NEXT work unit — audit pan-coefficient input and selector lifecycle

HYPOTHESIS-ID: m3-pan-coefficient-input-provenance-audit

Next work unit: perform one complete grep-enumerate/classify audit of every
caller input and source-structure writer feeding
`computeVoicePanCoefficients` (`0x8009C2D0`), plus the lifecycle of
`voice+0x188` from slot initialization through the three callers. Do not
re-audit the closed table consumer/producer body. Do not change runtime code
unless a concrete invalid input, selector, or source writer is identified.
Any mitigation needs an ORIGIN line naming the writer and assessing
legitimacy.

Competing hypotheses and discriminator:

- H-PanInputsComplete: all callers supply bounded, initialized source fields
  and a valid selector lifecycle.
- H-PanInputsGap: a concrete caller/source writer supplies an invalid field,
  selector, or voice-object base.
- H-PanInputsMisread: the apparent pan source fields are not the active inputs
  to the mix-table writer.

Discriminator: one complete caller/source-field table with writer PCs, field
layouts, selector values/bounds, and initialization order. Select
H-PanInputsGap only with a concrete invalid edge; select
H-PanInputsComplete only when every caller and source writer is covered;
otherwise leave it unclassified.

Exact checks:

    rg -n 'computeVoicePanCoefficients|0x8009C2D0|0x8009C2E0|0x8009C4C8|0x8009C4D0|0X188|0X168' ../N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n -i 'voice.*pan|pan.*voice|0x164|0x166|0x168|0x188' ../N64Recomp/RecompiledFuncs/funcs_{22,23,24,25,26,27}.c
