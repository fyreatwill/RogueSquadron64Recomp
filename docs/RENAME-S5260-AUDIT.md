# Session 5260 generated-symbol audit

Candidate: `_Printf = 0x80035FD0`.

The bounded helper reported `renamed 0 references in 0 files` and classified
the candidate as `already-synchronized`. Independent checks found the exact
companion entry in `../rogue_squadron64/symbol_files/libultra.txt` with
`defined:true`, a generated `_Printf` body in
`../N64Recomp/RecompiledFuncs/funcs_8.c`, its declaration in `funcs.h`, and
its overlay record in `recomp_overlays.inl`. The generated body starts at the
candidate address and there is one direct generated caller.

Conclusion: preserve `_Printf`; this is not a placeholder, fragment, or
unmaterialized ABI entry. The next sweep candidate is `_Genld = 0x80036620`.
