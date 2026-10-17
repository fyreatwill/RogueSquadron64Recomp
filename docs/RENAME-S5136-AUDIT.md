# Session 5136 rename audit

Candidate: `__osLeoAbnormalResume = 0x8002CBA4`.

The bounded helper was run over `0x8002CBA4..0x8002D0B0` with the companion
symbol files. It changed zero references and reported `already-synchronized`
for `__osLeoAbnormalResume`, `__osLeoResume`, `osEPiRawStartDma`, and
`osLeoDiskInit`.

Independent generated-tree inspection found no placeholder, ABI declaration,
generated body, overlay record, or direct generated caller for
`__osLeoAbnormalResume`. The companion map independently defines the symbol
with span `0xE8`, ending at `__osLeoResume = 0x8002CC8C`. There is therefore no
generated artifact to rename; preserve the companion ABI name as an
unmaterialized libultra entry. No build or soak is needed.
