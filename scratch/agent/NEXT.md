# NEXT work unit — audit indirect audio mix-table provenance

HYPOTHESIS-ID: m3-audio-mix-table-provenance-audit

Next work unit: perform one complete grep-enumerate/classify audit of every
initializer, selector writer, and indirect consumer for the voice mix-table
fields at `voice+0x168` and `voice+0x188`. Start with generated
`../N64Recomp/RecompiledFuncs/funcs_*.c`; include named callers and all
address-derived aliases, but do not re-audit the closed MORT body at
`0x8009D7D0..0x8009DD7C`. Do not change runtime code unless a concrete
invalid table base, selector, or writer is identified. Any mitigation needs an
ORIGIN line naming the writer and assessing legitimacy.

Competing hypotheses and discriminator:

- H-MixTableComplete: all table/function-pointer initializers and selector
  writers establish the two 8-entry banks consumed by `audioMixStereoBlock8`.
- H-MixTableGap: a concrete table initializer, selector writer, or consumer
  uses a missing/invalid base, bank, count, or function pointer.
- H-MixTableMisread: `+0x168`/`+0x188` are not the active voice mix-table
  fields and the indirect path is mislabeled.

Discriminator: one complete table of field writers, initialization values,
bank layout, selector/count bounds, and all indirect consumers. Select
H-MixTableGap only with a concrete invalid edge; select H-MixTableComplete
only when all writers and consumers are covered; otherwise leave it
unclassified.

Exact checks:

    rg -n -i '0x168|0x188|168\(|188\(|audioMixStereoBlock8|jalr|voice.*mix|mix.*table' ../N64Recomp/RecompiledFuncs/funcs_*.c
    rg -n -i '0x8009DC98|0x8009DC9C|0x8009DCAC|0x8009C4C8|0x8009C4D0' ../N64Recomp/RecompiledFuncs/funcs_*.c
