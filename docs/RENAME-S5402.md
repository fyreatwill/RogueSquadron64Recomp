# Session 5402 — `fake_func_800AF6A8` exact-span audit

## Competing hypotheses

- H1: this is a callable generated function with an independently supported
  semantic name.
- H2: this is a data/splat fragment and must retain a non-semantic gap name.
- H3: the generated tree and existing mappings are already synchronized or
  the address is reused.

## Discriminator and result

The generated record, overlay entry, companion symbol files, and checked-in
syms table were compared at the exact address and boundary.

- `../N64Recomp/RecompiledFuncs/funcs_29.c` emits a trap-only placeholder at
  `0x800AF6A8`; it is explicitly marked as an invalid-C gap filler.
- `recomp_overlays.inl` gives the generated placeholder a broad synthetic
  span, but this is not independent callable-function evidence.
- `../rogue_squadron64/symbol_files/cinematic_overlay.txt` retains
  `fake_func_800AF6A8` and independently places `cutsceneTypeStrings` at
  `0x800AF6B0`.
- `syms/rogue_squadron.syms.toml` classifies exactly
  `0x800AF6A8..0x800AF6B0` as `data_gap_800AF6A8`, size `0x8`.

The exact independent span and the invalid generated body select H2. No
semantic rename is safe, and no generated or mapping change is made.

## Next candidate

Continue the same exact-span test with `fake_func_800AE3E4`.
