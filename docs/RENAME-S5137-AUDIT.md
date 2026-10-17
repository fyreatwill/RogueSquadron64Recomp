# Generated-symbol audit — Session 5137

Candidate: `__osLeoResume = 0x8002CC8C`.

The bounded helper was run over `0x8002CC8C..0x8002CD80` with the companion
symbol files. It changed zero references and reported `already-synchronized`.

Independent inspection of `RecompiledFuncs/funcs_*.c`, `funcs.h`, and
`recomp_overlays.inl` found no placeholder, ABI declaration, generated body,
overlay record, or direct generated caller for this address. The companion
map gives `__osLeoResume` an exact `0xEC` span ending at
`0x8002CD80`, the next entry `osEPiRawStartDma`.

This selects the unmaterialized libultra/ABI-boundary outcome. Preserve the
companion ABI name; no semantic generated-symbol rename, build, or soak is
warranted.
