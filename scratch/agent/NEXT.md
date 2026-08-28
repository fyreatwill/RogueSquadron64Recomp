# NEXT work unit (s2985) — classify the next generated-symbol fragment

HYPOTHESIS-ID: generated-symbol-renaming-sweep

## Unit

Resume the regeneration-safe symbol sweep at the lowest remaining placeholder:
`0x80023968`. Inspect one bounded entry in `../N64Recomp/RecompiledFuncs`, its
callers, predecessor/successor boundaries, and the companion
`../rogue_squadron64/symbol_files` map. Rename only if the exact semantic
identity is independently supported; otherwise record it as ambiguous and
leave the generated symbol unchanged.

## Competing hypotheses and discriminator

- `H-semantic-fragment`: the candidate is a real entry/preamble with a
  companion-supported semantic name, so a regeneration-safe rename is justified.
- `H-boundary-gap`: it is a data/fixup or invalid-decode gap bounded by complete
  routines, so it should receive only a `data_gap_*` classification.
- `H-ambiguous-fragment`: it is executable but lacks a standalone contract or
  exact companion identity, so the placeholder must remain.

The discriminator is one table combining generated body disassembly,
predecessor/successor boundaries, generated callers, companion symbols, and
independent lookup. A complete callable contract plus exact companion name
selects the rename; a mechanically proven non-callable gap selects the data
classification; otherwise preserve the placeholder.

## Commands

`rg -n 'func_[0-9A-Fa-f]{8}' ../N64Recomp/RecompiledFuncs --glob 'funcs_*.c'`

Inspect bounded windows around `0x80023968`, update the companion map,
project TOML, and regeneration-safe rename path only when selected. If a
rename is selected, run the bounded `rename_generated_symbols.py` command with
the candidate's exact address range, then build
`cmake --build build --config Debug --target RecompiledFuncs -j`. Record the
source table under `scratch/agent/s2985_generated_symbol_rename/`.
