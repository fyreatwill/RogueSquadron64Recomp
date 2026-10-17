# Session 5157 rename audit — `osPfsDeleteFile`

- Candidate: `osPfsDeleteFile = 0x800300F0`.
- Companion span: `0x800300F0` through the requested next companion boundary,
  `0x800303D0`.
- Bounded helper result: `already-synchronized`; zero references renamed in
  zero files.
- Generated-tree evidence: no generated body or placeholder at
  `0x800300F0`; the overlay table has a zero-size `osPfsDeleteFile_recomp`
  record, and one generated caller dispatches to that ABI wrapper.
- Independent source evidence: `lib/N64ModernRuntime/librecomp/src/pak.cpp`
  defines `osPfsDeleteFile_recomp` as a host wrapper returning
  `PFS_ERR_NOPACK`. The symbol table’s `0x2E0` companion span is not
  materialized as generated code.
- Classification: unmaterialized libultra/ABI entry. There is no generated
  body or exact generated body span supporting a rename.

Preserve the existing ABI name. No build or soak was needed for this
naming-only classification.
