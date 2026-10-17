# Session 5262 generated-symbol audit: `_Ldtob`

The bounded rename helper covered `0x80036B90..0x80037270` and made zero
edits, reporting `_Ldtob = 0x80036B90` as `already-synchronized`. It also
reported the adjacent `lldiv` and `ldiv` entries as already synchronized.

Independent checks found `_Ldtob = 0x80036B90` marked `defined:true` in
`../rogue_squadron64/symbol_files/libultra.txt`, an exact generated body
beginning at `0x80036B90` in `../N64Recomp/RecompiledFuncs/funcs_8.c`, its
declaration in `funcs.h`, and its `recomp_overlays.inl` record spanning
`0x80036B90..0x800370DF`. The generated tree also has a direct call from
`0x80035E1C`. There is no placeholder or data-fragment evidence at the
candidate address.

This selects H1 (already synchronized), rules out companion propagation and
fragment renaming for `_Ldtob`, and requires no build or soak. The next
bounded candidate is `_Litob = 0x80037270`.
