# Session 5131 rename audit

Candidate: `__osEnqueueAndYield = 0x8002BC1C`.

The bounded helper was run over `0x8002BC1C..0x8002BF00` with the companion
symbol files. It changed zero references and reported `already-synchronized`
for `__osEnqueueAndYield`, `__osEnqueueThread`, `__osPopThread`,
`__osDispatchThread`, and `__osCleanupThread`. The generated snapshot contains
no candidate placeholder or named body, no overlay record at the candidate
address, and no direct generated caller. The companion map confirms the
semantic names and places the next library entry at `__osGetSR = 0x8002C230`.

Classification: host-wrapper/ABI boundary or unmaterialized libultra entry;
preserve the existing ABI naming and do not build or soak. This is an
independent helper/companion-map result plus a generated-tree search; no
semantic rename is justified.
