# Next: continue the generated-symbol sweep

Classify `osViModePalLan1 = 0x800392E0` with the same bounded
generated-symbol helper and independent companion/generated-tree inspection.
Determine its following boundary from the companion map before running the
helper. Do not build or soak unless the discriminator finds a callable
placeholder or a needed rename.

Exact commands:
`rg -n -C 2 'osViModePalLan1|0x800392E0' ../rogue_squadron64/symbol_files`
then run
`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x800392E0 --end-address 0x80039330 --limit 1`
and inspect the bounded generated tree with `rg -n
'func_800392E0|fake_func_800392E0|osViModePalLan1|800392E0'
../N64Recomp/RecompiledFuncs --glob '*.c' --glob '*.h' --glob '*.inl'`.
Expected H1 is typed `OSViMode` data with no callable generated symbol;
H2/H3 require preserving the helper output and callable evidence in a new
audit before any build.

Competing hypotheses and discriminator:

- H1: the record is typed data or an already-synchronized ABI symbol.
- H2: it is an unmaterialized callable placeholder that the helper missed.
- H3: it is a generated callable/data fragment whose name needs correction.

Discriminating measurement: helper result plus independent checks for a
companion type, generated body, placeholder, declaration, overlay record, and
direct generated reference. H1 is selected by typed data/no callable; H2 by a
callable placeholder/body; H3 by a callable fragment or conflicting semantic
record.

HYPOTHESIS-ID: generated-symbol-renaming-sweep
