# Session 5573 — `fake_func_8006ACA4` exact-span audit

## Competing hypotheses

- H1: this is a callable generated function with a companion-backed semantic name.
- H2: this is a data/gap fragment and must retain a non-semantic gap name.
- H3: the generated tree and existing mappings are already synchronized or the address is reused.

## Discriminator and result

The generated record, overlay registration, companion symbol file, and checked-in
syms table were compared at the exact address and boundary.

- `../N64Recomp/RecompiledFuncs/funcs_16.c` emits a 12-byte record at
  `0x8006ACA4`, containing only the fragment `lwc1 $f0, 0x10($fp)`,
  `lwc1 $f2, 0x0($v0)`, and `add.s $f0, $f0, $f2`.
- The generated overlay registration spans `0x8006ACA4..0x8006ACB0`
  (`rom_size = 0xC`), immediately before `transformObjectColliderCenter`.
- `../rogue_squadron64/symbol_files/main_overlay.txt` retains the same
  `fake_func_8006ACA4` entry and places `transformObjectColliderCenter` at
  `0x8006ACB0`; it supplies no semantic name for the fragment.
- `syms/rogue_squadron.syms.toml` independently classifies exactly
  `0x8006ACA4..0x8006ACB0` as `data_gap_8006ACA4`, size `0xC`.
- The regeneration-safe rename tables already map the placeholder to
  `data_gap_8006ACA4`; no mapping change is needed.

The exact three-source span agreement and absence of a callable semantic name
select H2. No generated or mapping change is justified.

## Next candidate

Continue the same exact-span test with `fake_func_800AE3E4`.
