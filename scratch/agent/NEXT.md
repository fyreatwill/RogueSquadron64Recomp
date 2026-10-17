# Next: generated-symbol sweep — `spawnInheritedNpcVariantB`

Work unit: classify companion symbol `spawnInheritedNpcVariantB = 0x8003F880`
with the existing bounded renaming helper, then independently inspect its
generated body, declaration, overlay record, callers, and any placeholder
conflict. Do not change runtime code if it is already named.

Competing hypotheses:

- H1: the companion entry is already synchronized and the helper makes zero
  edits.
- H2: a generated placeholder remains and the helper renames a bounded set of
  references.
- H3: the companion record is data or an ABI boundary rather than a callable
  placeholder, so preserve its existing name without renaming.

Discriminator: the helper's edit count and independent generated-tree checks
must distinguish a named callable, a placeholder rename, or a non-callable
data/ABI boundary; no build or soak is warranted for a classification-only
result.

Exact commands: run `python3 tools/rename_generated_symbols.py
../N64Recomp/RecompiledFuncs --companion-dir
../rogue_squadron64/symbol_files --start-address 0x8003F880
--end-address 0x8003F884 --limit 1`, then grep the companion map and generated
tree for the address, symbol, placeholder, declaration, overlay record, and
callers.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
