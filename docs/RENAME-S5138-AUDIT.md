# Session 5138 rename audit

Candidate: `osEPiRawStartDma = 0x8002CD80`.

The bounded helper was run over `0x8002CD80..0x8002D0B0` with the companion
symbol files. It changed zero references and reported `already-synchronized`
for `osEPiRawStartDma` and `osLeoDiskInit`.

Independent generated-tree inspection found only the ABI declaration and an
overlay-table entry with `rom_size = 0`; there is no generated body,
placeholder, or direct generated caller for this address. The companion map
independently defines `osEPiRawStartDma` and places the next entry,
`osLeoDiskInit`, at `0x8002CFB0`. There is therefore no generated artifact to
rename; preserve the companion ABI name as an unmaterialized libultra entry.
No build or soak is needed.
