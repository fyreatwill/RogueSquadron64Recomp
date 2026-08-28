# `0x8001B7B8` generated-symbol audit

## Classification

`0x8001B7B8` is the uniquely identified callable
`requestViFeatureChange`.

## Evidence

- `../rogue_squadron64/symbol_files/main_overlay.txt` maps the address to
  `requestViFeatureChange`.
- `../N64Recomp/RecompiledFuncs/funcs_5.c` contains one complete
  `RECOMP_FUNC` definition at the address. It stores `$a0` to the pending VI
  feature word and returns one.
- `funcs_9.c`, `funcs_28.c`, `funcs_29.c`, `funcs_31.c`, and `funcs_33.c`
  contain the generated callers; all dispatch through the same named
  definition. No duplicate callable definition was found.
- `funcs.h` and `recomp_overlays.inl` already use the same name and register
  the 0x10-byte entry.

## Change

Synchronized `syms/rogue_squadron.syms.toml` from `func_8001B7B8` to
`requestViFeatureChange`. `cmake --build build --config Debug --target
RecompiledFuncs` completed successfully.
