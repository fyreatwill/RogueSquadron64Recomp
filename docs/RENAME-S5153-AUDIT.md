# Session 5153 rename audit — `__osGetId`

- Candidate: `__osGetId = 0x8002FA04`.
- Companion span: `0x8002FA04` through the next libultra entry,
  `__osCheckId = 0x8002FC60`.
- Direct generated-tree search: no `__osGetId`, `func_8002FA04`, or
  `fake_func_8002FA04` reference in `funcs_*.c`, `funcs.h`, or
  `recomp_overlays.inl`.
- Bounded helper result: `already-synchronized`; zero references renamed in
  zero files.
- Classification: unmaterialized libultra/ABI entry. There is no generated
  body, exact body span, or independent generated caller supporting a rename.

Preserve the existing ABI name. No build or soak was needed for this
naming-only classification.
