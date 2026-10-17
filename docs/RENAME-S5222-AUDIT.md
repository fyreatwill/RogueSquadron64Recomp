# Session 5222 symbol audit: `__osViSwapContext`

Candidate: `__osViSwapContext = 0x80035550`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent generated-tree searches found no body,
placeholder, header declaration, overlay record, or direct generated caller at
the companion address. The neighboring generated ABI entries
`osWritebackDCache = 0x800358B0` and `osWritebackDCacheAll = 0x80035930` are
zero-size host-wrapper records; `_Putfld = 0x80035960` is the next companion
entry, giving this candidate a nominal `0x410` span, but there is no generated
body to validate.

Classification: unmaterialized libultra/ABI entry; preserve the ABI name and
do not rename. No build or soak was warranted for this naming-only result.
