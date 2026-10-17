# Session 5152 symbol audit

Candidate: `__osCheckPackId = 0x8002F86C`

The bounded `rename_generated_symbols.py` audit reported
`already-synchronized` and made zero edits. Direct searches of the generated
function files, `funcs.h`, and `recomp_overlays.inl` found no generated body,
placeholder, overlay record, or independent generated caller at the candidate
address. The companion boundary is `__osGetId = 0x8002FA04`, but no generated
body exists to establish a rename span. Preserve the existing ABI name as an
unmaterialized libultra entry; no build or soak was needed.
