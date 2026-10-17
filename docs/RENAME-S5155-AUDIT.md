# Session 5155 rename audit — `__osPfsRWInode`

- Candidate: `__osPfsRWInode = 0x8002FD5C`.
- Companion span: `0x8002FD5C` through the requested next companion boundary,
  `0x8003007C`.
- Direct generated-tree search: no `__osPfsRWInode`, `func_8002FD5C`, or
  `fake_func_8002FD5C` reference in `funcs_*.c`, `funcs.h`, or
  `recomp_overlays.inl`.
- Bounded helper result: `already-synchronized`; zero references renamed in
  zero files.
- Classification: unmaterialized libultra/ABI entry. There is no generated
  body, exact body span, or independent generated caller supporting a rename.

Preserve the existing ABI name. No build or soak was needed for this
naming-only classification.
