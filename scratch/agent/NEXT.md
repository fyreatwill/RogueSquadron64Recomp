# Next: generated-symbol sweep — `spawnNpcFormationWithRandomOrientation`

Work unit: classify `spawnNpcFormationWithRandomOrientation = 0x800409A4` with the bounded helper,
then independently inspect the companion record and generated tree.
This is a classification-only unit; do not build or soak.

Competing hypotheses and discriminator:

- H1: zero helper edits and a named callable body plus declaration/overlay metadata select “already synchronized.”
- H2: a generated `func_...` placeholder and nonzero bounded edit count select a real rename; verify callers and conflicts.
- H3: typed data or an ABI boundary with no callable placeholder selects preservation without renaming.

Run:
`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x800409A4 --end-address 0x80044724 --limit 1`

Session 5311 result: the helper returned `already-synchronized` with zero
edits. The companion map and generated tree independently agreed: named body
in `funcs_9.c`, prototype in `funcs.h`, and overlay record in
`recomp_overlays.inl`; no placeholder remained.

Then grep the companion map and generated tree for the next address, symbol,
placeholder, declaration, overlay record, and callers. The helper result and
independent tree inspection are the two required evidence lines. The
discriminator is whether the helper reports a placeholder requiring edits, or
a named callable/data/ABI record requiring preservation.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
