# Next: generated-symbol sweep — `findFirstActiveNpcChildInChain`

Work unit: classify `findFirstActiveNpcChildInChain = 0x8003FCBC` with the bounded helper, then independently inspect the companion record and generated tree. This is a classification-only unit; do not build or soak.

Competing hypotheses and discriminator:

- H1: zero helper edits and a named callable body plus declaration/overlay metadata select “already synchronized.”
- H2: a generated `func_...` placeholder and nonzero bounded edit count select a real rename; verify callers and conflicts.
- H3: typed data or an ABI boundary with no callable placeholder selects preservation without renaming.

Run:
`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x8003FCBC --end-address 0x8003FCC0 --limit 1`

Then grep the companion map and generated tree for the address, symbol, placeholder, declaration, overlay record, and callers. The helper result and independent tree inspection are the two required evidence lines.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
