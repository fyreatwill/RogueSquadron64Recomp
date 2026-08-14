# NEXT work unit (s987)

HYPOTHESIS-ID: m4-zero-shade-writer

## One work unit

Run one bounded writer inventory for the phase-6 VTXCOLOR payload range
`0x732A10..0x73E3B0`, with phase-4 control range `0x726200..0x726C50`.
Enumerate generated stores and base/index forms, classify each candidate by
owning object and reachability, and land no mitigation.

## Competing hypotheses and discriminating measurement

- H-game-writer: a game-side store owns the nonzero VTXCOLOR payload.
- H-dma-copy: a DMA or copy path owns the payload.
- H-renderer-state: neither sampled range has a relevant writer, so zero is
  introduced after the F5 fetch in renderer state conversion.

Discriminating measurement: an exhaustive writer set for the sampled addresses,
plus one positive source control. A reachable game-side writer selects
H-game-writer; a reachable DMA/copy writer selects H-dma-copy; no writer in
either region leaves H-renderer-state as the remaining boundary.

## Exact commands

`rg -n -C 3 '0x(732A10|732F38|733460|733988|7340C0|7344E0|734A08|737EA0|7384D0|7388F0|739238|739B80|739FA0|73A4C8|73A9F0|73B020|73B758|73BD88|73C4C0|73C9E8|73CF10|73D540|73DC78|73E3B0)|0x726200|0x726728|0x726C50' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`

`rg -n -C 2 'MEM_[BHDW]|MEM_B|MEM_H|MEM_W|MEM_D' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c | rg '732A|732F|7334|7339|7340|7344|734A|737E|7384|7388|7392|739B|739F|73A4|73A9|73B0|73B7|73BD|73C4|73C9|73CF|73D5|73DC|73E3|7262|7267|726C'`

Do not infer a writer from an address-only string hit. Classify the base,
stride, index, and owner, and state whether it can reach the phase-6 sources.
