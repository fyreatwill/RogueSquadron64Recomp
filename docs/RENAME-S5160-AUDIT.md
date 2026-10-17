# Session 5160 rename audit — `osPfsFreeBlocks`

- Candidate: `osPfsFreeBlocks = 0x80030710`.
- Companion span requested: `0x80030710` through `0x80030A70` (`0x360` bytes).
- Bounded helper result: `already-synchronized`; zero references renamed in zero files.
- Generated-tree evidence: `funcs.h` contains only the ABI declaration, and
  `recomp_overlays.inl` records a zero-size overlay at ROM offset `0x302D0`.
  The bounded search found no generated body, placeholder, or independent
  caller at the companion address.
- Classification: unmaterialized libultra/ABI entry. Preserve the existing
  ABI name; there is no generated body whose semantic name can be improved.

No build or soak was needed for this naming-only classification.
