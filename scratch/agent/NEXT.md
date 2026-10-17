# Next: continue the generated-symbol sweep

Work unit: classify `relinkNpcSlotToNewParentGroup = 0x8003EFDC`, the next
address-ordered companion record after Session 5295. Run one bounded helper
and independent generated-tree inspection. Do not build or soak unless the
discriminator finds a callable placeholder or a needed rename.

Before any build, competing hypotheses:

- H1: the record is typed data or an already-synchronized named callable.
- H2: the bounded helper misses a callable placeholder at the address.
- H3: generated code contains a callable/data fragment whose semantic name
  conflicts with the companion record.

Discriminator: combine the helper result with companion typing/description and
searches for a generated body, placeholder, declaration, overlay record, and
direct reference. H1 requires typed data or a matching named callable plus no
placeholder/conflict; H2 requires a callable placeholder/body; H3 requires a
callable fragment or conflicting semantic record.

Exact commands:

`rg -n -C 2 'relinkNpcSlotToNewParentGroup|8003EFDC' ../rogue_squadron64/symbol_files`

`python3 tools/rename_generated_symbols.py ../N64Recomp/RecompiledFuncs --companion-dir ../rogue_squadron64/symbol_files --start-address 0x8003EFDC --end-address 0x8003EFE0 --limit 1`

`rg -n 'relinkNpcSlotToNewParentGroup|func_8003EFDC|fake_func_8003EFDC|8003EFDC' ../N64Recomp/RecompiledFuncs --glob '*.c' --glob '*.h' --glob '*.inl'`

HYPOTHESIS-ID: generated-symbol-renaming-sweep
