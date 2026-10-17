# Session 5259 symbol audit: `_Putfld`

Candidate: `_Putfld = 0x80035960`.

The bounded rename helper, run against the generated tree and companion
`symbol_files`, renamed zero references in zero files and classified the
candidate as `already-synchronized`.

Independent evidence agrees: the companion decomp declares `_Putfld` in
`libultra/libc/xprintf.c` and `symbol_files/libultra.txt`; the generated tree
contains a full `_Putfld` body spanning `0x670` bytes in `funcs_8.c`, the
matching declaration in `funcs.h`, the overlay record in
`recomp_overlays.inl`, and an internal generated caller. This is a real
libultra formatting routine, not a placeholder requiring a semantic rename.

Classification: already synchronized; preserve `_Putfld`. No build or soak
was warranted for this naming-only result. The next sweep candidate is
`_Printf = 0x80035FD0`.
