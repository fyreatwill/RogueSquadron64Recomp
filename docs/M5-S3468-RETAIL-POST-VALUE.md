# M5 Session 3468 — retail table-entry post-store values

The corrected independent Rice-oracle capture ran for 35 seconds with the
whole-RDRAM and source-slot positive controls, title phase gates, table-span
watch, candidate writer execution watches, load/store watches, and post-store
sampling in one run. It recorded 14,935 whole-RDRAM writes, 3,032 writes in
`0x1B4AA0..0x1B4B24`, and 1,903 writes to `0x1E8710`. Title reached both
`0x00790400` and `0x00790800` at width 1024.

All candidate writers fired: `0x80064350` (2,108), `0x80064360` (2,090),
`0x80064378` (2,090), and `0x800646D8` (564). The corrected store-field
configuration retained 1,863 phase-qualified callbacks and 968 unique rows.
Post-store sampling measured 445, 427, 427, and 564 rows for those writers;
the values include selected table pointers in the `0x801Bxxxx` family. The
shared `0x80064524` source-slot sampler recorded 398 nonzero rows: 327
`0x801B4F00` and 71 `0x801B5E70`.

This repairs the prior instrument configuration failure and proves that
retail candidate stores have observable post-store values. It does not join
those values to a port-side table pointer or selection, so it selects neither
`H-SourceWriterValue` nor `H-TablePointerDivergence` across runtimes. The next
measurement must expose the port pointer at the intervening table-load edge.

The first attempt used table addresses as `--store-field-dump` PCs and omitted
`--post-value-pc-detail`; its controls fired but its post-target table was
empty. No runtime behavior or mitigation changed.
