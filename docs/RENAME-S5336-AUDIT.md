# Generated-symbol census — `0x800927B0`

The planned audit was repeated against the current checkout because
`scratch/agent/NEXT.md` still named this address as unresolved.

| Surface | Current evidence |
|---|---|
| Generated body | `N64Recomp/RecompiledFuncs/funcs_24.c` defines `interpolatePointTableSamplesToPackedWord` at the `0x800927B0` instruction span; the body covers `0x124` bytes. |
| Callers | The same generated file calls it from `0x800926F8` and `0x80092704`. |
| Registration/header | `funcs.h` and `recomp_overlays.inl` use the semantic name and the same `0x124` size. |
| Project/fixup maps | `syms/rogue_squadron.syms.toml` and `tools/rename_generated_symbols.py` use the semantic name. |
| Companion source | `rogue_squadron64/symbol_files/main_overlay.txt` maps `0x800927B0` to `interpolatePointTableSamplesToPackedWord` and marks it defined. |

H1 is already satisfied by the checked-in state; there is no stale generated
placeholder left to rename. This fresh census adds no runtime behavior and
does not justify an M4 or audio inference.
