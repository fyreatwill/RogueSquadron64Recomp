# Unblock result

Route 3 — re-scope.

The external MIPS compiler dependency is real for a fresh source-to-ELF
qualification: `mips64-elf-gcc` and `mips64-elf-ld` are absent, Clang has no
MIPS target, and no sibling installation exists. The block is narrower than
the whole PatchesLib path because the repository already contains
`patches/patches.elf`.

Evidence this iteration:

- `build/N64Recomp patches.toml` succeeded and regenerated the 11-function
  host output.
- Clang compiled `RecompiledPatches/patches.c` with exit 0.
- `ar` created a host archive, and `nm` showed
  `allocateDisplayListBuffer`.
- Homebrew `mips-linux-gnu-ld` relinked the existing assembly object with exit
  0; this does not substitute for the missing C compiler.

The next unit is host-side artifact qualification using those commands. The
one experiment that would close the remaining dependency is a fresh
`patches/*.c` to MIPS ELF build after a human supplies the MIPS GCC/LD pair.
