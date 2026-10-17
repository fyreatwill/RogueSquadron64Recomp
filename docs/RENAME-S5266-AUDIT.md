# Session 5266 — `_Putfld` duplicate sweep check

The bounded rename helper was run over exactly `0x80035960..0x80035FD0`.
It renamed zero references in zero files and reported
`_Putfld = 0x80035960` as `already-synchronized`.

Independent checks found the companion declaration, a full named `_Putfld`
body spanning `0x670` bytes in `../N64Recomp/RecompiledFuncs/funcs_8.c`, the
matching `funcs.h` declaration, the `recomp_overlays.inl` record, and an
internal generated caller. This is a real named libultra formatting routine,
not a placeholder or data fragment. Preserve the name; no build or soak was
warranted.

The candidate had already been recorded by Session 5259; this iteration
confirms the stale next-step pointer and does not claim a new rename.

Next bounded candidate: `__osContinitialized = 0x800390D0`, a companion data
symbol to classify separately from callable generated functions.
