# M5 s3575 — retail zero-fill caller join

The retail oracle ran with whole-RDRAM and source-span positive controls, plus
phase-gated execution watches for presumed caller `0x8008F2CC` and entry
`0x800078E0`. Whole-RDRAM had 10,674 writes, the source span had 674 writes,
and the target `0x006AB400:512` phase contained 3,166 entry executions.

The presumed caller had zero executions. Retail entry execution is therefore
live, but this run cannot join it to the port tuple
`dst=0x801797B0`, `fill=0`, `len=0x298`, or order that tuple against the first
source DMA. This selects none of `H-ZeroFillParity`, `H-ZeroFillPortInput`, or
`H-ZeroFillPortOrdering`; only the absent-entry alternative is ruled out.

The entry predecessor histogram identifies `0x800C825C` (2,260 hits) and
`0x800052C4` (867 hits) as the dominant observed edges. The next table should
watch those edges and `0x800078E0` together, retaining both controls, then
classify entry rows by argument registers and source-DMA chronology.

ORIGIN: diagnostic-only retail caller/entry qualification. No game state,
output, PCM, task, DMA, or source contents were changed.

Evidence: `scratch/agent/soak_results/s3575_retail_zero_fill_join.log`.
