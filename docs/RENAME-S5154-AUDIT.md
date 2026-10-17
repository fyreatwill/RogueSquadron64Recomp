# Session 5154 rename audit — `__osCheckId`

- Candidate: `__osCheckId = 0x8002FC60`.
- Companion span: `0x8002FC60` through the next libultra entry,
  `__osPfsRWInode = 0x8002FD5C`.
- Direct generated-tree search: no `__osCheckId`, `func_8002FC60`, or
  `fake_func_8002FC60` reference in `funcs_*.c`, `funcs.h`, or
  `recomp_overlays.inl`.
- Independent companion-map check: `libultra.txt` lists the candidate and
  next boundary as named ABI entries, but supplies no generated body or
  caller evidence.
- Bounded helper result: `already-synchronized`; zero references renamed in
  zero files. The helper also exposed the next candidate,
  `__osPfsRWInode = 0x8002FD5C`.
- Classification: unmaterialized libultra/ABI entry. There is no generated
  body, exact body span, or independent generated caller supporting a rename.

Preserve the existing ABI name. No build or soak was needed for this
naming-only classification.
