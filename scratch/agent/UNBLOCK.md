# Unblock result — M5 retail-grounded boundary

Route taken: 2, satisfy locally.

The claimed missing source was already available as the companion project's
generated ELF:

`/Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf`

Evidence from this iteration:

- `file` identifies it as a non-stripped, statically linked, 32-bit big-endian
  MIPS-I ELF.
- `nm -S -n` identifies `osViSetMode` at `0x800352D0` with size `0x70` and
  `__osViSwapContext` at `0x80035550` with size `0x360`.
- The companion `tools/make_elf.py` documents that this ELF is generated from
  the retail ROM and symbol files and is consumable by N64Recomp.
- The companion C files are still `INCLUDE_ASM` stubs and no standalone
  matching `.s` files are present, so the ELF is the local equivalent body
  missed by the prior census.

This proves the dependency was locally obtainable and makes the block false.
The next unit will decode those exact ELF ranges and use the recovered edge
to select a single phase-gated retail oracle watch.
