# Session 5263 generated-symbol audit: `_Litob`

The bounded rename helper covered `0x80037270..0x80037510` and made zero
edits, reporting `_Litob = 0x80037270` as `already-synchronized`.

Independent checks found `_Litob = 0x80037270` marked `defined:true` in
`../rogue_squadron64/symbol_files/libultra.txt`, an exact generated body
beginning at `0x80037270` in `../N64Recomp/RecompiledFuncs/funcs_8.c`, its
declaration in `funcs.h`, and its `recomp_overlays.inl` record spanning
`0x80037270..0x8003750F`. The generated tree also has direct callers from
`0x80035B68`, `0x80035CB8`, and `0x80035F34`. There is no placeholder or
data-fragment evidence at the candidate address.

This selects H1 (already synchronized), rules out companion propagation and
fragment renaming for `_Litob`, and requires no build or soak. The next
bounded candidate is `osYieldThread = 0x80037510`.
