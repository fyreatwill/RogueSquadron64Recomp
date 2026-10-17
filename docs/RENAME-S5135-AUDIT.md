# Session 5135 rename audit

Candidate: `__osLeoInterrupt = 0x8002C500`.

The bounded helper was run over `0x8002C500..0x8002DB70` with the companion
symbol files. It changed zero references and reported `already-synchronized`
for `__osLeoInterrupt` and the other companion entries in the selected range.

Independent generated-tree inspection found no candidate placeholder, ABI
declaration, generated body, overlay record, or direct generated caller for
`__osLeoInterrupt`. The companion map independently defines the symbol at
`0x8002C500`; no generated artifact exists to rename. Preserve the ABI name
as an unmaterialized libultra entry. No build or soak is needed.
