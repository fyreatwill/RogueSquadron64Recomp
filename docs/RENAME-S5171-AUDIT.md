# Session 5171 symbol audit: `osPfsReadWriteFile`

Candidate: `osPfsReadWriteFile = 0x80031BDC`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. The generated tree contains the ABI declaration in
`funcs.h` and three generated callers in `funcs_2.c`, but no generated body or
placeholder at `0x80031BDC`. `recomp_overlays.inl` has a zero-size record at
offset `0x3179C`, so this is an unmaterialized libultra/ABI entry rather than
a generated function available for semantic renaming. The companion boundary
is `osPfsRepairId = 0x80032000`.

Classification: preserve the existing ABI name; do not rename.
