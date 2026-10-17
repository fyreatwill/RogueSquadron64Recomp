# Next: generated-symbol sweep — `markLowLodCellsInGrid`

Work unit: classify `markLowLodCellsInGrid = 0x80043AEC` with the bounded helper,
then independently inspect the companion record and generated tree. This is a
classification-only unit; do not build or soak.

Competing hypotheses and discriminator:

- H1: zero helper edits and a named callable body plus declaration/overlay metadata select “already synchronized.”
- H2: a generated `func_...` placeholder and nonzero bounded edit count select a real rename; verify callers and conflicts.
- H3: typed data or an ABI boundary with no callable placeholder selects preservation without renaming.

Run:
`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x80043AEC --end-address 0x80044724 --limit 1`

Session 5318 result: `destroyNpcSlotByIndexU16 = 0x80041CEC` was already
synchronized with zero edits. The companion map and generated tree independently
agreed: named wrapper body, prototype, overlay record, and named generated caller;
the body masks `a0` to u16 before forwarding to `destroyNpcSlotByIndex`. No
placeholder or conflicting fragment remained. For the next iteration the
discriminator is whether the helper reports a placeholder requiring edits, or a
named callable/data/ABI record requiring preservation.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
