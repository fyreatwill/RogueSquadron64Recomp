# Session 3064 — `fake_func_800B2628`

## Discriminator

The competing hypotheses were:

- `H-ExactIdentity`: the companion project names a real callable routine and
  all six surfaces support a semantic rename.
- `H-BoundaryOnly`: the address is a fragment, invalid decode, or data gap and
  should retain an address-derived placeholder.
- `H-MappingDrift`: companion and generated/project metadata disagree and need
  synchronization.

The discriminator was the six-surface comparison: companion symbol entry,
generated body, callers, generated header, overlay registration, and project
TOML, including duplicate-address entries.

## Results

| Surface | Finding |
|---|---|
| Companion map | `symbol_files/menu_overlay.txt` has only `fake_func_800B2628 = 0x800B2628`; no semantic name or body note. |
| Generated body | `RecompiledFuncs/funcs_30.c` contains exactly two instructions: load a float from `-0x5D04($at)` and store it at `0x168($v0)`. It has no `jr`, epilogue, or return value. |
| Callers | No generated caller or exact-address call reference was found. The other `800B2628` hit is an instruction comment inside an unrelated address-encoded function. |
| Header | `RecompiledFuncs/funcs.h` declares the same placeholder with an 8-byte host function signature. |
| Overlay registration | `RecompiledFuncs/recomp_overlays.inl` registers the menu-overlay span at offset `0xD4F8`, size `0x8`, under the same placeholder. |
| Project TOML | `syms/rogue_squadron.syms.toml` records the same name, VRAM `0x800B2628`, and size `0x8`. |
| Local duplicates | No duplicate symbol entry for the exact address was found in the current generated tree, companion map, or project TOML. |

## Conclusion

`H-BoundaryOnly` selected. The exact metadata agrees, so `H-MappingDrift` is
rejected, but the two-instruction span cannot independently establish a
callable routine: it is adjacent to the preceding function's return and the
following `buildFormatMessageGlyphBuffer` entry, and has no return sequence or
caller. No rename or generated-file edit is justified. The placeholder is
preserved as a bounded fragment/data-boundary name.

