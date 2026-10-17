# Generated-symbol audit: `__osProbeTLB`

Session 5221 (2026-10-17) audited `__osProbeTLB = 0x800351A0`.

The bounded `rename_generated_symbols.py` pass reported
`already-synchronized` and renamed zero references in zero files. Independent
generated-tree searches found no body, placeholder, header declaration,
overlay record, or direct generated caller at the companion address. The
companion symbol map places `__osViSwapContext` at `0x80035550`, so the
nominal span is `0x3B0`, but there is no generated body to validate it.

This selects the unmaterialized libultra/ABI outcome. Preserve the existing
semantic name. It rules out a generated-symbol rename and a body/span mismatch
for this candidate, but makes no runtime claim.
