# Session 5156 rename audit — `__osPfsSelectBank`

- Candidate: `__osPfsSelectBank = 0x8003007C`.
- Companion span: `0x8003007C` through the requested next companion boundary,
  `0x800303D0`.
- Bounded helper result: `already-synchronized`; zero references renamed in
  zero files.
- Generated-tree evidence: no `__osPfsSelectBank`, `func_8003007C`, or
  `fake_func_8003007C` definition or overlay record; five generated callers
  dispatch to the existing ABI wrapper.
- Independent source evidence: `src/main/upstream_compat.cpp` defines
  `__osPfsSelectBank_recomp` as a host wrapper returning `PFS_ERR_NOPACK`, and
  the symbol table assigns the companion address a `0x6C` span.
- Classification: unmaterialized libultra/ABI entry. There is no generated
  body or exact generated body span supporting a rename.

Preserve the existing ABI name. No build or soak was needed for this
naming-only classification.
