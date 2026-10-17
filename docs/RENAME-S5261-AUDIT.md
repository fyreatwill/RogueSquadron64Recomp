# Session 5261 generated-symbol audit

Candidate: `_Genld = 0x80036620`.

The bounded helper reported `renamed 0 references in 0 files` and classified
the candidate as `already-synchronized`. Independent checks found the exact
companion entry in `../rogue_squadron64/symbol_files/libultra.txt` with
`defined:true`, a generated `_Genld` body in
`../N64Recomp/RecompiledFuncs/funcs_8.c` beginning at `0x80036620`, its
declaration in `funcs.h`, and its overlay record in `recomp_overlays.inl`.
The record spans `0x80036620` through `0x80036B87`; a generated caller at
`0x800370AC` invokes `_Genld` directly.

The next address, `0x80036B88`, is a separate pure `jr ra` stub named
`noopHandler_80036B88` in both trees and is not part of `_Genld`.

Conclusion: preserve `_Genld`; this is not a placeholder, fragment, or
unmaterialized ABI entry. The next sweep candidate is `_Ldtob = 0x80036B90`.
